import serial
import os
import re
import time 
import datetime
import csv
from time import sleep
import paho.mqtt.client as mqttClient

def config(phone):

	n=0
	phone.write(b'ATE\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()

	n=0
	phone.write(b'AT+CGDCONT= 1, "IP", "nbiot"\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
	n=0
	phone.write(b'AT+COPS=0\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
	phone.write(b'AT+CFUN=1,1\r\n')

def get_ip(phone):
	new_ip = "NOIP"
	phone.write(b'AT+CGPADDR=1\r\n')
	n=0
	while n < 2:
		ip=(phone.readline()).decode('utf-8')
		print(ip)
		n=n+1

	for i in ip:
		if ',' in ip:
			l = list(re.finditer(',', ip))
			new_ip = ip[l[0].span()[1]:]
	return new_ip.rstrip()
			
def info(phone):

	n=0
	phone.write(b'ATE\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()

	
	n=0
	phone.write(b'AT+CREG?\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
	n=0
	phone.write(b'AT+CGDCONT?\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
	get_ip(phone)
	
def RSXX(phone, fname="RSRX_simcom.txt"):
	z = 0
	n = 0
	while z < 200:
		phone.write(b'AT+CPSI?\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			n = n + 1
		print(result.rstrip())
		text_file = open(fname,"a")
		text_file.write(result)
		text_file.flush()
		text_file.close()
		time.sleep(2)
		n = 0
		z = z + 1
		phone.reset_input_buffer()
def get_signal(phone):
	signal = "NOSIGNAL"
	phone.write(b'AT+CSQ\r\n')
	time.sleep(2)
	csq=[]
	n = 0
	#try:
	while n < 10:
		csq.append((phone.readline()).decode('utf-8'))
		if csq[n] == '':
			break
		n=n+1
	phone.reset_input_buffer()
	nok = 1
	for csq_list in csq:
		if '+CSQ:' in csq_list:
			nok = 0
			l = list(re.finditer('CSQ:', csq_list))
			new_csq_list = csq_list[l[0].span()[1]+1:]
			m = list(re.finditer('\n', new_csq_list))
			signal = new_csq_list[:(m[0].span()[0])-1]
			print(signal)
	if nok == 1:
		print("CSQ NOK")
	return signal
	
def get_gps(phone, on):
	position = "NOGPS"
	n=0
	if on == 0:
		phone.write(b'AT+CLTS=0\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()
	
		n=0
		phone.write(b'AT+CGNSPWR=1\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()

	phone.write(b'AT+CGNSINF\r\n')
	time.sleep(2)
	n = 0
	gpslist = []
	try:
		while n < 5:
			gpslist.append((phone.readline()).decode('utf-8'))
			n=n+1
		phone.reset_input_buffer()

	except OSError:
		print("GPS ERROR")
		
	except IOError:
		print("GPS IO ERROR")
		
	else:
		nok = 1
		for gps_list in gpslist:
			if '+CGNSINF:' in gps_list:
				if ',,,,,,,,,,' in gps_list:
					break
				else:
					nok = 0
					position = gps_list.rstrip()
		if nok == 1:
			print("GPS NOK")
	phone.reset_input_buffer()
	return position
		
def get_now():
	date_now = datetime.datetime.now()
	now = str(date_now) + "\n"
	return now

def drive(phone, sample, interval, choose, fname="log_simcom.txt"): 

	x = 0 
	n=0
	time.sleep(1)
	phone.reset_input_buffer()
	while x < int(sample):
		print('***** GETTING SIGNAL SAMPLE: %d' % (n))
		csq = get_signal(phone)
		print('##### END SIGNAL SAMPLE: %d \n' % (n))
		print('***** STARTING GPS SAMPLE: %d' % (n))
		gps = get_gps(phone)
		print('##### END GPS SAMPLE: %d \n' % (n))
		now = get_now()
		print("SAVING: csq = %s, gps = %s, time = %s" %(csq, gps, now))
		
		text_file = open(fname,"a")
		text_file.write(str(csq) + " " + str(gps) + " " + str(now) + " ")
		text_file.close()
		time.sleep(interval)
		x = x + 1
		n = n + 1
		if int(choose) == 4:
			x = 0

def send_ping(phone, pings, ping_tout, on):
	time.sleep(1)
	n=0	
	phone.write(b'AT+CIPPING="www.google.cn",%d,8,%d,64\r\n' % (pings, ping_tout))

	while n < pings+1:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	return result.rstrip()
		
def ping(phone, p_host, pings, ping_tout):
	z=0
	n=0
	print("SENDING " + str(z) + " PINGS")
	phone.write(b'AT+CGATT?\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
	n=0	
	phone.write(b'AT+CSTT="nbiot"\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1		
	phone.reset_input_buffer()
	
	n=0	
	phone.write(b'AT+CIICR\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
	n=0
	phone.write(b'AT+CIFSR\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
	result = send_ping(phone, pings, ping_tout, 1)	
	phone.reset_input_buffer()
	return result.rstrip()
	
def sig_reg_ping(phone, p_host, interval, ping_tout, fname="log_sig_reg_ping_simcom.txt"):
	n = 0
	on = 0
	pings = 1
	while n < 1:
		now = get_now()
		print('***** GETTING CSQ SAMPLE: %d' % (z))
		csq = get_signal(phone)
		print('##### END SIGNAL SAMPLE: %d \n' % (z))
		print('***** GETTING GPS SAMPLE: %d' % (z))
		gps = get_gps(phone, z)
		print('##### END GPS SAMPLE: %d \n' % (z))
		ip = get_ip(phone)
		print("\n")
		if on == 0:
			ping_out = ping(phone, p_host, pings, ping_tout)
		else:
			ping_out = send_ping(phone, 1, ping_tout, 1)
			
		print("PIN_OUT = " + str(ping_out))
		log_str = "%s; %s; %s; %s; %s" % (csq, ip, ping_out, gps, now)
		text_file = open(fname,"a")
		text_file.write(log_str)
		text_file.flush()
		text_file.close()
		print(log_str)
		on = 1
		z = z + 1
		time.sleep(interval)
		return csq, ip, ping_out, gps, now
	
def on_connect(client, userdata, flags, rc):
 
	if rc == 0:
 
		print("Connected to broker")
 
		global Connected                #Use global variable
		Connected = True                #Signal connection 
 
	else:
 
		print("Connection failed")
	return Connected

def on_message(client, obj, msg):
	print(msg.payload.decode())	
	
def mqtt(phone): 
	Connected = False   #global variable for the state of the connection
 
	broker_address= "m16.cloudmqtt.com"
	port = 18848
	user = "hiazdzmd"
	password = "iHEXfY2epNNc"
 
	client = mqttClient.Client("Python")               #create new instance
	client.username_pw_set(user, password=password)    #set username and password
	client.on_connect= on_connect                      #attach function to callback
	Connected = on_connect
	client.connect(broker_address, port=port)          #connect to broker
 
	client.loop_start()        #start the loop
 
	while Connected != True:    #Wait for connection
		print("CONNECTED = " + str(Connected))
		time.sleep(0.1)
 
		try:
			while True:
	
				value = input('Enter the message:')
				client.publish("python/test",value)
				teste = client.subscribe("python/test")
		except KeyboardInterrupt:
 
			client.disconnect()
			client.loop_stop()
			exit()