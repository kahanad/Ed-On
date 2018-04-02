import apiai
import json
import speech
import learning_model
import nao
from tips import tips
import sys


# DialogFloe API key
CLIENT_ACCESS_TOKEN = '8ee5fc28852545958ba95a8bbcb8e1af'


class Dialog:
    def __init__(self):
        # Query for the bot
        self.query = 'Who are you?'
        # The bot's response
        self.response = {'intent': 'pre_session'}
        # Math question
        self.question = None
        # Questions asked in the current session
        self.ques_count = 0
        # Initialize nao
        self.nao = nao.Eddie()
        self.nao.startSession()
        # If we're waiting for an answer
        self.pending_answer = False
        # Question model
        self.model = None
        # Help count
        self.help_count = 0
        # Max number of questions
        self.max_num_of_questions = 3
        # For intro
        self.intro = True
        self.last_intent = None

    def send_to_bot(self, text_query, token=CLIENT_ACCESS_TOKEN, session_id='12345'):
        ai = apiai.ApiAI(token)
        # Create a text request
        request = ai.text_request()
        request.lang = 'en'
        # Session id, unique for each user
        request.session_id = session_id
        # The query
        request.query = text_query

        # Get the bot's response
        self.response = json.loads(request.getresponse().read().decode('utf-8'))
        # Get the message
        response_text = self.response['result']['fulfillment']['speech']
        # Get the intent
        try:
            intent = self.response['result']['metadata']['intentName']
        except KeyError as e:
            intent = 'pre_session'

        # Get the number (answer)
        try:
            number = self.response['result']['parameters']['number'][0]
        except KeyError as e:
            number = -1

        self.response = {'message': response_text, 'intent': intent, 'number': number}

    def record(self, time_limit=2):
        # Play start recording
        speech.play_file('siri_start.mp3')

        self.query = speech.speech_to_text(time_limit=time_limit)

        # If error
        if self.query == 'speech error':
            self.nao.talk({'text': "I didn't quite get that, please repeat"})
            self.record()
        if self.query == 'connection error':
            self.nao.talk({'text': "I'm sorry, the connection is not available right now"})
            sys.exit()

        # Play stop recording
        speech.play_file('siri_end.mp3')

    def handle_answer(self):
        # Record user's answer
        self.record()

        # Send the answer to the bot
        self.send_to_bot(self.query)

        # Check intent
        if self.response['intent'] == 'Help':
            # Get answer
            self.question['answer'] = self.response['number']
            # Get help
            self.help()

        elif self.response['intent'] == 'Answer':
            # Get answer
            self.question['answer'] = self.response['number']

            # Check answer
            self.check_answer()

        elif self.response['intent'] == 'stop':
            # Stop
            self.stop()

    def check_answer(self):
        # If the answer is correct
        if self.question['answer'] == self.question['result']:
            # Nao says good job
            self.send_to_bot('say congrats')
            # System says correct
            speech.play_file('correct.mp3')
            # Display correct screen
            #####
            print('Display correct screen')
            # Nao says good job
            self.nao.talk({'text': self.response['message'], 'gesture': 'happy'})

        else:
            # Nao says wrong answer
            self.send_to_bot('say wronganswer')
            # System says wrong
            speech.play_file('wrong.mp3')
            # Display wrong screen
            #####
            print('Display wrong screen')
            # Get tip and talk
            tip = tips(self.question)
            self.nao.talk({'text': tip, 'gesture': 'explain'})
            # Nao says
            self.nao.talk({'text': self.response['message'], 'gesture': 'explain'})

        # Update Model
        self.question = self.model.flow_2(self.question)

        # No longer pending answer
        self.pending_answer = False

        # Return to event manager
        self.event_manager()

    def event_manager(self):
        print('intent: {}'.format(self.response['intent']))

        """Decide which function to call based on intent"""
        # Small talk
        if self.response['intent'] == 'pre_session':
            self.conversation()

        # If waiting for an answer
        elif self.pending_answer:
            self.handle_answer()

        # First question
        elif self.response['intent'] == 'SessionStart' and self.ques_count == 0:
            # Create Model instance
            self.model = learning_model.Model(user_id='1')

            # First question - open the questions screen with the record button
            #######

            # Initialize first question
            self.question = self.model.flow_1()

            # Ask the question
            self.ask_question()

        # Question
        elif (self.response['intent'] == 'SessionStart' and self.ques_count > 0) or \
                self.response['intent'] == 'wrongAnswer' or self.response['intent'] == 'correctAnswer':

            # Let's move to the next question
            if self.ques_count < self.max_num_of_questions:
                speech.play_file('next.mp3')

            # Ask the question
            self.ask_question()

        # Help
        elif self.response['intent'] == 'Help':
            self.help()

        # Stop
        elif self.response['intent'] == 'stop':
            self.stop()

        elif self.response['intent'] == 'Default Fallback Intent':
            self.record()
            self.event_manager()

    def ask_question(self):
        # Check if need to stop
        if self.ques_count == self.max_num_of_questions:
            self.end_session()

        self.ques_count += 1
        # Display question
        ######
        print(self.question['string'])

        # Speak question
        speech.text_to_speech(self.question['string'], '{}{}{}.mp3'.format(\
            self.question['string'][:4], self.question['num1'], self.question['num2']))

        # Update pending answer
        self.pending_answer = True

        # Return to event manager
        self.event_manager()

    def help(self):
        self.help_count += 1
        if self.help_count <= 2:
            # Speak via nao
            tip = tips(self.question)
            self.nao.talk({'text': tip, 'gesture': 'explain'})
            self.nao.talk({'text': "Okay, now think and try again", 'gesture': 'explain'})

        # Set as wrong answer
        else:
            # Nao speaks
            self.nao.talk({'text': "Let's try another question", 'gesture': 'explain'})

            # Update answer to -1
            self.question['answer'] = -1

            # Update Model
            self.question = self.model.flow_2(self.question)

            # Reset help_count
            self.help_count = 0

        # Return to event manager
        self.event_manager()

    def stop(self):
        # Say goodbye (bot and nao)
        self.nao.talk({'text': self.response['message'], 'gesture': 'happy'})

        # Save data
        if self.model:
            self.model.save_file()

        # kill app
        sys.exit()

    def end_session(self):
        # Save data
        self.model.save_file()
        # Nao says goodbye
        self.nao.talk({'text': 'You did great my friend, hope to see again soon. Bye Bye', 'gesture': 'happy'})
        # exit
        sys.exit()

    def conversation(self):
        # Send the query to thr bot
        self.send_to_bot(self.query)

        # If first meeting
        if self.intro:
            # Nao says response
            self.nao.talk({'text': self.response['message'], 'gesture': 'intro'})
            self.intro = False

        else:
            # Nao says response
            self.nao.talk({'text': self.response['message']})

        # If still in pre_session
        if self.response['intent'] == 'pre_session':
            # Record the user text
            self.record()

        # Return to event_manager
        self.event_manager()


if __name__ == '__main__':
    d = Dialog()
    while True:
        x = raw_input("input:")
        if x == 's':
            d.event_manager()
        elif x == 'r':
            d.record()
