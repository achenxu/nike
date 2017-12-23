#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import nike
import time


def main():
    # Chinese support
    reload(sys)
    sys.setdefaultencoding('utf8')

    # TODO: load configuration from DB
    db = nike.database()
    iteration = iter(db.info)
    context = {}

    try:
        rec = iteration.next()
        while True:
            # start process
            try:
                web = nike.nikeWeb()
                web.USER_NAME, web.PASSWD, web.SHOE_SIZE = tuple(rec)
                context[web.USER_NAME] = web
                web.startOrchestration()
            except nike.doItAgain, e:
                print("{username} Failed! try again!".format(
                    username = web.USER_NAME
                ))
                web.close()
                time.sleep(10)
                continue
            else:
                print("Deal for {username} is done!".format(username = web.USER_NAME))
                rec = next(iteration)
                time.sleep(10)
    except StopIteration:
        pass

    time.sleep(1800)

if __name__ == '__main__':
    main()
