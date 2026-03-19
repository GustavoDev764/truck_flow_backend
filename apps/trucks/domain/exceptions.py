class TruckDomainError(Exception):
    """Erro base da camada de domínio."""


class DuplicateLicensePlateError(TruckDomainError):
    def __init__(self, license_plate: str):
        super().__init__(f"Já existe um caminhão com a placa '{license_plate}'.")
        self.license_plate = license_plate


class InvalidFipeDataError(TruckDomainError):
    def __init__(self, message: str = "Dados inválidos para consulta na FIPE."):
        super().__init__(message)


class TruckNotFoundError(TruckDomainError):
    def __init__(self, truck_id):
        super().__init__(f"Caminhão não encontrado (id={truck_id}).")
        self.truck_id = truck_id
