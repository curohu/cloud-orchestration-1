#! /user/bin/python3
# This is an API template built on FastAPI that can be easily modified

# standard lib imports
import sys,os,time,json,hashlib,multiprocessing

# imports requiring pip
from fastapi import FastAPI, Response, Request, status

# import from local path
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/../')
import remotelogger.event as rEvent
import remotelogger.remotelogger as rLogger


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

# initialize fast API app
app = FastAPI() 

DRIVING_PROCESS_TREE = "API_TEMPLATE" # This is used for syslog reporting in splunk. Once reports are generated you can search for this application with: index=* driving_process_tree={DRIVING_PROCESS_TREE}
ENDPOINT_BASE = '/api_template/v1/' # This is the base for the proceeding API endpoints


# this is where Uvicorn or Gunicorn knows to pickout your endpoints. They can be app.get(), app.delete(), app.post(), etc
@app.get(ENDPOINT_BASE+'example1')

# This is where you can get information from the client's request/url. At the moment we are expecting a "cube" parrameter to be passed.
# example url: http://127.0.0.1:8080/api_template/v1/example1?cube=54321
# This is an async python function. I recomend doing research on your own for this. But if you are familiar with node this is like that. All operations that are not await'ed will happen at the sametime 
async def example1(request: Request, cube: float) -> Response:
    # getting the endpoint for logging
    endpoint = ENDPOINT_BASE+'example1'
    
    # getting the ip of the requesting client
    clientIp = request.client.host
    
    # seting up a basic log string
    eventString = ',processingTime={:.3f},endpoint={},clientIp={},dataSent={},statusCode={}'

    # starting clock to measure processing time
    stime = time.time()

    try: 
        # This grabs the 'X-API-KEY' header in order to authenticate the client. See _checkKey() for more info
        if not await _checkKey(request.headers.get('X-API-KEY')):

            # This generates a log and sends it to our syslog server to then be picked up by splunk. Note that it is not awaited so it will not slowdown the app.
            _generateLog(eventString.format(time.time()-stime,endpoint,clientIp,cube,'401'))

            # if the user cannot be authenticated return a 401
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)

        # if the user can be authenticated run the await'ed task in the content field and return it to the user
        return Response(content=await example1_task(cube),media_type='application/json',status_code=status.HTTP_200_OK)
    
    except Exception as e:
        # if the process breaks for some reason add exception code to log string
        eventString+="exceptionCode={},".format(str(e))

        # kick off log to syslog server
        _generateLog(eventString.format(time.time()-stime,endpoint,clientIp,cube,'500'))

        # return 500 to client
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# async functions lend themselves to a lot of smaller functions. However they take into account loops like for, while, if, etc and will only run async when relevent
async def example1_task(cube: float) -> float:
    try:
        if cube:
            # all of the returns should be in json. the easy way to convert into json is to json.dumps() a dict
            return json.dumps({'request': cube,'return': cube**3,})
        else:
            return json.dumps({'request': None,})
    except Exception as e:
        return json.dumps({'request':cube,'error': str(e),})



# same as before, but now there are two parrameters to be passed.
# example url: http://127.0.0.1:8080/api_template/v1/example1?add1=123&add2=456
@app.get(ENDPOINT_BASE+'example2')
async def example1(request: Request, add1: float, add2: float) -> Response:
    endpoint = ENDPOINT_BASE+'example2'
    clientIp = request.client.host
    eventString = ',processingTime={:.3f},endpoint={},clientIp={},dataSent={},statusCode={}'
    stime = time.time()
    try: 
        if not await _checkKey(request.headers.get('X-API-KEY')):
            _generateLog(eventString.format(time.time()-stime,endpoint,clientIp,'{} + {}'.format(add1,add2),'401'))
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
        return Response(content=await example2_task(add1,add2),media_type='application/json',status_code=status.HTTP_200_OK)
    except Exception as e:
        eventString+="exceptionCode={},".format(str(e))
        _generateLog(eventString.format(time.time()-stime,endpoint,clientIp,'{} + {}'.format(add1,add2),'500'))
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def example2_task(add1: float, add2: float) -> float:
    try:
        if add1 and add2:
            return json.dumps({'request': '{} + {}'.format(add1,add2),'return': add1+add2,})
        else:
            return json.dumps({'request': None,})
    except Exception as e:
        return json.dumps({'request':'{} + {}'.format(add1,add2),'error': str(e),})


###################################################################################
# Utility Functions
###################################################################################

# this is a security function to authenticate the client. It is really basic in that it rounds unix time to the 100s place and uses that to salt the md5 hash of our secret_key.
# It is not perfect as there is a small chance that when the user sends the request and when the server recieves it you will increment the 100s place. However, you could catch this error in the client and just resend it.
# most APIs use https to get around sending the key in plain text, but I don't want to set that up
async def _checkKey(apiKey:str) -> bool:
    requestTime = str(round(time.time(),-2))
    md5Hash = hashlib.md5(str(KEY+requestTime).encode()).hexdigest()
    return md5Hash == apiKey

# This function creates the Event object and then passes it to the remote logger inorder to be sent over to our syslog server
# I want this to run in both async and parallel so it also kicks off a new process to do this
def _generateLog(eventText: str, drivingProcessTree: str = DRIVING_PROCESS_TREE) -> None:
    evnt = rEvent.Event(event_text=eventText,driving_process_tree=drivingProcessTree)
    logProc = multiprocessing.Process(target=_generateLogSubprocess,args=(evnt,))
    logProc.start()

def _generateLogSubprocess(evnt: rEvent.Event) -> None:
    rLogger.sendLog(evnt)