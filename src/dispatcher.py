from src.filas import QueueManager
from src.arquivos import FileManager

# Classe responsável por ler os arquivos de texto e enviar a leitura para o gerenciador de filas.
class Dispatcher:
	def __init__(self):
		self.queue_manager = QueueManager()

	# Lê o arquivo de texto 'processes.txt' e aciona o gerenciador de fila para criar os processos com os parâmetros lidos.
	def readProcesses(self):
		f = open("processes.txt", "r")
		for line in f:
			params = line.split(", ")
			self.queue_manager.createProcess(int(params[0]), int(params[1]), int(params[2]), int(params[3]), int(params[4]), int(params[5]), int(params[6]), int(params[7]))

	# Cria os processos e inicia o gerenciador de filas.
	def run(self):
		self.readProcesses()
		self.queue_manager.run()
		file_manager = FileManager("files.txt", self.queue_manager.last_PID)
		file_manager.start()
		file_manager.stop()