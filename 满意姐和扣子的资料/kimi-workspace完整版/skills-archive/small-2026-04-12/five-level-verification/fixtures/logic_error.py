# 逻辑错误示例
# 用于测试L5端到端验证

def calculate_sum(a, b):
    """错误的加法实现"""
    return a - b  # 应该是加法

def calculate_product(a, b):
    """错误的乘法实现"""
    return a + b  # 应该是乘法

if __name__ == "__main__":
    result = calculate_sum(5, 3)
    print(f"5 + 3 = {result}")  # 会输出 2 而不是 8
