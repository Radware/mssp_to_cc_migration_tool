# MSSP to Cyber Controller Configuration Migration Tool

This CLI tool automates the process of exporting configuration data from Radware's MSSP platform and importing it into a Cyber Controller. It supports direct export and import operations as well as the ability to save the exported configuration to a file for later use.

## Overview

### User Account Initialization

All users will be assigned a default password and will be required to change their password on their first login.

### Tool Limitations & Assumptions

- The tool supports the legacy MSSP asset which is mapped to Protected Object in Cyber Controller and not policies.
- Accounts of type “Service Provider” are ignored.
- The tool is designed to support a single Cyber Controller (CC) setup.
- Operator roles from the legacy MSSP Portal, such as Operator-Monitor and Operator-Admin, won’t be migrated and are not supported.

## Directory Structure Upon Execution

When this script runs, it creates the following folders:
- `logs`: Contains log files generated during the migration process. (always created)
    - `mssp_migration_full`: Contains all actual logs for the migration and responses from CC.
    - `mssp_migration_dry_run`: Shows what info would be persisted to CC, will be populated when the script runs in 'dry-run' mode
- `config`: Stores JSON files exported from the MSSP platform for later use.

## Requirements

- Python 3.8 or later.
- `requests` library for Python. Install via pip:
```bash
pip install requests
```

## Installation

Clone this repository or download the script directly. Ensure you have Python and the required packages installed.

## Usage

The script can be executed in two main modes: direct migration and file-based migration.

### Direct Migration

To export from MSSP and import to Cyber Controller, use the following command:
```bash
mssp_migrate_to_cc.py --mssp-address <MSSP_ADDRESS> --mssp-username <MSSP_USERNAME> --mssp-password <MSSP_PASSWORD> --cc-address <CC_IP> --cc-username <CC_USERNAME> --cc-password <CC_PASSWORD> [--initial-user-password <DEFAULT_PASSWORD>] [--dry-run]
```
##### default password: P@ssw0rd1!
### File-based Migration

To export the MSSP configuration to a file:
```bash
mssp_migrate_to_cc.py --mssp-address <MSSP_ADDRESS> --mssp-username <MSSP_USERNAME> --mssp-password <MSSP_PASSWORD> --export-file <FILENAME.json>
```

To import configuration from a file to the Cyber Controller:
```bash
mssp_migrate_to_cc.py --mssp-address <MSSP_ADDRESS> --mssp-username <MSSP_USERNAME> --cc-address <CC_IP> --cc-username <CC_USERNAME> --cc-password <CC_PASSWORD> --config-file <FILENAME.json> --import-from-file [--initial-user-password <DEFAULT_PASSWORD>] [--dry-run]
```
##### default password: P@ssw0rd1!
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
- `--initial-user-password`: (Optional) Default password for any users created during migration.


## Migration details
**extracted fields:**
- **Username**
- **User Full Name** (A mandatory field in the legacy MSSP Portal)
- **User Role**, according to the following mapping:
  > - Tenant Viewer -> User-Monitor
  > - Tenant User -> User-Basic
  > - Tenant Admin -> User-Admin
  > *If there are more than one role in the legacy MSSP Portal, the higher will be fetched.*
- **E-mail** (A mandatory field in the legacy MSSP Portal)

- **Optional fields (if they exist):**
  > - Details
  > - Allow login only from this IP Address

- **Default fields (regardless of the legacy users):**
  > - **Password** – all the users will get the following default password: `P@ssw0rd1!`
  > - **Password Change on next login** (checkbox) - enabled by default.
  > - **Allow user to activate Operations** (checkbox) – disabled by default. This checkbox is disabled by default for the entire account group, hence it does not appear for the users. To enable it for a specific user, you should enable it for the entire group first.
  > - **Network Analytics page** - enabled by default.
  > - **Extended Analytics package** - enabled by default.
  > - **Security Operations page** - enabled by default.
  > - **Reporting pages** - enabled by default.

- All the other fields of the legacy product are ignored.
