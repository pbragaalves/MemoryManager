'''
Management class for dealing with Memories and Processes.
Initialized with memory objects, a switch policy and page size, it makes calls for the Memory
objects for creating processes, accessing addresses and allocating memory.
Author: Pedro Braga Alves
Date: Jun 26, 2017
'''
from process import Process
class Manager:
	def __init__(self, ram, disc, switch, psize):
		self.ram = ram
		self.disc = disc
		self.process_list = {}		# process dictionary to save Process objects by their name
		self.page_size = psize
		self.switch_method = switch
	'''
	Print memories status: see Memory.py for more information.
	'''
	def print_memories(self):
		print('##RAM##')
		self.ram.print_status()
		print('##Disc##')
		self.disc.print_status()
	'''
	Tries to allocate more memory for a process:
		process: name of the process to receive memory
		size: how much memory it wants to allocate
		time: current time of execution based on operations done
	'''
	def allocate_memory(self, process, size, time):
		p = self.process_list[process]	# get current process from dictionary
		pid = len(p.pagetable)		# if new pages are created, the process will have 
						# new pages which id starts at its pagetable length
		pages = self.ram.allocate_page(time, process, size, page_id=pid)	# tries to allocate memory, see Memory.py
		if pages is None: 						# if allocation was not successful
			print('No space to allocate for {}'.format(process))	# inform user
			if self.disc.is_full():			# if there are no space in disc, there are no space left
				print('Out of Memory')
				return False
			else:
				print('###Page fault###')	# if there are space in disc, dumps memory to get more space
				print('###Before###')
				self.print_memories()		# memory status before memory dump
				page, pageid = self.ram.get_page_by_method(self.switch_method)	# picks a page from memory
				self.disc.on_new_page((time,page,pageid))			# puts page in disc
				print('###After###')
				self.print_memories()		# memory status after memory dump
				return self.allocate_memory(process, size, time)		# tries to allocate memory again
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
	def access_memory(self, process, address, time):
		p = self.process_list[process]	# get current process from dictionary
		if p.size <= address:	# if it's trying to access an address it doesn't have, just report
			print('Segmentation fault: Process {} tried to access {}. Size: {}'.format(process, address, p.size))
		else:
			page_id = address//self.page_size	# the page id identifies which page from the process it's trying to access
			n_page = p.pagetable[page_id]	# gets the memory index from the pagetable of the process using the page id
							# Example: 
							# 	p.pagetable[1] == 0 means that the page 1 from the process
							#  	is the page 0 from the memory
			result = self.ram.access_address(process, time, n_page, page_id)	# tries to access memory address, see Memory.py
			if result is None:			# if could not access a valid address
				print('###Page fault###')	# page fault occurs
				print('{} could not access address {}'.format(process, address))
				print('###Before###')			
				self.print_memories()	# memory status before page fault
				disc_page = self.disc.get_page_by_address(process, page_id)	# gets page from disc using page id, see Memory.py
				ram_page = self.ram.get_page_by_method(self.switch_method)	# gets page from memory to switch with disc
				self.disc.on_new_page((time,)+ram_page)			# stores memory page in disc
				p.pagetable[page_id] = self.ram.on_new_page((time,)+disc_page) # stores disc page in memory, returning its memory index
				print('###After###')
				self.print_memories()	# memory status after page fault
				self.access_memory(process, address, time)	# and tries to access memory address again
			else:	# if address was accessed, reports
				print('-Process {} accessed address {} at page {}'.format(process, address, p.pagetable[page_id]))
	'''
	Tries to create a new process and allocate it in the memory:
		process: process name
		size: size of the process to be created
		time: current time of execution based on operations done
	'''
	def create_process(self, process, size, time):
		p = Process(process, size)	# creates a new process object
		pages = self.ram.allocate_page(time, process, size)	# tries to allocate memory for the new process
		if pages is None:				# if there was no space in memory
			print('No size to create new process with size {}'.format(size))
			if self.disc.is_full() and (self.ram.is_full() or size>self.ram.size-self.ram.mem_allocated):	# if there are no space at all
				print('Out of Memory')	# it can't create the process
				return False
			else:
				print('###Page fault###')	# if there are space, dumps memory
				print('###Before###')
				self.print_memories()	# memory status before page fault
				page, pageid = self.ram.get_page_by_method(self.switch_method)	# get page from memory
				self.disc.on_new_page((time,page,pageid))			# store page in disc
				print('###After###')
				self.print_memories()	# memory status after page fault
				return self.create_process(process, size, time)		# tries to create proccess again
		else :						# if allocated successfully
			p.pagetable = pages			# pagetable of process is created (received from allocation method)
			self.process_list[process] = p		# puts new process in dictionary
			print('-Process {} created. Size: {}.'.format(process, size))	# reports success and returns
			return True
