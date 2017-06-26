class Process:
	def __init__(self, name, size):
		self.name = name
		self.size = size
		self.pagetable = []
		
	def on_page_allocation(self, idx_list):
		self.pagetable.extend(idx_list)
	
	def on_mem_allocation(self, size):
		self.size = self.size + size
