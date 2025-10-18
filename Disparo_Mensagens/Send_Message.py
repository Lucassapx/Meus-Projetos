# RESUMO:
# Este script automatiza o envio de mensagens personalizadas via API do WhatsApp (Evolution),
# com base em uma planilha do Excel. Ele verifica se o horário atual está dentro do período permitido,
# e envia mensagens apenas para registros ainda não marcados como "ENTREGUE".
# Após cada envio bem-sucedido, aguarda 3 minutos antes de continuar.
# Cria backups da planilha a cada tentativa e evita envios duplicados.

import pandas as pd
import requests
from datetime import datetime
import time
import os
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

# Dados baseados em Evoluiton
# === Configurações ===
server_url = "" # URL Evolution
instance_id = "" # Nome da Instância
api_key = "" # Chave da API

arquivo_base = r"" # Arquivo base
pasta_backup = r"" # Pasta para direcionamento de backups

# Criar pasta de backup se não existir
os.makedirs(pasta_backup, exist_ok=True)

# === Função de verificação de horário permitido ===
def horario_permitido():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    dia_semana = agora.weekday()  # Segunda=0, Domingo=6
    hora_atual = agora.time()

    hora_inicio = dt_time(9, 0) # Definir início
    hora_fim = dt_time(17, 0) # Definir fim

    if dia_semana >= 5:  # sem sábado e domingo
        return False
    if not (hora_inicio <= hora_atual < hora_fim):  # até horário final
        return False

    return True

# === Função principal de envio ===
def executar_envio():
    print("Carregando planilha...")
    df = pd.read_excel(arquivo_base)
    print("Planilha carregada, total de linhas:", len(df))
    print("Colunas disponíveis:", df.columns.tolist())

    if 'ENTREGUE' not in df.columns: # Insere coluna ENTREGUE para carimbo de envios bem sucedidos
        df['ENTREGUE'] = ""
        print("Coluna 'ENTREGUE' criada.")

    pendentes = df[df['ENTREGUE'].isna() | (df['ENTREGUE'] == "")]
    total_pendentes = len(pendentes)
    print(f"Números pendentes para envio: {total_pendentes}")

    telefones_prioridade = [ # Denifir colunas de telefone para envio. Ordem de colunas defini prioridade.
        ""
    ]

    if total_pendentes == 0:
        print("Nenhum número pendente.")
        return

    contador_envios = 0

    for idx, row in pendentes.iterrows():
        # Verifica se ainda está no horário permitido.
        if not horario_permitido():
            print("⏹️ Horário final atingido durante execução. Pausando envio.")
            return

        empresa = str(row['']).strip() # Definir coluna com  Nome do Cliente.
        cnpj = str(row['']).strip() # Definir coluna com  CNPJ do Cliente.

        ja_enviado = not df[(df[''] == empresa) # Coluna Nome do Cliente
        & (df['ENTREGUE'].notna()) & (df['ENTREGUE'] != "")].empty

        if ja_enviado:
            df.at[idx, 'ENTREGUE'] = "Duplicado"
            print(f"Empresa '{empresa}' já recebeu mensagem. Marcando como Duplicado.")
        else:
            mensagem_personalizada = ( # Definir mensagem de disparo.
                f""
            )

            enviado_com_sucesso = False

            for coluna_tel in telefones_prioridade:
                raw_numero = row.get(coluna_tel, "")

                if pd.notna(raw_numero):
                    try:
                        numero = str(int(float(raw_numero))).strip()
                    except:
                        numero = str(raw_numero).strip()
                else:
                    numero = ""

                if not numero or numero.lower() == "nan":
                    continue

                if not numero.startswith("55"):
                    numero = "55" + numero

                url = f"{server_url}/message/sendText/{instance_id}"
                headers = {"apikey": api_key}
                payload = {"number": numero, "text": mensagem_personalizada}

                print(f"Tentando envio para {empresa} ({coluna_tel} - {numero})...")
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                    if response.status_code in (200, 201):
                        df.at[idx, 'ENTREGUE'] = datetime.now().strftime("%d/%m/%Y")
                        print(f"✅ Mensagem enviada com sucesso para {numero}.")
                        enviado_com_sucesso = True
                        contador_envios += 1
                        break
                    elif response.status_code in (400, 500):
                        print(f"⚠️ Falha (Sem WhatsApp): {numero}")
                        continue
                    else:
                        print(f"⚠️ Erro inesperado {response.status_code}: {numero}")
                        continue
                except Exception as e:
                    print(f"❌ Erro ao tentar enviar para {numero}: {e}")
                    continue

            if not enviado_com_sucesso:
                df.at[idx, 'ENTREGUE'] = "Não enviado"
                print(f"❌ Nenhum número válido para {empresa}.")

        # Salva planilha e backup
        df.to_excel(arquivo_base, index=False)
        backup_file = os.path.join(
            pasta_backup,
            f"Planilha_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx" # Definir nome da planilha backup com formatação para data e hora atual.
        )
        df.to_excel(backup_file, index=False)
        print(f"💾 Backup salvo em: {backup_file}")

        # Espera 3 minutos entre envios se foi bem-sucedido
        if enviado_com_sucesso:
            print("⏳ Aguardando 3 minutos antes do próximo envio...") # Definir tempo de disparo.
            for _ in range(180):  # Verifica a cada segundo se ainda está dentro do horário.
                if not horario_permitido():
                    print("🕔 Horário encerrado durante espera. Encerrando ciclo.")
                    return
                time.sleep(1)

# === Loop Principal Infinito ===
print("⏰ Iniciando monitoramento...")

while True:
    if horario_permitido():
        print("\n🔄 Horário permitido. Iniciando processo de envio.")
        executar_envio()
        print("✅ Ciclo de envio concluído.")
    else:
        agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
        print(f"\n🕒 Fora do horário permitido ({agora.strftime('%H:%M')} - {agora.strftime('%A')}). Aguardando...")
    
    # Espera antes de verificar novamente (ex: a cada 5 minutos fora do horário)
    time.sleep(300)
