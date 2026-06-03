#!/usr/bin/env python3
"""
secret-manager: 密钥管理
安全存储和检索敏感信息

作者: 满意妞
版本: 1.0.0
日期: 2026-03-28
"""

import os
import json
import base64
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


@dataclass
class SecretEntry:
    """密钥条目"""
    key_id: str
    encrypted_value: str
    salt: str
    created_at: str
    updated_at: str
    access_count: int = 0
    last_accessed: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "key_id": self.key_id,
            "encrypted_value": self.encrypted_value,
            "salt": self.salt,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SecretEntry":
        return cls(
            key_id=data["key_id"],
            encrypted_value=data["encrypted_value"],
            salt=data["salt"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed"),
        )


class SecretManager:
    """
    密钥管理器 - 安全存储和检索敏感信息
    
    功能:
    - 密钥安全存储（加密）
    - 密钥检索（解密）
    - 访问审计
    """
    
    def __init__(
        self,
        storage_path: str = "~/.openclaw/system-v2/secrets",
        master_key: Optional[str] = None,
    ):
        """
        初始化密钥管理器
        
        Args:
            storage_path: 密钥存储路径
            master_key: 主密钥（如不提供，从环境变量获取）
        """
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 主密钥（从环境变量或参数获取）
        self._master_key = master_key or os.environ.get("SECRET_MASTER_KEY")
        if not self._master_key:
            # 首次使用，生成主密钥
            self._master_key = Fernet.generate_key().decode()
            print(f"⚠️  首次使用，生成主密钥。请保存到环境变量: SECRET_MASTER_KEY={self._master_key}")
        
        # 审计日志
        self._audit_log = self.storage_path / "audit.log"
        
        # 加载已有密钥
        self._secrets: Dict[str, SecretEntry] = {}
        self._load_secrets()
    
    def _derive_key(self, salt: bytes) -> bytes:
        """从主密钥派生加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self._master_key.encode()))
        return key
    
    def _encrypt(self, value: str, salt: bytes) -> str:
        """加密值"""
        key = self._derive_key(salt)
        f = Fernet(key)
        encrypted = f.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def _decrypt(self, encrypted_value: str, salt: bytes) -> str:
        """解密值"""
        key = self._derive_key(salt)
        f = Fernet(key)
        encrypted = base64.urlsafe_b64decode(encrypted_value.encode())
        decrypted = f.decrypt(encrypted)
        return decrypted.decode()
    
    def _load_secrets(self):
        """加载已有密钥"""
        secrets_file = self.storage_path / "secrets.json"
        if secrets_file.exists():
            try:
                with open(secrets_file, 'r') as f:
                    data = json.load(f)
                
                for key_id, entry_data in data.items():
                    self._secrets[key_id] = SecretEntry.from_dict(entry_data)
            except Exception as e:
                print(f"[SecretManager] 加载密钥失败: {e}")
    
    def _save_secrets(self):
        """保存密钥"""
        secrets_file = self.storage_path / "secrets.json"
        data = {key_id: entry.to_dict() for key_id, entry in self._secrets.items()}
        
        # 原子写入
        temp_file = secrets_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        temp_file.replace(secrets_file)
    
    def _log_audit(self, action: str, key_id: str, success: bool):
        """记录审计日志"""
        timestamp = datetime.now().isoformat()
        status = "SUCCESS" if success else "FAILURE"
        log_entry = f"{timestamp} | {action} | {key_id} | {status}\n"
        
        with open(self._audit_log, 'a') as f:
            f.write(log_entry)
    
    def store(self, key_id: str, value: str) -> Tuple[bool, str]:
        """
        存储密钥
        
        Args:
            key_id: 密钥标识
            value: 密钥值
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 生成随机盐值
            salt = secrets.token_bytes(16)
            salt_b64 = base64.urlsafe_b64encode(salt).decode()
            
            # 加密
            encrypted = self._encrypt(value, salt)
            
            # 创建条目
            now = datetime.now().isoformat()
            entry = SecretEntry(
                key_id=key_id,
                encrypted_value=encrypted,
                salt=salt_b64,
                created_at=now,
                updated_at=now,
            )
            
            # 保存
            self._secrets[key_id] = entry
            self._save_secrets()
            
            # 审计日志
            self._log_audit("STORE", key_id, True)
            
            return True, f"密钥已存储: {key_id}"
            
        except Exception as e:
            self._log_audit("STORE", key_id, False)
            return False, f"存储失败: {e}"
    
    def retrieve(self, key_id: str) -> Tuple[bool, str]:
        """
        检索密钥
        
        Args:
            key_id: 密钥标识
            
        Returns:
            (成功标志, 密钥值或错误消息)
        """
        if key_id not in self._secrets:
            self._log_audit("RETRIEVE", key_id, False)
            return False, f"密钥不存在: {key_id}"
        
        try:
            entry = self._secrets[key_id]
            
            # 解密
            salt = base64.urlsafe_b64decode(entry.salt.encode())
            value = self._decrypt(entry.encrypted_value, salt)
            
            # 更新访问记录
            entry.access_count += 1
            entry.last_accessed = datetime.now().isoformat()
            self._save_secrets()
            
            # 审计日志
            self._log_audit("RETRIEVE", key_id, True)
            
            return True, value
            
        except Exception as e:
            self._log_audit("RETRIEVE", key_id, False)
            return False, f"检索失败: {e}"
    
    def delete(self, key_id: str) -> Tuple[bool, str]:
        """
        删除密钥
        
        Args:
            key_id: 密钥标识
            
        Returns:
            (成功标志, 消息)
        """
        if key_id not in self._secrets:
            return False, f"密钥不存在: {key_id}"
        
        del self._secrets[key_id]
        self._save_secrets()
        
        self._log_audit("DELETE", key_id, True)
        return True, f"密钥已删除: {key_id}"
    
    def list_keys(self) -> list:
        """列出所有密钥标识"""
        return list(self._secrets.keys())
    
    def get_audit_log(self, limit: int = 100) -> list:
        """获取审计日志"""
        if not self._audit_log.exists():
            return []
        
        with open(self._audit_log, 'r') as f:
            lines = f.readlines()
        
        return [line.strip() for line in lines[-limit:]]


def main():
    """CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Secret Manager - 密钥管理")
    parser.add_argument("--store", type=str, help="存储密钥（key_id）")
    parser.add_argument("--value", type=str, help="密钥值")
    parser.add_argument("--retrieve", type=str, help="检索密钥（key_id）")
    parser.add_argument("--delete", type=str, help="删除密钥（key_id）")
    parser.add_argument("--list", action="store_true", help="列出所有密钥")
    parser.add_argument("--audit", action="store_true", help="显示审计日志")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 请运行: python3 -m pytest test_secret_manager.py")
        return
    
    manager = SecretManager()
    
    if args.store:
        if not args.value:
            print("❌ 需要 --value 参数")
            exit(1)
        success, msg = manager.store(args.store, args.value)
        print(f"{'✅' if success else '❌'} {msg}")
        exit(0 if success else 1)
    
    elif args.retrieve:
        success, value = manager.retrieve(args.retrieve)
        if success:
            print(f"✅ 密钥值: {value}")
        else:
            print(f"❌ {value}")
        exit(0 if success else 1)
    
    elif args.delete:
        success, msg = manager.delete(args.delete)
        print(f"{'✅' if success else '❌'} {msg}")
        exit(0 if success else 1)
    
    elif args.list:
        keys = manager.list_keys()
        if keys:
            print("📋 密钥列表:")
            for key in keys:
                print(f"  • {key}")
        else:
            print("📭 无密钥")
    
    elif args.audit:
        logs = manager.get_audit_log()
        if logs:
            print("📋 审计日志:")
            for log in logs:
                print(f"  {log}")
        else:
            print("📭 无审计日志")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
