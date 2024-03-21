import os
import fnmatch
from parse_and_send import convert_and_send

def find_feature_files(folder):
    """
    Find all .feature files in the given folder and its subfolders.

    Args:
    - folder: Path to the folder to search in.

    Returns:
    - List of paths to .feature files.
    """
    feature_files = []
    # Get the absolute path of the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Combine the script directory with the provided folder name
    folder_path = os.path.join(script_dir, folder)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if fnmatch.fnmatch(file, '*.feature'):
                feature_files.append(os.path.join(root, file))
    return feature_files

# Example usage:
folder_path = 'features'
feature_files = find_feature_files(folder_path)
for file_path in feature_files:
    convert_and_send(file_path)
    print(file_path)