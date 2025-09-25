# Python Speech-to-Speech Assistant

This repo contains a ready to use speech-to-speech assistant designed to run on edge devices like the `Jetson Nano`. It uses `ollama` in combination with `vosk` and `piper` to achieve real-time conversational capabilities with minimal system requirements.

## Installation

1.  Install `ollama` - https://ollama.com/download

2.  Install `jq` (can be skipped - needed only for running `./install.sh`).
  
    For Debian-based systems:
    ```bash
    sudo apt-get install jq
    ```

3.  Clone the repository:
    ```bash
    git clone https://github.com/M1chol/atom-assistant
    cd atom-assistant
    ```

4.  You then need to manually install all the [ollama models](https://ollama.com/search) you want to use:
    ```bash
    ollama serve
    ollama run <MODEL_NAME>
    ```

5.  Update `config.json` with your values. You need to change:
    -   `ollama_model_name` to match a model available in your `ollama` server.
    -   LLM system prompt to match your language and requirements (`ollama_system_prompt`).
    -   Microphone sample rate to match your hardware (`stt_config/microphone_samplerate`).
    -   Speech-to-text [vosk model](https://alphacephei.com/vosk/models) to match your language (`stt_config/model`).
    -   Text-to-speech [piper model](https://rhasspy.github.io/piper-samples/) to match your language (`tts_config/model`).

6.  Run the install script:
    ```bash
    ./install.sh
    ```

## Running

After running the install script, execute:
```bash
python main.py
```
If the script fails to activate the Python environment (could happen in non-desktop environments), do it manually:
```bash
source .venv/bin/activate
python main.py
```

## Tweaking Default `config.json` Values

In `config.json`, you can change the reading speed. If your LLM is not fast enough and is blocking speech generation, you can **increase** the `tts_config/length_scale` to slow down the reading speed.

`noise_scale` and `noise_w_scale` control respectivly **audio** and **speaking** variation. You can also change the `volume` of the output speech.

## Singular use examples
I have also included example files for educational puposes for the used `ollama`, `piper` and `vosk` libraries. They all in some way expand on simple examples provided by the library contributors.