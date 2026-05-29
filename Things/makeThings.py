import subprocess
import logging


def make_new_task(title: str = ...,
				  completed: bool = False, 
				  cancelled: bool = False, 
				  show_quick_entry: bool = False, 
				  reveal: bool = False, 
				  notes: str = ..., 
				  checklist_items: list = ...,
				  when: str = ...,
				  deadline: str = ...,
				  tags: list = ...,
				  list: str = ...,
				  heading: str = ...,
				  creation_date: str = ...,
				  completion_date: str = ...) -> None:
	
	arguments = locals()
	
	if show_quick_entry:
		arguments.pop('show_quick_entry')    
		arguments['show-quick-entry'] = True
	
	if checklist_items != Ellipsis:
		checklist = arguments.pop('checklist_items')    
		arguments['checklist-items'] = '\n'.join(checklist)
	
	if tags != Ellipsis:
		arguments['tags'] = ','.join(tags)    
	
	parameters = [f"{k}={v}" for k, v in arguments.items() if v != Ellipsis]
	params = '&'.join(parameters)
	base_url = "things:///add?reveal=False&"
	
	subprocess.run(['open', f"{base_url + params}"])
	
	heading: str = "NEW TASK CREATED BY MAKETHINGS"
	logging.info(f"""\n\n{heading:-^54}
\tTitle: {title}
\tDatetime: {when}\n""")


def update_task(auth_token: str,
				task_id: str, 
				title: str = ...,
				completed: bool = False, 
				cancelled: bool = False, 
				reveal: bool = False,
				show: bool = False,
				duplicate: bool = ...,
				prepend_notes: str = ..., 
				append_notes: str = ..., 
				checklist_items: list = ...,
				when: str = ...,
				deadline: str = ...,
				tags: list = ...,
				list: str = ...,
				heading: str = ...,
				creation_date: str = ...,
				completion_date: str = ...) -> None:
	
	arguments = locals()
	token = arguments.pop('auth_token')    
	arguments['auth-token'] = token
	id = arguments.pop('task_id')
	arguments['id'] = id    
	
	if prepend_notes != Ellipsis:
		arguments.pop('prepend_notes')    
		arguments['prepend-notes'] = prepend_notes
	
	if append_notes != Ellipsis:
		arguments.pop('append_notes')    
		arguments['append-notes'] = append_notes
	
	if checklist_items != Ellipsis:
		checklist = arguments.pop('checklist_items')    
		arguments['checklist-items'] = '\n'.join(checklist)
	
	if tags != Ellipsis:    
		arguments['tags'] = ','.join(tags)    
	
	parameters = [f"{k}={v}" for k, v in arguments.items() if v != Ellipsis]
	params = '&'.join(parameters)
	base_url = "things:///update?reveal=False&"
	
	subprocess.run(['open', f"{base_url + params}"])

	heading: str = "TASK UPDATED BY MAKETHINGS"
	logging.info(f"""\n\n{heading:-^54}
\tTitle: {title}
\tuuid: {task_id}
\tDatetime: {when}\n""")
	


