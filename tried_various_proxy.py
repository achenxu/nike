#coding = utf-8


import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from remoteFn import action


useProxy = 0
startHubCmd = 'java -jar /opt/nike/selenium-server-standalone-3.8.1.jar -role hub &'
startNodeCmd = 'java -jar /opt/nike/selenium-server-standalone-3.8.1.jar -role node -hub http://{hub_ip}:4444/grid/register -maxSession 35 -browser browserName=firefox,maxInstances=35,platform=LINUX,seleniumProtocol=WebDriver &'
stopCmd = 'killall java'

 
class gridService(object):
    def __init__(self):
        self.nodes = []
        with open("nodes.csv") as f :
            csvFile = csv.reader(f)
            for row in csvFile :
                dic={}
                dic['IP']=row[0]
                dic['MaxSession']=row[1]
                self.nodes.append(dic)
        print self.nodes

    def startService(self):
        #ensure environment clean
        gridService.stopService(self)

        #start hub
        print 'Start Hub Service'
        os.system(startHubCmd)
        
        #start nodes
        hub_ip = self.nodes[0]['IP']
        print 'hub_ip is ', hub_ip
        for node in self.nodes:
            print 'Start Node Service On ', node['IP']
            conn = action(node['IP'], command=startNodeCmd.format(hub_ip = hub_ip))
            conn.ssh_connect()

    def stopService(self):
       for node in self.nodes:
            print 'Stop Service On ', node['IP']
            conn = action(node['IP'], stopCmd)
            conn.ssh_connect()

    def restartService(self):
        gridService.stoptService(self)
        gridService.startService(self)


def main():
    grid = gridService()
    grid.startService()
    time.sleep(20)
    grid.stopService()
    exit()

#capabilities = DesiredCapabilities.CHROME
capabilities = DesiredCapabilities.FIREFOX
capabilities["platform"] = "ANY"
capabilities["maxInstances"] = 35


'''
proxy = Proxy(
{
# 'proxyType': ProxyType.MANUAL,
'httpProxy': "not_sure:8888"
}
)
'''
'''
proxy = webdriver.Proxy()  
proxy.proxy_type = ProxyType.MANUAL  
proxy.http_proxy = "192.168.1.1:22"
'''


profile = webdriver.FirefoxProfile()
profile.set_preference('network.proxy.type', 1)
profile.set_preference('network.proxy.http', '192.168.2.1')
profile.set_preference('network.proxy.http_port', 1234)
profile.set_preference('network.proxy.ssl', 'proxy_url')
profile.set_preference('network.proxy.ssl_port', 3128)
profile.update_preferences()


#driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities, proxy=proxy)
#driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities, browser_profile=profile)
#driver1 = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities, browser_profile=profile)
#driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities)
driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities)
driver1 = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities)

#driver1 = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities )
#driver2 = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities )
#driver3 = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities )
#driver4 = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities )
#driver5 = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities )
#driver = webdriver.Ie()

#driver.implicitly_wait(3)

#time.sleep(15)

driver.get("https://www.baidu.com")
driver1.get("https://www.baidu.com")
#driver2.get("https://www.baidu.com")
#driver3.get("https://www.baidu.com")
#driver4.get("https://www.baidu.com")
#driver5.get("https://www.baidu.com")

driver.find_element_by_id("kw").send_keys("python")
driver1.find_element_by_id("kw").send_keys("python")
#driver2.find_element_by_id("kw").send_keys("python")
#driver3.find_element_by_id("kw").send_keys("python")
#driver4.find_element_by_id("kw").send_keys("python")
#driver5.find_element_by_id("kw").send_keys("python")
driver.find_element_by_id("su").click()
driver1.find_element_by_id("su").click()
#driver2.find_element_by_id("su").click()
#driver3.find_element_by_id("su").click()
#driver4.find_element_by_id("su").click()
#driver5.find_element_by_id("su").click()

time.sleep(5)
driver.quit()
driver1.quit()
#driver2.quit()
#driver3.quit()
#driver4.quit()
#driver5.quit()

if __name__ == '__main__':
    main()
