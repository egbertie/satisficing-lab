#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API客户端基类
提供Token管理、自动刷新、请求重试和错误处理功能
"""

import json
import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('feishu_api')


@dataclass
class FeishuConfig:
    """飞书配置类"""
    app_id: str
    app_secret: str
    base_url: str = "https://open.feishu.cn/open-apis"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    token_refresh_margin: int = 300  # Token过期前5分钟刷新
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'FeishuConfig':
        return cls(
            app_id=config.get('app_id', ''),
            app_secret=config.get('app_secret', ''),
            base_url=config.get('base_url', 'https://open.feishu.cn/open-apis'),
            timeout=config.get('timeout', 30),
            max_retries=config.get('max_retries', 3),
            retry_delay=config.get('retry_delay', 1.0),
            token_refresh_margin=config.get('token_refresh_margin', 300)
        )
    
    @classmethod
    def from_json_file(cls, filepath: str) -> 'FeishuConfig':
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return cls.from_dict(config)


class FeishuAPIError(Exception):
    """飞书API错误"""
    def __init__(self, message: str, code: int = None, response: dict = None):
        super().__init__(message)
        self.code = code
        self.response = response


class TokenExpiredError(FeishuAPIError):
    """Token过期错误"""
    pass


class RateLimitError(FeishuAPIError):
    """请求频率限制错误"""
    pass


def retry_on_error(max_retries: int = 3, delay: float = 1.0, 
                   exceptions: tuple = (requests.RequestException,)):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # 指数退避
                        logger.warning(f"请求失败，{wait_time}s后重试 ({attempt + 1}/{max_retries}): {e}")
                        time.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator


class FeishuTokenManager:
    """Token管理器 - 负责获取和刷新Tenant Access Token"""
    
    def __init__(self, config: FeishuConfig):
        self.config = config
        self._token: Optional[str] = None
        self._token_expire_time: float = 0
        self._session = requests.Session()
        
    def _is_token_valid(self) -> bool:
        """检查Token是否有效"""
        if not self._token:
            return False
        # 提前5分钟刷新Token
        return time.time() < (self._token_expire_time - self.config.token_refresh_margin)
    
    @retry_on_error(max_retries=3, delay=1.0)
    def get_token(self) -> str:
        """获取有效的Tenant Access Token"""
        if self._is_token_valid():
            return self._token
            
        url = f"{self.config.base_url}/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {
            "app_id": self.config.app_id,
            "app_secret": self.config.app_secret
        }
        
        logger.info("正在获取Tenant Access Token...")
        response = self._session.post(
            url, 
            headers=headers, 
            json=data, 
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('code') != 0:
            error_msg = result.get('msg', '获取Token失败')
            logger.error(f"获取Token失败: {error_msg}")
            raise FeishuAPIError(error_msg, code=result.get('code'))
        
        self._token = result.get('tenant_access_token')
        expire = result.get('expire', 7200)
        self._token_expire_time = time.time() + expire
        
        logger.info(f"Token获取成功，有效期{expire}秒")
        return self._token
    
    def refresh_token(self) -> str:
        """强制刷新Token"""
        self._token = None
        self._token_expire_time = 0
        return self.get_token()


class FeishuAPIClient:
    """飞书API客户端基类"""
    
    # API错误码映射
    ERROR_CODES = {
        99991663: TokenExpiredError,
        99991664: TokenExpiredError,
        99991661: TokenExpiredError,
        99991662: TokenExpiredError,
        99991400: RateLimitError,
    }
    
    def __init__(self, config: Union[FeishuConfig, str, Dict[str, Any]]):
        """
        初始化客户端
        
        Args:
            config: FeishuConfig对象、配置文件路径或配置字典
        """
        if isinstance(config, str):
            self.config = FeishuConfig.from_json_file(config)
        elif isinstance(config, dict):
            self.config = FeishuConfig.from_dict(config)
        else:
            self.config = config
            
        self.token_manager = FeishuTokenManager(self.config)
        self._session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """创建配置好的requests Session"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def _get_headers(self, need_auth: bool = True, extra_headers: Dict = None) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        
        if need_auth:
            token = self.token_manager.get_token()
            headers["Authorization"] = f"Bearer {token}"
            
        if extra_headers:
            headers.update(extra_headers)
            
        return headers
    
    def _handle_error(self, response: requests.Response, result: Dict) -> None:
        """处理API错误"""
        code = result.get('code', -1)
        msg = result.get('msg', '未知错误')
        
        if code != 0:
            error_class = self.ERROR_CODES.get(code, FeishuAPIError)
            
            # Token过期，尝试刷新并重试
            if error_class == TokenExpiredError:
                logger.warning("Token已过期，正在刷新...")
                self.token_manager.refresh_token()
                raise TokenExpiredError(f"Token过期: {msg}", code=code, response=result)
            
            # 频率限制
            if error_class == RateLimitError:
                logger.warning(f"触发频率限制: {msg}")
                raise RateLimitError(f"请求过于频繁: {msg}", code=code, response=result)
            
            logger.error(f"API错误 [code={code}]: {msg}")
            raise error_class(f"API错误: {msg}", code=code, response=result)
    
    def request(self, method: str, endpoint: str, 
                need_auth: bool = True,
                headers: Dict = None,
                **kwargs) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            method: HTTP方法
            endpoint: API端点（不含base_url）
            need_auth: 是否需要认证
            headers: 额外请求头
            **kwargs: 传递给requests的参数
            
        Returns:
            API响应数据
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers(need_auth, headers)
        
        logger.debug(f"请求: {method} {url}")
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=request_headers,
                timeout=self.config.timeout,
                **kwargs
            )
            
            # 尝试解析JSON响应
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {'code': response.status_code, 'msg': response.text}
            
            # 处理错误
            self._handle_error(response, result)
            
            return result
            
        except TokenExpiredError:
            # Token过期，重试一次
            request_headers = self._get_headers(need_auth, headers)
            response = self._session.request(
                method=method,
                url=url,
                headers=request_headers,
                timeout=self.config.timeout,
                **kwargs
            )
            result = response.json()
            self._handle_error(response, result)
            return result
    
    def get(self, endpoint: str, params: Dict = None, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return self.request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, json_data: Dict = None, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return self.request("POST", endpoint, json=json_data, **kwargs)
    
    def put(self, endpoint: str, json_data: Dict = None, **kwargs) -> Dict[str, Any]:
        """PUT请求"""
        return self.request("PUT", endpoint, json=json_data, **kwargs)
    
    def patch(self, endpoint: str, json_data: Dict = None, **kwargs) -> Dict[str, Any]:
        """PATCH请求"""
        return self.request("PATCH", endpoint, json=json_data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE请求"""
        return self.request("DELETE", endpoint, **kwargs)
    
    def upload_file(self, endpoint: str, file_path: str, 
                    file_field: str = "file",
                    extra_data: Dict = None,
                    **kwargs) -> Dict[str, Any]:
        """
        上传文件
        
        Args:
            endpoint: API端点
            file_path: 本地文件路径
            file_field: 文件字段名
            extra_data: 额外表单数据
            
        Returns:
            API响应数据
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers(need_auth=True)
        # 移除Content-Type，让requests自动设置
        headers.pop("Content-Type", None)
        
        files = {}
        data = extra_data or {}
        
        if os.path.exists(file_path):
            files[file_field] = open(file_path, 'rb')
        else:
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            logger.info(f"上传文件: {file_path}")
            response = self._session.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=self.config.timeout * 3  # 上传超时更长
            )
            
            result = response.json()
            self._handle_error(response, result)
            return result
            
        finally:
            for f in files.values():
                f.close()


class FeishuDriveAPI(FeishuAPIClient):
    """飞书云文档API封装"""
    
    def create_document(self, title: str, folder_token: str = None) -> Dict[str, Any]:
        """
        创建云文档
        
        Args:
            title: 文档标题
            folder_token: 父文件夹token（可选）
            
        Returns:
            创建结果，包含document_id和url
        """
        data = {
            "type": "docx",
            "title": title
        }
        if folder_token:
            data["folder_token"] = folder_token
            
        return self.post("/drive/v1/files/create", json_data=data)
    
    def upload_media(self, file_path: str, file_type: str = "image") -> Dict[str, Any]:
        """
        上传媒体文件（图片等）
        
        Args:
            file_path: 文件路径
            file_type: 文件类型（image等）
            
        Returns:
            上传结果，包含file_token
        """
        return self.upload_file(
            "/drive/v1/medias/upload_all",
            file_path=file_path,
            extra_data={"type": file_type}
        )
    
    def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """获取文档信息"""
        return self.get(f"/docx/v1/documents/{document_id}")
    
    def get_document_blocks(self, document_id: str, page_size: int = 500) -> Dict[str, Any]:
        """
        获取文档内容块
        
        Args:
            document_id: 文档ID
            page_size: 每页数量
            
        Returns:
            文档块列表
        """
        params = {"page_size": page_size}
        return self.get(f"/docx/v1/documents/{document_id}/blocks", params=params)
    
    def batch_update_blocks(self, document_id: str, 
                           requests_data: List[Dict]) -> Dict[str, Any]:
        """
        批量更新文档块
        
        Args:
            document_id: 文档ID
            requests_data: 更新请求列表
            
        Returns:
            更新结果
        """
        data = {"requests": requests_data}
        return self.patch(f"/docx/v1/documents/{document_id}/blocks/batch_update", 
                         json_data=data)


# 便捷函数
def create_client(config_path: str = None, **kwargs) -> FeishuDriveAPI:
    """
    创建飞书API客户端
    
    Args:
        config_path: 配置文件路径
        **kwargs: 直接传入配置参数
        
    Returns:
        FeishuDriveAPI实例
    """
    if config_path:
        return FeishuDriveAPI(config_path)
    else:
        return FeishuDriveAPI(FeishuConfig(**kwargs))


if __name__ == "__main__":
    # 简单测试
    print("飞书API客户端模块已加载")
    print("使用方法:")
    print("  from feishu_api_client import create_client")
    print("  client = create_client('config/feishu_config.json')")
    print("  # 或")
    print("  client = create_client(app_id='xxx', app_secret='xxx')")
