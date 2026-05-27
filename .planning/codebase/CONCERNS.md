# Codebase Concerns

**Analysis Date:** 2026-05-27

## Tech Debt

**Upload de fotos incompleto nas views:**
- Issue: `MeasurementForm` inclui `foto_frente`, `foto_perfil` e `foto_costas`, e os templates usam `enctype="multipart/form-data"`, mas `adicionar_medicao` e `editar_medicao` instanciam o form apenas com `request.POST` — nunca passam `request.FILES`.
- Files: `measurements/views.py` (linhas ~221–276), `measurements/forms.py`, `templates/measurements/adicionar_medicao.html`, `templates/measurements/editar_medicao.html`
- Impact: Fotos enviadas pelo usuário são descartadas silenciosamente; galeria “antes/depois” no dashboard permanece vazia apesar da UI prometer upload.
- Fix approach: Usar `MeasurementForm(request.POST, request.FILES)` (e o mesmo na edição); adicionar teste de integração que posta um arquivo e verifica `Measurement.foto_*`.

**Documentação de status desatualizada:**
- Issue: `PROJECT_STATUS.md` marca `meta_peso`, `meta_gordura` e campos de foto como pendentes, mas já existem em `accounts/models.py`, migração `accounts/migrations/0002_*` e `measurements/migrations/0002_*`.
- Files: `PROJECT_STATUS.md`, `accounts/models.py`, `measurements/models.py`
- Impact: Planejamento e onboarding confusos; risco de reimplementar features já existentes.
- Fix approach: Atualizar tabelas de status e roadmap para refletir o código atual; apontar pendências reais (upload funcional, compressão Pillow, backup).

**Templates duplicados de autenticação:**
- Issue: Existem pares paralelos (`login.html` / `login_standalone.html`, `signup.html` / `signup_standalone.html`); as views ativas usam apenas `*_standalone.html`.
- Files: `accounts/views.py`, `templates/accounts/login.html`, `templates/accounts/login_standalone.html`, `templates/accounts/signup.html`, `templates/accounts/signup_standalone.html`
- Impact: Manutenção duplicada e divergência visual/funcional entre rotas.
- Fix approach: Remover templates mortos ou unificar em um único conjunto referenciado pelas views.

**HTMX configurado mas pouco usado:**
- Issue: `templates/base.html` carrega HTMX via CDN; views retornam `JsonResponse` para `HX-Request`, porém a maior parte dos formulários faz POST HTML tradicional.
- Files: `templates/base.html`, `measurements/views.py`
- Impact: Complexidade sem benefício claro; dependência externa (unpkg) em produção.
- Fix approach: Ou adotar `hx-*` de forma consistente nos formulários de medição, ou remover HTMX até haver caso de uso.

**Pillow instalado sem pipeline de imagem:**
- Issue: `requirements.txt` inclui `Pillow==10.1.0`, mas não há redimensionamento, validação de tipo/tamanho nem compressão no `save()` do modelo — contrário a `context.md` §5.2.
- Files: `requirements.txt`, `measurements/models.py`, `context.md`
- Impact: Disco e banda crescem com uploads grandes; superfície para arquivos maliciosos disfarçados de imagem.
- Fix approach: Validar MIME/dimensões em `MeasurementForm.clean_*` ou signal `pre_save`; redimensionar antes de gravar em `media/`.

**Interpretações clínicas embutidas em view monolítica:**
- Issue: `get_interpretacoes()` em `measurements/views.py` (~60 linhas) codifica faixas de IMC, gordura, massa muscular etc. sem distinção por sexo/idade e com tom de orientação médica.
- Files: `measurements/views.py`, `templates/measurements/dashboard.html`
- Impact: Difícil testar e evoluir regras; risco de conselhos inadequados para parte dos usuários.
- Fix approach: Extrair para módulo `measurements/interpretations.py` com testes unitários; adicionar disclaimer no template; parametrizar faixas no futuro.

## Known Bugs

**Conflito de rota `/admin/`:**
- Symptoms: Link “Administração” (`{% url 'admin' %}`) aponta para `/admin/`, mas `bioimpedancia/urls.py` registra `django.contrib.admin` em `path('admin/', ...)` antes do `include` de `measurements.urls`, que também define `path("admin/", views.admin_view, name="admin")`.
- Files: `bioimpedancia/urls.py`, `measurements/urls.py`, `templates/base.html`, `templates/measurements/admin.html`
- Trigger: Staff/superuser acessa `/admin/` ou clica no menu de administração customizado.
- Workaround: Usar apenas o Django Admin em `/admin/` e ignorar `admin.html`, ou renomear a rota customizada (ex.: `/gestao-usuarios/`) e atualizar `name=` e templates.

**Aprovação/rejeição de usuário aceita GET:**
- Symptoms: `aprovar_usuario` e `rejeitar_usuario` não usam `@require_POST`; um GET autenticado como staff poderia ativar ou apagar usuário sem formulário.
- Files: `measurements/views.py` (funções ~46–61)
- Trigger: Requisição GET para `/admin/aprovar/<id>/` ou `/admin/rejeitar/<id>/` (ex.: prefetch de link, bookmark mal formado, ou ataque induzido).
- Workaround: Templates já usam POST com CSRF; mitigar adicionando `@require_POST` e retorno 405 para GET.

**Troca de senha redireciona para login sem invalidar sessão de forma explícita:**
- Symptoms: Após `PasswordChangeForm.save()`, redirect para `login` sem `update_session_auth_hash` nem `logout()` — sessão antiga pode permanecer válida até expirar.
- Files: `measurements/views.py` (`trocar_senha`), `templates/measurements/trocar_senha.html`
- Trigger: Usuário altera senha em `/trocar-senha/` e espera que todas as sessões sejam encerradas.
- Workaround: Documentar que o usuário deve sair manualmente; corrigir com `update_session_auth_hash` ou `logout(request)` após save.

**Lógica “primeira medição” frágil no dashboard:**
- Symptoms: `primeira_medicao = user.medicoes.last() if user.medicoes.count() > 1 else None` — com ordenação `-data_hora`, `.last()` é a medição mais antiga, mas `count() > 1` omite comparação quando há exatamente uma medição com fotos.
- Files: `measurements/views.py` (`dashboard`)
- Trigger: Usuário com uma única medição e fotos não vê bloco “antes/depois” esperado.
- Workaround: Nenhum documentado no código.

## Security Considerations

**Configuração insegura por padrão em desenvolvimento:**
- Risk: `SECRET_KEY` e `DEBUG=True` são defaults em `bioimpedancia/settings.py` via `python-decouple`; exposição de tracebacks e cookies inseguros se `.env` não for configurado em produção.
- Files: `bioimpedancia/settings.py`, `.env.example`
- Current mitigation: `.env` está no `.gitignore`; Docker Compose define `DEBUG=False` para o serviço `web`.
- Recommendations: Falhar no boot se `DEBUG=True` e `SECRET_KEY` contiver o valor default em ambiente de produção; documentar checklist de deploy.

**Segredos embutidos no Docker Compose:**
- Risk: `SECRET_KEY`, `DB_PASSWORD` e credenciais Postgres aparecem em texto claro em `docker-compose.yml` (adequado só para dev local).
- Files: `docker-compose.yml`
- Current mitigation: Nenhuma para produção — arquivo versionado.
- Recommendations: Usar `env_file: .env` e placeholders; nunca commitar valores de produção.

**Mídia de fotos corporais servida publicamente:**
- Risk: `nginx.conf` expõe `location /media/` sem autenticação; URLs previsíveis (`/media/fotos/YYYY/MM/...`) permitem acesso a imagens sensíveis se o path vazar.
- Files: `nginx.conf`, `bioimpedancia/urls.py` (static media em `DEBUG`), `measurements/models.py` (`upload_to='fotos/%Y/%m/'`)
- Current mitigation: Apenas obscuridade de URL; `media/` no `.gitignore` para o repositório.
- Recommendations: Servir mídia via view autenticada (`@login_required` + `FileResponse`) ou signed URLs; considerar LGPD (dados de saúde/imagem corporal).

**Ausência de headers HTTPS / cookies seguros:**
- Risk: Não há `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_*` em `bioimpedancia/settings.py`.
- Files: `bioimpedancia/settings.py`, `nginx.conf` (proxy headers presentes, mas app não força HTTPS)
- Current mitigation: Depende do terminador TLS na VPS (não codificado).
- Recommendations: Bloco de settings condicional `if not DEBUG` com flags de segurança Django 4.2.

**`cookies.txt` versionado no Git:**
- Risk: Arquivo rastreado pelo repositório (`git ls-files cookies.txt`) — tipicamente export de cookies de sessão de testes; vazamento de sessão se contiver tokens válidos.
- Files: `cookies.txt`, `.gitignore` (não ignora `cookies.txt`)
- Current mitigation: Nenhuma.
- Recommendations: Remover do histórico Git, adicionar `cookies.txt` ao `.gitignore`, nunca commitar artefatos de sessão.

**PostgreSQL exposto na máquina host:**
- Risk: Serviço `db` publica `5432:5432` em `docker-compose.yml`.
- Files: `docker-compose.yml`
- Current mitigation: Senha fraca apenas para dev.
- Recommendations: Remover mapeamento de porta em produção ou restringir firewall.

**Cadastro aberto sem rate limiting:**
- Risk: `SignUpView` em `accounts/views.py` aceita cadastros ilimitados; usuários inativos acumulam até aprovação.
- Files: `accounts/views.py`, `accounts/forms.py`
- Current mitigation: `is_active=False` até aprovação staff.
- Recommendations: Throttling (django-ratelimit), CAPTCHA ou convite; monitorar fila em `admin_view`.

**CSRF trusted origins hardcoded:**
- Risk: `CSRF_TRUSTED_ORIGINS` lista localhost e porta `45897` fixa em `bioimpedancia/settings.py` — deploy em domínio real exige alteração manual fácil de esquecer.
- Files: `bioimpedancia/settings.py`
- Current mitigation: Parcial para dev/preview.
- Recommendations: Ler origens de variável de ambiente (lista separada por vírgula).

## Performance Bottlenecks

**Histórico carrega todas as medições no gráfico:**
- Problem: `historico()` faz `request.user.medicoes.all()` e serializa todos os pontos em JSON para Chart.js.
- Files: `measurements/views.py` (`historico`), `templates/measurements/historico.html`
- Cause: Sem paginação nem limite (dashboard limita a 30; histórico não).
- Improvement path: Limitar query (ex.: últimos 100), paginar tabela, ou endpoint AJAX com intervalo de datas.

**Consultas repetidas no dashboard:**
- Problem: `user.medicoes.first()`, `.last()`, `.count()`, `.filter(...).first()` e slice `[:30]` geram múltiplas queries por request.
- Files: `measurements/views.py` (`dashboard`)
- Cause: Ausência de `select_related` / agregação única.
- Improvement path: Uma query ordenada reutilizada em memória ou `Prefetch` objetivo.

**CDN externo para Tailwind, Chart.js e HTMX:**
- Problem: `templates/base.html` depende de unpkg/jsdelivr em runtime.
- Files: `templates/base.html`
- Cause: Sem vendor local ou build de assets.
- Improvement path: Pin de assets em `static/` para latência e disponibilidade offline na VPS.

## Fragile Areas

**Painel administrativo customizado vs Django Admin:**
- Files: `measurements/views.py` (`admin_view`, `aprovar_usuario`, `rejeitar_usuario`), `bioimpedancia/urls.py`, `templates/measurements/admin.html`
- Why fragile: Colisão de URL `/admin/` e duas UIs de administração com capacidades sobrepostas (aprovação só no template customizado, inacessível se rota errada).
- Safe modification: Renomear rotas customizadas para prefixo `/gestao/`; adicionar testes de URL; smoke test de aprovação POST.
- Test coverage: Nenhum teste automatizado.

**Formulário de medição híbrido (manual + ModelForm):**
- Files: `templates/measurements/adicionar_medicao.html`, `measurements/views.py`
- Why fragile: Template declara inputs HTML manuais além dos widgets do form; qualquer renomeação de campo no model pode quebrar binding silenciosamente.
- Safe modification: Renderizar exclusivamente via `{{ form }}` / crispy ou garantir paridade de `name=` com `MeasurementForm.Meta.fields`.
- Test coverage: Nenhum.

**Cálculo de idade e IMC espalhado:**
- Files: `accounts/models.py` (`idade`), `measurements/models.py` (`save`), `measurements/views.py` (IMC em views e `get_interpretacoes`)
- Why fragile: Altura zero ou ausente não é validada de forma central; divisão por altura em vários pontos.
- Safe modification: Validador em `UserProfileForm` / `MeasurementForm`; propriedade `imc_calculado` no model.
- Test coverage: Nenhum.

## Scaling Limits

**Armazenamento de mídia em volume Docker local:**
- Current capacity: Volume `media_volume` sem quota nem lifecycle.
- Limit: Disco da VPS enche com fotos full-size triplas por medição.
- Scaling path: Compressão Pillow, política de retenção, object storage (S3-compatible) conforme `context.md`.

**Banco único PostgreSQL sem réplicas:**
- Current capacity: Instância `postgres:15` no Compose.
- Limit: Sem backup automatizado no código (pendente em `context.md` e `PROJECT_STATUS.md`).
- Scaling path: `pg_dump` cron + off-site backup; connection pooling se tráfego crescer.

**Processo web single-container Gunicorn:**
- Current capacity: Um worker Gunicorn no `docker-compose.yml` (`command: ... gunicorn ...`).
- Limit: Requisições CPU-bound (gráficos JSON grandes) bloqueiam workers.
- Scaling path: `--workers` proporcional a CPUs; separar servir mídia do app.

## Dependencies at Risk

**Django 4.2.7 pin fixo:**
- Risk: Linha 4.2.x deixa de receber patches de segurança após fim de suporte estendido; sem CI verificando advisories.
- Impact: Vulnerabilidades web não corrigidas automaticamente.
- Migration plan: Acompanhar Django 4.2 LTS schedule; planejar upgrade para 5.x com suite de testes (hoje inexistente).

**Pillow 10.1.0:**
- Risk: Versão antiga pode acumular CVEs em decoders de imagem.
- Impact: Vetores via upload malicioso quando upload for corrigido.
- Migration plan: Atualizar para última 10.x/11.x compatível após adicionar validação de upload.

**psycopg2-binary:**
- Risk: Pacote binary dificulta builds em algumas arquiteturas; alternativa `psycopg[binary]` na stack moderna.
- Impact: Baixo em VPS amd64 típica.
- Migration plan: Opcional em refactor de dependências.

## Missing Critical Features

**Suite de testes automatizados:**
- Problem: Não existem `tests.py`, `test_*.py` nem configuração pytest/unittest no repositório.
- Blocks: Refatoração segura de auth, upload, URLs e interpretações; CI de qualidade.

**Compressão e backup de mídia/DB:**
- Problem: Exigidos em `context.md` §5.2; não implementados.
- Blocks: Deploy confiável na Hostgator/VPS descrita no README.

**Proteção de mídia e conformidade (LGPD):**
- Problem: Dados de composição corporal e fotos sem política de privacidade, retenção ou exportação no código.
- Blocks: Uso comercial/multi-usuário com requisitos legais brasileiros.

**Metas no dashboard:**
- Problem: `meta_peso` e `meta_gordura` existem no model e formulários, mas não há visualização de progresso em relação às metas no dashboard (apenas comparação entre duas medições).
- Blocks: Feature de “meta vs atual” prometida implicitamente no perfil.

## Test Coverage Gaps

**Autenticação e ciclo de aprovação:**
- What's not tested: Cadastro inativo, login bloqueado, aprovação/rejeição staff, reset de senha.
- Files: `accounts/views.py`, `accounts/forms.py`, `measurements/views.py`, `accounts/urls.py`
- Risk: Regressões impedem novos usuários de entrar ou permitem acesso indevido.
- Priority: High

**CRUD de medições e autorização por usuário:**
- What's not tested: `get_object_or_404(..., usuario=request.user)` em editar/excluir; cálculo de IMC; exclusão HTMX.
- Files: `measurements/views.py`, `measurements/models.py`
- Risk: IDOR se filtro por usuário for removido acidentalmente.
- Priority: High

**Upload de imagens (quando corrigido):**
- What's not tested: POST multipart, limites de tamanho, tipos MIME.
- Files: `measurements/views.py`, `measurements/forms.py`
- Risk: Armazenamento quebrado ou aceitação de arquivos perigosos.
- Priority: High

**Resolução de URLs `/admin/`:**
- What's not tested: Qual view responde; `reverse('admin')` vs painel customizado.
- Files: `bioimpedancia/urls.py`, `measurements/urls.py`
- Risk: Painel de aprovação inutilizável em produção.
- Priority: High

**Interpretações e gráficos:**
- What's not tested: Limites de `get_interpretacoes`, serialização JSON de `chart_data`.
- Files: `measurements/views.py`
- Risk: Erros 500 com dados extremos ou timezone.
- Priority: Medium

---

*Concerns audit: 2026-05-27*
