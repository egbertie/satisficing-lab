from __future__ import annotations

def get_token_saver_prompt(mode: str = "auto") -> str:
    """
    根据模式返回对应的系统提示词追加内容
    """
    prompts = {
        "caveman": (
            "You are now in CAVEMAN MODE. Rules:\n"
            '1. No filler words. No "I\'d be happy to help". No "Let me search".\n'
            "2. Do first, explain later (if needed).\n"
            "3. Max 2-3 words per tool response.\n"
            "4. Format: [Action]. [Result]. Done.\n"
            '5. Example: "Tool work. Found 3 items. Done."'
        ),
        "classical_chinese": (
            "汝今以文言作答。戒律如下：\n"
            '1. 凡回复，惜字如金，不赘不饰。去"好的""明白""让我来"等废话。\n'
            "2. 先行后言，果先因后。工具调用后直接给结果，不加解释。\n"
            '3. 事毕则止，无"希望对您有帮助"等客套。\n'
            "4. 测通则云\"三测皆通\"，索毕则云\"索毕\"，码成则云\"码成\"。\n"
            "5. 例：正常模式180token，汝须45token内毕。\n"
            "6. 若无必要，勿增实体。"
        ),
        "hybrid": (
            "MODE: Ultra-terse communication.\n"
            "Chinese: Use classical Chinese style (文言文), 1-2 characters where possible.\n"
            "English: Use caveman style, 1-2 words.\n"
            "No politeness. No explanations. Action → Result → Stop."
        )
    }
    return prompts.get(mode, prompts["hybrid"])


def auto_inject_to_claw(user_message: str, current_system_prompt: str) -> str:
    """
    自动检测用户意图并注入省Token指令
    """
    trigger_words = ['快', '速度', '省token', 'token', '限额', '额度',
                     '慢', '优化', '提速', '效率', 'caveman', 'verbose']

    should_optimize = any(w in user_message.lower() for w in trigger_words)

    if should_optimize:
        is_chinese = any('\u4e00' <= c <= '\u9fff' for c in user_message)
        mode = "classical_chinese" if is_chinese else "caveman"
        injection = get_token_saver_prompt(mode)
        return current_system_prompt + "\n\n" + "=" * 20 + "\n" + injection

    return current_system_prompt


if __name__ == '__main__':
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else "帮我省token，快速回复"
    base_prompt = "You are a helpful assistant."
    result = auto_inject_to_claw(msg, base_prompt)
    print(result)
    print("\n--- 注入长度增加:", len(result) - len(base_prompt), "chars ---")
