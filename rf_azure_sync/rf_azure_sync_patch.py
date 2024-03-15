"""
Module: rf_azure_devops_sync_patch

This module provides functionality to synchronize test cases between Robot Framework
and Azure DevOps. It includes classes and functions for extracting, parsing, and updating
test cases in both systems.

Requirements:
- Python 3.x
- requests library

Make sure a 'sync_config.json' file is installed with the required configuration parameters.

Use:
1. Configure 'sync_config.json' with the required settings.
2. Run the script.
"""
import base64
import json
import os
import re
import requests


class TestStep:
    """
    Class representing a test step in Azure DevOps.

    Attributes:
        action (str): The action or instruction for the test step.
        description (str): The description or expected result of the test step.
    """

    def __init__(self, action, description):
        """
        Initializes a TestStep instance.

        Args:
            action (str): The action or instruction for the test step.
            description (str): The description or expected result of the test step.
        """
        self.action = action
        self.description = description
        self.validate()

    def validate(self):
        """
        Validates the TestStep instance.

        Raises:
            ValueError: If the action is not a string.
        """
        if not isinstance(self.action, str):
            raise ValueError("Action must be strings.")

    def to_dict(self, step_id):
        """
        Converts the TestStep instance to a dictionary.

        Args:
            step_id (int): The ID of the test step.

        Returns:
            dict: A dictionary representing the test step in Azure DevOps format.
        """
        return {
            "step": {
                "id": step_id,
                "type": "ActionStep",
                "action": (
                    f'<parameterizedString isformatted="true">'
                    f"&lt;P&gt;{self.action}&lt;BR/&gt;&lt;/P&gt;</parameterizedString>"
                ),
                "expectedResult": (
                    '<parameterizedString isformatted="true">'
                    "&lt;DIV&gt;&lt;P&gt;&lt;BR/&gt;&lt;/P&gt;&lt;/DIV&gt;</parameterizedString>"
                ),
                "description": f"{self.description}",
            }
        }


def load_sync_config(file_path="sync_config.json"):
    """
    Loads synchronization configuration from a JSON file.

    Args:
        file_path (str, optional): The path to the synchronization configuration JSON file.
            Defaults to "sync_config.json".

    Returns:
        dict: A dictionary containing synchronization configuration.
    """
    with open(file_path, "r", encoding="utf-8") as config_file:
        sync_config = json.load(config_file)
    return sync_config


def find_robot_files(folder_path):
    """
    Finds Robot Framework files in the specified folder and its subfolders.

    Args:
        folder_path (str): The path to the folder to search.

    Returns:
        list: A list of paths to Robot Framework files.
    """
    robot_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".robot"):
                robot_files.append(os.path.normpath(os.path.join(root, file)))
    return robot_files

def find_gherkin_files(folder_path):
    """
    Finds Gherkin Feature files in the specified folder and its subfolders.

    Args:
        folder_path (str): The path to the folder to search.

    Returns:
        list: A list of paths to Gherkin Feature files.
    """
    gherkin_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".feature"):
                gherkin_files.append(os.path.normpath(os.path.join(root, file)))
    return gherkin_files


def read_robot_file(file_path):
    """
    Reads the content of a Robot Framework file.

    Args:
        file_path (str): The path to the Robot Framework file.

    Returns:
        str: The content of the Robot Framework file.
    """
    with open(file_path, "r", encoding="utf-8") as rf_file:
        return rf_file.read()

def read_gherkin_file(file_path):
    """
    Reads the content of a Gherkin Feature file.

    Args:
        file_path (str): The path to the Gherkin Feature file.

    Returns:
        str: The content of the Gherkin Feature file.
    """
    with open(file_path, "r", encoding="utf-8") as rf_file:
        return rf_file.read()


def extract_test_tags_and_test_cases(robot_content):
    """
    Extracts test tags and test cases from Robot Framework content.

    Args:
        robot_content (str): The content of a Robot Framework file.

    Returns:
        tuple: A tuple containing raw test cases data and test tags.
    """
    settings_match = re.search(
        r"\*\*\*\s*Settings\s*\*\*\*(.*?)\*\*\*", robot_content, re.DOTALL
    )
    settings_data = settings_match.group(1).strip() if settings_match else ""
    settings_lines = settings_data.split("\n")
    settings_dict = {}
    for line in settings_lines:
        parts = line.split()
        if len(parts) >= 2:
            key = parts[0]
            value = " ".join(parts[1:])
            settings_dict[key] = value
    test_tags_match = re.search(r"Test\s*Tags\s+(.+)", settings_data, re.IGNORECASE)
    case_tags = test_tags_match.group(1).strip() if test_tags_match else None
    case_tags = "; ".join(case_tags.split()) if case_tags else None
    test_cases_match = re.search(
        r"\*\*\*\s*Test Cases\s*\*\*\*(.*?)(?=\*\*\*|$)", robot_content, re.DOTALL
    )
    raw_test_cases_data = test_cases_match.group(1).strip() if test_cases_match else ""
    return raw_test_cases_data, case_tags


def parse_test_cases(raw_test_cases_data, config_settings):
    """
    Parses raw test cases data into a structured format.

    Args:
        raw_test_cases_data (str): Raw test cases data from a Robot Framework file.
        config_settings (dict): Configuration settings.

    Returns:
        list: A list of dictionaries representing parsed test cases.
    """
    test_cases = []
    current_test_case = {}
    lines = raw_test_cases_data.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(config_settings["tag_config"]["title"]):
            if current_test_case:
                test_cases.append(current_test_case)
            current_test_case = {
                "Title": line[len(config_settings["tag_config"]["title"]) :].strip(),
                "Tags": "",
                "Steps": [],
            }
        elif line.startswith("[tags]"):
            current_test_case["Tags"] = line[len("[tags]") :].strip()
        else:
            current_test_case["Steps"].append(line)
    if current_test_case:
        test_cases.append(current_test_case)
    return test_cases


def parse_tags(tag_string):
    """
    Parses test tags from a string.

    Args:
        tag_string (str): The string containing test tags.

    Returns:
        dict: A dictionary representing parsed test tags.
    """
    tag_dict = {}
    categories_and_values = re.findall(r"(\S+)\s*(?::|\s)\s*(\S+)", tag_string)
    for category, value in categories_and_values:
        if category not in tag_dict:
            tag_dict[category] = []
        tag_dict[category].append(value)
    return tag_dict


def transform_steps(steps_list):
    """
    Transforms a list of raw test steps into a list of TestStep objects.

    Args:
        steps_list (list): List of raw test steps.

    Returns:
        list: List of TestStep objects.
    """
    transformed_steps = []
    for step_id, step in enumerate(steps_list, start=1):
        test_step = TestStep(step, step_id)
        transformed_steps.append(test_step)
    return transformed_steps


def extract_tags_info(case_tag, sync_configuration):
    """
    Extracts information from test case tags.

    Args:
        case_tag (dict): Dictionary containing information about test case tags.
        sync_configuration (dict): Configuration settings.

    Returns:
        tuple: A tuple containing automation status tag key, priority tag key, and tags value.
    """
    automation_status_tag_key_match = re.search(
        rf"{sync_configuration['tag_config']['AutomationStatus']}\s*([^\s]+)",
        case_tag["Tags"],
    )
    automation_status_tag_key = (
        automation_status_tag_key_match.group(1)
        .strip()
        .replace("_", " " if automation_status_tag_key_match else None)
    )
    priority_tag_key_match = re.search(
        rf"{sync_configuration['tag_config']['Priority']}\s*([^\s]+)", case_tag["Tags"]
    )
    priority_tag_key = (
        priority_tag_key_match.group(1).strip() if priority_tag_key_match else None
    )
    test_tags_key = case_tag["Tags"].strip() if case_tag["Tags"] else None
    system_tags_key_match = re.search(
        rf"{sync_configuration['tag_config']['System.Tags']}\s*([\w\s]+)",
        case_tag["Tags"],
    )
    system_tags_key = (
        system_tags_key_match.group(1).strip() if system_tags_key_match else None
    )

    tags_value = ""
    if test_tags_key and not system_tags_key:
        tags_value = test_tags_key
    elif system_tags_key and not test_tags_key:
        tags_value = system_tags_key
    elif system_tags_key and test_tags_key:
        tags_value = f"{test_tags_key}; {system_tags_key}"

    return automation_status_tag_key, priority_tag_key, tags_value


def build_iteration_path_tags(iteration_path_tags, sync_configuration):
    """
    Builds the iteration path tags for updating Azure Test Cases.

    Args:
        iteration_path_tags (list): List of iteration path tags.
        sync_configuration (dict): Configuration settings.

    Returns:
        dict: Azure DevOps update operation for iteration path.
    """
    update_iteration_path = None
    iteration_path_tag_candidate_with_spaces = None

    for iteration_path_tag_candidate in iteration_path_tags:
        iteration_path_tag_candidate_with_spaces = iteration_path_tag_candidate.replace(
            "_", " "
        )
        iteration_path_value = (
            f"{sync_configuration['constants']['System.AreaPath']}"
            f"{iteration_path_tag_candidate_with_spaces}"
        )
        update_iteration_path = {
            "op": "replace",
            "path": "/fields/System.IterationPath",
            "value": iteration_path_value,
        }

    return update_iteration_path


def build_linked_items(linked_work_items, organization_name, project_name):
    """
    Builds the linked items for updating Azure Test Cases.

    Args:
        linked_work_items (list): List of linked work items.
        organization_name (str): Azure DevOps organization name.
        project_name (str): Azure DevOps project name.

    Returns:
        list: List of linked items for Azure Test Cases.
    """
    linked_items = []

    for linked_item in linked_work_items:
        linked_items.append(
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "Microsoft.VSTS.Common.TestedBy-Reverse",
                    "url": (
                        f"https://dev.azure.com/{organization_name}/"
                        f"{project_name}/_apis/wit/workitems/{linked_item}"
                    ),
                    "attributes": {"comment": "Associated test case with work item"},
                },
            }
        )

    return linked_items


def build_steps_xml(transformed_steps):
    """
    Builds XML representation of test steps for updating Azure Test Cases.

    Args:
        transformed_steps (list): List of transformed test steps.

    Returns:
        str: XML representation of test steps.
    """
    test_steps = [step.to_dict(i) for i, step in enumerate(transformed_steps, start=1)]
    steps_xml = f'<steps id="0" last="{len(test_steps)}">'
    steps_xml += "".join(
        f'<step id="{step_id}" type="{step["step"]["type"]}">'
        f'{step["step"]["action"]}{step["step"]["expectedResult"]}'
        f"<description/></step>"
        for step_id, step in enumerate(test_steps, start=1)
    )
    steps_xml += "</steps>"
    return steps_xml


def build_fields(data_tags, title, linked_items, transformed_steps):
    """
    Builds the fields for updating Azure Test Cases.

    Args:
        automation_status_tag_key (str): Automation status tag key.
        priority_tag_key (str): Priority tag key.
        tags_value (str): Combined value of test tags.
        title (str): Test case title.
        linked_items (list): List of linked items for Azure Test Cases.
        transformed_steps (list): List of transformed test steps.

    Returns:
        list: List of fields for updating Azure Test Cases.
    """
    steps_xml = build_steps_xml(transformed_steps)
    fields = [
        *filter(
            None,
            [
                {
                    "op": "replace",
                    "path": "/fields/Custom.AutomationStatus",
                    "value": data_tags[0],
                },
                {
                    "op": "replace",
                    "path": "/fields/Microsoft.VSTS.Common.Priority",
                    "value": data_tags[1],
                },
                {
                    "op": "replace",
                    "path": "/fields/System.Title",
                    "value": title,
                },
                {
                    "op": "replace",
                    "path": "/fields/Microsoft.VSTS.TCM.Steps",
                    "value": steps_xml,
                },
                {
                    "op": "replace",
                    "path": "/fields/System.Tags",
                    "value": data_tags[2],
                },
                *linked_items,
            ],
        )
    ]

    return list(filter(lambda x: x["value"] is not None and x["value"] != "", fields))


def update_azure_test_case(
    cases_dict, system_tags, transformed_steps, sync_configuration, linked_work_items
):
    """
    Updates an Azure Test Case with the provided information.

    Args:
        cases_dict (dict): Dictionary containing information about the test case.
        system_tags (str): Tags related to the test case.
        transformed_steps (list): List of transformed test steps.
        sync_configuration (dict): Configuration settings.
        linked_work_items (list): List of linked work items.

    Returns:
        None
    """
    tags = parse_tags(cases_dict["Tags"])
    for test_step in transformed_steps:
        test_step.validate()

    automation_status_tag_key, priority_tag_key, _ = extract_tags_info(
        cases_dict, sync_configuration
    )

    organization_name = sync_configuration["credentials"]["organization_name"]
    project_name = sync_configuration["credentials"]["project_name"]
    personal_access_token = sync_configuration["credentials"]["personal_access_token"]

    title_test_case = cases_dict["Title"]

    test_case_id_match = re.search(r"TestCase\s*(\d+)", cases_dict["Tags"])
    test_case_id = test_case_id_match.group(1) if test_case_id_match else ""

    iteration_path_tags = tags.get(
        sync_configuration["tag_config"]["IterationPath"], []
    )
    build_iteration_path_tags(iteration_path_tags, sync_configuration)

    url = (
        f"https://dev.azure.com/{organization_name}/"
        f"{project_name}/_apis/wit/workitems/{test_case_id}"
        "?api-version=7.2-preview.3"
    )

    linked_items = build_linked_items(
        linked_work_items, organization_name, project_name
    )

    tags_info = [automation_status_tag_key, priority_tag_key, system_tags]

    fields = build_fields(
        tags_info,
        title_test_case,
        linked_items,
        transformed_steps,
    )

    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": "Basic "
        + base64.b64encode(f"{personal_access_token}:".encode()).decode(),
    }
    payload = json.dumps(fields)
    timeout_seconds = 10

    try:
        response = requests.patch(
            url, data=payload, headers=headers, timeout=timeout_seconds
        )
        if response.status_code == 200:
            print("Atualização dos Tests Cases na Azure bem-sucedida!")
        else:
            print(
                f"Erro na atualização dos Tests Cases na Azure. "
                f"Código de status: {response.status_code}"
            )
            print(response.text)

    except requests.Timeout:
        print(
            f"A atualização dos Tests Cases na Azure excedeu o "
            f"tempo limite de {timeout_seconds} segundos."
        )
    except requests.RequestException as e:
        print(f"Erro na atualização dos Tests Cases na Azure: {e}")

def rf_azure_sync_patch():
    """
     This function performs synchronization between the Robot Framework and Azure DevOps.
     It reads Robot Framework files, extracts test cases and tags, and updates
     the corresponding test cases in Azure DevOps.
     """
    config_data = load_sync_config()
    path_robot_files = find_robot_files(config_data["path"])
    for robot_file in path_robot_files:
        if "todo_organize.robot" not in robot_file:
            content = read_robot_file(robot_file)
            test_cases_data, test_tags = extract_test_tags_and_test_cases(content)
            cases = parse_test_cases(test_cases_data, config_data)
            for case in cases:
                print("\n" + "=" * 70)
                # test_case_identifier = (
                #     re.search(r"TestCase\s*(\d+)", case["Tags"]).group(1)
                #     if "TestCase" in case["Tags"]
                #     else "N/A"
                # )
                tags = parse_tags(case["Tags"])
                user_story_ids = tags.get("UserStory", [])
                bug_ids = tags.get("Bug", [])
                linked_item_id = user_story_ids + bug_ids
                steps = transform_steps(case["Steps"])
                update_azure_test_case(case, test_tags, steps, config_data, linked_item_id)

if __name__ == "__main__":
    rf_azure_sync_patch()
