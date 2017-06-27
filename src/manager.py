import time as tm
import random as rd
from memory import Memory
from process import Process
from threading import Thread, Lock

INPUT_FILE = 'randtest.txt'	### input file for execution
RAND_TIMEOUT = 30		### timeout constant for stopping random mode
process_list = {}		### processes dictionary
mutex = Lock()			### lock for random mutual exclusion
time_counter = 0		### time counter for random mode

'''
Method for running operations received by parameters.
It verifies which operation may run, and then calls its respective method.
'''
def execute_operation(operation, process, num, time):
	global ram
	global disc
	if operation == 'C':	### calls process creation method
		create_process(process, num, time)
	elif operation == 'A':	### calls memory access method
		access_memory(process, num, time)
	elif operation == 'M':	### call memory allocation method
		allocate_memory(process, num, time)
	else:
		print('Invalid operation')
'''
Starts random mode.
It starts new threads that create a new process each and then make
randomic calls for memory access and allocation.
'''
def random_mode():
	while True:
		if time_counter%(RAND_TIMEOUT//5)==0:		# verifier to create new threads less often
			t = Thread(target=create_random_access)	# instantiates and starts a new thread with a process and
			t.start()				# random accesses
			tm.sleep(1)
		if time_counter>RAND_TIMEOUT:	# stops when the counter reachs the timeout
			break
'''
Print memories status: see Memory.py for more information.
'''
def print_memories():
	global ram
	global disc
	print('##RAM##')
	ram.print_status()
	print('##Disc##')
	disc.print_status()
'''
Tries to allocate more memory for a process:
	process: name of the process to receive memory
	size: how much memory it wants to allocate
	time: current time of execution based on operations done
'''
def allocate_memory(process, size, time):
	global process_list
	p = process_list[process]	# get current process from dictionary
	pid = len(p.pagetable)		# if new pages are created, the process will have 
					# new pages which id starts at its pagetable length
	pages = ram.allocate_page(time, process, size, page_id=pid)	# tries to allocate memory, see Memory.py
	if pages is None: 						# if allocation was not successful
		print('No space to allocate for {}'.format(process))	# inform user
		if disc.is_full():			# if there are no space in disc, there are no space left
			print('Out of Memory')
			return False
		else:
			print('###Page fault###')	# if there are space in disc, dumps memory to get more space
			print('###Before###')
			print_memories()		# memory status before memory dump
			page, pageid = ram.get_page_by_method(switch_method)	# picks a page from memory
			disc.on_new_page((time,page,pageid))			# puts page in disc
			print('###After###')
			print_memories()		# memory status after memory dump
			return allocate_memory(process, size, time)		# tries to allocate memory again
	else:
		p.on_page_allocation(pages)	# if allocation was successful, update process info
		p.on_mem_allocation(size)	# reports and returns
		print('-Memory allocated to process {}. New size: {}'.format(process, p.size))
		return True
'''
Tries to access certain memory address from a process:
	process: name of the process trying to access address
	address: address number from the process to be accessed
	time: current time of execution based on operations done
'''
def access_memory(process, address, time):
	global process_list
	p = process_list[process]	# get current process from dictionary
	if p.size <= address:	# if it's trying to access an address it doesn't have, just report
		print('Segmentation fault: Process {} tried to access {}. Size: {}'.format(process, address, p.size))
	else:
		page_id = address//page_size	# the page id identifies which page from the process it's trying to access
		n_page = p.pagetable[page_id]	# gets the memory index from the pagetable of the process using the page id
						# Example: 
						# 	p.pagetable[1] == 0 means that the page 1 from the process
						#  	is the page 0 from the memory
		result = ram.access_address(process, time, n_page, page_id)	# tries to access memory address, see Memory.py
		if result is None:			# if could not access a valid address
			print('###Page fault###')	# page fault occurs
			print('{} could not access address {}'.format(process, address))
			print('###Before###')			
			print_memories()	# memory status before page fault
			disc_page = disc.get_page_by_address(process, page_id)	# gets page from disc using page id, see Memory.py
			ram_page = ram.get_page_by_method(switch_method)	# gets page from memory to switch with disc
			disc.on_new_page((time,)+ram_page)			# stores memory page in disc
			p.pagetable[page_id] = ram.on_new_page((time,)+disc_page) # stores disc page in memory, returning its memory index
			print('###After###')
			print_memories()	# memory status after page fault
			access_memory(process, address, time)	# and tries to access memory address again
		else:	# if address was accessed, reports
			print('-Process {} accessed address {} at page {}'.format(process, address, p.pagetable[page_id]))
'''
Tries to create a new process and allocate it in the memory:
	process: process name
	size: size of the process to be created
	time: current time of execution based on operations done
'''
def create_process(process, size, time):
	global process_list
	p = Process(process, size)	# creates a new process object
	pages = ram.allocate_page(time, process, size)	# tries to allocate memory for the new process
	if pages is None:				# if there was no space in memory
		print('No size to create new process with size {}'.format(size))
		if disc.is_full() and (ram.is_full() or size>ram.size-ram.mem_allocated):	# if there are no space at all
			print('Out of Memory')	# it can't create the process
			return False
		else:
			print('###Page fault###')	# if there are space, dumps memory
			print('###Before###')
			print_memories()	# memory status before page fault
			page, pageid = ram.get_page_by_method(switch_method)	# get page from memory
			disc.on_new_page((time,page,pageid))			# store page in disc
			print('###After###')
			print_memories()	# memory status after page fault
			return create_process(process, size, time)		# tries to create proccess again
	else :						# if allocated successfully
		p.pagetable = pages			# pagetable of process is created (received from allocation method)
		process_list[process] = p		# puts new process in dictionary
		print('-Process {} created. Size: {}.'.format(process, size))	# reports success and returns
		return True
'''
Tries to create a new proccess and then does multiple randomic operations.
As it's called in a thread, uses a lock to delimitate critical sections.
'''
def create_random_access():
	global mutex
	global time_counter
	name = 'p'+str(len(process_list))	# process name based on dictionary length
	ram_size = ram.size			# memory size in bytes
	size = rd.randint(1, ram_size/2)	# generates random process size between 1 and half the memory size
	with mutex:				# critical section
		created = create_process(name, size, time_counter)	# tries to create a new proccess
		time_counter = time_counter + 1				# upgrades execution time
		tm.sleep(1)	# sleep to see running better
	if not created: return						# if the process was not created, return
	while True:							# with the created process
		add = int((time_counter*time_counter*rd.random())%ram_size)	# random address based on execution time and memory size
		with mutex:			# critical section
			access_memory(name, add, time_counter)	# calls memory access method
			time_counter = time_counter + 1		# update execution time
			tm.sleep(1)
		if time_counter%10==0:				# verifier to allocate memory less often
			al_size = rd.randint(1, ram_size/2)	# random allocation size
			with mutex:		# critical section
				allocate_memory(name, al_size, time_counter)	# calls allocation method
				time_counter = time_counter + 1			# update execution time
				tm.sleep(1)
		if time_counter>RAND_TIMEOUT:	# if execution times out, stops thread
			break
		tm.sleep(1)
		
			
if __name__ == '__main__':
	with open(INPUT_FILE, 'r') as f:	# open input file in read mode
		mode = int(f.readline())	
		global switch_method
		global page_size
		global ram
		global disc
		switch_method = f.readline()[:-1]	### reads header of the input and declares variables
		page_size = int(f.readline())
		ram_size = int(f.readline())/page_size
		disc_size = int(f.readline())/page_size
		ram = Memory(page_size, ram_size)
		disc = Memory(page_size, disc_size)
		time = 0
		if switch_method != 'lru' or switch_method != 'sequential':	### verifies if switch method is valid or not
			print('Please use 'lru' or 'sequential' as memory switch method')	# requires a valid entry
			return
		### prints header information
		print('Mode: {}. Switch method: {}'.format('Sequential' if mode==0 else 'Random', switch_method))
		print('Ram size: {}. Disc size: {}'.format(ram_size*page_size,disc_size*page_size))
		print('Page size: {}'.format(page_size))
		if mode == 0:		# if mode is sequential
			while True:	# reads file
				line = f.readline()	### read new line and breaks into words
				if line == '':
					break
				ops = line.split(' ')
				op = ops[0]		### sets variables and calls execution method
				process = ops[1]
				num = int(ops[2])
				execute_operation(op, process, num, time)
				time = time + 1		### upgrade execution time for sequential mode
		elif mode == 1:		# if mode is randomic
			random_mode()	# calls random mode method
		else:			# if mode is invalid reports to user and terminates
			print('Please use 0 or 1 to select execution mode (sequential or random).')
			
