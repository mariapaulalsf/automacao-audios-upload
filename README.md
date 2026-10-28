# 🎙️ Automação de Processamento de Áudios e Upload (Google Drive)

Um pipeline em Python desenvolvido para automatizar o fluxo de trabalho com arquivos de áudio do WhatsApp (OGG/OPUS). O sistema processa os arquivos em lote, converte-os para MP3 e realiza o upload automático e seguro para uma pasta designada no Google Drive.

Projeto inicialmente desenhado para resolver um gargalo operacional em um escritório de advocacia, eliminando o tempo gasto com conversão e organização manual de evidências em áudio.

## Funcionalidades

- **Leitura em Lote:** Mapeia automaticamente a pasta de `entrada` em busca de arquivos de áudio suportados (`.ogg`, `.opus`, `.m4a`, `.wav`).
- **Conversão de Alta Qualidade:** Utiliza o FFmpeg via `subprocess` para converter os arquivos para `.mp3` (192kbps).
- **Prevenção de Sobrescrita:** Aplica timestamps únicos aos arquivos convertidos, garantindo que áudios com o mesmo nome original não se percam.
- **Upload Automatizado (OAuth 2.0):** Integra-se de forma nativa com a API v3 do Google Drive.
- **Gestão Segura de Estado:** Move os arquivos processados com sucesso para uma pasta de backup local (`processados`), evitando duplicação em execuções futuras.

## Tecnologias Utilizadas

- **Python 3.x**
- **Google Drive API v3** (`google-api-python-client`, `google-auth-oauthlib`)
- **FFmpeg** (Engine de processamento de áudio)
- Bibliotecas nativas: `shutil`, `pathlib`, `subprocess`, `time`

## Pré-requisitos

1. **Python 3.8+** instalado.
2. **FFmpeg** instalado e adicionado às variáveis de ambiente (PATH) do seu sistema operacional.
3. Um projeto ativo no [Google Cloud Console](https://console.cloud.google.com/) com a **Google Drive API** ativada.

## Como Instalar e Executar

**1. Clone o repositório:**
```bash
git clone [https://github.com/mariapaulalsf/nome-do-seu-repositorio.git](https://github.com/mariapaulalsf/nome-do-seu-repositorio.git)
cd nome-do-seu-repositorio
