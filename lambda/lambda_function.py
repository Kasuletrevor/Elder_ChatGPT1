# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import requests
import json
from datetime import datetime
from neo4j import GraphDatabase

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

URI = "neo4j+s://029008c7.databases.neo4j.io"
AUTH = ("neo4j", "kbr-5jhXp9wLUsNYZc-c8NYwZCloS4ZJxen44amvnHU")
family_circle_api = "https://kk-family-circle.herokuapp.com/api/getmessages/Victoria.Poller@kin-keepers.ai/bcde2345"

#from ask_sdk_core.dispatch_components import AbstractRequestHandler

from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello welcome to your family news. \
        what would you like to do?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


# ----------------------------------------------------------------------------------FAMILY NEWS INTENT HANDLERS---------------------------------------------------------------------------------------
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model import Response
from ask_sdk_model.interfaces.audioplayer import PlayDirective, PlayBehavior, AudioItem, Stream


# def convert_to_mp3(input_url):
#     response = requests.get(input_url)
#     audio = AudioSegment.from_file(io.BytesIO(response.content))
#     output_file = io.BytesIO()
#     audio.export(output_file, format='mp3')
#     output_file.seek(0)
#     return output_file

class FamilyNewsIntentHandler(AbstractRequestHandler):
    """Handler for Family News Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name('FamilyNewsIntent')(handler_input)


    def handle(self, handler_input):
        #audio_url = "https://res.cloudinary.com/degr4sxew/video/upload/v1685693206/mjufmhfjd3dxhg5jdws1_akoqhm.mp3"
        #audio_url = 'https://res.cloudinary.com/degr4sxew/video/upload/v1668678965/kin-keepers/mjufmhfjd3dxhg5jdws1.ogg'
        #audio_url = 'https://res.cloudinary.com/kin-keepers-com/video/upload/v1657310028/audio/Victoria.Poller__Victoria.Poller__1657309994641__bcde2345.mp3'
        response = requests.get(family_circle_api)
        data = response.json()
        url = data[0]['url']
        audio_url = url.rsplit(".webm",1)[0]+".mp3"
        
        
        response_builder = handler_input.response_builder
        response_builder.add_directive(
            PlayDirective(
                play_behavior=PlayBehavior.REPLACE_ALL,
                audio_item=AudioItem(
                    stream=Stream(
                        token="pyv-p8",
                        url=audio_url,
                        offset_in_milliseconds=0,
                        expected_previous_token=None
                    )
                )
            )
        )
        #response_builder.set_should_end_session(False)

        return response_builder.response

class LastNameIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LastNameIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Extract the value of the "lastname" slot from the user input
        name = handler_input.request_envelope.request.intent.slots["lastname"].value

        if name:
            name = name.capitalize()
            url = "https://kin-keepers-neo4j.herokuapp.com/api/returnOneVariable"
            cypher_query = "MATCH (p) WHERE p.lastName = $param1  RETURN p"
            json_args = json.dumps({"param1": name})
            result = custom_query(url, cypher_query, json_args)

            # If a value was extracted, capitalize the name and query a Neo4j database for people with that last name
            names = []
            for i in result:
                names.append(i['firstName'])

            # # get user' first name and remove from list
            # user_firstName = user.split()[0].capitalize()
            # if user_firstName in names:
            #     names.remove(user_firstName)
            # else:
            #     pass
            if len(names) > 1:
                names.insert(-1, 'and')
                speak_output = f"The following people share the last name {name}.  {','.join(names)}"
            elif len(names) == 1:
                speak_output = f"{names[0]} is the only person that has last name {name} last name."
            else:
                speak_output = f"Sorry, I did not find anyone with the last name {name}"

                speak_output = f"Sorry I don't have anyone registered with the last name {name} "

        # If no value was extracted, assume the user wants to know about people with the same last name as them
        else:
            speak_output = "Please do provide a last name"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class GetGrandParentsIntentHandler(AbstractRequestHandler):
    """Handler for GrandParentIntent Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetGrandParentsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # obtain person from slot
        person = handler_input.request_envelope.request.intent.slots["person"].value

        if person:

            # format the person string

            person = " ".join([name.capitalize() for name in person.split()])
            email_format = (
                ".".join([name.capitalize()
                          for name in person.split()]) + "@kin-keepers.ai"
            )

            url = "https://kin-keepers-neo4j.herokuapp.com/api/myGrandparents"
            url_p = f"{url}/{email_format}"

            # Call the custom_query function with the parameters
            result = requests.get(url_p)
            data = result.json()
            # print(data)
            granny = []
            for i in data:
                granny.append(i["firstName"] + " " + i["lastName"])
            # granny.insert(-1, "and")
            if granny:
                granny.insert(-1, 'and')
                speak_output = f"Grand parents for {person} are: {','.join(granny)}"
            else:
                speak_output = f"Sorry, I do not have grand parents registered for {person}"

        # using the username
        else:
            speak_output = f"I didn't get well, whose grand parents are you looking for"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class GetGrandChildrenIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetGrandChildrenIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        person = handler_input.request_envelope.request.intent.slots["person"].value
        url = "https://kin-keepers-neo4j.herokuapp.com/api/myGrandchildren"
        if person:
            # format the person string
            person = " ".join([name.capitalize() for name in person.split()])
            email_format = (
                ".".join([name.capitalize()
                          for name in person.split()]) + "@kin-keepers.ai"
            )
            url_p = f"{url}/{email_format}"
            # Call the custom_query function with the parameters
            result = requests.get(url_p)
            data = result.json()
            # print(data)
            grand_children = []
            for i in data:
                grand_children.append(i["firstName"] + " " + i["lastName"])
            # granny.insert(-1, "and")
            if grand_children:
                if len(grand_children) == 1:
                    speak_output = f"{grand_children[0]} is the only grand child of {person}"
                else:
                    grand_children.insert(-1, 'and')
                    speak_output = f"The following are the grand children of {person}: {','.join(grand_children)}"
            else:
                speak_output = f"Sorry, there are no grand children registered for {person}"

        # using the username
        else:
            speak_output = f"Hmm, whose grand children are you looking for"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class GetAgeIntentHandler(AbstractRequestHandler):
    """Handler for GrandParentIntent Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetAgeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        url = "https://kin-keepers-neo4j.herokuapp.com/api/returnOneVariable"

        # obtain slot values
        slots = handler_input.request_envelope.request.intent.slots
        person = slots["person"].value

        if person:
            # obtain first and last name from full name
            first_name, last_name = person.split()

            # construct query to retrieve person
            cypher_query = "MATCH (p) WHERE p.firstName = $param1 AND p.lastName = $param2 RETURN p"
            json_args = json.dumps(
                {'param1': first_name.capitalize(), 'param2': last_name.capitalize()})
            results = custom_query(url, cypher_query, json_args)

            # obtain  date of birth from result. The output is dict in a list for example
            # [{ .....'firstName': 'Sarah', 'lastName': 'Burns', 'DOB': '5-20-1925',....}]
            dob = results[0]['DOB']

            dob = datetime.strptime(dob, '%m-%d-%Y')
            today_date = datetime.today()
            age = today_date.year - dob.year

            # Birthday has not reached remove one year else do nothing
            if dob.month >= today_date.month & dob.day >= today_date.day:
                pass
            else:
                age = age - 1

            speak_output = f'{person} is currently {age} years old'

        else:
            speak_output = f'Sorry I could not find {person} in the database'

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


# --------------------------------------------------------------------------------------21-QUESTIONS INTENT HANDLERS--------------------------------------------------------------------------------------------


class CaptureQuestionIntentHandler(AbstractRequestHandler):
    """Handler for CaptureQuestionIntent"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_intent_name("CaptureQuestionIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        question = handler_input.request_envelope.request.intent.slots["question"].value
        attributes_manager = handler_input.attributes_manager
        session_attributes = attributes_manager.session_attributes
        session_attributes["current_question"] = question
        session_attributes["user_question"] = question
        session_attributes["object"] = None
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            with driver.session(database="neo4j") as session:
                result = session.run(
                    """
                    MATCH (q:Question {text:$question})-[:HAS_ANSWER]->(a:Answer)
                    RETURN q.timestamp AS timestamp, a
                    """,
                    question=question,
                )
                # Retrieves first (and only) record from result
                record = result.single()
                if record is not None:
                    # The answer is the second item, from the return defined above.
                    answer = record[1]["object"].lower()
                    speak_output = f"Are you looking for {answer}?"
                    session_attributes['current_question'] = f'{answer}_likely'
                else:
                    # Redirect to Play21QuestionsIntentHandler
                    speak_output = "We have captured new question, Yes to continue"
                    session_attributes["current_question"] = "start"
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Play21QuestionsIntentHandler(AbstractRequestHandler):
    """Handler for playing 21-questions to figure out what Elder is looking for"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            or ask_utils.is_intent_name("AMAZON.YesIntent")
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attributes_manager = handler_input.attributes_manager
        session_attributes = attributes_manager.session_attributes
        current_question = session_attributes.get("current_question")

        speak_output = None

        if current_question == 'start':
            # Ask the first question to start the game
            speak_output = "Is it something electronic?"
            session_attributes["current_question"] = 'electronic_filter'

        elif current_question == 'electronic_filter':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "Does it have batteries?"
                session_attributes["current_question"] = 'electronic_items'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Is it made of leather or fabric?"
                session_attributes["current_question"] = 'non_electronic_items'

        # ----------electronic items-----------------------------------------
        elif current_question == 'electronic_items':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "Is it typically used indoors?"
                session_attributes["current_question"] = 'battery_device'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Does it have a screen to it?"
                session_attributes["current_question"] = 'not_battery_device'

        elif current_question == 'battery_device':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "I have an idea of what you are looking for. Are you looking for the TV remote?"
                session_attributes["current_question"] = 'tv remote_likely'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Could not find what you looking for"
                session_attributes["current_question"] = 'not_found'

        elif current_question == 'not_battery_device':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "I think I have figured out what you looking for. Are you looking for your smartphone?"
                session_attributes["current_question"] = 'smartphone_likely'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Sorry, I could not find item you looking for"
                session_attributes["current_question"] = 'not_found'

    # ------------------------non electronic items-----------------------------------------
        elif current_question == 'non_electronic_items':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "Does it have straps for handling?"
                session_attributes["current_question"] = 'fabric_items'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Is it a personal item?"
                session_attributes["current_question"] = 'not_fabric'  # *****

        elif current_question == 'fabric_items':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "Does it have zips"
                session_attributes["current_question"] = 'has_straps'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Do you wear it on your foot"
                session_attributes["current_question"] = 'no_straps'

        elif current_question == 'has_straps':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "I have an idea of what you looking for. Are you looking for bag?"
                session_attributes["current_question"] = 'bag_likely'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "No item for this category currently"
                session_attributes["current_question"] = 'not_found'

        elif current_question == 'no_straps':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "I think I have an idea of what you looking for. Are you looking for your shoes?"
                session_attributes["current_question"] = 'shoes_likely'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "No item for this category currently"
                session_attributes["current_question"] = 'not_found'

        elif current_question == 'not_eye_glasses':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "Think i have figured out what you looking for. Are you looking for your Bag?"
                session_attributes["current_question"] = 'bag_likely'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Could not clearly figure out"
                session_attributes["current_question"] = 'not_found'

        elif current_question == 'not_accessory':
            if ask_utils.intent_name('AMAZON.YesIntent')(handler_input):
                speak_output = 'Is it made of fabric?'
                session_attributes['current_question'] = 'personal_items'
            elif ask_utils.intent_name('AMAZON.NoIntent')(handler_input):
                speak_output = 'No items in this category currently'
                session_attributes['current_question'] = 'not_found'

        elif current_question == 'not_fabric':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "Is it something that helps you see clearly?"
                session_attributes["current_question"] = 'personal_items'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "category not available"
                session_attributes["current_question"] = 'not_found'

        elif current_question == 'personal_items':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "I have an idea, Are you looking for your eye glasses"
                session_attributes["current_question"] = 'eye glasses_likely'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Is it something metalic?"
                session_attributes["current_question"] = 'metalic_items'

        elif current_question == 'metalic_items':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "Is it something that helps you access other places"
                session_attributes["current_question"] = 'access_places'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "category not available"
                session_attributes["current_question"] = 'not_found'

        elif current_question == 'access_places':
            # If the answer to the first question is yes, ask the next question
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = "I have an idea, are you looking for your house keys"
                session_attributes["current_question"] = 'keys_likely'
            # If the answer is no, ask a different question
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "category not available"
                session_attributes["current_question"] = 'not_found'

        # ------------------------- shoes have been found -----------------------------------------------------------------

        elif current_question == "shoes_likely":
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                session_attributes["object"] = "Shoes"
                question = session_attributes["user_question"]
                answer = session_attributes["object"]
                session_attributes['current_question'] = 'shoes_locations'
                locations = get_locations('Shoes')
                speak_output = f"Check {locations[0]} for {answer}. Did you find them?"

                # adding relationship for question and bag in the database
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                    with driver.session(database="neo4j") as session:
                        session.execute_write(add_qtn_ans, question, answer)

            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                #speak_output = "Hmm,Let start over. Is it something you wear?"
                session_attributes["current_question"] = "start"

        # -------------------------keys have been found -----------------------------------------------------------------

        elif current_question == "keys_likely":
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                session_attributes["object"] = "Keys"
                question = session_attributes["user_question"]
                answer = session_attributes["object"]
                session_attributes['current_question'] = 'keys_locations'
                locations = get_locations('Keys')
                speak_output = f"Check {locations[0]} for {answer}. Did you find them?"

                # adding relationship for question and bag in the database
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                    with driver.session(database="neo4j") as session:
                        session.execute_write(add_qtn_ans, question, answer)

            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                #speak_output = "Hmm,Let start over. Is it something you wear?"
                session_attributes["current_question"] = "start"

        # ------------------------- smartphone has been found -----------------------------------------------------------------

        elif current_question == "smartphone_likely":
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                session_attributes["object"] = "Smartphone"
                question = session_attributes["user_question"]
                answer = session_attributes["object"]
                session_attributes['current_question'] = 'smartphone_locations'
                locations = get_locations('Bag')
                speak_output = f"Check {locations[0]} for your {answer}. Did you find it?"

                # adding relationship for question and bag in the database
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                    with driver.session(database="neo4j") as session:
                        session.execute_write(add_qtn_ans, question, answer)

            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                #speak_output = "Hmm,Let start over. Is it something you wear?"
                session_attributes["current_question"] = "start"

        # ------------------------- bag has been found -----------------------------------------------------------------

        elif current_question == "bag_likely":
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                session_attributes["object"] = "Bag"
                question = session_attributes["user_question"]
                answer = session_attributes["object"]
                session_attributes['current_question'] = 'bag_locations'
                locations = get_locations('Bag')
                speak_output = f"Check {locations[0]} for {answer}. Did you find it?"

                # adding relationship for question and bag in the database
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                    with driver.session(database="neo4j") as session:
                        session.execute_write(add_qtn_ans, question, answer)

            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                #speak_output = "Hmm,Let start over. Is it something you wear?"
                session_attributes["current_question"] = "start"

        # ------------------ eye glasses have been found-----------------------------------------

        elif current_question == "eye glasses_likely":
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                session_attributes["object"] = "Eye glasses"
                question = session_attributes["user_question"]
                answer = session_attributes["object"]
                session_attributes['current_question'] = 'eye glasses_locations'
                locations = get_locations('Eye glasses')

                # adding relationship for question and eye glasses in the database
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                    with driver.session(database="neo4j") as session:
                        session.execute_write(add_qtn_ans, question, answer)

                speak_output = f"Check the {locations[0]} for your {answer}. Have you gotten them?"

            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Hmm,Let start over. Is it something you wear?"
                session_attributes["current_question"] = "start_21_questions"

        # -------------------------Tv remote has been found ----------------------------------------------

        elif current_question == "tv remote_likely":
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                session_attributes["object"] = "TV Remote"
                question = session_attributes["user_question"]
                answer = session_attributes["object"]
                session_attributes['current_question'] = 'tv remote_locations'
                locations = get_locations('TV Remote')
                speak_output = f"Check the {locations[0]} for {answer}. Did you find it?"

                # adding relationship for question and bag in the database
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                    with driver.session(database="neo4j") as session:
                        session.execute_write(add_qtn_ans, question, answer)

            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                speak_output = "Hmm,Let start over. Is it something you wear?"
                session_attributes["current_question"] = "start_21_questions"

        # --------------------------""""""""Retriving answers to questions already saved""""----------------------------------

            # ---------getting various tv locations---------------------------------
        elif current_question == 'tv remote_locations':
            locations = get_locations("TV Remote")
            answer = session_attributes["object"]
            location_suggestions = session_attributes.get(
                "location_suggestions", 0)
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = f"Glad I could help you find the {answer}"
                location_suggestions = 0
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                if location_suggestions == 0:
                    speak_output = f"Have you checked the {locations[1]} for the {answer}? Have you found it?"
                    location_suggestions += 1
                elif location_suggestions == 1:
                    speak_output = f"How about the {locations[2]}? It's a common place for {answer}. Have you seen it?"
                    location_suggestions += 1
                elif location_suggestions == 2:
                    speak_output = f"Sorry I have run out of possible locations for {answer}"
                    location_suggestions = 0

            session_attributes["location_suggestions"] = location_suggestions

        # ------------------getting various bag locations-------------------------------------
        elif current_question == 'bag_locations':
            locations = get_locations("Bag")
            answer = session_attributes["object"]
            location_suggestions = session_attributes.get(
                "location_suggestions", 0)
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = f"Glad I could help you find your {answer}"
                location_suggestions = 0
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                if location_suggestions == 0:
                    speak_output = f"Have you checked the {locations[1]} for your {answer}? Have you found it?"
                    location_suggestions += 1
                elif location_suggestions == 1:
                    speak_output = f"What about the {locations[2]}?. Have you seen it?"
                    location_suggestions += 1
                elif location_suggestions == 2:
                    speak_output = f"Sorry I have run out of possible locations for {answer}"
                    location_suggestions = 0

            session_attributes["location_suggestions"] = location_suggestions

        # -------------------getting various eye glasses location --------------------------------
        elif current_question == 'eye glasses_locations':
            locations = get_locations("Eye glasses")
            answer = session_attributes["object"]
            location_suggestions = session_attributes.get(
                "location_suggestions", 0)
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = f"Glad I could help you find your {answer}"
                location_suggestions = 0
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                if location_suggestions == 0:
                    speak_output = f"Have you checked the {locations[1]} for your {answer}? Have you found them?"
                    location_suggestions += 1
                elif location_suggestions == 1:
                    speak_output = f"How about the {locations[2]}. Have you seen your {answer}?"
                    location_suggestions += 1
                elif location_suggestions == 2:
                    speak_output = f"Sorry I have run out of possible locations for {answer}"
                    location_suggestions = 0

            session_attributes["location_suggestions"] = location_suggestions

        # ---------getting various Smartphone locations---------------------------------
        elif current_question == 'smartphone_locations':
            locations = get_locations("Smartphone")
            answer = session_attributes["object"]
            location_suggestions = session_attributes.get(
                "location_suggestions", 0)
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = f"Glad I could help you find the {answer}"
                location_suggestions = 0
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                if location_suggestions == 0:
                    speak_output = f"Have you checked the {locations[1]} for the {answer}? Have you found it?"
                    location_suggestions += 1
                elif location_suggestions == 1:
                    speak_output = f"How about the {locations[2]}? It's a common place for {answer}. Have you seen it?"
                    location_suggestions += 1
                elif location_suggestions == 2:
                    speak_output = f"Sorry I have run out of possible locations for {answer}"
                    location_suggestions = 0

            session_attributes["location_suggestions"] = location_suggestions

        # ---------getting various keys locations---------------------------------
        elif current_question == 'keys_locations':
            locations = get_locations("Keys")
            answer = session_attributes["object"]
            location_suggestions = session_attributes.get(
                "location_suggestions", 0)
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = f"Glad I could help you find the {answer}"
                location_suggestions = 0
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                if location_suggestions == 0:
                    speak_output = f"Have you checked the {locations[1]} for the {answer}? Have you found them?"
                    location_suggestions += 1
                elif location_suggestions == 1:
                    speak_output = f"How about the {locations[2]}? It's a common place for {answer}. Have you seen them?"
                    location_suggestions += 1
                elif location_suggestions == 2:
                    speak_output = f"Sorry I have run out of possible locations for {answer}"
                    location_suggestions = 0

            session_attributes["location_suggestions"] = location_suggestions

        # ---------getting various shoes locations---------------------------------
        elif current_question == 'shoes_locations':
            locations = get_locations("Shoes")
            answer = session_attributes["object"]
            location_suggestions = session_attributes.get(
                "location_suggestions", 0)
            if ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input):
                speak_output = f"Glad I could help you find the {answer}"
                location_suggestions = 0
            elif ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input):
                if location_suggestions == 0:
                    speak_output = f"Have you checked the {locations[1]} for the {answer}? Have you gotten them?"
                    location_suggestions += 1
                elif location_suggestions == 1:
                    speak_output = f"How about the {locations[2]}? It's a common place where you keep your {answer}. Have you seen them?"
                    location_suggestions += 1
                elif location_suggestions == 2:
                    speak_output = f"Sorry I have run out of possible locations for {answer}"
                    location_suggestions = 0

            session_attributes["location_suggestions"] = location_suggestions

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

        elif current_question == 'not_found':
            speak_output = 'Item not found, sorry'

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return handler_input.response_builder.speak(speak_output).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


"""--------------------------------------------------MY CUSTOM FUNCTIONS-----------------------------------------------------------------------------------"""


def custom_query(url, cypher_query, json_args):
    # Define the headers for the request
    headers = {"cypherquery": cypher_query, "jsonargs": json_args}

    try:
        # Send a GET request to the URL with the headers
        response = requests.get(url, headers=headers)

        # Check if the response is valid
        response.raise_for_status()

        # Parse the response as JSON and return the result
        return response.json()

    except requests.exceptions.HTTPError as error:
        print(f"Custom query error: {error}")


def get_locations(object):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        with driver.session(database='neo4j') as session:
            result = session.run(
                """
                        MATCH (a:Answer {object:$object})
                        RETURN a.location1,  a.location2, a.location3
                        """,
                object=object
            )

            record = result.single()
            return record


def add_qtn_ans(tx, question, answer):
    result = tx.run(
        """
        
                
                
                MERGE (q:Question {text: $question, timestamp:datetime()})
                MERGE (a:Answer {object:$answer})
                WITH q,a
                MERGE (q)-[:HAS_ANSWER]->(a)        
                """,
        question=question,
        answer=answer,
    )

"""------------------------------------------------MY CUSTOM FUNCTIONS----------------------------------------------------------------------------------------------"""

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(FamilyNewsIntentHandler())
sb.add_request_handler(LastNameIntentHandler())
sb.add_request_handler(GetGrandChildrenIntentHandler())
sb.add_request_handler(GetGrandParentsIntentHandler())
sb.add_request_handler(GetAgeIntentHandler())
sb.add_request_handler(CaptureQuestionIntentHandler())
sb.add_request_handler(Play21QuestionsIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler()
)  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
