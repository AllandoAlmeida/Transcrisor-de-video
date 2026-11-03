import pyaudiowpatch as pyaudio

pa = pyaudio.PyAudio()

print("=" * 80)
print("DISPOSITIVOS")
print("=" * 80)

for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)

    print(
        f"ID: {i:2d} | "
        f"Input: {info['maxInputChannels']} | "
        f"Output: {info['maxOutputChannels']} | "
        f"{info['name']}"
    )

print("\n")
print("=" * 80)
print("LOOPBACKS ENCONTRADOS")
print("=" * 80)

try:
    for device in pa.get_loopback_device_info_generator():
        print(device)
except Exception as e:
    print(e)

pa.terminate()