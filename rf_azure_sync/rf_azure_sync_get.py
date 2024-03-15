"""
This script facilitates the synchronization of test cases between Robot Framework and Azure DevOps.
It performs the extraction of test cases from Robot Framework content, 
queries Azure DevOps for new test cases, and subsequently updates the 
Robot Framework content with the newly obtained test cases.

Requirements:
- Python 3.x
- requests library

Ensure that a 'sync_config.json' file is in place with the required configuration parameters.

Usage:
1. Configure 'sync_config.json' with the necessary settings.
2. Run the script.
"""
import json
import re
import os
from html import unescape
from collections import namedtuple
import base64
import requests


def extract_test_tags_and_test_cases(rf_content):
    """
    Extract test tags and test cases from Robot Framework content.

    Args:
        rf_content (str): Robot Framework content.

    Returns:
        Tuple[str, str]: A tuple containing raw test cases data and case tags.
    """
    settings_match = re.search(
        r"\*\*\*\s*Settings\s*\*\*\*(.*?)\*\*\*", rf_content, re.DOTALL
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
        r"\*\*\*\s*Test Cases\s*\*\*\*(.*?)(?=\*\*\*|$)", rf_content, re.DOTALL
    )
    raw_test_cases_data = test_cases_match.group(1).strip() if test_cases_match else ""
    return raw_test_cases_data, case_tags

def extract_test_tags_and_test_cases_for_features(rf_content):
    """
    Extract test tags and test cases from Robot Framework content.

    Args:
        rf_content (str): Robot Framework content.

    Returns:
        Tuple[str, str]: A tuple containing raw test cases data and case tags.
    """
    settings_match = re.search(
        r"\*\*\*\s*@\s*\*\*\*(.*?)\*\*\*", rf_content, re.DOTALL
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
    test_tags_match = re.search(r"@\s+(.+)", settings_data, re.IGNORECASE)
    case_tags = test_tags_match.group(1).strip() if test_tags_match else None
    case_tags = "; ".join(case_tags.split()) if case_tags else None
    test_cases_match = re.search(
        r"\*\*\*\s*Test Cases\s*\*\*\*(.*?)(?=\*\*\*|$)", rf_content, re.DOTALL
    )
    raw_test_cases_data = test_cases_match.group(1).strip() if test_cases_match else ""
    return raw_test_cases_data, case_tags

def parse_test_cases(raw_test_cases_data, config_settings):
    """
    Parse test cases from Robot Framework data.

    Args:
        raw_test_cases_data (str): The data containing test cases.
        config_settings (dict): Configuration data for synchronization.

    Returns:
        List[dict]: A list of dictionaries representing parsed test cases.
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


def load_sync_config(file_path="sync_config.json"):
    """
    Load synchronization configuration from a JSON file.

    Args:
        file_path (str, optional): The path to the synchronization configuration JSON file.
            Defaults to "sync_config.json".

    Returns:
        dict: A dictionary containing synchronization configuration.
    """
    with open(file_path, "r", encoding="utf-8") as config_file:
        sync_config = json.load(config_file)
    return sync_config


def get_azure_test_cases(base_url, headers_wiql):
    """
    Retrieve Azure test cases based on the given Wiql query.

    Args:
        base_url (str): The base URL for Azure DevOps REST API.
        headers_wiql (dict): Headers for the Wiql request.

    Returns:
        set: A set of Azure test case IDs.
    """
    url_wiql = f"{base_url}wiql?api-version=7.1-preview.2"

##{config_settings["constants"]["System.AreaPath"]}
    query = {
        "query": "SELECT [System.Id] "
        "FROM WorkItems "
        "WHERE [System.AreaPath] = 'LOG.co\\Transportation\\Core Transportes\\Squad Bino' "
        "AND [System.WorkItemType] = 'Test Case' "
    }

    response_wiql = requests.post(
        url_wiql, json=query, headers=headers_wiql, timeout=10
    )

    if response_wiql.status_code == 200:
        data_wiql = response_wiql.json()
        return set(test_case["id"] for test_case in data_wiql["workItems"])

    # Return an empty set if the request was not successful
    return set()


def read_robot_file(rf_folder_path, file_path):
    """
    Read the contents of a Robot Framework file.

    Args:
        file_path (str): The path to the Robot Framework file.

    Returns:
        str: The contents of the Robot Framework file.
    """

    file_path = f"{rf_folder_path}/{file_path}"
    with open(file_path, "r", encoding="utf-8") as rf_file:
        return rf_file.read()
    
def read_feature_file(rf_folder_path, file_path):
    """
    Read the contents of a Robot Framework file.

    Args:
        file_path (str): The path to the Robot Framework file.

    Returns:
        str: The contents of the Robot Framework file.
    """

    file_path = f"{rf_folder_path}/{file_path}"
    with open(file_path, "r", encoding="utf-8") as rf_file:
        return rf_file.read()


def create_robot_content(fields, pref_config):
    """
    Create Robot Framework content based on Azure DevOps work item fields.

    Args:
        fields (dict): Azure DevOps work item fields.
        pref_config (dict): Prefix configuration for tags.

    Returns:
        str: Robot Framework content.
    """
    WorkItemDetails = namedtuple(
        "WorkItemDetails",
        ["id", "title", "iteration_path", "priority", "automation_status", "sprint"],
    )

    def get_tags_line(work_item_details):
        tags_line = (
            f"    [tags]  {prefix_test_case} {work_item_details.id}    "
            f"{prefix_automation_status} {work_item_details.automation_status}    "
            f"{prefix_priority} {work_item_details.priority}    "
            f"{prefix_iteration_path} {work_item_details.sprint}"
        )

        tags_line += get_tags(fields)
        tags_line += get_relations_tags(fields)
        tags_line += "\n"

        return tags_line

    def get_steps_and_expected_results(steps_raw):
        steps_and_expected_results = re.findall(
            r'<step id="\d+" type=".*?">'
            r'<parameterizedString isformatted="true">(.*?)</parameterizedString>'
            r'<parameterizedString isformatted="true">(.*?)</parameterizedString>'
            r"<description/></step>",
            steps_raw,
            re.DOTALL,
        )

        return steps_and_expected_results

    def get_tags(fields):
        tags_line = ""
        if "System.Tags" in fields and fields["System.Tags"] is not None:
            tags_list = [tag.strip() for tag in prefix_system_tags.split(";")]
            tags_line += "    " + "    ".join(
                f"{prefix_system_tags} {tag}" for tag in tags_list
            )
        return tags_line

    def get_relations_tags(fields):
        tags_line = ""
        if "relations" in fields:
            relations = fields["relations"]
            for relation in relations:
                if "url" in relation and "_apis/wit/workItems/" in relation["url"]:
                    us_id = re.search(
                        r"_apis/wit/workItems/(\d+)", relation["url"]
                    ).group(1)
                    tags_line += f"    {prefix_user_story} {us_id}"
        return tags_line

    work_item_details = WorkItemDetails(
        id=fields.get("System.Id", ""),
        title=fields.get("System.Title", ""),
        iteration_path=fields.get("System.IterationPath", ""),
        priority=fields.get("Microsoft.VSTS.Common.Priority", ""),
        automation_status=fields.get("Custom.AutomationStatus", ""),
        sprint=fields.get("Sprint", "").replace(" ", "_"),
    )

    tags_line = get_tags_line(work_item_details)

    rf_content = f"\n {pref_config['title']}: {work_item_details.title}\n"
    rf_content += tags_line

    steps_raw = fields.get("Microsoft.VSTS.TCM.Steps", "")
    steps_and_expected_results = get_steps_and_expected_results(steps_raw)

    for _, (step, _) in enumerate(steps_and_expected_results, start=1):
        step = unescape(re.sub("<[^<]+?>", "", step.strip()))
        step = step.replace("<P>", "").replace("</P>", "")
        step = step.replace("<DIV>", "").replace("</DIV>", "")
        step = step.replace("<BR>", "").replace("<BR/>", "")

        if step:
            rf_content += f"    {step}\n"
    rf_content += "\n"

    return rf_content


def get_robot_test_case_ids(rf_folder_path, pref_test_case, config):
    """
    Retrieve Robot Framework test case IDs from files in the specified folder.

    Args:
        rf_folder_path (str): The path to the folder containing Robot Framework files.
        pref_test_case (str): The prefix for identifying test cases in tags.
        config (dict): Configuration data for synchronization.

    Returns:
        set: A set of Robot Framework test case IDs.
    """
    rf_test_case_ids = set()

    print("Starting to sync files.")
    print(f"Paths: {rf_folder_path}")

    for _, _, files in os.walk(rf_folder_path):
        for rf_file in files:
            if rf_file.endswith(".robot"):
                content = read_robot_file(rf_folder_path, rf_file)
                test_cases_data, _ = extract_test_tags_and_test_cases(content)
                cases = parse_test_cases(test_cases_data, config)
                rf_test_case_ids.update(
                    int(re.search(rf"{pref_test_case}\s*(\d+)", case["Tags"]).group(1))
                    for case in cases
                    if re.search(rf"{pref_test_case}\s*(\d+)", case["Tags"])
                )
            if rf_file.endswith(".feature"):
                content = read_feature_file(rf_folder_path, rf_file)
                test_cases_data, _ = extract_test_tags_and_test_cases(content)
                cases = parse_test_cases(test_cases_data, config)
                rf_test_case_ids.update(
                    int(re.search(rf"{pref_test_case}\s*(\d+)", case["Tags"]).group(1))
                    for case in cases
                    if re.search(rf"{pref_test_case}\s*(\d+)", case["Tags"])
                )

    return rf_test_case_ids

def rf_azure_sync_get():
    """
    Synchronize Azure test cases with Robot Framework.

    This function retrieves Azure test cases, identifies new test cases that are not present in the Robot Framework,
    and updates the Robot Framework file with the new test cases.

    Note: Make sure to replace the placeholder comments with actual implementations.
    """
    print(f"Starting to sync {url}")
    print(f"Headers {headers}")

    azure_test_cases = get_azure_test_cases(url, headers)

    robot_test_case_ids = get_robot_test_case_ids(
        robot_folder_path, prefix_test_case, config_data
    )
    new_test_case_ids = azure_test_cases - robot_test_case_ids
    response_json_list = []
    for test_case_id in new_test_case_ids:
        if test_case_id not in robot_test_case_ids:
            url_workitems = (
                f"{url}workitems?ids={test_case_id}&$expand=all&api-version=7.1-preview.3"
            )
            response_workitems = requests.get(url_workitems, headers=headers, timeout=10)
            if response_workitems.status_code == 200:
                data_workitems = response_workitems.json()
                work_item = data_workitems["value"][0]["fields"]
                print(f"ID: {test_case_id}, Title: {work_item['System.Title']}")
                response_json_list.append(data_workitems)
            else:
                print(
                    f"Error in request: "
                    f"{response_workitems.status_code} - {response_workitems.text}"
                )
    robot_content: str = ""
    for response_json in response_json_list:
        work_item = response_json["value"][0]["fields"]
        robot_content += create_robot_content(work_item, prefix_config)

    file_name = os.path.join(robot_folder_path, "todo_organize.robot")

    existing_content:str = ""

    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as existing_file:
            existing_content = existing_file.read()

    if not existing_content or (
        settings_section not in existing_content
        and test_cases_section not in existing_content
    ):
        existing_content += settings_section + test_cases_section

    if robot_content:
        existing_content += robot_content

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(existing_content)

    print(f"Robot Framework file '{file_name}' updated successfully.")

config_data = load_sync_config()
robot_folder_path = config_data["path"]
constants = config_data["constants"]
credentials = config_data["credentials"]
prefix_config = config_data["tag_config"]
settings_section = constants["settings_section"]
test_cases_section = constants["test_cases_section"]
personal_access_token = credentials["personal_access_token"]
organization = credentials["organization_name"]
project = credentials["project_name"]
prefix_user_story = prefix_config["user_story"]
prefix_system_tags = prefix_config["System.Tags"]
prefix_priority = prefix_config["Priority"]
prefix_test_case = prefix_config["test_case"]
url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/"
headers = {
    "Authorization": "Basic "
    + base64.b64encode(f"{personal_access_token}:".encode()).decode(),
}
prefix_automation_status = prefix_config["AutomationStatus"]
prefix_iteration_path = prefix_config["IterationPath"]

if __name__ == "__main__":
    rf_azure_sync_get()
