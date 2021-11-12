import requests
import json
import jsonpath
from datetime import datetime
import argparse
from bs4 import BeautifulSoup

# TODO: - Reavaliar pat
# TODO: - criar libs
# TODO: - Refactoring da criação de json
# TODO: - Unit Testing para as funções

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
pat = 'zaxgv5p7zh63bhp4owmkn672u5vjlnmwi665frz56sxtvkro5owq'
api_version = "6.0-preview.6"
xml_report = "output.xml"

planName = "Teste Realese 14"
suitename = "Teste Realese 14"
testcaseid = "88"
status = "passed"
url_base = api_url + "/" + organization + "/" + project



def get_testplan_details():
    try:
        url = url_base + "/_apis/test/plans?api-version=" + api_version
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
              "/suites?api-version=" + api_version
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
              "/points?api-version=" + api_version
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
              "&api-version=" + api_version
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
              "/_apis/test/runs?api-version=" + api_version
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
              "/results?api-version=" + api_version
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
              "/results?api-version=" + api_version
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

def add_parent_link(userstory):
    parent_xml = '{' \
        '"op": "add",' \
        '"path": "/relations/-",' \
        '"value": {' \
        '"rel": "Microsoft.VSTS.Common.TestedBy-Reverse",' \
        '"url": "' + url_base + \
        '/_apis/wit/workItems/' + userstory + '",' \
        '"attributes": {' \
                                              '"comment": "Create with Robot framework Sync"' \
                                              '}' \
        '}' \
        '}'
    return parent_xml


def add_tags(tags):
    parent_xml = '{' \
            '"op": "add",' \
            '"path": "/fields/System.Tags",' \
            '"from": null,' \
            '"value": "' + tags + '"}'
    return parent_xml


def add_test_status():
    parent_xml = '{' \
            '"op": "add",' \
            '"path": "/fields/Microsoft.VSTS.TCM.AutomationStatus",' \
            '"from": null,' \
            '"value": "Planned"}'
    return parent_xml


def add_test_steps(steps):
    parent_xml = '{' \
            '"op": "add",' \
            '"path": "/fields/Microsoft.VSTS.TCM.Steps",' \
            '"from": null,' \
            '"value": "<steps id=\\\"0\\\" last=\\\"4\\\">' + steps + '</steps>"' \
            '}'
    return parent_xml

def add_step_to_steps(id, step):
    step_format = '<step id=\\\"' + str(id) + '\\\" type=\\\"ActionStep\\\">' \
        '<parameterizedString isformatted=\\\"true\\\">&lt;DIV&gt;&lt;P&gt;' + step + '&lt;/P&gt;&lt;/DIV&gt;</parameterizedString>' \
        '<parameterizedString isformatted=\\\"true\\\">&lt;DIV&gt;&lt;P&gt;&lt;BR/&gt;&lt;/P&gt;&lt;/DIV&gt;</parameterizedString><description/>' \
        '</step>'
    return step_format


def add_test_title(testcaseName):
    parent_xml = '{' \
            '"op": "add",' \
            '"path": "/fields/System.Title",' \
            '"from": null,' \
            '"value": "' + testcaseName + '"}'
    return parent_xml


def add_test_description(test_description):
    test_description_json = '{' \
            '"op": "add",' \
            '"path": "/fields/System.Description",' \
            '"from": null,' \
            '"value": "' + test_description + '"}'
    return test_description_json


def create_test_case(add_test_case):
    try:
        url = url_base + \
            "/_apis/wit/workitems/$Test%20Case?api-version=" + api_version
        payload = add_test_case
        payloadjson = json.loads(payload)
        response = requests.post(url=url, json=payloadjson, auth=(username, pat),
                                 headers={'Content-Type': 'application/json-patch+json'})
        print(response)
        responsejson = json.loads(response.text)
        testcaseId = jsonpath.jsonpath(responsejson, "$.id")[0]
        print(testcaseId)
        return str(testcaseId)
    except Exception as e:
        print('Something went wrong in creating Test Case :' + str(e))


def update_test_case(update_test_case,test_case_id):
    try:
        url = url_base + \
            "/_apis/wit/workitems/"+test_case_id+"?api-version=" + api_version
        payload = update_test_case
        payloadjson = json.loads(payload)
        response = requests.patch(url=url, json=payloadjson, auth=(username, pat),
                                  headers={'Content-Type': 'application/json-patch+json'})
        responsejson = json.loads(response.text)
        testcaseId = jsonpath.jsonpath(responsejson, "$.id")[0]
        print("Test case: " + str(testcaseId))
        return str(testcaseId)
    except Exception as e:
        print('Something went wrong in Update Test Case :' + str(e))


def read_xml_report():
    f = open(xml_report, "r", encoding="utf-8")
    lines = f.read()
    soup = BeautifulSoup(lines, 'xml')
    return soup


def read_test_cases(json_report):
    # TODO: - Validar se Teste já existe, se já existe faz Update senão faz create
    # TODO: - Não permitir alteração a testes que estejam fechados
    # TODO: - Criar ficheiro log com resultado da execução
    test_cases = json_report.find_all('test')
    for test_case in test_cases:
        testcaseid = None
        test_to_update = False

        # Add Test case title and initialise json
        test_case_name = test_case["name"]
        test_case_json = "["
        test_case_json = test_case_json + add_test_title(test_case_name)

        # Add Tags to Test Case
        # Search for user story id
        # If tag TC: exists update test case
        tags = "Test Automated"
        test_tags = test_case.find_all('tag')
        if test_tags is not None:
            for test_tag in test_tags:
                if "US:" in test_tag.string:
                    userstory = test_tag.string[3:]
                    test_case_json = test_case_json + "," + add_parent_link(userstory)
                    tags = tags + ";" + test_tag.string
                elif "TC:" in test_tag.string:
                    test_to_update = True
                    testcaseid = test_tag.string[3:]
                    tags = tags + ";" + test_tag.string
                else:
                    tags = tags + ";" + test_tag.string
            # print(tags)
        test_case_json = test_case_json + "," + add_tags(tags)

        # Add test status = Pending
        test_case_json = test_case_json + "," + add_test_status()

        # Add Summary to TC
        summary = ""
        test_description = test_case.find_all('doc', recursive=False)

        if test_description != "":
            for doc in test_description:
                summary = doc.string
            test_case_json = test_case_json + "," + add_test_description(summary)


        # Add steps
        steps = ""
        test_steps = test_case.find_all('kw', recursive=False)
        if test_steps != "":
            step_id = 2
            for step in test_steps:
                steps = steps + add_step_to_steps(step_id, step["name"])
                step_id = step_id + 1
            print(steps)
            test_case_json = test_case_json + "," + add_test_steps(steps)


        # Close json format
        test_case_json = test_case_json + "]"

        if test_to_update:
            print(test_case_json)
            update_test_case(test_case_json, testcaseid)
        else:
            create_test_case(test_case_json)


if operation == "create":
    report = read_xml_report()
    read_test_cases(report)
    # create_test_case(test_cases_json)
else:
    update_result(status.upper())



