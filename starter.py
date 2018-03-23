#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import sys
import getopt
import nike
import time
import csv
import importlib
import sched
import distributed
import proxyAgent
import ConfigParser
from collections import namedtuple

address = namedtuple(
    'address',
    [
        'surname',
        'firstname',
        'shippingAddress',
        'zone',
        'postcode',
        'cellphone'
    ],
    verbose = False
)

class confDB(object):
    DEBUG = True
    SUBMIT = True
    ENGINE = "nike"
    TIMER = "09:00:00"
    SELECTIONS = ['41','42','43']
    CONT = 0
    DISTRIBUTED = False
    USEPROXY = False
    TITLE = u'Air'
    TARGET = ''
    ADDRESSMODE = False
    ADDRESS = None

    def __init__(self):
        self.confFile = ConfigParser.SafeConfigParser()
        self.confFile.read('conf')
        confDB.TARGET = self.confFile.get('default', 'TARGET')
        confDB.TITLE = self.confFile.get('default', 'TITLE')
        confDB.SELECTIONS = self.confFile.get('default', 'SELECTION').split()
        print("TARGET url is {url}".format(url=confDB.TARGET))
        print("TITLE is {title}".format(title=confDB.TITLE))
        print("Shoe size collection is {size}".format(size=confDB.SELECTIONS))
        if confDB.ADDRESSMODE:
            self._loadAddress()

        self.info = []
        with open("userdata.csv") as f :
            csvFile = csv.reader(f)
            for row in csvFile :
                self.info.append(row)

    def _loadAddress(self):
        confDB.ADDRESS = address(
            self.confFile.get("address", "surname").decode('utf8'),
            self.confFile.get("address", "firstname").decode('utf8'),
            self.confFile.get("address", "shippingAddress").decode('utf8'),
            self.confFile.get("address", "zone").decode('utf8'),
            self.confFile.get("address", "postcode").decode('utf8'),
            self.confFile.get("address", "cellphone").decode('utf8'),
        )
        print('Will update new address:')
        print('surname will be {s}'.format(s=confDB.ADDRESS.surname))
        print('firstname will be {s}'.format(s=confDB.ADDRESS.firstname))
        print('shippingAddress will be {s}'.format(s=confDB.ADDRESS.shippingAddress))
        print('zone will be {s}'.format(s=confDB.ADDRESS.zone))
        print('postcode will be {s}'.format(s=confDB.ADDRESS.postcode))
        print('cellphone will be {s}'.format(s=confDB.ADDRESS.cellphone))

def doNothing():
    pass

def setupTimerAndWait(timeStr):
    now = time.localtime()
    try:
        timer = time.mktime(time.strptime(timeStr))
    except ValueError as e:
        print("Illegal time format!(eg: Tue Feb 6 22:00:00 2018)")
        exit(2)
    if timer < time.mktime(now):
        print "Invalid timer! Will run the script immediately!"
        return
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(timer, 0, doNothing, [])
    s.run()

def usage():
    # TODO: Shall we add something here?
    print("I'm lasy...")

def processArg():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "Dpdne:t:c:s:A",
            [
                "debug",
                "nosubmit",
                "engine",
                "timer",
                "continuous",
                "start_script",
                "distributed",
                "useProxy",
                "address"
            ]
        )
        print("============ opts ==================");
        print(opts);
        print("============ args ==================");
        print(args);
        for o, a in opts:
            if o in ("-d", "--debug"):
                # TODO: Right now debug mode is default mode(using chrome
                # driver), but in the future the default mode should be no-debug
                # mode, which is using no-browser
                confDB.DEBUG = True
            if o in ("-n", "--nosubmit"):
                # WILL submit the deal finally.
                # By default this flag is turned OFF.
                confDB.SUBMIT = False
            if o in ("-e", "--engine"):
                # Default Nikeweb, right now only supports nike
                if a in ("nike"):
                    confDB.ENGINE = a
                else:
                    raise getopt.GetoptError()
            if o in ("-t", "--timer"):
                # After logged in, start a timer to put the deal,
                # Normaly the timer will be set to 9:00 AM,
                # Change it by -t/--timer args
                confDB.TIMER = a
            if o in ("-c", "--continuous"):
                # Start the orchestration one by one
                # By default disabled(confDB.CONT = 0)
                confDB.CONT = int(a)
            if o in ("-s", "--start_script"):
                # overall script's timer;
                # if the param's set then let's wait
                setupTimerAndWait(a)
                print("GOGOGO")
            if o in ("-D", "--distributed"):
                # For distributed running
                # Default: False
                confDB.DISTRIBUTED = True
            if o in ("-p", "--useproxy"):
                # Using proxy for distributed running
                # Default: False
                confDB.USEPROXY = True
            if o in ("-A", "--address"):
                # Address modification mode
                # Only modify an account's address then exit
                # Does NOT support distributed mode now!
                # TODO: Shall we consider to support distributed mode?
                # Default: False
                confDB.ADDRESSMODE = True

    except getopt.GetoptError, e:
        # TODO: Need a logger class sooner or later
        print("ERROR: Invalid arguments!")
        usage()
        sys.exit(255)

def startOrch(rec, diff, idx):
    mod = importlib.import_module(confDB.ENGINE)
    drvClass = getattr(mod, "WebDrv")
    while(True):
        try:
            if confDB.DISTRIBUTED == True:
                web = drvClass(
                    re.sub("[0-9]*$", str(diff), confDB.TIMER),
                    confDB,
                    distributed.genRemoteDrv(confDB.USEPROXY)
                )
            else:
                web = drvClass(
                    re.sub("[0-9]*$", str(diff), confDB.TIMER),
                    confDB,
                    None
                )

            web.USER_NAME, web.PASSWD = tuple(rec)
            web.SHOE_SIZE = confDB.SELECTIONS[idx % len(confDB.SELECTIONS)]
            print("Shoe size for {user} is {size}".format(user=web.USER_NAME, size = web.SHOE_SIZE))
            web.startOrchestration()
        except nike.doItAgain, e:
            print("{username} Failed! try again!".format(
                username = web.USER_NAME))
            web.close()
            time.sleep(5)
            continue
        else:
            print("{t}: Deal for {username} is done!".format(t=time.asctime(time.localtime()),
                                                            username=web.USER_NAME))
            time.sleep(3600)

def main():
    # Chinese support
    reload(sys)
    sys.setdefaultencoding('utf8')

    # Process cmdline arguments
    processArg()

    # For Proxy
    if confDB.USEPROXY == True:
        print "Sleep for 1 minutes for scripts to collect enough proxy ips..."
        res = os.fork()
        if res == 0:
            proxyAgent.proxyStart()
        time.sleep(60)

    # For distrubited running
    grid = distributed.gridService()
    if confDB.DISTRIBUTED == True:
        grid.startService()

    # TODO: load configuration from DB
    db = confDB()
    iteration = iter(db.info)
    idx = 0

    try:
        rec = iteration.next()
        while True:
            # start process
            pid = os.fork()
            if pid == 0:
                startOrch(rec, confDB.CONT * idx, idx)
                # In address mode, now the process can be killed.
                if confDB.ADDRESSMODE:
                    return
            else:
                rec = next(iteration)
                idx = idx + 1
                time.sleep(10)
    except StopIteration:
        pass

    time.sleep(3600)

    if confDB.DISTRIBUTED == True:
        grid.stopService()

if __name__ == '__main__':
    main()
