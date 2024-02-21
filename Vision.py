import logging
from requests import Session, packages
import json, os
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime

# Define the directory for logs
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
# Ensure the directory exists
os.makedirs(log_dir, exist_ok=True)

# Format the current date and time to include in the log filename
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Main log file with date and time
main_log_filename = os.path.join(log_dir, f'mssp_migration_full.log')
# Dry-run log file with date and time
dry_run_log_filename = os.path.join(log_dir, f'mssp_migration_dry_run_{current_time}.log')

# Set up the main logger
logging.basicConfig(filename=main_log_filename, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a separate logger for dry-run operations
dry_run_logger = logging.getLogger('dry_run')
dry_run_handler = logging.FileHandler(dry_run_log_filename)
dry_run_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
dry_run_handler.setFormatter(dry_run_formatter)
dry_run_logger.addHandler(dry_run_handler)
dry_run_logger.setLevel(logging.INFO)
dry_run_logger.propagate = False

# Suppress only the single warning from urllib3.
packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class Vision:
	login_path = '/mgmt/system/user/login'
	auth_POs_path = '/mgmt/system/config/itemlist/authorizedpos'
	cc_group_path = '/mgmt/system/config/itemlist/visiongroup'
	cc_user_path = '/mgmt/vision/group/management/mssp/user'

	def __init__(self, ip, username, password):
		self.ip = ip
		self.login_data = {"username": username, "password": password}
		self.base_url = f"https://{ip}"
		self.sess = Session()
		self.sess.headers.update({"Content-Type": "application/json"})

	def login(self):
		url = self.base_url + self.login_path
		r = self.sess.post(url=url, json=self.login_data, verify=False)
		response = r.json()
		if response['status'] == 'ok':
			self.sess.headers.update({"JSESSIONID": response['jsessionid']})
			print(f"Cyber Controller: Login Successful, JSESSIONID: {response['jsessionid']}")
			logging.info(f"Cyber Controller: Login Successful, JSESSIONID: {response['jsessionid']}")
			return True
		else:
			print(f"Login Error: {r.text}")
			logging.error(f"Login Error: {r.text}")
			return False

	def fetch_auth_POs(self):
		url = self.base_url + self.auth_POs_path
		r = self.sess.get(url=url, verify=False)
		try:
			response = r.json()
			print(json.dumps(response, indent=4))
			logging.info(f"Fetched authorized POS: {json.dumps(response, indent=4)}")
		except ValueError:
			print("Failed to decode JSON response")
			print(r.text)
			logging.error("Failed to decode JSON response")
			logging.error(r.text)

	def create_cc_group(self, name, authorizedPOs, disableNetworkAnalytics=True, 
					allowActivateOperations=False, disableSecurityOperations=True, 
					disableReporting=True, disableDefensePro=True, dry_run=False):
		success = True  # Initialize success flag as True
		payload = {
			"name": name,
			"requireDeviceLock": True,
			"msspUserSettings": {
				"disableNetworkAnalytics": disableNetworkAnalytics,
				"allowActivateOperations": allowActivateOperations,
				"disableSecurityOperations": disableSecurityOperations,
				"disableReporting": disableReporting,
				"disableDefensePro": disableDefensePro
			},
			"parameters": {},
			"authorizedPOS": self.fetch_full_PO_objects(authorizedPOs, name)
		}

		if dry_run:
			dry_run_logger.info(f"Dry run: Would create CC group with payload: {json.dumps(payload, indent=4)}")
			logging.info("Dry Run Mode, skipping create group, assuming success")
		else:
			url = self.base_url + self.cc_group_path
			r = self.sess.post(url=url, json=payload, verify=False)
			try:
				response = r.json()
				if response.get('status') == 'error':
					logging.error(f"Group creation failed: {response['message']}")
					success = False  # Set success to False if there's an error
				else:
					logging.info(f"CC Group {name} creation status: {json.dumps(response, indent=4)}")
					# success remains True if creation was successful
			except ValueError:
				logging.error("Failed to decode JSON response")
				logging.error(r.text)
				success = False  # Set success to False if there was an issue processing the response

		return success  # Return the success flag indicating the outcome

	def add_user_to_group(self, user, group_name, password="Radware1!",
						allowActivateOperations=False, disableNetworkAnalytics=False, disableDefensePro=False,
						disableSecurityOperations=False, disableReporting=False, dry_run=False):
		url = self.base_url + self.cc_user_path
		payload = {
			"name": user["Username"],
			"userFullName": user["Name"],
			"contactInfo": {
				"email": user["Email"]
			},
			"password": password,
			"roleGroupPairList": [
				{
					"groupName": group_name,
					"roleName": user["New Role"]
				}
			],
			"userSettings": {
				"globalLandingPage": "MsspSecurityOperation"
			},
			"msspUserSettings": {
				"changePassword": True,
				"permittedIPAddress": "",
				"userDetails": "",
				"allowActivateOperations": allowActivateOperations,
				"disableNetworkAnalytics": disableNetworkAnalytics,
				"disableDefensePro": disableDefensePro,
				"disableSecurityOperations": disableSecurityOperations,
				"disableReporting": disableReporting
			}
		}

		if dry_run:
			dry_run_logger.info(f"Dry run: Would add user {user['Username']} to group {group_name} with payload: {json.dumps(payload, indent=4)}")
			logging.info("Dry Run Mode, skipping add user")
		else:
			url = self.base_url + self.cc_user_path
			r = self.sess.post(url=url, json=payload, verify=False)
			try:
				if r.status_code == 500:
					logging.error(f"Internal Server Error when trying to add user {user['Username']} to group {group_name}.")
					success = False
				else:
					response = r.json()
					if response.get("status") == "error":
						logging.error(f"Error adding user {user['Username']} to group {group_name}: {response['message']}")
						success = False  # Set success to False if there's an error
					else:
						logging.info(f"User {user['Username']} added to group {group_name}")
						# success remains True if user was added successfully
			except ValueError:
				logging.error("Failed to decode JSON response")
				logging.error(r.text)
				success = False  # Set success to False if there was an issue processing the response

		return success  # Return the success flag indicating the outcome

	def fetch_full_PO_objects(self, po_names, group_name):
		url = self.base_url + self.auth_POs_path
		r = self.sess.get(url=url, verify=False)
		full_pos = []
		try:
			all_pos = r.json()
			for po in all_pos['authorizedpos']:
				if po['poName'] in po_names:
					full_pos.append(po)
					logging.info(f"Po {po['poName']} was found in autherizedPOs and will be added to group {group_name}")
				else:
					logging.warning(f"Po {po['poName']} was not found in autherizedPOs and will not be added to group {group_name}")

		except ValueError:
			print("Failed to decode JSON response")
			print(r.text)
			logging.error("Failed to decode JSON response")
			logging.error(r.text)
		return full_pos

if __name__ == '__main__':
	v = Vision('cc.address.ip.or.fqdn', 'cc_user', 'cc_password')
	input_json = [
			{
				"Account Name": "Graph testing",
				"Type": "CustomerAccount",
				"Account OID": "65b0bd2806ff00a4c6a4a1d1",
				"Assets": [
					"new_poSilvi",
					"NEW",
					"host32",
					"net100",
					"new_poSilvi_1"
				],
				"Users": [
					 {
						"Name": "Shani",
						"Username": "shani_test_2024",
						"Role": "user",
						"Email": "shanic@radware.com",
						"Auth Type": "local",
						"Account OID": "6284af9503ca3d5d63b5d27a",
						"Role (Current)": "basicUser",
						"New Role": "MSSP_PORTAL_USER"
					},
					{
						"Name": "Shanic",
						"Username": "shanis",
						"Role": "user",
						"Email": "shanic@radware.com",
						"Auth Type": "local",
						"Account OID": "6284af9503ca3d5d63b5d27a",
						"Role (Current)": "basicUser",
						"New Role": "MSSP_PORTAL_USER"
					}
				]
			},
			{
				"Account Name": "Nutanix",
				"Type": "CustomerAccount",
				"Account OID": "655f0279fd98dc1a803d8753",
				"Assets": [
					"Vision",
					"rest"
				],
				"Users": [
					{
						"Name": "adrfsdf",
						"Username": "msspviewer1",
						"Role": "user",
						"Email": "talbe@radware.com",
						"Auth Type": "local",
						"Account OID": "6284af9503ca3d5d63b5d27a",
						"Role (Current)": "basicUser",
						"New Role": "MSSP_PORTAL_VIEWER"
					},
					{
						"Name": "chenallroles",
						"Username": "chenallroles",
						"Role": "user",
						"Email": "chen@all.roles",
						"Auth Type": "local",
						"Account OID": "6284af9503ca3d5d63b5d27a",
						"Role (Current)": "dashboardUser, basicUser, userViewer, userAdmin",
						"New Role": "MSSP_PORTAL_ADMIN"
					}
				]
			}
		]

	dry_run = True
	if v.login():
		for group in input_json:
			cc_group_name = (group["Account Name"] + "_" + group["Account OID"])[:31]
			poList = group["Assets"]
			v.create_cc_group(cc_group_name, poList, dry_run=dry_run)
			for user in group["Users"]:
				v.add_user_to_group(user,cc_group_name,password="Radware1!", dry_run=dry_run)
