import os
import hashlib
from sharedutils import stdlog
from datetime import datetime

def md5(file_path, chunk_size=8192):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def remove_duplicate_files(directory):
    files_hash = {}
    duplicates = []

    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_hash = md5(file_path)
            
            if file_hash in files_hash:
                duplicates.append(file_path)
            else:
                files_hash[file_hash] = file_path

    for duplicate in duplicates:
        os.remove(duplicate)
        stdlog("Removed duplicate file: " + duplicate.replace(directory,''))

    stdlog("Duplicate removal complete.")

if __name__ == "__main__":
    start_time = datetime.now()  # Capture start time
    print(
    '''
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
     /  ************  \     ransomwhat?      /  ************  \ 
    --------------------                    --------------------
    '''
    )
    directory_to_check = "./source/"
    remove_duplicate_files(directory_to_check)
    end_time = datetime.now()  # Capture end time
    duration = end_time - start_time  # Calculate duration
    stdlog("Script execution time: " + str(duration.total_seconds()) + " seconds")

