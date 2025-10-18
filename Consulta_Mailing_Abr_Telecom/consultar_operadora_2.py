"""
==================================================
📞 Consulta de Portabilidade - ABR Telecom (Selenium)
==================================================

⚙️ Funcionamento:
- Lê uma planilha com números de telefone.
- Separa os números em arquivos `.txt` com blocos de 30 para upload.
- Acessa o site da ABR Telecom para consulta de portabilidade.
- Aguarda o usuário resolver o reCAPTCHA e clicar manualmente.
- Extrai a operadora e a mensagem de status de cada número.
- Atualiza a planilha com os dados da consulta (prestadora e mensagem).
- Salva o resultado final em uma nova planilha.

📦 Requisitos:
- Chrome instalado e ChromeDriver compatível (caminho configurado).
- Planilha Excel com coluna de telefones.
- Site da ABR Telecom requer resolução manual do reCAPTCHA.
- Pastas e nomes de arquivos de entrada/saída definidos corretamente.

==================================================
"""

import os
import glob
import time
import threading
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIGURAÇÕES ===
CAMINHO_CHROMEDRIVER = r"" # Chrome Driver.
PLANILHA_PATH = "" # Definir planilha com resultados
PASTA_SAIDA = "" # Definir saidas de numeros por blocos de 30 numeros.
PLANILHA_SAIDA = "" # Definir planilha com resultado final.
URL = "https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg" # URL ABR Telecom

# === FUNÇÃO: Separar os números em arquivos TXT com 30 por bloco ===
def separar_clientes_em_txt():
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    arquivos_existentes = glob.glob(os.path.join(PASTA_SAIDA, '*.txt'))
    for arquivo in arquivos_existentes:
        os.remove(arquivo)

    df = pd.read_excel(PLANILHA_PATH)
    df_filtrado = df[df[''].notna()].copy() # Definir coluna da planilha de resultados para gerar blocos.
    
    # Limpeza completa: remove tudo que não for número.
    df_filtrado['Telefone'] = (
        df_filtrado[''] # Definir coluna da planilha de resultados
        .astype(str)
        .str.replace(r'\D', '', regex=True)
    )

    telefones = df_filtrado['Telefone'].tolist()

    bloco = 1
    for i in range(0, len(telefones), 30):
        telefones_bloco = telefones[i:i + 30]
        caminho_saida = os.path.join(PASTA_SAIDA, f'abr_{bloco}.txt') # Nomeia os blocos com os telefones.

        with open(caminho_saida, 'w', encoding='utf-8') as f:
            for telefone in telefones_bloco:
                f.write(f"{telefone}\n")

        bloco += 1

    print("✅ Arquivos .txt com blocos de 30 números salvos em 'base/abr'.")

# === FUNÇÃO: Esperar ENTER com timeout ===
def esperar_enter(timeout=120):
    print("\n" + "="*60)
    print(f">>> Você tem até {timeout} segundos para apertar ENTER e continuar...") # Defini tempo para apertar ENTER.
    print("="*60)

    result = {"pressed": False}
    def esperar():
        input()
        result["pressed"] = True

    thread = threading.Thread(target=esperar)
    thread.start()

    for i in range(timeout):
        if result["pressed"]:
            break
        print(f"Aguardando ENTER... {timeout - i}s restantes", end='\r') # Código aguarda pressionar ENTER para prosseguir.
        time.sleep(1)

    if not result["pressed"]:
        print("\n⏰ Tempo esgotado. Continuando mesmo assim...")

# === FUNÇÃO: Consultar telefones no site ===
def consultar_telefones(driver, wait, df, index_atual):
    driver.get(URL)

    # Aguarda usuário resolver o reCAPTCHA manualmente
    esperar_enter()

    try:
        wait.until(EC.element_to_be_clickable((By.ID, "idSubmit"))).click()
    except Exception as e:
        print(f"Erro ao clicar no botão CONSULTAR: {e}")
        return df, index_atual

    try:
        wait.until(EC.presence_of_element_located((By.ID, "resultado")))
        time.sleep(2)
    except Exception as e:
        print(f"Erro ao esperar a tabela aparecer: {e}")
        return df, index_atual

    # Coleta os dados da tabela
    linhas = driver.find_elements(By.CSS_SELECTOR, "#resultado tbody tr")
    resultados = []
    for linha in linhas:
        colunas = linha.find_elements(By.TAG_NAME, "td")
        if len(colunas) >= 5:
            telefone = colunas[0].text.strip()
            nome_prestadora = colunas[1].text.strip()
            mensagem = colunas[4].text.strip()
            resultados.append((telefone, nome_prestadora, mensagem))

    # Atualiza o DataFrame com os resultados
    for tel, prestadora, msg in resultados:
        try:
            # Limpa o telefone retornado pelo site (só dígitos)
            tel_limpo = ''.join(filter(str.isdigit, tel))

            # Compara com coluna TELEFONE_EMPRESA limpa
            idx = df[
                df[""] # Definir coluna da planilha de resultados
                .astype(str)
                .str.replace(r'\D', '', regex=True) == tel_limpo
            ].index

            if not idx.empty:
                linha = idx[0]
                df.loc[linha, "Nome da Prestadora"] = prestadora # Gera planilha final com coluna de prestadores.
                df.loc[linha, "Mensagem"] = msg # Gera planilha final com coluna de mensagem.
        except Exception as e:
            print(f"Erro ao salvar dados da linha com telefone {tel}: {e}")

    index_atual += 20
    return df, index_atual

# === FUNÇÃO: Carregar e preparar planilha ===
def carregar_planilha():
    df = pd.read_excel(PLANILHA_PATH)
    # Normaliza a coluna TELEFONE_EMPRESA: só dígitos.
    if '' in df.columns: # Definir coluna da planilha de resultados nas 3 linhas.
        df[''] = ( 
            df[''] 
            .astype(str)
            .str.replace(r'\D', '', regex=True)
        )
    if "Nome da Prestadora" not in df.columns:
        df["Nome da Prestadora"] = ""
    if "Mensagem" not in df.columns:
        df["Mensagem"] = ""
    return df

# === FUNÇÃO: Configurar o navegador Selenium ===
def configurar_driver():
    servico = Service(CAMINHO_CHROMEDRIVER)
    opcoes = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=servico, options=opcoes)
    wait = WebDriverWait(driver, 120)
    return driver, wait

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    # Etapa 1: Gerar arquivos de telefone em TXT.
    separar_clientes_em_txt()

    # Etapa 2: Carrega planilha e navegador.
    df = carregar_planilha()
    driver, wait = configurar_driver()

    index_atual = 0
    try:
        while index_atual < len(df):
            df, index_atual = consultar_telefones(driver, wait, df, index_atual)
            time.sleep(2)
    except Exception as e:
        print("⚠️ Erro inesperado ou navegador fechado:", e)
    finally:
        df.to_excel(PLANILHA_SAIDA, index=False)
        print("✅ Consulta finalizada e planilha salva com sucesso!")
        driver.quit()
