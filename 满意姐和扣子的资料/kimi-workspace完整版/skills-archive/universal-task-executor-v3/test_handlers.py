import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/universal-task-executor-v3')

print("=== Universal Task Executor V3.0 - 处理器加载测试 ===\n")

handlers = [
    ('C1 Cron', 'handlers.category1_cron_handler', 'Category1CronHandler'),
    ('C2 TEE', 'handlers.category2_tee_handler', 'Category2TEEHandler'),
    ('C3 Skill', 'handlers.category3_skill_handler', 'Category3SkillHandler'),
    ('C4 Conversation', 'handlers.category4_conversation_handler', 'Category4ConversationHandler'),
    ('C5 Document', 'handlers.category5_document_handler', 'Category5DocumentHandler'),
    ('C6 Mechanism', 'handlers.category6_mechanism_handler', 'Category6MechanismHandler'),
]

success_count = 0
for name, module_path, class_name in handlers:
    try:
        module = __import__(module_path, fromlist=[class_name])
        handler_class = getattr(module, class_name)
        handler = handler_class()
        print(f"✅ {name}: {handler.handler_name} v{handler.version}")
        print(f"   Categories: {handler.supported_categories}")
        success_count += 1
    except Exception as e:
        print(f"❌ {name}: {e}")

print(f"\n=== 结果: {success_count}/6 处理器加载成功 ===")
