"""
Config Manager - 系统配置管理
统一管理 system.toml / production.toml / local.toml
"""

import os
import tomllib
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """加载、合并、验证多层配置"""

    DEFAULT_PATHS = [
        "config/system.toml",
        "config/production.toml",
        "config/local.toml",
    ]

    def __init__(self, workspace: Optional[str] = None):
        self.workspace = Path(workspace or "/root/.openclaw/workspace")
        self.config: Dict[str, Any] = {}
        self._load()

    def _load(self):
        for rel in self.DEFAULT_PATHS:
            p = self.workspace / rel
            if p.exists():
                try:
                    with open(p, "rb") as f:
                        data = tomllib.load(f)
                    self._deep_update(self.config, data)
                except Exception as e:
                    raise RuntimeError(f"Failed to load {p}: {e}")

    def _deep_update(self, base: dict, overlay: dict):
        for k, v in overlay.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_update(base[k], v)
            else:
                base[k] = v

    def get(self, key_path: str, default=None):
        """支持点号路径，如 'cognitive_resilience.default_tier'"""
        parts = key_path.split(".")
        node = self.config
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return default
        return node

    def require(self, key_path: str):
        val = self.get(key_path)
        if val is None:
            raise KeyError(f"Required config key missing: {key_path}")
        return val

    def as_dict(self) -> dict:
        return self.config
