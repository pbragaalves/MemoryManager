'''
This class represents an arbitrary memory, it's used to instantiate RAM and Disc.
It takes as input the page size and the number of pages in the memory, and stores
its total size, initialize a list of pages and how much memory is allocated (in pages or bytes).
The list of pages starts with a None type for each position, and therefore replaced by a tuple
that represents a page.

Each page is represented by a tuple (time, page, page_id):
	time: the time of execution that the page was last accessed
	page: an Page object, see Page.py
	page_id: the index of the page stored by its process 
		(a page_id=1 for a process p means that this page is the page 1 in p's pagetable)
The Memory class is responsible for creating, adding, removing and accesing pages.
The None types returned by this class are dealed by the Manager as a Page fault.

Author: Pedro Braga Alves
Date: Jun 27, 2017
'''
from page import Page
class Memory:

	def __init__(self, page_size, n_pages):		# initialize Memory with a page size and number of pages
		self.page_size = page_size		
		self.n_pages = n_pages
		self.size = n_pages*page_size		# stores total size in bytes 
		self.pagelist = []			# initialize an empty list of pages
		self.allocated = 0			# total of pages stored in memory
		self.mem_allocated = 0			# total of memory allocated in bytes
		self.last_removed = None		# the index of the last page removed (for sequential method purposes)
		for i in range(n_pages):		# initialize the empty list of pages with None types
			self.pagelist.append(None)
	'''
	Allocate a new page in memory, searching for an empty slot and updating attributes.
	Returns the index of the page allocated if successful, or a Nonetype object otherwise.
	'''
	def on_new_page(self, page):
		for i,p in enumerate(self.pagelist):	# for each page in list
			if p is None:			# if the page is None (slot is empty)
				self.pagelist[i] = page	# new page is allocated
				self.allocated = self.allocated+1			### update allocated pages and
				self.mem_allocated = self.mem_allocated+page[1].stored	### size in bytes
				return i		# returns new page's index
		return None				# if there was no space for a new page, page fault
	'''
	Method that takes page arguments, verifies for space in memory and allocates a new Page object.
	Returns a list of indexes of pages allocated when successful, or a Nonetype object otherwise.
	'''
	def allocate_page(self, time, process, size, page_id=0):
		if size>(self.size-self.mem_allocated):	# if there are no size in bytes available
			return None			# page fault
		p_size = self.page_size
		if self.allocated == self.n_pages:	# if there are no space for new pages
			p = Page(process, p_size, size)	# creates a new Page object
			result = self.allocate_memory(process, size, time)	### tries to allocate more memory for
			if result:						### the process instead of a new page
				return []					### if memory was allocated, return no indexes
			return None						### otherwise, page fault
		
		pages = []	# initialize a list of page indexes
		pid = page_id
		if size>=self.page_size:	# if the memory size needed is greater or equal to one page
			size = size - p_size	# subtracts one page of the memory needed
			p = Page(process, p_size, p_size)	# creates new Page fully stored
			idx = self.on_new_page((time,p, pid))	# tries to allocate the new page in memory
			if idx is None: return None		# if there was no free slot, page fault
			pages.append(idx)			# appends page index to list otherwise
			pid = pid + 1				# increments relative page id
			if size>0:				# if there are memory needed left
				aux = self.allocate_page(time, process, size, page_id=pid)	# recursively allocates more pages
				if aux is None:		# if couldn't allocate, page fault
					return aux	
				pages.extend(aux)	# otherwise appends the indexes returned
		elif size!=0:				# if the memory needed is less than one page
			result = self.allocate_memory(process, size, time)	# tries to allocate memory in existing pages
			if not result:						# if couldn't allocate
				p = Page(process, p_size, size)	# creates a Page with the size left
				idx = self.on_new_page((time,p, pid))	# tries to allocate the new Page
				if idx is None: return None		# if couldn't, page fault
				pages.append(idx)			# if allocated, appends page index
		return pages	# return list of page indexes
	'''
	Method for allocating memory for a process that already has pages stored.
	Searches for a page owned by certain process and then tries to allocate more memory in it.
	Returns True in success and False otherwise
	'''
	def allocate_memory(self, process, size, time):
		success = False	
		for i,p in enumerate(self.pagelist):			# for each page slot in memory
			if p is not None and p[1].process == process:	# if there are a page stored owned by process
				success = p[1].allocate(size)		# tries to allocate memory in this page
				if success:				# if succeeded, update tuple in list of pages
					self.pagelist[i] = (time, p[1], p[2])
					break				# and breaks the loop
		return success						# returns if succeeded or not
	'''
	Self-explaining method, returns if memory has pages left to store.
	'''
	def is_full(self):
		return self.n_pages == self.allocated
	'''
	Removes and returns a page based on its selected method.
	Deault is Least Recent Used, and the other option is a sequential method.
	The sequential method iterates through the page list getting the first valid page
	next to the last index removed.
	'''
	def get_page_by_method(self, method='lru'):
		if method=='lru':				### if the method is lru
			for i,page in enumerate(self.pagelist):	# for each page in list
				if page is not None:		# if there are a valid page in slot
					older = page[0]		# initialize the older page with the execution time of it
					idx = i			# stores its index
					break			# break the loop
			for i,n in enumerate(self.pagelist):		# for each page in list
				if n is not None and n[0] < older:	# if the page is valid and it was accessed before
					older = n[0]		 	# this page is the new older page
					idx = i				# stores its index
			p = self.remove_page(idx)	# remove the page from memory
			return p[1], p[2]		# return its Page object and page id
		elif method=='sequential':			### if the method is sequential
			if self.last_removed is None:			# if there wasn't a last removed index
				for i,n in enumerate(self.pagelist):	# for each page in list
					if n is not None:		# if it's a valid page
						p = self.remove_page(i)	# remove page
						break			# break loop
				return p[1], p[2]			# returns Page and page id
			else:						# if there was a last removed index
				n = (self.last_removed+1)%n_pages	# takes the next index
				self.last_removed = n			# stores the new last removed
				p = self.remove_page(n)			# remove page from memory
				return p[1], p[2]			# return Page and page id
		else:			# if invalid method, returns None (it should not occur)
			return None
	'''
	Simply remove a page from memory by its index.
	Returns the page removed.
	'''
	def remove_page(self, idx):
		p = self.pagelist[idx]		# gets the page from list
		self.pagelist[idx] = None	# sets its slot to None
		self.allocated = self.allocated - 1			### updates memory allocated
		self.mem_allocated = self.mem_allocated - p[1].stored
		return p			# returns removed page
	'''
	Removes and returns page by its name and page id.
	'''
	def get_page_by_address(self, process, page_id):
		for i,p in enumerate(self.pagelist):		# for each page in list
			if p is not None  and p[1].process == process and p[2] == page_id:
				p = self.remove_page(i)		### if its the page we're looking for
				return p[1], p[2]		### removes and returns
	'''
	Tries to access some page in memory, if the page isn't there, returns page fault.
	'''
	def access_address(self, process, time, page, pid):
		p = self.pagelist[page]	# gets page by index
		if p is None:		# if there are no page, it's page fault
			return None
		if p[1].process == process and p[2] == pid:	### if the page is the page we're looking for
			self.pagelist[page] = (time, p[1], p[2])### update the execution time for last accessed 
			return 1				### returns
		else:			# otherwise, page fault
			return None
	'''
	Prints Memory status on screen.
	Lists its size and memory allocated in bytes, and the list of pages
	without the last execution time accessed for each.
	'''
	def print_status(self):
		print('Size: {}. Allocated: {}'.format(self.size, self.mem_allocated))
		result = []
		for p in self.pagelist:				### loops through the page list getting only the
			if p is not None:			### useful info for printing
				result.append((p[1].process,p[2]))
			else:
				result.append(p)
		print(result)
