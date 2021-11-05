import requests
import json
import jsonpath
import names # for test purposes
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("org", help="Name of the the organization ")
parser.add_argument("proj", help="Name of the Project ")
parser.add_argument("user", help="User to access Azure Dev Ops")
parser.add_argument("pat", help="PAT to access Azure Dev Ops")
parser.add_argument("oper", help="Type of operation, create-> Create test cases, update -> update test run")
args = parser.parse_args()

api_url = 'https://dev.azure.com'
headers = {'Content-Type': 'application/json'}

username = args.user
organization = args.org
project = args.proj
operation = args.oper
# pat = args.pat
pat = 'z3xfvcbxffxnkt6e4er3rowipnboy6v7nhsab45ni3dndn7jtxua'

planName = "Teste Realese 14"
suitename = "Teste Realese 14"
testcaseid = "88"
status = "passed"
url_base = api_url + "/" + organization + "/" + project


def get_testplan_details():
    try:
        url = url_base + "/_apis/test/plans?api-version=5.0"
        response = requests.get(url=url, auth=(username, pat))
        reponsejson = json.loads(response.text)
        planid = jsonpath.jsonpath(reponsejson, "$.value.[?(@.name == '" + planName + "')].id")[0]
        suiteid = jsonpath.jsonpath(reponsejson, "$.value.[?(@.name == '" + planName + "')].rootSuite.id")[0]
        return str(planid), suiteid
    except Exception as e:
        print('Something went wrong in fetching Test Plan ID :' + str(e))


def get_testsuite_details():
    try:
        plandetails = get_testplan_details()
        url = url_base + \
              "/_apis/test/plans/" + plandetails[0] + \
              "/suites?api-version=5.0"
        response = requests.get(url=url, auth=(username, pat))
        reponsejson = json.loads(response.text)
        suiteID = jsonpath.jsonpath(reponsejson, "$.value.[?(@.name == '" + suitename + "')].id")[0]
        return str(suiteID)
    except Exception as e:
        print('Something went wrong in fetching Test Suite ID :' + str(e))


def get_testcase_id():
    try:
        planid = get_testplan_details()[0]
        suiteid = get_testsuite_details()
        url = url_base + \
              "/_apis/test/plans/" + planid + \
              "/suites/" + suiteid + \
              "/points?api-version=5.0"
        print(url)
        response = requests.get(url=url, auth=(username, pat))
        reponsejson = json.loads(response.text)
        chk_testcaseid = jsonpath.jsonpath(reponsejson, "$..[?(@.id == '" + testcaseid + "')].id")[0]
        return chk_testcaseid
    except Exception as e:
        print('Something went wrong in fetching Test Case ID :' + str(e))


def get_testpoint_ID():
    try:
        planid = get_testplan_details()[0]
        suiteid = get_testsuite_details()
        tcid = get_testcase_id()
        url = url_base + \
              "/_apis/test/plans/" + planid + \
              "/suites/" + suiteid + \
              "/points?testCaseId=" + tcid + \
              "&api-version=5.0"
        response = requests.get(url=url, auth=(username, pat))
        reponsejson = json.loads(response.text)
        testpointid = jsonpath.jsonpath(reponsejson, "$.value.[0].id")[0]
        return str(testpointid)
    except Exception as e:
        print('Something went wrong in fetching Test Point ID :' + str(e))


def create_run():
    try:
        runName = planName + "-" + str(datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
        planID = get_testplan_details()[0]
        pointID = get_testpoint_ID()
        url = url_base + \
              "/_apis/test/runs?api-version=5.0"
        payload = '{"name":"' + runName + '","plan":{"id":' + planID + '},"pointIds":[' + pointID + ']}'
        payloadJson = json.loads(payload)
        response = requests.post(url=url, json=payloadJson, auth=(username, pat),
                                 headers={'Content-Type': 'application/json'})
        reponsejson = json.loads(response.text)
        runID = jsonpath.jsonpath(reponsejson, "$.id")[0]
        return str(runID)
    except Exception as e:
        print('Something went wrong in fetching Run ID :' + str(e))


def get_testResult_ID():
    try:
        runID = create_run()
        url = url_base + \
              "/_apis/test/runs/" + runID + \
              "/results?api-version=6.0-preview.6"
        response = requests.get(url=url, auth=(username, pat))
        reponsejson = json.loads(response.text)
        resultID = jsonpath.jsonpath(reponsejson, "$.value.[0].id")[0]
        return str(resultID), runID
    except Exception as e:
        print('Something went wrong in fetching Result ID :' + str(e))

def update_result(status):
    try:
        resultdata = get_testResult_ID()
        resultid = resultdata[0]
        runid = resultdata[1]
        url = url_base + \
              "/_apis/test/runs/" + runid + \
              "/results?api-version=6.0-preview.6"
        if (status == 'PASSED'):
            payload = '[{ "id": ' + resultid + ',' \
                                               '"outcome": "' + status + '" ,' \
                                                                         '"state": "Completed",' \
                                                                         '"comment": "Execution Successful"' \
                                                                         '}]'
        else:
            payload = '[{ "id": ' + resultid + ',  ' \
                                               '"outcome": "' + status + \
                      '","state": "Completed",' \
                      '"comment": "Execution Failed"' \
                      '}]'

        payloadJson = json.loads(payload)
        resp = requests.patch(url=url, json=payloadJson, auth=(username, pat),
                              headers={'Content-Type': 'application/json'})
        print(resp.text)
    except Exception as e:
        print('Something went wrong in updating Test Results :' + str(e))


def create_test_case(testcaseName, Userstoryid):
    try:
        title = testcaseName
        tests = Userstoryid
        url = url_base + \
              "/_apis/wit/workitems/$Test%20Case?api-version=5.0"
        payload = '[{' \
                  '"op": "add",' \
                  '"path": "/fields/System.Title",' \
                  '"from": null,' \
                  '"value": "' + title + '"}' \
                ',{' \
                    '"op": "add",' \
                    '"path": "/fields/Microsoft.VSTS.TCM.AutomationStatus",' \
                    '"from": null,' \
                    '"value": "Planned"}' \
                 ',{' \
                    '"op": "add",' \
                    '"path": "/relations/-",' \
                    '"value": {' \
                    '"rel": "Microsoft.VSTS.Common.TestedBy-Reverse",' \
                    '"url": "' + url_base + '/_apis/wit/workItems/' + Userstoryid + '",' \
                    '"attributes": {' \
                    '"comment": "Test de Child"}' \
                 '}' \
                 '}]'
        payloadJson = json.loads(payload)
        response = requests.post(url=url, json=payloadJson, auth=(username, pat),
                                 headers={'Content-Type': 'application/json-patch+json'})
        responsejson = json.loads(response.text)
        testcaseId = jsonpath.jsonpath(responsejson, "$.id")[0]
        print(testcaseId)
        return str(testcaseId)
    except Exception as e:
        print('Something went wrong in creating Test Case :' + str(e))


if operation == "create":
    randomtxt = rand_name = names.get_full_name(gender='female')  # for test purpose
    testcaseName = "TC: " + randomtxt
    Userstoryid = "108"
    create_test_case(testcaseName, Userstoryid)
else:
    update_result(status.upper())
