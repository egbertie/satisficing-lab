# benchmark_token_saver.py
async def benchmark_claw_response():
    """
    对比正常模式 vs 文言文模式的性能
    """
    test_task = "写一个Python词频统计函数+单元测试+运行"
    
    # 测试A：正常模式
    normal_result = await claw.execute(
        test_task,
        system_prompt="You are a helpful assistant.",
        track_tokens=True
    )
    
    # 测试B：文言文模式
    classical_result = await claw.execute(
        test_task,
        system_prompt="汝以文言作答。惜字如金。",
        track_tokens=True
    )
    
    print(f"""
    === Token节省实测对比 ===
    正常模式:
      - Token消耗: {normal_result.tokens}
      - 耗时: {normal_result.duration}s
      - 工具调用: {normal_result.tool_calls}
      
    文言文模式:
      - Token消耗: {classical_result.tokens} (-{(1-classical_result.tokens/normal_result.tokens)*100:.0f}%)
      - 耗时: {classical_result.duration}s (-{(1-classical_result.duration/normal_result.duration)*100:.0f}%)
      - 工具调用: {classical_result.tool_calls}
      
    预期效果: Token -11%, 速度 -59%, 工具调用 -33%
    """)

# 运行测试
# python benchmark_token_saver.py
