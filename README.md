# Neo4j Agent Chat System

Sistema de chat inteligente com integração Neo4j e Claude SDK para processamento de linguagem natural e gerenciamento de conhecimento em grafo.

## 🚀 Quick Start

### Iniciar o Sistema

```bash
# Backend API (porta 8080)
python3 -m uvicorn server:app --host 0.0.0.0 --port 8080 --reload

# Frontend Chat (porta 3000)
cd chat && python3 -m http.server 3000
```

## 📱 Acessar o Sistema

- **Chat Interface**: http://localhost:3000
- **API Backend**: http://localhost:8080
- **API Docs (Swagger)**: http://localhost:8080/docs

## 🏗️ Arquitetura

### Backend (FastAPI)
- **Porta**: 8080
- **Framework**: FastAPI com Uvicorn
- **Funcionalidades**:
  - API RESTful para processamento de mensagens
  - Integração com Neo4j para persistência em grafo
  - Documentação automática via Swagger/OpenAPI
  - Hot reload para desenvolvimento

### Frontend (Web Chat)
- **Porta**: 3000
- **Servidor**: Python HTTP Server
- **Interface**: HTML5 + JavaScript vanilla
- **Features**:
  - Chat em tempo real
  - Interface responsiva
  - Histórico de conversas
  - Indicadores de status

## 📋 Pré-requisitos

- Python 3.8+
- Neo4j Database (opcional)
- Navegador web moderno

## 🛠️ Instalação

1. **Clone o repositório**
```bash
git clone [seu-repositorio]
cd neo4j-agent/claude-code-sdk
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8080

# Neo4j Configuration (opcional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Claude SDK Configuration
CLAUDE_API_KEY=your-api-key
```

## 🚦 Verificação de Status

### Testar Backend
```bash
curl http://localhost:8080/docs
```

### Testar Frontend
```bash
curl http://localhost:3000/index.html
```

### Verificar Processos
```bash
# Ver processos rodando
ps aux | grep -E "uvicorn|http.server"

# Ver portas em uso
lsof -i :3000,8080
```

## 🔄 Gerenciamento de Serviços

### Parar Serviços
```bash
# Parar backend
pkill -f "uvicorn server:app"

# Parar frontend
pkill -f "python3 -m http.server 3000"
```

### Reiniciar Serviços
```bash
# Parar tudo
pkill -f "uvicorn server:app"
pkill -f "python3 -m http.server 3000"

# Iniciar novamente
python3 -m uvicorn server:app --host 0.0.0.0 --port 8080 --reload &
cd chat && python3 -m http.server 3000 &
```

## 📂 Estrutura do Projeto

```
claude-code-sdk/
├── server.py           # API Backend principal
├── chat/              # Frontend do chat
│   ├── index.html     # Interface do chat
│   ├── styles.css     # Estilos
│   └── script.js      # Lógica do cliente
├── core/              # Lógica de negócio
├── routes/            # Rotas da API
├── services/          # Serviços e integrações
├── utils/             # Utilitários
├── tests/             # Testes
├── docs/              # Documentação
└── requirements.txt   # Dependências Python
```

## 🔍 Troubleshooting

### Porta já em uso
```bash
# Verificar processo usando a porta
lsof -ti :8080  # ou :3000

# Matar processo na porta
lsof -ti :8080 | xargs kill -9
```

### Backend não inicia
```bash
# Verificar logs
python3 -m uvicorn server:app --host 0.0.0.0 --port 8080 --log-level debug
```

### Frontend não carrega
```bash
# Verificar se o servidor está rodando
curl -I http://localhost:3000

# Verificar permissões do diretório
ls -la chat/
```

## 🧪 Testes

```bash
# Rodar testes
pytest

# Com cobertura
pytest --cov=.

# Testes específicos
pytest tests/test_api.py
```

## 📚 API Endpoints

### Principais Endpoints

- `GET /docs` - Documentação Swagger
- `GET /health` - Status do servidor
- `POST /chat` - Enviar mensagem
- `GET /history` - Histórico de conversas
- `POST /clear` - Limpar histórico

### Exemplo de Requisição

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, como posso ajudar?"}'
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 💡 Suporte

- Issues: [GitHub Issues](https://github.com/seu-usuario/seu-repo/issues)
- Documentação: http://localhost:8080/docs
- Email: support@example.com

## 🎯 Roadmap

- [ ] Autenticação JWT
- [ ] WebSockets para tempo real
- [ ] Dashboard administrativo
- [ ] Exportação de conversas
- [ ] Integração com mais LLMs
- [ ] Suporte a múltiplos idiomas
- [ ] Deploy com Docker

---

**Desenvolvido com ❤️ usando Neo4j, Claude SDK e FastAPI**