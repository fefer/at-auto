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
	phone.write(b'ATE1\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	time.sleep(2)

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

"""def RSXX(phone):
	result = []
	z = 0
	n=0
	phone.write(b'AT+CESQ\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		n=n+1
	RSXX = result.rstrip()
	phone.reset_input_buffer()
	z = z + 1
	print(RSXX)
	return RSXX"""
	
def RSXX(phone):
	signal = "NOSIGNAL"
	phone.write(b'AT+CESQ\r\n')
	time.sleep(2)
	cesq=[]
	n = 0
	while n < 10:
		cesq.append((phone.readline()).decode('utf-8'))
		if cesq[n] == '':
			break
		n=n+1
	phone.reset_input_buffer()
	nok = 1
	for cesq_list in cesq:
		if '+CESQ:' in cesq_list:
			nok = 0
			l = list(re.finditer('CESQ:', cesq_list))
			signal = cesq_list[l[0].span()[1]+1:]
			print(signal)
	if nok == 1:
		print("CSQ NOK")		
	return signal.rstrip()

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
	nok = 1
	n=0
	gps_list = []
	phone.write(b'AT$GPSP=1\r\n')
	phone.reset_input_buffer()
	
	time.sleep(2)
	gpslist = []
	phone.write(b'AT$GPSACP\r\n')	
	while n < 4:
		gpslist.append((phone.readline()).decode('utf-8'))
		n=n+1
	phone.reset_input_buffer()
	for gps_list in gpslist:
		if 'W' in gps_list:
			print(gpslist[3])
			nok = 0
			l = list(re.finditer('W', gps_list))
			position = gps_list[:l[0].span()[1]]
	if nok == 1:
		print("GPS NOK")			

	return position

def get_now():
	date_now = datetime.datetime.now()
	now = str(date_now) + "\n"
	return now

def drive(phone, sample, interval, choose, fname="log_telit.txt"):     

	x = 0 
	n = 0
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


def send_ping(phone, pings, p_host, ping_tout, on):
	ping_result = "NOPING"
	n=0
	pinglist=[]
	print("PINGS = " + str(pings))
	phone.write(b'AT#PING=8.8.8.8,%d,64,%d\r\n' % (pings, ping_tout))
	print('AT#PING=8.8.8.8,%d,64,%d\r\n' % (pings, ping_tout))
	while n < pings+3:
		pinglist.append((phone.readline()).decode('utf-8'))
		n=n+1
	#print(pinglist)
	for i in pinglist:
		if 'PING' in i:
			ping_result = i
	return ping_result.rstrip()

def get_ping(phone, p_host, n, ping_tout):
	phone.write(b'AT#SGACT=1,1\r\n')
	phone.reset_input_buffer()
	
	ping = send_ping(phone, n, p_host, ping_tout, 0)
	return ping
 
def mqtt(phone):
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
	phone.write(b'AT+UMQTT=4,"daniel","dc003b40-7579-438a-b7d3-ae8a753c635b"\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
		
	n=0
	phone.write(b'AT+UMQTT=10,3600\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
		
	n=0
	phone.write(b'AT+UMQTTWTOPIC=1,1,"tago/data/post"\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
		
	n=0
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
	phone.reset_input_buffer()
		
	n=0
	phone.write(b'AT+UMQTTC=1\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()
	
	n=0
	phone.write(b'AT+UMQTTC=2,1,1,"tago/data/post","{"variable":"rssi","value":90,"unit":"dB"}"\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1	
	phone.reset_input_buffer()
	
def sig_reg_ping(phone, p_host, interval, ping_tout, fname="log_sig_reg_ping_telit.txt"):
	n = 0
	z = 0
	while n < 1:
		now = get_now()
		print('***** GETTING CSQ SAMPLE: %d' % (z))
		csq = RSXX(phone)
		print('##### END SIGNAL SAMPLE: %d \n' % (z))
		print('***** GETTING GPS SAMPLE: %d' % (z))
		gps = get_gps(phone)
		print('##### END GPS SAMPLE: %d \n' % (z))
		ip = get_ip(phone)
		print("\n")
		ping = get_ping(phone, p_host, 1, ping_tout)	
		log_str = "%s; %s; %s; %s; %s" % (csq, ip, ping, gps, now)
		text_file = open(fname,"a")
		text_file.write(log_str)
		text_file.flush()
		text_file.close()
		print(log_str)
		z = z + 1
		time.sleep(interval)