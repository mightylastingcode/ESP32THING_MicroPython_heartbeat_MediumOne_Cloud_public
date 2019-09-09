'''

Author: Michael Li
Date: 7/10/2019

Example: MQTT Publish & Subscribe 
		1. Publish heartbeat.
		2. Scuscribe LED switch command (0,1,2) from the server.
		     0 - off, 1 - on, 2 - toggle

Heart beat


msg length:  6
b'30000'
300.0
300.0
Time (minutes) =  1
Publish sensor data.
{'event_data': {'heartbeat': 'true'}}
Time (minutes) =  2
Publish sensor data.
{'event_data': {'heartbeat': 'true'}}


'''


import json
import machine
import sys
import time
import utime
import ubinascii

from machine import Pin
from umqtt.simple import MQTTClient


from machine import Pin, I2C
from light_sensor import LIGHT_Sensor

blueledstate = 0

# default MQTT setting
'''
SERVER 		= "mosquitto.org"
CLIENTID 	= ubinascii.hexlify(machine.unique_id());
PUB_TOPIC 	= b"xyzabc/fahrenheit"
SUB_TOPIC 	= b"xyzabc/led"
PORT 		= 1883
MQTT_USERNAME = None
MQTT_password = None

'''
'''
SERVER 		  = "<broker server>"
PORT 		  = <port number>
PUB_TOPIC 	  = b"0/<PROJECT MQTT>/<USER MQTT>/esp32thing"
SUB_TOPIC 	  = b"1/<PROJECT MQTT>/<USER MQTT>/esp32thing/event"
clientID      = "<PROJECT MQTT>/<USER MQTT>"
MQTT_USERNAME = "<PROJECT MQTT>/<USER MQTT>"
MQTT_password = "<API Key>/<API user password>"
'''


SERVER 		  = "mqtt.mediumone.com"
#PORT 		  = 61619  # non secured TCP port
PORT 		  = 61620  # secured TCP port  (SSL must be True)


PUB_TOPIC 	  = b"0/<PROJECT MQTT>/<USER MQTT>/esp32thing"
SUB_TOPIC 	  = b"1/<PROJECT MQTT>/<USER MQTT>/esp32thing/event"
clientID      = "<PROJECT MQTT>/<USER MQTT>"
MQTT_USERNAME = "<PROJECT MQTT>/<USER MQTT>"
MQTT_password = "<API Key>/<API user password>"

SAMPLING_TIME   = 60  # 1 minute
SAMPLING_LIGHT_TIME = 10 # 1 minute

def sub_cb(topic, msg):	
	global msg_rec_count
	global blueledstate
	global SAMPLING_TIME
	print ((topic,msg))  # an array of bytes, not char type.
	                     # need to convert with chr() for 
	                     # comparison.	
	length = len(msg)	
	print ("msg length: ", length)                                          
	if (length > 0):
		if chr(msg[0]) == 'S':	                     
			print (msg[1:length])
			new_sample_time = int(msg[1:length])/100  # convert from 10ms base to second base
			print (new_sample_time)
			SAMPLING_TIME = new_sample_time
			print (SAMPLING_TIME)
		# Toggle - L2
		# LED ON - L2:1
		# LED OFF - L2:0
		#if chr(msg[0]) == 'L' and chr(msg[1]) == '2':
		if chr(msg[0]) == 'L':
			print ("Toggle command!")
			if length == 2:
				print ("toggle led")		
				if blueledstate == 0:
					blueledstate = 1
					blueled.value(1)
				else:				
					blueledstate = 0
					blueled.value(0)
			elif length == 4:		
				print ("LED state")		
				if chr(msg[3]) == '1':
					print ("turn on led")
					blueledstate = 1
					blueled.value(1)
				elif chr(msg[3]) == '0':
					print ("turn off led")
					blueledstate = 0
					blueled.value(0)		

def main(clientID = CLIENTID, server = SERVER, topic = PUB_TOPIC):
	print ("Sampling time (sec):", SAMPLING_TIME)
	obj = {"event_data":{}}

	print ("Client ID: %s" % clientID)
	print ("MQTT broker server: %s" % server)
	print ("Topic: %s" % topic)
	c = MQTTClient(client_id=clientID, 
                    server=server, 
                    port=PORT,
                    user=MQTT_USERNAME, 
                    password=MQTT_password,
                    ssl=True)
	c.set_callback(sub_cb)
	if c.connect() == 0:
		print('cCient connect status : Success')	
	else:
		print ('Client connect status : Failure')
	print('Publish data to the broker.')
	c.publish(topic, '{"event_data":{"connected":true}}')    
	print('subscribe topic (%s)' % SUB_TOPIC)

	previous_time = utime.time()
	time_min = 0
	c.subscribe(SUB_TOPIC)

	# Set up Sensors
	light_sensor_obj = LIGHT_Sensor(freq = 1000000, port = 2, csbpin = 22)
	light_sensor_data = light_sensor_obj.get_light_sensor_data()
	print ("Light sensor data = %d" % light_sensor_data)

	sensor_previous_time = utime.time()

	while True:
		if False:
			#print ('Waiting for subscribe message')			
			# blocking wait for message
			c.wait_msg()
		else:
			# non blocking wait for message
			#print ('Waiting for subscribe message Non-blocking')
			c.check_msg()
			utime.sleep_ms(10)	# 10ms for cpu process.
		# If button 0 is pressed, drop to REPL
		if repl_button.value() == 0:
			print("Dropping to REPL now")
			sys.exit()			
		current_time = utime.time()
		sensor_current_time = utime.time()
		#if (current_time - previous_time) > SAMPLING_TIME:
		if (current_time - previous_time) > 60:  # fix the time to 1 min
			time_min += 1
			print ("Time (minutes) = ", time_min * SAMPLING_TIME / 60)
			previous_time = current_time
			obj['event_data']['heartbeat'] = 'true'
			obj['event_data']['lightsensor'] = light_sensor_data 
			print ("Publish sensor data.")
			print (obj)
			c.publish(topic, json.dumps(obj))    
		if (sensor_current_time - sensor_previous_time) > SAMPLING_LIGHT_TIME:
			light_sensor_data = light_sensor_obj.get_light_sensor_data()
			print ("Light sensor data = %d" % light_sensor_data)
			sensor_previous_time = sensor_current_time

	print ('Client disconnect')			
	c.disconnect()

# Module name
print ("Python name : %s." % __name__)

# Pin definitions
repl_button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
blueled = machine.Pin(5, machine.Pin.OUT)


if __name__ == "__main__":
	main()

# Wait for button 0 to be pressed, and then exit
while True:
    # If button 0 is pressed, drop to REPL
    if repl_button.value() == 0:
        print("Dropping to REPL now")
        sys.exit()


    # Do nothing
    utime.sleep_ms(10)
