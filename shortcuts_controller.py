import subprocess
import time


def run_shortcut(shortcut_name: str, params: dict) -> None: 
    
    url_encoded_name: str = ...
    
    url = f"shortcuts://run-shortcut?name={url_encoded_name}"

    subprocess.run(['open', url])
    


def make_new_reminder_shortcut(task_name: str, due_date, due_time, task_list: str, things_uuid: str) -> None:
    ...



if __name__ == "__main__": 
    
    TEST_URL: str = f"shortcuts://run-shortcut?name=ThingSyncTest"
    

    for i in range(5):
        run_shortcut(TEST_URL)
        time.sleep(0.1)

    