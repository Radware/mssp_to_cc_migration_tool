# MSSP to Cyber Controller Configuration Migration Tool

This CLI tool automates the process of exporting configuration data from Radware's MSSP platform and importing it into a Cyber Controller. 
It supports direct export and import operations as well as the ability to save the exported configuration to a file for later use.

When this script runs it creates the following folders:
-   logs: Contains log files generated during the migration process. (always created)
    -   mssp_migration_full: would contain all actual logs for the migration and responses from CC
    -   mssp_migration_dry_run_<date_time>: would show you what info would be persisted to CC
    both files are created for each script execution.
-   config: Stores JSON files exported from the MSSP platform for later use.

## Requirements

- Python 3.8 or later.
- `requests` library for Python. Install via pip:
```pip install requests```
- Access to the MSSP platform and Cyber Controller with valid credentials.

## Installation

Clone this repository or download the script directly. Ensure you have Python and the required packages installed.

## Usage

The script can be executed in two main modes: direct migration and file-based migration.

### Direct Migration

To export from MSSP and import to Cyber Controller, use the following command:
```bash mssp_migrate_to_cc.py --mssp-address <MSSP_ADDRESS> --mssp-username <MSSP_USERNAME> --mssp-password <MSSP_PASSWORD> --cc-address <CC_IP> --cc-username <CC_USERNAME> --cc-password <CC_PASSWORD> [--created-users-default-password <DEFAULT_PASSWORD>] [--dry-run]```

### File-based Migration

To export the MSSP configuration to a file:

```bash mssp_migrate_to_cc.py --mssp-address <MSSP_ADDRESS> --mssp-username <MSSP_USERNAME> --mssp-password <MSSP_PASSWORD> --export-file <FILENAME.json>```


To import configuration from a file to the Cyber Controller:

```bash mssp_migrate_to_cc.py --cc-address <CC_IP> --cc-username <CC_USERNAME> --cc-password <CC_PASSWORD> --config-file <FILENAME.json> --import-from-file [--created-users-default-password <DEFAULT_PASSWORD>] [--dry-run]```

## Options

- `--mssp-address`: The IP address or hostname of the MSSP platform.
- `--mssp-username`: Username for MSSP login.
- `--mssp-password`: Password for MSSP login.
- `--cc-address`: The IP address of the Cyber Controller.
- `--cc-username`: Username for Cyber Controller login.
- `--cc-password`: Password for Cyber Controller login.
- `--import-from-file`: Flag to indicate importing configuration from a file.
- `--config-file`: The path to the configuration JSON file for import. Required if `--import-from-file` is set.
- `--export-file`: (Optional) Filename to save the exported MSSP configuration.
- `--dry-run`: (Optional) Run the script in dry-run mode without making actual changes.
- `-created-users-default-password`: (Optional) Default password for any users created during migration.
