from page import Page
class Memory:

	def __init__(self, page_size, n_pages):
		self.page_size = page_size
		self.n_pages = n_pages
		self.size = n_pages*page_size
		self.pagelist = []
		self.allocated = 0
		self.mem_allocated = 0
		self.last_removed = None
		for i in range(n_pages):
			self.pagelist.append(None)
	
	def on_new_page(self, page):
		for i,p in enumerate(self.pagelist):
			if p is None:
				self.pagelist[i] = page
				self.allocated = self.allocated+1
				self.mem_allocated = self.mem_allocated+page[1].stored
				return i
		return None

	def allocate_page(self, time, process, size, page_id=0):
		if size>(self.size-self.mem_allocated):
			return None
		p_size = self.page_size
		if self.allocated == self.n_pages:
			p = Page(process, p_size, size)
			result = self.allocate_memory(process, size, time)
			if result:
				return []
			return None
		
		pages = []
		pid = page_id
		if size>=self.page_size:
			size = size - p_size
			p = Page(process, p_size, p_size)
			idx = self.on_new_page((time,p, pid))
			if idx is None: return None
			pages.append(idx)
			pid = pid + 1
			if size>0:
				aux = self.allocate_page(time, process, size, page_id=pid)
				if aux is None:
					return aux
				pages.extend(aux)
		elif size!=0:
			p = Page(process, p_size, size)
			result = self.allocate_memory(process, size, time)
			if not result:
				idx = self.on_new_page((time,p, pid))
				if idx is None: return None
				pages.append(idx)
				
		return pages
	
	def allocate_memory(self, process, size, time):
		success = False
		for i,p in enumerate(self.pagelist):
			if p is not None and p[1].process == process:
				success = p[1].allocate(size)
				if success:
					self.pagelist[i] = (time, p[1], p[2])
					break
		return success
		
	def is_full(self):
		return self.n_pages == self.allocated
	
	def get_page_by_method(self, method='lru'):
		if method=='lru':
			for i,page in enumerate(self.pagelist):
				if page is not None:
					older = page[0]
					idx = i
					break
			for i,n in enumerate(self.pagelist):
				if n is not None and n[0] < older:
					older = n[0]
					idx = i
			p = self.remove_page(idx)
			return p[1], p[2]
		elif method=='sequential':
			if self.last_removed is None:
				for i,n in enumerate(self.pagelist):
					if n is not None:
						p = self.remove_page(i)
						break
				return p[1], p[2]
			else:
				n = (self.last_removed+1)%n_pages
				self.last_removed = n
				p = self.remove_page(n)
				return p[1], p[2]
		else:
			return None
	def remove_page(self, idx):
		p = self.pagelist[idx]
		self.pagelist[idx] = None
		self.allocated = self.allocated - 1
		self.mem_allocated = self.mem_allocated - p[1].stored
		return p

	def get_page_by_address(self, process, page_id):
		for i,p in enumerate(self.pagelist):
			if p is not None  and p[1].process == process and p[2] == page_id:
				self.pagelist[i] = None
				self.allocated = self.allocated - 1
				self.mem_allocated = self.mem_allocated - p[1].stored
				return p[1], p[2]
	
	def access_address(self, process, time, page, pid):
		p = self.pagelist[page]
		if p is None:
			return None
		if p[1].process == process and p[2] == pid:
			p = (time, p[1])
			return 1
		else:
			return None

	def print_status(self):
		print('Size: {}. Allocated: {}'.format(self.size, self.mem_allocated))
		result = []
		for p in self.pagelist:
			if p is not None:
				result.append((p[1].process,p[2]))
			else:
				result.append(p)
		print(result)

