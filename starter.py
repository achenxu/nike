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


class confDB(object):
    DEBUG = True
    SUBMIT = True
    ENGINE = "nike"
    TIMER = "09:00:00"
    SELECTIONS = ['41','42','43']
    CONT = 0
    DISTRIBUTED = False
    USEPROXY = False

    def __init__(self):
        self.info = []
        with open("userdata.csv") as f :
            csvFile = csv.reader(f)
            for row in csvFile :
                self.info.append(row)

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
            "Dpdne:t:c:s:",
            [
                "debug",
                "nosubmit",
                "engine",
                "timer",
                "continuous",
                "start_script",
                "distributed",
                "useProxy"
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
                    distributed.genRemoteDrv(confDB.USEPROXY),
                    confDB.DEBUG,
                    confDB.SUBMIT,
                    confDB.SELECTIONS
                )
            else:
                web = drvClass(
                    re.sub("[0-9]*$", str(diff), confDB.TIMER),
                    None,
                    confDB.DEBUG,
                    confDB.SUBMIT,
                    confDB.SELECTIONS
                )

            web.USER_NAME, web.PASSWD, _ = tuple(rec)
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
