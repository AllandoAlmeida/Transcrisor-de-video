# Transcrição de Vídeos

## Crie e ative o ambiente virtual

Este projeto permite extrair o áudio de vídeos, dividi-lo em partes menores e transcrever o conteúdo em texto. Ele é organizado em pastas para facilitar o gerenciamento dos arquivos.

## O que o código faz agora?

1. **Localiza o vídeo na pasta `video_transcrição`:**

   - O código verifica todos os arquivos na pasta `video_transcrição` e processa apenas os arquivos de vídeo (extensões `.mp4`, `.avi`, `.mkv`).

2. **Extrai o áudio e salva na pasta `audio_extraído`:**

   - O áudio é extraído e salvo com o mesmo nome do arquivo de vídeo, mas com a extensão `.wav`.

3. **Transcreve o áudio e salva o texto na pasta `transcrição`:**

   - O texto transcrito é salvo em um arquivo `.txt` com o mesmo nome do arquivo de vídeo.

4. **Organização das pastas:**
   - O código cria as pastas `audio_extraído` e `transcrição` se elas não existirem.

## Como usar?

1. Coloque seus vídeos na pasta `video_transcrição`.
2. Execute o código.
3. O áudio extraído será salvo na pasta `audio_extraído`.
4. A transcrição será salva na pasta `transcrição`.

## Estrutura de Pastas

Após a execução, a estrutura de pastas será semelhante a esta:

Meu_Projeto/
├── video_transcrição/
│ └── video_exemplo.mp4
├── audio_extraído/
│ └── video_exemplo.wav
└── transcrição/
└── video_exemplo.txt

## Requisitos

- Python 3.x
- Bibliotecas necessárias: `moviepy`, `speechrecognition`

Instale as bibliotecas com o seguinte comando:

```bash
pip install moviepy speechrecognition

Executando o Projeto
Para executar o projeto, basta rodar o script Python:

python seu_script.py

```
