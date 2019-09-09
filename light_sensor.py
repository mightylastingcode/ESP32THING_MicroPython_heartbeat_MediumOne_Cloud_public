'''
	Project: SPI Light Sensor 

	SPI Port:
	 Port 1: fixed hardware spi port location (id=1).
	 Port 2: fixed hardware spi port location (id=2).
	 None: Software spi bit bang driver (any pin defined by users)

'''

import machine
import sys
import utime

from machine import Pin, SPI


class LIGHT_Sensor:
	'''
	Represents a light sensor
	'''
	def __init__(self,freq,port,csbpin,sckpin=18,mosipin=23,misopin=19):
		print ("CSB pin = %d" % csbpin)
		self.csb  = machine.Pin(csbpin, machine.Pin.OUT)
		self.csb.value(1)   # disable

		# construct an SPI bus on the given pins
		# polarity is the idle state of SCK
		# phase=0 means sample on the first edge of SCK, phase=1 means the second
		# 1M, 10M, 20M ok (1M is more stable)
		if (port == 1):
			print("Use hardware spi port 1: sck 14, mosi 13, miso 12")
			self.spi = SPI(1, baudrate=freq, polarity=1, phase=1, bits=8, firstbit=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
		elif (port == 2):
			print("Use hardware spi port 2: sck 18, mosi 23, miso 19")
			self.spi = SPI(2, baudrate=freq, polarity=1, phase=1, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
		else:
			print("Use software spi port : sck %d, mosi %d, miso %d" % (sckpin,mosipin,misopin))
			self.spi = SPI(baudrate=freq, polarity=1, phase=1, sck=Pin(sckpin), mosi=Pin(mosipin), miso=Pin(misopin))	# software spi

	def get_light_sensor_data(self):
		#print ("Read 2 bytes from SPI light sensor.")
		self.csb.value(0)   # enable
		buf = self.spi.read(2)            # read 2 bytes on MISO 
		self.csb.value(1)   # disable

		print ("Raw Data from the sensor:")
		for x in buf:
			print ("%x" % x)
		#print ("MSB data")
		data_msb = (buf[0] & 0x1f) <<3
		#print ("%x" % data_msb)  

		#print ("LSB data")
		data_lsb = (buf[1] & 0xe0) >>5
		#print ("%x" % data_lsb)  

		#print ("8 bit sensor data:")
		data = data_msb | data_lsb
		#print ("%x" % data)  
		return data

'''
# place this section in the main.py.

import machine
import sys
import utime
from machine import Pin, I2C

from light_sensor import LIGHT_Sensor

# Pin definitions
repl_button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

#light_sensor_obj = LIGHT_Sensor(freq = 1000000, port = 1, csbpin = 15)
#light_sensor_obj = LIGHT_Sensor(freq = 1000000, port = 2, csbpin = 15)
light_sensor_obj = LIGHT_Sensor(freq = 200000, port = 3, csbpin = 15, sckpin=0,mosipin=2,misopin=4)
light_sensor_data = light_sensor_obj.get_light_sensor_data()
print ("Light sensor data = %d" % light_sensor_data)
utime.sleep_ms(100)
# Wait for button 0 to be pressed, and then exit
while True:
    if repl_button.value() == 0:
        print("Dropping to REPL now")
        sys.exit()
    else:
		light_sensor_data = light_sensor_obj.get_light_sensor_data()
		print ("Light sensor data = %d" % light_sensor_data)
		utime.sleep_ms(100)

'''

