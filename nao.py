
from naoqi import ALProxy
import sys
import almath
import json
import time
import argparse

import nao_alproxy

class Eddie(nao_alproxy.NaoALProxy):
    def __init__(self):
        nao_alproxy.NaoALProxy.__init__(self)

    def startSession(self):
        self.wake_up()
        try:
            self.autonomous.setState("solitary")
        except:
            return

        #self.face_tracker()

    def talk(self, message):
        '''
        :param message: Dict. ["text"]: a string - the robot's text, ["emotion"] - the wanted behavior - animation.
        '''
        try:
            text = [message["text"]]
        except:
            print "There is no text in the message."
            return

        try:
            gesture = message["gesture"]
        except:
            self.animated_text_to_speech([message["text"]])
            return

        if message["gesture"] == "normal":
            self.animated_text_to_speech([message["text"]])

        elif message["gesture"] == "happy":
            self.do_animation(message["gesture"], "wait")
            self.say_text_to_speech_post([message["text"]], "wait")

        elif message["gesture"] == "thinking":
            self.do_animation(message["gesture"])
            self.say_text_to_speech([message["text"]])

        elif message["gesture"] == "explain":
            self.say_text_to_speech_post([message["text"]], "wait")
            self.do_animation(message["gesture"], "wait")

        elif message["gesture"] == "intro":
            self.intro_behavior([message["text"]])

    def intro_behavior(self, text):
        self.animated_text_to_speech([text], "wait")
        # self.run_behavior(["animations/Stand/Gestures/Hey_4"])
        # self.run_behavior(["animations/Stand/Gestures/Me_2"])
        # self.say_text_to_speech(text)





        #self.do_animation("explain")

    def endSession(self):
        self.autonomous.setState("disabled")

#
# message_normal = {"text" : "This is a testing text. This is a normal conversation",
#            "gesture" : "normal"}
#
#
# message_happy = {"text": "I am so happy now!",
#                  "gesture": "happy"}
#
# message_thinking = {"text": "I have to think about it",
#                     "gesture": "thinking"}
#
# message_none = {"text": "This is a text without gesture"}
#
# message_explain = {"text": ["I have a lot to explain", "it will take me several hours", "I just love talking"],
#                     "gesture": "explain"}
#
#
#
# eddie1 = Eddie()
# #
# eddie1.talk({"text": "hello, I am Eddie. Nice to meet you! Let's learn together!. I want to speak for a long time in order to check if I stop the code or not.", "gesture":"intro"})
#
# print "hi!"
#
#
