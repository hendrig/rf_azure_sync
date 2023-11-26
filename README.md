# rf_azure_sync

## Overview

This Python package provides synchronization capabilities for Azure-related tasks. Includes scripts to get data from Test Cases from Azure (`rf_azure_sync_get.py`), to Azure (`rf_azure_sync_patch.py`), and to run Robot Framework tests with specific tags.

## Installation

To install `rf_azure_sync`, you can use `pip`. Open a terminal and run:

```bash
pip instalar rf_azure_sync
```
# Usage
## Synchronization
To sync data to Azure, you can use the following commands:

```bash
#Run synchronize_get and synchronize_patch
rf_azure_sync

#Just run sync_get
rf_azure_sync get

#Run sync_patch only
rf_azure_sync patch
```

## Robot Framework Tests
When running rf_azure_sync without extension it will use the tests folder path configured in sync_config.json to run Robot Framework tests with the 'Automation_Status Automated' tag:

```bash
rf_azure_sync
```
# Configuration
The package requires a configuration file **'sync_config.json'** with Azure-related settings. If the file is not found, it will be created interactively.

Example **'sync_config.json'**:
```JSON
{
     "path": "tests",
     "credentials": {
       "personal_access_token": "your_azure_personal_access_token",
       "organization_name": "your_organization_name",
       "project_name": "your_project_name"
     },
     "tag_config": {
       "test_case": "TC",
       "user_story": "USA",
       "bug": "Bug",
       "title": "Title",
       "TestedBy-Reverse": "",
       "IterationPath": "",
       "AutomationStatus": "",
       "ignore_sync": "",
       "System.Tags": "",
       "Priority": ""
     },
     "constants": {
       "System.AreaPath": "",
       "System.TeamProject": "",
       "settings_section": "",
       "test_cases_section": ""
     }
}
```
## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## Contributing
If you would like to contribute to this project, please follow the [Contribution Guidelines](CONTRIBUTING.md).