import requests
import json
import sys
import pathlib

def get_config():
    # Check to ensure the configuration file exists and is readable.
    try:
        path = pathlib.Path("conf.json")
        if path.exists() and path.is_file():
            with open(path) as config_file:
                try:
                    qtest_config = json.load(config_file)
                    return qtest_config
                except json.JSONDecodeError:
                    print("Error: Configuration file not in valid JSON format.")
        else:
            raise IOError
    except IOError:
        print("Error: Configuration file not found or inaccessible.")
        return -1
    except Exception as e:
        print("Error: Unexpected error loading configuration: " + str(e))
        return -1

def get_param_from_test_suite():
    params = []
    qtest_config = get_config()
    api_token = qtest_config["qtest_api_token"]
    qTestUrl = qtest_config["qtest_url"]
    projectId = qtest_config["project_id"]
    testSuiteId = qtest_config["test_suite_id"]

    baseUrl = '{}/api/v3/projects/{}/test-suites/{}'
    testSuiteUrl = baseUrl.format(qTestUrl, projectId, testSuiteId)
    key = '{}'
    key = key.format(api_token)
    headers = {'Content-Type': 'application/json',
               "Authorization": key}
    r = requests.get(testSuiteUrl, headers=headers)
    suiteData = json.loads(r.content)

    for field in suiteData["properties"]:
        params.append(field["field_name"] + "=" + field["field_value"])
    return params

with open('jenkinsconfig.json', 'r') as f:
    config = json.load(f)
KeyList = ""

if len(sys.argv) > 1:
    JenkinsJob = sys.argv[1]
    JenkinsAPIToken = config[JenkinsJob]['JenkinsAPIToken']
    JenkinsJobName = config[JenkinsJob]['JenkinsJobName']
    JenkinsJobToken = config[JenkinsJob]['JenkinsJobToken']
    JenkinsURL = config[JenkinsJob]['JenkinsURL']
    JenkinsUserName = config[JenkinsJob]['JenkinsUserName']
    CrumbUrl = "http://" + JenkinsUserName + ":" + JenkinsAPIToken + "@" + JenkinsURL + '/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)'
    CrumbResult = requests.get(CrumbUrl)
    #print(CrumbResult.status_code)

    if (CrumbResult.ok):
        Crumb = CrumbResult.content.decode().split(":")[1]

        if len(sys.argv) < 3:
            PostUrl = "http://" + JenkinsUserName + ":" + JenkinsAPIToken + "@" +  JenkinsURL + "/job/" + JenkinsJobName + "/build?token=" + JenkinsJobToken
            Headers = {"Jenkins-Crumb": Crumb, "content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
            TriggerJenkinsJob = requests.post(PostUrl, headers=Headers)
        else:

            params = get_param_from_test_suite()
            PostUrl = "http://" + JenkinsUserName + ":" + JenkinsAPIToken + "@" +  JenkinsURL + "/job/" + JenkinsJobName + "/buildWithParameters?token=" + JenkinsJobToken + "&"
            first = True
            for key in params:
                if first:
                    PostUrl = PostUrl + key
                    first = False
                else:
                    PostUrl = PostUrl + "&" + key
            Headers = {"Jenkins-Crumb": Crumb, "content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
            TriggerJenkinsJob = requests.post(PostUrl, headers=Headers)


        #print(TriggerJenkinsJob.status_code)
else:
    for Key in config.keys():
        KeyList = KeyList + Key + ", "
    print("Usage: calljenkins.py <Jenkins Job>")
    print("   where valid Jenkins Job values are " + KeyList)

    
