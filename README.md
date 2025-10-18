# 🤖 Portfólio de Projetos de Automação em Python

Este repositório reúne meus principais projetos de automação desenvolvidos, mostrando habilidades em Python, automação de processos, manipulação de dados e integração de sistemas. 
Os scripts foram desenvolvidos para otimizar tarefas operacionais e são ideais para uso em times de **televendas, marketing, atendimento e análise de dados**.



## 📌 Projetos

### 1. 📍 Consulta de Mailing – Google Maps

Automação que realiza buscas no **Google Maps** com base em logradouros e cidades de uma planilha, extraindo informações de empresas como nome, telefone e endereço.

**Funcionalidades:**
- Leitura de planilha com logradouros e cidades
- Busca automatizada no Google Maps via Selenium
- Scroll automático para carregar resultados
- Extração de nome da empresa, telefone e endereço
- Controle por teclado:  
  - `[` pausa/continua a execução  
  - `]` troca de perfil do navegador (evita bloqueios)
- Exportação dos dados para Excel
- Registro automático de quais endereços já foram consultados

**Tecnologias usadas:**
- Python, Selenium, Pandas, Keyboard, JSON, Excel (openpyxl)

**Exemplo de resultado:**

| NM_EMPRESA           | TELEFONE_EMPRESA | ENDERECO                      |
|----------------------|------------------|-------------------------------|
| Padaria Central      | (11) 91234-5678  | Av. Paulista, 123 – São Paulo |
| Clínica XYZ          | (11) 99888-7766  | R. da Consolação, 456         |

🔗 [Ver detalhes do projeto](./Consulta_Mailing_Abr_Telecom/prospect_2.py) 

---

### 2. ☎️ Consulta de Portabilidade – ABR Telecom

Automação que realiza a consulta da **portabilidade numérica** de telefones através do site da ABR Telecom, identificando a prestadora atual e status da linha.

**Funcionalidades:**
- Leitura de planilha com números de telefone
- Divisão dos números em blocos de 30 para upload
- Navegação automática até o site da ABR Telecom
- Aguardando ação manual do usuário para resolver o reCAPTCHA
- Coleta de nome da operadora e mensagem de status
- Atualização automática da planilha com os dados extraídos

**Tecnologias usadas:**
- Python, Selenium, Pandas, Threads, Excel (openpyxl)

**Observação:** O site da ABR Telecom exige interação humana para resolver o reCAPTCHA. O script pausa até o usuário apertar `ENTER` no terminal para continuar.

**Exemplo de resultado:**

| TELEFONE_EMPRESA | Nome da Prestadora | Mensagem                       |
|------------------|--------------------|--------------------------------|
| 11999998888      | Claro              | Número portado com sucesso     |
| 11988887777      | Vivo               | Número original da operadora   |

🔗 [Ver detalhes do projeto](./Consulta_Portabilidade_ABR/consultar_operadora_2.py)



### 3. 💬 Disparo de Mensagens – WhatsApp (API Evolution)

Script que envia mensagens personalizadas via **API da plataforma Evolution (WhatsApp)** com base em uma planilha.  
Possui verificação de horário, controle de envios e backups automáticos.

🔧 **Tecnologias:** Python, Pandas, Requests  
📁 Pasta: `Disparo_Mensagens`

**Funcionalidades:**
- Leitura de uma planilha Excel com contatos e mensagens
- Envio de mensagens via API REST (WhatsApp Evolution)
- Verificação de horário de envio (ex: apenas dias úteis, entre 9h e 17h)
- Marcação automática de mensagens entregues ou duplicadas
- Criação de backups da planilha a cada tentativa
- Espera de 3 minutos entre envios para evitar bloqueios

🔗 [Ver detalhes do projeto](./Disparo_Mensagens/Send_Message.py)



## 📦 Instalação

Clone o repositório e instale os pacotes necessários:

```bash
git clone https://github.com/Lucassapx/Meus-Projetos.git
cd Meus-Projetos
pip install -r requirements.txt
