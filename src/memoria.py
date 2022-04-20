# Classe responsável por alocar, liberar e verificar se há memória disponível para que processos possam ser enfileirados.
class MemoryManager:
	def __init__(self):
		self.real_time_memory = 64
		self.user_memory = 960
		self.user_memory_offset = 64
		self.waiting_processes = []

	# Aloca memória para um processo de acordo com sua prioridade.
	# Retorna -1 caso não haja memória disponível para aquele processo.
	# Se for um processo de usuário, retorna o offset daquele processo caso a alocação seja bem sucedida.
	def allocateMemory(self, process):
		if (process.priority == 0):
			if (process.memory_blocks <= self.real_time_memory):
				if (process.PID in self.waiting_processes):
					self.waiting_processes.remove(process.PID)
				self.real_time_memory -= process.memory_blocks
				return 0
			else:
				if (process.PID not in self.waiting_processes):
					print ("\n\tProcesso " + str(process.PID) + " em espera por falta de memória.")
					self.waiting_processes.append(process.PID)
				return -1
		else:
			if (process.memory_blocks <= self.user_memory):
				if (process.PID in self.waiting_processes):
					self.waiting_processes.remove(process.PID)
				self.user_memory -= process.memory_blocks
				self.user_memory_offset += process.memory_blocks
				return self.user_memory_offset - process.memory_blocks
			else:
				if (process.PID not in self.waiting_processes):
					print ("\n\tProcesso " + str(process.PID) + " em espera por falta de memória.")
					self.waiting_processes.append(process.PID)
				return -1

	# Libera a memória alocada para um determinado processo, de acordo com sua prioridade. 
	def freeMemory(self, process):
		if (process.priority == 0):
			self.real_time_memory += process.memory_blocks
		else:
			self.user_memory += process.memory_blocks
			self.user_memory_offset -= process.memory_blocks
