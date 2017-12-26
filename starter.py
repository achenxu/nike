#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import getopt
import nike
import time
import csv
import importlib

class confDB(object):
    DEBUG = True
    SUBMIT = True
    ENGINE = "nike"
    TIMER = "09:00:00"
    SELECTIONS = ['40','39', '41','42','42.5']

    def __init__(self):
        self.info = []
        with open("userdata.csv") as f :
            csvFile = csv.reader(f)
            for row in csvFile :
                self.info.append(row)

def usage():
    # TODO: Shall we add something here?
    print("I'm lasy...")

def processArg():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "dnet:",
            [
                "debug",
                "nosubmit",
                "engine",
                "timer"
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

    except getopt.GetoptError, e:
        # TODO: Need a logger class sooner or later
        print("ERROR: Invalid arguments!")
        usage()
        sys.exit(255)

def main():
    # Chinese support
    reload(sys)
    sys.setdefaultencoding('utf8')

    # Process cmdline arguments
    processArg()

    # TODO: load configuration from DB
    db = confDB()
    iteration = iter(db.info)
    context = {}

    try:
        rec = iteration.next()
        while True:
            # start process
            try:
                mod = importlib.import_module(confDB.ENGINE)
                drvClass = getattr(mod, "WebDrv")
                web = drvClass(
                    confDB.TIMER,
                    confDB.DEBUG,
                    confDB.SUBMIT,
                    confDB.SELECTIONS,
                )
                web.USER_NAME, web.PASSWD, web.SHOE_SIZE = tuple(rec)
                context[web.USER_NAME] = web
                web.startOrchestration()
            except nike.doItAgain, e:
                print("{username} Failed! try again!".format(
                    username = web.USER_NAME
                ))
                web.close()
                time.sleep(5)
                continue
            else:
                print("{t}: Deal for {username} is done!".format(t=time.asctime(time.localtime()),
                                                                 username=web.USER_NAME))
                rec = next(iteration)
                time.sleep(10)
    except StopIteration:
        pass

    time.sleep(1800)

if __name__ == '__main__':
    main()
