import  requests
import json

recentbuildsurls = 'https://circleci.com/api/v1.1/recent-builds?circle-token=03dc9a9f0a2cfe00c80f27aaf0405e810680702d&limit=100'

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
                print (branch['build_num'])


if __name__ == '__main__':
    get_build_num()