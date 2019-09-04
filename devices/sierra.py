import serial
import os
import time 
import datetime
import csv
from time import sleep
import re
import subprocess
import sys
import json
import paramiko
import requests
from geopy.distance import vincenty

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
	phone.write(b'AT!SELRAT=06\r\n')
	while n < 2:
		result=(phone.readline()).decode('utf-8')
		print(result)
		n=n+1
	phone.reset_input_buffer()

	n=0
	phone.write(b'AT!BAND=00\r\n')
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
	phone.reset_input_buffer()
	phone.write(b'AT+CGPADDR=1\r\n')
	n=0
	while n < 2:
		ip=(phone.readline()).decode('utf-8')
		print(ip.rstrip())
		n=n+1
	
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
	
	phone.write(b'AT!GSTATUS?\r\n')
	n = 0
	status= []
	print("#### PRINTING STATUS ####")
	while n < 18:
		status=(phone.readline()).decode('utf-8')
		print(status.rstrip())
		if status[n] == '':
			break
		n=n+1
	phone.reset_input_buffer()
		
def RSXX(phone, fname = "RSRX_sierra.txt"):
	
	ON = "OFFLINE"
	TECH = "Unknown"
	new_RSSI = "Unknown"
	new_RSRP = "Unknown"
	RSSI_RSRP = "Unknown"
	phone.write(b'AT!GSTATUS?\r\n')
	n = 0
	status= []

	while n < 18:
		status=(phone.readline()).decode('utf-8')

		if 'ONLINE' in status:
			ON = "ONLINE"
		if '1.4 MHz' in status:
			TECH = "NBIOT"
		if 'RxM' in status:

			l = list(re.finditer('RxM', status))
			RSSI = status[l[0].span()[1]+7:l[0].span()[1]+12]
			l = list(re.finditer('dBm', status))
			RSRP = status[l[0].span()[1]+3:l[0].span()[1]+8]
			RSSI_RSRP = RSSI + "  " + RSRP
			new_RSSI = "".join(RSSI.split())
			new_RSRP = "".join(RSRP.split())	
		n=n+1
	print (ON + " " + TECH + " " + RSSI_RSRP)
	text_file = open(fname,"a")
	text_file.write(ON + " " + TECH + " " + RSSI_RSRP + "\n")
	text_file.flush()
	text_file.close()
	phone.reset_input_buffer()
	
	

	return new_RSSI, new_RSRP


def get_signal(phone):
	signal = "NOSIGNAL"
	phone.write(b'AT+CSQ\r\n')
	time.sleep(2)
	csq=[]
	n = 0
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
	
def distance(point_lat,point_lon):
	
	core_coords_1 = (-15.056433333333334, -48.999111111111111)
	core_coords_2 = (point_lat, point_lon)
	dist = vincenty(core_coords_1, core_coords_2).km
	print(dist)
	return dist

def get_gps(phone):
	phone.reset_input_buffer()
	position = "NOGPS"
	Dlat = "NOLAT"
	Dlon = "NOLON"

	phone.write(b'AT!GPSLOC?\r\n')
	time.sleep(2)
	n = 0
	gpslist = []
	try:
		while n < 5:
			gpslist.append((phone.readline()).decode('utf-8'))
			n=n+1
		
	except OSError:
		print("GPS ERROR")
		
	except IOError:
		print("GPS IO ERROR")
		
	else:
		nok = 1
		for gps_list in gpslist:
			if 'Lat:' in gps_list:
				nok = 0
				l = list(re.finditer('Lat: ', gps_list))
				m = list(re.finditer('Deg', gps_list))
				lat_deg = gps_list[l[0].span()[1]:m[0].span()[1]-3]
				
				l = list(re.finditer('Deg', gps_list))
				m = list(re.finditer('Min', gps_list))
				lat_min = gps_list[l[0].span()[1]+1:m[0].span()[1]-4]
				
				l = list(re.finditer('Min', gps_list))
				m = list(re.finditer('Sec', gps_list))
				lat_sec = gps_list[l[0].span()[1]+1:m[0].span()[1]-4]
				
				Dlat = (-1)*((float(lat_deg)/1) + (float(lat_min)/60) + (float(lat_sec)/3600))
				
			if 'Lon:' in gps_list:
				l = list(re.finditer('Lon: ', gps_list))
				m = list(re.finditer('Deg', gps_list))
				lon_deg = gps_list[l[0].span()[1]:m[0].span()[1]-3]
				
				l = list(re.finditer('Deg', gps_list))
				m = list(re.finditer('Min', gps_list))
				lon_min = gps_list[l[0].span()[1]+1:m[0].span()[1]-4]
				
				l = list(re.finditer('Min', gps_list))
				m = list(re.finditer('Sec', gps_list))
				lon_sec = gps_list[l[0].span()[1]+1:m[0].span()[1]-4]
				
				Dlon = (-1)*((float(lon_deg)/1) + (float(lon_min)/60) + (float(lon_sec)/3600))
				
				position = str(Dlat) + "," + str(Dlon)
				print(position)
		if nok == 1:
			print("GPS NOK")
	
	return position, Dlat,Dlon

def get_now():
	date_now = datetime.datetime.now()
	now = str(date_now) + "\n"
	return now.rstrip()

def drive(phone, sample, interval, choose, fname="log_sierra.txt"): 
     
	x = 0
	n = 0
	time.sleep(1)
	phone.reset_input_buffer()
	while x < int(sample):
		print('***** GETTING SIGNAL SAMPLE: %d' % (n))
		csq = RSXX(phone)
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
		if int(choose) == 4:
			x = 0
		n=n+1
	time.sleep(interval)
		
		

def send_ping(n, p_host, ping_tout, on):
	print("CONNECTING...")
	ping = "NOPING"
	x = 0
	HOST="root@192.168.2.2"
	if on == 0:
		COMMAND = "/legato/systems/current/bin/cm data connect"
		ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
								shell=False,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
		result = ssh.stdout.readlines()
	ssh = subprocess.Popen(["ssh", "%s" % HOST, "ping 8.8.8.8 -c " + str(n) + " -W " + str(ping_tout)],
							shell=False,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)
	result = ssh.stdout.readlines()
	
	if result == []:
		error = ssh.stderr.readlines()
		print("\nERROR NO IP YET\n")
	else:
		for i in result:
			new_i = i.decode('utf-8')
			if 'seq' in new_i:
				l = list(re.finditer('time=', new_i))
				n_ping = new_i[l[0].span()[1]:].rstrip()
				m = list(re.finditer(' ', n_ping))
				ping = n_ping[:(m[0].span()[0])-1]
	return on, ping
	
def ping(phone, p_host, n, ping_tout, outfile="ping_sierra"):
	ping = send_ping(n, p_host, ping_tout, 0)

def mqtt(ping, RSSI, RSRP, lat, lon, now):
	HOST="root@192.168.2.2"
	print("lat = " + str(lat))
	if lat == 'NOLAT':
		lat = -23
		lon = -42
	msg_pub_latency = {
		"variable": "latency",
		"value": ping,
		"unit": "ms",
		"time": now,
		"location": {
			"lat": lat,
			"lng": lon
		}
	}
	platform = 'iota'
	if platform == 'tago':
		COMMAND = "curl -H \"Content-Type: application/json\" -H \"Device-Token: dc003b40-7579-438a-b7d3-ae8a753c635b\" -X POST -d '" + json.dumps(msg_pub_latency) + "' https://api.tago.io/data"
		print(COMMAND)
		ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
								shell=False,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
		result = ssh.stdout.readlines()
		COMMAND = "curl -H \"Content-Type: application/json\" -H \"Device-Token: dc003b40-7579-438a-b7d3-ae8a753c635b\" -X POST -d \'{\"variable\":\"rssi\",\"value\":" + str(RSSI) + ",\"unit\":\"dBm\"}\' https://api.tago.io/data"
		print(COMMAND)
		ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
								shell=False,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
		result = ssh.stdout.readlines()
		COMMAND = "curl -H \"Content-Type: application/json\" -H \"Device-Token: dc003b40-7579-438a-b7d3-ae8a753c635b\" -X POST -d \'{\"variable\":\"rsrp\",\"value\":" + str(RSRP) + ",\"unit\":\"dBm\"}\' https://api.tago.io/data"
		print(COMMAND)
		ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
								shell=False,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
		result = ssh.stdout.readlines()
	else:
		hrAtual = str(time.time())

		url = "https://iotabusinesslab.servicebus.windows.net/datacollectoroutbox/publishers/e4456206-f634-49b7-b6dd-96ab81ec3111/messages"

		payload = "{\"bu\": \"default-unit\",\"e\": [{\"n\":\"sierra/4423/0/1862371\",\"u\": \"default-unit\",\"v\": " + str(RSRP) + ",\"sv\": null,\"bv\": null,\"t\":"+hrAtual+"}]}"
		headers = {
			'Content-Type': "application/json",
			'Authorization': "SharedAccessSignature sr=https%3a%2f%2fiotabusinesslab.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2fe4456206-f634-49b7-b6dd-96ab81ec3111%2fmessages&sig=KaDn0TapHrl6qBds%2foJ1F0F6SeX1V1ILk6ek5rbEzFo%3d&se=4705758071&skn=SendAccessPolicy",
			'PayloadType': "application/senml+json",
			'DataCollectorId': "e4456206-f634-49b7-b6dd-96ab81ec3111",
			'cache-control': "no-cache",
			'Postman-Token': "31ed566b-be2d-4ea8-bdb4-21c616f3c4a2"
		}

		response = requests.request("POST", url, data=payload, headers=headers)
	
		print(response.status_code)
	
		hrAtual = str(time.time())

		url = "https://iotabusinesslab.servicebus.windows.net/datacollectoroutbox/publishers/e4456206-f634-49b7-b6dd-96ab81ec3111/messages"

		payload = "{\"bu\": \"default-unit\",\"e\": [{\"n\":\"sierra/4423/0/3336\",\"u\": \"default-unit\",\"v\": null,\"sv\": \"" + str(lat) + ";" + str(lon) + "\",\"bv\": null,\"t\":"+hrAtual+"}]}"
		headers = {
			'Content-Type': "application/json",
			'Authorization': "SharedAccessSignature sr=https%3a%2f%2fiotabusinesslab.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2fe4456206-f634-49b7-b6dd-96ab81ec3111%2fmessages&sig=KaDn0TapHrl6qBds%2foJ1F0F6SeX1V1ILk6ek5rbEzFo%3d&se=4705758071&skn=SendAccessPolicy",
			'PayloadType': "application/senml+json",
			'DataCollectorId': "e4456206-f634-49b7-b6dd-96ab81ec3111",
			'cache-control': "no-cache",
			'Postman-Token': "31ed566b-be2d-4ea8-bdb4-21c616f3c4a2"
		}

		response = requests.request("POST", url, data=payload, headers=headers)
	
		print(response.status_code)
	

def sig_reg_ping(phone, p_host, interval = 5, ping_tout = 5, fname = "log_sig_reg_ping_sierra.txt"):
	n = 0
	on = 0
	z = 0
	dist = "NODISTANCE"
	while n < 1:
		now = get_now()
		print('***** GETTING CSQ SAMPLE: %d' % (z))
		RSSI, RSRP = RSXX(phone)
		print('##### END SIGNAL SAMPLE: %d \n' % (z))
		print('***** GETTING GPS SAMPLE: %d' % (z))
		gps, lat, lon = get_gps(phone)
		print('##### END GPS SAMPLE: %d \n' % (z))
		ip = get_ip(phone)
		print("\n")
		if on == 1:
			on, ping = send_ping(1, p_host, ping_tout, 1)
		else:
			if ip != "NOIP":
				on, ping = send_ping(1, p_host, ping_tout, 0)
				on = 1
		mqtt(ping, RSSI, RSRP, lat, lon, now)
		print(ping)
		if gps == "NOGPS":
			print("CANT CALCULATE THE DISTANCE")
		else:
			dist = distance(lat,lon)
		log_str = "%s, %s; %s; %s; %s; %s; %s \n" % (RSSI, RSRP, ip, ping, gps, dist, now)
		text_file = open(fname,"a")
		text_file.write(log_str)
		text_file.flush()
		text_file.close()
		print(log_str)
		z = z + 1
		time.sleep(interval)