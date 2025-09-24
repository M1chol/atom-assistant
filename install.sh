echo "Checking ollama status..."
if command -v ollama > /dev/null 2>&1; then
    echo "Ollama is installed"
else
    echo "Failed, Please check that Ollama is installed. https://ollama.com/download"
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
mkdir models
python3 -m piper.download_voices pl_PL-darkman-medium --download-dir ./models

echo "Installation complete!"