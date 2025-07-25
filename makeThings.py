from pprint import pprint
import webbrowser
import config


def make_new_task(title: str = None,
                  completed: bool = False, 
                  cancelled: bool = False, 
                  show_quick_entry: bool = False, 
                  reveal: bool = False, 
                  notes: str = None, 
                  checklist_items: list = None,
                  when: str = None,
                  deadline: str = None,
                  tags: list = None,
                  list: str = None,
                  heading: str = None,
                  creation_date: str = None,
                  completion_date: str = None) -> None:
    
    arguments = locals()
    
    if show_quick_entry == True:
        arguments.pop('show_quick_entry')    
        arguments['show-quick-entry'] = True
    
    if checklist_items != None:
        checklist = arguments.pop('checklist_items')    
        arguments['checklist-items'] = '\n'.join(checklist)
    
    if checklist_items != None:
        arguments['tags'] = ','.join(tags)    
    
    parameters = [f"{k}={v}" for k, v in arguments.items() if v != None]
    params = '&'.join(parameters)
    
    base_url = "things:///add?"
    webbrowser.open(base_url+params)


def update_task(auth_token: str,
                task_id: str, 
                title: str = None,
                completed: bool = False, 
                cancelled: bool = False, 
                reveal: bool = False,
                duplicate: bool = None,
                prepend_notes: str = None, 
                append_notes: str = None, 
                checklist_items: list = None,
                when: str = None,
                deadline: str = None,
                tags: list = None,
                list: str = None,
                heading: str = None,
                creation_date: str = None,
                completion_date: str = None) -> None:
    
    arguments = locals()
    token = arguments.pop('auth_token')    
    arguments['auth-token'] = token
    id = arguments.pop('task_id')
    arguments['id'] = id    
    
    if prepend_notes == True:
        arguments.pop('prepend_notes')    
        arguments['prepend-notes'] = True
    
    if append_notes == True:
        arguments.pop('append_notes')    
        arguments['append-notes'] = True
    
    if checklist_items != None:
        checklist = arguments.pop('checklist_items')    
        arguments['checklist-items'] = '\n'.join(checklist)
    
    if checklist_items != None:    
        arguments['tags'] = ','.join(tags)    
    
    parameters = [f"{k}={v}" for k, v in arguments.items() if v != None]
    params = '&'.join(parameters)
    
    base_url = "things:///update?"
    webbrowser.open(base_url+params)


