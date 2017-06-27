'''
This system was made to simulate a Virtual Memory Manager as in arbitrary Operational Systems.
It takes as input a .txt file and simulates processes and accesses to memories in two ways: Sequential and Random.
In Sequential mode, it'll read the file line by line interpreting commands as below:
	C | A | M process size | address | size
Where:
	process: process name to be created/access memory/allocate memory
	C: Create process with name and size as specified
	A: Access address in memory with process and address as specified
	M: Allocate memory for process with specified size

In Random mode it will generate new threads that create a process each and then randomly solicitates
accesses to memory and memory allocation to this process in mutual exclusion.
The Random mode has a timeout defined in RAND_TIMEOUT variable.

The execution will deal with Page faults, segmentation faults and lack of memory.

Author: Pedro Braga Alves
Date: Jun 26, 2017
'''
import time as tm
import random as rd
from memory import Memory
from process import Process
from manager import Manager
from threading import Thread, Lock

INPUT_FILE = 'test.txt'		### input file for execution
RAND_TIMEOUT = 30		### timeout constant for stopping random mode
mutex = Lock()			### lock for random mutual exclusion
time_counter = 0		### time counter for random mode

'''
Method for running operations received by parameters.
It verifies which operation may run, and then calls its respective method.
'''
def execute_operation(operation, process, num, time):
	if operation == 'C':	### calls process creation method
		mngr.create_process(process, num, time)
	elif operation == 'A':	### calls memory access method
		mngr.access_memory(process, num, time)
	elif operation == 'M':	### call memory allocation method
		mngr.allocate_memory(process, num, time)
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
Tries to create a new proccess and then does multiple randomic operations.
As it's called in a thread, uses a lock to delimitate critical sections.
'''
def create_random_access():
	global mutex
	global time_counter
	name = 'p'+str(len(mngr.process_list))	# process name based on dictionary length
	ram_size = ram.size			# memory size in bytes
	size = rd.randint(1, ram_size/2)	# generates random process size between 1 and half the memory size
	with mutex:				# critical section
		created = mngr.create_process(name, size, time_counter)	# tries to create a new proccess
		time_counter = time_counter + 1				# upgrades execution time
		tm.sleep(1)	# sleep to see running better
	if not created: return						# if the process was not created, return
	while True:							# with the created process
		add = int((time_counter*time_counter*rd.random())%ram_size)	# random address based on execution time and memory size
		with mutex:			# critical section
			mngr.access_memory(name, add, time_counter)	# calls memory access method
			time_counter = time_counter + 1		# update execution time
			tm.sleep(1)
		if time_counter%10==0:				# verifier to allocate memory less often
			al_size = rd.randint(1, ram_size/2)	# random allocation size
			with mutex:		# critical section
				mngr.allocate_memory(name, al_size, time_counter)	# calls allocation method
				time_counter = time_counter + 1			# update execution time
				tm.sleep(1)
		if time_counter>RAND_TIMEOUT:	# if execution times out, stops thread
			break
		tm.sleep(1)
		
			
if __name__ == '__main__':
	with open(INPUT_FILE, 'r') as f:	# open input file in read mode
		mode = int(f.readline())
		switch_method = f.readline()[:-1]	### reads header of the input and declares variables
		page_size = int(f.readline())
		ram_size = int(f.readline())/page_size
		disc_size = int(f.readline())/page_size
		ram = Memory(page_size, ram_size)
		disc = Memory(page_size, disc_size)
		global mngr
		time = 0
		if switch_method != 'lru' and switch_method != 'sequential':	### verifies if switch method is valid or not
			print('Please use \'lru\' or \'sequential\' as memory switch method')	# requires a valid entry
		else:
			### prints header information
			print('Mode: {}. Switch method: {}'.format('Sequential' if mode==0 else 'Random', switch_method))
			print('Ram size: {}. Disc size: {}'.format(ram_size*page_size,disc_size*page_size))
			print('Page size: {}'.format(page_size))
			mngr = Manager(ram, disc, switch_method, page_size)	# instantiate Manager to execute tasks and manage memory
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
