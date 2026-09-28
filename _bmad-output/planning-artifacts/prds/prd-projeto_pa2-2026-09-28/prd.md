---
title: CodeView - PRD Onda 1 (MVP Core)
created: 2026-09-28
updated: 2026-09-28
status: final
---

# PRD: CodeView — Onda 1 (MVP Core)

## 0. Document Purpose

Este documento de requisitos de produto (PRD) estabelece a especificação funcional, comportamental e técnica da **Onda 1 (MVP Core)** do **CodeView**. Ele traduz a visão consolidada no [brief.md](file:///c:/Users/Karol/Desktop/PA2/projeto_pa2/_bmad-output/planning-artifacts/briefs/brief-projeto_pa2-2026-09-14/brief.md) em requisitos executáveis para engenharia de software e design de interfaces. O documento serve como contrato de alinhamento entre Product Management (John), Business Analysis (Mary), Arquitetura/Engenharia (Django backend) e stakeholders do projeto (Karol Sabino e Leandro Moura).

---

## 1. Vision

O **CodeView** é uma plataforma web de microaprendizado dinâmico de programação que substitui o formato estático e cansativo de tutoriais longos por uma experiência imersiva e visual de **vídeos curtos verticais (formato pílula/TikTok)**, focados na resolução prática de problemas reais de código. 

A plataforma combate a sobrecarga cognitiva, a frustração de iniciantes com configurações complexas e o esgotamento de profissionais ocupados. Na **Onda 1**, validamos a hipótese central de engajamento: *se desenvolvedores e estudantes de tecnologia consomem ativamente pílulas de conhecimento técnico em vídeo vertical filtradas por linguagem, com fricção zero de entrada e uma experiência web fluida.*

---

## 2. Target User

### 2.1 Jobs To Be Done (JTBD)
* **JTBD-1 (Iniciante / Estudante - "Carlinhos"):** Quando tenho pequenos intervalos de tempo no meu dia (intervalo da faculdade, transporte, pausas), quero consumir dicas práticas e macetes rápidos de programação (ex: Python) em formato visual e direto ao ponto, para fixar conceitos essenciais sem cansaço mental.
* **JTBD-2 (Identidade / Portfólio Vivo - "Carlinhos"):** Quando estudo e aplico tecnologia, quero ter um perfil centralizado onde minhas tecnologias de interesse e minha jornada fiquem visíveis, para construir autoridade profissional sem precisar preencher currículos tradicionais em PDF.
* **JTBD-3 (Profissional Ocupado / Empreendedor - "Leozinho"):** Quando preciso me atualizar rapidamente sobre novas abordagens de código sem perder 40 minutos em aulas teóricas prolixas, quero filtrar vídeos verticais objetivos e específicos de uma tecnologia para aplicar no meu projeto imediatamente.
* **JTBD-4 (Transparência e Confiança - Ambos):** Quando crio uma conta em uma nova plataforma de ensino, quero clareza total sobre o uso dos meus dados pessoais (LGPD), garantindo segurança e controle sobre a minha privacidade.

### 2.2 Non-Users (v1)
* **Consumidores não-técnicos:** Pessoas sem nenhum interesse em aprender ou aplicar linguagens de programação e tecnologias de desenvolvimento de software.
* **Crianças menores de 13 anos:** Plataforma voltada para jovens e adultos em formação técnica e transição de carreira.
* **Instrutores em busca de monetização direta por visualização:** A plataforma na Onda 1 não possui monetização de criadores por visualizações (sem modelo de Adsense/revenue share).

### 2.3 Key User Journeys

#### UJ-1: Primeiro Acesso, Cadastro e Consentimento LGPD
* **Persona & Contexto:** Carlinhos (19 anos, estudante de Ciência da Computação), acessando a plataforma pelo notebook via navegador desktop para conhecer a novidade.
* **Entry State:** Usuário anônimo na landing/login page do CodeView.
* **Path:**
  1. Carlinhos clica em "Criar Conta".
  2. Preenche Nome, E-mail e Senha (com confirmação).
  3. Visualiza o modal/bloco dos Termos de Uso e Política de Privacidade (LGPD) com checkbox obrigatório de consentimento.
  4. Clica em "Cadastrar".
* **Climax:** A conta é criada instantaneamente, a sessão é autenticada e Carlinhos é redirecionado para a Aba Principal (Feed de Vídeos) com uma mensagem de boas-vindas.
* **Resolution:** Carlinhos está autenticado e pronto para consumir conteúdos.
* **Edge Case:** Se o e-mail já estiver cadastrado ou a senha for fraca, o formulário exibe validação inline em tempo real sem limpar os demais campos preenchidos.

#### UJ-2: Consumo do Feed Vertical e Filtro por Tecnologia
* **Persona & Contexto:** Carlinhos deseja focar exclusivamente em conteúdos de Python para sua aula da noite.
* **Entry State:** Usuário autenticado na Aba Principal.
* **Path:**
  1. Carlinhos visualiza o feed com player vertical centralizado e a barra de filtros de tecnologia no topo/lateral.
  2. Clica na tag/pílula **"Python"**.
  3. O feed recarrega/filtra instantaneamente apenas vídeos catalogados com a tag Python.
  4. Carlinhos assiste ao primeiro vídeo (30 a 60 segundos), visualiza o título, descrição e autor.
  5. Rola para baixo (scroll do mouse ou seta do teclado) e o próximo vídeo da lista carrega com reprodução fluida.
* **Climax:** Carlinhos aprende um macete de list comprehension em menos de 1 minuto sem precisar pausar ou avançar barras de progresso longas.
* **Resolution:** Carlinhos continua navegando pelo feed de Python ou reseta o filtro para ver todas as tecnologias.
* **Edge Case:** Se a tecnologia selecionada não possuir vídeos ativos, o sistema exibe um estado vazio (*empty state*) elegante convidando o usuário a explorar outras tags.

#### UJ-3: Edição e Consulta da Tela de Perfil
* **Persona & Contexto:** Carlinhos quer personalizar seu perfil para registrar sua bio e seus links públicos (GitHub / LinkedIn).
* **Entry State:** Usuário autenticado navegando no CodeView.
* **Path:**
  1. Carlinhos clica no avatar/ícone de perfil na barra de navegação superior.
  2. Acessa a página de Perfil (`/profile/`).
  3. Clica em "Editar Perfil".
  4. Atualiza foto de avatar, preenche a bio ("Estudante apaixonado por Python e Django") e insere link do GitHub.
  5. Clica em "Salvar Alterações".
* **Climax:** O perfil é atualizado imediatamente com feedback visual de sucesso e exibe os dados consolidados.
* **Resolution:** O perfil de Carlinhos reflete sua identidade técnica atualizada.

#### UJ-4: Exploração Rápida de Conteúdo por Empreendedor Técnico
* **Persona & Contexto:** Leozinho (32 anos, empresário de tecnologia), quer ver rapidamente quais linguagens estão com conteúdo ativo na plataforma.
* **Entry State:** Usuário autenticado acessando pelo navegador.
* **Path:**
  1. Acessa a Aba Principal.
  2. Alterna os filtros rápidos entre as tecnologias disponíveis (ex: Python, JavaScript, Banco de Dados).
  3. Assiste a um vídeo de boas práticas de arquitetura.
* **Climax:** Em 3 minutos, obtém um insight prático para discutir com seu time.
* **Resolution:** Sai da plataforma satisfeito e planeja retornar para acompanhar novos tópicos.

---

## 3. Glossary

* **Dev / Usuário:** Qualquer usuário cadastrado e autenticado na plataforma (estudante, entusiasta ou profissional sênior).
* **Micro-vídeo:** Conteúdo audiovisual técnico em formato vertical (aspect ratio 9:16), com duração curta (geralmente entre 30 e 90 segundos), focado em uma única dica, conceito ou resolução de código.
* **Feed Vertical:** Mecanismo de exibição contínua de micro-vídeos em formato coluna vertical com transição fluida entre conteúdos (navegação via scroll/teclado).
* **Tecnologia / Tag:** Categoria técnica associada ao vídeo (ex: `Python`, `JavaScript`, `SQL`, `Django`). Permite a filtragem temática direta do feed.
* **Perfil de Usuário:** Página individual do Dev contendo informações de identificação, bio, links externos e, em ondas futuras, conquistas e certificados.
* **Termo de Consentimento LGPD:** Registro explícito, com data/hora e versão, da anuência do usuário ao tratamento de dados pessoais conforme a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).

---

## 4. Features (Onda 1)

### 4.1 Autenticação e Gestão de Contas

**Description:**
Módulo responsável por permitir que novos usuários se cadastrem, realizem login com segurança através de sessão web no Django, recuperem senhas esquecidas e finalizem suas sessões. Realiza UJ-1.

**Functional Requirements:**

#### FR-1: Cadastro de Novo Usuário com E-mail Único
O visitante anônimo pode criar uma conta na plataforma fornecendo Nome Completo, E-mail válido e Senha segura.
* **Consequences (testable):**
  * O sistema rejeita o cadastro com erro `400` caso o e-mail já esteja cadastrado no banco.
  * O sistema exige senha com no mínimo 8 caracteres, contendo pelo menos 1 número ou caractere especial.
  * Ao submeter dados válidos e com aceite LGPD marcado, o sistema cria o registro no modelo `User` e redireciona para a Aba Principal com status HTTP `200/302`.
* **Out of Scope:** Login social via OAuth (Google/GitHub) na Onda 1 (reservado para ondas futuras).

#### FR-2: Login com Autenticação de Sessão
O usuário cadastrado pode autenticar-se utilizando seu e-mail e senha.
* **Consequences (testable):**
  * Credenciais corretas autenticam a sessão (`request.user.is_authenticated == True`) e criam cookie seguro de sessão (`sessionid`).
  * Credenciais incorretas exibem mensagem de erro genérica ("E-mail ou senha inválidos") sem indicar se o e-mail existe no banco.
  * Tentativas repetidas com erro sofrem rate-limiting preventivo.

#### FR-3: Logout de Sessão
O usuário autenticado pode encerrar sua sessão a qualquer momento através de botão explícito no menu superior.
* **Consequences (testable):**
  * Ao acionar logout, a sessão do Django é invalidada (`logout(request)`), o cookie é limpo e o usuário é redirecionado para a tela de login/home pública.

#### FR-4: Recuperação de Senha via E-mail
O usuário que esqueceu a senha pode solicitar a redefinição informando seu e-mail.
* **Consequences (testable):**
  * O sistema gera um token seguro e temporário (expiração em 24h) e dispara e-mail com link de redefinição.
  * Na Onda 1 (ambiente local/desenvolvimento), o envio de e-mail é simulado via console backend (`django.core.mail.backends.console.EmailBackend`).

---

### 4.2 Consentimento e Termos de Privacidade (LGPD)

**Description:**
Módulo que garante conformidade formal com a LGPD, exigindo leitura/aceite dos termos de privacidade antes de liberar o uso total da plataforma e mantendo trilha de auditoria do consentimento. Realiza UJ-1.

**Functional Requirements:**

#### FR-5: Aceite Obrigatório dos Termos no Cadastro
No fluxo de criação de conta, o formulário deve conter um link clicável para leitura dos Termos de Uso e Política de Privacidade e uma caixa de seleção (*checkbox*) de aceite obrigatório.
* **Consequences (testable):**
  * O formulário não permite submissão se a caixa de aceite não estiver marcada, exibindo alerta: *"Você precisa concordar com os Termos de Privacidade para continuar"*.
  * O texto completo dos termos deve estar acessível em rota dedicada pública (`/terms/` e `/privacy/`) ou modal sem descarregar o formulário.

#### FR-6: Registro e Auditoria do Consentimento
O sistema deve persistir a evidência do consentimento de cada usuário.
* **Consequences (testable):**
  * Cada aceite gera um registro no modelo `UserConsent` gravando: `user_id`, `terms_version` (ex: "v1.0-2026"), `accepted_at` (timestamp UTC) e `ip_address`.
  * Usuários que não possuem registro de consentimento ativo para a versão vigente são interceptados por middleware e redirecionados para confirmação dos termos.

---

### 4.3 Shell de Navegação e Aba Principal (Layout Base)

**Description:**
Estrutura visual base da aplicação web desktop responsiva. Fornece cabeçalho superior (navbar), menu de navegação lateral ou superior, área de conteúdo principal e rodapé. Realiza UJ-1, UJ-2, UJ-3.

**Functional Requirements:**

#### FR-7: Layout Base Responsivo (Desktop-first otimizado)
A aplicação deve carregar um layout consistente construído em templates Django baseados em componentes semânticos de HTML5 e CSS.
* **Consequences (testable):**
  * O layout renderiza de forma centralizada e sem quebras visuais em resoluções de desktop (1920x1080, 1366x768) e adapta-se elegantemente em telas menores (tablets e smartphones).
  * O cabeçalho apresenta o logotipo do **CodeView**, atalho para a Aba Principal, atalho para o Perfil e menu de usuário com Logout.

#### FR-8: Indicador de Estado de Autenticação na Navbar
A barra de navegação deve alternar componentes de acordo com o estado da sessão.
* **Consequences (testable):**
  * Usuário anônimo: exibe botões "Entrar" e "Cadastrar-se".
  * Usuário autenticado: exibe avatar, primeiro nome do dev e menu dropdown com "Meu Perfil" e "Sair".

#### FR-9: Roteamento da Aba Principal
A rota raiz autenticada (`/` ou `/feed/`) deve carregar a Aba Principal como ponto de entrada padrão.
* **Consequences (testable):**
  * Acesso à raiz sem autenticação redireciona para `/login/?next=/feed/`.
  * Acesso autenticado carrega imediatamente o feed de vídeos.

---

### 4.4 Perfil do Aluno / Dev (Portfólio Vivo)

**Description:**
Página dedicada de exibição e edição dos dados de perfil do usuário. No CodeView, o perfil é o portfólio vivo do estudante, eliminando currículos em anexo. Realiza UJ-3.

**Functional Requirements:**

#### FR-10: Visualização do Perfil Pessoal
O usuário autenticado pode acessar a rota `/profile/` para visualizar suas informações pessoais e profissionais.
* **Consequences (testable):**
  * Exibe: Nome Completo, E-mail, Avatar, Bio, Links externos (GitHub, LinkedIn) e Data de Entrada na plataforma ("Membro desde MM/AAAA").
  * Exibe contadores de atividades (na Onda 1: vídeos assistidos / tecnologias exploradas).

#### FR-11: Edição de Perfil e Atualização de Avatar
O usuário pode alterar seus dados cadastrais e foto de perfil através de formulário dedicado.
* **Consequences (testable):**
  * O upload de avatar aceita arquivos de imagem válidos (JPG, PNG, WebP) com limite máximo de 2MB.
  * O sistema redimensiona/sanitiza a imagem para padrão 300x300px antes de persistir.
  * O usuário pode atualizar sua bio (máximo 250 caracteres) e URLs externas (com validação de formato de URL).

#### FR-12: Bloqueio Estrito de Upload de Currículo (Regra de Negócio)
A interface de perfil e a API **não** fornecem campo de upload de arquivos PDF/DOCX de currículo.
* **Consequences (testable):**
  * Não existe endpoint ou campo de formulário para anexar currículo. A validação de competências baseia-se exclusivamente no registro das interações na própria plataforma.

---

### 4.5 Feed de Vídeos Verticais com Filtro por Tecnologia

**Description:**
Funcionalidade central de consumo de conteúdo da Onda 1. Consiste em uma interface imersiva de micro-vídeos em formato vertical (estilo pílula de conhecimento), com controles de reprodução e barra de filtragem dinâmica por tecnologia. Realiza UJ-2, UJ-4.

**Functional Requirements:**

#### FR-13: Renderização do Player de Vídeo Vertical
O feed exibe os vídeos em um container centralizado otimizado para aspect ratio 9:16.
* **Consequences (testable):**
  * O player HTML5 reproduz arquivos de vídeo (MP4/H.264 ou WebM) de forma nativa e responsiva.
  * O vídeo exibe sobreposto na parte inferior: Título do vídeo, descrição sucinta, tag da linguagem e nome do autor/instrutor.
  * Controles visíveis: Botão Play/Pause, controle de mudo/volume e indicador discreto de progresso.

#### FR-14: Navegação Vertical entre Vídeos (Scroll / Teclas)
O usuário pode transitar entre os vídeos disponíveis na lista de reprodução através de rolagem ou teclas de atalho (seta para cima / seta para baixo).
* **Consequences (testable):**
  * Ao rolar para o próximo vídeo, o vídeo anterior pausa automaticamente e o novo vídeo inicia a reprodução (com áudio ativado se o usuário já tiver interagido com o player).
  * O carregamento do próximo vídeo é realizado com pré-carregamento (*lazy loading*) para evitar travamentos.

#### FR-15: Filtragem Dinâmica por Tecnologia
O topo do feed exibe uma lista horizontal de tecnologias disponíveis (ex: `Todos`, `Python`, `JavaScript`, `Django`, `SQL`).
* **Consequences (testable):**
  * Ao clicar em uma tag (ex: "Python"), o feed atualiza imediatamente a listagem para conter apenas vídeos associados a essa tecnologia.
  * A URL reflete o filtro ativo (ex: `/feed/?tech=python`) permitindo compartilhamento e recarregamento sem perder o contexto.
  * O filtro `Todos` exibe o feed cronológico/relevante geral.

#### FR-16: Curadoria e Gestão de Conteúdo via Django Admin (Onda 1)
O cadastro, edição e publicação de novos micro-vídeos é realizado com exclusividade pela equipe administrativa através do painel `/admin/` do Django.
* **Consequences (testable):**
  * Apenas usuários com `is_staff == True` possuem permissão para criar registros no modelo `Video`.
  * Não há interface pública de envio de vídeos para usuários comuns na Onda 1.

---

## 5. Non-Goals (Explicit)

Os seguintes itens estão **explicitamente fora de escopo** na Onda 1 e nas diretrizes gerais do produto:

* **SEM Sistema de Seguidores:** Não haverá botões de "Seguir", métricas de contagem de seguidores ou feeds exclusivos de quem sigo. Evita vaidade social e queries relacionais complexas de grafos sociais.
* **SEM Upload de Currículo:** Nenhum upload de arquivo de CV (PDF/Word). O perfil do dev e seu histórico de aprendizado compõem o portfólio vivo.
* **SEM Monetização de Criadores por View:** Sem divisão de receita com base em visualizações de vídeos ou programas de afiliados de criadores.
* **SEM Envio de Vídeos por Usuários Comuns:** O catálogo de vídeos da Onda 1 é 100% curado e cadastrado pelos administradores no Django Admin.
* **SEM Editor de Código no Navegador na Onda 1:** Desafios práticos e execução de código interativo no browser fazem parte da **Onda 2**.
* **SEM Mensagens Diretas (DMs) / Chat na Onda 1:** A conexão direta com devs experientes faz parte da **Onda 4**.

---

## 6. MVP Scope (Onda 1)

### 6.1 In Scope
1. **Cadastro, Login, Logout e Recuperação de Senha** (Django Authentication System).
2. **Consentimento LGPD com registro de versão, data e IP** (Modelo `UserConsent`).
3. **Shell de Navegação Web Desktop Responsivo** (Navbar, Sidebar/Top filters, Footer).
4. **Página de Perfil do Aluno** (Visualização e edição de bio, links externos e avatar).
5. **Feed de Micro-Vídeos Verticais (9:16)** com player fluido e navegação por scroll.
6. **Barra de Filtros por Tecnologia** (Python, JavaScript, etc.) com atualização dinâmica.
7. **Painel Django Admin customizado** para gestão de Tags e Vídeos pela equipe.

### 6.2 Out of Scope for MVP (Onda 1)
* Editor de código Monaco / Pyodide no navegador (Onda 2).
* Desafios interativos de código atrelados aos vídeos (Onda 2).
* Mini-cursos com trilhas estruturadas (Onda 3).
* Mensagens Diretas (DMs) e Mentoria 1:1 (Onda 4).
* Emissão de certificados digitais e checkout de pagamento (Onda 5).
* Métricas avançadas de analytics de retenção segundo a segundo (Onda 6+).

---

## 7. Success Metrics

### 7.1 Primary Metrics
* **SM-1 (Eficiência de Cadastro):** Taxa de conclusão de cadastro > 85% dos usuários que iniciam o fluxo, com tempo médio de conclusão inferior a 60 segundos. *Valida FR-1 e FR-5.*
* **SM-2 (Engajamento no Feed):** Mais de 60% das sessões assistem a pelo menos 3 vídeos completos por visita. *Valida FR-13 e FR-14.*
* **SM-3 (Adoção dos Filtros de Tecnologia):** Pelo menos 50% dos usuários ativos utilizam o filtro por linguagem pelo menos uma vez na sessão. *Valida FR-15.*
* **SM-4 (Conformidade LGPD):** 100% dos usuários com contas ativas possuem registro auditável de consentimento ativo na base de dados. *Valida FR-6.*

### 7.2 Counter-Metrics (O Que Não Otimizar)
* **SM-C1 (Tempo de Tela Passivo Indefinido):** O CodeView **não** busca maximizar horas consecutivas de consumo passivo zumbi (como redes sociais puras de entretenimento). O objetivo é micro-aprendizado ágil e objetivo que direcione o aluno para a prática ativa.

---

## 8. Technical Architecture & Data Schema (Adapt-In)

### 8.1 Stack Tecnológica
* **Backend:** Python 3.10+ / Django 5.x / Django REST Framework (DRF).
* **Banco de Dados:** PostgreSQL (produção) / SQLite3 (desenvolvimento local).
* **Frontend:** Django Templates + Tailwind CSS (ou Bootstrap 5) + JavaScript (HTML5 Video API / Alpine.js para controle do feed vertical).
* **Armazenamento de Mídia:** Django Media Storage local (desenvolvimento) / AWS S3 ou Cloudinary (produção).

### 8.2 Modelagem de Dados Inicial (Django Models)

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="E-mail")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.CharField(max_length=250, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consents')
    terms_version = models.CharField(max_length=20, default='v1.0-2026')
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

# videos/models.py
class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

class Video(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    technology = models.ForeignKey(Technology, on_delete=models.PROTECT, related_name='videos')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos')
    duration_seconds = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 9. Cross-Cutting NFRs (Requisitos Não-Funcionais)

* **RNF-1 (Segurança de Credenciais):** Todas as senhas devem ser hasheadas com algoritmos robustos padrão Django (PBKDF2 com SHA256). Proteção CSRF obrigatória em todos os formulários (`{% csrf_token %}`).
* **RNF-2 (Desempenho de Vídeo):** O player deve iniciar a renderização do primeiro frame do vídeo em menos de 1,5 segundos em conexões padrão de banda larga.
* **RNF-3 (Privacidade e LGPD):** Dados pessoais sensíveis não devem ser expostos publicamente. O e-mail do usuário não deve ser exibido em páginas públicas de perfil.
* **RNF-4 (Responsividade da Interface):** A Aba Principal e o Perfil devem manter proporção visual e legibilidade perfeita em resoluções de desktop (1920x1080 até 1280x720) e mobile (375x667 até 430x932).

---

## 10. Open Questions

1. **Armazenamento de Vídeos no MVP:** No ambiente de desenvolvimento local usaremos arquivos locais em `media/videos/`. Para o primeiro deploy em nuvem, utilizaremos Cloudinary (camada gratuita) ou um bucket AWS S3 simples?
2. **Vídeos Iniciais do Catálogo:** Quantos vídeos iniciais de Python e JavaScript iremos cadastrar na base para o teste de lançamento da Onda 1 (recomendação: 5 a 10 vídeos pílula)?

---

## 11. Assumptions Index

* `[ASSUMPTION-1]`: A autenticação principal usará o **E-mail** como identificador de login em vez de username tradicional, facilitando o acesso do usuário.
* `[ASSUMPTION-2]`: O formato dos vídeos cadastrados será estritamente vertical (proporção 9:16, resolução sugerida 1080x1920 ou 720x1280), codificado em MP4 H.264 para compatibilidade com todos os navegadores modernos.
* `[ASSUMPTION-3]`: Na Onda 1, o cadastro de novos vídeos será feito exclusivamente via Django Admin pelos administradores do sistema.
