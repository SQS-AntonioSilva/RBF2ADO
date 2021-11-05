from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("org", help = "Name of the the organization ")
parser.add_argument("proj", help = "Name of the Project ")
parser.add_argument("user", help = "User to access Azure Dev Ops")
parser.add_argument("pass", help = "Password to access Azure Dev Ops")
args = parser.parse_args()

api_url = 'https://dev.azure.com'
headers = {'Content-Type': 'application/json'}


# Get a client (the "core" client provides access to projects, teams, etc)
myusername = args.user
Organization = args.org
Project = args.proj
mybasicpass = 'z3xfvcbxffxnkt6e4er3rowipnboy6v7nhsab45ni3dndn7jtxua'


def output(status, jasondata):
    print(status)
    print(jasondata)


def get_test_case(status, jasondata):
    print(status)
    print(jasondata)


def update_test_case(test_case_id, status, jasondata):
    #Field to update
    print(test_case_id)
    print(status)
    print(jasondata)


def read_output_xml(path_to_xml_file, status, jasondata):
    # Read_xml(path_to_xml_file)
    print(path_to_xml_file)
    print(status)
    print(jasondata)


# Fill in with your personal access token and org URL
personal_access_token = mybasicpass
organization_url = api_url + '/' + Organization
organization_project_url = organization_url + '/' + Project

# Create a connection to the org
credentials = BasicAuthentication(myusername, personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

core_client = connection.clients.get_core_client()
wit_client = connection.clients.get_work_item_tracking_client()

# get_test_case_response = wit_client.get_work_items('87')
desired_ids = ['87', '88']
work_items = wit_client.get_work_items(ids=desired_ids, error_policy="omit")

for work_item in work_items:
    if work_item:
        print(str(work_item.id) + ' - ' + work_item.fields["System.WorkItemType"] + ' - ' + work_item.fields["System.Title"])
    else:
        print("(work item {0} omitted by server)")

# index = 0
# while get_projects_response is not None:
#     for project in get_projects_response.value:
#         pprint.pprint("[" + str(index) + "] " + project.name)
#         index += 1
#     if get_projects_response.continuation_token is not None and get_projects_response.continuation_token != "":
#         # Get the next page of projects
#         get_projects_response = core_client.get_projects(continuation_token=get_projects_response.continuation_token)
#     else:
#         # All projects have been retrieved
#         get_projects_response = None

