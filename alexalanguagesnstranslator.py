"""

"""

from __future__ import print_function
import botocore
import boto3
import json
from botocore.vendored import requests


# --------------- Helpers that build all of the responses ----------------------

#current_message = ""


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet hello - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    
    

def translate_message(intent, session):
    
 
    session_attributes = {}
    
    # Get the value of the Name slot
    message = intent['slots']['message']['value']
    
    session.get('attributes', {})
    
    name = session['attributes']['personName']
    
    language = session['attributes']['languageChoice']
    
    name = name.lower()
    language = language.lower()
    
    languageKey = determineLanguageKey(language)
    number = determineNumber(name)
    
    if (name == "no name found"):
        speech_output = "Sorry, no name was found for the one you said."
        should_end_session = True
    if (language == "no language found"):
        speech_output = "Sorry, I don't recognize that language."
        should_end_session = True
    
    
    translate = boto3.client('translate')
    result = translate.translate_text(Text=message,
                                  SourceLanguageCode="en",
                                  TargetLanguageCode=languageKey)
    
    current_message = f' {result["TranslatedText"]}'
        
    if (languageKey == "no"):
        speech_output = "Sorry, I don't recognize that language"
    elif (number == "0"):
        speech_output = "Sorry, I don't recognize that name"
    else:
        sns = boto3.client('sns')
       
        #Send a SMS message to the specified phone number
        response = sns.publish(
            PhoneNumber= number,
            Message= current_message,  
        )
        
        speech_output = "Okay, I sent a message to " + name + " in " + language
    
    card_title = "MessageSender"

    should_end_session = True
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

        

def store_message_in_attributes(current_message):
    return {"currentMessage": current_message}

        
def gather_message_parts(intent, session):
    name = intent['slots']['name']['value']
    language = intent['slots']['language']['value']
    session_attributes = {}
    session_attributes = store_contact_in_attributes(name, language)

    speech_output = "Okay, what would you like to send and translate?"
    
    card_title = "GatherMessage"
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
        
def store_contact_in_attributes(name, language):
    return {"personName": name, 
            "languageChoice": language
            }

def determineNumber(name):
    if name == "joey":
        return "+111111111"
    elif name == "meg":
        return "+555555555"
    elif name == "dave":
        return "+333333333"
    else:
        return "0"
        
def determineLanguageKey(language):
    if language == "italian":
        return "it"
    elif language == "german":
        return "de"
    elif language == "japanese":
        return "ja"
    elif language == "chinese":
        return "zh"
    elif language == "arabic":
        return "ar"
    elif language == "finnish":
        return "fi"
    elif language == "french":
        return "fr"
    elif language == "korean":
        return "ko"
    elif language == "spanish":
        return "es"
    elif language == "swedish":
        return "sv"
    elif language == "turkish":
        return "tr"
    elif language == "russian":
        return "ru"
    else:
        return "no"
        
def send_message(number, current_message, name, languageKey, session):
    
    
    session_attributes = {}
    
    print("Inside send_message")
    print(number)
    print(languageKey)
    print(name)
    
    
    if (languageKey == "no"):
        speech_output = "Sorry, I don't recognize that language"
    elif (number == "0"):
        speech_output = "Sorry, I don't recognize that name"
    else:
        sns = boto3.client('sns')
       
        #Send a SMS message to the specified phone number
        response = sns.publish(
            PhoneNumber= number,
            Message= current_message,  
        )
        
        speech_output = "Okay"
    
    card_title = "MessageSender"

    should_end_session = True
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

        

        
    

 
        

    
    




   
        

        
 



    
    
    
    

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    #if session.get('attributes', {}) and "current_Message" not in session.get('attributes', {}):
       # current_Message = intent['slots']['message']['value']
       # session_attributes = create_Message_Attribute(current_Message)
    
    card_title = "Welcome"
    speech_output = "Welcome to the Joey. " \
    "Please tell me the name of the person you want to send a message to, and the language you want it to be in."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me the name of a person and a language."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Joey skill. " \
    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
        

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
                       
    if intent_name == "TranslateMessage":
        return translate_message(intent, session)
    elif intent_name == "SendMessage":
        return gather_message_parts(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
       # event['session']['attributes'] = {}
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

