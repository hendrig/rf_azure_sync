"""
Module: rf_azure_sync

Description: This module provides synchronization functionalities for Azure-related tasks.
"""

import sys
import subprocess
import json
import os

def run_sync_get():
    """
    Run the synchronization process for getting data from Azure.
    """
    subprocess.run(["python", "rf_azure_sync_get.py"], check=True)

def run_sync_patch():
    """
    Run the synchronization process for patching data to Azure.
    """
    subprocess.run(["python", "rf_azure_sync_patch.py"], check=True)

def run_robot_tests(tests_folder):
    """
    Run Robot Framework tests with a specific tag in the specified folder.

    :param tests_folder: The folder containing the Robot Framework tests.
    """
    subprocess.run(["robot", "--include", "Automation_Status Automated", tests_folder], check=True)

def create_sync_config():
    """
    Create the sync_config.json file interactively.
    """
    print("The sync_config.json file was not found. Let's create it.")

    # Gather information interactively
    tests_folder = input("Folder with Robot Framework tests to be synchronized (default: tests): ")
    personal_access_token = input("Azure personal access token with read and write permission: ")
    organization_name = input("Organization name (the one that comes after https://dev.azure.com/): ")
    project_name = input(f"Project name (the one after https://dev.azure.com/{organization_name}/): ")
    test_case = input("Prefix used to identify the Test Case id example (TC, TestCase): ")
    user_story = input("Prefix used to identify the User Story id related to the Test Case example (US, UserStory): ")
    bug = input("Prefix used to identify the Bug id related to the Test Case example (Bug): ")
    title = input("Prefix used to identify the title of the Test Case example(Title, Scenario): ")
    tested_by_reverse = input("Reverse the 'Tested By' relationship between Test Cases and User Stories: ")
    iteration_path = input("Azure DevOps field for Iteration Path: ")
    automation_status = input("Azure DevOps field for Automation Status: ")
    ignore_sync = input("Azure DevOps field to mark Test Cases that should be ignored during synchronization: ")
    system_tags = input("Azure DevOps field for System Tags: ")
    priority = input("Azure DevOps field for Priority: ")
    area_path = input("Azure DevOps field for Area Path: ")
    team_project = input("Azure DevOps field for Team Project: ")
    settings_section = input("Section in the Robot Framework settings file to store Azure-related settings: ")
    test_cases_section = input("Section in the Robot Framework settings file to store synchronized Test Cases: ")


    # Populate the sync_config structure
    sync_config = {
        "path": tests_folder,
        "credentials": {
            "personal_access_token": personal_access_token,
            "organization_name": organization_name,
            "project_name": project_name
        },
        "tag_config": {
            "test_case": test_case,
            "user_story": user_story,
            "bug": bug,
            "title": title,
            "TestedBy-Reverse": tested_by_reverse,
            "IterationPath": iteration_path,
            "AutomationStatus": automation_status,
            "ignore_sync": ignore_sync,
            "System.Tags": system_tags,
            "Priority": priority
        },
        "constants": {
            "System.AreaPath": area_path,
            "System.TeamProject": team_project,
            "settings_section": settings_section,
            "test_cases_section": test_cases_section
        }
    }

    # Save the sync_config.json file
    with open("sync_config.json", "w", encoding="utf-8") as config_file:
        json.dump(sync_config, config_file, indent=2)

    print("sync_config.json created successfully.")

def main():
    """
    Main entry point of the synchronization script.

    If no command-line arguments are provided, it runs both sync_get and sync_patch.
    If 'get' is provided as an argument, only sync_get is executed.
    If 'patch' is provided as an argument, only sync_patch is executed.

    Additionally, if sync_config.json is present and contains the tests folder path,
    it runs Robot Framework tests with the tag 'Automation_Status Automated' in that folder.

    If sync_config.json is not found, create it interactively.
    """
    if not os.path.isfile("sync_config.json"):
        create_sync_config()

    if len(sys.argv) == 1:
        run_sync_get()
        run_sync_patch()

        config_path = 'sync_config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as config_file:
                config_data = json.load(config_file)
                tests_folder = config_data.get('path', '')
                if tests_folder:
                    run_robot_tests(tests_folder)
                else:
                    print("Tests folder path not specified in sync_config.json.")
        else:
            print("sync_config.json not found.")
    elif len(sys.argv) == 2:
        if sys.argv[1] == "get":
            run_sync_get()
        elif sys.argv[1] == "patch":
            run_sync_patch()
        else:
            print("Invalid argument. Use 'get' or 'patch'.")
    else:
        print("Usage: python rf_azure_sync.py [get | patch]")

if __name__ == "__main__":
    main()
