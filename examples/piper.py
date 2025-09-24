import sounddevice as sd
from piper.voice import PiperVoice
from piper.config import SynthesisConfig

# Setup
model = "models/pl_PL-darkman-medium.onnx"
print(f"Loading voice model from: {model}")
voice = PiperVoice.load(model)
print("Voice loaded successfully.")

syn_config = SynthesisConfig(
            length_scale=0.8,     # speed
            noise_scale=0.2,    # variation
            noise_w_scale=0.8,  # speaking variation
            volume=0.5
        )

stream = sd.OutputStream(
    samplerate=voice.config.sample_rate,
    channels=1,
    dtype="int16",
    latency="high"
)

try:
    text = input(">>> ").strip()
    while text != "quit":
        stream.start()
        for audio_chunk in voice.synthesize(text, syn_config=syn_config):
            audio_bytes = audio_chunk.audio_int16_array
            stream.write(audio_bytes)
        stream.stop()
        text = input(">>> ").strip()
except KeyboardInterrupt:
    pass

stream.stop()
stream.close()

print("Program stopped")
