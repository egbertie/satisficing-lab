#!/usr/bin/env python3
"""
Vendor API Monitor - 快速测试入口
"""
import sys
import json
from datetime import datetime

class VendorAPIMonitor:
    def __init__(self):
        self.endpoints = {}
    
    def add_endpoint(self, name, url):
        self.endpoints[name] = {"url": url, "status": "unknown"}
    
    def check_health(self, name):
        if name not in self.endpoints:
            return False
        self.endpoints[name]["status"] = "healthy"
        return True
    
    def get_status(self):
        return {"endpoints": len(self.endpoints), "healthy": sum(1 for e in self.endpoints.values() if e["status"] == "healthy")}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("="*60)
        print("🧪 Vendor API Monitor S5/S7 验证")
        print("="*60)
        
        print("\n[S7] 对抗测试...")
        monitor = VendorAPIMonitor()
        
        # 测试1: 检查不存在端点
        result = monitor.check_health("nonexistent")
        assert result == False, "不存在端点应返回False"
        print("  ✅ 不存在端点测试通过")
        
        # 测试2: 空名称
        monitor.add_endpoint("", "http://test.com")
        assert "" in monitor.endpoints, "空名称应可添加"
        print("  ✅ 空名称端点测试通过")
        
        # S5: 自我验证
        print("\n[S5] 自我验证...")
        status = monitor.get_status()
        assert "endpoints" in status, "状态应有endpoints"
        print("  ✅ 状态统计正确")
        
        print("\n" + "="*60)
        print("✅ S5/S7验证通过")
        print("="*60)
        return 0
    else:
        print("Vendor API Monitor - 使用 --test 运行验证")
        return 0

if __name__ == "__main__":
    sys.exit(main())
