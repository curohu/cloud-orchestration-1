#! /user/bin/python3
# This is a basic client that can access your api
# 09/22/2022

import sys,os,requests,time,json,hashlib

url = 'http://127.0.0.1'
port = 8080
ENDPOINT_BASE = '/api_template/v1/'
endpoint = ENDPOINT_BASE+'example2'

# get key for MD5 hash
# I have provided a random 64-bit key as an example. You should change it
keyFile = os.path.dirname(os.path.realpath(__file__))+'/../secret_key' 
KEY = ''
try:
    with open(keyFile, 'r') as file:
        KEY = file.readline()
        file.close()
except Exception as e:
    print('secret_key file not found')
    sys.exit()

# if the key is not found this will raise a "Missing secret_key" error
assert not KEY == '', "Missing secret_key" 

# this will error out if you do not change the secret_key
assert not KEY == 'g64iyGfvWE56wNC6kqgnUmTt5iFF4dodZKr8TZ17nnqwrUx78trNRhCKqpP5AAq6', "Change the secret_key" 

# get the current time and round it to the 100s place
requestTime = str(round(time.time(),-2))

# get the hash of key and current time
md5Hash = hashlib.md5(str(KEY+requestTime).encode()).hexdigest()

# add it to the request header
header = {
    'X-API-KEY': md5Hash,
}


add1 = 123
add2 = 456

# start the clock for processing time
stime = time.time()
print('\n\n')

endpoint += '?add1={}&add2={}'.format(add1,add2)
print('Data that was send:\n',(url+':'+str(port)+endpoint),'\n')
# send the request to the server with correct endpoint and headers
response = requests.get(url+':'+str(port)+endpoint,headers=header)

print("Status Code:",response.status_code)
if response.status_code == 200:
    loadedResponse = json.loads(response.text)
    print('Data received from server:\n',json.dumps(loadedResponse,indent=4),'\n')

print('Response Time: {:.3f}'.format(time.time()-stime))