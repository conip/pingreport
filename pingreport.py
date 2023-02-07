#!/usr/bin/env python
import re
import sys
import os
import time
import datetime
import subprocess
import shlex
import math

#============================================================================================================================
#CLASS definitions
#============================================================================================================================
class REPORT:
	def __init__(self,FILE=None,var_latency = None,var_num_pings = None):
		self.FILE = FILE
		self.file_content = ''
		self.ping_started = ''
		self.ping_ended = ''
		self.ping_duration = ''
		self.ping_started_sec = ''
		self.ping_ended_sec = ''
		self.ping_interval = ''
		self.total_ping_sent = ''
		self.total_ping_lost = ''
		self.total_ping_replies = 0
		self.highest_latency = '0'
		self.lowest_latency = '10000'
		self.avarage_latency = 0
		self.five_pings_list = []
		self.latency_above_list = []
		self.var_latency = float(var_latency)
		self.var_num_pings = int(var_num_pings)
	#-----------	
	def file_open(self):
		with open(self.FILE,'r+') as f:
			try:
				ping_data = f.readlines()
				#print(ping_data)
				var_whoami = subprocess.check_output('whoami').decode('ascii')
				cmd = 'date'
				var_date = subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')				
				f.write(str(int(time.time()))+" | "+str(var_date).strip()+" | [ANALYZING] - [DONE BY: " +str(var_whoami).strip()+"]\n")
				f.close()
				pass
			except:
				return 'ERROR';
				
		if ping_data:
			time_latency_i = ''
			sum = 0
			icmp_seq_x = ''
			icmp_seq_y = 0
			date_x = ''
			date_y = ''
			sec_x = '0'
			sec_y = '0'
			sec_gap_window = ''
			ping_gap_window = 0
			high_latency_start_sec = ''
			high_latency_end_sec = ''
			high_latency_start_date = ''
			high_latency_end_date = ''
			self.file_content = ping_data
			latency_window_count = 0
			latency_window = False
			#latency_ping_count = 0
			for i in range(len(ping_data)):
				#print(ping_data[i])
				if (re.search(r'END PING',str(ping_data[i])) and latency_window == True):
					high_latency_end_sec = sec_x
					high_latency_end_date = date_x
					self.latency_above_list.append([high_latency_start_sec, high_latency_end_sec, high_latency_start_date, high_latency_end_date, latency_window_count])
				
				
				
				if (re.search(r'icmp_seq',str(ping_data[i])) and re.search(r'time=\d+\.?\d?',str(ping_data[i]))):
					self.total_ping_replies = self.total_ping_replies + 1
					#print(self.total_ping_replies)
					line = re.split('\|',self.file_content[i])
					date_x = line[1]
					sec_x = line[0]
					icmp_seq_x = re.search(r'icmp_seq=\d+',str(self.file_content[i])).group(0)
					icmp_seq_x = icmp_seq_x.lstrip('icmp_seq=')	
					time_latency_i = re.search(r'time=\d+\.?\d?',str(ping_data[i])).group(0).strip('time=')
					
					sum = sum + float(time_latency_i)					
					if ((int(icmp_seq_x) - int(icmp_seq_y)) > 5):
						sec_gap_window = int(sec_x) - int(sec_y)
						ping_gap_window = int(icmp_seq_x) - int(icmp_seq_y)
						self.five_pings_list.append([sec_gap_window,date_x, date_y, icmp_seq_x, icmp_seq_y, ping_gap_window])

					

					
					if (float(time_latency_i) > self.var_latency):
						latency_window_count = latency_window_count + 1
					else:
						
						latency_window = False
						if (latency_window_count > 4):
							#adding window occurence to the list 
							self.latency_above_list.append([high_latency_start_sec, high_latency_end_sec, high_latency_start_date, high_latency_end_date, latency_window_count])
						latency_window_count = 0
					
					if ((latency_window_count == 1) and latency_window == False):
						
						high_latency_start_sec = sec_x
						high_latency_start_date = date_x
						latency_window = True
					elif ((latency_window == True) and (latency_window_count > 4)):
						high_latency_end_sec = sec_x
						high_latency_end_date = date_x
			
					#print('date: '+ date_x + ' | end date: '+high_latency_end_date+' | window count: '+str(latency_window_count) + ' | ' + str(time_latency_i))						
						
					

						#print('latency_window_count = '+str(latency_window_count))
						
					icmp_seq_y = icmp_seq_x
					date_y = date_x
					sec_y = sec_x
					self.highest_latency = max(float(time_latency_i), float(self.highest_latency))
					self.lowest_latency = min(float(time_latency_i), float(self.lowest_latency))
					self.avarage_latency = sum/self.total_ping_replies
					
			self.avarage_latency = float("{0:.2f}".format(self.avarage_latency))
			
			if self.total_ping_replies == 0: #if no reply found - we need to erase these 2 
				self.highest_latency = 'none'
				self.lowest_latency = 'none'
				self.avarage_latency = 'none'
			#print(ping_data[0])
			try: 
				interval_string = re.search(r'INTERVAL:.+sec',str(ping_data[0]))
				interval = interval_string.group(0).split(' ')
				self.ping_interval = interval[1]
			#print(interval_string)
			except:
				print('ERROR: File is missing INTERVAL information. Was probably modified manualy!')
				return 'ERROR';
			
			
		else:
			print('file empty')						
		return 
	#-----------
	def f_report_save(self):
		print('Saving to file: \"'+' XXXX ' + '\"')
		return
	#-----------
	def f_report_started(self):
		# print('################')
		# print(self.file_content)
		if len(self.file_content) == 1:
			firstline_time = re.split('\|',self.file_content[0])
		else:
			firstline_time = re.split('\|',self.file_content[1])
		self.ping_started = firstline_time[1]
		self.ping_started_sec = firstline_time[0]
		return 
	#-----------
	def f_read_last_icmp_seq(self):
		i = -1
		last_icmp_seq = ''
		last_icmp_seq_time_sec = ''
		while 1:
			self.file_content[i]
			if re.search(r'icmp_seq',str(self.file_content[i])):
				line_list = re.split('\|',self.file_content[i])
				last_icmp_seq_time_sec = str(line_list[0]).strip()
				last_icmp_seq = re.search(r'icmp_seq=\d+',str(self.file_content[i])).group(0)
				last_icmp_seq = last_icmp_seq.lstrip('icmp_seq=')
				break
			if re.search(r'BEGIN PING',str(self.file_content[i])):
				last_icmp_seq = 0
				last_icmp_seq_time_sec = 0
				break
			i = i-1

		return last_icmp_seq, last_icmp_seq_time_sec; 			
	#-----------
	def f_report_ended(self):
		#starting from last line
		i = -1
		time_final_asci = ''
		time_final_sec = ''
		cmd = 'date'
		last_icmp_seq, last_icmp_seq_time_sec = self.f_read_last_icmp_seq()
		
		if last_icmp_seq != 0:
		
			while 1:
				line_x = re.split('\|',self.file_content[i])
				line_y = re.split('\|',self.file_content[i-1]) #line before x
				time_x = int(line_x[0])
				time_y = int(line_y[0])

				test_analyzing_x = re.findall(r'ANALYZING',line_x[2])
				test_end_x = re.findall(r'END PING',line_x[2])
				test_icmp_seq_x = re.findall(r'icmp_seq',line_x[2])
				test_analyzing_y = re.findall(r'ANALYZING',line_y[2])
				test_end_y = re.findall(r'END PING',line_y[2])
				test_icmp_seq_y = re.findall(r'icmp_seq',line_y[2])
				test_begin_y = re.findall(r'BEGIN PING', line_y[2])
				
				if test_icmp_seq_x:
					#print('test_icmp_seq_x')

					var_date = subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')
					time_final_asci = str(var_date).strip()
					time_final_sec = int(time.time())
					break
				if test_analyzing_x:
					if test_analyzing_y:
						var_date = subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')
						time_final_asci = str(var_date).strip()
						time_final_sec = int(time.time())
					if test_icmp_seq_y:
						var_date = subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')
						time_final_asci = str(var_date).strip()
						time_final_sec = int(time.time())
						break
					if test_end_y:
						time_final_asci = str(line_y[1]).strip()
						time_final_sec = int(str(line_y[0]))
						break
					if test_begin_y:
						var_date = subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')
						time_final_asci = str(var_date).strip()
						time_final_sec = int(time.time())						
						break
				if test_end_x:
					time_final_asci = str(line_x[1]).strip()
					time_final_sec = str(line_x[0])
					break
				i = i-1
			
		else:
			# if there is no END PING tag and no icmp-seq reply it means proccess should still be running so check current time
			var_date = subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')
			time_final_asci = str(var_date).strip()
			time_final_sec = int(time.time())
		
		self.ping_ended = time_final_asci
		self.ping_ended_sec = time_final_sec
		return
	#-----------
	def f_duration(self):    # Wed May  8 03:36:58 DST 2019

		duration = int(self.ping_ended_sec) - int(self.ping_started_sec)
		days = duration//86400
		hours = (duration - days*86400)//3600
		minutes = (duration -(days*86400 + hours*3600))//60
		
		self.ping_duration = str(days)+" days "+str(hours)+" hours "+str(minutes)+" minutes"
		
	#-----------
	def f_total_ping_sent_lost(self):
		
		last_icmp_seq, time_of_last_icmp_seq = self.f_read_last_icmp_seq()
		
		if ((int(self.ping_ended_sec) - int(time_of_last_icmp_seq)) <= int(self.ping_interval)):
			self.total_ping_sent = int(last_icmp_seq)
			self.total_ping_lost = self.total_ping_sent - int(self.total_ping_replies)
			#print('x')
		else:
			self.total_ping_sent = 1 + (int(self.ping_ended_sec) - int(self.ping_started_sec)) // int(self.ping_interval)	
			self.total_ping_lost = self.total_ping_sent - self.total_ping_replies			
	#-----------
	def final_analize(self):
		self.f_report_started()
		self.f_report_ended()
		self.f_duration()
		self.f_total_ping_sent_lost()
		print(78 * "=")
		print(('PING REPORT - '+self.FILE).center(78,' '))
		print(78 * "=")
		print('TOTAL pings sent:   '.rjust(30,' ')+str(self.total_ping_sent))
		print('ping replies:   '.rjust(30,' ')+str(self.total_ping_replies))
		print('pings lost:   '.rjust(30,' ')+str(self.total_ping_lost))
		print('ping interval:   '.rjust(30,' ')+str(self.ping_interval))
		print('ping duration:   '.rjust(30,' ')+str(self.ping_duration))
		print('lowest latency:   '.rjust(30,' ')+str(self.lowest_latency)+' ms')
		print('highest latency:   '.rjust(30,' ')+str(self.highest_latency)+' ms')
		print('avarage latency:   '.rjust(30,' ')+str(self.avarage_latency)+' ms')
		print('report started:   '.rjust(30,' ')+str(self.ping_started).strip())
		print('report ended:   '.rjust(30,' ')+str(self.ping_ended))
		print('latency threshold:   '.rjust(30,' ')+"{:.0f}".format(float(self.var_latency))+' ms')
		#print(type(self.var_latency))
		print(78 * "-")
		#print('last icmp_seq = ' + str(x))
		print('periods when more than 5 following pings were lost:\n')
		#print(self.five_pings_list)
		
		for i in range(len(self.five_pings_list)):
			
			print(str(i+1)+')  '+str(self.five_pings_list[i][5])+' pings lost')
			print('started at: '.rjust(20,' ')+str(self.five_pings_list[i][2])+'icmp_seq = '+self.five_pings_list[i][4])
			print('restored at: '.rjust(20,' ') + str(self.five_pings_list[i][1])+'icmp_seq = '+str(self.five_pings_list[i][3])+'\n')
		print(78 * "-")
		#print(self.latency_above_list)
		print('periods with 5 or more following pings with latency higher than '+str(self.var_latency) +' ms:\n')
		#print(self.latency_above_list)
		for i in range(len(self.latency_above_list)):
			print(str(i+1)+')')
			print('started at: '.rjust(30,' ')+str(self.latency_above_list[i][2]))
			print('restored at: '.rjust(30,' ') + str(self.latency_above_list[i][3]))
			print('number of pings affected: '.rjust(30,' ') + str(self.latency_above_list[i][4])+'\n')
		return	


#============================================================================================================================
#functions definitions 
#============================================================================================================================
#------------------
def	f_ping(var_IP,var_interval):

	for x in range(len(var_IP)):
		file_name = 'ping_'+var_IP[x]+'.txt'
		output_file = open(file_name, "w+")
		os.chmod(file_name, 0o777)
		var_whoami = subprocess.check_output('whoami').decode('ascii')
		cmd = 'date'
		var_date = subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')
		output_file.write(str(int(time.time()))+" | "+str(var_date).rstrip()+" | [BEGIN PING] - [INTERVAL: "+str(var_interval)+" sec ] - [STARTED BY: " +str(var_whoami).rstrip()+"]\n")
		
		output_file.close()

		cmd = 'nohup sh -c \'ping -i '+var_interval+' '+var_IP[x]+' | while read pong; do echo \"$(date +\"%s | %a %b %d %H:%M:%S %Y %Z\") | $pong"; done >> ping_'+var_IP[x]+'.txt\' >> /dev/null 2>&1&'
		os.system(cmd)

		str1 = '\nping to '
		str2 = ' [STARTED]'
		print(str1.ljust(10)+var_IP[x].rjust(18,' ')+str2.rjust(12,' '))
		time.sleep(.6)
	time.sleep(2)
	os.system('clear')
#------------------
def f_ping_start():
	var_IP_list = [] 
	var_interval = 1
	var_sth_added = 0
	#os.system('clear')
	print('\nPlease provide IP to be tracked or type \'f\' to finish:')
	while 1:
		var_input = input()
		ip_candidate = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", str(var_input))
		if var_input == 'f':
			break
		if ip_candidate:
			x = f_proc_check(ip_candidate.group(0))
		
			if x == True:
				print('ping already active. Type another one or press \'f\' to finish: ')
			else:
				var_IP_list.append(ip_candidate.group(0))
				
				var_sth_added = 1
		else:
			print('please provide correct IP:')
	
	#os.system('clear')
	if var_sth_added == 1:
		while 1:
			var_interval = input('\nPlease provide TIME (sec) interval for ping:\n')
		
			if ( var_interval.isdigit() and var_interval != '0'):
				print('ok')
				break
	
	f_ping(var_IP_list,var_interval)
	
#------------------
def f_ping_analyze(var_latency,var_num_pings):
	os.system('clear')
	
	print(78 * "-")	
	print(('Select ID of the ping to analyze:').center(78,' '))
	print(78 * "-")	

	list_sorted = f_file_list()
	file_selected = ''
	if len(list_sorted) == 0:
		print('No files to analyze.\n')
		return
	
	if list_sorted:

		for i in range(len(list_sorted)):
			print('  '+str(i+1)+')\t'+str(list_sorted[i]))
		
	
	while 1:
		choice = input('\nSelect your option or press \'e\' to exit: ')		
		if choice.isdigit() and choice != '0' and int(choice) <= len(list_sorted):
			file_selected = list_sorted[int(choice)-1]
			
			analiza = REPORT(str(file_selected),var_latency,var_num_pings)
			analiza.file_open()
			analiza.final_analize()
			
		elif choice == 'e':
			os.system('clear')
			break
		else:
			print('Select again:')
		
#------------------
def f_current_ping_list_sorted():
	dict = f_proc_dict2()
	list = sorted(dict)
	#print(list)
	for i in range(len(dict)):
		dict_value = dict.get(list[i])
		string_user = '[ '+str(dict_value[0][1])+' ]'
		string_interval = '[ interval: '+str(dict_value[0][2]).rjust(3,' ')+' ms ]'
		#interval = str(dict_value[][])
		print('\t'+str(i+1)+')  '+str(list[i]).ljust(28,' ')+string_user + string_interval)
	#print dict	
		
	return dict,list;
#------------------
def f_ping_kill():
	os.system('clear')
	print(78 * "-")	
	print(('Select ID of the ping to stop:').center(78,' '))
	print(78 * "-")	
	dict, list_sorted = f_current_ping_list_sorted()	
	if len(dict) == 0:
		print('No active pings are running.\n')
		return		

	while 1:
	
		choice = input('\nSelect your option or press \'e\' to exit: ')		
	
		if choice.isdigit() and choice != '0' and int(choice) <= len(dict):
			process_list = dict[list_sorted[int(choice)-1]]
			#print(process_list)
			for j in range(len(process_list)):
				cmd = 'kill '+process_list[j][0]
				#print(cmd)
				#var = subprocess.call(cmd, shell = True)
				cmd_list = shlex.split(cmd)
				#var = subprocess.Popen(cmd_list	)
			
				p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
 
				(output, err) = p.communicate()
			
			
			if ('kill: Operation not permitted' in str(err)):
				#print(err)
				print('\nCan\'t kill this process. You may not be an owner!\n')
			else:
											
				str1 = '\nping to '
				str3 = '    [TERMINATED]\n'
				str2 = str(list_sorted[int(choice)-1])
				print(str1.ljust(10)+str2.rjust(18,' ')+str3.rjust(12,' '))
				del dict[list_sorted[int(choice)-1]]
				time.sleep(0.5)

				file_name = 'ping_'+str(list_sorted[int(choice)-1])+'.txt'
				output_file = open(file_name, "a+")
				var_whoami = subprocess.check_output('whoami').decode('ascii')
				cmd = 'date'
				var_date = subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')
				output_file.write(str(int(time.time()))+" | "+str(var_date).rstrip()+" | [END PING] - [TERMINDATED BY: "+str(var_whoami).rstrip()+"]\n")
				
				output_file.close()
			
			dict, list_sorted = f_current_ping_list_sorted()
		elif choice == 'e':
			os.system('clear')
			break
		else:
			print('Select again:')
	#os.system('clear')
#------------------
def f_proc_check(var_IP):
	cmd = "ps -aux | grep \'sh -c ping -i.*"+var_IP+".*while read pong\'"
	#var_proc = os.popen(cmd).read()
	#subprocess.check_output([cmd, '+%a %b %d %H:%M:%S %Y %Z']).decode('ascii')
	#var_proc = subprocess.check_output([cmd, "-aux | grep \'sh -c ping -i.*"+var_IP+".*while read pong\'"]).decode('ascii')
	var_proc = subprocess.check_output(cmd, shell=True).decode('ascii')
	var_proc_table = var_proc.splitlines()
	# print(len(var_proc_table))
	# print(var_proc_table)
	# one process is always for grep search - so if there are more processes that means that means that ping is active
	if len(var_proc_table) > 2:
		return True
	else:
		return False
	
	
#------------------
def f_proc_dict2():
	IP_dict = {}
	cmd = "ps -aux | grep \'ping -i '"
	#cmd = "ps -aux | grep \'ping -i\'"
	var_proc = os.popen(cmd).read()
	var_proc_table = var_proc.split('\n')
	#print(var_proc_table)
	for i in range(len(var_proc_table)-1):
		line_list = re.split('\s+',var_proc_table[i],maxsplit=10)
						
		#if you found grep string in ps -aux it means that its not the proccess
		#we are looking for. 
		grep_string = re.compile(r'grep ')
		grep_test = grep_string.search(line_list[10])
		IP_string_long = re.findall(r'ping -i.*',line_list[10])
		#print(str(IP_string_long))
		ip_candidates = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", str(IP_string_long))
		#print(IP_string_long)
		proc_owner = line_list[0]
		proc_number = line_list[1]
		if len(ip_candidates) != 0:


		
			x = ip_candidates[0]
			if grep_test == None:
				interval = re.findall(r'ping -i \d{1,3}',str(IP_string_long))
				interval = interval[0].strip('[\'ping -i ')
				#print('2-----'+interval_2)
				#print(interval)


			#print(proc_number + '------' + proc_owner)
				key = ip_candidates[0]
				value = [proc_number, proc_owner, interval]
				if IP_dict.get(key):
					IP_dict[key].append(value)
					#print(IP_dict[key])
				else:
					IP_dict[key] = [value]		
	#print(IP_dict)
	return IP_dict		
#------------------
def f_ping_list():
	os.system('clear')
	title = 'active pings'
	options = []
	f_print_menu(title, options)

	ping_process_list = []
	#ping_process_list = f_proc_list()
	ping_process_dict = {}
	ping_process_dict, ping_process_list = f_current_ping_list_sorted()
	
	if not ping_process_dict:
		print('There are no active pings.')
	print('\n')
	#os.system('clear')
#------------------
def f_file_list():
	file_list = []
	cmd = "ls -l"
	ls_output_all = os.popen(cmd).read()
	ls_output = ls_output_all.split('\n')
	for i in range(len(ls_output)):
		file_line = re.findall(r'ping_.*\.txt',ls_output[i])
		if len(file_line) != 0:
			x = file_line[0]
			file_list.append(file_line[0])
	return file_list	
#------------------	
def f_change_options(latency,num_pings):

	#choice = input('Select your option: ')
	title = 'OPTIONS'
	options = ['Change latency threshold','Change number of pings threshold','EXIT']
	os.system('clear')
	while 1:
		os.system('clear')
		f_print_menu(title, options)
		print('Current options:\n')
		print('Latency threshold:  '.rjust(30,' ')+str(latency)+' ms')
		print('Number of pings threshold:  '.rjust(30,' ')+str(num_pings))
		print(78 * "-")	
		choice = input('Select your option: ')
		if choice == '1':
			while 1:
				var_input = input('Type latency in ms [1-999]: ')
				variable = re.match(r"^[1-9]{1}[0-9]{0,2}$", str(var_input))
				if variable:
					latency = variable.group(0)
					print('new latency'+str(latency))
					break
		elif choice == '2':
			while 1:
				var_input = input('Type number of missing pings to be found [1-99]: ')
				variable = re.match(r"^[1-9]{1,2}$", str(var_input))
				if variable:
					num_pings = variable.group(0)
					print('new num '+str(num_pings))
					break
		elif choice == '3':
			os.system('clear')
			return latency,num_pings;
		else:
			print('\nWrong option selected. Make your choice again!')
	
#------------------
def f_delete_file():
	print('DELETE FILE(s):')
	file_list = []
	file_list = f_file_list()
	os.system('clear')
	print(78 * "-")	
	print(('Select file to remove:').center(78,' '))
	print(78 * "-")		
	
	if file_list:
		for i in range(len(file_list)):
			print('  '+str(i+1)+')\t'+str(file_list[i]))
		print('  '+str(i+2)+')\tALL')
	else:
		print('No files to be deleted')
	while 1:
	
		choice = input('\nSelect your option or press \'e\' to exit: ')		
	
		if choice.isdigit() and choice != '0' and int(choice) <= len(file_list):
			var_IP_to_del = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", file_list[int(choice)-1])
			#print(var_IP_to_del[0])
			if f_proc_check(var_IP_to_del[0]):
				#print('1szy process check')
				str1 = '\"'+str(file_list[int(choice)-1])+'\"'
				str2 =' [FAILED]  - ping to '
				print('\n  deleting file   '+str1.ljust(30,' ') + str2+str(var_IP_to_del[0])+' is active!')
			else:
				cmd = 'rm '+file_list[int(choice)-1]
				os.system(cmd)
				str1 = '\"'+str(file_list[int(choice)-1])+'\"'
				str2 ='[DELETED]'
				print('\n  deleting file   '+str1.ljust(30,' ')+str2)
			
			file_list = f_file_list()
			if file_list:
				print('\nSelect file to remove:')
				for i in range(len(file_list)):
					print('  '+str(i+1)+')\t'+str(file_list[i]))
				print('  '+str(i+2)+')\tALL')
						
		elif choice.isdigit() and int(choice) == len(file_list)+1:
			for j in range(len(file_list)):
				#print(file_list[j])
				var_IP_to_del = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", file_list[j])
				#print(var_IP_to_del[0])
				time.sleep(.5)
				if f_proc_check(var_IP_to_del[0]):
				#	print('2gi process check')
					str1 = '\"'+str(file_list[j])+'\"'
					str2 =' [FAILED]  - ping to '
					print('\n  deleting file   '+str1.ljust(30,' ') + str2+str(var_IP_to_del[0])+' is active!')
				else:
					cmd = 'rm '+file_list[j]
					os.system(cmd)
					str1 = '\"'+str(file_list[j])+'\"'
					str2 = ' [DELETED]'
					print('\n  deleting file   '+str1.ljust(30,' ')	+ str2)
					
				time.sleep(0.4)
				
			file_list = f_file_list()
			if file_list:
				print('\nSelect file to remove:')
				for i in range(len(file_list)):
					print('  '+str(i+1)+')\t'+str(file_list[i]))
				print('  '+str(i+2)+')\tALL')
		elif choice == 'e':
			os.system('clear')
			break
		else:
			print('Select again:')
#----------------
def f_print_menu(title, options):
	i = 1
	print(78 * "-")	
	print((title).center(78,' '))
	print(78 * "-")	
	for option in options:
		print(' '+str(i)+'. '+option)
		i = i+1
	if len(options) == 0:
		pass
	else:
		print(78 * "-")
	return

#============ MAIN SCRIPT =============
def main():
	var_latency = '150'		# for analyzing purpose we will look for pings with higher latency than this variable
	var_num_pings = '5'		# for analyzing purpose we will look for 5 concurent ping that we are missing 	
	title = 'PingReport MENU'
	options = ['ping START','ping ANALYZE','LIST active pings','KILL active ping','DELETE ping file','OPTIONS','EXIT']
	os.system('clear')


	while 1:
	
		f_print_menu(title, options)
		
		choice = input('\nSelect your option: ')
		if choice == '1':
			f_ping_start()
		elif choice == '2':
			f_ping_analyze(var_latency, var_num_pings)
		elif choice == '3':
			f_ping_list()
		elif choice == '4':
			f_ping_kill()
		elif choice == '5':
			f_delete_file()
		elif choice == '6':
			var_latency, var_num_pings = f_change_options(var_latency,var_num_pings)			
		elif choice == '7':
			break
		else:
			print('\nWrong option selected. Make your choice again!')



#============= EXECUTION ============= 
main() 