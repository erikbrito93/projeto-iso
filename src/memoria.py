# Classe responsável por alocar, liberar e verificar se há memória disponível para que processos possam ser enfileirados.
class MemoryManager:
	def __init__(self):
		self.real_time_memory = 64
		self.user_memory = 960
		self.user_memory_offset = 64

	# Aloca memória para um processo de acordo com sua prioridade.
	# Retorna -1 caso não haja memória disponível para aquele processo.
	# Se for um processo de usuário, retorna o offset daquele processo caso a alocação seja bem sucedida.
	def allocateMemory(self, process):
		if (process.priority == 0):
			if (process.memory_blocks <= self.real_time_memory):
				self.real_time_memory -= process.memory_blocks
				return 0
			else:
				return -1
		else:
			if (process.memory_blocks <= self.user_memory):
				self.user_memory -= process.memory_blocks
				self.user_memory_offset += process.memory_blocks
				return self.user_memory_offset - process.memory_blocks
			else:
				return -1

	# Libera a memória alocada para um determinado processo, de acordo com sua prioridade. 
	def freeMemory(self, process):
	if (process.priority == 0):
		self.real_time_memory += process.memory_blocks
	else:
		self.user_memory += process.memory_blocks
		self.user_memory_offset -= process.memory_blocks
