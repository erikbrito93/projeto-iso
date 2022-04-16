from processos import Process

class Resource(object):
    """Representação de rescursos de E/S."""

    def __init__(self, id_number: int, resource_name: str):
        self.id_number = id_number
        self.name = resource_name
        self.locked_process = 0


    @property
    def id_number(self) -> int:
        return self.id_number


    @property
    def name(self) -> str:
        return self.name

    @property
    def locked_process(self) -> int:
        return self.locked_process


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


    def printResourceStatus(self):
        """Informa a utilização dos recursos de E/S do sistema."""

        print("Status dos rescursos de E/S:")
        for r in self.resources:
            print("{resource_id} {resource_name}: {pid}".format(
                resource_id=r.id_number, 
                resource_name=r.name, 
                pid="PID: %s" % r.locked_process if r.locked_process else "livre"
            ))


    def lockResource(self, process: Process, resource_type: str) -> Resource:
        """Reserva o uso de um recurso para um processo específico.
        
            Args:
                process: instância da classe Process
                resource_type: tipo do recurso
        """
        
        # Varredura dos recursos existentes
        for r in self.resources:
            # Verifica se o recurso é do tipo especificado
            if r.name.startswith(resource_type):
                # Verifica se o recurso está livre pra uso
                if r.locked_process:
                    print("O recurso %s id:%s não está disponível para uso (reservado ao processo %s)." % (r.name, r.id_number, r.locked_process))
                else:
                    r.locked_process = Process.PID # Regitra no recurso o PID do processo que reservou o uso
                    
                    # Registra no processo o identificador do recurso
                    if resource_type == "scanner":
                        process.scanner_req = r.id_number
                    elif resource_type == "printer":
                        process.printer_code = r.id_number
                    elif resource_type == "modem":
                        process.modem_req = r.id_number
                    elif resource_type == "sata":
                        process.driver_code = r.id_number

                    print("Recurso %s reservado para o processo %s." % (r.name, r.id_number, r.locked_process))
                    return r


    def releaseResource(self, process: Process, resource_type: str):
        """Libera o uso de um recurso de um processo específico.
        
            Args:
                process: instância da classe Process
                resource_type: tipo do recurso
        """

        # Varredura dos recursos existentes
        for r in self.resources:
            # Verifica se o recurso é do tipo especificado
            if r.name.startswith(resource_type) and r.locked_process == process.PID:
                r.locked_process = 0 # Libera o uso do recurso

                # Desvincula o recurso do processo
                if resource_type == "scanner":
                    process.scanner_req = 0
                elif resource_type == "printer":
                    process.printer_code = 0
                elif resource_type == "modem":
                    process.modem_req = 0
                elif resource_type == "sata":
                    process.driver_code = 0

                print("Recurso %s liberado pelo processo %s." % (r.name, process.PID))
                return
            
        print("O processo %s não estava reservando nenhum recurso do tipo %s." % (process.PID, resource_type))


    def useResource(self, process: Process, resource_type: str):
        """Representa o uso de um recurso de E/S."""

        r = self.lockResource(process, resource_type)
        
        if r:
            print("Recurso %s em uso pelo processo %s." % (r.name, process.PID))
            self.releaseResource(process, resource_type)
