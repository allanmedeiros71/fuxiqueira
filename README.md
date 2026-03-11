# Sistema de Acompanhamento de Bioimpedância

Um sistema web responsivo para registro e acompanhamento de evolução física através de dados de balança de bioimpedância.

## 🚀 Funcionalidades

- **Autenticação de Usuários**: Cadastro, login e logout
- **Registro de Medições**: Formulário otimizado para mobile com dados da balança
- **Dashboard Interativo**: Visualização da última medição e comparativos
- **Gráficos de Evolução**: Histórico visual com Chart.js
- **Design Mobile-First**: Interface responsiva com TailwindCSS
- **Interações com HTMX**: Atualizações parciais sem recarregar página

## 🛠️ Stack de Tecnologia

- **Backend**: Django 4.2.7 (Python)
- **Frontend**: HTML/CSS, TailwindCSS, HTMX, Chart.js
- **Banco de Dados**: PostgreSQL
- **Deploy**: Docker Compose, Nginx, Gunicorn

## 📋 Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local)
- PostgreSQL (para desenvolvimento local)

## 🚀 Instalação e Execução

### Com Docker (Recomendado)

1. Clone o repositório:
```bash
git clone https://github.com/allanmedeiros71/fuxiqueira.git
cd fuxiqueira
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Suba os containers:
```bash
docker-compose up --build
```

4. Acesse a aplicação em `http://localhost`

### Para Desenvolvimento Local

1. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o banco de dados PostgreSQL e atualize o `.env`

4. Execute as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Crie um superusuário:
```bash
python manage.py createsuperuser
```

6. Execute o servidor:
```bash
python manage.py runserver
```

## 📁 Estrutura do Projeto

```
fuxiqueira/
├── bioimpedancia/          # Configurações do Django
│   ├── settings.py         # Configurações principais
│   ├── urls.py            # URLs principais
│   └── wsgi.py            # WSGI configuration
├── accounts/              # App de autenticação
│   ├── models.py          # Custom User model
│   ├── views.py           # Views de login/cadastro
│   └── forms.py           # Forms de autenticação
├── measurements/          # App de medições
│   ├── models.py          # Model Measurement
│   ├── views.py           # Views de medições
│   └── forms.py           # Forms de medições
├── templates/             # Templates HTML
│   ├── base.html          # Template base
│   ├── accounts/          # Templates de autenticação
│   └── measurements/     # Templates de medições
├── static/               # Arquivos estáticos
├── media/                # Arquivos de mídia
├── Dockerfile            # Configuração do Docker
├── docker-compose.yml    # Orquestração dos containers
├── nginx.conf           # Configuração do Nginx
├── requirements.txt      # Dependências Python
└── manage.py            # Script de gerenciamento Django
```

## 🎯 Uso do Sistema

1. **Cadastro**: Crie sua conta com dados pessoais e altura
2. **Login**: Acesse o sistema com email e senha
3. **Adicionar Medição**: Registre os dados da sua balança de bioimpedância
4. **Dashboard**: Visualize sua evolução com gráficos interativos
5. **Histórico**: Consulte todas as medições anteriores

## 🔧 Configurações

### Variáveis de Ambiente

- `SECRET_KEY`: Chave secreta do Django
- `DEBUG`: Modo de debug (True/False)
- `ALLOWED_HOSTS`: Hosts permitidos
- `DB_*`: Configurações do banco de dados

### Personalização

- Altere `templates/base.html` para customizar o layout
- Modifique `static/css/style.css` para ajustes visuais
- Configure `bioimpedancia/settings.py` para comportamentos específicos

## 🐳 Comandos Docker Úteis

```bash
# Subir os containers
docker-compose up --build

# Subir em background
docker-compose up -d --build

# Ver logs
docker-compose logs -f web

# Executar comandos no container
docker-compose exec web python manage.py shell

# Parar os containers
docker-compose down

# Remover volumes (cuidado!)
docker-compose down -v
```

## 📱 Mobile-First

O sistema foi desenvolvido com prioridade para dispositivos móveis:
- Interface adaptativa com TailwindCSS
- Botões grandes e fáceis de tocar
- Navegação otimizada para telas pequenas
- Formulários simplificados para uso mobile

## 🔒 Segurança

- Proteção CSRF habilitada
- Senhas com hash
- Validação de inputs
- Configurações seguras para produção

## 📊 Features Técnicas

- **HTMX**: Interações dinâmicas sem recarregar página
- **Chart.js**: Gráficos responsivos e interativos
- **PostgreSQL**: Banco de dados robusto
- **Nginx**: Servidor web reverso
- **Gunicorn**: Servidor WSGI para Django

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob licença MIT.

## 📞 Suporte

Para dúvidas ou suporte, abra uma issue no repositório.
