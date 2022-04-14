from src.filas import QueueManager

class Dispatcher:
	def __init__(self):
		self.queue_manager = QueueManager()

	def readProcesses(self):
		f = open("processes.txt", "r")
		for line in f:
			params = line.split(", ")
			self.queue_manager.createProcess(int(params[0]), int(params[1]), int(params[2]), int(params[3]), int(params[4]), int(params[5]), int(params[6]), int(params[7]))

	def run(self):
		self.readProcesses()
		self.queue_manager.run()