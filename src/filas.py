from src.processos import Process
from src.memoria import MemoryManager
from src.recursos import ResourceManager
import queue

# Classe responsável por criar processos e também inseri-los nas filas de execução quando estes estão aptos.
class QueueManager:
	# Inicializa as filas de execução e também cria os gerenciadores auxiliares.
	def __init__(self):
		self.memory_manager = MemoryManager()
		self.resource_manager = ResourceManager()
		self.processes = []
		self.real_time_processes = queue.Queue(1000)
		self.user_processes = queue.Queue(1000)
		self.user_processes1 = queue.Queue(1000)
		self.user_processes2 = queue.Queue(1000)
		self.user_processes3 = queue.Queue(1000)
		self.current_process = {}
		self._last_PID = 0
		self.is_finished = False
		self.quantum = 5

	@property
	def last_PID(self) -> int:
		return self._last_PID
	
	# Cria um processo com os parâmetros dados, dando a cada um um número de PID único.
	def createProcess(self, start_time, priority, processing_time, memory_blocks, printer_code, scanner_req, modem_req, driver_code):
		self._last_PID += 1
		newProcess = Process(self.last_PID, start_time, priority, processing_time, memory_blocks, printer_code, scanner_req, modem_req, driver_code)
		self.processes.append(newProcess)

	# Ordena os processos criados (lidos do arquivo) por tempo de chegada e depois por prioridade
	def orderProcesses(self):
		self.processes.sort(key=lambda process: (process.start_time, process.priority))

	# Anuncia a inserção de um processo nas filas de execução.
	def announceProcess(self, process):
		print("\nProcess created:")
		print("PID: " + str(process.PID))
		print("Priority: " + str(process.priority))
		print("Processing Time: " + str(process.processing_time))
		print("Offset: " + str(process.memory_offset))
		print("Memory Blocks: " + str(process.memory_blocks))
		print("Printers: " + str(process.printer_code))
		print("Scanners: " + str(process.scanner_req))
		print("Modems: " + str(process.modem_req))
		print("Drivers: " + str(process.driver_code) + "\n")

	# Tenta enfileirar o processo na posição 'position' da lista de processos criados na fila de prioridade correspondente.
	# O processo só será enfileirado se:
	# - Seu tempo de chegada já tiver ocorrido.
	# - Houver memória suficiente para alocação.
	# - Os recursos que o processo utilizará estiverem livres.
	def enqueueProcesses(self, time, position = 0):
		enqueued = False
		if (len(self.processes) > position):
			# Enfileirar processos em tempo real
			if (self.processes[position].priority == 0 and time >= self.processes[position].start_time):
				if (self.processes[position].PID in self.memory_manager.waiting_processes):
					if (self.memory_manager.allocateMemory(self.processes[position]) != -1):
						if (self.resource_manager.scanProcess(self.processes[position]) == 0):	
							enqueued = True	
						else:
							self.memory_manager.freeMemory(self.processes[position])			
				elif (self.resource_manager.scanProcess(self.processes[position]) == 0):
					if (self.memory_manager.allocateMemory(self.processes[position]) != -1):
						enqueued = True
					else:
						self.resource_manager.releaseResources(self.processes[position])
				if enqueued:
					self.announceProcess(self.processes[position])
					self.real_time_processes.put(self.processes.pop(position))
				
			# Enfileirar processos de usuário
			elif (time >= self.processes[position].start_time):
				memory_offset = 0
				if (self.processes[position].PID in self.memory_manager.waiting_processes):
					memory_offset = self.memory_manager.allocateMemory(self.processes[position])
					if (memory_offset != -1):
						if (self.resource_manager.scanProcess(self.processes[position]) == 0):	
							enqueued = True				
						else:
							self.memory_manager.freeMemory(self.processes[position])
				elif (self.resource_manager.scanProcess(self.processes[position]) == 0):
					memory_offset = self.memory_manager.allocateMemory(self.processes[position])
					if (memory_offset != -1):
						enqueued = True
					else:
						self.resource_manager.releaseResources(self.processes[position])
				if enqueued: 
					self.processes[position].memory_offset = memory_offset
					self.announceProcess(self.processes[position])
					self.user_processes.put(self.processes.pop(position))
						
		# Aqui é verificado se o próximo processo na lista também está pronto para ser enfileirado.
		# Caso positivo, abrimos uma nova recursão para enfileirá-lo.
		if (len(self.processes) > position):
			if (enqueued):
				if (time >= self.processes[position].start_time):
					self.enqueueProcesses(time, position)
			elif (len(self.processes) > position + 1):
				if (time >= self.processes[position + 1].start_time):
					self.enqueueProcesses(time, position + 1)
		
		# Percorrendo a fila de processos de usuário para dividir os processos nas filas de diferentes prioridades.
		while (not self.user_processes.empty()):
			process_to_enqueue = self.user_processes.get()
			if (process_to_enqueue.priority == 1):
				self.user_processes1.put(process_to_enqueue)
			elif (process_to_enqueue.priority == 2):
				self.user_processes2.put(process_to_enqueue)
			elif (process_to_enqueue.priority == 3):
				self.user_processes3.put(process_to_enqueue)

	# Execução do loop do gerenciador de filas.
	# Em cada loop, fazemos:
	# 1) Enfileiramos os processos prontos de acordo com o tempo atual e recursos disponíveis.
	# 2) Verificamos se um processo de usuário deve ser interrompido por um processo de prioridade em tempo real.
	# 3) Caso não haja processos ocupando a CPU, tira um processo da fila de maior prioridade para ocupá-la.
	# 4) Executamos uma instrução do processo que ocupa a CPU atualmente.
	# 5) Caso o processo se encerre, liberamos a memória alocada para ele.
	# 6) Verificamos se o processo deve ser interrompido pelo quantum definido (5 instruções)
	# 7) Caso positivo, mudamos a sua prioridade para um nível abaixo.
	# 8) O loop se encerra quando todas as filas estão vazias e não há mais processos ocupando a CPU.
	def run(self):
		self.orderProcesses()
		time = 0
		while (not self.is_finished):
			# 1) Enfileiramos os processos prontos de acordo com o tempo atual e recursos disponíveis.
			self.enqueueProcesses(time)
			
			# 2) Verificamos se um processo de usuário deve ser interrompido por um processo de prioridade em tempo real.
			if (not self.real_time_processes.empty() and self.current_process != {}):
				if (self.current_process.priority > 0):
					self.user_processes.put(self.current_process)
					self.current_process = {}
					print (" ")
			
			# 3) Caso não haja processos ocupando a CPU, tira um processo da fila de maior prioridade para ocupá-la.
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
				# 4) Executamos uma instrução do processo que ocupa a CPU atualmente.
				if (time >= self.current_process.start_time):
					self.current_process.runInstruction()
					self.current_process.current_execution_time += 1
	
				# 5) Caso o processo se encerre, liberamos a memória alocada para ele.
				if (self.current_process.is_finished):
					self.memory_manager.freeMemory(self.current_process)
					self.resource_manager.releaseResources(self.current_process)
					self.current_process = {}
					print (" ")

				# 6) Verificamos se o processo deve ser interrompido pelo quantum definido (5 instruções)
				elif (self.current_process.current_execution_time >= self.quantum and self.current_process.priority > 0):
					if (self.current_process.priority < 3):
						self.current_process.priority += 1
					self.current_process.current_execution_time = 0
					self.user_processes.put(self.current_process)
					self.current_process = {}
					print (" ")
					
			# 8) O loop se encerra quando todas as filas estão vazias e não há mais processos ocupando a CPU.
			if (len(self.processes) == 0 and self.real_time_processes.empty() and self.user_processes.empty() and self.user_processes1.empty() and self.user_processes2.empty() and self.user_processes3.empty() and self.current_process == {}):
				self.is_finished = True
			time += 1



