"""
==================================================
🗺️ Google Maps Scraper Automatizado (Selenium)
==================================================

⚙️ Funcionamento:
- Lê uma planilha com logradouros e cidades.
- Formata os endereços e realiza buscas no Google Maps.
- Rola a lista de resultados e extrai nome, telefone e endereço das empresas.
- Salva os dados em uma planilha final e marca os endereços já consultados.
- Permite pausar (`[`) ou trocar de perfil (`]`) durante a execução.
- Reinicia o navegador ao trocar de perfil para evitar captchas.

📦 Requisitos:
- Chrome instalado e driver compatível (com caminho configurado no script).
- Planilha Excel com colunas de logradouro e cidade.
- Arquivo `quantidade.json` para definir o número de buscas por execução.
- Pastas e caminhos para salvar resultados e backups definidos corretamente.

==================================================
"""

import time
import pandas as pd
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import keyboard

pause_flag = False
profile_flag = 1
restart_driver_flag = False

def toggle_pause(): # Botão de Pausa do Script '['.
    global pause_flag
    pause_flag = not pause_flag
    print("\n[PAUSA] Script pausado. Pressione [ novamente para continuar." if pause_flag else "\n[CONTINUAÇÃO] Script retomado.")

def toggle_profile(): # Trocar profile para evitar Captcha ']'.
    global profile_flag, restart_driver_flag
    profile_flag += 1
    if profile_flag > 5:
        profile_flag = 1
    restart_driver_flag = True
    print(f"\n🔄 Trocando para Profile {profile_flag}...")

keyboard.add_hotkey('[', toggle_pause)
keyboard.add_hotkey(']', toggle_profile)

def wait_if_paused():
    while pause_flag:
        time.sleep(0.5)

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f'--profile-directory=Profile {profile_flag}')
    service = Service(r"")  # Chrome Driver. Atualize conforme necessário.
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def search_address(driver, query):
    driver.get(f"https://www.google.com/maps/search/{query}") # URL Google Maps.
    time.sleep(10)

def get_company_data(driver):
    results = []

    time.sleep(4)
    scrollable_div_xpath = '//div[@role="feed"]' # Scroll Automático.
    try:
        scrollable_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, scrollable_div_xpath))
        )
    except:
        print("❌ Não foi possível localizar a área de resultados da pesquisa.")
        return results

    # Scroll para carregar mais resultados.
    for _ in range(10):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(1.5)

    # Novo XPath para os cards.
    cards = driver.find_elements(By.XPATH, '//div[contains(@class,"Nv2PK")]') # Analisa quantidade de cards encontrado por psquisa.
    print(f"🔎 Encontradas {len(cards)} empresas visíveis na lista.")

    for i in range(len(cards)):
        try:
            wait_if_paused()

            # Re-localiza todos os cards a cada iteração.
            cards = driver.find_elements(By.XPATH, '//div[contains(@class,"Nv2PK")]') # Clica nos cards.
            if i >= len(cards):
                break
            card = cards[i]

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", card)
            time.sleep(1)

            # Clica no card diretamente.
            actions = ActionChains(driver)
            actions.move_to_element(card).click().perform()

            # Aguarda o painel da empresa abrir.
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//h1[contains(@class, "DUwDvf")]'))
            )

            nome = driver.find_element(By.XPATH, '//h1[contains(@class, "DUwDvf")]').text

            try:
                telefone = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "phone")]/div[1]/div[2]/div').text # Pega dados de Telefone.
            except:
                telefone = "N/A"

            try:
                endereco = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "address")]/div[1]/div[2]/div').text # Pega dados de Endereço.
            except:
                endereco = "N/A"

            print(f"✅ [{i+1}] {nome} | {telefone} | {endereco}")
            results.append({ # Gera planilha final com as seguintes Colunas.
                "NM_EMPRESA": nome, 
                "TELEFONE_EMPRESA": telefone,
                "TELEFONE_EMPRESA_2": "N/A",
                "ENDERECO": endereco
            })

            time.sleep(2)

            # Voltar para a lista.
            driver.execute_script("window.history.go(-1)")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
            )
            time.sleep(2)

        except Exception as e:
            print(f"❌ Erro ao extrair dados da empresa [{i+1}]: {e}")
            continue

    return results

def salvar_parcial(extracted_data):
    if extracted_data:
        parcial_df = pd.DataFrame(extracted_data)
        parcial_df.to_excel("", index=False) # Definir planilha de backup com resultados parciais.
        print("Backup salvo")

def extrair_nome_rua(logradouro):
    match = re.match(r"^[^,]+", str(logradouro).strip())
    return match.group(0) if match else str(logradouro).strip()

def main():
    global restart_driver_flag

    with open("quantidade.json", "r", encoding="utf-8") as f: # Lê arquivo que define a qualidade de endereços que devem ser consultados.
        config = json.load(f)
    qtd_consultas = config.get("Quantidade", 0)

    df = pd.read_excel("") # Lê planilha com endereços.

    if "Consultado" not in df.columns: 
        df["Consultado"] = ""
    df["Consultado"] = df["Consultado"].astype(str)  # Corrige dtype do pandas.

    df_nao_consultado = df[df["Consultado"] != "Sim"] # Cria coluna para registro das quais já foram consultadas.
    df_para_consultar = df_nao_consultado.head(qtd_consultas)

    if qtd_consultas <= 0:
        print("⚠️ O valor de 'Quantidade' no arquivo quantidade.json está vazio ou igual a 0.")
        return

    if df_nao_consultado.empty:
        print("✅ Todos os endereços da planilha já foram consultados. Nada novo pra rodar.")
        return

    if df_para_consultar.empty:
        print(f"⚠️ Existem endereços não consultados, mas o limite de {qtd_consultas} não cobre nenhum novo.")
        return

    extracted_data = []
    searched_addresses = set()

    index_list = list(df_para_consultar.index)
    i = 0
    driver = setup_driver()

    try:
        while i < len(index_list):
            wait_if_paused()

            if restart_driver_flag:
                print(f"♻️ Reiniciando navegador com Profile {profile_flag}...")
                driver.quit()
                driver = setup_driver()
                restart_driver_flag = False

            index = index_list[i]
            logradouro = df.at[index, ""] # Definir coluna com Rua/Avenida.
            cidade = df.at[index, ""] # Definir coluna com Cidade.

            nome_rua = extrair_nome_rua(logradouro).upper()
            endereco_formatado = f"empresas+RUA+{nome_rua.replace(' ', '+')}+{cidade.upper().replace(' ', '+')}" # Formatação para pesquisa no Google Maps.

            if endereco_formatado in searched_addresses:
                i += 1
                continue

            searched_addresses.add(endereco_formatado)

            print(f"\n📍 Consulta de mailing número {i+1}/{qtd_consultas}") # Print momentâneo com quantidade de endereços que já foram consultados.
            print(f"🔍 Pesquisando: {endereco_formatado}")
            search_address(driver, endereco_formatado)

            company_data = get_company_data(driver)

            for data in company_data:
                extracted_data.append(data)

            df.at[index, "Consultado"] = "Sim"
            i += 1

    except Exception as e:
        print("❌ Erro durante a execução:", e)
        salvar_parcial(extracted_data)

    finally:
        if driver:
            driver.quit()

        final_df = pd.DataFrame(extracted_data)
        os.makedirs("", exist_ok=True) # Definir pasta para planilha de resultado.
        final_df.to_excel("", index=False) # Definir pasta / nome da planilha resultado.
        df.to_excel("base/data_1.xlsx", index=False)

        print("✅ Processo finalizado! Resultados salvos em ''.") # Definir caminho de saída com resultado para visualização final.

if __name__ == "__main__":
    main()
