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
or on linux and mac do this instead
```
source .venv/bin/activate
pip install -r requirements.txt
```

you will need following following things:
1. OpenAI [api key](https://platform.openai.com/api-keys)
2. Spotify [developer app](https://developer.spotify.com/dashboard)
   
from there you will need:
1. username
2. clientID 
3. clientSecret
4. redirect_url
   
you can follow first steps of [this guide](https://developer.spotify.com/documentation/web-api/tutorials/getting-started) to create app and find those variables

launch `assistant.py`