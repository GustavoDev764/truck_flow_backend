# TruckFlow truck_flow_backend

API REST para gerenciamento de caminhões, integrada à tabela FIPE para consulta de preços. Desenvolvida com **Django** e **Django REST Framework**, seguindo **Clean Architecture**.

---

## O que é o projeto

O TruckFlow truck_flow_backend é a API do sistema TruckFlow, responsável por:

- **CRUD de caminhões** (cadastro, listagem, atualização e exclusão)
- **Integração com a FIPE** para consulta de preços e dados de marcas/modelos/anos
- **Autenticação JWT** para acesso às rotas protegidas
- **Dashboard** com dados agregados

---

## Arquitetura

O projeto utiliza **Clean Architecture** com quatro camadas. Os módulos ficam em `apps/`:

```
apps/
├── accounts/          # Autenticação e usuários
├── trucks/            # Caminhões e integração FIPE
└── (futuro: cars, home, clicksign...)

apps/trucks/
├── domain/           # Núcleo do negócio (sem dependências externas)
│   ├── entities.py   # Entidade Truck
│   ├── repositories.py   # Protocolos (contratos) TruckRepository, FipeClient
│   └── exceptions.py     # Erros de domínio
│
├── application/      # Casos de uso
│   ├── use_cases/    # CreateTruckUseCase, UpdateTruckUseCase, etc.
│   ├── dtos/         # Commands e DTOs
│   └── services/     # TruckController (orquestrador)
│
├── infrastructure/   # Implementações externas
│   ├── persistence/  # DjangoTruckRepository (ORM)
│   └── fipe/         # FipeClientHttp (cliente HTTP da API FIPE)
│
└── presentation/     # Camada web (DRF)
    ├── views.py
    ├── serializers.py
    └── urls.py
```

| Camada             | Responsabilidade                                    |
| ------------------ | --------------------------------------------------- |
| **Domain**         | Entidades, regras de negócio, contratos (protocols) |
| **Application**    | Casos de uso, orquestração, DTOs                    |
| **Infrastructure** | Persistência (Django), integrações (FIPE)           |
| **Presentation**   | Controllers REST, serialização, respostas HTTP      |

O `dependencies.py` atua como **composition root**, instanciando repositórios, clientes e use cases para injeção de dependência.

---

## Pré-requisitos

- **Python 3.11+**
- **PostgreSQL** (ou SQLite para desenvolvimento local)

---

## Instalação

### 1. Clone o repositório e entre na pasta

```bash
cd truck_flow_backend
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com suas configurações (banco de dados, JWT, etc.). Para usar **SQLite** em vez de PostgreSQL, defina:

```env
DB_PROVIDER=sqlite
```

(ou omita `DB_PROVIDER` e deixe `DB_NAME` vazio para usar o padrão SQLite)

### 4. Execute as migrações

```bash
python manage.py migrate
```

### 5. Crie um superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 6. Usuários de exemplo (seed)

Para criar grupos e usuários de teste:

```bash
python manage.py seed_groups --create-users
```

| E-mail                | Senha        | Grupo   | Permissões                     |
| --------------------- | ------------ | ------- | ------------------------------ |
| manage@truckflow.com  | truckflow123 | manage  | CRUD caminhões + CRUD usuários |
| cliente@truckflow.com | truckflow123 | cliente | CRUD caminhões                 |

---

## Como iniciar o servidor

```bash
python run.py
```

Ou diretamente com o Django:

```bash
python manage.py runserver 127.0.0.1:3000
```

A porta padrão é **3000** (configurável via `HOST_PORT` no `.env`).

---

## Como rodar o truck_flow_backend

Existem **duas maneiras** de rodar o projeto:

| Opção                          | Descrição                       |
| ------------------------------ | ------------------------------- |
| **1. Com Docker**              | Para quem tem Docker instalado  |
| **2. Windows 11 (sem Docker)** | Instalação manual no Windows 11 |

---

### Opção 1 – Com Docker

Para quem já possui **Docker** e **Docker Compose** instalados.

1. Entre na pasta do truck_flow_backend:

```bash
cd truck_flow_backend
```

2. Configure o `.env` (opcional; há valores padrão):

```bash
cp .env.example .env
```

3. Suba os containers:

```bash
docker compose up --build
```

O entrypoint executa automaticamente: aguarda o PostgreSQL, migrações, usuários de exemplo, superusuário e inicia o servidor.

- **API:** http://localhost:3000
- **PostgreSQL:** localhost:5432 (user: `postgres`, password: `postgres`, db: `truckflow`)

---

### Opção 2 – Windows 11 (sem Docker)

Para rodar no **Windows 11 sem Docker**, siga a seção [Instalação](#instalação) acima. Resumo:

1. Instale **Python 3.11+** e **PostgreSQL** (ou use SQLite com `DB_PROVIDER=sqlite`)
2. No **PowerShell** ou **Terminal**, entre na pasta do truck_flow_backend e execute:

```powershell
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_groups --create-users
python run.py
```

- **API:** http://localhost:3000

---

### Credenciais criadas automaticamente (Docker)

| Usuário               | Senha        | Tipo      |
| --------------------- | ------------ | --------- |
| admin                 | admin123     | Superuser |
| manage@truckflow.com  | truckflow123 | manage    |
| cliente@truckflow.com | truckflow123 | cliente   |

### Customizar superusuário (Docker – .env)

```env
SUPERUSER_USERNAME=meu_admin
SUPERUSER_EMAIL=admin@email.com
SUPERUSER_PASSWORD=minha_senha
```

### Comandos úteis (Docker)

```bash
# Subir em background
docker compose up -d --build

# Descer containers
docker compose down

# Ver logs
docker compose logs -f truck_flow_backend
```

---

## Extensões recomendadas (Cursor / VS Code)

| Extensão            | ID                          | Uso                                |
| ------------------- | --------------------------- | ---------------------------------- |
| **Python**          | `ms-python.python`          | IntelliSense, debug, interpretador |
| **Ruff**            | `charliermarsh.ruff`        | Lint e formatação de código        |
| **Black Formatter** | `ms-python.black-formatter` | Formatação alternativa ao Ruff     |
| **Pylance**         | `ms-python.vscode-pylance`  | Tipagem e análise estática         |

Com **Ruff** ou **Black** + `editor.formatOnSave: true`, o código será formatado automaticamente ao salvar.

---

## Rotas principais

| Método | Endpoint            | Descrição                      |
| ------ | ------------------- | ------------------------------ |
| POST   | `/api/auth/login/`  | Login (obtém JWT)              |
| GET    | `/api/trucks/`      | Lista caminhões                |
| POST   | `/api/trucks/`      | Cria caminhão                  |
| PUT    | `/api/trucks/<id>/` | Atualiza caminhão              |
| DELETE | `/api/trucks/<id>/` | Exclui caminhão                |
| GET    | `/api/dashboard/`   | Dados do dashboard             |
| GET    | `/api/fipe/brands/` | Marcas FIPE                    |
| GET    | `/api/docs/`        | Documentação Swagger (OpenAPI) |

---

## Desenvolvimento

### Formatação e lint

```bash
python scripts/format_project.py
```

Ou manualmente:

```bash
ruff check --fix .
black .
```

### Testes

```bash
python manage.py test
```

---

## Estrutura de pastas

```
truck_flow_backend/
├── config/              # Configuração Django (settings, urls, env)
├── core/                # Modelos base (UUIDModel)
├── apps/                # Módulos da aplicação
│   ├── accounts/        # Autenticação e usuários
│   ├── trucks/
│   └── (cars, home, clicksign...)  # Novos módulos
├── scripts/             # Scripts auxiliares (formatação, etc.)
├── manage.py
├── run.py               # Inicia o servidor
├── Dockerfile           # Build da imagem Docker
├── docker-compose.yml   # Orquestração Docker (truck_flow_backend + PostgreSQL)
├── entrypoint.sh        # Script de inicialização no container
├── requirements.txt
├── pyproject.toml       # Config Black/Ruff
└── .env.example
```

---

## Tecnologias

- **Django** – Framework web
- **Django REST Framework** – API REST
- **djangorestframework-simplejwt** – Autenticação JWT
- **drf-spectacular** – Documentação OpenAPI/Swagger
- **django-cors-headers** – CORS
- **psycopg2-binary** – Driver PostgreSQL
- **python-dotenv** – Variáveis de ambiente
- **requests** – Cliente HTTP (integração FIPE)
- **Black** / **Ruff** – Formatação e lint
