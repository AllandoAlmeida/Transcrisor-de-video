import os
import wave
import datetime
import numpy as np
import pyaudiowpatch as pyaudio
import speech_recognition as sr


PASTA_TRANSCRICAO = "transcrição"
os.makedirs(PASTA_TRANSCRICAO, exist_ok=True)

MIC_DEVICE_INDEX = 1
LOOPBACK_DEVICE_INDEX = 19
CHUNK = 1024


def abrir_stream(pa, device_index):
    info = pa.get_device_info_by_index(device_index)

    channels = int(info["maxInputChannels"])
    rate = int(info["defaultSampleRate"])

    if channels <= 0:
        raise RuntimeError(f"Dispositivo inválido para entrada: {info['name']}")

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=rate,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK,
    )

    return stream, rate, channels, info["name"]


def bytes_para_mono(audio_bytes, channels):
    audio = np.frombuffer(audio_bytes, dtype=np.int16)

    resto = len(audio) % channels
    if resto:
        audio = audio[:-resto]

    audio = audio.reshape(-1, channels)
    mono = audio.mean(axis=1)

    return mono.astype(np.float32)


def reamostrar(audio, taxa_origem, taxa_destino):
    if taxa_origem == taxa_destino:
        return audio

    duracao = len(audio) / taxa_origem
    x_old = np.linspace(0, duracao, len(audio), endpoint=False)
    x_new = np.linspace(0, duracao, int(duracao * taxa_destino), endpoint=False)

    return np.interp(x_new, x_old, audio).astype(np.float32)


def capturar_audio_completo(caminho_audio, duracao=10):
    pa = pyaudio.PyAudio()

    mic_stream = None
    pc_stream = None

    try:
        mic_stream, mic_rate, mic_channels, mic_name = abrir_stream(pa, MIC_DEVICE_INDEX)
        pc_stream, pc_rate, pc_channels, pc_name = abrir_stream(pa, LOOPBACK_DEVICE_INDEX)

        print(f"\nCapturando tudo por {duracao} segundos...")
        print(f"🎤 Microfone: {mic_name} | {mic_rate} Hz | {mic_channels} canal(is)")
        print(f"🔊 PC Loopback: {pc_name} | {pc_rate} Hz | {pc_channels} canal(is)")

        mic_frames = []
        pc_frames = []

        total_chunks = int(max(mic_rate, pc_rate) / CHUNK * duracao)

        for _ in range(total_chunks):
            try:
                
                mic_frames.append(mic_stream.read(CHUNK, exception_on_overflow=False))
                pc_frames.append(pc_stream.read(CHUNK, exception_on_overflow=False))
            except KeyboardInterrupt:
                print("\nInterrupção solicitada durante a captura.")
                raise    

        mic_audio = bytes_para_mono(b"".join(mic_frames), mic_channels)
        pc_audio = bytes_para_mono(b"".join(pc_frames), pc_channels)

        taxa_final = pc_rate
        mic_audio = reamostrar(mic_audio, mic_rate, taxa_final)

        tamanho = min(len(mic_audio), len(pc_audio))
        mic_audio = mic_audio[:tamanho]
        pc_audio = pc_audio[:tamanho]

        mix = (mic_audio * 0.8) + (pc_audio * 0.8)

        pico = np.max(np.abs(mix))
        if pico > 32767:
            mix = mix / pico * 32767

        mix = mix.astype(np.int16)

        with wave.open(caminho_audio, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
            wf.setframerate(taxa_final)
            wf.writeframes(mix.tobytes())

        print(f"Áudio salvo: {caminho_audio}")

    finally:
        if mic_stream:
            mic_stream.stop_stream()
            mic_stream.close()

        if pc_stream:
            pc_stream.stop_stream()
            pc_stream.close()

        pa.terminate()


def transcrever_audio(caminho_audio):
    r = sr.Recognizer()

    with sr.AudioFile(caminho_audio) as source:
        audio = r.record(source)

    try:
        return r.recognize_google(audio, language="pt-BR")
    except sr.UnknownValueError:
        return "[Fala não reconhecida]"
    except sr.RequestError as e:
        return f"[Erro na requisição: {e}]"


def transcrever_reuniao(intervalo=10):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    nome_arquivo = f"Transcricao_{timestamp}.txt"

    caminho_transcricao = os.path.join(
        PASTA_TRANSCRICAO,
        nome_arquivo
    )

    print(f"Transcrição será salva em: {caminho_transcricao}")
    print(f"🎤 Microfone ID: {MIC_DEVICE_INDEX}")
    print(f"🔊 Loopback ID: {LOOPBACK_DEVICE_INDEX}")

    with open(caminho_transcricao, "w", encoding="utf-8") as arquivo:
        try:
            while True:
                caminho_temp = "temp_audio.wav"

                capturar_audio_completo(caminho_temp, duracao=intervalo)

                tempo = datetime.datetime.now().strftime("%H:%M:%S")
                texto = transcrever_audio(caminho_temp)

                print(f"[{tempo}] {texto}")
                arquivo.write(f"[{tempo}] {texto}\n")
                arquivo.flush()

                if os.path.exists(caminho_temp):
                    os.remove(caminho_temp)

        except KeyboardInterrupt:
            print("\nTranscrição finalizada por solicitação do usuário.")


if __name__ == "__main__":
    transcrever_reuniao(intervalo=10)
    
""" import os
import wave
import datetime
import numpy as np
import pyaudiowpatch as pyaudio
import speech_recognition as sr


PASTA_TRANSCRICAO = "transcrição"
os.makedirs(PASTA_TRANSCRICAO, exist_ok=True)

MIC_DEVICE_INDEX = 1
LOOPBACK_DEVICE_INDEX = 14
CHUNK = 1024


def abrir_stream_microfone(pa, device_index):
    info = pa.get_device_info_by_index(device_index)

    channels = int(info["maxInputChannels"])
    rate = int(info["defaultSampleRate"])

    if channels <= 0:
        raise RuntimeError(f"Dispositivo inválido para microfone: {info['name']}")

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=rate,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK,
    )

    return stream, rate, channels, info["name"]


def abrir_stream_loopback(pa, device_index):
    info = pa.get_device_info_by_index(device_index)

    channels = int(info["maxInputChannels"])
    rate = int(info["defaultSampleRate"])

    if channels <= 0:
        raise RuntimeError(
            f"Dispositivo inválido para loopback: {info['name']}. "
            "Escolha um dispositivo que tenha '(loopback)' no nome."
        )

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=rate,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK,
    )

    return stream, rate, channels, info["name"]

def bytes_para_mono(audio_bytes, channels):
    audio = np.frombuffer(audio_bytes, dtype=np.int16)

    resto = len(audio) % channels
    if resto:
        audio = audio[:-resto]

    audio = audio.reshape(-1, channels)
    mono = audio.mean(axis=1)

    return mono.astype(np.float32)


def reamostrar(audio, taxa_origem, taxa_destino):
    if taxa_origem == taxa_destino:
        return audio

    duracao = len(audio) / taxa_origem
    x_old = np.linspace(0, duracao, len(audio), endpoint=False)
    x_new = np.linspace(0, duracao, int(duracao * taxa_destino), endpoint=False)

    return np.interp(x_new, x_old, audio).astype(np.float32)


def capturar_audio_completo(caminho_audio, duracao=10):
    pa = pyaudio.PyAudio()

    mic_stream = None
    pc_stream = None

    try:
        mic_stream, mic_rate, mic_channels, mic_name = abrir_stream_microfone(
            pa,
            MIC_DEVICE_INDEX
        )

        pc_stream, pc_rate, pc_channels, pc_name = abrir_stream_loopback(
            pa,
            LOOPBACK_DEVICE_INDEX
        )

        print(f"\nCapturando tudo por {duracao} segundos...")
        print(f"🎤 Microfone: {mic_name} | {mic_rate} Hz | {mic_channels} canal(is)")
        print(f"🔊 PC Loopback: {pc_name} | {pc_rate} Hz | {pc_channels} canal(is)")

        mic_frames = []
        pc_frames = []

        taxa_base = max(mic_rate, pc_rate)
        total_chunks = int(taxa_base / CHUNK * duracao)

        for _ in range(total_chunks):
            mic_frames.append(
                mic_stream.read(CHUNK, exception_on_overflow=False)
            )

            pc_frames.append(
                pc_stream.read(CHUNK, exception_on_overflow=False)
            )

        mic_audio = bytes_para_mono(b"".join(mic_frames), mic_channels)
        pc_audio = bytes_para_mono(b"".join(pc_frames), pc_channels)

        taxa_final = pc_rate
        mic_audio = reamostrar(mic_audio, mic_rate, taxa_final)

        tamanho = min(len(mic_audio), len(pc_audio))
        mic_audio = mic_audio[:tamanho]
        pc_audio = pc_audio[:tamanho]

        mix = (mic_audio * 0.8) + (pc_audio * 0.8)

        pico = np.max(np.abs(mix))
        if pico > 32767:
            mix = mix / pico * 32767

        mix = mix.astype(np.int16)

        with wave.open(caminho_audio, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
            wf.setframerate(taxa_final)
            wf.writeframes(mix.tobytes())

        print(f"Áudio salvo: {caminho_audio}")

    finally:
        if mic_stream:
            mic_stream.stop_stream()
            mic_stream.close()

        if pc_stream:
            pc_stream.stop_stream()
            pc_stream.close()

        pa.terminate()


def transcrever_audio(caminho_audio):
    r = sr.Recognizer()

    with sr.AudioFile(caminho_audio) as source:
        audio = r.record(source)

    try:
        return r.recognize_google(audio, language="pt-BR")
    except sr.UnknownValueError:
        return "[Fala não reconhecida]"
    except sr.RequestError as e:
        return f"[Erro na requisição: {e}]"


def transcrever_reuniao(intervalo=10):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"Transcricao_{timestamp}.txt"

    caminho_transcricao = os.path.join(PASTA_TRANSCRICAO, nome_arquivo)

    print(f"Transcrição será salva em: {caminho_transcricao}")
    print(f"🎤 Microfone ID: {MIC_DEVICE_INDEX}")
    print(f"🔊 Loopback ID: {LOOPBACK_DEVICE_INDEX}")

    with open(caminho_transcricao, "w", encoding="utf-8") as arquivo:
        try:
            while True:
                caminho_temp = "temp_audio.wav"

                capturar_audio_completo(caminho_temp, duracao=intervalo)

                tempo = datetime.datetime.now().strftime("%H:%M:%S")
                texto = transcrever_audio(caminho_temp)

                print(f"[{tempo}] {texto}")
                arquivo.write(f"[{tempo}] {texto}\n")
                arquivo.flush()

                if os.path.exists(caminho_temp):
                    os.remove(caminho_temp)

        except KeyboardInterrupt:
            print("\nTranscrição finalizada por solicitação do usuário.")

            if os.path.exists("temp_audio.wav"):
                os.remove("temp_audio.wav")


if __name__ == "__main__":
    transcrever_reuniao(intervalo=10) """