#! /usr/bin/python3


# This is a standardized syslog compatible event object that I use in my modules
# 05/10/2022



import datetime
import time   

class Event(object): # EVENT object for Syslogging 
    
    def __init__(self,event_text: str,driving_process_tree: str):

        '''
        LEVEL = {
            'emerg': 0, 'alert':1, 'crit': 2, 'err': 3,
            'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
        }
        '''

        self.event_priority = 4 # default level is warning (or priority level 4) This is needed when sending syslog to server, see comment for priority levels
        self.event_date = str(datetime.datetime.now()) # for ease of use adds time when event object is created
        self.event_time = time.time() # for ease of use adds time when event object is created
        self.driving_process_tree = driving_process_tree # This is used to enable easy filtering in Splunk/Syslog. Please enter the "name" of your project or overarching process. e.g. use "xyz" for a function foo that is part of the xyz project
        # self.process_name = __file__
        self.event_text = event_text


