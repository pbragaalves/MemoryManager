import Memory, Process

INPUT_FILE = 'teste.txt'
process_list = {}


def execute_operation(self, operation, process, num, time):
	global ram
	global disc
	if operation == 'C':
		self.create_process(process, num, time)
	elif operation == 'A':
		self.access_memory(process, num, time)
	elif operation == 'M':
		self.allocate_memory(process, num, time)
	else:
		print('Invalid operation')
	
def print_memories(self):
	global ram
	global disc
	print('RAM:')
	ram.print_status()
	print('Disc:')
	disc.print_status()

def allocate_memory(self, process, size, time):
	p = process_list[process]
	pid = len(p.pagetable)-1
	pages = ram.allocate_page(process, size, time)
	if pages is None:
		print('Page fault')
		self.print_memories()
		if disc.is_full():
			print('Out of Memory')
		else:
			page, pageid = ram.get_page_by_method(switch_method)
			disc.on_new_page((time,page,pageid))
			allocate_memory(process, size, time)
	else:
		p.on_page_allocation(pages)
		p.on_mem_allocation(size)
		print('Memory allocated to process {}. New size: {}'.format(process, p.size))
		
	

def access_memory(self, process, address, time):
	p = process_list[process]
	if p.size < address:
		print('Segmentation fault: Process {} tried to access {}. Size: {}'.format(process, adrress, p.size))
	else:
		page_id = address/page_size
		n_page = p.pagetable[page_id]
		result = ram.access_address(process, time, n_page)
		if result is None:
			print('Page fault')
			self.print_memories()
			disc_page = disc.get_page_by_address(process, page_id)
			ram_page = ram.get_page_by_method(switch_method)
			disc.on_new_page((time,ram_page, page_id))
			p.pagetable[page_id] = ram.on_new_page((time, disc_page,page_id))
			self.access_memory(process, address, time)
		else:
			print('Process {} accessed address {} at page {}'.format(process, address, p.pagetable[page_id]))
		

def create_process(self, process, size, time):
	p = Process(process, num)
	pages = ram.allocate_page(time, process, num)
	if pages is None:
		print('Page fault')
		self.print_memories()
		if disc.is_full():
			print('Out of Memory')
		else:
			page, pageid = ram.get_page_by_method(switch_method)
			disc.on_new_page((time,page,pageid))
			create_process(process, size, time)
	else :
		p.pagetable = pages
		process_list[process] = p
		print('Process {} created. Size: {}.'.format(process, size))
		self.print_memories()
			
if __name__ == '__main__':
	with open(INPUT_FILE, 'r') as f:
		mode = f.readline()
		global switch_method
		global page_size
		global ram
		global disc
		switch_method = f.readline()
		page_size = int(f.readline())
		ram_size = int(f.readline())/page_size
		disc_size = int(f.readline())/page_size
		
		ram = Memory(page_size, ram_size)
		disc = Memory(page_size, disc_size)
		time = 0
		if mode == 0:		
			while True:
				line = f.readline()
				if line == '':
					break
				ops = line.split(' ')
				op = ops[0]
				process = ops[1]
				num = ops[2]
				self.execute_operation(op, process, num, time)
				time = time + 1
