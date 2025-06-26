from StateController import State


def test_list_updated_tasks() -> None:
    test_task = [{'area': '2nN2ynMGK84cyws9AZKLo6',
                    'area_title': 'Home',
                    'created': '2025-06-08 00:00:00',
                    'deadline': None,
                    'index': -2060,
                    'modified': '2025-06-08 16:29:59',
                    'notes': '',
                    'reminder_time': '15:00',
                    'start': 'Anytime',
                    'start_date': '2025-06-16',
                    'status': 'incomplete',
                    'stop_date': None,
                    'tags': ['30m'],
                    'title': 'Test Item Updated',
                    'today_index': 4920975,
                    'type': 'to-do',
                    'uuid': '12345',
                    }]
    
    updated_task = [{'area': '2nN2ynMGK84cyws9AZKLo6',
                    'area_title': 'Home',
                    'created': '2025-06-08 00:00:00',
                    'deadline': None,
                    'index': -2060,
                    'modified': '2025-06-08 16:29:59',
                    'notes': '',
                    'reminder_time': '15:00',
                    'start': 'Anytime',
                    'start_date': '2025-06-17',
                    'status': 'incomplete',
                    'stop_date': None,
                    'tags': ['30m'],
                    'title': 'Test Item Updated',
                    'today_index': 4920975,
                    'type': 'to-do',
                    'uuid': '12345',
                    }]
    
    state = State()
    state.current_tasks = test_task
    updated_tasks = updated_task
    print(State.list_updated_tasks(state, updated_tasks))