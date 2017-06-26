class Page:
	def __init__(self, process, size, stored):
		self.process = process
		self.size = size
		self.stored = stored
		self.free = size-stored

	def allocate(self, size):
		if self.free >= size:
			self.stored = self.stored + size
			self.free = self.free - size
			return True
		return False
