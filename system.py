import subprocess
import logging
import os

def caffeinate() -> None:
    PID = os.getpid()
    logging.debug(f"Caffeinating process number {PID}...")
    subprocess.Popen(['caffeinate', '-s', '-w', str(PID)])
    logging.debug(f"Caffeination successfull for process {PID}")
    