from __future__ import annotations
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
import shutil

class ClawCloudStorage:
    """
    Kimi Claw 云存储管理器（本地降级版）
    将数据持久化到 workspace 本地目录，无需 /app 权限
    """
    
    def __init__(self, user_id: str = "default", quota_gb: int = 40):
        self.user_id = user_id
        self.quota = quota_gb * 1024 * 1024 * 1024  # 转换为字节
        # 降级到本地 workspace，无需 /app 权限
        self.storage_root = Path(f"/root/.openclaw/workspace/claw_data/storage/{user_id}")
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.storage_root / ".storage_meta.json"
        
        # 加载元数据
        self.meta = self._load_meta()
    
    def _load_meta(self) -> dict:
        if self.meta_file.exists():
            with open(self.meta_file, 'r') as f:
                return json.load(f)
        return {"files": {}, "total_size": 0}
    
    def _save_meta(self):
        with open(self.meta_file, 'w') as f:
            json.dump(self.meta, f)
    
    async def save_file(self, file_name: str, content: bytes or str, folder: str = "") -> str:
        target_dir = self.storage_root / folder
        target_dir.mkdir(exist_ok=True)
        
        file_path = target_dir / file_name
        
        mode = 'wb' if isinstance(content, bytes) else 'w'
        with open(file_path, mode) as f:
            f.write(content)
        
        file_size = file_path.stat().st_size
        file_hash = hashlib.md5(content if isinstance(content, bytes) else content.encode()).hexdigest()
        
        self.meta["files"][f"{folder}/{file_name}"] = {
            "size": file_size,
            "hash": file_hash,
            "path": str(file_path)
        }
        self.meta["total_size"] += file_size
        self._save_meta()
        
        return f"claw://storage/{self.user_id}/{folder}/{file_name}"
    
    async def read_file(self, file_uri: str) -> bytes:
        path_parts = file_uri.replace("claw://storage/", "").split("/")
        relative_path = "/".join(path_parts[1:])
        
        file_path = self.storage_root / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_uri}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def get_usage(self) -> Dict:
        return {
            "total_quota_gb": self.quota / (1024**3),
            "used_gb": self.meta["total_size"] / (1024**3),
            "remaining_gb": (self.quota - self.meta["total_size"]) / (1024**3),
            "file_count": len(self.meta["files"]),
            "files": list(self.meta["files"].keys())
        }
    
    def list_skills_data(self) -> List[str]:
        return [f for f in self.meta["files"] if f.startswith("skills/")]

if __name__ == '__main__':
    import asyncio
    storage = ClawCloudStorage()
    uri = asyncio.run(storage.save_file("test.txt", "Hello from claw_cloud_storage", "demo"))
    print("Saved:", uri)
    print(json.dumps(storage.get_usage(), ensure_ascii=False, indent=2))
