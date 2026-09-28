---
title: "Product Brief: Plataforma de Micro-Aprendizado e Desafios Práticos (PA2)"
status: "final"
created: "2026-09-14"
updated: "2026-09-14"
---

# Product Brief: Plataforma de Micro-Aprendizado e Desafios Práticos

## Executive Summary

A plataforma nasce para revolucionar a forma como tecnologia e programação são ensinadas, atacando o problema crítico da taxa de abandono em cursos EAD tradicionais. Combinando o dinamismo e o alto engajamento dos vídeos curtos verticais (estilo TikTok) com a fixação instantânea de conhecimento por meio de micro-desafios de código executáveis diretamente no navegador, o produto transforma o aprendizado passivo em uma experiência interativa, prática e divertida.

A proposta de valor é ancorada em três pilares centrais consensuados pela equipe: **Ensino Dinâmico**, **Conteúdo Relevante** e **Conexões com Devs Experientes**. A plataforma opera sob um modelo freemium de alto impacto social e acadêmico (PA2): o acesso ao conteúdo e aos desafios é 100% gratuito, monetizando e gerando receita sustentável através da emissão de certificações pagas que atestam a competência real do aluno perante o mercado e recrutadores conectados na rede.

---

## The Problem

1. **A Fadiga dos Cursos Tradicionais e a "Ilusão de Competência":** Cursos de programação de 40 a 60 horas em vídeo aulas expositivas geram taxas de desistência superiores a 85%. O aluno assiste passivamente, tem a sensação de que compreendeu a matéria, mas trava completamente quando abre um editor em branco ("tutorial hell").
2. **Falta de Prática Imediata:** O intervalo de tempo entre ver uma sintaxe e aplicá-la é longo demais nas plataformas atuais, quebrando o ciclo de memorização e dopamina.
3. **Isolamento e Dificuldade de Acesso ao Mercado:** Desenvolvedores iniciantes e estudantes em transição sofrem para construir networking e obter validação técnica de profissionais seniores. Recrutadores, por sua vez, recebem centenas de currículos sem conseguir avaliar quem realmente sabe programar.

---

## The Solution

Uma plataforma web moderna, construída sobre o ecossistema **Django (Python)**, com interface desktop otimizada e arquitetura preparada para uma transição fluida para **Mobile First**.

* **Feed Dinâmico de Vídeos Curtos de Tecnologia:** Vídeos de 1 a 3 minutos com dicas práticas, conceitos de sintaxe, truques de arquitetura e boas práticas, organizados por tópicos e tecnologias.
* **Micro-Desafios com Editor de Código Embutido:** Logo após assistir ao conteúdo, o usuário é convidado a resolver um desafio prático de código dentro da própria página, recebendo validação imediata da solução.
* **Cursos Gratuitos Estruturados:** Trilhas de conhecimento compostas por sequências de micro-vídeos + desafios correlatos.
* **Rede de Conexão e Recrutamento:** Espaço de comentários por vídeo e sistema de mensagens diretas (DMs) entre perfis, permitindo que iniciantes tirem dúvidas com criadores e que empresas identifiquem talentos ativos que estão dominando os desafios.
* **Certificação Paga Flexível:** Opção de emissão de certificado formal pago, condicionado à conclusão de 100% dos desafios práticos do curso ou à aprovação em um projeto prático final avaliado.

---

## What Makes This Different (Diferenciais Competitivos)

* **Micro-Doses de Dopamina Educacional:** Elimina o tédio. A cada vídeo curto assistido e micro-desafio resolvido, o aluno ganha pontos, avança na trilha e vê o código funcionar em tempo real.
* **Prática Instantânea no Navegador:** Não exige configuração complexa de ambiente local para quem está começando; o editor integrado testa a lógica na hora.
* **Feed Aberto Especializado:** Qualquer usuário cadastrado pode compartilhar conhecimento em vídeo, criando uma comunidade orgânica e descentralizada focada estritamente em tecnologia.
* **Perfil como Portfólio Vivo:** O perfil do usuário expõe seu histórico de desafios concluídos e certificados obtidos, funcionando como um currículo verificado que atrai desenvolvedores experientes e recrutadores.

---

## Who This Serves (Personas do Projeto)

### Persona 1: Carlos ("Carlinhos") — O Aspirante a Dev Gamer (criado por Karol - KS)
* **Demografia & Perfil:** 19 anos, curioso, introvertido, focado em hábitos e alimentação saudável, sonha em se tornar programador Fullstack.
* **Comportamento & Interesses:** Joga no seu PC gamer, assiste a tutoriais de manutenção de computadores/celulares, consome conteúdo em formatos ágeis e visuais.
* **Dores & Necessidades:** Cansaço de plataformas teóricas e monótonas; busca um ambiente que realmente **instigue sua vontade de programar** através de desafios práticos interativos e dinâmicos, permitindo fazer networking sem o constrangimento de eventos formais.

### Persona 2: "Leozinho" — O Empresário Ocupado & Pragmático (criado por Leandro - LM)
* **Demografia & Perfil:** 32 anos, empresário, casado e com filhos, formação superior, rotina de alta demanda de tempo.
* **Comportamento & Interesses:** Sociável, perfeccionista, calmo no dia a dia mas com reações explosivas diante de perda de tempo, ineficiência ou interfaces confusas.
* **Dores & Necessidades:** Precisa aprender tecnologia com foco em **aplicação prática imediata no seu negócio** (automações, controle e otimização de processos). Não tem paciência para enrolação teórica de 40 minutos; quer mini cursos diretos ao ponto ("assistiu 2 min ➔ aplicou no editor ➔ funcionou") e certificações rápidas que comprovem competência real.

### Jornadas dos Usuários (User Journeys & Mapeamento de Funcionalidades)

#### 🚀 A Jornada de Carlinhos (Karol - KS) — O Aluno Ágil
* **Rotina Diária:** Acorda cedo, café da manhã com sucrilhos, trajeto de ônibus até a faculdade.
* **O Momento da Descoberta (Viralidade Orgânica):** Na faculdade, comenta com um colega sobre o **CodeView**, gerando tração boca a boca.
* **A Decisão de Agir:** Volta para casa, descansa 30 minutos e acorda motivado a aprimorar suas habilidades em Python para se destacar nas aulas da faculdade.
* **A Experiência no CodeView (Mapeamento de Ações ➔ Funcionalidades):**
  1. Acessa o **CodeView** diretamente do seu computador.
  2. **Busca pelo conteúdo de Python** ➔ *Transcrição e Busca por Palavra-chave / Filtro por Linguagem*.
  3. **Assiste aos vídeos verticais curtos** ➔ *Feed de vídeos curtos com filtro por linguagem*.
  4. **Interage comentando nos vídeos** ➔ *Comentários Públicos nos Vídeos / Anotações Pessoais*.
  5. **Faz todos os exercícios propostos** ➔ *Tela de perguntas/desafios com feedback instantâneo*.
  6. **Descobre curso rápido** ➔ *Transcrição e Busca por Palavra-chave / Catálogo de Cursos*.
  7. **Se inscreve no curso** ➔ *Inscrição em cursos*.
  8. **Inscrição aceita** ➔ *Notificações de mensagens e de inscrição*.
  9. **Inicia curso rápido** com meta de conclusão em até **2 semanas**.

#### 💼 A Jornada de Leozinho (Leandro - LM) — O Empresário Pragmático
* **Rotina Diária:** Acorda às 8h, vai de carro para o escritório, toma café, resolve demandas operacionais da empresa, almoça às 13h e participa de reuniões executivas.
* **O Ponto de Inflexão (Dor Real de Negócio):** Em conversa pós-reunião com um colaborador, identifica um gargalo operacional crítico e a necessidade de implementar **automações com programação (Python)** na sua empresa.
* **A Busca por Solução:** Procura plataformas ágeis e intuitivas — seu tempo é escasso e ele não tolera burocracia ou aulas teóricas arrastadas.
* **A Experiência no CodeView (Mapeamento de Ações ➔ Funcionalidades):**
  1. **Descobre a plataforma e faz sua inscrição** ➔ *Busca por Palavra-chave / Cadastro de Usuário*.
  2. **Gosta da dinâmica e decide entrar em um curso** ➔ *Feed e Catálogo de Cursos*.
  3. **Faz sua inscrição** ➔ *Inscrição em cursos*.
  4. **Jornada de aprendizado contínuo** em um curso de automação com Python ao longo de **3 meses**.
  5. **Surgem dúvidas durante o curso e busca apoio de especialistas** ➔ *Aba de DMs para conversas com pessoas mais experientes*.
  6. **Conclui a jornada de 3 meses e recebe a validação formal** ➔ *Emissão do Certificado*.

---

## Success Criteria (Critérios de Sucesso do MVP)

* **Engajamento com Desafios:** Mais de 60% dos usuários que assistem a um vídeo ou aula com desafio associado executam ao menos uma tentativa no editor de código embutido.
* **Retenção e Interatividade Social:** Registro de interações contínuas por meio de comentários nos vídeos e troca de mensagens diretas entre usuários.
* **Viabilidade Técnica e Performance no PA2:** Apresentação funcional completa do ciclo: Cadastro -> Feed de Vídeos -> Execução de Desafio no Editor -> Mensageria -> Emissão do Certificado.
* **Arquitetura Escalável:** Backend estruturado de forma desacoplada com Django e Django REST Framework, permitindo a ingestão de vídeos e execução de testes de desafios com estabilidade.

---

## Matriz de Definição de Escopo: É / Não É / Faz / Não Faz (Semana 2)

| É | Não É |
| :--- | :--- |
| • Plataforma de Ensino/Aprendizado Dinâmico<br>• Plataforma Web voltada estritamente à tecnologia<br>• Plataforma de conteúdo tecnológico ágil | • Plataforma de formação longa / graduação<br>• Plataforma de capacitação especializada profunda<br>• Monetizador por visualização de vídeos (estilo Creator Fund/AdSense)<br>• Portal de empregos tradicional (tipo Catho/Gupy) |

| Faz | Não Faz |
| :--- | :--- |
| • Network e conexão direta entre usuários (DMs e comentários)<br>• Mini cursos modulares<br>• Vídeos educativos e práticos de curta duração | • Capacitação especializada exaustiva<br>• Divulgação / envio de currículos tradicionais (PDFs de CV)<br>• Sistema de seguidores entre usuários (elimina vaidade e simplifica o MVP) |

---

## Matriz de Trade-off Sliders (Semana 2: Karol Sabino & Leandro Moura)

Escala de 1 a 7 (onde 7 representa a maior prioridade arquitetural e de produto):

| Atributo de Qualidade | LM (Leandro) | KS (Karol) | Consenso / Média | Diretriz Estratégica para o Projeto |
| :--- | :---: | :---: | :---: | :--- |
| **Simplicidade e Usabilidade** | 7 | 6 | **6.5 (Topo Absoluto)** | Prioridade máxima. O feed vertical e a transição para o editor devem ser intuitivos e sem atrito para iniciantes. |
| **Segurança** | 5 | 7 | **6.0 (Crítico)** | Blindagem obrigatória contra execução de código malicioso no editor (sandbox) e garantia de privacidade nas DMs. |
| **Performance** | 4 | 7 | **5.5 (Alto)** | Streaming ágil de vídeos curtos e resposta rápida do runner de código sem sobrecarregar o servidor do PA2. |
| **Rastreabilidade** | 3 | 6 | **4.5 (Médio-Alto)** | Auditoria e registro confiável das tentativas e conclusões de desafios para validação idônea do certificado pago. |
| **Flexibilidade** | 3 | 5 | **4.0 (Equilibrado)** | Foco em 1 ou 2 linguagens iniciais (JS/Python) no MVP, com arquitetura preparada para plugar novas no futuro. |
| **Integridade** | 4 | 4 | **4.0 (Consenso Exato)** | Dados de progresso e certificados consistentes e atômicos via Django ORM, sem complexidade desnecessária. |
| **Multiplataforma** | 2 | 5 | **3.5 (Pragmático)** | Web Desktop responsiva otimizada para telas verticais no PA2, com backend desacoplado via DRF para o futuro app mobile. |

---

## Brainstorming de Funcionalidades (Consolidação Karol & Leandro)

A partir das contribuições individuais de **Karol Sabino (KS)** e **Leandro Moura (LM)**, as funcionalidades foram agrupadas em 4 domínios de arquitetura e priorizadas via **MoSCoW**:

### 📦 Agrupamento por Domínios Funcionais (Módulos do Sistema)

1. **Módulo de Contas & Usuário (`accounts`):**
   * Cadastro e Login na plataforma.
   * Tela de perfil de usuário.
   * Editar perfil (dados e preferências).
   * Busca de perfis.
   * Compartilhar perfil.
   * Encerrar conta.
   * Termos de Privacidade e conformidade LGPD.

2. **Módulo de Feed de Vídeos & Interação (`videos`):**
   * Feed de vídeos curtos verticais com filtro por linguagem/tecnologia.
   * Busca de vídeos por palavra-chave / tecnologia.
   * Publicar vídeo (upload de arquivo de vídeo).
   * Aba de câmera (gravação direta / captura no navegador).
   * Curtir vídeos.
   * Aba de comentários em vídeos.
   * Compartilhar vídeo.
   * Alerta (sininho) de novas publicações.
   * Selo/votação comunitária de "Conteúdo Confiável" (upvotes).
   * Anotações privadas nos vídeos *(bloco pessoal de estudos)*.
   * Transcrição e busca por termos falados.

3. **Módulo de Mini Cursos & Desafios Práticos (`courses`):**
   * Aba de cursos (catálogo de trilhas).
   * Busca de cursos.
   * Inscrição em cursos.
   * Cancelamento de inscrição em cursos.
   * Cronograma do curso.
   * Progresso do curso (% e aulas concluídas).
   * Tela de perguntas e desafios com feedback instantâneo.
   * Enviar desafios (submissão de código no editor).
   * Medidor de conhecimento *(pontuação de domínio / termômetro de habilidades)*.

4. **Módulo de Certificação (`certificates`):**
   * Emissão do Certificado digital.
   * Baixar certificado (PDF).
   * Compartilhar certificado (link público com validação e QR Code).

5. **Módulo de Mensageria & Notificações (`chat` / `notifications`):**
   * Aba de DMs para conversas com pessoas experientes *(networking/mentoria)*.
   * Notificações de mensagens recebidas.
   * Notificações de inscrição confirmada.
   * Notificações de inscrição cancelada.

---

### 🎯 Priorização MoSCoW para o MVP (PA2)

* **Must Have (Obrigatório para o MVP no PA2):**
  * Cadastro / Login / Tela de perfil básica.
  * Feed de vídeos verticais com filtro por linguagem.
  * Publicar vídeo (upload).
  * Catálogo e Inscrição em cursos.
  * Progresso do curso.
  * Tela de perguntas/desafios com envio e feedback instantâneo.
  * Emissão e Download de Certificado.
  * Aba de DMs assíncronas para tirar dúvidas com devs experientes.
* **Should Have (Interface rica e engajamento da comunidade):**
  * Aba de comentários nos vídeos.
  * Curtir vídeos.
  * Compartilhar vídeo, perfil e certificado.
  * Busca de perfis e busca de cursos.
  * Cancelamento de inscrição e notificações de confirmação/cancelamento.
  * Notificações de mensagens na navbar.
  * Selo comunitário de "Conteúdo Confiável" (upvotes).
  * Medidor de conhecimento (pontuação de desafios).
  * Editar perfil, Encerrar conta e Termos de Privacidade (LGPD).
* **Could Have (Diferenciais avançados se o tempo permitir):**
  * Aba de câmera com gravação ao vivo no navegador (no MVP o upload de arquivo mp4 resolve).
  * Anotações privadas nos vídeos.
  * Transcrição textual e busca por palavra-chave no vídeo.
  * Alerta (sininho) de nova publicação.
  * Cronograma do curso.
* **Won't Have (Fora do Escopo do MVP):**
  * Monetização de criadores por view (excluído por decisão estratégica de negócio).
  * Sistema de seguidores (foco no conteúdo e DMs).
  * Upload ou divulgação de currículo em PDF.

---

### In Scope (Dentro do MVP)
* **Autenticação & Perfis:** Cadastro/login de usuários com perfis públicos exibindo bio, histórico de desafios e cursos em andamento.
* **Feed Aberto de Vídeos Curtos:** Publicação e reprodução de vídeos verticais sobre tecnologia, com suporte a categorização por tags (ex: Python, JavaScript, CSS).
* **Editor de Código Integrado no Navegador:** Interface com editor embutido (ex: CodeMirror / Monaco) com execução/validação de saída para resolução imediata de desafios propostos.
* **Mini Cursos Gratuitos:** Agrupamento de vídeos em módulos com desafios práticos sequenciais focados em tópicos específicos (sem enrolação).
* **Módulo Social & Conexões:** Seção de comentários em cada vídeo e sistema de troca de mensagens diretas (DMs) entre usuários para networking e oportunidades diretas.
* **Sistema de Certificação Flexível:** Emissão de certificado digital pago (fluxo com status pago e validação de requisitos: 100% dos desafios concluídos ou projeto final).

### Out of Scope (Fora do Escopo Inicial / Não Faz)
* **Sem Sistema de Seguidores:** A conexão é feita por mensagens diretas e comentários no próprio vídeo, eliminando a complexidade de grafos de seguidores e algoritmos de feed de quem você segue.
* **Sem Divulgação de Currículo Tradicional:** O perfil com o histórico de desafios concluídos é o próprio portfólio vivo; não haverá upload ou envio de currículos em PDF nem portal de vagas.
* **Sem Monetização por Views de Vídeo:** O modelo é focado em certificação paga; a plataforma não gerencia repasse de dinheiro por número de visualizações.
* **Sem Cursos de Longa Duração / Capacitação Especializada:** Foco exclusivo em mini cursos e pílulas práticas.
* **Sem Aplicativo Mobile Nativo:** O MVP de PA2 será Web Desktop responsivo, estruturado em Django REST Framework para consumo futuro.
* **Sem Sandbox Docker Pesada:** Runner seguro e controlado no navegador/backend simplificado.
* **Sem Algoritmo Complexo de IA:** Feed cronológico e ordenado por tags técnicas.

---

## Matriz de Revisão Técnica, de Negócio e de UX (Avaliação Karol & Leandro)

| Funcionalidade | Nível de Confiança | Esforço | Valor UX | Valor de Negócio | Diagnóstico da Analista Mary |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Cadastro/Login** | 🟢 Verde | E | ♥♥♥ | $$ | **Quick Win:** Entrega imediata usando a autenticação nativa do Django. |
| **Feed de vídeos com filtro** | 🟡 Amarelo | EEE | ♥♥♥ | $$$ | **Core do Produto:** Prioridade máxima; foco em player vertical responsivo. |
| **Inscrição em cursos** | 🟢 Verde | E | ♥♥♥ | $$ | **Quick Win:** Relacionamento simples entre Usuário e Curso no Django ORM. |
| **Tela de perguntas/desafios** | 🔴 Vermelho | EEE | ♥♥ | $$$ | **Risco Desmistificado:** Reduzir o esforço executando código no navegador (Web Workers / Pyodide) para não onerar o servidor. |
| **Aba de DMs para conversas** | 🔴 Vermelho | EEE | ♥♥ | $ | **Simplificação Obrigatória:** Baixo valor de negócio e alto esforço. Fazer mensageria assíncrona simples (inbox direto), sem WebSockets complexos. |
| **Emissão do Certificado** | 🟡 Amarelo | EE | ♥♥♥ | $$$ | **Motor de Monetização:** Geração de página web pública de validação com QR Code. |
| **Notificações (mensagens/inscrição)** | 🟢 Verde | E | ♥ | $ | **Polimento Rápido:** Indicador visual simples de novas mensagens na navbar. |
| **Busca de perfis** | 🟡 Amarelo | EE | ♥♥♥ | $$ | **Conexão:** Busca simples no banco por nome de usuário e habilidades. |
| **Cancelamento de inscrição** | 🟢 Verde | E | ♥♥♥ | $ | **Autonomia:** Botão simples para remover a matrícula do curso. |
| **Selo "Conteúdo Confiável"** | 🔴 Vermelho | EEE | ♥♥♥ | $$$ | **Transformação em Quick Win:** Em vez de algoritmo pesado, usar contagem de upvotes da comunidade ("Código Aprovado"). |
| **Anotações Privadas nos Vídeos (LM)** | 🟡 Amarelo | EEE | ♥♥♥ | $$ | **Otimização:** No Django, isso é apenas uma tabela de 3 campos (`user`, `video`, `nota`), caindo de EEE para E! |
| **Transcrição e Busca (LM)** | 🟡 Amarelo | EE | ♥♥ | $$ | **Eficiência:** Armazenar texto da transcrição junto ao vídeo e filtrar com busca textual simples. |
| **Monetização por views** | 🔴 Vermelho | EEE | ♥♥♥ | $$$ | **FORA DO ESCOPO:** 100% descartado conforme a matriz É/Não É, economizando esforço crítico. |

---

## Sequenciador de Funcionalidades (Ondas do MVP - Lean Inception)

Estruturado rigorosamente sob as **6 Regras de Ouro do Sequenciador**:
1. *4 a 6 cartões por onda.*
2. *No máximo 2 cartões vermelhos por onda.*
3. *Não conter cartões somente amarelos ou vermelhos (presença obrigatória de verdes).*
4. *Soma de esforço <= 9 E por onda.*
5. *Soma de valor >= 7 $ e >= 5 ♥ por onda.*
6. *Dependências atendidas obrigatoriamente em onda anterior.*

---

### 🚀 ONDA 1: O MVP Core (A Jornada Ponta a Ponta)
*Objetivo: Fechar a jornada essencial de aprendizado e fixação prática de Carlinhos e Leozinho.*

| Funcionalidade | Confiança | Esforço | Valor UX | Valor Negócio | Justificativa / Dependência |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Cadastro/Login** | 🟢 Verde | E (1) | ♥♥♥ (3) | $$ (2) | Base de autenticação de toda a plataforma. Sem dependências. |
| **Feed de vídeos curtos com filtro** | 🟡 Amarelo | EEE (3) | ♥♥♥ (3) | $$$ (3) | O formato dinâmico central do CodeView. |
| **Inscrição em cursos** | 🟢 Verde | E (1) | ♥♥♥ (3) | $$ (2) | Matrícula na trilha estruturada de Python. |
| **Tela de perguntas/desafios instantâneos** | 🔴 Vermelho | EEE (3) | ♥♥ (2) | $$$ (3) | A prática imediata e fixação de conhecimento. |

* **Total de Cartões:** 4 `[Atende Regra 1: 4 a 6]`
* **Cores:** 2 Verdes, 1 Amarelo, 1 Vermelho `[Atende Regras 2 e 3: máx 2 vermelhos e contém verdes]`
* **Esforço Total:** 1 + 3 + 1 + 3 = **8 E** `[Atende Regra 4: <= 9 E]`
* **Valor de Negócio ($):** 2 + 3 + 2 + 3 = **10 $** `[Atende Regra 5: >= 7 $]`
* **Valor de UX (♥):** 3 + 3 + 3 + 2 = **11 ♥** `[Atende Regra 5: >= 5 ♥]`
* **Dependências:** Todas primitivas satisfeitas `[Atende Regra 6]`.

---

### 🌟 ONDA 2: Incremento de Networking, Certificação & Controle
*Objetivo: Ativar o pilar de mentoria/conexões, a monetização por certificados e a autonomia do aluno.*

| Funcionalidade | Confiança | Esforço | Valor UX | Valor Negócio | Justificativa / Dependência |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Emissão do Certificado** | 🟡 Amarelo | EE (2) | ♥♥♥ (3) | $$$ (3) | Depende de Inscrição e Desafios (Onda 1). |
| **Cancelamento de inscrição** | 🟢 Verde | E (1) | ♥♥♥ (3) | $ (1) | Depende de Inscrição em cursos (Onda 1). |
| **Aba de DMs para conversas** | 🔴 Vermelho | EEE (3) | ♥♥ (2) | $ (1) | Depende de Cadastro/Login (Onda 1). |
| **Busca de perfis** | 🟡 Amarelo | EE (2) | ♥♥♥ (3) | $$ (2) | Depende de Cadastro/Login (Onda 1). |

* **Total de Cartões:** 4 `[Atende Regra 1: 4 a 6]`
* **Cores:** 1 Verde, 2 Amarelos, 1 Vermelho `[Atende Regras 2 e 3: máx 2 vermelhos e contém verdes]`
* **Esforço Total:** 2 + 1 + 3 + 2 = **8 E** `[Atende Regra 4: <= 9 E]`
* **Valor de Negócio ($):** 3 + 1 + 1 + 2 = **7 $** `[Atende Regra 5: >= 7 $]`
* **Valor de UX (♥):** 3 + 3 + 2 + 3 = **11 ♥** `[Atende Regra 5: >= 5 ♥]`
* **Dependências:** Todas dependências implementadas na Onda 1 `[Atende Regra 6]`.

---

### 🛡️ ONDA 3: Incremento de Produtividade, Curadoria & Alertas
*Objetivo: Adicionar recursos avançados de eficiência de busca, anotações e feedback comunitário.*

| Funcionalidade | Confiança | Esforço | Valor UX | Valor Negócio | Justificativa / Dependência |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Notificações (mensagens/inscrição)** | 🟢 Verde | E (1) | ♥ (1) | $ (1) | Depende de DMs (Onda 2) e Inscrição (Onda 1). |
| **Selo "Conteúdo Confiável"** | 🔴 Vermelho | EEE (3) | ♥♥♥ (3) | $$$ (3) | Depende de Feed de Vídeos (Onda 1). |
| **Transcrição e Busca por Palavra** | 🟡 Amarelo | EE (2) | ♥♥ (2) | $$ (2) | Depende de Feed de Vídeos (Onda 1). |
| **Comentários Privados nos Vídeos (LM)**| 🟡 Amarelo | EEE (3) | ♥♥♥ (3) | $$ (2) | Depende de Feed de Vídeos e Cadastro (Onda 1). |

* **Total de Cartões:** 4 `[Atende Regra 1: 4 a 6]`
* **Cores:** 1 Verde, 2 Amarelos, 1 Vermelho `[Atende Regras 2 e 3: máx 2 vermelhos e contém verdes]`
* **Esforço Total:** 1 + 3 + 2 + 3 = **9 E** `[Atende Regra 4: <= 9 E]`
* **Valor de Negócio ($):** 1 + 3 + 2 + 2 = **8 $** `[Atende Regra 5: >= 7 $]`
* **Valor de UX (♥):** 1 + 3 + 2 + 3 = **9 ♥** `[Atende Regra 5: >= 5 ♥]`
* **Dependências:** Todas dependências implementadas nas Ondas 1 e 2 `[Atende Regra 6]`.

---

## Canvas MVP (Lean Inception — 7 Perguntas Estratégicas)

O **Canvas MVP** consolida o planejamento tático do projeto em 7 blocos fundamentais:

### 1. 🎯 Proposta do MVP
Plataforma web de micro-aprendizado dinâmico em tecnologia que combate a alta evasão dos cursos tradicionais através do ciclo contínuo: **vídeo vertical curto (1 a 3 min) ➔ prática imediata com desafio de código no navegador ➔ conexão direta com devs experientes (DMs)**. O modelo opera com conteúdo gratuito e monetização sustentável através de certificação digital validada com histórico de desafios concluídos.

### 2. 👥 Personas Segmentadas
* **Público Amplo:** Aspirantes a desenvolvedores, estudantes de tecnologia e profissionais de diversas áreas que buscam aprender programação de forma prática e rápida.
* **Segmentação Piloto (Grupo Menor para Validação):**
  * Estudantes universitários de tecnologia (colegas do **Carlinhos** em início de graduação/disciplinas de algoritmos).
  * Pequenos empresários e profissionais autônomos da rede do **Leandro/Leozinho** que necessitam automatizar processos operacionais com Python.
  * **Grupo Piloto Fechado:** 30 a 50 usuários beta testando a trilha piloto de *Fundamentos e Automação com Python*.

### 3. 🛤️ Jornadas Atendidas
* **Jornada de Carlinhos (O Aluno Ágil):** Descobre a plataforma, busca por "Python", assiste ao vídeo curto sem cansaço, executa e valida o desafio prático no editor integrado com feedback imediato, e se inscreve na trilha rápida de 2 semanas.
* **Jornada de Leozinho (O Empresário Pragmático):** Identifica a necessidade de automação na empresa, cadastra-se sem burocracia, consome pílulas práticas de Python sem enrolação, tira dúvidas via DMs com desenvolvedores experientes e conquista a certificação formal para seu negócio.

### 4. ⚙️ Funcionalidades do MVP (O Que Vamos Construir e Simplificar)
* **O que vamos construir:**
  * Cadastro / Login com aceite de Termos de Privacidade (LGPD) e Tela de Perfil.
  * Feed dinâmico de vídeos verticais curtos com filtro por linguagem técnica (Python).
  * Catálogo de cursos e sistema de inscrição em trilhas estruturadas.
  * Tela de perguntas e desafios interativos com submissão de código e feedback instantâneo.
  * Acompanhamento de progresso do curso (% concluído).
  * Emissão e Download de Certificado com validação digital pública e QR Code.
  * Aba de DMs diretas assíncronas para tirar dúvidas e mentoria com profissionais experientes.
* **O que é simplificado ou melhorado:**
  * Elimina a barreira de instalação de IDEs e terminais locais pesados para iniciantes.
  * Substitui aulas expositivas de 60 minutos por doses dinâmicas de 2 a 5 minutos.
  * Elimina a burocracia de envio de currículos em PDF e a vaidade de números de seguidores, conectando pessoas diretamente através do código e do conteúdo.

### 5. 💡 Resultado Esperado (Hipóteses e Aprendizado)
* **Hipótese de Engajamento:** Usuários submetem significativamente mais exercícios quando o desafio prático é proposto imediatamente após um vídeo curto, reduzindo a taxa de abandono do curso para menos de 40%.
* **Hipótese de Monetização:** Alunos que concluem 100% dos desafios práticos reconhecem valor real na certificação paga devido à comprovação técnica pública dos desafios resolvidos.
* **Hipótese de Networking:** A existência de DMs diretas com devs experientes aumenta a confiança do aluno iniciante e acelera o aprendizado prático.

### 6. 📈 Métricas para Validar as Hipóteses do Negócio
* **Taxa de Conclusão de Desafios:** % de usuários que assistem ao vídeo e realizam ao menos uma tentativa de código no editor (Meta: $\ge 60\%$).
* **Taxa de Conclusão de Trilha:** % de alunos inscritos no curso piloto de Python que finalizam todos os módulos e desafios (Meta: $\ge 35\%$).
* **Taxa de Retenção Semanal (D7 / D14):** % de usuários que retornam à plataforma após 7 e 14 dias para continuar praticando.
* **Conversão de Certificados:** % de alunos aptos que geram e compartilham o certificado digital com QR Code.
* **Interações Sociais:** Volume de mensagens trocadas na Aba de DMs e dúvidas respondidas por mentores.

### 7. 💰 Custo e Cronograma
* **Custo Financeiro Previsto:** Próximo de R$ 0,00 no MVP acadêmico (Stack Open-Source: Django + SQLite/PostgreSQL gratuito; hospedagem em tier gratuito do Render/Railway; armazenamento de vídeo em tier gratuito de CDN/Cloudinary). Custo restrito às horas de dedicação da equipe (Karol e Leandro).
* **Cronograma de Entrega (Semestre do PA2):**
  * **Semanas 1 e 2:** Concepção, Briefing, Personas, Matrizes e Sequenciador *(Concluído!)*.
  * **Semanas 3 a 5:** Desenvolvimento do Core da Onda 1 e Onda 2 (Auth, Feed, Cursos e Editor de Desafios).
  * **Semanas 6 a 8:** Desenvolvimento das Ondas 3 e 4 (Submissão de Código, Progresso, Emissão de Certificados e DMs).
  * **Semanas 9 e 10:** Testes com os 30-50 usuários do grupo piloto e correções de bugs.
  * **Semanas 11 e 12:** Consolidação de métricas, documentação final e apresentação para a banca examinadora do PA2.
  * **Data Prevista de Entrega do MVP:** Fim do semestre letivo do PA2.

---

## Strategic Considerations & Risk Mitigation (Recomendações da Analista Mary)

1. **Curadoria do Feed Aberto e Confiabilidade:**
   * *Risco:* Como qualquer usuário pode postar, há risco de vídeos com códigos errados ou desatualizados, ferindo o pilar de *Conteúdo Confiável*.
   * *Mitigação:* Implementar sistema de upvotes técnicos ("Código Validado pela Comunidade") e mecanismo ágil de denúncia para conteúdos de baixa qualidade ou fora do escopo de tecnologia.

2. **Segurança e Viabilidade do Editor Embutido (Opção B):**
   * *Risco:* Execução de código arbitrário submetido por usuários no backend pode sobrecarregar o servidor ou gerar brechas de segurança.
   * *Mitigação:* No MVP, priorizar runners leves com limites estritos de tempo de execução (timeout) ou execução client-side segura (ex: Web Workers / Pyodide / Iframe isolado) para garantir a estabilidade durante a apresentação do PA2.

3. **Percepção de Valor do Certificado Pago:**
   * *Risco:* Em cursos gratuitos, os alunos podem relutar em pagar pelo certificado se ele for apenas um PDF genérico.
   * *Mitigação:* O certificado deve incluir uma URL pública e QR Code que mostre a relação exata dos desafios práticos que o aluno concluiu, servindo como comprovação técnica real pronta para ser anexada ao LinkedIn e avaliada por recrutadores.

---

## Vision (Visão de Futuro)

* **Lançamento do App Mobile First:** Expansão da experiência do feed vertical para aplicativo mobile nativo (React Native ou Flutter), mantendo a sincronização perfeita de progresso com a versão web.
* **Marketplace de Recrutamento Ativo:** Empresas pagando por assinaturas corporativas para filtrar os melhores alunos com base nas pontuações reais de desafios e métricas de código.
* **Gamificação Avançada:** Batalhas de código em tempo real entre usuários, rankings semanais e desafios patrocinados por grandes empresas de tecnologia.
