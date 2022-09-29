from utime import sleep
from machine import Pin
import network
from mqtt import MQTTClient

from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_VEML6030 import PiicoDev_VEML6030

import secrets as s

#from workshop_lib import wifiConnect,wlanInit

# Lets control our onboard LED through the MQTT server
led_onboard = machine.Pin("LED", machine.Pin.OUT)

# Initialise the atmospheric, colour sensor and display
atmo = PiicoDev_BME280()

wlan = network.WLAN(network.STA_IF) # ...tell it to be a station - or a node/endpoint
wlan.active(True) # ... Turn the radio on

wlan.connect(s.s_ssid, s.s_password)


if wlan.isconnected() and wlan.active():
   print('already conn')
else:
    wlan.active(True)
    while wlan.isconnected() == False:
        sleep(1)
        print('trying again')

print('WiFi Connected')

# Create an MQTT client
client_ID = 'picowhub'
server = 'server-ip'
user='mqtt-user'
api_key = 'password'

client = MQTTClient(client_ID, server,user=user, password=api_key, port=1883)

# Create a 'call back' function - more on this later
def sub_cb(topic, msg):
    # Callback from MQTT
    print(msg)
    print(topic)


# Configure the MQTT connection
client.set_callback(sub_cb) # Specify the function that is run when new data is avialable from the MQTT server
client.connect() # Use provided details to connect to MQTT server
client.subscribe('test/test') # Where we want to check on the MQTT server


while True:
    print("LED state: " ,str(led_onboard.value())) # Print the local LED state to REPL
    
    
    client.check_msg() # Check the MQTT server for updates
    
    # Getting the sensor data into a nice format, removing 
    tempC, presPa, humRH = atmo.values()
    tempC_str = "{:.1f}".format(tempC)
    humRH_str = "{:.1f}".format(humRH)
    print(tempC_str,humRH_str)
    # Make sure wlan is connected before we send to AdafruitIO
    if wlan.isconnected():
        
        #client.publish(topic='sens/feeds/workshop-examples.onboard-led', msg=str(led_onboard.value()))
        client.publish(topic='mqtt-raw/liams-room/picowhub.temperature-data', msg=tempC_str)
        client.publish(topic='mqtt-raw/liams-room/picowhub.humidity-data', msg=humRH_str)
    else:
        # If WiFi is disconnected, ensure it is and reconnect
        wlan.disconnect()
        wifiConnect(wlan)
    
    
    # Wait a bit before sending more data, even 3 seconds is pretty short!
    #print("Waiting...")
    sleep(3)