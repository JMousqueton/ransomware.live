#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import psutil
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

# Validate environment variables
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir_env = os.getenv("TMP_DIR")

if not home or not tmp_dir_env:
    print("⚠️ Environment variables RANSOMWARELIVE_HOME or TMP_DIR are missing.")
    sys.exit(1)

# Paths
home_path = Path(home).expanduser().resolve()
tmp_dir = home_path / Path(tmp_dir_env).name
parsers_dir = home_path / "bin/_parsers"

# Lock files to check
LOCK_FILES = [tmp_dir / "scrape.lock", tmp_dir / "parse.lock"]

def read_lock_file(lock_file):
    """Reads PID and script name from the lock file."""
    if not lock_file.exists():
        return None, None

    pid, script_name = None, None
    try:
        with lock_file.open("r") as f:
            for line in f:
                if line.startswith("PID:"):
                    pid_str = line.partition(":")[2].strip()
                    try:
                        pid = int(pid_str)
                    except ValueError:
                        print(f"⚠️ Invalid PID format in {lock_file}: {pid_str}")
                        return None, None
                elif line.startswith("SCRIPT:"):
                    script_name = line.partition(":")[2].strip()
    except Exception as e:
        print(f"⚠️ Error reading {lock_file}: {e}")
    
    return pid, script_name

def get_process_info(pid):
    """Returns process details including uptime, CPU, and memory usage."""
    try:
        proc = psutil.Process(pid)
        start_time = proc.create_time()

        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        cpu_usage = proc.cpu_percent(interval=0.1)
        memory_usage = proc.memory_percent()

        return {
            "running_since": f"{minutes}:{seconds:02d}",
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage
        }
    except psutil.NoSuchProcess:
        return None
    except Exception as e:
        print(f"⚠️ Error retrieving process info for PID {pid}: {e}")
        return None

def is_script_running(script_basename):
    """Check if a Python process is running the expected script."""
    expected_script = f"{script_basename}.py"
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if "python" in proc.info["name"].lower():
                cmdline = proc.info["cmdline"]
                if cmdline and expected_script in " ".join(cmdline):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def main(clean_mode=False):
    """Main function to check lock files and process information."""
    print("\n🔍 Checking lock files and process statuses...\n")

    for lock_file in LOCK_FILES:
        print(f"📂 Checking {lock_file}...")
        script_basename = lock_file.stem  # e.g. "scrape" from "scrape.lock"

        if not lock_file.exists():
            # Check if the script is still running
            if is_script_running(script_basename):
                print(f"   🔴 Lock file missing, but script '{script_basename}.py' is running!")
            else:
                print(f"   ⏸️ Lock file not found. Script '{script_basename}.py' is not running.")
            print("-" * 40)
            continue

        # Lock file exists
        pid, script_name = read_lock_file(lock_file)

        if pid is None:
            print("   ⚠️ Lock file exists but is invalid or incomplete.")
            print("-" * 40)
            continue

        print(f"✅ Found PID: {pid}")
        process_info = get_process_info(pid)

        if process_info:
            print(f"   🕛 Uptime: {process_info['running_since']} min | 🔥 CPU: {process_info['cpu_usage']}% | 💾 Mem: {process_info['memory_usage']:.2f}%")

            if script_name:
                last_modified = time.time() - lock_file.stat().st_mtime
                print(f"   📜 Running Script: {script_name} (Last modified {int(last_modified)} sec ago)")
            elif lock_file.name == 'parse.lock':
                print("   🌕 Could not determine which script is running.")
        else:
            print("   ⏸️ Process is not running.")
            if clean_mode:
                try:
                    lock_file.unlink()
                    print(f"   🧹 Lock file {lock_file} deleted.")
                except Exception as e:
                    print(f"   🔴 Failed to delete lock file: {e}")
        print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check and manage Ransomware.live lock files.")
    parser.add_argument("--clean", action="store_true", help="Automatically delete orphan lock files (no associated process)")

    args = parser.parse_args()
    main(clean_mode=args.clean)
