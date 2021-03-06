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
import sched


# TODO: Shall we let user input the url?
# Address
# SURNAME = u'张'


class doItAgain(Exception):
    pass

class wrongShoeSize(Exception):
    pass

class WebDrv(object):
    TIMEOUT = 30

    orchestration = namedtuple(
        'orchestration',
        [
            'driver',
            'locator',
            'action',   # click or send_keys or save_screenshot
            'data',     # Optional, only for send_keys
        ],
        verbose = False
    )

    def __init__(self,
                 timer,
                 config,
                 drv = None):
        self.debug = config.DEBUG
        self.submit = config.SUBMIT
        self.selections = config.SELECTIONS
        self.addressMode = config.ADDRESSMODE
        self.config = config
        now = time.localtime()
        self.timer = time.mktime(
            time.strptime(
                "{year}-{month}-{day} {t}".format(
                    year=now.tm_year,
                    month=now.tm_mon,
                    day=now.tm_mday,
                    t=timer),
                "%Y-%m-%d %X")
        )
        if self.timer < time.mktime(now):
            print "Invalid timer! Will put the deal directly!"
            self.timer = None
        if drv == None:
            self.driver = webdriver.Chrome()
        else:
            self.driver = drv
        self.driver.maximize_window()
        self._reloadPage()

    def retry(func):
        def con(self, *args, **kargs):
            retry = True
            while (retry):
                try:
                    return func(self, *args, **kargs)
                except doItAgain, e:
                    pass
                except wrongShoeSize, e:
                    if len(self.selections) > 1:
                        self.selections.remove(self.SHOE_SIZE)
                    self.SHOE_SIZE = self.selections[0]
                else:
                    retry = False
        return con

    def _error_handle(self, n):
        #sys.exit(n)
        print("Some error happens, error code = {num}".format(num = n))
        raise doItAgain()

    def _reloadPage(self):
        self.driver.get(self.config.TARGET)
        try:
            # Confirm whether the page's opened
            WebDriverWait(self.driver, WebDrv.TIMEOUT).until(
                EC.title_contains(self.config.TITLE)
            )
        except TimeoutException, e:
            # Wrong URL?
            print("Cannot open the webpage")
            self._error_handle(1)

    def _orchestra(self, orchestrations, name):
        for orch in orchestrations :
            if orch.driver != None :
                driver = orch.driver
            else :
                driver = self.driver

            try:
                elem = WebDriverWait(driver, WebDrv.TIMEOUT).until(
                    EC.visibility_of_element_located(orch.locator)
                )
                print '##############after visibility of element located'
                if orch.action == 'click' :
                    WebDriverWait(driver, WebDrv.TIMEOUT).until(
                        EC.element_to_be_clickable(orch.locator)
                    )
                    elem.click()
                elif orch.action == 'send_keys':
                    elem.clear()
                    elem.send_keys(orch.data)
                elif orch.action == 'select':
                    elem.send_keys(orch.data)
                elif orch.action == 'save_screenshot':
                    driver.save_screenshot(self.USER_NAME + '.png')

            except (TimeoutException, WebDriverException, NoSuchElementException) as e:
                print("Error happens during running {script}! Error message is {err}"
                      .format(script = name, err = e))
                self._error_handle(2)

            time.sleep(1)

    def _login(self):
        print '###_login is executed'
        try:
            elem = self.driver.find_element_by_link_text(u'登录')
        except NoSuchElementException:
            loginStr =  u'加入/登录'
        else:
            loginStr = u'登录'

        orchestrations = [
            WebDrv.orchestration(
                None,
                (By.LINK_TEXT, loginStr),
                'click',
                None
            ),
            WebDrv.orchestration(
                None,
                (By.NAME, u'emailAddress'),
                'send_keys',
                self.USER_NAME
            ),
            WebDrv.orchestration(
                None,
                (By.NAME, u'password'),
                'send_keys',
                self.PASSWD
            ),
            WebDrv.orchestration(
                None,
                (By.CLASS_NAME, "nike-unite-submit-button"),
                'click',
                None
            ),
        ]
        self._orchestra(orchestrations, self._login.__name__)
        time.sleep(8)

    @retry
    def _submitSize(self):
        orchestrations = [
            WebDrv.orchestration(
                None,
                (By.CLASS_NAME, 'size-selector-component'),
                'click',
                None
            ),
            WebDrv.orchestration(
                None,
                (
                    By.XPATH,
                    '//li[@data-size="{size}"]'.format(size=self.SHOE_SIZE)
                ),
                'click',
                None
            ),
        ]
        try:
            self._orchestra(orchestrations, self._submitSize.__name__)
        except doItAgain, e:
            # The shoe size's unavailable, need to select another size
            raise wrongShoeSize()

    @retry
    def _clickPurchaseButton(self):
        orchestrations = [
            WebDrv.orchestration(
                None,
                (By.CLASS_NAME, 'js-buy'),
                'click',
                None
            ),
            WebDrv.orchestration(
                None,
                (By.LINK_TEXT, u'确定'),
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
            newDriver = WebDriverWait(self.driver, WebDrv.TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'shipping-component'))
            )
            time.sleep(3)
            orchestrations = [
                WebDrv.orchestration(
                    newDriver,
                    (By.CLASS_NAME, 'open-close'),
                    'click',
                    None
                ),
                WebDrv.orchestration(
                    newDriver,
                    (By.LINK_TEXT, u'添加新地址'),
                    'click',
                    None
                ),
                WebDrv.orchestration(
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

    @retry
    def _payment(self):
        orchestrations = [
            WebDrv.orchestration(
                None,
                (By.XPATH, '//a[@data-provide="aliPayId"]'),
                'click',
                None
            ),
            WebDrv.orchestration(
                None,
                (By.LINK_TEXT, u'保存并继续'),
                'click',
                None
            ),
        ]
        if self.submit :
            orchestrations.append(
                WebDrv.orchestration(
                    None,
                    (By.LINK_TEXT, u'提交订单'),
                    'click',
                    None
                )
            )
            orchestrations.append(
                WebDrv.orchestration(
                    None,
                    (By.CLASS_NAME, u'js-confirm'),
                    'click',
                    None
            ),
            )

        self._orchestra(orchestrations, self._payment.__name__)

    def _prepare(self):
        orchestrations = [
            WebDrv.orchestration(
                None,
                (By.CSS_SELECTOR, 'a[href="{ref}"]'.format(ref=SHOE_URL)),
                'click',
                None
            ),
        ]
        self._orchestra(orchestrations, self._prepare.__name__)

    def _getPaymentQR(self):
        orchestrations = [
            WebDrv.orchestration(
                None,
                (By.CLASS_NAME, 'QRIframeContainer'),
                'save_screenshot',
                None
            ),
        ]
        self._orchestra(orchestrations, self._prepare.__name__)

    def _modifyAddress(self):
        # Click purchase button
        orchestrations =  [
            WebDrv.orchestration(
                None,
                (By.CLASS_NAME, 'js-buy'),
                'click',
                None
            )
        ]
        self._orchestra(orchestrations, self._modifyAddress.__name__)
        time.sleep(5)

        drv = self.driver.find_element_by_class_name("shipping-component")
        orchestrations = [
            WebDrv.orchestration(
                drv,
                (By.CLASS_NAME, 'open-close'),
                'click',
                None
            ),
            WebDrv.orchestration(
                None,
                (By.CLASS_NAME, 'js-edit'),
                'click',
                None
            ),
            WebDrv.orchestration(
                None,
                (By.ID, 'last-name-shipping'),
                'send_keys',
                self.config.ADDRESS.surname
            ),
            WebDrv.orchestration(
                None,
                (By.ID, 'first-name-shipping'),
                'send_keys',
                self.config.ADDRESS.firstname
            ),
            WebDrv.orchestration(
                None,
                (By.ID, 'shipping-address-1'),
                'send_keys',
                self.config.ADDRESS.shippingAddress
            ),
            WebDrv.orchestration(
                None,
                (By.ID, 'shipping-address-2'),
                'send_keys',
                ' '
            ),

            WebDrv.orchestration(
                None,
                (By.ID, 'zipcode'),
                'send_keys',
                self.config.ADDRESS.postcode
            ),
            WebDrv.orchestration(
                None,
                (By.ID, 'phone-number'),
                'send_keys',
                self.config.ADDRESS.cellphone
            ),
        ]
        self._orchestra(orchestrations, self._modifyAddress.__name__)

        # TODO: Following code is hack. But it's the only way I can make it
        # work.Right now I can't find the zone-option via classname,
        # will fix it in the future.
        selectItems = self.driver.find_elements_by_tag_name('select')
        selectItems[1].send_keys(u'上海市')
        selectItems[2].send_keys(u'上海市')
        selectItems[3].send_keys(self.config.ADDRESS.zone)

        orchestrations = [
            WebDrv.orchestration(
                None,
                (By.LINK_TEXT, u'保存并继续'),
                'click',
                None
            ),
        ]
        self._orchestra(orchestrations, self._modifyAddress.__name__)

    def startOrchestration(self):
        self._login()
        if self.addressMode:
            self.addressModificationProcess()
            print("{username}'s address's fixed, please confirm.".format(username=self.USER_NAME))
            raw_input()
            return
        if self.timer:
            s = sched.scheduler(time.time, time.sleep)
            s.enterabs(self.timer, 0, self.purchaseProcess, [])
            s.run()
        else:
            self.purchaseProcess()

    def addressModificationProcess(self):
        print("{t}:Now try to modify {u}'s address!".format(t = time.asctime(time.localtime()), u = self.USER_NAME))
        WebDriverWait(self.driver, WebDrv.TIMEOUT).until(
                EC.element_to_be_clickable((
                    By.CLASS_NAME,
                    'size-selector-component'
                ))
        )
        self._submitSize()
        self._modifyAddress()

    def purchaseProcess(self):
        print("{t}:Orchestration of {u} starts!".format(t = time.asctime(time.localtime()), u = self.USER_NAME))
        #self._reloadPage()
        WebDriverWait(self.driver, WebDrv.TIMEOUT).until(
                EC.element_to_be_clickable((
                    By.CLASS_NAME,
                    'size-selector-component'
                ))
        )
        self._submitSize()
        self._clickPurchaseButton()
        self._submitAddress()
        self._payment()
        while(1):
            print("{username}: Taking screenshot to {picname}".format(username=self.USER_NAME, picname=self.USER_NAME + '.png'))
            self._getPaymentQR()
            time.sleep(100)

    def close(self):
        self.driver.close()
