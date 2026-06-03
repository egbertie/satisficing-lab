#!/usr/bin/env python3
"""
零Token实时文件监控 - 替代Cron轮询
使用inotify事件驱动，零API调用
"""

import os
import sys
import time
import json
import tarfile
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

class ZeroTokenMonitor(FileSystemEventHandler):
    def __init__(self):
        self.vault_path = os.path.expanduser("~/.openclaw/immortal-state")
        self.checkpoint_dir = f"{self.vault_path}/checkpoints"
        self.last_snapshot = 0
        self.min_interval = 300  # 5分钟防抖
        self.changed_files = set()
        
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
    def on_modified(self, event):
        if event.is_directory:
            return
        if any(x in event.src_path for x in ["/workspace/", "/config/", "/skills/"]):
            self.changed_files.add(event.src_path)
            self.trigger_checkpoint()
    
    def on_created(self, event):
        if not event.is_directory:
            if any(x in event.src_path for x in ["/workspace/", "/config/", "/skills/"]):
                self.changed_files.add(event.src_path)
                self.trigger_checkpoint()
    
    def trigger_checkpoint(self):
        now = time.time()
        if now - self.last_snapshot < self.min_interval:
            return
        self.last_snapshot = now
        
        if not self.changed_files:
            return
            
        self.create_checkpoint()
        self.changed_files.clear()
    
    def create_checkpoint(self):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base_dir = os.path.expanduser("~/.openclaw")
        
        # 使用zstd压缩（更快更好）
        if ZSTD_AVAILABLE:
            ext = "tar.zst"
            cctx = zstd.ZstdCompressor(level=3, threads=2)
            snapshot_path = f"{self.checkpoint_dir}/cpt-event-{timestamp}.{ext}"
            
            with open(snapshot_path, 'wb') as f:
                with cctx.stream_writer(f) as compressor:
                    with tarfile.open(fileobj=compressor, mode='w|') as tar:
                        tar.add(f"{base_dir}/workspace", arcname="workspace")
                        tar.add(f"{base_dir}/config", arcname="config")
        else:
            ext = "tar.gz"
            snapshot_path = f"{self.checkpoint_dir}/cpt-event-{timestamp}.{ext}"
            with tarfile.open(snapshot_path, 'w:gz') as tar:
                tar.add(f"{base_dir}/workspace", arcname="workspace")
                tar.add(f"{base_dir}/config", arcname="config")
        
        # 更新索引
        self.update_index(timestamp, snapshot_path, len(self.changed_files))
        
        size_mb = os.path.getsize(snapshot_path) / 1024 / 1024
        print(f"[ZERO-TOKEN] ✅ 事件驱动检查点: {timestamp} ({size_mb:.1f}MB, {len(self.changed_files)} files)")
        
        # 清理旧检查点（保留20个）
        self.cleanup_old_checkpoints()
    
    def update_index(self, timestamp, path, file_count):
        index_file = f"{self.checkpoint_dir}/index.json"
        try:
            with open(index_file, 'r') as f:
                index = json.load(f)
        except:
            index = {"checkpoints": []}
        
        index["checkpoints"].append({
            "timestamp": timestamp,
            "path": path,
            "file_count": file_count,
            "type": "event",
            "created": datetime.now().isoformat()
        })
        
        # 只保留最近20个
        index["checkpoints"] = index["checkpoints"][-20:]
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def cleanup_old_checkpoints(self):
        pattern = "cpt-event-*"
        import glob
        files = sorted(glob.glob(f"{self.checkpoint_dir}/{pattern}"), 
                      key=os.path.getmtime, reverse=True)
        for old_file in files[20:]:
            try:
                os.remove(old_file)
            except:
                pass
    
    def run(self):
        observer = Observer()
        paths = [
            os.path.expanduser("~/.openclaw/workspace"),
            os.path.expanduser("~/.openclaw/config")
        ]
        
        for path in paths:
            if os.path.exists(path):
                observer.schedule(self, path, recursive=True)
                print(f"[ZERO-TOKEN] 监控: {path}")
        
        observer.start()
        print("[ZERO-TOKEN] 事件驱动监控已启动（零Token）")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    monitor = ZeroTokenMonitor()
    monitor.run()
