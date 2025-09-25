import sounddevice as sd
from sounddevice import CallbackFlags
from piper.voice import PiperVoice
from piper.config import SynthesisConfig
from queue import Empty, Queue
import numpy as np
import json
import threading
from time import sleep

class ttsWrapper:
    def __init__(self) -> None:
        with open("config.json") as f:
            self.__config = json.load(f)['tts_config']
        if not self.__config:
            raise FileNotFoundError("config file not found")
        self.__model_path = self.__config['model_dir'] + '/' + self.__config['model'] + ".onnx"
        self.__voice = PiperVoice.load(self.__model_path)
        self.__syn_config = SynthesisConfig(
            length_scale=self.__config['length_scale'],
            noise_scale=self.__config['noise_scale'],
            noise_w_scale=self.__config['noise_w_scale'],
            volume=self.__config['volume']
        )
        self.__stream = sd.OutputStream(
            samplerate=self.__voice.config.sample_rate,
            channels=1,
            dtype="int16",
            latency="high",
            blocksize=self.__config['blocksize'],
            callback=self.callback
        )
        self.__audio_queue = Queue(maxsize=self.__config['buffersize'])
        self.__text_queue = Queue()
        self.__leftover = np.empty((0, 1), dtype=np.int16)
        self.__audio_thread = threading.Thread(target=self.__worker, daemon=True)
        self.__audio_thread_stop_event = threading.Event()

        self.__stream.start()
        self.__audio_thread.start()
    
    def __del__(self):
        self.__audio_thread_stop_event.set()
        self.__stream.stop()
        self.__stream.close()

    def callback(self, outdata, frames, time, status):
        wrote = 0
        
        def copy_from(src):
            nonlocal wrote
            if src.size == 0:
                return 0
            take = min(len(src), frames - wrote)
            outdata[wrote : wrote + take] = src[:take]
            wrote += take
            return take
        
        # First add leftover bytes
        if len(self.__leftover) > 0 and wrote < frames:
            taken = copy_from(self.__leftover)
            if taken < len(self.__leftover):
                self.__leftover = self.__leftover[taken:]
            else:
                self.__leftover = self.__leftover[0:0]
            
        while wrote < frames:
            try:
                data = self.__audio_queue.get_nowait()
            except Empty:
                outdata[wrote:frames] = 0
                # self.__queue_is_empty = True
                return
            data = data.reshape(-1, 1)
            if data.size == 0:
                continue
            taken = copy_from(data)
            if taken < len(data):
                self.__leftover = data[taken:]
                return

    def __push_text(self, text: str) -> None:
        if not text.strip():
            return
        for audio_chunk in self.__voice.synthesize(text, syn_config=self.__syn_config):
            audio_bytes = audio_chunk.audio_int16_array
            self.__audio_queue.put(audio_bytes)
    
    def __worker(self):
        print("[TTS] Worker started")
        sentence = ""
        while not self.__audio_thread_stop_event.is_set():
            token = self.__text_queue.get()
            if token is None or token in ['.', '!', '?', ','] or len(sentence.split()) > 5:
                if token: 
                    sentence += token
                if sentence:
                    self.__push_text(sentence)
                sentence = ""
            else:
                sentence += token

    def speak(self, text:str | None):
        self.__text_queue.put(text)