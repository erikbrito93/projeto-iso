class Process:
	def __init__(self, PID, start_time, priority, processing_time, memory_blocks, printer_code, scanner_req, modem_req, disk_code):
		self.PID = PID
		self.start_time = start_time
		self.priority = priority
		self.processing_time = processing_time
		self.memory_blocks = memory_blocks
		self.printer_code = printer_code
		self.scanner_req = scanner_req
		self.modem_req = modem_req
		self.disk_code = disk_code
		self.execution_time = 0
		self.is_finished = False

	def runInstruction(self):
		if (self.execution_time == 0):
			print ("\nP" + str(self.PID) + " STARTED")
		if (self.execution_time >= self.processing_time):
			self.is_finished = True
			print ("P" + str(self.PID) + " return SIGINT")
		else:
			self.execution_time += 1 
			print ("P" + str(self.PID) + " instruction " + str(self.execution_time))

