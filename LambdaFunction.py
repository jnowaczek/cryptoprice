import requests
import json
import traceback
import os


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    print("Output speech: " + output)
    print("Reprompt: " + reprompt_text)
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
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


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome to Crypto Price"
    speech_output = "You can retrieve current cryptocurrency spot prices from Coinbase by asking, what is the current Bitcoin price? You may indicate a different cryptocurrency or fiat currency."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You may request current cryptocurrency spot prices from Coinbase by asking, what is the current Bitcoin price?"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Thanks for using Crypto Price!"
    speech_output = "Cancelling price lookup."
    reprompt_text = ""
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_price(intent, session):
    card_title = "Price Lookup"
    session_attributes = {}
    reprompt_text = ""
    speech_output = None
    should_end_session = True
    
    print(intent['slots'])
    
    fiat_currency_name_to_symbol = {'dollars': 'usd', 'euros': 'eur', 'eur': 'eur', 'pounds': 'gbp', 'pounds stirling': 'gbp', 'gbp': 'gbp', 'US dollars': 'usd', 'usd': 'usd'}
    cryptocurrency_name_to_symbol = {'bitcoin': 'btc', 'btc': 'btc', 'ethereum': 'eth', 'ether': 'eth', 'eth': 'eth', 'litecoin': 'ltc', 'ltc': 'ltc'}
                                    
    fiat_currency_symbol_to_name = {'usd': 'dollars', 'eur': 'euros', 'gbp': 'pounds'}
    cryptocurrency_symbol_to_name = {'btc': 'bitcoin', 'eth': 'ether', 'ltc': 'litecoin'}
    
    if 'value' in intent['slots']['cryptocurrency']:
        if not intent['slots']['cryptocurrency']['value'].lower() in cryptocurrency_name_to_symbol:
            speech_output = "Sorry, I don't recognize that cryptocurrency. Please try again."
            reprompt_text = "Please specify bitcoin, litecoin, or ether. If not specified the default is bitcoin."
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
        crypto_symbol = cryptocurrency_name_to_symbol[intent['slots']['cryptocurrency']['value'].lower()]
    else:
        crypto_symbol = 'btc'
        
    if 'value' in intent['slots']['fiat_currency']:
        if not intent['slots']['fiat_currency']['value'].lower() in fiat_currency_name_to_symbol:
            speech_output = "Sorry, I don't recognize that currency. Please try again."
            reprompt_text = "Please specify either US dollars, british pounds, or euros. The default is US dollars."
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
        fiat_symbol = fiat_currency_name_to_symbol[intent['slots']['fiat_currency']['value'].lower()]
    else:
        fiat_symbol = 'usd'

    try:
        price = lookup_price(crypto_symbol, fiat_symbol)

        speech_output = "The current spot price for " + cryptocurrency_symbol_to_name[crypto_symbol] + " is " + price + " " + fiat_symbol.upper() + "."
    except Exception as e:
        if isinstance(e, requests.exceptions.Timeout):
            speech_output = "Coinbase did not respond with price data in time, please try again."
            reprompt_text = "Please repeat your request. If you continue to experience errors, try again later."
        elif isinstance(e, ValueError):
            speech_output = "An error occurred: " + str(e)
            reprompt_text = "Please repeat your request. If you continue to experience errors, try again later."
        
        should_end_session = False
        traceback.print_exc()
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def lookup_price(cryptocurrency, fiat_currency):
    request_url = "https://api.coinbase.com/v2/prices/" + cryptocurrency + "-" + fiat_currency + "/spot"
    headers = {"CB-VERSION": "2015-05-12"}
    
    print("Attempting to fetch price data from " + request_url)

    response = requests.get(request_url, headers=headers, timeout=1.5).text
        
    json_object = json.loads(response)
    
    if 'errors' in json_object:
        for error in json_object['errors']:
            raise ValueError(error['message'])
    
    price = json_object['data']['amount']

    print("Obtained price data for " + cryptocurrency + " to " + fiat_currency + ": " + price)

    return price


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetPriceIntent":
        return get_price(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] != os.environ['applicationID']):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
