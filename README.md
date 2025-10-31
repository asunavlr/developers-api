# 🚀 Developers API - FastAPI + Supabase

Uma API REST moderna e robusta para gerenciamento de usuários, construída com FastAPI e Supabase. Inclui autenticação JWT, validações avançadas, logging estruturado e documentação automática.

## ✨ Características

- 🔐 **Autenticação JWT** com Supabase Auth
- 📝 **Validações robustas** com Pydantic
- 📊 **Logging estruturado** em JSON
- 📚 **Documentação automática** com Swagger/OpenAPI
- 🧪 **Testes automatizados** com pytest
- 🐳 **Docker** pronto para produção
- 🔒 **Segurança** com middleware CORS e validação de tokens
- 🎯 **Endpoints RESTful** bem estruturados

## 🛠️ Stack Tecnológica

- **Backend**: Python 3.11+ com FastAPI
- **Banco de dados**: Supabase (PostgreSQL)
- **Autenticação**: Supabase Auth (JWT)
- **Validação**: Pydantic v2
- **Testes**: pytest
- **Containerização**: Docker + Docker Compose
- **Logging**: Estruturado em JSON

## 📋 Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (opcional)
- Conta Supabase (gratuita)

## 🔧 Configuração do Supabase

### 1. Criar Projeto
1. Acesse [supabase.com](https://supabase.com) e crie um novo projeto
2. Anote a URL e as chaves do projeto

### 2. Configurar Banco de Dados
Execute no SQL Editor do Supabase:

```sql
-- Criar tabela de usuários
create table public.users (
  id uuid primary key,
  name text not null,
  email text not null unique,
  phone text not null,
  status text not null default 'active',
  role text not null default 'user',
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now()
);

-- Trigger para atualizar updated_at automaticamente
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists users_set_updated_at on public.users;
create trigger users_set_updated_at
before update on public.users
for each row execute function public.set_updated_at();

-- Habilitar RLS (Row Level Security)
alter table public.users enable row level security;

-- Política: usuários podem ver seus próprios dados
create policy "Users can select own row"
on public.users
for select
to authenticated
using (auth.uid() = id);

-- Política: usuários podem atualizar seus próprios dados
create policy "Users can update own row"
on public.users
for update
to authenticated
using (auth.uid() = id)
with check (auth.uid() = id);

-- Política: admins podem atualizar qualquer usuário
create policy "Admin can update any status"
on public.users
for update
to authenticated
using (
  exists (
    select 1 from public.users u
    where u.id = auth.uid() and u.role = 'admin'
  )
)
with check (
  exists (
    select 1 from public.users u
    where u.id = auth.uid() and u.role = 'admin'
  )
);
```

### 3. Configurar Variáveis de Ambiente
Copie `.env.example` para `.env` e configure:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-chave-anonima-aqui
SUPABASE_SERVICE_ROLE_KEY=sua-chave-service-role-aqui
```

**Onde encontrar as chaves:**
- Dashboard → Settings → API
- `SUPABASE_URL`: Project URL
- `SUPABASE_ANON_KEY`: anon/public key
- `SUPABASE_SERVICE_ROLE_KEY`: service_role key (use apenas em ambiente seguro)

## 🚀 Instalação e Execução

### Opção 1: Ambiente Local

```bash
# Clonar o repositório
git clone https://github.com/asunavlr/developers-api.git
cd developers-api

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependências
pip install -r python/requirements.txt

# Executar a aplicação
uvicorn python.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Opção 2: Docker

```bash
# Clonar o repositório
git clone https://github.com/asunavlr/developers-api.git
cd developers-api

# Executar com Docker Compose
docker-compose up --build

# Ou construir e executar manualmente
docker build -t developers-api .
docker run --env-file .env -p 8000:8000 developers-api
```

### 🌐 Acessar a Aplicação

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## 📖 Documentação da API

### Autenticação

#### POST /auth/register
Registra um novo usuário.

**Body:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "MinhaSenh@123",
  "name": "João Silva",
  "phone": "+5511999999999"
}
```

**Validações:**
- Email: formato válido
- Senha: mínimo 8 caracteres, deve conter maiúscula, minúscula e número
- Telefone: formato E.164 (+5511999999999)
- Nome: mínimo 2 caracteres

**Resposta (201):**
```json
{
  "message": "Usuário cadastrado com sucesso",
  "user": {
    "id": "uuid-aqui",
    "email": "usuario@exemplo.com",
    "name": "João Silva"
  }
}
```

#### POST /auth/login
Autentica um usuário existente.

**Body:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "MinhaSenh@123"
}
```

**Resposta (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid-aqui",
    "email": "usuario@exemplo.com",
    "name": "João Silva"
  }
}
```

### Gerenciamento de Usuários

#### GET /users/me
Retorna dados do usuário autenticado.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Resposta (200):**
```json
{
  "id": "uuid-aqui",
  "name": "João Silva",
  "email": "usuario@exemplo.com",
  "phone": "+5511999999999",
  "status": "active",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### PUT /users/{id}
Atualiza dados do usuário (apenas próprios dados).

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (todos os campos opcionais):**
```json
{
  "name": "João Silva Santos",
  "email": "novoemail@exemplo.com",
  "phone": "+5511888888888"
}
```

**Resposta (200):**
```json
{
  "message": "Usuário atualizado com sucesso",
  "user": {
    "id": "uuid-aqui",
    "name": "João Silva Santos",
    "email": "novoemail@exemplo.com",
    "phone": "+5511888888888",
    "status": "active",
    "updated_at": "2024-01-15T11:45:00Z"
  }
}
```

#### PATCH /users/{id}/status
Atualiza status do usuário (apenas admins).

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Body:**
```json
{
  "status": "inactive"
}
```

**Status permitidos:** `active`, `inactive`, `blocked`

**Resposta (200):**
```json
{
  "message": "Status atualizado com sucesso",
  "user": {
    "id": "uuid-aqui",
    "status": "inactive"
  }
}
```

### Códigos de Resposta

- **200**: Sucesso
- **201**: Criado com sucesso
- **400**: Erro na requisição
- **401**: Não autorizado (token inválido/ausente)
- **403**: Proibido (sem permissão)
- **404**: Não encontrado
- **422**: Erro de validação
- **500**: Erro interno do servidor

### Exemplo de Erro de Validação (422)

```json
{
  "message": "Erro de validação",
  "errors": [
    {
      "field": "password",
      "message": "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
    }
  ],
  "path": "/auth/register"
}
```

## 🧪 Testes

### Executar Testes Localmente

```bash
# Ativar ambiente virtual
.\.venv\Scripts\activate

# Instalar dependências (se necessário)
pip install -r python/requirements.txt

# Executar testes
python -m pytest -v

# Ou usar o Makefile
make test

# Executar com cobertura
python -m pytest --cov=python/app --cov-report=html
```

### Cobertura de Testes

Os testes incluem:
- ✅ Endpoint raiz (`GET /`)
- ✅ Documentação (`GET /docs`)
- ✅ Validações de registro (email, senha, telefone)
- ✅ Validações de status
- ✅ Autenticação (cenários com/sem token)
- ✅ Testes happy-path com mocks
- ✅ Cenários de erro

## 🔧 Funcionalidades Avançadas

### Logging Estruturado

A API utiliza logging estruturado em JSON com os seguintes campos:
- `level`: nível do log (INFO, ERROR, etc.)
- `message`: mensagem do log
- `timestamp`: timestamp ISO 8601
- `logger`: nome do logger
- `method`: método HTTP (para requests)
- `path`: caminho da requisição
- `status`: código de status HTTP
- `latency_ms`: latência da requisição em milissegundos

**Exemplo de log:**
```json
{
  "level": "INFO",
  "message": "Request completed",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "logger": "api.middleware",
  "method": "POST",
  "path": "/auth/login",
  "status": 200,
  "latency_ms": 45
}
```

### Middleware de Segurança

- **CORS**: Configurado para desenvolvimento e produção
- **Request Logging**: Log automático de todas as requisições
- **Validation Error Handler**: Tratamento global de erros de validação

### Validações Pydantic

- **Email**: Validação de formato
- **Senha**: Mínimo 8 caracteres, maiúscula, minúscula e número
- **Telefone**: Formato E.164 internacional
- **Status**: Valores permitidos (`active`, `inactive`, `blocked`)

## 🔐 Administração

### Promover Usuário a Admin

Execute no SQL Editor do Supabase:

```sql
UPDATE public.users 
SET role = 'admin' 
WHERE email = 'admin@exemplo.com';
```

### Gerenciar Status de Usuários

Apenas usuários com `role = 'admin'` podem usar o endpoint `PATCH /users/{id}/status`.

## 🐳 Docker

### Dockerfile

O projeto inclui um Dockerfile otimizado:
- Baseado em Python 3.11 slim
- Multi-stage build para reduzir tamanho
- Usuário não-root para segurança
- Health check configurado

### Docker Compose

 ```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
 ```

## ☁️ Deploy no Railway

Você pode fazer deploy no Railway de duas formas: usando Docker (recomendado) ou usando Start Command sem Docker.

### Opção A: Deploy com Docker (recomendado)
- Pré-requisito: `Dockerfile` já configurado para usar `PORT` do ambiente.
- Passos:
  1. Acesse https://railway.app e crie um novo projeto.
  2. Conecte o repositório GitHub: `asunavlr/developers-api`.
  3. Railway detectará o `Dockerfile` automaticamente e fará o build.
  4. Em "Variables", adicione:
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`
     - `SUPABASE_SERVICE_ROLE_KEY` (opcional, recomendado para admin/status)
  5. Faça deploy. O serviço ficará disponível em uma URL pública do Railway.

### Opção B: Deploy sem Docker (Start Command)
- Pré-requisito: `Procfile` incluído com `web: uvicorn python.app.main:app --host 0.0.0.0 --port $PORT`.
- Passos:
  1. No Railway, crie um serviço a partir do GitHub.
  2. Em "Deploy → Start Command", use: `uvicorn python.app.main:app --host 0.0.0.0 --port $PORT`.
  3. Em "Variables", adicione `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` (se aplicável).
  4. Faça deploy e verifique os logs para confirmar que está rodando em `0.0.0.0:$PORT`.

### Verificação pós-deploy
- Acesse `https://<seu-subdominio>.railway.app/docs` para conferir a documentação Swagger.
- Teste endpoints:
  - `POST /auth/register` com payload válido.
  - `POST /auth/login` e use o `access_token`.
  - `GET /users/me` com `Authorization: Bearer {access_token}`.
  - (Opcional Admin) `PATCH /users/{id}/status` com role admin.

### Dicas
- Caso use Docker, o container escuta `${PORT:-8000}` — Railway injeta `PORT` automaticamente.
- Mantenha as chaves do Supabase como variáveis no Railway, nunca commitadas.
- Use os logs do Railway para depurar falhas de build/start.

## ☁️ Deploy no Render (gratuito)

Render oferece um plano gratuito que roda serviços web a partir do seu `Dockerfile`.

### Opção A: Deploy com Docker (recomendado)
- Pré-requisito: `Dockerfile` já usa a variável `PORT` do ambiente.
- Passos:
  1. Acesse https://render.com e crie uma conta.
  2. Clique em "New +" → "Web Service" → conecte seu repositório GitHub `asunavlr/developers-api`.
  3. Render detectará o `Dockerfile` automaticamente.
  4. Selecione o plano "Free".
  5. Em "Environment Variables", adicione:
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`
     - `SUPABASE_SERVICE_ROLE_KEY` (opcional)
  6. Deploy. A URL pública ficará algo como `https://developers-api.onrender.com`.

### Opção B: Blueprint (render.yaml)
- Este repositório inclui `render.yaml` para facilitar.
- Passos:
  1. No Render, use "Blueprints" e aponte para o `render.yaml` deste repo.
  2. Preencha as variáveis de ambiente.
  3. Deploy no plano "Free".

### Pós-deploy
- Acesse `https://<seu-servico>.onrender.com/docs` para verificar o Swagger.
 

## 📁 Estrutura do Projeto

## 📁 Estrutura do Projeto

```
developers-api/
├── python/
│   ├── app/
│   │   ├── deps/
│   │   │   └── supabase_client.py    # Cliente Supabase
│   │   ├── routers/
│   │   │   ├── auth.py               # Endpoints de autenticação
│   │   │   └── users.py              # Endpoints de usuários
│   │   ├── utils/
│   │   │   └── logging.py            # Configuração de logging
│   │   ├── main.py                   # Aplicação FastAPI
│   │   └── schemas.py                # Modelos Pydantic
│   ├── tests/
│   │   ├── test_app.py               # Testes principais
│   │   └── test_users_happy.py       # Testes happy-path
│   └── requirements.txt              # Dependências Python
├── .env.example                      # Exemplo de variáveis
├── .gitignore                        # Arquivos ignorados
├── docker-compose.yml               # Configuração Docker
├── Dockerfile                       # Imagem Docker
├── Makefile                         # Comandos úteis
└── README.md                        # Este arquivo
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- Use `black` para formatação
- Siga PEP 8
- Adicione testes para novas funcionalidades
- Mantenha a cobertura de testes acima de 80%

## 📝 Changelog

### v1.2.0 (Atual)
- ✅ Logging estruturado em JSON
- ✅ Validações aprimoradas (senha, telefone)
- ✅ Response models para documentação
- ✅ Handler global para erros de validação
- ✅ Testes expandidos com mocks

### v1.1.0
- ✅ Endpoint GET /users/me
- ✅ Endpoint PATCH /users/{id}/status
- ✅ Sistema de roles (user/admin)
- ✅ Testes automatizados

### v1.0.0
- ✅ Autenticação JWT com Supabase
- ✅ CRUD de usuários
- ✅ Validações Pydantic
- ✅ Docker support

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/asunavlr/developers-api/issues)
- **Documentação**: http://localhost:8000/docs
- **Email**: suporte@exemplo.com

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Supabase](https://supabase.com/) - Backend as a Service
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validação de dados
- [pytest](https://pytest.org/) - Framework de testes

---

**Desenvolvido com ❤️ usando FastAPI e Supabase**