import os
import shutil
import subprocess
import time
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Configuração dos caminhos locais
PASTA_ENTRADA = Path('entrada')
PASTA_CONVERTIDOS = Path('convertidos')
PASTA_PROCESSADOS = Path('processados')
PASTA_LOGS = Path('logs')

# 2. Configurações do Google Drive
ARQUIVO_CREDENCIAIS = 'credenciais.json'
ID_PASTA_DRIVE = '1Mm96D6r4nKho7D4y2f8Nqdi_OW1SVadZ'  # ID sem o ?hl=pt-br
ESCOPOS = ['https://www.googleapis.com/auth/drive.file']

def configurar_ambiente():
    PASTA_ENTRADA.mkdir(exist_ok=True)
    PASTA_CONVERTIDOS.mkdir(exist_ok=True)
    PASTA_PROCESSADOS.mkdir(exist_ok=True)
    PASTA_LOGS.mkdir(exist_ok=True)

def autenticar_google_drive():
    creds = None
    # O ficheiro token.json guardará o seu acesso para não pedir login de cada vez
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ESCOPOS)
        
    # Se não houver credencial guardada ou for inválida, pede o login no navegador
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(ARQUIVO_CREDENCIAIS, ESCOPOS)
            creds = flow.run_local_server(port=0)
            
        # Guarda as credenciais para a próxima execução
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        servico = build('drive', 'v3', credentials=creds)
        return servico
    except Exception as e:
        print(f"ERRO: Não foi possível autenticar no Google Drive. Detalhe: {e}")
        return None

def listar_audios_pendentes():
    extensoes_validas = ['.ogg', '.opus', '.m4a', '.wav', '.mp3']
    arquivos_encontrados = []
    if PASTA_ENTRADA.exists():
        for item in PASTA_ENTRADA.iterdir():
            if item.is_file() and item.suffix.lower() in extensoes_validas:
                arquivos_encontrados.append(item)
    return arquivos_encontrados

def fazer_upload_drive(servico, caminho_arquivo, nome_arquivo):
    try:
        print(f"A iniciar upload para o Drive: {nome_arquivo}...")
        metadados_arquivo = {
            'name': nome_arquivo,
            'parents': [ID_PASTA_DRIVE]
        }
        media = MediaFileUpload(str(caminho_arquivo), mimetype='audio/mpeg', resumable=True)
        
        arquivo_enviado = servico.files().create(
            body=metadados_arquivo,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"Upload concluído com sucesso! (ID: {arquivo_enviado.get('id')})")
        return True
    except Exception as e:
        print(f"Erro durante o upload de {nome_arquivo}: {e}")
        return False

def processar_e_converter_audios(arquivos, servico_drive):
    for original in arquivos:
        nome_base = original.stem
        
        # Adiciona o timestamp para evitar sobrescrita de ficheiros com o mesmo nome
        carimbo_tempo = int(time.time())
        nome_arquivo_mp3 = f"{nome_base}_{carimbo_tempo}.mp3"
        
        caminho_destino = PASTA_CONVERTIDOS / nome_arquivo_mp3
        
        print(f"\nProcessando: {original.name}")
        
        try:
            # 1. Converter para MP3
            comando = [
                "ffmpeg", "-y", "-i", str(original), 
                "-b:a", "192k", str(caminho_destino)
            ]
            subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(" - Conversão para MP3 concluída.")
            
            # 2. Fazer Upload para o Drive
            if servico_drive:
                sucesso_upload = fazer_upload_drive(servico_drive, caminho_destino, nome_arquivo_mp3)
                
                # 3. Mover o original se tudo correr bem
                if sucesso_upload:
                    shutil.move(str(original), str(PASTA_PROCESSADOS / original.name))
                    print(f" - Ficheiro original movido para a pasta '{PASTA_PROCESSADOS.name}'.")
                else:
                    print(" - Falha no upload. O ficheiro original não foi movido.")
            else:
                print(" - Serviço do Drive indisponível. Conversão feita, mas upload ignorado.")
                
        except Exception as e:
            print(f" - Erro ao processar o ficheiro {original.name}: {e}")

if __name__ == '__main__':
    configurar_ambiente()
    
    print("A autenticar no Google Drive...")
    servico_drive = autenticar_google_drive()
    
    audios = listar_audios_pendentes()
    if audios:
        print(f"Encontrado(s) {len(audios)} ficheiro(s). A iniciar processamento...")
        processar_e_converter_audios(audios, servico_drive)
    else:
        print("Nenhum áudio para processar no momento.")