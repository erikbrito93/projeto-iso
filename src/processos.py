class Process:
	def __init__(self, PID, start_time, priority, processing_time, memory_blocks, printer_code, scanner_req, modem_req, driver_code):
		self.PID = PID
		self.start_time = start_time
		self.priority = priority
		self.processing_time = processing_time
		self.memory_blocks = memory_blocks
		self.memory_offset = 0
		self.printer_code = printer_code
		self.scanner_req = scanner_req
		self.modem_req = modem_req
		self.driver_code = driver_code
		self.execution_time = 0
		self.is_finished = False
		self.current_execution_time = 0

	@property
	def printer_code(self) -> int:
		return self.printer_code

	@property
	def scanner_req(self) -> int:
		return self.scanner_req
	
	@property
	def modem_req(self) -> int:
		return self.modem_req
	
	@property
	def driver_code(self) -> int:
		return self.driver_code

	def runInstruction(self):
		if (self.execution_time == 0):
			print ("P" + str(self.PID) + " STARTED")
		if (self.execution_time < self.processing_time):
			self.execution_time += 1 
			print ("P" + str(self.PID) + " instruction " + str(self.execution_time))			
		if (self.execution_time >= self.processing_time):
			self.is_finished = True
			print ("P" + str(self.PID) + " return SIGINT")
