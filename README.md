## Open source Polish voice assistant
Requierd OpenAI API key to work

### Setup
```
git clone https://github.com/M1chol/atom-assistant
cd atom-assistant
python -m venv .venv
```
then on Windows
```
.\.venv\Scripts\activate
pip install -r .\requirements.txt
```
on linux and mac do this instead
```
source .venv/bin/activate
pip install -r requirements.txt
```

create `openaikey.py` file and add line like this  
```
apiKey = "YOUR-API-KEY"
```

launch `assistant.py`