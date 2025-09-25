from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json
import threading
import queue
import sys

class sttWrapper:

    def __init__(self, callback) -> None:
        with open("config.json") as f:
            self.__config = json.load(f)['stt_config']
        if not self.__config:
            raise FileNotFoundError("config file not found")
        self.__model = Model(lang=self.__config['model'])
        self.__samplerate = self.__config['microphone_samplerate']
        self.__stream = sd.RawInputStream(samplerate=self.__samplerate, 
                                        blocksize = self.__config['blocksize'], 
                                        device=sd.default.device,
                                            dtype="int16", channels=1, callback=self.__callback)
        self.__queue = queue.Queue()
        self.__listening_thread = threading.Thread(target=self.__worker, args=(callback,), daemon=True)
        self.__listening_thread_stop_event = threading.Event()
        self.__recorder = KaldiRecognizer(self.__model, self.__samplerate)
        
        self.__listening_thread.start()
        self.__stream.start()

    def __del__(self):
        self.__listening_thread_stop_event.set()
        self.__stream.close() 

    def __callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.__queue.put(bytes(indata))

    def __worker(self, callback):
        print("[STT] Worker started")
        while not self.__listening_thread_stop_event.is_set():
            data = self.__queue.get()
            if self.__recorder.AcceptWaveform(data):
                result = json.loads(self.__recorder.Result())['text']
                if result.strip():
                    callback(result, True)
            else:
                partial = json.loads(self.__recorder.PartialResult())['partial']
                if partial.strip(): 
                    callback(partial, False)
