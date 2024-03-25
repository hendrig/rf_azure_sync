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
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

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

def get_steps_and_expected_results(steps_raw):
    soup = BeautifulSoup(steps_raw, 'html.parser')
    xml_removed = soup.get_text(separator=' ')
    soup = BeautifulSoup(xml_removed, 'html.parser')
    plain_text = soup.get_text(separator=' ')

    plain_text_with_escape = plain_text.replace("     ", "\n")
    # Define the regular expression pattern to match any word following '@'
    pattern = r'@(\w+)'

    # Define the replacement pattern using a backreference (\1) to include the matched word
    replacement = r'<\1>'

    # Use re.sub() to perform the replacement
    plain_text_with_escape_and_tags = re.sub(pattern, replacement, plain_text_with_escape)

    return plain_text_with_escape_and_tags

def get_test_case(test_case_id):	
    url_workitems = (	
        f"{url}wit/workitems/{test_case_id}?$expand=relations&api-version=7.1-preview.3"	
    )

    response_workitems = requests.get(url_workitems, headers=headers, timeout=10)
    if response_workitems.status_code == 200:	
        data_workitems = response_workitems.json()	
        work_item = data_workitems["fields"]
        wi_relations = []

        if data_workitems.get("relations") is not None:
            relations = data_workitems["relations"]
            for relation in relations:
                match = re.search(r'/(\d+)$', relation["url"])
                if match:
                    wi_relation = match.group(1)
                    wi_relations.append(wi_relation)
        
        print(f"ID: {test_case_id}, Title: {work_item['System.Title']}")

        test_case_title = work_item['System.Title']
        raw_steps = work_item["Microsoft.VSTS.TCM.Steps"]
        raw_params = ""
        
        if work_item.get("Microsoft.VSTS.TCM.Parameters") is not None:
            raw_params = work_item["Microsoft.VSTS.TCM.Parameters"]
            root = ET.fromstring(raw_params)

            # Find the 'param' element and get its 'name' attribute
            param_names = [param.attrib['name'] for param in root.findall('param')]

        raw_examples = ""
        my_params_dict = {}
        if work_item.get("Microsoft.VSTS.TCM.LocalDataSource") is not None:
            raw_examples = work_item["Microsoft.VSTS.TCM.LocalDataSource"]
            root = ET.fromstring(raw_examples)
            for param in param_names:
                status_texts = [status.text for status in root.findall(f".//{param}")]
                my_params_dict[f"{param}"] = status_texts

        steps = get_steps_and_expected_results(raw_steps)

        result = f"@tc:{test_case_id}\n"

        for r in wi_relations:
            result += f"@wi:{r}\n"

        if len(my_params_dict)> 0:
            transposed = transpose_dict(my_params_dict)
            formated = format_transposed_dict(transposed, param_names)
            result += f"Esquema do Cenário: {test_case_title} \n"
            result += f"{steps} \n"
            result += "\nExemplos: \n"
            result += f"{formated} \n"
        else:
            result += f"Cenário: {test_case_title} \n"
            result += f"{steps} \n"

        return result
    else:	
        print(
            f"Error in request: "	
            f"{response_workitems.status_code} - {response_workitems.text}"	
        )

def transpose_dict(dict_to_transpose):
    # Transpose the dictionary
    transposed_dict = {}
    for key, values in dict_to_transpose.items():
        for index, value in enumerate(values):
            transposed_dict.setdefault(index, {})[key] = value
    return transposed_dict

def format_transposed_dict(transposed_dict, params):
    headers = '   |'
    for header in params:
        headers += f" {header} |"

    rows = ""
    for key, line in transposed_dict.items():
        rowN = '   |'
        for param in params:
            rowN += f" {line.get(param)} |" if line.get(param) is not None else " |"
        rows += rowN + "\n"
    return headers + "\n" + rows

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

    main_test_plan_id = config_data["constants"]["TestPlanId"]	
    test_suites = f"{url}testplan/Plans/{main_test_plan_id}/suites"	

    print(f"Consulting {test_suites}")

    response_wiql = requests.get(	
        test_suites, headers=headers, timeout=10	
    )

    if response_wiql.status_code == 200:	
        data = response_wiql.json()	

        for item in data["value"]:
            print(f"Syncing {item['id']} {item['name']}")
            suite_id = item["id"]
            suite_name = item["name"]
            create_file = False
            file_content = ''

            response_test_cases = requests.get(item["_links"]["testCases"]["href"], headers=headers, timeout=10)	
            if response_test_cases.status_code == 200:	
                test_cases = response_test_cases.json()
                formated_test_cases = []

                if test_cases["count"] > 0:
                    for test_case in test_cases["value"]:
                        wi = test_case["workItem"]["id"]
                        name = test_case["workItem"]["name"]
                        print(f"Syncing {wi} {name}")
                        formated_test_case = get_test_case(test_case["workItem"]["id"])
                        formated_test_cases.append(formated_test_case)
                    create_file = True

            if create_file:
                # create file
                file_content = f"#language:pt \n"
                file_content += f"@suiteId:{suite_id} \n"
                file_content += f"Funcionalidade: {suite_name} \n"
                file_content += "\n\n"
                for tc in formated_test_cases:
                    file_content += f"{tc} \n"

                file_name = os.path.join(robot_folder_path, f"{suite_id}.feature")
                existing_content:str = ""

                if os.path.exists(file_name):	
                    with open(file_name, "r", encoding="utf-8") as existing_file:	
                        existing_content = existing_file.read()	

                # if not existing_content or (	
                #     settings_section not in existing_content	
                #     and test_cases_section not in existing_content	
                # ):	
                #     existing_content += settings_section + test_cases_section	

                # if robot_content:	
                #     existing_content += robot_content	

                with open(file_name, "w", encoding="utf-8") as file:	
                    file.write(file_content)	

                print(f"Feature file '{file_name}' updated successfully.")	

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