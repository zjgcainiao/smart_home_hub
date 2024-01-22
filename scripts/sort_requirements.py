# Read, sort, and write back to requirements.txt
url_requirements='/Users/stephenwang/smart_home_hub/requirements.txt'
try:
    with open(url_requirements, 'r') as file:
        lines = file.readlines()
        lines = sorted(lines)

    with open(url_requirements, 'w') as file:
        file.writelines(lines)
    print("Requirements sorted successfully.")
except FileNotFoundError:
    print("File not found. Please check the file path.")
except Exception as e:
    print("An error occurred:", str(e))
