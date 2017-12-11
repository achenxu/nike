#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# First you need chrome and chromedriver installed in your host.
# You can use the latest chrome, and my versions are
# (Chrome 61 and Chromedriver 2.33)

'''
TODO:
    * Process clarification with customer
    * Docker/Docker Hyperviser implementation
    * Scatter the last Ali pay images
    * Database configuration
    * No browser solution
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, \
    NoSuchElementException
from collections import namedtuple
import time
import sys
import csv


# TODO: Following content should be put into a DB
#USER_NAME = 'thealaskalife@hotmail.com'
#PASSWD = 'Nike6326424'
#SHOE_SIZE = 44
# TODO: Shall we let user input the url?
SHOE_TYPE = u'Air Jordan'
TARGET = 'https://www.nike.com/cn/launch/t/air-jordan-11-win-like-96'
# Address
SURNAME = u'张'

class doItAgain(Exception):
    pass

class database(object):
    def __init__(self):
        self.info = []
        with open("userdata.csv") as f :
            csvFile = csv.reader(f)
            for row in csvFile :
                self.info.append(row)

class nikeWeb(object):
    TIMEOUT = 10

    orchestration = namedtuple(
        'orchestration',
        [
            'driver',
            'locator',
            'action',   # click or send_keys
            'data',     # Optional, only for send_keys
        ],
        verbose = False
    )

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self._reloadPage()

    def _error_handle(self, n):
        #sys.exit(n)
        print("Some error happens, error code = {num}".format(num = n))
        raise doItAgain()

    def _reloadPage(self):
        self.driver.get(TARGET)
        try:
            # Confirm whether the page's opened
            WebDriverWait(self.driver, nikeWeb.TIMEOUT).until(
                EC.title_contains(SHOE_TYPE)
            )
        except TimeoutException, e:
            # Wrong URL?
            print("Cannot open the webpage, wrong shoe({shoe_type})?"
                  .format(shoe_type = SHOE_TYPE))
            self._error_handle(1)

    def _orchestra(self, orchestrations, name):
        for orch in orchestrations :
            if orch.driver != None :
                driver = orch.driver
            else :
                driver = self.driver

            try:
                elem = WebDriverWait(driver, nikeWeb.TIMEOUT).until(
                    EC.visibility_of_element_located(orch.locator)
                )
                action = getattr(elem, orch.action)
                if orch.action == 'click' :
                    WebDriverWait(driver, nikeWeb.TIMEOUT).until(
                        EC.element_to_be_clickable(orch.locator)
                    )
                    action()
                else :
                    # send_keys
                    action(orch.data)
            except (TimeoutException, WebDriverException) as e:
                print("Error happens during running {script}! Error message is {err}"
                      .format(script = name, err = e))
                self._error_handle(2)

            time.sleep(1)

    def _login(self):
        orchestrations = [
            nikeWeb.orchestration(
                None,
                (By.LINK_TEXT, u'加入/登录'),
                'click',
                None
            ),
            nikeWeb.orchestration(
                None,
                (By.NAME, u'emailAddress'),
                'send_keys',
                self.USER_NAME
            ),
            nikeWeb.orchestration(
                None,
                (By.NAME, u'password'),
                'send_keys',
                self.PASSWD
            ),
            nikeWeb.orchestration(
                None,
                (By.CLASS_NAME, "nike-unite-submit-button"),
                'click',
                None
            ),
        ]
        self._orchestra(orchestrations, self._login.__name__)
        time.sleep(8)

    def _submitSize(self):
        orchestrations = [
            nikeWeb.orchestration(
                None,
                (By.CLASS_NAME, 'size-selector-component'),
                'click',
                None
            ),
            nikeWeb.orchestration(
                None,
                (
                    By.XPATH,
                    '//li[@data-size="{size}"]'.format(size=self.SHOE_SIZE)
                ),
                'click',
                None
            ),
        ]
        self._orchestra(orchestrations, self._submitSize.__name__)

    def _clickPurchaseButton(self):
        orchestrations = [
            nikeWeb.orchestration(
                None,
                (By.CLASS_NAME, 'js-buy'),
                'click',
                None
            ),
        ]
        self._orchestra(orchestrations, self._clickPurchaseButton.__name__)

    def _submitAddress(self):
        # Is there address already setup?
        try:
            self.driver.find_element_by_class_name('payment')
        except NoSuchElementException, e:
            # Need to submit address
            # TODO: Need to verify.
            '''
            newDriver = WebDriverWait(self.driver, nikeWeb.TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'shipping-component'))
            )
            time.sleep(3)
            orchestrations = [
                nikeWeb.orchestration(
                    newDriver,
                    (By.CLASS_NAME, 'open-close'),
                    'click',
                    None
                ),
                nikeWeb.orchestration(
                    newDriver,
                    (By.LINK_TEXT, u'添加新地址'),
                    'click',
                    None
                ),
                nikeWeb.orchestration(
                    newDriver,
                    (By.XPATH, '//*[@id="last-name-shipping"]'),
                    'send_keys',
                    SURNAME
                ),
                #......
            ]
            self._orchestra(orchestrations, self._submitAddress.__name__)
            '''
        else:
            # No need to submit address
            return

    def _payment(self):
        orchestrations = [
            nikeWeb.orchestration(
                None,
                (By.XPATH, '//a[@data-provide="aliPayId"]'),
                'click',
                None
            ),
            nikeWeb.orchestration(
                None,
                (By.LINK_TEXT, u'保存并继续'),
                'click',
                None
            ),
#            nikeWeb.orchestration(
#                None,
#                (By.LINK_TEXT, u'提交订单'),
#                'click',
#                None
#            ),
        ]
        self._orchestra(orchestrations, self._payment.__name__)

    def startOrchestration(self):
        self._login()
        self._submitSize()
        self._clickPurchaseButton()
        self._submitAddress()
        self._payment()

    def close(self):
        self.driver.close()

def main():
    # Chinese support
    reload(sys)
    sys.setdefaultencoding('utf8')

    # TODO: load configuration from DB
    db = database()
    iteration = iter(db.info)
    context = {}

    try:
        rec = iteration.next()
        while True:
            # start process
            try:
                nike = nikeWeb()
                nike.USER_NAME, nike.PASSWD, nike.SHOE_SIZE = tuple(rec)
                context[nike.USER_NAME] = nike
                nike.startOrchestration()
            except doItAgain, e:
                print("{username} Failed! try again!".format(
                    username = nike.USER_NAME
                ))
                nike.close()
                time.sleep(10)
                continue
            else:
                print("Deal for {username} is done!".format(username = nike.USER_NAME))
                rec = next(iteration)
                time.sleep(10)
    except StopIteration:
        pass

    time.sleep(60)


if __name__ == '__main__':
    main()
