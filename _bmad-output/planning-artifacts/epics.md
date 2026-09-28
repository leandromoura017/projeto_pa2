---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-projeto_pa2-2026-09-28/prd.md
  - _bmad-output/planning-artifacts/briefs/brief-projeto_pa2-2026-09-14/brief.md
---

# CodeView - Epic and Story Breakdown (Onda 1 - MVP Core)

## Overview

Este documento estabelece o detalhamento completo dos **Épicos e Histórias de Usuário** para o desenvolvimento da **Onda 1 (MVP Core)** do **CodeView**. Ele decompõe todos os requisitos funcionais (FR-1 a FR-16), requisitos não-funcionais (RNF-1 a RNF-4) e diretrizes arquiteturais do PRD aprovado em unidades atômicas de trabalho, prontas para execução pela equipe de engenharia.

---

## Requirements Inventory

### Functional Requirements (PRD Onda 1)
* **FR-1**: Cadastro de Novo Usuário com E-mail Único.
* **FR-2**: Login com Autenticação de Sessão Django.
* **FR-3**: Logout de Sessão e Invalidação de Cookie.
* **FR-4**: Recuperação de Senha via E-mail.
* **FR-5**: Aceite Obrigatório dos Termos de Uso e Privacidade (LGPD) no Cadastro.
* **FR-6**: Registro e Auditoria do Consentimento LGPD (Versão, Data/Hora, IP).
* **FR-7**: Layout Base Responsivo (Desktop-first otimizado com Navbar e Shell).
* **FR-8**: Indicador de Estado de Autenticação na Navbar (Visitante vs. Logado).
* **FR-9**: Roteamento Protegido da Aba Principal (`/feed/` ou `/`).
* **FR-10**: Visualização do Perfil Pessoal do Aluno / Dev.
* **FR-11**: Edição de Perfil e Upload de Foto de Avatar (com sanitização).
* **FR-12**: Bloqueio Estrito de Upload de Arquivo de Currículo (Perfil é o portfólio vivo).
* **FR-13**: Renderização do Player de Vídeo Vertical (Aspect Ratio 9:16 nativo HTML5).
* **FR-14**: Navegação Vertical Contínua entre Vídeos via Scroll e Teclas (Cima/Baixo).
* **FR-15**: Filtragem Dinâmica por Tecnologia (Tags na URL e reload reativo).
* **FR-16**: Curadoria e Gestão de Tags e Vídeos via Django Admin (Staff only).

### Non-Functional Requirements
* **RNF-1 (Segurança de Credenciais)**: PBKDF2/SHA256 para senhas e proteção CSRF ativa em todos os formulários.
* **RNF-2 (Desempenho do Player)**: Primeiro frame do vídeo renderizado em < 1.5s em banda larga.
* **RNF-3 (Privacidade de Dados LGPD)**: Não exposição pública de e-mails de usuários; trilha auditável de consentimento.
* **RNF-4 (Responsividade da Interface)**: Adaptação harmoniosa entre Desktop (1920x1080 até 1280x720) e Mobile (375x667 até 430x932).

### Additional / Architecture Requirements
* **Framework**: Python 3.10+ / Django 5.x / Django REST Framework.
* **Starter Architecture**: Estrutura modular em apps Django: `accounts`, `core`, `videos`.
* **Banco de Dados**: SQLite3 (desenvolvimento local) com schema compatível para PostgreSQL.
* **Frontend**: Django Templates + Tailwind CSS (ou Bootstrap 5) + JavaScript Vanilla/Alpine.js para controle interativo do feed.

---

## FR Coverage Map

| Requisito Funcional | Épico Associado | História de Usuário |
| :--- | :--- | :--- |
| **FR-1** (Cadastro) | Épico 1 | Story 1.1 |
| **FR-2** (Login de Sessão) | Épico 1 | Story 1.3 |
| **FR-3** (Logout) | Épico 1 | Story 1.4 |
| **FR-4** (Recuperação de Senha) | Épico 1 | Story 1.5 |
| **FR-5** (Aceite Termos LGPD) | Épico 1 | Story 1.2 |
| **FR-6** (Auditoria de Consentimento) | Épico 1 | Story 1.2 |
| **FR-7** (Layout Base Responsivo) | Épico 2 | Story 2.1 |
| **FR-8** (Estado Auth na Navbar) | Épico 2 | Story 2.1 |
| **FR-9** (Roteamento Protegido Feed) | Épico 2 | Story 2.2 |
| **FR-10** (Visualização do Perfil) | Épico 2 | Story 2.3 |
| **FR-11** (Edição e Avatar) | Épico 2 | Story 2.4 |
| **FR-12** (Bloqueio Upload de CV) | Épico 2 | Story 2.3 |
| **FR-13** (Player 9:16 Vertical) | Épico 3 | Story 3.2, Story 3.3 |
| **FR-14** (Navegação Scroll/Teclas) | Épico 3 | Story 3.4 |
| **FR-15** (Filtro por Tecnologia) | Épico 3 | Story 3.1, Story 3.5 |
| **FR-16** (Curadoria via Django Admin) | Épico 3 | Story 3.1, Story 3.2 |

---

## Epic List

1. **Épico 1: Autenticação Segura e Conformidade com Privacidade (LGPD)**  
   *Objetivo:* Permitir que novos desenvolvedores e estudantes criem suas contas com e-mail, autentiquem-se com segurança, façam logout, recuperem senhas e manifestem consentimento auditável aos termos da LGPD.
2. **Épico 2: Shell Web Desktop e Perfil Vivo do Dev**  
   *Objetivo:* Fornecer a estrutura visual de navegação da plataforma e a página de perfil do usuário, onde o estudante exibe sua identidade e links profissionais sem a barreira de anexar currículos tradicionais.
3. **Épico 3: Feed de Micro-Vídeos Verticais e Descoberta por Tecnologia**  
   *Objetivo:* Entregar a experiência central de microaprendizado do CodeView: exibição contínua de vídeos verticais (9:16), controle de reprodução fluida, filtragem por linguagem de programação e painel administrativo para curadoria de conteúdo.

---

## Épico 1: Autenticação Segura e Conformidade com Privacidade (LGPD)

**Meta do Épico:** Estabelecer a fundação técnica do projeto Django e do gerenciamento de usuários do CodeView, garantindo autenticação resiliente por e-mail e conformidade formal com a legislação de dados pessoais (LGPD).

### Story 1.1: Inicialização do Projeto Django e Cadastro com Modelo Customizado de Usuário
**As a** visitante interessado no CodeView,  
**I want** me cadastrar informando meu nome, e-mail e uma senha forte na aplicação,  
**So that** eu tenha uma conta pessoal segura para acessar a plataforma.

**Acceptance Criteria:**
* **Given** que o ambiente do projeto Django 5.x é inicializado com dependências (`requirements.txt`) e app `accounts`,
* **When** o visitante acessa a página de cadastro (`/accounts/signup/`) e preenche Nome, E-mail não cadastrado e senha com no mínimo 8 caracteres,
* **Then** o sistema cria o usuário no modelo `User` customizado (`AUTH_USER_MODEL` com `email` como identificador de login),
* **And** a senha é criptografada com algoritmo PBKDF2/SHA256,
* **And** se o e-mail já existir no banco de dados, o sistema impede a submissão e exibe o erro inline: *"Este e-mail já está em uso."*

### Story 1.2: Termos de Privacidade e Auditoria de Consentimento LGPD
**As a** usuário que se preocupa com a privacidade dos meus dados,  
**I want** ler e aceitar formalmente os Termos de Uso e Política de Privacidade no ato do cadastro,  
**So that** eu tenha garantia de como meus dados serão tratados e a plataforma cumpra a LGPD.

**Acceptance Criteria:**
* **Given** que o formulário de cadastro é renderizado,
* **When** o usuário tenta submeter os dados sem marcar a caixa de consentimento dos termos,
* **Then** o formulário bloqueia o envio e destaca a mensagem: *"Você precisa concordar com os Termos de Privacidade para continuar"*,
* **And** os links para os termos abrem em um modal ou aba dedicada sem limpar os dados já preenchidos,
* **And** quando o cadastro é concluído com aceite marcado, um registro é criado no modelo `UserConsent` gravando `user_id`, `terms_version` (ex: "v1.0-2026"), `accepted_at` (data/hora UTC) e `ip_address`.

### Story 1.3: Login por E-mail e Gestão de Sessão Web
**As a** estudante ou dev já cadastrado,  
**I want** entrar na minha conta utilizando meu e-mail e senha,  
**So that** eu acesse as áreas exclusivas e meu perfil na plataforma.

**Acceptance Criteria:**
* **Given** que o usuário está na tela de login (`/accounts/login/`),
* **When** ele insere suas credenciais válidas (e-mail e senha),
* **Then** o Django autentica o usuário, inicia a sessão via cookie seguro (`sessionid`),
* **And** redireciona o usuário para a Aba Principal do feed (`/feed/`),
* **And** caso as credenciais estejam erradas, exibe mensagem genérica de erro sem expor se o e-mail existe no banco.

### Story 1.4: Logout e Invalidação de Sessão
**As a** usuário autenticado,  
**I want** encerrar minha sessão através de um botão de logout,  
**So that** meu acesso não permaneça aberto em um computador compartilhado.

**Acceptance Criteria:**
* **Given** que o usuário está logado em qualquer página da aplicação,
* **When** ele clica na opção "Sair" (Logout) no menu superior,
* **Then** o sistema invalida a sessão no servidor (`django.contrib.auth.logout`),
* **And** limpa o cookie de sessão no navegador,
* **And** redireciona o usuário para a tela pública de login com mensagem informativa de saída bem-sucedida.

### Story 1.5: Fluxo de Recuperação de Senha por E-mail
**As a** usuário que esqueceu a senha de acesso,  
**I want** solicitar a redefinição de senha informando meu e-mail,  
**So that** eu possa redefinir minha credencial e recuperar o acesso à minha conta.

**Acceptance Criteria:**
* **Given** que o usuário acessa a página de recuperação (`/accounts/password_reset/`),
* **When** ele digita o e-mail cadastrado,
* **Then** o sistema gera um token temporário assinado e dispara um e-mail com link de redefinição com validade de 24 horas (no ambiente local, exibido no console do servidor),
* **And** ao clicar no link válido, o usuário define uma nova senha forte que passa a valer imediatamente.

---

## Épico 2: Shell Web Desktop e Perfil Vivo do Dev

**Meta do Épico:** Construir a casca visual da aplicação web desktop (navegação, estados de sessão e rotas) e a experiência de identidade do perfil do estudante como portfólio vivo.

### Story 2.1: Layout Base Responsivo e Shell de Navegação (Navbar e Footer)
**As a** usuário navegando no CodeView,  
**I want** ter um layout limpo, moderno e responsivo com navegação consistente,  
**So that** eu possa me localizar facilmente e alternar entre o Feed e o meu Perfil.

**Acceptance Criteria:**
* **Given** que qualquer página da aplicação é acessada,
* **When** a página é renderizada no navegador desktop,
* **Then** a navbar superior exibe o logotipo do CodeView, link para o Feed e componentes de perfil/autenticação,
* **And** para usuários anônimos, a navbar exibe os botões "Entrar" e "Cadastrar-se",
* **And** para usuários autenticados, exibe o avatar miniatura do dev, seu primeiro nome e dropdown com opções de Perfil e Logout.

### Story 2.2: Roteamento Protegido da Aba Principal
**As a** usuário da plataforma,  
**I want** que a Aba Principal do Feed seja a página inicial após o login,  
**So that** eu acerte de primeira o conteúdo central sem cliques desnecessários.

**Acceptance Criteria:**
* **Given** que um visitante não-autenticado tenta acessar `/` ou `/feed/`,
* **When** a requisição é interceptada pelo Django (`login_required`),
* **Then** ele é redirecionado para `/accounts/login/?next=/feed/`,
* **And** assim que fizer login com sucesso, ele é imediatamente encaminhado para `/feed/`.

### Story 2.3: Visualização do Perfil Pessoal (Portfólio Vivo sem CV)
**As a** estudante/dev na plataforma,  
**I want** visualizar minha página de perfil com meus dados, bio e links externos,  
**So that** eu tenha uma vitrine da minha identidade técnica sem precisar carregar currículos em PDF.

**Acceptance Criteria:**
* **Given** que o usuário autenticado acessa `/profile/`,
* **When** a página carrega,
* **Then** exibe: Foto de Avatar (ou placeholder padrão), Nome Completo, Bio descritiva, Links do GitHub e LinkedIn (clicáveis com abertura em nova aba), e Data de Ingressão ("Membro desde MM/AAAA"),
* **And** a interface NÃO contém qualquer botão, link ou formulário para upload de arquivos de currículo (PDF/Word),
* **And** o e-mail do usuário não é exposto publicamente para proteger sua privacidade (RNF-3).

### Story 2.4: Edição de Perfil e Upload de Foto de Avatar
**As a** usuário que deseja atualizar sua apresentação,  
**I want** editar minha bio, links do GitHub/LinkedIn e subir uma foto de perfil,  
**So that** meu perfil esteja sempre condizente com meu momento profissional.

**Acceptance Criteria:**
* **Given** que o usuário está na tela de edição de perfil (`/profile/edit/`),
* **When** ele altera sua bio (até 250 caracteres), links e seleciona um arquivo de imagem válido (JPG, PNG ou WebP de até 2MB),
* **Then** o backend valida as dimensões e tipo de arquivo, grava a foto na pasta `media/avatars/`,
* **And** exibe mensagem toast/alerta de sucesso: *"Perfil atualizado com sucesso!"*,
* **And** se o arquivo for maior que 2MB ou não for uma imagem válida, o sistema rejeita o upload com erro explícito de validação.

---

## Épico 3: Feed de Micro-Vídeos Verticais e Descoberta por Tecnologia

**Meta do Épico:** Implementar o núcleo do produto: consumo contínuo e fluido de vídeos verticais em pílula (9:16), filtragem ágil por tecnologia e gestão administrativa do catálogo.

### Story 3.1: Modelagem e Curadoria de Categorias de Tecnologia via Django Admin
**As a** administrador do CodeView,  
**I want** cadastrar e gerenciar tecnologias (ex: Python, JavaScript, SQL, Django) no painel administrativo,  
**So that** os vídeos possam ser categorizados e filtrados pelos alunos.

**Acceptance Criteria:**
* **Given** que o administrador autenticado com `is_staff=True` acessa o Django Admin (`/admin/`),
* **When** ele cadastra uma nova Tecnologia com Nome, Slug único e status ativo,
* **Then** a tecnologia fica disponível para associação no cadastro de vídeos e para renderização na barra de filtros do feed,
* **And** usuários comuns sem privilégios de staff não conseguem acessar o `/admin/` (HTTP 403 / redirecionamento).

### Story 3.2: Modelagem e Cadastro de Micro-Vídeos Verticais via Django Admin
**As a** curador de conteúdo do CodeView,  
**I want** cadastrar novos micro-vídeos associando título, arquivo de vídeo (9:16), tecnologia e autor,  
**So that** o catálogo da Onda 1 seja populado com conteúdos educativos de alta qualidade.

**Acceptance Criteria:**
* **Given** que o administrador está na seção de Vídeos do Django Admin,
* **When** ele preenche Título (até 150 caracteres), Descrição sucinta, seleciona a Tecnologia, anexa o arquivo MP4/WebM vertical e define a duração,
* **Then** o arquivo é salvo em `media/videos/` e o registro no modelo `Video` é publicado com status ativo,
* **And** o autor do vídeo é atribuído a um usuário da plataforma.

### Story 3.3: Interface do Player de Vídeo Vertical (9:16) no Feed
**As a** estudante consumindo o CodeView,  
**I want** assistir ao vídeo vertical em um player centralizado de alta qualidade com sobreposição de dados,  
**So that** eu aprenda o conceito do vídeo em menos de um minuto com foco total.

**Acceptance Criteria:**
* **Given** que o usuário autenticado está na Aba Principal (`/feed/`),
* **When** a página carrega,
* **Then** o player HTML5 renderiza o primeiro vídeo em formato estrito 9:16 centralizado na tela,
* **And** sobreposto na parte inferior do vídeo são exibidos: Título, Autor, Tag da Tecnologia e Descrição breve,
* **And** o player fornece botões de Play/Pause, silenciar áudio (Mute/Unmute) e barra discreta de progresso do vídeo.

### Story 3.4: Navegação Vertical entre Vídeos por Scroll e Teclado
**As a** usuário navegando pelo catálogo de vídeos,  
**I want** rolar suavemente para o próximo vídeo ou voltar para o anterior usando o scroll do mouse ou as setas do teclado,  
**So that** eu tenha uma navegação contínua no estilo de micro-vídeos (TikTok-style).

**Acceptance Criteria:**
* **Given** que um vídeo está em reprodução no feed,
* **When** o usuário realiza um scroll para baixo ou pressiona a tecla "Seta para Baixo",
* **Then** a visualização desliza com transição suave para o próximo vídeo da lista,
* **And** o vídeo anterior é pausado automaticamente e o novo vídeo inicia sua reprodução,
* **And** o mesmo comportamento ocorre de forma reversa ao rolar para cima ou usar a "Seta para Cima".

### Story 3.5: Barra de Filtragem Dinâmica por Tecnologia no Feed
**As a** estudante focado em aprender uma linguagem específica (ex: Python),  
**I want** clicar na tag da linguagem desejada na barra de filtros superior,  
**So that** o feed mostre apenas pílulas de conhecimento dessa tecnologia.

**Acceptance Criteria:**
* **Given** que o usuário está visualizando a Aba Principal,
* **When** ele clica no botão de filtro "Python",
* **Then** o feed atualiza dinamicamente (ou via parâmetro de URL `?tech=python`) para listar exclusivamente vídeos vinculados à tecnologia Python,
* **And** a tag "Python" ganha destaque visual como filtro selecionado,
* **And** se o usuário clicar em "Todos", o feed retorna à exibição global cronológica de todos os vídeos,
* **And** se a tecnologia selecionada não tiver vídeos ativos, o feed exibe uma tela amigável (*empty state*): *"Nenhum vídeo encontrado para esta tecnologia ainda. Que tal explorar outras tags?"*.
