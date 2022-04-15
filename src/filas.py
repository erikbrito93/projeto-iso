from src.processos import Process
import queue

class QueueManager:
	def __init__(self):
		self.processes = []
		self.ready_processes = queue.Queue(1000)
		self.real_time_processes = queue.Queue(1000)
		self.user_processes = queue.Queue(1000)
		self.user_processes1 = queue.Queue(1000)
		self.user_processes2 = queue.Queue(1000)
		self.user_processes3 = queue.Queue(1000)
		self.current_process = {}
		self.last_PID = 0
		self.is_finished = False
		self.quantum = 5

	def createProcess(self, start_time, priority, processing_time, memory_blocks, printer_code, scanner_req, modem_req, driver_code):
		self.last_PID += 1
		newProcess = Process(self.last_PID, start_time, priority, processing_time, memory_blocks, printer_code, scanner_req, modem_req, driver_code)
		self.processes.append(newProcess)

	def orderProcesses(self):
		self.processes.sort(key=lambda process: process.start_time)

	def announceProcess(self, process):
		print("\nProcess created:")
		print("PID: " + str(process.PID))
		print("Priority: " + str(process.priority))
		print("Processing Time: " + str(process.processing_time))
		print("Offset: 0")
		print("Memory Blocks: " + str(process.memory_blocks))
		print("Printers: " + str(process.printer_code))
		print("Scanners: " + str(process.scanner_req))
		print("Modems: " + str(process.modem_req))
		print("Drivers: " + str(process.driver_code))
		print ("\n")

	def enqueueProcesses(self, time):
		if (len(self.processes) > 0):
			process_to_enqueue = self.processes[0]
			if (process_to_enqueue.priority == 0 and time >= process_to_enqueue.start_time):
				self.real_time_processes.put(self.processes.pop(0))
				self.announceProcess(process_to_enqueue)
			elif (time >= process_to_enqueue.start_time):
				self.user_processes.put(self.processes.pop(0))
				self.announceProcess(process_to_enqueue)
		
		if (len(self.processes) > 0):
			if (self.processes[0].start_time == time):
				self.enqueueProcesses(time)

		while (not self.user_processes.empty()):
			process_to_enqueue = self.user_processes.get()
			if (process_to_enqueue.priority == 1):
				self.user_processes1.put(process_to_enqueue)
			elif (process_to_enqueue.priority == 2):
				self.user_processes2.put(process_to_enqueue)
			elif (process_to_enqueue.priority == 3):
				self.user_processes3.put(process_to_enqueue)

	def run(self):
		self.orderProcesses()
		time = 0
		while (not self.is_finished):
			self.enqueueProcesses(time)
			
			if (not self.real_time_processes.empty() and self.current_process != {}):
				if (self.current_process.priority > 0):
					self.user_processes.put(self.current_process)
					self.current_process = {}
					print ("\n")

			if (self.current_process == {}):
				if (not self.real_time_processes.empty()):
					self.current_process = self.real_time_processes.get()
				elif (not self.user_processes1.empty()):	
					self.current_process = self.user_processes1.get()
				elif (not self.user_processes2.empty()):	
					self.current_process = self.user_processes2.get()
				elif (not self.user_processes3.empty()):	
					self.current_process = self.user_processes3.get()

			if (self.current_process != {}):			
				if (time >= self.current_process.start_time):
					self.current_process.runInstruction()
					self.current_process.current_execution_time += 1

				if (self.current_process.is_finished):
					self.current_process = {}
					print ("\n")
				elif (self.current_process.current_execution_time >= self.quantum and self.current_process.priority > 0):
					if (self.current_process.priority < 3):
						self.current_process.priority += 1
					self.current_process.current_execution_time = 0
					self.user_processes.put(self.current_process)
					self.current_process = {}
					print ("\n")

			if (len(self.processes) == 0 and self.real_time_processes.empty() and self.user_processes1.empty() and self.user_processes2.empty() and self.user_processes3.empty() and self.current_process == {}):
				self.is_finished = True
			time += 1



