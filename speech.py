import speech_recognition as sr
from gtts import gTTS
from playsound import playsound


def speech_to_text(time_limit=2):
    # Record Audio
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now")
        audio = r.listen(source, phrase_time_limit=time_limit)

    # Speech recognition using Google Speech Recognition
    try:
        return r.recognize_google(audio)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return 'speech error'
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return 'connection error'


def text_to_speech(text, file_name='./audio/audio.mp3'):
    # Get the audio using google text to speech
    tts = gTTS(text=text, lang='en')
    # Save the audio file
    tts.save('./audio/{}'.format(file_name))

    # Play the audio file
    playsound('./audio/{}'.format(file_name))


def play_file(file_name='audio.mp3'):
    # Play the audio file
    playsound('./audio/{}'.format(file_name))


# text_to_speech("Okay, Let's move to the next question", 'next.mp3')