
import paramiko

class action(object):
    def __init__(self, IP, command, username="root", password="123456"):
        self.IP = IP
        self.username = username
        self.password = password
        self.command = command

    def ssh_connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=self.IP, username=self.username, password=self.password)
            stdin,stdout,stderr=ssh.exec_command(self.command)
            print "######################> %s <####################" %(self.IP)
#            print stderr.read()
#            print stdout.read()
            ssh.close()
 
        except Exception,e:
            print "######################> %s <####################" %(self.IP)
            print



def get_values(hostname):
    conf_file=open('scn.conf','r')
    lines = conf_file.readlines()
    for line in lines:
        line = line.strip("\n")
        line = eval(line) 
        if  hostname == line["hostname"]:
            return(line)
            break
    conf_file.close()


if __name__ == "__main__":
      
    #hostname = raw_input("write your hostname:")
    #username = raw_input("write your username:")
    #password = raw_input("write your password:")
    # command = raw_input("write your excute command:")
     #host = get_values(hostname)
     #host_ip = list(host["host_ip"])
     host_ip = ["192.168.2.10",]
     command = 'java -jar /opt/nike/selenium-server-standalone-3.8.1.jar -role node -hub http://{hub_ip}:4444/grid/register -maxSession 35 -browser browserName=firefox,maxInstances=35,platform=LINUX,seleniumProtocol=WebDriver &'.format(hub_ip='192.168.2.6')

     print 'command is: ', command
     
     for i in range(0,len(host_ip)):
        #conn = action(host_ip[i],username,password,command)
         conn = action(host_ip[i], command=command)
         conn.ssh_connect()
