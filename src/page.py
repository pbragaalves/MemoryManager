'''
Page object for storing its owner process and how much bytes it's using.
This class is responsible only for allocating more memory after it's created.
	process: name of the process owning this page
	size: the size of the page in bytes
	stored: how much of the page size is in use
	
Author: Pedro Braga Alves
Date: Jun 27, 2017
'''
class Page:
	def __init__(self, process, size, stored):
		self.process = process
		self.size = size
		self.stored = stored
		self.free = size-stored	# bytes left to allocate
	'''
	Method for storing more bytes in the page.
	Takes a size as argument and then tries to allocate it to the page.
	Returns if it has succeeded or not.
	'''
	def allocate(self, size):
		if self.free >= size:				# if there are space to allocate
			self.stored = self.stored + size	## update stored bytes and free bytes
			self.free = self.free - size
			return True	## returns if succeeded or not
		return False
