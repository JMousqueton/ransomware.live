#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib.util
import os
import argparse
import sys
import fcntl
import traceback
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import stdlog, errlog, screenshot
import time
import threading
# For logging the time
import json
from datetime import datetime


# Load environment variables from ../.env
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

# Paths from environment variables
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))
lock_file_path = Path(tmp_dir) / "parse.lock"

execution_time_path = Path(tmp_dir) / "execution_times.json"

def acquire_lock():
    """
    Acquires a lock to prevent simultaneous script execution.

    Returns:
        file: The lock file object.
    """
    lock_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure TMP_DIR exists
    lock_file = open(lock_file_path, "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Acquire exclusive non-blocking lock
        lock_file.write(f"PID: {os.getpid()}\n")
        lock_file.flush()
        stdlog(f"Update lock file {lock_file_path} with PID {os.getpid()}")
        return lock_file
    except BlockingIOError:
        errlog("Another instance of the script is already running.")
        errlog(f"{lock_file_path}")
        sys.exit(1)

def release_lock(lock_file):
    """
    Releases the lock file.

    Args:
        lock_file (file): The lock file object.

    Returns:
        None
    """
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()

def remove_lock_file():
    """
    Removes the lock file if it exists.

    Returns:
        None
    """
    if lock_file_path.exists():
        lock_file_path.unlink()
        stdlog("Previous lock removed.")

def execute_main(file_path, execution_data, run_date):
    """
    Dynamically imports a Python file, executes its `main` function, and logs execution time.

    Args:
        file_path (str): Path to the Python script to execute.
        execution_data (dict): Dictionary storing execution times.
        run_date (str): Date of script execution (YYYY-MM-DD).
    """
    try:
        module_name = os.path.splitext(os.path.basename(file_path))[0]

        # Update lock file with script details
        with open(lock_file_path, "w") as lock_file:
            lock_file.write(f"PID: {os.getpid()}\n")
            lock_file.write(f"SCRIPT: {module_name}\n")
            stdlog(f"Update lock file {lock_file_path} with module {module_name}")

        # Measure execution time
        start_time = time.time()
        
        # Load and execute the module
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "main") and callable(module.main):
            module.main()
        else:
            errlog(f"File {file_path} does not have a callable main() function.")

        end_time = time.time()
        execution_duration = round(end_time - start_time, 2)  # Time in seconds

        # Store execution time
        if run_date not in execution_data:
            execution_data[run_date] = {}

        execution_data[run_date][module_name] = execution_duration

    except Exception as e:
        errlog(f"Error executing {file_path}: {e}")
        traceback.print_exc()



def main():
    """
    Parses arguments and executes `main` functions in ./parsers/ directory.
    Logs execution times in JSON.
    """
    print(
    r'''
       _______________                        |*\_/*|________
      |  ___________  |                      ||_/-\_|______  |
      | |           | |                      | |           | |
      | |   0   0   | |                      | |   0   0   | |
      | |     -     | |                      | |     -     | |
      | |   \___/   | |                      | |   \___/   | |
      | |___     ___| |                      | |___________| |
      |_____|\_/|_____|                      |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                          / ********** \ 
     /  ************  \   ransomware.live     /  ************  \ 
    --------------------                    --------------------
    '''
    )   
    start_time = time.time()
    parser = argparse.ArgumentParser(description="Execute all main functions in ./parsers/ or a specific one.")
    parser.add_argument("-G", "--group", help="Specify the group (parser's filename without .py) to execute.", default=None)
    parser.add_argument("-F", "--force", help="Force remove previous lock and run the script", action="store_true")
    args = parser.parse_args()

    # Generate execution date (static for the entire run)
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Handle lock mechanism
    lock_file = None
    if args.force:
        remove_lock_file()
    lock_file = acquire_lock()

    # Load previous execution times from JSON (if exists)
    if execution_time_path.exists():
        with open(execution_time_path, "r") as json_file:
            try:
                execution_data = json.load(json_file)
            except json.JSONDecodeError:
                execution_data = {}  # Reset if file is corrupted
    else:
        execution_data = {}

    try:
        parsers_dir = "./_parsers"
        if not os.path.isdir(parsers_dir):
            errlog(f"The directory {parsers_dir} does not exist.")
            return

        if args.group:
            # Execute only the specified group
            file_path = os.path.join(parsers_dir, f"{args.group}.py")
            if os.path.isfile(file_path):
                stdlog(f"Parsing {Path(file_path).stem}...")
                execute_main(file_path, execution_data, run_date)
            elif os.path.isfile(os.path.join(parsers_dir, f"{args.group}-api.py")):
                stdlog(f"Parsing {Path(file_path).stem} with API Parser...")
                execute_main(os.path.join(parsers_dir, f"{args.group}-api.py"), execution_data, run_date)
            else:
                errlog(f"No file named {args.group}.py found in {parsers_dir}.")
        else:
            # Get all .py files in the directory
            parsers = [
                file_name for file_name in sorted(os.listdir(parsers_dir))
                if file_name.endswith(".py") and os.path.isfile(os.path.join(parsers_dir, file_name))
            ]
            total_parsers = len(parsers)

            # Run each parser with counter
            for index, file_name in enumerate(parsers, start=1):
                stdlog(f"[{index}/{total_parsers}] Parsing {Path(file_name).stem}...")
                execute_main(os.path.join(parsers_dir, file_name), execution_data, run_date)

    finally:
        # Save execution times to JSON file
        with open(execution_time_path, "w") as json_file:
            json.dump(execution_data, json_file, indent=4)

        if lock_file:
            release_lock(lock_file)
        remove_lock_file()
        end_time = time.time()
        runtime_minutes = (end_time - start_time) / 60
        stdlog(f"Script finished. Total runtime: {runtime_minutes:.2f} minutes.")

if __name__ == "__main__":
    main()
