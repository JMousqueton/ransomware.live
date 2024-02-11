import os
import json

def check_parser_file_exists(location_name):
    lowercase_name = location_name.lower()
    file_path = os.path.join("parsers", f"{lowercase_name}.py")
    return os.path.exists(file_path)

def main():
    print("begin check ...")
    with open("groups.json", "r") as json_file:
        data = json.load(json_file)
    # Loop through the data and print the 'name' variable for each item
    for item in data:
        group_name = item["name"] 
        if check_parser_file_exists(group_name):
            print(f"Parser file for group '{group_name}' exists.")
            item["parser"] = True
        else:
            print(f"Parser file for group '{group_name}' does not exist.")
            item["parser"] = False
    
    with open("groups.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    main()

