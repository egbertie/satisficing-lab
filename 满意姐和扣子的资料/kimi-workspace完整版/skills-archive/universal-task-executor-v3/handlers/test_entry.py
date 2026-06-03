

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run tests')
    args = parser.parse_args()
    
    if args.test:
        print("=== Category1 Cron Handler Test ===")
        handler = Category1CronHandler()
        print(f"Handler loaded: {handler.handler_name} v{handler.version}")
        print(f"Categories: {handler.supported_categories}")
        
        # Test task execution
        test_task = {
            "task_id": "test-cron-001",
            "name": "Test Cron Job",
            "category": "category_1",
            "priority": "p1",
            "content": {
                "schedule": "0 9 * * *",
                "command": "echo 'test'",
                "description": "Test cron job"
            }
        }
        
        result = handler.execute(test_task)
        print(f"Task execution: {result['status']}")
        print(f"Cost estimation: {handler.estimate_cost(test_task)} tokens")
        print("=== Test Complete ===")
