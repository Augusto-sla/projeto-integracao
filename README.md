# 📦 Production Order System

Sistema web para gerenciamento de ordens de produção, com interface frontend em HTML/CSS/JavaScript e backend REST API em Python (Flask) com banco de dados SQLite.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação e Execução](#instalação-e-execução)
- [Endpoints da API](#endpoints-da-api)
- [Autenticação](#autenticação)
- [Documentação dos Arquivos](#documentação-dos-arquivos)

---

## Visão Geral

O **Production Order System** permite criar, visualizar, atualizar e excluir ordens de produção através de uma interface web intuitiva. O backend expõe uma API REST protegida por chave de autenticação, com validação de dados, sanitização contra XSS e tratamento global de erros.

---

## Funcionalidades

- ✅ Cadastro de ordens com produto, quantidade e status inicial
- ✅ Listagem de todas as ordens em tabela com atualização em tempo real
- ✅ Alteração de status diretamente na tabela (Pending / In Progress / Completed)
- ✅ Exclusão de ordens com confirmação do usuário
- ✅ Indicador de status da API (Online / Offline) no header
- ✅ Filtro de ordens por status via query string (`?status=Pending`)
- ✅ Interface responsiva para desktop e mobile
- ✅ Feedback visual de sucesso e erro em todas as operações

---

## Tecnologias

| Camada     | Tecnologia                        |
|------------|-----------------------------------|
| Frontend   | HTML5, CSS3, JavaScript (ES2017+) |
| Backend    | Python 3, Flask, Flask-CORS       |
| Banco de Dados | SQLite3                       |
| Autenticação | API Key via header HTTP         |

---

## Estrutura do Projeto

```
production-order-system/
│
├── static/                  # Arquivos servidos pelo Flask como estáticos
│   ├── index.html           # Interface principal da aplicação
│   ├── style.css            # Estilos e layout responsivo
│   └── script.js            # Lógica de comunicação com a API (CRUD)
│
├── app.py                   # Backend Flask — rotas, autenticação e validação
├── database.py              # Módulo de conexão e inicialização do SQLite
├── orders.db                # Banco de dados SQLite (gerado automaticamente)
│
└── README.md
```

---

## Instalação e Execução

### Pré-requisitos

- Python 3.8+
- pip

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/production-order-system.git
cd production-order-system
```

### 2. Instale as dependências

```bash
pip install flask flask-cors
```

### 3. Inicie o servidor

```bash
python app.py
```

O servidor estará disponível em: `http://localhost:5000`

### 4. Acesse a interface

Abra o navegador em `http://localhost:5000`. A página `index.html` é servida diretamente pelo Flask.

> O banco de dados `orders.db` é criado automaticamente na primeira execução.

---

## Endpoints da API

### `GET /status`
Retorna o status da API e o total de ordens cadastradas.

```json
{
  "status": "online",
  "system": "Production Order System",
  "version": "2.0.0",
  "total_orders": 42,
  "timestamp": "2026-04-08 14:30:00"
}
```

---

### `GET /orders`
Retorna todas as ordens. Aceita filtro opcional por status.

```
GET /orders?status=Pending
```

---

### `GET /orders/{id}`
Retorna uma ordem específica pelo ID.

---

### `POST /orders` 🔒
Cria uma nova ordem de produção.

**Body (JSON):**
```json
{
  "product": "WEG Electric Motor",
  "quantity": 100,
  "status": "Pending"
}
```

**Resposta (201):**
```json
{
  "id": 1,
  "product": "WEG Electric Motor",
  "quantity": 100,
  "status": "Pending",
  "created_at": "2026-04-08 14:30:00"
}
```

---

### `PUT /orders/{id}` 🔒
Atualiza o status de uma ordem existente.

**Body (JSON):**
```json
{
  "status": "In Progress"
}
```

---

### `DELETE /orders/{id}` 🔒
Remove permanentemente uma ordem.

**Resposta (200):**
```json
{
  "message": "Order 1 (WEG Electric Motor) deleted successfully.",
  "deleted_id": 1
}
```

---

## Autenticação

As rotas de escrita (🔒 POST, PUT, DELETE) exigem o header `X-API-Key`:

```
X-API-Key: senai-cybersystems-2026-secure-key
```

| Cenário              | HTTP Status | Mensagem                        |
|----------------------|-------------|---------------------------------|
| Header ausente       | 401         | `Authentication required.`      |
| Chave inválida       | 403         | `Invalid or expired API Key.`   |
| Chave correta        | 2xx         | Operação realizada com sucesso  |

> ⚠️ Em produção, substitua a chave por uma variável de ambiente:
> ```python
> API_KEY = os.environ.get('API_KEY')
> ```

---

## Documentação dos Arquivos

| Arquivo        | Documentação                   |
|----------------|--------------------------------|
| `index.html`   | [index.md](./index.md)         |
| `style.css`    | [style.md](./style.md)         |
| `script.js`    | [script.md](./script.md)       |
| `app.py`       | Docstrings inline no arquivo   |
| `database.py`  | Docstrings inline no arquivo   |

---

## Validações

### Frontend (`script.js`)
- Produto não pode ser vazio
- Quantidade deve ser um número positivo

### Backend (`app.py`)
- Produto: obrigatório, máximo 200 caracteres, sanitizado com `html.escape()` (anti-XSS)
- Quantidade: inteiro entre 1 e 999.999
- Status: deve ser um de `['Pending', 'In Progress', 'Completed']`

---

## Licença

Projeto desenvolvido para fins educacionais — SENAI CyberSystems 2026.
