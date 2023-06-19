import speech_recognition as sr
import keyboard
import asyncio
import threading
import traceback
import sys
import enum
import random
from obswebsocket import obsws, requests, events
import obspython as obs
import json

class DEBUG_TYPE(enum.Enum):
    DISABLE_DEBUG = 0
    ENABLE_DEBUG = 1
    ENABLE_FULL_DEBUG = 2

    @classmethod
    def from_value(cls, value: int):
        return next((m_value for m_value in list(cls) if m_value.value == value), None)

class AutoVoiceMemeGenerator(object):
    seconds_to_listen_phrase: int = 3
    memes_keywords: list = []
    voice_language: str = "pt-BR"
    ws_host: str = "localhost"  # OBS WebSocket host address
    ws_port: int = 4444  # OBS WebSocket server port
    debug: DEBUG_TYPE = DEBUG_TYPE.DISABLE_DEBUG
    cancel: bool = False

    __KEYWORDS_KEY_FROM_CONFIG: str = "keywords"
    __MEMES_KEY_FROM_CONFIG: str = "memes"
    __SOURCE_KEY_FROM_CONFIG: str = "source"

    __LOCAL_FILE_KEY_FROM_SOURCE_SETTINGS: str = "local_file"
    __NAME_KEY_FROM_SOURCE_SETTINGS: str = "name"
    __FILE_KEY_FROM_SOURCE_SETTINGS: str = "file"

    def __init__(self):
        self.start()

    def start(self):
        if len(self.memes_keywords) > 0 and len(self.ws_host) > 0 and len(self.voice_language) > 0 and (self.seconds_to_listen_phrase >= 3 and self.seconds_to_listen_phrase <= 10):
            thread = threading.Thread(target=self.__run_async_function)
            thread.start()

    def __run_async_function(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__recognize_voice())
        loop.close()

    def __format_exception(self, e):
        exception_list = traceback.format_stack()
        exception_list = exception_list[:-2]
        exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
        exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

        exception_str = "Traceback (most recent call last):\n"
        exception_str += "".join(exception_list)
        # Removing the last \n
        exception_str = exception_str[:-1]

        return exception_str

    async def __recognize_voice(self):    
        microfone = sr.Recognizer()
        with sr.Microphone() as mic_source:        
            microfone.adjust_for_ambient_noise(mic_source)

            web_socket = obsws(self.ws_host, self.ws_port)
            web_socket.connect()

            if self.debug != DEBUG_TYPE.DISABLE_DEBUG:
                print("Say something!")
            while self.cancel == False:
                try:
                    audio = microfone.listen(mic_source, self.seconds_to_listen_phrase, self.seconds_to_listen_phrase)
                    phrase = microfone.recognize_google(audio,language=self.voice_language)
                    if self.debug != DEBUG_TYPE.DISABLE_DEBUG:
                        print("You said: " + phrase)

                    keyword_meme = next((m_keywords_memes for m_keywords_memes in self.memes_keywords if next((m_keyword_meme for m_keyword_meme in m_keywords_memes[self.__KEYWORDS_KEY_FROM_CONFIG] if str.upper(phrase).__contains__(str.upper(m_keyword_meme))), None) != None), None)
                    if keyword_meme != None:
                        self.__call_meme_from_keyword(web_socket, keyword_meme)
                except Exception as e: 
                    if self.debug == DEBUG_TYPE.ENABLE_FULL_DEBUG:
                        #print(self.__format_exception(e))
                        print("It didn't get what you said!")
                    else:
                        pass
            web_socket.disconnect()

    def __call_meme_from_keyword(self, web_socket: obsws, keyword_meme: list):
         if self.debug != DEBUG_TYPE.DISABLE_DEBUG:
            print("Call the MEME!!")

         current_scene = web_socket.call(requests.GetCurrentScene())

         random_meme = keyword_meme[self.__MEMES_KEY_FROM_CONFIG][random.randint(0, len(keyword_meme[self.__MEMES_KEY_FROM_CONFIG]) - 1)]
         source_name = random_meme[self.__SOURCE_KEY_FROM_CONFIG]

         source = next((m_source for m_source in current_scene.getSources() if m_source[self.__NAME_KEY_FROM_SOURCE_SETTINGS] == source_name), None)
         if source != None:
            web_socket.call(requests.SetSceneItemProperties(item=source[self.__NAME_KEY_FROM_SOURCE_SETTINGS], visible=False))

            settings_response = web_socket.call(requests.GetSourceSettings(sourceName=source[self.__NAME_KEY_FROM_SOURCE_SETTINGS]))

            if settings_response.status:
                media_settings = settings_response.getSourceSettings()
                media_settings[self.__LOCAL_FILE_KEY_FROM_SOURCE_SETTINGS] = random_meme[self.__FILE_KEY_FROM_SOURCE_SETTINGS]

                web_socket.call(requests.SetSourceSettings(sourceName=source[self.__NAME_KEY_FROM_SOURCE_SETTINGS], sourceSettings=media_settings))
                web_socket.call(requests.SetSceneItemProperties(item=source[self.__NAME_KEY_FROM_SOURCE_SETTINGS], visible=True))
            else:
                if self.debug != DEBUG_TYPE.DISABLE_DEBUG:
                    print("Media source not found.")
         else:
            if self.debug != DEBUG_TYPE.DISABLE_DEBUG:
                print("Media source not found.")

# ------------------------------------------------------------

__instanced_main_class: AutoVoiceMemeGenerator = None
__debug: DEBUG_TYPE = DEBUG_TYPE.DISABLE_DEBUG

def script_properties():
	props = obs.obs_properties_create()
	voice_language_list = obs.obs_properties_add_list(props, "voiceLanguage", "Voice Recognition Language", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)

	obs.obs_property_list_add_string(voice_language_list, "Português (Brasil)", "pt-BR")
	obs.obs_property_list_add_string(voice_language_list, "Português (Portugal)", "pt-PT")
	obs.obs_property_list_add_string(voice_language_list, "English (United States)", "en-US")
	obs.obs_property_list_add_string(voice_language_list, "English (England)", "en-EN")

	obs.obs_properties_add_path(props, "configFile", "Configuration File", obs.OBS_PATH_FILE, "AutoMemeConfig.json", "")
	obs.obs_properties_add_int_slider(props, "seconds2ListenPhrase", "Time in seconds to wait for phrase\n(It may cause a delay if its too high)", 3, 10, 1)
	obs.obs_properties_add_text(props, "host", "OBS WebSocket Hostname", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_int(props, "port", "OBS WebSocket Port", 1, 99999, 1)
        
	debug_list = obs.obs_properties_add_list(props, "debug", "Debug", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_INT)

	obs.obs_property_list_add_int(debug_list, "Disabled", 0)
	obs.obs_property_list_add_int(debug_list, "Enabled", 1)
	obs.obs_property_list_add_int(debug_list, "Enabled (Full)", 2)

	return props

def script_description():
    sb: str = "It plays a video media source with a MEME according the configuration file through voice recognition.\n\n"
    
    sb += "**IMPORTANT NOTE**\n"
    sb += "This is a beta version, so it may not play the MEME sometimes.\n\n"

    sb += "By Renan Niemietz Cardoso"

    return sb

def script_defaults(settings):
	obs.obs_data_set_default_string(settings, "voiceLanguage", "pt-BR")
	obs.obs_data_set_default_int(settings, "seconds2ListenPhrase", 3)
	obs.obs_data_set_default_int(settings, "debug", 0)
	obs.obs_data_set_default_string(settings, "host", "localhost")
	obs.obs_data_set_default_int(settings, "port", 4444)

def script_update(settings):
	global __instanced_main_class

	json_config = []
	voice_language = obs.obs_data_get_string(settings, "voiceLanguage")
	config_file = obs.obs_data_get_string(settings, "configFile")
	seconds_2_listen_phrase = obs.obs_data_get_int(settings, "seconds2ListenPhrase")
	port = obs.obs_data_get_int(settings, "port")
	host = obs.obs_data_get_string(settings, "host")
	debug = DEBUG_TYPE.from_value(obs.obs_data_get_int(settings, "debug"))

	if len(config_file) > 0 and __instanced_main_class != None:
		with open(config_file, 'r', encoding='utf-8') as json_file:
			json_config = json.load(json_file)

		__instanced_main_class.memes_keywords = json_config
		__instanced_main_class.seconds_to_listen_phrase = seconds_2_listen_phrase
		__instanced_main_class.voice_language = voice_language
		__instanced_main_class.ws_host = host
		__instanced_main_class.ws_port = port
		__instanced_main_class.debug = debug
		__instanced_main_class.start()

def __on_key_press(event):
    if str.upper(event.name) == "O":
        if __debug != DEBUG_TYPE.DISABLE_DEBUG:
            print("Finishing...")
        __instanced_main_class.cancel = True

keyboard.on_press(__on_key_press)
__instanced_main_class = AutoVoiceMemeGenerator()