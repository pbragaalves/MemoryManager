'''
Process object responsible to represent an active process.
Stores a name to call the process and its size in bytes.
Maintains a page table that stores the indexes of its pages in memory.
	Ex: pagetable[1]==0 means that the page 1 from 
	this process is at position 0 in memory
The object deals with pages and memory allocated to it.

Author: Pedro Braga Alves
Date: Jun 27, 2017
'''
class Process:
	def __init__(self, name, size):
		self.name = name
		self.size = size
		self.pagetable = []	# initialize page table
	'''
	Method for storing new page indexes
	'''
	def on_page_allocation(self, idx_list):
		self.pagetable.extend(idx_list)
	'''
	Method for updating its size in bytes
	'''
	def on_mem_allocation(self, size):
		self.size = self.size + size
