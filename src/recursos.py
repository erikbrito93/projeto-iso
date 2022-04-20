from src.processos import Process

class Resource(object):
    """Representação de rescursos de E/S."""

    def __init__(self, id_number: int, resource_name: str):
        self._id_number = id_number
        self._name = resource_name
        self._locked_process = 0


    @property
    def id_number(self) -> int:
        return self._id_number


    @property
    def name(self) -> str:
        return self._name

    @property
    def locked_process(self) -> int:
        return self._locked_process

    @locked_process.setter
    def locked_process(self, process):
        self._locked_process = process


class ResourceManager(object):
    """Gerencia os recursos de E/S do pseudo S.O."""

    def __init__(self):
        self.resources = [
            Resource(1, "scanner"),
            Resource(2, "printer_01"),
            Resource(3, "printer_02"),
            Resource(4, "modem"),
            Resource(5, "sata_01"),
            Resource(6, "sata_02")
        ]
        self.waiting_processes = [[],[],[],[],[],[]]


    def printResourceStatus(self):
        """Informa a utilização dos recursos de E/S do sistema."""

        print("Status dos rescursos de E/S:")
        for r in self.resources:
            print("{resource_id} {resource_name}: {pid}".format(
                resource_id=r.id_number, 
                resource_name=r.name, 
                pid="PID: %s" % r.locked_process if r.locked_process else "livre"
            ))


    def scanProcess(self, process: Process):
        success = True
        if process.scanner_req == 1: 
            r = self.lockResource(process, self.resources[0].name)
            if not r: 
                success = False
        if process.printer_code == 1:
            r = self.lockResource(process, self.resources[1].name)
            if not r: 
                success = False
        if process.printer_code == 2:
            r = self.lockResource(process, self.resources[2].name)
            if not r: 
                success = False
        if process.modem_req == 1: 
            r = self.lockResource(process, self.resources[3].name)
            if not r: 
                success = False
        if process.driver_code == 1:
            r = self.lockResource(process, self.resources[4].name)
            if not r: 
                success = False
        if process.driver_code == 2:
            r = self.lockResource(process, self.resources[5].name)
            if not r: 
                success = False

        if not success:
            self.releaseResources(process)
            return -1

        return 0

    def lockResource(self, process: Process, resource_type: str) -> Resource:
        """Reserva o uso de um recurso para um processo específico.
        
            Args:
                process: instância da classe Process
                resource_type: tipo do recurso
        """
        #Verifica se o processo já está esperando por outros recursos e se estão disponíveis
        others_available = True
        for index, r in enumerate(self.resources):
            if (resource_type != r.name and process.PID in self.waiting_processes[index]):
                if r.locked_process and r.locked_process != process.PID:
                    others_available = False

        # Varredura dos recursos existentes
        for index, r in enumerate(self.resources):
            # Verifica se o recurso é do tipo especificado
            if r.name == resource_type:
                # Verifica se o processo já possui o recurso
                if r.locked_process == process.PID:
                    return r

                # Verifica se o recurso está livre pra uso
                if r.locked_process:
                    if (process.PID not in self.waiting_processes[index]):
                        print("\n\tO recurso %s não está disponível para uso do processo %s, (reservado ao processo %s)." % (r.name, process.PID, r.locked_process))
                        self.waiting_processes[index].append(process.PID)
                elif others_available:
                    r.locked_process = process.PID # Regitra no recurso o PID do processo que reservou o uso

                    print("\n\tRecurso %s reservado para o processo %s." % (r.name, r.locked_process))
                    if (process.PID in self.waiting_processes[index]):
                        self.waiting_processes[index].remove(process.PID)
                    return r


    def releaseResources(self, process: Process):
        """Libera o uso dos recursos de um processo específico.
        
            Args:
                process: instância da classe Process
        """

        # Varredura dos recursos existentes
        for r in self.resources:
            # Verifica se o recurso está travado neste processo
            if r.locked_process == process.PID: 
                r.locked_process = 0 # Libera o uso do recurso

                print("\n\tRecurso %s liberado pelo processo %s." % (r.name, process.PID))

    def useResource(self, process: Process, resource_type: str):
        """Representa o uso de um recurso de E/S."""

        r = self.lockResource(process, resource_type)
        
        if r:
            print("Recurso %s em uso pelo processo %s." % (r.name, process.PID))
            self.releaseResource(process, resource_type)
