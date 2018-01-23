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
accountNum = 5
startHubCmd = 'java -jar /opt/nike/selenium-server-standalone-3.8.1.jar -role hub &'
NodeFile = '/opt/nike/nodeStarter.sh'
startNodeCmd = 'echo "java -jar /opt/nike/selenium-server-standalone-3.8.1.jar -role node -hub http://{hub_ip}:4444/grid/register -maxSession {max_sessions} -browser browserName=firefox,maxInstances={max_instances},platform=LINUX,seleniumProtocol=WebDriver &" > {file_name}'
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
        
        #start nodes
        hub_ip = self.nodes[0]['IP']
        print 'hub_ip is ', hub_ip
        for node in self.nodes:
            print 'Start Node Service On ', node['IP']
            conn = action(node['IP'], command=startNodeCmd.format(hub_ip = hub_ip, max_sessions=node['MaxSession'], max_instances=node['MaxSession'],file_name = NodeFile))
            conn.ssh_connect()

        #start hub
        print 'Start Hub Service'
        os.system(startHubCmd)
        
        #sleep 5 seconds for service start
        time.sleep(5)

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

    capabilities = DesiredCapabilities.FIREFOX
    capabilities["platform"] = "ANY"
    capabilities["maxInstances"] = 35

    # proxy works now but need try ip agent services
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.http', '192.168.2.1')
    profile.set_preference('network.proxy.http_port', 1234)
    profile.set_preference('network.proxy.ssl', 'proxy_url')
    profile.set_preference('network.proxy.ssl_port', 3128)
    profile.update_preferences()


    #start browsers
    drivers = []
    for i in range(accountNum):
        if useProxy:
            driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities, browser_profile=profile)
        else:
            driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",  desired_capabilities=capabilities)
        drivers.append(driver)
        
    #get web
    for driver in drivers:
        driver.get("https://www.baidu.com")
        driver.find_element_by_id("kw").send_keys("python")
        driver.find_element_by_id("su").click()

    #quit
    time.sleep(5)
    for driver in drivers:
        driver.quit()

    #stop service
    grid.stopService()

if __name__ == '__main__':
    main()
