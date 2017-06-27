import time as tm
import random as rd
from memory import Memory
from process import Process
from threading import Thread, Lock

INPUT_FILE = 'randtest.txt'
RAND_TIMEOUT = 30
process_list = {}
mutex = Lock()
time_counter = 0

def execute_operation(operation, process, num, time):
	global ram
	global disc
	if operation == 'C':
		create_process(process, num, time)
	elif operation == 'A':
		access_memory(process, num, time)
	elif operation == 'M':
		allocate_memory(process, num, time)
	else:
		print('Invalid operation')
	
def print_memories():
	global ram
	global disc
	print('##RAM##')
	ram.print_status()
	print('##Disc##')
	disc.print_status()

def allocate_memory(process, size, time):
	global process_list
	p = process_list[process]
	pid = len(p.pagetable)
	pages = ram.allocate_page(time, process, size, page_id=pid)
	if pages is None:
		print('No space to allocate for {}'.format(process))
		if disc.is_full():
			print('Out of Memory')
			return False
		else:
			print('###Page fault###')
			print('###Before###')
			print_memories()
			page, pageid = ram.get_page_by_method(switch_method)
			disc.on_new_page((time,page,pageid))
			return allocate_memory(process, size, time)
			print('###After###')
			print_memories()
	else:
		p.on_page_allocation(pages)
		p.on_mem_allocation(size)
		print('-Memory allocated to process {}. New size: {}'.format(process, p.size))
		return True
		
	

def access_memory(process, address, time):
	global process_list
	p = process_list[process]
	if p.size <= address:
		print('Segmentation fault: Process {} tried to access {}. Size: {}'.format(process, address, p.size))
	else:
		page_id = address//page_size
		n_page = p.pagetable[page_id]
		result = ram.access_address(process, time, n_page, page_id)
		if result is None:
			print('###Page fault###')
			print('{} could not access address {}'.format(process, address))
			print('###Before###')			
			print_memories()
			disc_page = disc.get_page_by_address(process, page_id)
			ram_page = ram.get_page_by_method(switch_method)
			disc.on_new_page((time,)+ram_page)
			p.pagetable[page_id] = ram.on_new_page((time,)+disc_page)
			access_memory(process, address, time)
			print('###After###')
			print_memories()
		else:
			print('-Process {} accessed address {} at page {}'.format(process, address, p.pagetable[page_id]))
		

def create_process(process, size, time):
	global process_list
	p = Process(process, size)
	pages = ram.allocate_page(time, process, size)
	if pages is None:
		print('No size to create new process with size {}'.format(size))
		if disc.is_full() and (ram.is_full() or size>ram.size-ram.mem_allocated):
			print('Out of Memory')
			return False
		else:
			print('###Page fault###')
			print('###Before###')
			print_memories()
			page, pageid = ram.get_page_by_method(switch_method)
			disc.on_new_page((time,page,pageid))
			return create_process(process, size, time)
			print('###After###')
			print_memories()
	else :
		p.pagetable = pages
		process_list[process] = p
		print('-Process {} created. Size: {}.'.format(process, size))
		return True

def random_mode():
	while True:
		if time_counter%(RAND_TIMEOUT//5)==0:		
			t = Thread(target=create_random_access)
			t.start()
			tm.sleep(1)
		if time_counter>RAND_TIMEOUT:
			break

def create_random_access():
	global mutex
	global time_counter
	name = 'p'+str(len(process_list))
	ram_size = ram.n_pages*page_size
	size = rd.randint(1, ram_size/2)
	with mutex:
		created = create_process(name, size, time_counter)
		time_counter = time_counter + 1
		tm.sleep(1)
	if not created: return
	while True:
		add = int((time_counter*time_counter*rd.random())%ram_size)
		with mutex:
			access_memory(name, add, time_counter)
			time_counter = time_counter + 1
			tm.sleep(1)
		if time_counter%10==0:
			al_size = rd.randint(1, ram_size/2)
			with mutex:
				allocate_memory(name, al_size, time_counter)
				time_counter = time_counter + 1
				tm.sleep(1)
		if time_counter>RAND_TIMEOUT:
			break
		tm.sleep(1)
		
			
if __name__ == '__main__':
	with open(INPUT_FILE, 'r') as f:
		mode = int(f.readline())
		global switch_method
		global page_size
		global ram
		global disc
		switch_method = f.readline()[:-1]
		page_size = int(f.readline())
		ram_size = int(f.readline())/page_size
		disc_size = int(f.readline())/page_size
		ram = Memory(page_size, ram_size)
		disc = Memory(page_size, disc_size)
		time = 0
		print('Mode: {}. Switch method: {}'.format('Sequential' if mode==0 else 'Random', switch_method))
		print('Ram size: {}. Disc size: {}'.format(ram_size*page_size,disc_size*page_size))
		print('Page size: {}'.format(page_size))
		if mode == 0:		
			while True:
				line = f.readline()
				if line == '':
					break
				ops = line.split(' ')
				op = ops[0]
				process = ops[1]
				num = int(ops[2])
				execute_operation(op, process, num, time)
				time = time + 1
		elif mode == 1:
			random_mode()
		else:
			print('Please use 0 or 1 to select execution mode (sequential or random).')
			
