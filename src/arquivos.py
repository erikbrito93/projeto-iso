from os.path import isfile
from time import sleep
from threading import Thread

class FileManager(object):
    """Gerencia os sistema de arquivos do pseudo S.O."""

    def __init__(self, storage_file: str, PIDs):
        if not isfile(storage_file):
            raise StorageFileNotFound("Arquivo de armazenamento %s não encontrado!" % storage_file)

        self.storage_file = storage_file
        self.PIDs_of_processes = PIDs
        self.total_blocks = None # Quantidade total de blocos do sistema de arquivos
        self.n_occupied_segments = None # Quantide de arquivos escritos
        self.occupied_segments = None # Informação dos arquivos escritos conforme tupla (PID, bloco inicial, quantidade de blocos)
        self.occupied_blocks_map = None # Mapeamento do uso de disco
        self.file_operations = None # Operações de arquivo a serem executadas
        self.has_pending_ops = False # Controle de informação de existência de operações pendentes
        self.is_running_ops = False # Controle de status de execução de operações em disco
        self.thread_alive = False # Controle de execução da thread
        self.thread = Thread(target=self.run) # Thread da execução do gerenciamento de arquivos
    
    def __del__(self):
        self.printStorageMap()


    def start(self):
        """Inicia a execução do gerenciador de arquivos."""

        self.thread_alive = True
        self.readStorageFile()
        self.thread.start()


    def stop(self):
        """Termina a execução do gerenciador de arquivos."""

        self.thread_alive = False
        self.thread.join()

    
    def createFile(self, pid: int, file_name: str, n_blocks: int) -> bool:
        """Cria um novo arquivo no armazenamento do sistema.
            Args:
                pid: identificador do processo que solicitou a operação
                file_name: nome do arquivo a ser criado
                n_blocks: quantidade de blocos ocupados pelo arquivo

            Returns:
                booleano conforme sucesso da operação
        """

        while self.has_pending_ops or self.is_running_ops:
            sleep(0.01)

        self.readStorageFile()

        file_names = [s[0] for s in self.occupied_segments]

        if file_name in file_names:
            print("O processo %s não pode criar o arquivo %s (nome já existente)." % (pid, file_name))
            return False
        
        with open(self.storage_file, "at") as f:
            f.write("\n%s, 0, %s, %s" % (pid, file_name, n_blocks))

        self.has_pending_ops = True

        return True


    def deleteFile(self, pid: int, file_name: str) -> bool:
        """Deleta um arquivo existente no armazenamento do sistema.
            Args:
                pid: identificador do processo que solicitou a operação
                file_name: nome do arquivo a ser deletado

            Returns:
                booleano conforme sucesso da operação
        """

        while self.has_pending_ops or self.is_running_ops:
            sleep(0.01)

        self.readStorageFile()

        file_names = [s[0] for s in self.occupied_segments]

        if file_name not in file_names:
            print("O processo %s não pode deletar o arquivo %s (nome inexistente)." % (pid, file_name))
            return False

        with open(self.storage_file, "at") as f:
            f.write("\n%s, 1, %s" % (pid, file_name))

        self.has_pending_ops = True
        
        return True

    
    def run(self):
        """Controla o fluxo da execução do gerenciador de arquivos."""

        while self.thread_alive:
            if self.has_pending_ops and not self.is_running_ops:
                self.runFileOperations()
            else:
                sleep(0.01)


    def readStorageFile(self):
        """Realiza a leitura das informações do sistema de arquivo salvas em disco."""

        with open(self.storage_file, "rt") as f:
            lines = f.readlines()
        
        # Leitura de algumas informações do sistema de arquivo e inicialização de listas vazias
        self.total_blocks = int(lines[0])
        self.n_occupied_segments = int(lines[1])
        self.occupied_segments = []
        self.occupied_blocks_map = [0 for _ in range(self.total_blocks)]
        self.file_operations = []

        # Leitura da informação detalhada dos segmentos ocupados
        for l in lines[2 : (2 + self.n_occupied_segments)]:
            segment_info = [i.strip() for i in l.split(", ")]
            self.occupied_segments.append(segment_info)

        # Mapeamento do uso de blocos do sistema de arquivo
        for s in self.occupied_segments:
            file_name = s[0]
            initial_block = int(s[1]) 
            n_blocks = int(s[2])

            for i in range(n_blocks):
                self.occupied_blocks_map[i + initial_block] = file_name

        # Leitura das operações de arquivo a serem realizadas
        for l in lines[2 + self.n_occupied_segments:]:
            operation_info = [i.strip() for i in l.split(", ")]
            self.file_operations.append(operation_info)
            self.has_pending_ops = True


    def writeStorageFile(self):
        """Realiza a escrita das informações do sistema de arquivo em disco."""
        
        with open(self.storage_file, "wt") as f:
            f.write("%s\n" % self.total_blocks)
            f.write("%s\n" % self.n_occupied_segments)

            for s in self.occupied_segments[:-1]:
                f.write("%s\n" % ", ".join(tuple([str(i) for i in s])))
            
            f.write("%s" % ", ".join(tuple([str(i) for i in self.occupied_segments[-1]])))


    def runFileOperations(self):
        """Executa efetivamente as operações de arquivo solicitadas."""

        self.is_running_ops = True # Informa o início de operações, bloqueando novas operações
        self.readStorageFile()

        print ("Sistema de arquivos:\n")
        
        for opnumber, op in enumerate(self.file_operations, start=1):
            print("\nOperação " + str(opnumber) + ":")
            pid = int(op[0])
            operation_type = int(op[1])
            file_name = op[2]

            # Operação de criação de arquivo
            if (pid < 1 or pid > self.PIDs_of_processes):
                print("Falha: não existe o processo.")
            elif operation_type == 0:
                n_blocks = int(op[3])
                required_free_blocks = [0 for _ in range(n_blocks)]

                # Varredura do mapa de blocos ocupados
                for i in range(len(self.occupied_blocks_map)):
                    # Verifica se o bloco está ocupado
                    if self.occupied_blocks_map[i] != 0:
                        continue
                    
                    # Caso existam blocos livres contíguos o suficiente, atualiza as informações de alocação
                    if self.occupied_blocks_map[i:i + n_blocks] == required_free_blocks:
                        # Escrita no mapeamento de blocos
                        for j in range(i, i + n_blocks):
                            self.occupied_blocks_map[j] = file_name

                        self.occupied_segments.append([file_name, i, n_blocks]) # Atualiza informação dos segmentos ocupados
                        self.n_occupied_segments = len(self.occupied_segments) # Atualiza o total de segmentos ocupados

                        print("O processo {pid} criou o arquivo {file_name} (bloco(s) {occupied_blocks}).".format(
                            pid=pid, 
                            file_name=file_name, 
                            occupied_blocks=list(range(i, i + n_blocks)))
                        )
                        break
                    
                    # Caso não exista blocos contíguos o suficiente, rejeita a escrita do arquivo
                    if len(self.occupied_blocks_map[i:]) < len(required_free_blocks):
                        print("O processo %s não pode criar o arquivo %s (falta de espaço)." % (pid, file_name))
                        break
            # Operação de remoção de arquivo
            elif operation_type == 1:
                # Remove as informações do arquivo do mapeamento de blocos
                for i in range(len(self.occupied_blocks_map)):
                    if self.occupied_blocks_map[i] == file_name:
                        self.occupied_blocks_map[i] = 0
                
                # Remove as informações do arquivo da lista de segmentos ocupados
                for s in self.occupied_segments:
                    if s[0] == file_name:
                        self.occupied_segments.remove(s)
                        self.n_occupied_segments = len(self.occupied_segments)
                        break

                print("O processo %s deletou o arquivo %s." % (pid, file_name))

        self.writeStorageFile()
        self.file_operations = [] # Limpa a lista de operações pendentes
        self.has_pending_ops = False # Atualiza o status de não haver mais operações pendentes
        self.is_running_ops = False # Informa o fim das operações, liberando novas solicitações


    def printStorageMap(self):
        """Informa a utilização dos blocos no sistema de arquivo."""

        occupied_blocks = [str(b) for b in self.occupied_blocks_map]

        print("\nMapa de ocupação do disco:")
        print("| " + " | ".join(occupied_blocks) + " |")


class StorageFileNotFound(Exception):
    pass
