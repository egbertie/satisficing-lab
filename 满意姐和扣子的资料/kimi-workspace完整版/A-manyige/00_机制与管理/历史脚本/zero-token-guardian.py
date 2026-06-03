#!/usr/bin/env python3
"""
零Token进程守护 - 检测Claw中断并自动保存
零API调用，纯本地psutil监控
"""

import os
import time
import json
import signal
import tarfile
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[GUARDIAN] 警告: psutil未安装，进程监控不可用")

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

class ZeroTokenGuardian:
    def __init__(self):
        self.claw_pid = None
        self.vault_path = os.path.expanduser("~/.openclaw/immortal-state")
        self.running = True
        self.last_seen = 0
        
        os.makedirs(f"{self.vault_path}/emergency", exist_ok=True)
        
    def find_claw_process(self):
        if not PSUTIL_AVAILABLE:
            return None
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info.get('name', '') or ''
                cmdline = proc.info.get('cmdline') or []
                if 'claw' in name.lower() or any('claw' in str(c).lower() for c in cmdline):
                    return proc.info['pid']
            except:
                pass
        return None
    
    def emergency_save(self):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = f"{self.vault_path}/emergency/interrupt-{timestamp}"
        
        # 保存中断标记
        flag_file = f"{self.vault_path}/.interrupted"
        with open(flag_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "pid": self.claw_pid,
                "status": "interrupted",
                "auto_save": True
            }, f)
        
        # 后台执行紧急备份
        base_dir = os.path.expanduser("~/.openclaw")
        tar_path = f"{backup_path}.tar.zst" if ZSTD_AVAILABLE else f"{backup_path}.tar.gz"
        
        def do_backup():
            try:
                if ZSTD_AVAILABLE:
                    cctx = zstd.ZstdCompressor(level=1)  # 快速压缩
                    with open(tar_path, 'wb') as f:
                        with cctx.stream_writer(f) as compressor:
                            with tarfile.open(fileobj=compressor, mode='w|') as tar:
                                tar.add(f"{base_dir}/workspace", arcname="workspace")
                else:
                    with tarfile.open(tar_path, 'w:gz') as tar:
                        tar.add(f"{base_dir}/workspace", arcname="workspace")
                print(f"[GUARDIAN] ✅ 紧急备份完成: {tar_path}")
            except Exception as e:
                print(f"[GUARDIAN] ⚠️  备份失败: {e}")
        
        import threading
        threading.Thread(target=do_backup, daemon=True).start()
        print(f"[GUARDIAN] 🚨 检测到中断，已触发紧急保存: {timestamp}")
    
    def generate_micro_summary(self):
        """生成<300 tokens的极简恢复摘要"""
        workspace = os.path.expanduser("~/.openclaw/workspace")
        
        # 极简结构
        summary = {
            "t": datetime.now().strftime("%m%d-%H:%M"),  # 时间
            "f": 0,  # 文件数
            "a": [],  # 动作
            "p": []   # 待办
        }
        
        # 统计文件
        try:
            summary["f"] = len([f for f in os.listdir(workspace) if os.path.isfile(os.path.join(workspace, f))])
        except:
            pass
        
        # 检查TODO文件
        todo_file = f"{workspace}/.todo"
        if os.path.exists(todo_file):
            try:
                with open(todo_file) as f:
                    summary["p"] = [l.strip() for l in f if l.strip() and not l.startswith('#')][:3]
            except:
                pass
        
        # 检查内存文件
        memory_file = f"{workspace}/memory/{datetime.now().strftime('%Y-%m-%d')}.md"
        if os.path.exists(memory_file):
            summary["a"].append("memory-updated")
        
        # 超紧凑序列化
        compact = f"{{t:{summary['t']},f:{summary['f']},a:{summary['a']},p:{summary['p']}}}"
        
        # 确保<300字符
        if len(compact) > 300:
            compact = compact[:297] + "...}"
        
        # 保存
        resume_file = f"{self.vault_path}/micro-context.txt"
        with open(resume_file, 'w') as f:
            f.write(f"RESUME:{compact}\n")
            f.write(f"CMD:恢复上下文，继续工作\n")
        
        return compact
    
    def monitor(self):
        print("[GUARDIAN] 零Token进程守护已启动")
        print("[GUARDIAN] 监控Claw进程，中断时自动保存")
        
        while self.running:
            current_pid = self.find_claw_process()
            
            if self.claw_pid and not current_pid:
                # Claw退出
                if time.time() - self.last_seen < 30:  # 30秒内消失视为中断
                    self.emergency_save()
                    self.generate_micro_summary()
                self.claw_pid = None
                
            elif not self.claw_pid and current_pid:
                # Claw启动
                self.claw_pid = current_pid
                self.last_seen = time.time()
                print(f"[GUARDIAN] Claw已连接 (PID: {current_pid})")
                
                # 清理中断标记
                flag_file = f"{self.vault_path}/.interrupted"
                if os.path.exists(flag_file):
                    os.remove(flag_file)
                    print("[GUARDIAN] 已清理中断标记")
            
            if current_pid:
                self.last_seen = time.time()
            
            time.sleep(3)  # 每3秒检查
    
    def stop(self, signum=None, frame=None):
        print("[GUARDIAN] 停止监控")
        self.running = False

if __name__ == "__main__":
    if not PSUTIL_AVAILABLE:
        print("请先安装psutil: pip install psutil")
        exit(1)
    
    guardian = ZeroTokenGuardian()
    signal.signal(signal.SIGTERM, guardian.stop)
    signal.signal(signal.SIGINT, guardian.stop)
    
    try:
        guardian.monitor()
    except KeyboardInterrupt:
        guardian.stop()
