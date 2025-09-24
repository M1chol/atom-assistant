import sounddevice as sd
from piper.voice import PiperVoice
from piper.config import SynthesisConfig
from queue import Empty, Queue
import numpy as np
import json

class ttsWrapper:
    def __init__(self) -> None:
        with open("config.json") as f:
            self.__config = json.load(f)
        self.__model_path = self.__config['tts_model_path']
        self.__voice = PiperVoice.load(self.__model_path)
        self.__syn_config = SynthesisConfig(
            length_scale=self.__config['tts_config']['length_scale'],
            noise_scale=self.__config['tts_config']['noise_scale'],
            noise_w_scale=self.__config['tts_config']['noise_w_scale'],
            volume=self.__config['tts_config']['volume']
        )
        self.__stream = sd.OutputStream(
            samplerate=self.__voice.config.sample_rate,
            channels=1,
            dtype="int16",
            latency="high",
            blocksize=1024,
            callback=self.callback
        )
        self.__queue = Queue()
    
    def __del__(self):
        self.__stream.stop()
        self.__stream.close()

    def callback(self, outdata, frames, time, status):
        if status:
            print("callback:", status)
        try:
            chunk = self.__queue.get_nowait()
        except Empty:
            chunk = np.zeros((frames, 1), dtype=np.int16)
            return
        if len(chunk) < frames:
            outdata[:len(chunk)] = chunk
            outdata[len(chunk):] = 0
        else:
            outdata[:] = chunk[:frames]

    def speak(self, text: str) -> None:
        self.__stream.start()
        for audio_chunk in self.__voice.synthesize(text, syn_config=self.__syn_config):
            audio_bytes = audio_chunk.audio_int16_array
            self.__stream.write(audio_bytes)
        self.__stream.stop()
    
    def speak_streamed(self, text_fragment: str) -> None:
        self.__queue.put(text_fragment)