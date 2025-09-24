echo "Checking dependencies..."
if ! command -v ollama > /dev/null 2>&1; then
    echo "Failed, Please check that Ollama is installed. https://ollama.com/download"
    exit 1
fi
if ! command -v jq > /dev/null 2>&1; then
    echo "Failed, Please check that jq is installed."
    exit 1
fi
if [ ! -d ".venv" ]; then
    echo "Creating virtual enviroment..."
    python3 -m venv .venv
fi

echo "Activating virtual enviroment..."
source .venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Downloading Piper voice..."
model=$(cat config.json | jq -r '.tts_model')
dir=$(cat config.json | jq -r '.tts_model_dir')
mkdir 
python3 -m piper.download_voices $model --download-dir $dir

echo "Installation complete!"