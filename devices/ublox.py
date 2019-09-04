import serial
import os
import time 
import datetime
import csv
from time import sleep
import re
import subprocess
import sys


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
			
def get_ip(phone):
	new_ip = "NOIP"
	phone.write(b'AT+CGPADDR=1\r\n')
	n=0
	while n < 2:
		ip=(phone.readline()).decode('utf-8')
		print(ip)
		n=n+1
	phone.reset_input_buffer()
	for i in ip:
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

def RSXX(phone):
	RSXX = "NOSIGNAL"
	n=0
	phone.write(b'AT+CESQ\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		if ":" in result:
			l = list(re.finditer(':', result))
			comma =  result[l[0].span()[1]+1:]
			RSXX = [x.strip() for x in comma.split(',')]
		n=n+1

	
	
	phone.reset_input_buffer()

		
	return RSXX[5]
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
	
def get_gps(phone):
	position = "NOGPS"
	phone.write(b'AT+CGNSINF\r\n')
	time.sleep(2)
	n = 0
	gpslist = []
	while n < 10:
		gpslist.append((phone.readline()).decode('utf-8'))
		if gpslist[n] == '':
			break
		n=n+1
	phone.reset_input_buffer()
		
	nok = 1
	for gps_list in gpslist:
		if 'Lob' in gps_list:
			nok = 0
			l = list(re.finditer(b'\n', gps_list))
			n_gps = gps_list[:gps_list[l[0].span()[1]]]
			m =  list(re.finditer(b'Lon', gps_list))
			pos = gps_list[l[0].span()[1]+1:]
			position = pos.decode('utf-8')
	if nok == 1:
		print("GPS NOK")			
	return position

def get_now():
	date_now = datetime.datetime.now()
	now = str(date_now) + "\n"
	return now

def drive(phone, sample, interval, choose, fname="log_ublox.txt"): 
	x = 0 
	n = 0
	choose = 4
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

def get_ping(phone, p_host, n, ping_tout):
	print("Operation not allowed")
	ping = "NOPING"
	return ping
 

 
def mqtt(phone, param, msg, on, interval):
	if on == 0:
		n=0
		phone.write(b'AT+UMQTT=1,1883\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()
	
		n=0
		phone.write(b'AT+UMQTT=2,"mqtt.tago.io"\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()
		
		n=0
		phone.write(b'AT+UMQTT=3,"18.233.119.83",1883\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()
		
		n=0
		phone.write(b'AT+UMQTT=4,"daniel","a5f5e561-60ec-4fa5-bc40-a76a0b8725fe"\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()
		
		"""n=0
		phone.write(b'AT+UMQTT=10,3600\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()"""
		
		n=0
		phone.write(b'AT+UMQTTWTOPIC=1,1,"tago/data/post"\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()

		"""n=0
		phone.write(b'AT+UMQTTWMSG="{"variable":"rssi","value":90,"unit":"dB"}"\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()
		
		n=0
		phone.write(b'AT+UMQTTNV=2\r\n')
		while n < 2:
			result=(phone.readline()).decode('utf-8')
			print(result)
			n=n+1
		phone.reset_input_buffer()"""
		#response = "NOTHING"
		#while "NOTHING" in response:
		
	n=0
	phone.write(b'AT+UMQTTC=1\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
		#	n=0
		#	if "1,0" in result:
		#		print ("BREAKING")
		#		break
		#	else:
		#		time.sleep(1)
		
	msg = -141 + int(msg)
		
	phone.write(b'AT+UMQTTC=2,1,1,"tago/data/post","{"variable":"' + param.encode('ascii') + b'","value":' + str(msg).encode('ascii') + b',"unit":"dB"}"\r\n')
	print('AT+UMQTTC=2,1,1,"tago/data/post","{"variable":"' + str(param) + '","value":' + str(msg) + ',"unit":"dB"}"\r\n')
	print("PUBLISHING: " + str(param) + " " + str(msg))
	n=0
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1	
	phone.reset_input_buffer()
	time.sleep(interval)
	n=0
	phone.write(b'AT+UMQTTC=0\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
def sig_reg_ping(phone, p_host, interval, ping_tout, fname="log_sig_reg_ping_ublox.txt"):
	n = 0
	on = 0
	z = 0
	while n < 1:
		now = get_now()
		print('***** GETTING CSQ SAMPLE: %d' % (z))
		csq = RSXX(phone)
		if z > 1:
			on = 1
		mqtt(phone, "rsrp", csq, on, interval)
		print('##### END SIGNAL SAMPLE: %d \n' % (z))
		print('***** GETTING GPS SAMPLE: %d' % (z))
		gps = get_gps(phone)
		print('##### END GPS SAMPLE: %d \n' % (z))
		ip = get_ip(phone)
		print("\n")
		ping = get_ping(1, p_host, ping_tout, 1)	
		log_str = "%s; %s; %s; %s; %s" % (csq, ip, ping, gps, now)
		text_file = open(fname,"a")
		text_file.write(log_str)
		text_file.flush()
		text_file.close()
		print(log_str)
		z = z + 1
		time.sleep(interval)
	
def UDP(phone):

	n=0
	phone.write(b'AT+USOCR=17\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	time.sleep(5)
	n=0
	phone.write(b'AT+USOST=0,"195.34.89.241",7,5,"Hello"\r\n')
	while n < 3:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	n=0
	time.sleep(5)
	phone.write(b'AT+USORF=0,5\r\n')
	while n < 5:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1