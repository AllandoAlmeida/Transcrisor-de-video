import os
from moviepy import VideoFileClip
import speech_recognition as sr


# Caminhos das pastas
PASTA_VIDEO = "video_transcrição"
PASTA_AUDIO = "audio_extraído"
PASTA_TRANSCRICAO = "transcrição"

# Verifica se as pastas existem, se não, cria elas
os.makedirs(PASTA_VIDEO, exist_ok=True)
os.makedirs(PASTA_AUDIO, exist_ok=True)
os.makedirs(PASTA_TRANSCRICAO, exist_ok=True)

def extrair_audio_do_video(caminho_video, caminho_audio):
    """
    Extrai o áudio de um vídeo e salva em um arquivo WAV.
    """
    try:
        video = VideoFileClip(caminho_video)
        audio = video.audio
        audio.write_audiofile(caminho_audio)
        print(f"Áudio extraído com sucesso e salvo em: {caminho_audio}")
    except Exception as e:
        return f"Erro ao extrair o áudio do vídeo: {e}"
    return caminho_audio

def dividir_audio_em_partes(caminho_audio, duracao_maxima=60):
    """
    Divide o áudio em partes menores, para facilitar a transcrição.
    """
    r = sr.Recognizer()
    audio_file = sr.AudioFile(caminho_audio)
    partes_audio = []
    
    with audio_file as source:
        # Dividir o áudio em partes menores
        duracao_audio = audio_file.DURATION
        num_partes = int(duracao_audio // duracao_maxima)
        
        for i in range(num_partes + 1):
            # Lê uma parte do áudio
            inicio = i * duracao_maxima
            fim = min((i + 1) * duracao_maxima, duracao_audio)
            print(f"Lendo parte {i + 1} de {num_partes + 1}, tempo: {inicio}-{fim} segundos")
            
            audio_parte = r.record(source, offset=inicio, duration=fim - inicio)
            partes_audio.append(audio_parte)
    
    return partes_audio

def transcrever_audio_partes(partes_audio):
    """
    Transcreve as partes do áudio e junta o texto.
    """
    texto_completo = ""
    r = sr.Recognizer()
    
    for idx, audio_parte in enumerate(partes_audio):
        try:
            print(f"Transcrevendo parte {idx + 1}...")
            texto = r.recognize_google(audio_parte, language="pt-br")
            texto_completo += texto + " "
        except sr.UnknownValueError:
            texto_completo += f"[Parte {idx + 1} não reconhecida] "
        except sr.RequestError as e:
            texto_completo += f"[Erro na requisição da parte {idx + 1}: {e}] "
    
    return texto_completo

def processar_video(nome_arquivo):
    """
    Processa o vídeo: extrai áudio, transcreve e salva os arquivos.
    """
    # Caminhos completos
    caminho_video = os.path.join(PASTA_VIDEO, nome_arquivo)
    nome_base = os.path.splitext(nome_arquivo)[0]  # Remove a extensão do arquivo
    caminho_audio = os.path.join(PASTA_AUDIO, f"{nome_base}.wav")
    caminho_transcricao = os.path.join(PASTA_TRANSCRICAO, f"{nome_base}.txt")

    # 1. Extrair o áudio do vídeo
    print(f"Extraindo áudio do vídeo: {nome_arquivo}")
    extrair_audio_do_video(caminho_video, caminho_audio)

    # 2. Dividir o áudio em partes menores
    print("Dividindo o áudio em partes...")
    partes_audio = dividir_audio_em_partes(caminho_audio)

    # 3. Transcrever as partes e salvar o texto
    print("Transcrevendo o áudio...")
    texto_transcrito = transcrever_audio_partes(partes_audio)

    # Salvar a transcrição em um arquivo de texto
    with open(caminho_transcricao, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto_transcrito)
    print(f"Transcrição salva em: {caminho_transcricao}")

def main():
    """
    Função principal que processa todos os vídeos na pasta de vídeos.
    """
    # Lista todos os arquivos na pasta de vídeos
    for nome_arquivo in os.listdir(PASTA_VIDEO):
        if nome_arquivo.endswith((".mp4", ".avi", ".mkv")):  # Verifica se é um arquivo de vídeo
            print(f"\nProcessando vídeo: {nome_arquivo}")
            processar_video(nome_arquivo)
        else:
            print(f"Ignorando arquivo não suportado: {nome_arquivo}")

if __name__ == "__main__":
    main()