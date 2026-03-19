class UserDomainError(Exception):
    """Erro base da camada de domínio de usuários."""


class UserNotFoundError(UserDomainError):
    def __init__(self, user_id: int):
        super().__init__(f"Usuário não encontrado (id={user_id}).")
        self.user_id = user_id


class DuplicateUsernameError(UserDomainError):
    def __init__(self, username: str):
        super().__init__(f"Já existe um usuário com o username '{username}'.")
        self.username = username
