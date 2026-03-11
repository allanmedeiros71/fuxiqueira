# Contexto do Projeto: Sistema de Acompanhamento de Bioimpedância

## 1. Visão Geral
O projeto é um sistema web responsivo, com prioridade de uso em dispositivos móveis (Mobile-First), destinado ao registro e acompanhamento de evolução física através de dados fornecidos por uma balança de bioimpedância e registros fotográficos. O sistema permitirá múltiplos usuários, cada um com seu próprio login, histórico de medições e visualização de progresso através de gráficos e galeria de evolução.

## 2. Stack de Tecnologia
- **Backend:** Python com Django.
- **Frontend:** HTML/CSS puro com HTMX e uma biblioteca de gráficos leve (ex: Chart.js). Framework CSS: TailwindCSS (focado em mobile).
- **Banco de Dados:** PostgreSQL.
- **Armazenamento de Mídia:** Armazenamento local na VPS utilizando Volumes do Docker (gerenciado pelo Django no diretório `media/`).
- **Infraestrutura/Hospedagem:** VPS (Hostgator), ambiente containerizado utilizando Docker/Podman (via `docker compose`).

## 3. Requisitos Funcionais (Features)
- **Autenticação:** Cadastro de usuário, login, logout e recuperação de senha.
- **Gestão de Perfil:** Registro e edição dos dados básicos do usuário (incluindo metas).
- **Registro de Medições:** Formulário otimizado para celular com suporte a upload de fotos (frente, costas, perfil) capturadas diretamente da câmera.
- **Dashboard/Evolução:** Tela principal exibindo a última medição, gráficos de linha mostrando a evolução histórica e uma galeria comparativa de fotos ("Antes e Depois").

## 4. Estrutura de Dados (Modelos)

### 4.1. Usuário (Custom User Model)
- `nome` (String)
- `email` (String, único)
- `senha` (Hash)
- `data_nascimento` (Date)
- `altura` (Decimal/Float)
- `meta_peso` (Decimal/Float, opcional)
- `meta_gordura` (Decimal/Float, opcional)

### 4.2. Medição de Bioimpedância (Measurement)
- `usuario_id` (FK)
- `data_hora` (DateTime, padrão: now)
- `peso` (Decimal/Float, kg)
- `imc` (Decimal/Float)
- `percentual_gordura` (Decimal/Float, %)
- `percentual_massa_muscular` (Decimal/Float, %)
- `metabolismo_basal` (Integer, kcal)
- `idade_metabolica` (Integer, anos)
- `indice_gordura_visceral` (Integer/Float)
- `foto_frente` (ImageField, salva em `media/fotos/`)
- `foto_perfil` (ImageField, salva em `media/fotos/`)
- `foto_costas` (ImageField, salva em `media/fotos/`)
- `notas` (Text, opcional)

## 5. Diretrizes de Arquitetura e Fluxo de Desenvolvimento

### 5.1. Ambiente de Desenvolvimento Local (VS Code)
- O projeto deve obrigatoriamente utilizar um ambiente virtual Python (`venv`) para o desenvolvimento local.
- **Setup Local:** Executar `python3 -m venv venv` e ativar com `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows) para instalar dependências.
- O VS Code e o agente de IA devem utilizar este interpretador virtual para garantir o correto funcionamento do IntelliSense, linting e formatação de código do Django.

### 5.2. Dockerização e Deploy
- O ambiente de produção/VPS será orquestrado via `docker compose`, utilizando o arquivo `compose.yaml` para subir a aplicação web e o PostgreSQL.
- **Gestão de Arquivos:** As imagens enviadas pelos usuários devem ser salvas no diretório `media/`, mapeado para um Volume persistente no Docker.
- **Compressão de Imagens:** Implementar redimensionamento e compressão das imagens no backend (Pillow) antes do salvamento.
- **Rotinas de Backup:** Configurar rotina de backup (ex: cron job) na VPS para salvar o volume de mídia e o dump do banco de dados (enviando para o Google Drive ou similar).
- **Variáveis de Ambiente:** Credenciais gerenciadas estritamente via arquivo `.env`.

## 6. Instruções Específicas para o Agente de IA
- Sempre que adicionar uma nova dependência ao projeto, lembre-se de instruir a atualização do `requirements.txt` no ambiente virtual local e reconstruir a imagem Docker se necessário.
- Configure o `MEDIA_URL` e o `MEDIA_ROOT` no `settings.py` para servir arquivos estáticos e de mídia durante o desenvolvimento (via Django) e produção (via WhiteNoise/Nginx).
- Implemente views lidando com `enctype="multipart/form-data"` para uploads via HTMX.
- A interface de upload deve focar no acesso nativo à câmera (`accept="image/*" capture="camera"`).
- Otimize o carregamento de imagens no frontend (lazy loading).