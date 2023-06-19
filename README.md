# Auto Meme Voice Player (for OBS - Open Broadcaster Software)

> THIS IS A BETA VERSION, SOMETIMES THE MEDIA SOURCE MAY NOT PLAY DUE TO VOICE RECOGNITION INCONSTENCE

A Python script for OBS (Open Broadcaster Software) that plays a video media source according the configuration file through voice recognition.

## Setup

1. Create a file with the extension `.json` and follow the structure of the [sample file](https://github.com/Niemietz/Auto-Meme-Voice-Player/blob/master/config_sample/AutoMemeConfig.json)

2. Install the `speech_recognition` requirement in which the script needs by opening the terminal, going to the folder where the script is located and running the command `pip install speech_recognition`

3. Open **Scripts** window from Tools (T) -> Script and click at **Python Configuration** tab and set the location of Python installed on your machine

<img width="740" alt="image" src="https://github.com/Niemietz/Auto-Meme-Voice-Player/assets/8949271/0d398233-1b7f-4a04-b047-abccf7b9fbb4">

4. Go back to **Scripts** tab and include the python script by clicking at the + sign

<img width="739" alt="image" src="https://github.com/Niemietz/Auto-Meme-Voice-Player/assets/8949271/668d9ebf-7c4e-46ea-9301-3d945ed290cb">

5. Set the script configurations as you wish. Check out each configuration description:

| Configuration                        | Description                                                                                                                                                                                     |
|--------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Voice Recognition Language           | Set the language of the voice to be recognized                                                                                                                                                  |
| Configuration File                   | Configuration file in JSON format (Only files named AutoMemeConfig.json is accepted)                                                                                                            |
| Time in seconds to wait for phrase   | Time to listen the phrase before checking if a video/meme should be played or not.<br/>If the time is longer then processing time (delay) to find a video/meme and play it will also be longer  |
| OBS Web Socket Hostname              | Hostname of the web socket of you OBS client                                                                                                                                                    |
| OBS Web Socket Port                  | Port of the web socket of you OBS client                                                                                                                                                        |
| Debug                                | Allow logging on the events of the script (Ignore this if you don't know about it)                                                                                                              |
