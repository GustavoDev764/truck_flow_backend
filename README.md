# TruckFlow truck_flow_backend

API REST para gerenciamento de caminhões, integrada à tabela FIPE para consulta de preços. Desenvolvida com **Django** e **Django REST Framework**, seguindo **Clean Architecture**.

---

## Regras e orientações – Aderência à entrega

Esta seção responde aos critérios de avaliação exigidos no repositório.

### Código funcional

A API está completa e operacional:

- **CRUD de caminhões** com validação de placas e integração à tabela FIPE (marcas, modelos, anos, preços)
- **Autenticação JWT** (SimpleJWT) com login, refresh token e logout com invalidação de sessão
- **Gerenciamento de usuários** e permissões por grupo (manage, cliente)
- **Dashboard** com dados agregados da frota
- **Documentação OpenAPI** em `/api/docs/`
- **Docker** com PostgreSQL para ambiente isolado

O código segue Clean Architecture: domínio independente, casos de uso testáveis e infraestrutura injetada via `dependencies.py`.

---

### Documentação explicando o raciocínio adotado

**Por que Clean Architecture?**

- **Domínio isolado:** entidades e regras de negócio em `domain/` sem dependências externas, facilitando testes e evolução.
- **Casos de uso explícitos:** `application/use_cases/` orquestra repositórios e clientes externos; a lógica fica testável com Spies.
- **Inversão de dependência:** repositórios e `FipeClient` são protocolos (contratos); implementações Django/HTTP são injetadas.
- **Composition root:** `dependencies.py` instancia repositórios, use cases e views, centralizando a configuração.

**Por que testes unitários com Spies (sem banco)?**

- **Rapidez:** `SimpleTestCase` não cria banco; os testes rodam em milissegundos.
- **Determinismo:** `TruckRepositorySpy`, `FipeClientSpy` etc. controlam exatamente o comportamento e permitem asserções sobre interações.
- **Independência:** não dependem de PostgreSQL, migrations ou dados externos; funcionam em qualquer ambiente (CI, local).
- **Coverage alto:** 100% em `apps/trucks` e `core` (exceto migrations, scripts e apresentação secundária).

**Decisões técnicas**

- **JWT com invalidação:** modelo `Session` armazena `jti`; logout revoga a sessão no backend para maior segurança.
- **Integração FIPE:** cliente HTTP isolado em `infrastructure/fipe/`; testes usam `FipeClientSpy` para simular respostas.

---

### Testes para códigos relevantes

**O que existe hoje**

- **Testes unitários (Django `SimpleTestCase`):** cobrem domínio, casos de uso, infraestrutura e apresentação em `apps/trucks/tests/`.

**Estrutura dos testes**

| Camada        | Arquivo(s)                                                                 | O que testa                                              |
| ------------- | -------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Use cases** | `create_truck_spec_use_case.py`, `update_*`, `delete_*`, `list_*`          | Regras de negócio, integração com repositório e FIPE     |
| **Controller**| `truck_controller_spec.py`                                                 | Orquestração dos use cases                               |
| **Repository**| `repositories_spec.py`                                                     | Persistência (Django ORM)                                |
| **FIPE**      | `fipe_client_spec.py`                                                      | Cliente HTTP da API FIPE                                 |
| **Presentation** | `views_spec.py`, `errors_and_serializers_spec.py`                       | Views DRF, serializers e tratamento de erros             |
| **Infra**     | `djangomodels_spec.py`, `seed_trucks_spec.py`, `migration_import_spec.py` | Modelos Django, management commands e migrations         |

**Estratégia: Spies em vez de mocks de banco**

Todos os testes usam Spies (`TruckRepositorySpy`, `FipeClientSpy`, etc.) que registram chamadas e retornam dados controlados. Isso permite:

- Validar que o use case chama o repositório e o FIPE com os parâmetros corretos
- Simular erros (ex.: placa duplicada, FIPE indisponível) sem tocar no banco real

---

### Originalidade, clareza e melhores práticas

- **Originalidade:** Implementação Clean Architecture em Django, integração FIPE, JWT com revogação de sessão, seed de grupos e usuários.
- **Clareza:** Camadas bem definidas, nomes descritivos, `pyproject.toml` com Ruff/Black e regras de coverage explícitas.
- **Práticas:** Type hints, formatação automática, lint configurado, `.env` para configuração sensível, `.gitignore` excluindo evidências de teste (htmlcov, .coverage).

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

Todos os testes usam dados mockados (padrão Spy: `TruckRepositorySpy`, `FipeClientSpy`, `TruckControllerSpy`, etc.) e **não criam banco de testes**, rodando com `SimpleTestCase`:

```bash
python manage.py test --noinput
```

Rodar com cobertura e gerar relatório HTML (`htmlcov/`):

```bash
python -m coverage run manage.py test --noinput
python -m coverage html
```

O relatório fica em `htmlcov/index.html`. O backend atinge **100% de coverage** em `apps/trucks` e `core` (consulte `[tool.coverage.run]` em `pyproject.toml` para exclusions).

```bash
# Ver resumo no terminal (opcional)
python -m coverage report
```

> **Nota:** Use `python -m coverage` para garantir funcionamento mesmo sem o venv ativado no PATH.

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
