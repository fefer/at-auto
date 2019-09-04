import serial
import os
import time 
import datetime
import csv
from time import sleep
import re
import json

PING_TIMEOUT = 10
ECHO_TIMEOUT = 10
MQTT_TIMEOUT = 60
def reset_radio(phone):
	phone.write(b'AT+CFUN=4\r\n') # Desliga Radio
	result=(phone.read(phone.inWaiting())).decode('utf-8')
	print(result)
	time.sleep(5)
	phone.write(b'AT+CFUN=1\r\n') # Liga Radio
	result=(phone.read(phone.inWaiting())).decode('utf-8')
	print(result)

def config(phone):



	phone.write(b'AT+QCFG="nwscanmode",3,1\r\n') # Configura 3 (LTE only), 1 (efeito imediato)
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+QCFG="nwscanmode"\r\n') # Consulta: 3 = LTE only, 1 = GSM only, 0 = Automatic  
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+QCFG="nwscanseq", 030201, 1\r\n') # Configura: 3 = NB; 1 = efeito imediato
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+QCFG="nwscanseq"\r\n') # Consulta: 03 = NB, 02 = M1, 01 = GSM, 00 = auto (M1, NB, GSM)
	result=(phone.read(100)).decode('utf-8')
	print(result)

	phone.write(b'AT+CGDCONT= 1, "IP", "nbiot"\r\n')
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+QCFG="iotopmode", 1, 1\r\n') # Configura para 1 (NB), 1 (efeito imediato)
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+QCFG="iotopmode"\r\n')	# Consulta opmode: 2 = M1 e NB, 1 = NB, 0 = M1
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+QCFG="roamservice",2,1\r\n') # Configura: 2 (roam enable), 1 (efeito imediato)
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+QCFG="roamservice"\r\n')
	result=(phone.read(100)).decode('utf-8')
	print(result)


			
def info(phone):

	phone.write(b'ATE\r\n')
	result=(phone.read(100)).decode('utf-8')
	print(result)

	phone.write(b'AT+CREG=0\r\n')	# Configura para nao mostrar resultados nao solicitados
	phone.write(b'AT+CREG?\r\n')	# Consulta se esta registrado. Resposta: +CREG: <n>,<stat>[,<lac>,<ci>[,<Act>]]
									# stat: 0 = nao registrado, ainda tentando; 1 = registrado home; 2 = nao registrado, mas tentando attach ou buscando operadora
									#	3 = registro recusado; 4 = Desconhecido; 5 = registrado em roaming
									# lac = location area code; ci = cell id; Act = access technology (0=GSM, 8=M1, 9=NB)
	result=(phone.read(100)).decode('utf-8')
	print(result)
	rs = result.split(',') #at+CREG?  +CREG: <n>,<stat>[,<lac>,<ci>[,<Act>]]  OK
	if len(rs) == 2:
		stat = int(rs[1][0])
		if stat == 0:
			print("Nao registrado. Ainda tentando...")
		elif stat == 1:
			print("Registrado rede home!")
		elif stat == 2:
			print("Nao regsitrado. Tentando attach ou outra operadora")
		elif stat == 3:
			print("Registro circuito recusado")
		elif stat == 4:
			print("Desconhecido")
		elif stat == 5:
			print("Registrado em roaming!")
		else:
			print("Situacao de registro nao conhecida")
	elif len(rs) > 2:
		lac = rs[2]
		ci = rs[3]
		Act = int(rs[4][0])
		if Act == 0:
			Act_str = "GSM"
		elif Act == 8:
			Act_str = "CAT-M1"
		elif Act == 9:
			Act_str = "NB-IoT"
		else:
			Act_str = "Unknows Access Technology"
		print("Registrado: LAC = %s, Cell_ID = %s, Act = %d (%s)" % (lac, ci, Act, Act_str))
	
	phone.write(b'AT+CEREG=2\r\n')	# Configura para habilitar unsolicited results
	result=(phone.read(100)).decode('utf-8')
	print(result)
	phone.write(b'AT+CEREG?\r\n')	# Consulta se esta registrado na rede de pacotes. Trabalhando com n=0. Resposta: 
									#	When <n>=0, 1, or 2 and command successful:
									# +CEREG: <n>,<stat>[,[<tac>],[<ci>],[<AcT>[,<cause_type>,<reject_cause>]]]
									# stat: 0 = nao registrado, ainda tentando; 1 = registrado home; 2 = nao registrado, mas tentando attach ou buscando operadora
									#	3 = registro recusado; 4 = Desconhecido; 5 = registrado em roaming
									# tac = tracking area code; ci = cell id; Act = access technology (0=GSM, 8=M1, 9=NB)
									# cause_type = 0 indica que reject_cause contem EMM cause value, 1 indica que reject_cause contem manufacturer-specific cause
									# reject_cause contem a causa da falha no registro
	result=(phone.read(100)).decode('utf-8')
	print(result)
	rs = result.split(',') #at+CEREG?  +CEREG: <n>,<stat>[,[<tac>],[<ci>],[<AcT>[,<cause_type>,<reject_cause>]]]  OK
	if len(rs) == 2:
		stat = int(rs[1][0])
		if stat == 0:
			print("Nao registrado. Ainda tentando...")
		elif stat == 1:
			print("Registrado rede home!")
		elif stat == 2:
			print("Nao regsitrado. Tentando attach ou outra operadora")
		elif stat == 3:
			print("Registro recusado")
		elif stat == 4:
			print("Desconhecido")
		elif stat == 5:
			print("Registrado em roaming!")
		else:
			print("Situacao de registro nao conhecida")
	if len(rs) > 2:
		stat = int(rs[1][0])
		if stat == 0:
			print("Nao registrado. Ainda tentando...")
		elif stat == 1:
			print("Registrado rede home!")
		elif stat == 2:
			print("Nao regsitrado. Tentando attach ou outra operadora")
		elif stat == 3:
			print("Registro recusado")
		elif stat == 4:
			print("Desconhecido")
		elif stat == 5:
			print("Registrado em roaming!")
		else:
			print("Situacao de registro nao conhecida")
		tac = rs[2]
		ci = rs[3]
		desc = rs[4]
		Act = int(rs[5][0])
		if Act == 0:
			Act_str = "GSM"
		elif Act == 8:
			Act_str = "CAT-M1"
		elif Act == 9:
			Act_str = "NB-IoT"
		else:
			Act_str = "Unknows Access Technology"
		if len(rs) > 6:
			cause_type = int(rs[5][0])
			reject_cause = int((rs[6].split())[0])
			print("NAO Registrado: TAC = %s, Cell_ID = %s, Desc = %s, Act = %d (%s), Cause_type = %d, Reject_Cause = %d" % (tac, ci, desc, Act, Act_str, cause_type, reject_cause))
		else:
			print("Registrado: TAC = %s, Cell_ID = %s, Desc = %s, Act = %d (%s)" % (tac, ci, desc, Act, Act_str))
	phone.write(b'AT+CEREG=0\r\n')	# Configura para desabilitar unsolicited results
	
	phone.write(b'AT+CGDCONT?\r\n')
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+CGPADDR=1\r\n')
	result=(phone.read(100)).decode('utf-8')
	print(result)

	phone.write(b'AT+QNWINFO\r\n')
	result=(phone.read(100)).decode('utf-8')
	print(result)

	phone.write(b'AT+QSPN\r\n')
	result=(phone.read(100)).decode('utf-8')
	print(result)
	
	phone.write(b'AT+QCFG="celevel"\r\n')
	result=(phone.read(100)).decode('utf-8')
	print(result)

	
def get_gps(phone):
	"""
	at+qgpsloc?
	+CME ERROR: 516
	at+qgpsloc=2
	+QGPSLOC: 202008.0,-22.98486,-43.35916,2.5,4.0,2,0.00,0.0,0.0,290119,09
	at+qgpsloc?
	+QGPSLOC: 142748.0,2259.0881S,04321.5515W,2.0,-83.0,2,0.00,0.0,0.0,140119,10

	OK

	516 Not fixed now
	+QGPSLOC: <UTC>,<latitude>,<longitude>,<hdop>,<altit
	ude>,<fix>,<cog>,<spkm>,<spkn>,<date>,<nsat>
	"""
	d_err_code = {
		0: "Erro inespecifico de GPS",
		501: "Invalid parameter",
		502: "Operation not supported",
		503: "GNSS subsystem busy",
		504: "Session is ongoing",
		505: "Session not active",
		506: "Operation timeout",
		507: "Function not enabled",
		508: "Time information error",
		509: "XTRA not enabled",
		512: "Validity time is out of range",
		513: "Internal resource error",
		514: "GNSS locked",
		515: "End by E911",
		516: "Not fixed now",
		517: "Geo-fence ID is not existed",
		549: "Unknown error"
	}
	ptout_bkp = phone.timeout
	phone.timeout = 3.0
	position = "NOGPS"
	phone.write(b'AT+QGPS=1\r\n')
	time.sleep(1)
	phone.reset_input_buffer()
	phone.write(b'AT+QGPSLOC=2\r\n')
	time.sleep(2)
	try:
		#gps=(phone.read(100)).decode('utf-8')
		blank = (phone.readline()).decode('utf-8')
		gps=(phone.readline()).decode('utf-8')
		phone.reset_input_buffer()
		print(gps)
	except OSError:
		print("GPS OS Error")
		
	except IOError:
		print("GPS IO Error")
		
	else:
		if '+CME ERROR:' in gps:
			#print("GPS ERROR")
			# +CME ERROR: <errcode>
			errcode = int((gps.split(': '))[1])
			print("GPS ERROR: %d - %s" % (errcode, d_err_code[errcode]))
			gps = "ERROR"
		else:
			if '+QGPSLOC: ' in gps:			
				l = gps.split("+QGPSLOC: ")
				new_gps = l[1]
				m = new_gps.split('\r')
				position = m[0]
				
			else:
				gps = "ERROR"
	phone.timeout = ptout_bkp
	return gps, position

def get_now():
	#print("Getting date & time")
	date_now = datetime.datetime.now()
	now = str(date_now) + "\n"
	return now
	
def get_signal(phone):
	"""
	at+qcsq
	+QCSQ: "CAT-NB1",75,-81,96,-9

	OK
	“CAT-NB1” <lte_rssi> <lte_rsrp> <lte_sinr> <lte_rsrq>
	“CAT-M1” <lte_rssi> <lte_rsrp> <lte_sinr> <lte_rsrq>
	“GSM” <gsm_rssi>
	“NOSERVICE”
	"""
	signal = "NOSIGNAL"
	rssi = 255
	rsrp = 255
	sinr = 255
	rsrq = 255
	phone.write(b'AT+QCSQ\r\n')
	time.sleep(2)
	try:
		#qcsq=(phone.read(100)).decode('utf-8')
		blank = (phone.readline()).decode('utf-8')
		qcsq=(phone.readline()).decode('utf-8')
		phone.reset_input_buffer()
		print(qcsq)
	except OSError:
		print("QCSQ ERROR")
		
	except IOError:
		print("QCSQ IO ERROR")
		
	else:
		if '+QCSQ:' not in qcsq:
			print("QCSQ NOK")
		else:
			qcsq_data = qcsq.split("+QCSQ: ")
			qcsq_values = (qcsq_data[1]).split(",")
			if ('NB1' or 'M1') in qcsq_values[0]:
				rssi = int(qcsq_values[1])
				rsrp = int(qcsq_values[2])
				sinr = int(qcsq_values[3])
				rsrq = int(qcsq_values[4])
				if 'NB1' in qcsq_values[0]:
					l = qcsq.split('NB1",')
				else:
					l = qcsq.split('M1",')
				new_qcsq = l[1]
				m = new_qcsq.split('\r')
				signal = m[0]
			elif 'GSM' in qcsq_values[0]: 
				rssi = int(qcsq_values[1])
				rsrp = 255
				sinr = 255
				rsrq = 255
				l = qcsq.split('GSM",')
				new_qcsq = l[1]
				m = new_qcsq.split('\r')
				signal = m[0]
	
	phone.write(b'AT+QCFG="celevel"\r\n')
	time.sleep(0.4)
	celevel = phone.read(phone.inWaiting()).decode('utf-8')
	print(celevel)
	if 'celevel' in celevel:
		clvl = celevel.split(',')[1][0]
	else:
		clvl = "-1"
	
	return qcsq, signal, clvl, rssi, rsrp, sinr, rsrq

def get_registro(phone):
	d_stat = {
		0: ["Nao registrado. Ainda tentando...", "NOREG_STILLTRY", False],
		1: ["Registrado rede home!", "REGHOME", True],
		2: ["Nao regsitrado. Tentando attach ou outra operadora", "NOREG_TRYANOTHER", False], 
		3: ["Registro recusado", "NOREG_REFUSED", False], 
		4: ["Desconhecido", "NOREG_UNK", False], 
		5: ["Registrado em roaming!", "REGROAM", True]
	}
	d_Act = {
		0: "GSM",
		8: "CAT-M1",
		9: "NB-IoT"
	}
	reg = "NOREGISTER"
	res = False
	phone.write(b'AT+CEREG=2\r\n')	# Configura para habilitar unsolicited results
	time.sleep(0.5)
	result=(phone.read(phone.inWaiting())).decode('utf-8')
	print(result)
	phone.write(b'AT+CEREG?\r\n')	# Consulta se esta registrado na rede de pacotes. Trabalhando com n=0. Resposta: 
									#	When <n>=0, 1, or 2 and command successful:
									# +CEREG: <n>,<stat>[,[<tac>],[<ci>],[<AcT>[,<cause_type>,<reject_cause>]]]
									# stat: 0 = nao registrado, ainda tentando; 1 = registrado home; 2 = nao registrado, mas tentando attach ou buscando operadora
									#	3 = registro recusado; 4 = Desconhecido; 5 = registrado em roaming
									# tac = tracking area code; ci = cell id; Act = access technology (0=GSM, 8=M1, 9=NB)
									# cause_type = 0 indica que reject_cause contem EMM cause value, 1 indica que reject_cause contem manufacturer-specific cause
									# reject_cause contem a causa da falha no registro
	time.sleep(0.3)
	result=(phone.read(phone.inWaiting())).decode('utf-8')
	print(result)
	rs = result.split(',') #at+CEREG?  +CEREG: <n>,<stat>[,[<tac>],[<ci>],[<AcT>[,<cause_type>,<reject_cause>]]]  OK
	if len(rs) == 2:
		stat = int(rs[1][0])
		if stat in range(0,6):
			print(d_stat[stat][0])
			reg = d_stat[stat][1]
			res = d_stat[stat][2]
		else:
			print("Situacao de registro nao conhecida %d" % stat)
			reg = "UNKNOWNREGSTAT"
			res = False
		"""
		if stat == 0:
			print("Nao registrado. Ainda tentando...")
			reg = "NOREG_STILLTRY"
		elif stat == 1:
			print("Registrado rede home!")
			reg = "REGHOME"
			res = True
		elif stat == 2:
			print("Nao regsitrado. Tentando attach ou outra operadora")
			reg = "NOREG_TRYANOTHER"
		elif stat == 3:
			print("Registro recusado")
			reg = "NOREG_REFUSED"
		elif stat == 4:
			print("Desconhecido")
			reg = "NOREG_UNK"
		elif stat == 5:
			print("Registrado em roaming!")
			reg = "REGROAM"
			res = True
		else:
			print("Situacao de registro nao conhecida")
			reg = "UNKNOWNREGSTAT"
		"""
	if len(rs) > 2:
		stat = int(rs[1][0])
		if stat in range(0,6):
			print(d_stat[stat][0])
			reg = d_stat[stat][1]
			res = d_stat[stat][2]
		else:
			print("Situacao de registro nao conhecida %d" % stat)
			reg = "UNKNOWNREGSTAT"
			res = False
		"""
		if stat == 0:
			print("Nao registrado. Ainda tentando...")
			reg = "NOREG_STILLTRY"
		elif stat == 1:
			print("Registrado rede home!")
			reg = "REGHOME"
			res = True
		elif stat == 2:
			print("Nao regsitrado. Tentando attach ou outra operadora")
			reg = "NOREG_TRYANOTHER"
		elif stat == 3:
			print("Registro recusado")
			reg = "NOREG_REFUSED"
		elif stat == 4:
			print("Desconhecido")
			reg = "NOREG_UNK"
		elif stat == 5:
			print("Registrado em roaming!")
			reg = "REGROAM"
			res = True
		else:
			print("Situacao de registro nao conhecida")
			reg = "UNKNOWNREGSTAT"
		"""
		tac = rs[2]
		ci = rs[3]
		desc = rs[4]
		Act = int(rs[5][0])
		if Act in [0, 8, 9]:
			Act_str = d_Act[Act]
		else:
			Act_str = "Unknows Access Technology"
		"""
		if Act == 0:
			Act_str = "GSM"
		elif Act == 8:
			Act_str = "CAT-M1"
		elif Act == 9:
			Act_str = "NB-IoT"
		else:
			Act_str = "Unknows Access Technology"
		"""
		if len(rs) > 6:
			cause_type = int(rs[5][0])
			reject_cause = int((rs[6].split())[0])
			reg += ",%s,%s,%s,%s,%s" % (tac, ci, Act_str, cause_type, reject_cause)
			print("NAO Registrado: TAC = %s, Cell_ID = %s, Desc = %s, Act = %d (%s), Cause_type = %d, Reject_Cause = %d" % (tac, ci, desc, Act, Act_str, cause_type, reject_cause))
		else:
			print("Registrado: TAC = %s, Cell_ID = %s, Desc = %s, Act = %d (%s)" % (tac, ci, desc, Act, Act_str))
			reg += ",%s,%s,%s" % (tac, ci, Act_str)
	phone.write(b'AT+CEREG=0\r\n')	# Configura para desabilitar unsolicited results
	return reg, res
	
def get_activepdp(phone):
	pdpres = "NOPDP"
	is_pdp = False
	phone.write(b'AT+QIACT?\r\n') 
	phone.timeout = 150	#QIACT pode levar ate 150 segundos para responder
	time.sleep(2)
	result=(phone.read(phone.inWaiting())).decode('utf-8')
	print(result)
	phone.reset_input_buffer()
	rs = result.split(',')
	if len(rs) > 2:
		context_state = rs[1]
		context_type = rs[2]
		ip_addr = (rs[3].split("\r"))[0]
		if context_state == "1":
			print("PDP ativo. IP = %s" % ip_addr)
			pdpres = "PDPACTIVE,%s" % (ip_addr)
			is_pdp = True
		else:
			print("PDP inativo")
			pdpres = "NOPDP"
			is_pdp = False
	else:
		print("PDP inativo")
		pdpres = "NOPDP"
		is_pdp = False
	return pdpres, is_pdp

def activate_pdp(phone):
	res = False
	phone.write(b'AT+QIACT=1\r\n')
	time.sleep(3)
	result=(phone.read(phone.inWaiting())).decode('utf-8')
	if 'OK' not in result:
		print(result)
		print("ERRO: Nao consegue ativar PDP")
		res = False
	else:
		res = True
	phone.reset_input_buffer()

def send_ping(phone, p_host, ping_tout = PING_TIMEOUT):
	ping_res_str = "NOANSWER"
	ping_cmd_str = 'AT+QPING=1,"%s",%d,1\r\n' % (p_host, ping_tout)
	print(ping_cmd_str)
	ptout_bkp = phone.timeout
	phone.timeout = 1
	phone.write(ping_cmd_str.encode('ascii'))
	result = ""
	t_out = ping_tout+1
	while ("+QPING" not in result) and (t_out>=0):
		result+=(phone.read(phone.inWaiting())).decode('utf-8')
		time.sleep(1)
		t_out -= 1
	
	print(result)
	phone.reset_input_buffer()
	r_bytes = "0"
	r_time = "0"
	r_ttl = "0"
		
	if '+QPING' in result:
		rs = result.split("+QPING: ")
		if len(rs) > 1:
			rsp1 = rs[1]
			resp = rsp1.split(',')
			if resp[0] == "0":
				r_bytes = resp[2]
				r_time = resp[3]
				r_ttl = (resp[4].split('\r'))[0]
				ping_res_str = "PING:%s,%s,%s,%s" % (p_host, r_bytes, r_time, r_ttl)
			else:
				print("NOANSWER")
				ping_res_str = "NOANSWER"
				r_bytes = "-1"
				r_time = "-1"
				r_ttl = "-1"
				
				if '569' in rs[1]:
					print("Operation timeout (demorou mais que %d seg)" % (ping_tout))
					ping_res_str += ":TIMEOUT(>%d seg)" % (ping_tout)
				elif '570' in rs[1]:
					print("PDP context broken down")
					ping_res_str +=":PDP BROKEN"
				elif '568' in rs[1]:
					print("Operation busy")	
					ping_res_str += ":BUSY"
				else:
					print("Erro: %s" % rs[1])
					ping_res_str += ":ERRO(%s)" % rs[1]
		else:
			print("NOANSWER-NO-QPING")
			ping_res_str += ":NO-QPING"
			r_bytes = "-1"
			r_time = "-1"
			r_ttl = "-1"
			
			if '569' in rs[0]:
				print("Operation timeout (demorou mais que %d seg)" % (ping_tout))
				ping_res_str += ":TIMEOUT(>%d seg)" % (ping_tout)
			elif '570' in rs[0]:
				print("PDP context broken down")
				ping_res_str +=":PDP BROKEN"
			elif '568' in rs[0]:
				print("Operation busy")	
				ping_res_str += ":BUSY"
			else:
				print("Erro: %s" % (rs[0].split("\r"))[0])
				ping_res_str += ":ERRO(%s)" % rs[0]
	else:
		print("ERROR in result")
		ping_res_str += ":ERROR IN RESULT"
	phone.timeout = ptout_bkp

	return ping_res_str, r_time

def send_udp_echo(phone, p_host, echo_tout = ECHO_TIMEOUT):
	"""
	Considera que contexto PDP esta ativo (AT+QIACT=1 antes)
	AT+QIOPEN=1,2,"UDP SERVICE","127.0.0.1",0,3030,0 - context = 1, connect ID = 2, service type UDP, server = 127.0.0.1, remote port = 0, local port = 3030, access mode = 0 (buffer. Usar 1 para direct push). AT+QIACT tem que ser enviado antes. Esperar até 150segundos por  erro. Se vier +QIOPEN: <connectID>,<err> deve fechar o socket (AT+QICLOSE)
		OK
		
		+QIOPEN: 2,0
	AT+QISEND=2,10,“10.7.89.10”,6969  -envia 10 bytes para servidor em 10.7.89.10, porta 6969
	>1234567890
	SEND OK
	
	+QIURC: “recv”,2 - recebendo dados
	AT+QIRD=2 - pede para ler dados
	+QIRD: 4,“10.7.76.34”,7687 - 4 bytes para leitura
	AAAA  - dado
	AT+QICLOSE=2 - fecha serviço
	*********	TESTANDO:
	***
	AT+QIOPEN=1, 0, "UDP SERVICE", "echo.u-blox.com", 7, 3030, 0
	OK
	
	+QIOPEN: 0,0
	***
	
	AT+QISTATE?
	+QISTATE: 0,"UDP SERVICE","187.47.157.166",7,3030,2,1,0,0,"usbat"
	
	OK
	***
	List of (+QISTATE:
	<connectID>,<service_type>,<IP_address>,<remote_port>
	,<local_port>,<socket_state>,<contextID>,<serverID>,<access_mode>,<AT_port>)
	
	***
	AT+QIDNSGIP=1, "echo.u-blox.com"
	OK

	+QIURC: "dnsgip",0,1,300

	+QIURC: "dnsgip","195.34.89.241"
	***
	
	AT+QISEND=<connectID>,<send_length>,<remoteIP>,<remote_port>
	***
	AT+QISEND=0,14,"195.34.89.241",7
	> echo teste 001
	SEND OK

	+QIURC: "recv",0
	***
	
	+QIRD:
	<read_actual_length>,<remoteIP>,<remote_port><CR><LF><data>
	***	
	AT+QIRD=0
	+QIRD: 14,"195.34.89.241",7
	echo teste 001

	OK
	***

	***
	AT+QICLOSE=0
	
	"""
	echo_res_str = "NOANSWER"
	echo_cmd_str = 'AT+QPING=1,"%s",%d,1\r\n' % (p_host, ping_tout)
	print(echo_cmd_str)
	ptout_bkp = phone.timeout
	phone.timeout = 1
	phone.write(echo_cmd_str.encode('ascii'))
	result = ""
	t_out = echo_tout+1

def conn_mqtt(phone):
	"""
	1 - sem QMTCFG (vamos usar defaults)
	2 - AT+QMTOPEN=0,"mqtt.tago.io",1883
	OK

	+QMTOPEN: 0,0
	+QMTOPEN: <tcpconnectID>,<result>
	Result of the command execution
		-1 Failed to open network
		0 Network opened successfully
		1 Wrong parameter
		2 MQTT identifier is occupied
		3 Failed to activate PDP
		4 Failed to parse domain name
		5 Network disconnection error
		
	3 - AT+QMTCONN=0,"quecmq","atila","24310f13-22ea-4342-951a-e9000f818b2e"
	OK

	+QMTCONN: 0,0,0
	+QMTCONN: <tcpconnectID>,<result>[,<ret_code>]
	<result>	Result of the command execution
		0 Packet sent successfully and ACK received from server
		1 Packet retransmission
		2 Failed to send packet
	<ret_code>	Connection status return code
		0 Connection Accepted
		1 Connection Refused: Unacceptable Protocol Version
		2 Connection Refused: Identifier Rejected
		3 Connection Refused: Server Unavailable
		4 Connection Refused: Bad User Name or Password
		5 Connection Refused: Not Authorized
	OU
	+CME ERROR: <err>
	"""
	conn_ok = False
	result_code = -1
	result_d = {
		-1: "Failed to open network",
		0: "Network opened successfully",
		1: "Wrong parameter",
		2: "MQTT identifier is occupied",
		3: "Failed to activate PDP",
		4: "Failed to parse domain name",
		5: "Network disconnection error"
	}
	result_conn_d = {
		0: "Packet sent successfully and ACK received from server",
		1: "Packet retransmission",
		2: "Failed to send packet"
	}
	ret_code_d = {
		0: "Connection Accepted",
		1: "Connection Refused: Unacceptable Protocol Version",
		2: "Connection Refused: Identifier Rejected",
		3: "Connection Refused: Server Unavailable",
		4: "Connection Refused: Bad User Name or Password",
		5: "Connection Refused: Not Authorized"
	}
	phone.write(b'AT+QMTOPEN=0,"mqtt.tago.io",1883\r\n')
	#time.sleep(0.4)
	tout_bkp = phone.timeout
	phone.timeout = MQTT_TIMEOUT
	"""
	OK

	+QMTOPEN: 0,0
	"""
	blank = phone.readline().decode('utf-8')
	ret = phone.readline().decode('utf-8')
	#print('blank: %s ret:%s' % (blank,ret))
	if 'OK' in ret:
		blank = phone.readline().decode('utf-8')
		result_str = phone.readline().decode('utf-8')
		#print('blank:%s result_str:%s' % (blank, result_str))
		if '+QMTOPEN' in result_str:
			result_code = int(result_str.split(',')[1])
		print("%s - %s" % (result_str, result_d[result_code]))
	else:
		discconn_mqtt(phone)
	if result_code == 0:
		phone.write(b'AT+QMTCONN=0,"quecmq","atila","24310f13-22ea-4342-951a-e9000f818b2e"\r\n')
		"""
		OK

		+QMTCONN: 0,0,0
		"""
		blank = phone.readline().decode('utf-8')
		ret = phone.readline().decode('utf-8')
		if 'OK' in ret:
			blank = phone.readline().decode('utf-8')
			result_con_str = phone.readline().decode('utf-8')
			print('blank:%s, ret:%s, result_con_str:%s' %(blank, ret, result_con_str))
			tmp_res = result_con_str.split(',')
			result_con_code = int(tmp_res[1])
			if result_con_code == 0:
				ret_con_code = int(tmp_res[2])
				print("%s - %s - %s" % (result_con_str, result_conn_d[result_con_code], ret_code_d[ret_con_code]))
			else:
				ret_con_code = -1
			if (result_con_code != 0) or (ret_con_code != 0):
				conn_ok = False
			else:
				conn_ok = True
	else:
		discconn_mqtt(phone)
	
	phone.timeout = tout_bkp
	return conn_ok
	

	
def pub_mqtt(phone, msg):
	"""
	4- AT+QMTPUB=0,0,0,1,"tago/data/post"
	>{"variable":"rssi","value":90,"unit":"dB"}<CTRL-Z>
	OK

	+QMTPUB: 0,0,0
	AT+QMTPUB=0,0,0,1,"tago/data/post"
	{"variable":"rsrq","value":-9,"unit":"dB","time":"2019-01-29 18:43:10","location": {"lat": -21.98486, "lng": -42.35916}}

	AT+QMTDISC=0
	AT+QMTCLOSE=0
	
	msg = {
		"variable": "latency",
		"value": 0,
		"unit": "ms",
		"time": "2019-01-29 18:43:10",
		"location": {
			"lat": -21.98486,
			"lng": -42.35916
		}
	}
	msg["value"] = int(latency)
	msg["time"] = date_time
	msg["location"]["lat"] = float(lat)
	msg["location"]["lng"] = float(lng)
	"""
	
	phone.write(b'AT+QMTPUB=0,0,0,1,"tago/data/post"\r\n')
	time.sleep(0.4)
	#mqtt_cmd_str = '{"variable":"latency","value":"%s","unit":"ms","time":"%s","location": {"lat":%s, "lng":%s}}\x1A\r\n' % (latency, date_time, lat, lng )
	mqtt_cmd_str = json.dumps(msg)+'\x1A\r\n'
	print(mqtt_cmd_str)
	phone.write(mqtt_cmd_str.encode('ascii'))
	#phone.write(b'{"variable":"rsrq","value":-9,"unit":"dB","time":"2019-01-29 18:43:10","location": {"lat": -21.98486, "lng": -42.35916}}\x1A\r\n')

def discconn_mqtt(phone):
	phone.write(b'AT+QMTDISC=0\r\n')
	time.sleep(0.4)
	phone.write(b'AT+QMTCLOSE=0\r\n')


def drive(phone, sample, interval = 5, fname="log_quectel.txt"):	  
	x = 0 
	phone.write(b'ATE0\r\n') #desligando echo
	time.sleep(3)
	phone.reset_input_buffer()
	while x < int(sample):
		print('***** INICIO SIGNAL %d' % (x))
		qcsq, signal, celevel, rssi, rsrp, sinr, rsrq = get_signal(phone)
		print('##### FIM SIGNAL %d' % (x))
		#time.sleep(4)
		print('***** INICIO GPS %d' % (x))
		gps, position = get_gps(phone)
		print('##### FIM GPS %d' % (x))
		"""
		if signal == "NOSIGNAL" and position == "NOGPS":
			print("Nao leu nada")
			time.sleep(interval)
			continue
		"""
		#time.sleep(4)
	
		now = get_now()
		
		text_file = open(fname,"a")
		
		#print("SUMMARY: " + str(celevel) + " " + str(signal) + " " +  str(position) + " " + str(now))
		print("RESUMO: celevel = %s, sinal = %s, posicao = %s, momento = %s" %(celevel, signal, position, now))
		text_file.write(str(celevel) + " " + str(signal) + " " + str(position) + " " + str(now))
		text_file.close()

		x = x + 1
		time.sleep(interval)
		
def ping(phone, p_host, n, interval = 5, ping_tout = PING_TIMEOUT, fname="log_ping_quectel.txt"):
	"""
	at+qiact?
	+QIACT: 1,1,1,"191.142.97.204"
		1,<context_state>,<context_type>[,<IP_address>]
	OK
	at+qiact=1

	at+qping=1,"8.8.8.8"
	OK

	+QPING: 0,"8.8.8.8",32,823,255

	+QPING: 0,"8.8.8.8",32,193,255

	+QPING: 0,"8.8.8.8",32,400,255

	+QPING: 0,"8.8.8.8",32,173,255

	+QPING: 0,4,4,0,173,823,397

	[+QPING:
	<result>[,<IP_address>,<bytes>,<time>,<ttl>]<CR><LF>…]
	+QPING:
	<finresult>[,<sent>,<rcvd>,<lost>,<min>,<max>,<avg>]
	"""
	phone.write(b'ATE0\r\n') # desligando echo
	time.sleep(1)
	phone.write(b'AT+QIACT?\r\n') 
	phone.timeout = 150	#QIACT pode levar ate 150 segundos para responder
	time.sleep(2)
	result=(phone.read(phone.inWaiting())).decode('utf-8')
	print(result)
	phone.reset_input_buffer()
	rs = result.split(',')
	if len(rs) > 2:
		context_state = rs[1]
		context_type = rs[2]
		ip_addr = rs[3]
		if context_state == "1":
			print("PDP ativo. IP = %s" % ip_addr)
		else:
			print("PDP inativo. Ativando")
			phone.write(b'AT+QIACT=1\r\n')
			time.sleep(0.3)
			result=(phone.read(phone.inWaiting())).decode('utf-8')
			if 'OK' not in result:
				print(result)
				print("ERRO: Nao conseguiu ativar PDP. IP: %s" % (ip_addr))
				return
	else:
		phone.write(b'AT+QIACT=1\r\n')
		time.sleep(3)
		result=(phone.read(phone.inWaiting())).decode('utf-8')
		if 'OK' not in result:
			print(result)
			print("ERRO: Nao consegue ativar PDP")
			return
	
	phone.reset_input_buffer()
	#ping_cmd_str = 'AT+QPING=1,"%s",%d,1\r\n' % (p_host, PING_TIMEOUT)
	#phone.timeout = PING_TIMEOUT+1
	ping_cmd_str = 'AT+QPING=1,"%s",%d,1\r\n' % (p_host, ping_tout)
	print(ping_cmd_str)
	phone.timeout = 1
	time_l = []
	for i in range(n):
		print('***** INICIO PING %d' % (i))
		phone.write(ping_cmd_str.encode('ascii'))
		result = ""
		t_out = ping_tout+1
		while ("+QPING" not in result) and (t_out>=0):
			result+=(phone.read(phone.inWaiting())).decode('utf-8')
			time.sleep(1)
			t_out -= 1
		
		print(result)
		phone.reset_input_buffer()
		r_bytes = "0"
		r_time = "0"
		r_ttl = "0"
		f_sent = "0"
		f_rcvd = "0"
		f_lost = "0"
		f_min = "0"
		f_max = "0"
		f_avg = "0"
		
		if '+QPING' in result:
			rs = result.split("+QPING: ")
			if len(rs) > 1:
				rsp1 = rs[1]
				resp = rsp1.split(',')
				if resp[0] == "0":
					r_bytes = resp[2]
					r_time = resp[3]
					time_l.append(int(r_time))
					r_ttl = (resp[4].split('\r'))[0]
					#finresult = rs[-1]
					#frs = finresult.split(',')
					#f_sent = frs[1]
					#f_rcvd = frs[2]
					#f_lost = frs[3]
					#f_min = frs[4]
					#f_max = frs[5]
					#f_avg = (frs[6].split('\r'))[0]
				else:
					print("NOANSWER")
					r_bytes = "-1"
					r_time = "-1"
					r_ttl = "-1"
					
					if '569' in rs[1]:
						print("Operation timeout (demorou mais que %d seg)" % (ping_tout))
					elif '570' in rs[1]:
						print("PDP context broken down")
					elif '568' in rs[1]:
						print("Operation busy")	
					else:
						print("Erro: %s" % rs[1])
			else:
				print("NOANSWER-NO-QPING")
				r_bytes = "-1"
				r_time = "-1"
				r_ttl = "-1"
				
				if '569' in rs[0]:
					print("Operation timeout (demorou mais que %d seg)" % (ping_tout))
				elif '570' in rs[0]:
					print("PDP context broken down")
				elif '568' in rs[0]:
					print("Operation busy")	
				else:
					print("Erro: %s" % rs[0])
		else:
			print("ERROR in result")
		
					
		print('***** INICIO GPS %d' % (i))
		gps, position = get_gps(phone)
		print('##### FIM GPS %d' % (i))
		print('***** INICIO SIGNAL %d' % (i))
		qcsq, signal, celevel, rssi, rsrp, sinr, rsrq = get_signal(phone)
		print('##### FIM SIGNAL %d' % (i))
		now = get_now()
		#log_str = "%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % (p_host, f_sent, f_rcvd, f_lost, f_min, f_max, f_avg, position, now)
		#print("Host:%s, sent: %s, rcvd: %s, lost: %s, min: %s, max: %s, avg: %s, location: %s, datetime: %s" % (p_host, f_sent, f_rcvd, f_lost, f_min, f_max, f_avg, position, now))
		log_str = "%s,%s,%s,%s, %s, %s, %s, %s" % (p_host, r_bytes, r_time, r_ttl, celevel, signal, position, now)
		print("Host:%s, bytes_sent: %s, time (ms): %s, ttl: %s, celevel: %s, signal: %s, location: %s, datetime: %s" % (p_host, r_bytes, r_time, r_ttl, celevel, signal, position, now))

		text_file = open(fname,"a")
		text_file.write(log_str)
		text_file.flush()
		text_file.close()
		print('##### FIM PING %d' % (i))
		time.sleep(interval)
	log_str = "Resumo (timeout = %d) - total enviado: %d, total recebido: %d, media da latencia (ms): %.2f" % (ping_tout, n, len(time_l), float('inf') if len(time_l) == 0 else sum(time_l)/len(time_l) )
	text_file = open(fname,"a")
	text_file.write(log_str)
	text_file.flush()
	text_file.close()
	print(log_str)

def sig_reg_ping(phone, p_host, interval = 5, ping_tout = PING_TIMEOUT, fname="log_sig_reg_ping_quectel.txt"):
	"""
	Teste continuo com sinal, registro, attach e ping.
	pega gps
	pega momento
	tem sinal?
		sinal = s
		tem registro (IP)?
			registro = r
			tem activepdp?
				manda ping
				ping = p
			else
				activevatepdp
				attach = a
		else
			registra
			resgitro = r
	grava resultado de tudo	(sinal, registro, attach, ping, gps, momento)
		
	"""
	phone.write(b'ATE0\r\n') # desligando echo
	time.sleep(1)
	sinal = "NOSIGNAL"
	registro = "NOREGISTER"
	activepdp = "NOPDP"
	ping = "NOPING"
	i = 0
	while True:
		print('***** INICIO GPS %d' % (i))
		gps, position = get_gps(phone)
		print('##### FIM GPS %d' % (i))
		now = get_now()
		
		print('***** INICIO SIGNAL %d' % (i))
		qcsq, signal, celevel, rssi, rsrp, sinr, rsrq = get_signal(phone)
		print('##### FIM SIGNAL %d' % (i))
		if ('+QCSQ' in qcsq) and ('NOSERVICE' not in qcsq):	# Tem sinal NB
			sinal = "%s, %s" % (celevel,signal)
			print('***** INICIO REGISTRO %d' % (i))
			registro, is_reg = get_registro(phone)
			print('##### FIM REGISTRO %d' % (i))
			if is_reg:		# Esta registrado
				print('***** INICIO PDP %d' % (i))
				activepdp, is_pdp = get_activepdp(phone)
				print('##### FIM PDP %d' % (i))
				if is_pdp:	# Esta com PDP ativo
					print('***** INICIO PING %d' % (i))
					ping, p_time = send_ping(phone, p_host, ping_tout)
					print('##### FIM PING %d' % (i))
				else:		# PDP nao esta ativo
					activepdp = "NOPDP"
					ping = "NOPING"
					print('***** INICIO ACTIVATE PDP %d' % (i))
					res = activate_pdp(phone)
					print('##### FIM ACTIVATE PDP %d' % (i))
			else:		# Nao esta registrado
				registro = "NOREGISTER"
				activepdp = "NOPDP"
				ping = "NOPING"
		else:				# Nao tem sinal NB
			sinal = "NOSIGNAL"
			registro = "NOREGISTER"
			activepdp = "NOPDP"
			ping = "NOPING"
			print('***** INICIO Reset Radio %d' % (i))
			reset_radio(phone)
			print('##### FIM Reset Radio %d' % (i))

		
		
		log_str = "%s; %s; %s; %s; %s; %s" % (sinal, registro, activepdp, ping, position, now)
		text_file = open(fname,"a")
		text_file.write(log_str)
		text_file.flush()
		text_file.close()
		print(log_str)

		i += 1
		print('***** ESPERANDO %d segundos para proxima iteracao' % interval)
		time.sleep(interval)
		print('##### FIM DA ESPERA')
		
def sig_reg_ping_pub(phone, p_host, interval = 5, ping_tout = PING_TIMEOUT, fname="log_sig_reg_ping_pub_quectel.txt"):
	"""
	Teste continuo com sinal, registro, attach e ping, sendo também publicado em tago.io.
	pega gps
	pega momento
	tem sinal?
		sinal = s
		tem registro (IP)?
			registro = r
			tem activepdp?
				manda ping
				ping = p
				publica resultados (latencia do ping)
			else
				activevatepdp
				attach = a
		else
			registra
			resgitro = r
	grava resultado de tudo	(sinal, registro, attach, ping, gps, momento)
		
	"""
	phone.write(b'ATE0\r\n') # desligando echo
	time.sleep(1)
	sinal = "NOSIGNAL"
	registro = "NOREGISTER"
	activepdp = "NOPDP"
	ping = "NOPING"		
	latency = 0
	msg_pub_latency = {
		"variable": "latency",
		"value": 0,
		"unit": "ms",
		"time": "2019-01-29 18:43:10",
		"location": {
			"lat": -22.98486,
			"lng": -43.35916
		}
	}
	msg_pub_rsrp = {
		"variable": "rsrp",
		"value": 255,		# de -44 a -140. -75 (proximo do site) a -120 (na borda)
		"unit": "dBm",
		"time": "2019-01-29 18:43:10",
		"location": {
			"lat": -22.98486,
			"lng": -43.35916
		}
	}

	lat = -21.98486
	lng = -42.35916
	res_conn_mq = False
	i = 0
	while True:
		print('***** INICIO GPS %d' % (i))
		gps, position = get_gps(phone)
		if position != "NOGPS":
			lat = float((position.split(","))[1])
			lng = float((position.split(","))[2])
			print("Lat: %3.4f, Long: %3.4f" % (lat, lng))
		print('##### FIM GPS %d' % (i))
		now = get_now()
		
		print('***** INICIO SIGNAL %d' % (i))
		qcsq, signal, celevel, rssi, rsrp, sinr, rsrq = get_signal(phone)
		print('##### FIM SIGNAL %d' % (i))
		if ('+QCSQ' in qcsq) and ('NOSERVICE' not in qcsq):	# Tem sinal NB
			sinal = "%s, %s" % (celevel,signal)
			print('***** INICIO REGISTRO %d' % (i))
			registro, is_reg = get_registro(phone)
			print('##### FIM REGISTRO %d' % (i))
			if is_reg:		# Esta registrado
				print('***** INICIO PDP %d' % (i))
				activepdp, is_pdp = get_activepdp(phone)
				print('##### FIM PDP %d' % (i))
				if is_pdp:	# Esta com PDP ativo
					print('***** INICIO PING %d' % (i))
					ping, p_time = send_ping(phone, p_host, ping_tout)
					print('##### FIM PING %d' % (i))
					print('***** INICIO PUBLISH MQTT')
					res_conn_mq = conn_mqtt(phone)
					if res_conn_mq:
						print('### CONECTOU MQTT e VAI TENTAR PUBLICAR')
						msg_pub_latency["value"] = int(p_time)
						msg_pub_latency["time"] = now
						msg_pub_latency["location"]["lat"] = lat
						msg_pub_latency["location"]["lng"] = lng
						pub_mqtt(phone, msg_pub_latency)
						msg_pub_rsrp["value"] = rsrp
						msg_pub_rsrp["time"] = now
						msg_pub_rsrp["location"]["lat"] = lat
						msg_pub_rsrp["location"]["lng"] = lng
						pub_mqtt(phone, msg_pub_rsrp)
						discconn_mqtt(phone)
					else:
						print('### NAO CONSEGUIU CONECTAR MQTT')
					print('##### FIM PUBLISH MQTT')
					
				else:		# PDP nao esta ativo
					activepdp = "NOPDP"
					ping = "NOPING"
					print('***** INICIO ACTIVATE PDP %d' % (i))
					res = activate_pdp(phone)
					print('##### FIM ACTIVATE PDP %d' % (i))
			else:		# Nao esta registrado
				registro = "NOREGISTER"
				activepdp = "NOPDP"
				ping = "NOPING"
		else:				# Nao tem sinal NB
			sinal = "NOSIGNAL"
			registro = "NOREGISTER"
			activepdp = "NOPDP"
			ping = "NOPING"
			print('***** INICIO Reset Radio %d' % (i))
			reset_radio(phone)
			print('##### FIM Reset Radio %d' % (i))

		
		
		log_str = "%s; %s; %s; %s; %s; %s; %s" % (sinal, registro, activepdp, ping, res_conn_mq, position, now)
		text_file = open(fname,"a")
		text_file.write(log_str)
		text_file.flush()
		text_file.close()
		print(log_str)

		i += 1
		print('***** ESPERANDO %d segundos para proxima iteracao' % interval)
		time.sleep(interval)	
		print('##### FIM DA ESPERA')


 
