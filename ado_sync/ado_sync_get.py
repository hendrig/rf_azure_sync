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

def load_sync_config(file_path="ado_config.json"):
    """
    Load synchronization configuration from a JSON file.

    Args:
        file_path (str, optional): The path to the synchronization configuration JSON file.
            Defaults to "sync_config.json".

    Returns:
        dict: A dictionary containing synchronization configuration.
    """
    print("Starting")
    with open(file_path, "r", encoding="utf-8") as config_file:
        sync_config = json.load(config_file)
    return sync_config

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


def get_test_case(test_case_id):
    url_workitems = (
        f"{url}wit/workitems?ids={test_case_id}&$expand=all&api-version=7.1-preview.3"
    )
    response_json_list = []
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

def get_azure_test_cases():
    """
    Retrieve Azure test cases based on the given a Test Suite.

    Args:
        base_url (str): The base URL for Azure DevOps REST API.
        headers_wiql (dict): Headers for the Wiql request.

    Returns:
        set: A set of Azure test case IDs.
    """
    
    print(f"Starting to sync {url}")
    print(f"Headers {headers}")
    # print(f"Headers {config_data}")

    main_test_plan_id = config_data["constants"]["TestPlanId"]
    test_suites = f"{url}testplan/Plans/{main_test_plan_id}/suites"

    print(f"Consulting {test_suites}")

    response_wiql = requests.get(
        test_suites, headers=headers, timeout=10
    )

    print(f"Status Code {response_wiql.status_code}")

    if response_wiql.status_code == 200:
        data = response_wiql.json()
        
        for item in data["value"]:
            print("Suite Id: ", item["id"])
            print("Name", item["name"])

            response_test_cases = requests.get(item["_links"]["testCases"]["href"], headers=headers, timeout=10)
            print(f"Status Code {response_test_cases.status_code}")
            if response_test_cases.status_code == 200:
                test_cases = response_test_cases.json()

                if test_cases["count"] > 0:
                    for test_case in test_cases["value"]:
                        print("WI: ", test_case["workItem"]["id"])
                        print("TestCase: ", test_case["workItem"]["name"])
                        get_test_case(test_case["workItem"]["id"])
            print("\n")
        #print(data)

    # # Return an empty set if the request was not successful
    # return set()

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
url = f"https://dev.azure.com/{organization}/{project}/_apis/"
headers = {
    "Authorization": "Basic "
    + base64.b64encode(f"{personal_access_token}:".encode()).decode(),
}
prefix_automation_status = prefix_config["AutomationStatus"]
prefix_iteration_path = prefix_config["IterationPath"]

if __name__ == "__main__":
    get_azure_test_cases()