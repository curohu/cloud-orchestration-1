#! /usr/bin/python3
# Building off my origional Remote logger api this module will takes the logic of the api and refactors it into a module
# 09/10/2022

import sys,os,logging,socket
import logging.handlers
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/')
import event # locally created event object


def sendLog(event):
    SYSLOGSERVERS = ['',] # note at the moment adding two servers just duplicates the packet TODO: create a syslog server uselector based on reachability
    SYSLOGPORT = 514
    try:
        for server in SYSLOGSERVERS:
            lggr = logging.getLogger('lggr')
            if len(lggr.handlers) == 0:
                handler = logging.handlers.SysLogHandler(address = (server,SYSLOGPORT), socktype=socket.SOCK_DGRAM,facility=logging.handlers.SysLogHandler.LOG_LOCAL0)
                lggr.addHandler(handler)

            message = ''
            # print(len(event.__dict__))
            for i  in event.__dict__:
                message += i+'='+str(event.__dict__[i])+'; '

            if event.event_priority <= 2:
                lggr.critical(message)
            elif event.event_priority == 3:
                lggr.error(message)
            elif event.event_priority == 4:
                lggr.warning(message)
            elif event.event_priority == 5 or event.event_priority == 6:
                lggr.info(message)
            elif event.event_priority == 7:
                lggr.debug(message)

        return True

    except Exception as e:
        print(str(e))
        return False