#!/usr/bin/env python
"""
nbiot_test.py

Script para testar conectividade e sinal NBIoT.

"""

import sys
import argparse
import glob
import serial

import serial.tools.list_ports

#global ports

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def id_device(result_gmm):
	if 'BG96' in result_gmm:
		dev="Quectel"
	elif 'WP7702' in result_gmm:
		dev="Sierra"
	elif 'SIMCOM' in result_gmm:
		dev="Simcom"
	elif 'SARA' in result_gmm:
		dev="U-blox"
	elif 'ME910C1' in result_gmm:
		dev="Telit"
	else:
		dev="Not recognized"

	return dev


# Args parser
parser = argparse.ArgumentParser(description=
			"Connect to a NB-IoT serial port or USB" \
			"To execute connectivity signal and connectivity tests",
			formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-port", action="store", default="none", dest = "port",
					help="Modem serial port. No default port.")
parser.add_argument("-device", action="store", default="Unknown", dest = "device",
					help='Modem brand. If the script is not able to find a device, it will show "unknown" as result'
					"Supported brands: Quectel, Sierra, Simcom, u-blox")
parser.add_argument("-interval", action="store", default="5", dest = "interval",
					help="Interval between tests. Default: 5 seconds")
parser.add_argument("-ping_tout", action="store", default="10", dest = "ping_tout",
					help="ping timeout. Default: 10 seconds")
parser.add_argument("-outfile", action="store", default="log_nbiot.txt", dest = "outfile",
					help="Output filename.")
parser.add_argument("-host", action="store", default="8.8.8.8", dest = "p_host",
					help="Host to receive the ping. Default: 8.8.8.8 (google.com)")
args = parser.parse_args()

port = args.port
device = args.device
interval = int(args.interval)
ping_tout = int(args.ping_tout)
outfile = args.outfile
p_host = args.p_host

try:
	if port == "none":
		ports = serial_ports()
		while device == "Unknown": 
			for port in ports:
				print("Verificando porta %s" % port)
				try:
					test = serial.Serial(port, baudrate=115200, timeout=1, write_timeout=1)
					result=(test.read(100)).decode('utf-8')
					print(result)
				except KeyboardInterrupt:
					exit()
				except:
					continue
				try:
					test.write(b"AT+GMM\r\n")
				except:
					continue
				try:
					result=(test.read(100)).decode('utf-8')
					print("Resultado:" + str(result))
					if 'OK' in result:
						break
				except:
					continue
			device = id_device(result)
			if device == "Not recognized":
				print("Not recognized: %s" % result)
				exit()
	else:
		while device == "Unknown": 
			print("Verificando porta %s" % port)
			try:
				test = serial.Serial(port, baudrate=115200, timeout=1, write_timeout=1)
				result=(test.read(100)).decode('utf-8')
				print(result)
			except KeyboardInterrupt:
				exit()
			except:
				continue
			try:
				test.write(b"AT+GMM\r\n")
			except:
				print("Erro na escrita. Abortando")
				exit()

			try:
				result=(test.read(100)).decode('utf-8')
				print("Resultado:" + result)
			except:
				continue
			device = id_device(result)
			if device == "Not recognized":
				print("Not recognized: %s" % result)
				exit()			
	
	print("Trabalhando com modem %s" % (device))
	print("Intervalo entre medidas: %d, host para ping: %s, ping_timeout: %d, arquivo de saida: %s" %(interval, p_host, ping_tout, outfile))
	if device == 'Sierra':
		from sierra2 import *
	if device == 'Quectel':
		from quectel import *
	if device == 'Simcom':
		from simcom import *
	if device == 'U-blox':
		from ublox import *
	if device == 'Telit':
		from telit import *
	test.close()
	while True:
		print("1- Config device for TIM NB-IoT")
		print("2- Show system config")
		print("3- Drive test")
		print("4- Drive test with infinity samples")
		print("5- Ping test")
		print("6- Publish MQTT message")
		print("7- Signal, Registration, Ping continuo")
		print("8- Socket UDP test")
		print("9- RSRX test")
		print("0- Exit")
		choose = input("Choose one of the options: ")
		if int(choose) == 0:
			exit()
		phone = serial.Serial(port, baudrate=115200, timeout=3.0, write_timeout=1)
		phone.write(b'ATE\r\n')
		result=(phone.read(100)).decode('utf-8')
		if int(choose) == 1:
			config(phone);
		if int(choose) == 2:
			info(phone);
		if int(choose) == 3:
			sample = input("How many samples to take? ")
			print("Vai coletar %d amostras" % (int(sample)))
			drive(phone, sample, interval, choose, outfile);
		if int(choose) == 4:
			drive(phone,1, interval, choose, outfile);
		if int(choose) == 5:
			n = input("How many pings to make? ")
			ping_tout = input("Timeout (0-255 seg)? ")
			ping(phone, p_host, int(n), int(ping_tout), outfile);
		if int(choose) == 6:
			mqtt(phone)
		if int(choose) == 7:
			sig_reg_ping(phone, p_host, interval, int(ping_tout), outfile)
		if int(choose) == 8:
			UDP(phone)
		if int(choose) == 9:
			RSXX(phone)
		phone.close()
except KeyboardInterrupt:
	phone.close()
	pass


