#!/usr/bin/env python3

import os


try:_=os.system("apt-get -y install ipmitool")
except:pass
try:_=os.system("apt -y install  libsensors4-dev ")
except:pass
try:_=os.system("apt -y install python-paho-mqtt ")
except:pass


#function of import and install
class Easy_installer:
    import os
    import subprocess


    def __init__(self):
        import subprocess
        try:
            MAX_PATH = int(subprocess.check_output(['getconf', 'PATH_MAX', '/']))
        except (ValueError, subprocess.CalledProcessError, OSError):
            try:
                deprint('calling getconf failed - error:', traceback=True)
                MAX_PATH = 4096
            except:
                print("MAX_PATH had and issue...")
        try:_=os.system("apt -y install python3-pip")
        except:pass
        try:_=os.system("apt -y install git")
        except:pass
        try:_=os.system("apt -y install python3-dev ")
        except:pass
        try:_=os.system("apt -y install  libsensors4-dev ")
        except:pass


    def install_and_import(self,package):
        try:
            import importlib
            try:
                importlib.import_module(package)
            except ImportError:
                import pip
                try:
                    from pip._internal import main
                except:
                    from pip import main
                print("installing: "+package)
                try:
                    temp=main(['install', package])
                    globals()[package] = importlib.import_module(package)
                except:
                    main(['install',"--no-cache-dir", package,"--user"])
            finally:
                globals()[package] = importlib.import_module(package)
        except:
            import warnings
            warnings.warn("Warning "+str(package)+" might not have been installed...")



    def install_and_import_special(self,url,command=None):
        #self.install_and_import("gitpython")
        #from git import Repo
        try:os.system("git clone "+url)
        except:pass
        self.install_and_import("warnings")

        #Repo.clone_from(url, '''''')

        if not type(command)==type(None):
            os.chdir(url.split('/')[-1].replace(".git",""))
            os.system(command)
            os.chdir("..")
        else:warnings.warn("No install command for: "+str(url))


    def easy(self,url,import_name=None,easy_command=None):
        if type(import_name)==type(None) and not type(easy_command)==type(None):
            self.install_and_import_special(url,command=easy_command)
        elif not type(import_name)==type(None) and type(easy_command)==type(None):
            self.install_and_import(url)
            self.install_and_import(import_name)
        elif not type(import_name)==type(None) and not type(easy_command)==type(None):
            self.install_and_import_special(url,command=easy_command)
            self.install_and_import(import_name)




easy=Easy_installer()
easy.easy("pyyaml",import_name="yaml")
easy.easy("http://github.com/bastienleonard/pysensors.git",import_name="sensors",easy_command="python3 setup.py build; python3 setup.py install")


easy.easy("signal")
easy.easy("https://github.com/eclipse/paho.mqtt.python","paho.mqtt.client","python3 setup.py install")
#easy.easy("paho-mqtt","paho")

#easy.easy("json")
easy.easy("getopt")






import yaml
import getopt
import os
import re
import sensors # https://github.com/bastienleonard/pysensors.git
import subprocess
import sys
import time
import signal
import paho.mqtt.client as mqtt
import subprocess
import json

uid='proxmoxmini' #RPiSensor #RPiRTC #RPiFTP
mqttserver="192.168.1.30"
#ftpserver='pi@192.168.1.2'
port=1883


gpu_temp=0
gpu_history=[]
print(uid)





# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global uid
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#")
    client.publish('success/boot',uid)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global uid
    global ftpserver
    global gpu_temp
    global gpu_history
    output=None
    #<<<<<<<<<<<<<<<clock handler>>>>>>>>>>>>>>>>>>>>
    #if msg.topic == 'clock': #handles all clock
        #if len(msg.payload.decode('UTF-8')) <=27:
        #    output=os.system('sudo date -s '+"'"+msg.payload.decode('UTF-8')+"'")
        #    if output==0:
        #        #print('success/'+uid+'/clock/set'+' '+msg.payload.decode('UTF-8'))
        #        client.publish('success/'+uid+'/clock/set',msg.payload.decode('UTF-8'))
        #    else:
        #        #print('error/'+uid+'/clock/set'+' '+str(output))
        #        client.publish('error/'+uid+'/clock/set',str(output))
        #else:
        #    output='To Long'
        #    #print('error/'+uid+'/clock/set'+' '+output)
        #    client.publish('error/'+uid+'/clock/set',str(output))

    if msg.topic=='rollcall':#returns the uid used to see if till active
        if msg.payload.decode('UTF-8')=='1':
            client.publish('rollcall/devices',str(uid))
            client.publish('rollcall/devices',str(uid)+" "+str('''/opt/fan_control'''))
            client.publish('rollcall/devices',str(uid)+" "+str('''/etc/systemd/system/fan-control.service'''))
            client.publish('rollcall/devices',str(uid)+" "+str('''"query/temp 0"(tempature of gpu in celsus)''' ))
    if msg.topic=='command/start':
        if msg.payload.decode('UTF-8')=='1':
            #output=os.system('raspivid -t 0 -o /home/pi/Desktop/'+uid+'.h264 &')#-w 64 -h 64
            if output==0:
                client.publish('success/start/'+uid+'/placeholder',str(output))
            else:
                client.publish('error/start/'+uid+'/placeholder',str(output))
            
    if msg.topic=='command/stop':
        if msg.payload.decode('UTF-8')=='1':
            set_fan_control("automatic", host)
            #output=os.system('sudo pkill raspivid')
            if output==0:
                client.publish('success/stop/'+uid+'/video',str(output))
            else:
                client.publish('error/stop/'+uid+'/video',str(output))
    if msg.topic=='query/inlettemp':
        if msg.payload.decode('UTF-8')=='1' or True:
            try:
                p = subprocess.Popen("ipmitool sensor | grep " + '"Inlet Temp"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                #for shell=False use absolute paths
                p_stdout = p.stdout.read().decode("utf-8")
                p_stderr = p.stderr.read().decode("utf-8")
                #print (p_stdout)
                #print (p_stderr)
            
                output=int(round(float(p_stdout.split("|")[1].replace(" ",""))))


            #output=os.system('MP4Box -add /home/pi/Desktop/'+uid+'.h264 /home/pi/Desktop/'+uid+'.mp4')
            except:
                output=-100

            if output!=-100:
                client.publish('data/inlettemp/'+uid,str(output)+" °C")
            else:
                client.publish('error/inlettemp/'+uid,str(output)+" °C")
    #if msg.topic=='command/upload':
    #    if msg.payload.decode('UTF-8')=='1':
    #        temp=" -e 'ssh -i /home/pi/.ssh/id_rsa -o StrictHostKeyChecking=no'"
    #        #output=os.system('rsync -avip'+temp+' /home/pi/Desktop/'+uid+'.mp4'+' '+ftpserver+':/home/pi/stuff/'+' >/home/pi/Desktop/fil$
    #        if output==0:
    #            client.publish('success/upload/'+uid,str(output))
    #        else:
    #            client.publish('error/upload/'+uid,str(output))


    #log all data on mqtt
    print(msg.topic+" "+msg.payload.decode('UTF-8'))





    if msg.topic=='query/temp':
        if msg.payload.decode('UTF-8')=='1' or True:


           
            #output=os.system('MP4Box -add /home/pi/Desktop/'+uid+'.h264 /home/pi/Desktop/'+uid+'.mp4')
            try:
                output=int(round(float(msg.payload.decode('UTF-8'))))
                gpu_temp=output
                gpu_history.append(output)
            except:
                output=0

            if output!=0:
                client.publish('success/temp/'+uid,str(output)+" °C")
            else:
                client.publish('error/temp/'+uid,str(output)+" °C")
    #if msg.topic=='command/upload':
    #    if msg.payload.decode('UTF-8')=='1':
    #        temp=" -e 'ssh -i /home/pi/.ssh/id_rsa -o StrictHostKeyChecking=no'"
    #        #output=os.system('rsync -avip'+temp+' /home/pi/Desktop/'+uid+'.mp4'+' '+ftpserver+':/home/pi/stuff/'+' >/home/pi/Desktop/file.txt 2>&1')
    #        if output==0:
    #            client.publish('success/upload/'+uid,str(output))
    #        else:
    #            client.publish('error/upload/'+uid,str(output))
        

    #log all data on mqtt
    print(msg.topic+" "+msg.payload.decode('UTF-8'))
    

client = mqtt.Client() #client_id='mosquitto',password='raspberry'
client.on_connect = on_connect
client.on_message = on_message

temp=1
while temp!=0:
    try:
        temp=client.connect(mqttserver, port, 60)
    except:
        try:
            print("Waiting 30 seconds...")
            time.sleep(30)
            temp=client.connect(mqttserver, port, 60)
        except:
            pass
        while temp!=0:
            for i in range(0,256):
                for j in range(0,255):
                    try:
                        print("Trying to connect to "+"192.168."+str(i)+"."+str(j))
                        temp=client.connect("192.168."+str(i)+"."+str(j), port, 60)
                    except:
                        pass
        
client.loop_start() #this is a nonblocking loop that has to be stopped with client.loop_stop(force=False)




















config = {
    'config_path': '/opt/fan_control/fan_control.yaml',
    'general': {
        'debug': False,
        'interval': 60
    },
    'hosts': []
}
state = {}

class ConfigError(Exception):
    pass

def ipmitool(args, host):
    global state

    cmd = ["ipmitool"]
    if state[host['name']]['is_remote']:
        cmd += ['-I', 'lanplus']
        cmd += ['-H', host['remote_ipmi_credentials']['host']]
        cmd += ['-U', host['remote_ipmi_credentials']['username']]
        cmd += ['-P', host['remote_ipmi_credentials']['password']]
    cmd += (args.split(' '))
    if config['general']['debug']:
        print(re.sub(r'-([UP]) (\S+)', r'-\1 ___', ' '.join(cmd))) # Do not log IPMI credentials
        return True

    try:
        subprocess.check_output(cmd, timeout=15)
    except subprocess.CalledProcessError:
        print("\"{}\" command has returned a non-0 exit code".format(cmd), file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("\"{}\" command has timed out".format(cmd), file=sys.stderr)
        return False
    return True

def set_fan_control(wanted_mode, host):
    global state

    if wanted_mode == "manual" or wanted_mode == "automatic":
        if wanted_mode == "manual" and state[host['name']]['fan_control_mode'] == "automatic":
            if not config['general']['debug']:
                print("[{}] Switching to manual mode".format(host['name']))
            ipmitool("raw 0x30 0x30 0x01 0x00", host)
        elif wanted_mode == "automatic" and state[host['name']]['fan_control_mode'] == "manual":
            if not config['general']['debug']:
                print("[{}] Switching to automatic mode".format(host['name']))
            ipmitool("raw 0x30 0x30 0x01 0x01", host)
            state[host['name']]['fan_speed'] = 0

        state[host['name']]['fan_control_mode'] = wanted_mode

def set_fan_speed(threshold_n, host):
    global state

    wanted_percentage = host['speeds'][threshold_n]
    if wanted_percentage == state[host['name']]['fan_speed']:
        return

    if 5 <= wanted_percentage <= 100:
        wanted_percentage_hex = "{0:#0{1}x}".format(wanted_percentage, 4)
        if state[host['name']]['fan_control_mode'] != "manual":
            set_fan_control("manual", host)
            time.sleep(1)
        if not config['general']['debug']:
            print("[{}] Setting fans speed to {}%".format(host['name'], wanted_percentage))
        ipmitool("raw 0x30 0x30 0x02 0xff {}".format(wanted_percentage_hex), host)
        state[host['name']]['fan_speed'] = wanted_percentage
    client.publish('success/fanspeed/'+uid,str(wanted_percentage)+"%")

def parse_config():
    global config
    _debug = config['general']['debug']
    _interval = config['general']['interval']

    if not os.path.isfile(config['config_path']):
        raise RuntimeError("Missing or unspecified configuration file.")
    else:
        print("Loading configuration file.")
        _config = None
        try:
            with open(config['config_path'], 'r') as yaml_conf:
                _config = yaml.safe_load(yaml_conf)
        except yaml.YAMLError as err:
            raise err # TODO: pretty print
        config = _config
        if 'debug' not in list(config['general'].keys()):
            config['general']['debug'] = _debug
        if 'interval' not in list(config['general'].keys()):
            config['general']['interval'] = _interval

        for host in config['hosts']:
            if 'hysteresis' not in list(host.keys()):
                host['hysteresis'] = 0
            if len(host['temperatures']) != 10:
                raise ConfigError('Host "{}" has {} temperature thresholds instead of 10.'.format(host['name'], len(host['temperatures'])))
            if len(host['speeds']) != 10:
                raise ConfigError('Host "{}" has {} fan speeds instead of 10.'.format(host['name'], len(host['speeds'])))
            if ('remote_temperature_command' in list(host.keys()) or 'remote_ipmi_credentials' in list(host.keys()))  and \
                ('remote_temperature_command' not in list(host.keys()) or 'remote_ipmi_credentials' not in list(host.keys())):
                raise ConfigError('Host "{}" must specify either none or both "remote_temperature_command" and "remote_ipmi_credentials" keys.'.format(host['name']))
            if 'remote_ipmi_credentials' in list(host.keys()) and \
                ('host' not in list(host['remote_ipmi_credentials'].keys()) or \
                'username' not in list(host['remote_ipmi_credentials'].keys()) or \
                'password' not in list(host['remote_ipmi_credentials'].keys())):
                raise ConfigError('Host "{}" must specify either none or all "host", "username" and "password" values for the "remote_ipmi_credentials" key.'.format(host['name']))
            # TODO: check presence/validity of values instead of keys presence only

            if host['name'] in list(state.keys()):
                raise ConfigError('Duplicate "{}" host name found.'.format(host['name']))
            state[host['name']] = {
                'is_remote': 'remote_temperature_command' in list(host.keys()),
                'fan_control_mode': 'automatic',
                'fan_speed': 0
            }

def parse_opts():
    global config
    help_str = "fan_control.py [-d] [-c <path_to_config>] [-i <interval>]"

    try:
        opts, _ = getopt.getopt(sys.argv[1:],"hdc:i:",["help","debug","config=","interval="])
    except getopt.GetoptError as e:
      print("Unrecognized option. Usage:\n{}".format(help_str))
      raise getopt.GetoptError(e)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_str)
            raise InterruptedError
        elif opt in ('-d', '--debug'):
            config['general']['debug'] = True
        elif opt in ('-c', '--config'):
            config['config_path'] = arg
        elif opt in ('-i', '--interval'):
            config['general']['interval'] = arg

def checkHysteresis(temperature, threshold_n, host):
    global state

    return(True)
    return (
        not host['hysteresis'] or
        (
            host['hysteresis'] and (
                state[host['name']]['fan_speed'] > host['speeds'][threshold_n] or
                state[host['name']]['fan_control_mode'] == 'automatic'
            ) and
            temperature <= host['temperatures'][threshold_n] - host['hysteresis']
        )
    )

def compute_fan_speed(temp_average, host):
    global state

    if config['general']['debug']:
        print("[{}] T:{}°C M:{} S:{}%".format(host['name'], temp_average, state[host['name']]['fan_control_mode'], state[host['name']]['fan_speed']))
    temp=host['temperatures']
    #print(temp)
    for i in range(0,len(temp)-1):
        #print(str(host['temperatures'][i] < temp_average <= host['temperatures'][i+1])+str( checkHysteresis(temp_average, i, host)))

        #print("current temp: "+str(temp_average)+" LowRange: "+str(temp[i])+" HighRange: "+str(temp[i+1]))
        if (
            temp_average <= host['temperatures'][0] and
            checkHysteresis(temp_average, 0, host)
        ):
            print("current temp: "+str(temp_average)+" LowRange: "+str(temp[i])+" HighRange: "+str(temp[i+1]))
            set_fan_speed(0, host)
        # Threshold0 < Tavg ≤ Threshold1
        elif (
            host['temperatures'][i] < temp_average <= host['temperatures'][i+1] and
            checkHysteresis(temp_average, i, host)
        ):
            print("current temp: "+str(temp_average)+" LowRange: "+str(temp[i])+" HighRange: "+str(temp[i+1]))
            set_fan_speed(i, host)






#    # Tavg < Threshold0
#    if (
#        temp_average <= host['temperatures'][0] and
#        checkHysteresis(temp_average, 0, host)
#    ):
#        set_fan_speed(0, host)
#
#    # Threshold0 < Tavg ≤ Threshold1
#    elif (
#        host['temperatures'][0] < temp_average <= host['temperatures'][1] and
#        checkHysteresis(temp_average, 1, host)
#    ):
#        set_fan_speed(1, host)
#
#    # Threshold1 < Tavg ≤ Threshold2
#    elif (
#        host['temperatures'][1] < temp_average <= host['temperatures'][2] and
#        checkHysteresis(temp_average, 2, host)
#    ):
#        set_fan_speed(2, host)
#
#   # Threshold2 < Tavg ≤ Threshold3
#    elif (
#        host['temperatures'][2] < temp_average <= host['temperatures'][3] and
#        checkHysteresis(temp_average, 3, host)
#    ):
#        set_fan_speed(3, host)
#
#   # Threshold3 < Tavg ≤ Threshold4
#    elif (
#        host['temperatures'][3] < temp_average <= host['temperatures'][4] and
#        checkHysteresis(temp_average, 2, host)
#    ):
#        set_fan_speed(2, host)




def main():
    global config
    global state
    global gpu_temp

    print("Starting fan control script.")
    for host in config['hosts']:
        print("[{}] Thresholds of {}°C ({}%), {}°C ({}%), {}°C ({}%), {}°C ({}%), {}°C ({}%), {}°C ({}%), {}°C ({}%), {}°C ({}%), {}°C ({}%), {}°C ({}%)".format(
                host['name'],
                host['temperatures'][0], host['speeds'][0],
                host['temperatures'][1], host['speeds'][1],
                host['temperatures'][2], host['speeds'][2],
                host['temperatures'][3], host['speeds'][3],
                host['temperatures'][4], host['speeds'][4],
                host['temperatures'][5], host['speeds'][5],
                host['temperatures'][6], host['speeds'][6],
                host['temperatures'][7], host['speeds'][7],
                host['temperatures'][8], host['speeds'][8],
                host['temperatures'][9], host['speeds'][9],
            ))

    while True:
        for host in config['hosts']:
            temps = []

            if not state[host['name']]['is_remote']:
                cores = []
                for sensor in sensors.get_detected_chips():
                    if sensor.prefix == "coretemp":
                        cores.append(sensor)
                for core in cores:
                    for feature in core.get_features():
                        for subfeature in core.get_all_subfeatures(feature):
                            if subfeature.name.endswith("_input"):
                                temps.append(core.get_value(subfeature.number))
            else:
                cmd = os.popen(host['remote_temperature_command'])
                temps = list(map(lambda n: float(n), cmd.read().strip().split('\n')))
                cmd.close()


###############################GPU Logic#####################################
            max_over_time=10
            temp_average = round(sum(temps)/len(temps))
            if gpu_temp >= temp_average:
                print("Average temp: "+str(temp_average)+" C")
                client.publish('query/temp/cpu/'+uid,str(temp_average)+" C")
                client.publish('query/temp/gpu/'+uid,str(gpu_temp)+" C")
                temp_average = gpu_temp
                if len(gpu_history)>max_over_time:
                    temp_average=max(gpu_history)
                    while len(gpu_history)>max_over_time+2:
                        _=gpu_history.pop(0)
#############################################################################
            compute_fan_speed(temp_average, host)

        time.sleep(config['general']['interval'])


def graceful_shutdown(signalnum, frame):
    print("Signal {} received, giving up control".format(signalnum))
    for host in config['hosts']:
        set_fan_control("automatic", host)
    try:
        client.loop_stop(force=False)
    except:
        pass
    sys.exit(0)


if __name__ == "__main__":
    # Reset fan control to automatic when getting killed
    signal.signal(signal.SIGTERM, graceful_shutdown)

    try:
        try:
            parse_opts()
        except (getopt.GetoptError, InterruptedError):
            sys.exit(1)
        parse_config()
        main()
    finally:
        sensors.cleanup()

