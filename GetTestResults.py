import requests
import json
import re
import sqlite3



recentbuildsurls = 'https://circleci.com/api/v1.1/recent-builds?circle-token=03dc9a9f0a2cfe00c80f27aaf0405e810680702d&limit=100'
testdata_url_a = 'https://circleci.com/api/v1.1/project/github/aldo-dev/mfind/'
testdata_url_b = '/tests?circle-token=03dc9a9f0a2cfe00c80f27aaf0405e810680702d'
build_number = 0
build_start_time = 'yyyy-mm-ddT00:00:000Z'
build_stop_time = 'yyyy-mm-ddT00:00:000Z'

def get_build_num():
    global build_number
    global build_start_time
    global build_stop_time
    response = requests.get(recentbuildsurls)
    responseStatus = response.status_code
    build_start_times = []
    if responseStatus == 200:
        responseJson = json.loads(response.text)
        for branch in responseJson:
            if branch['branch'] == 'mfind-aws' and branch['build_parameters']['CIRCLE_JOB'] == 'run-ui-tests':
                build_start_times.append(branch['start_time'])
        for build in responseJson:
            if build['start_time'] == sorted(build_start_times, reverse=True)[0]:
                build_number = (build['build_num'])
                build_start_time = build['start_time']
                build_stop_time = build['stop_time']
                return build_number

def get_test_meta_data(build_num):
    if not build_num:
       return 0
    metadata_url = testdata_url_a + str(build_num) + testdata_url_b
    urlresponse = requests.get(metadata_url)
    if urlresponse.status_code == 200:
        r_json = json.loads(urlresponse.text)
        return r_json

def get_test_jira_id(testcase_name):
    tcname = testcase_name
    tcsplit = tcname.split("_")
    if len(tcsplit) > 2:
        jiraid_b  = tcsplit.pop()
        jiraid_a = tcsplit.pop(-1)
        jira_id = jiraid_a+"-"+jiraid_b
        return jira_id

def process_test_class_names(class_names):
    tn = class_names
    l = list(set(tn))
    r = re.compile(".*mFindUITests")
    newlist = list(filter(r.match, l))
    return newlist

def get_test_results(build_num):
    test_meta_data = get_test_meta_data(build_num)
    test_classes = []
    test_cases = []
    tests = test_meta_data ['tests']
    for test in tests:
        test_classes.append(test['classname'])
    valid_test_classes = process_test_class_names(test_classes)
    for testclass in valid_test_classes:
        for test in tests:
            if testclass == test['classname']:
                jira_id = get_test_jira_id(test['name'])
                if not jira_id == None:
                    test_cases.append ([build_num, jira_id, test['name'], test['result'], test['message'], build_start_time, build_stop_time])
                # print (test['name'], test['result'], test['message'])
    return test_cases



def main():
    results = get_test_results(3328)
    conn = sqlite3.connect('test_results')
    c = conn.cursor()
    c.execute('SELECT * FROM results where build_number = {}' .format(build_number))
    rows = c.fetchall()
    print('Total tests:', len(results))
    for result in results:
        if len(rows)<1:
            conn = sqlite3.connect('test_results')
            c = conn.cursor()
            c.execute('insert into results values (?,?,?,?,?,?,?)', result)
            conn.commit()
            conn.close()
        else:
            print ('results for the build already exists in the database')



    # c.execute('''CREATE TABLE results
    #          (build_number numeric, id text, name text, result text, message text, start_time text, stop_time text)''')





if __name__ == '__main__':
    main()