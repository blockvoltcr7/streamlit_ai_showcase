import os

# Get the root directory of the project
root_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the file
file_path = os.path.join(root_dir, "prompts", "choose-media-options.md")

try:
    with open(file_path, "r") as file:
        contents = file.read()
        print(contents)
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
