
def setup():
    try:
        with open("mysecrets.py", "r") as file:
            if file.readline() != "":
                if input("Setup file found, would you like to change it? y/N: ").lower() != 'y':
                    return True
    except FileNotFoundError:
        print("No setup file found, creating new one...")
    with open("mysecrets.py", "w") as file:
        print("If you want to skip some services leave their secrets blank\nIf you are not sure how to get those api keys refer to README\n")
        print("openaiKey =", '"' + input("provide OpenAI key: ") + '"', file=file)
        print("spotify_username =", '"' + input("provide Spotify username: ") + '"', file=file)
        print("spotify_clientID = ", '"' + input("provide Spotify clientID: ") + '"', file=file)
        print("spotify_clientSecret = ", '"' + input("provide Spotify clientSecret: ") + '"', file=file)
        print("spotify_redirect_url = ", '"' + input("provide Spotify redirect url: ") + '"', file=file)
        print("Setup complete!")
        return True
    
if __name__ == "__main__":
    setup()



