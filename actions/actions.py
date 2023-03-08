# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from datetime import datetime
from definitions import (DATABASE_HOST, DATABASE_PASSWORD, 
                         DATABASE_PORT, DATABASE_USER, df_act)
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, SlotSet
from typing import Any, Dict, List, Optional, Text

import mysql.connector
import pandas as pd
import random


class ActionEndDialog(Action):
    """Action to cleanly terminate the dialog."""
    # ATM this action just call the default restart action
    # but this can be used to perform actions that might be needed
    # at the end of each dialog
    def name(self):
        return "action_end_dialog"

    async def run(self, dispatcher, tracker, domain):

        return [FollowupAction('action_restart')]
    

class ActionDefaultFallbackEndDialog(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback_end_dialog"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_default")
        dispatcher.utter_message(template="utter_default_close_session")

        # End the dialog, which leads to a restart.
        return [FollowupAction('action_end_dialog')]


def get_latest_bot_utterance(events) -> Optional[Any]:
    """
       Get the latest utterance sent by the VC.
        Args:
            events: the events list, obtained from tracker.events
        Returns:
            The name of the latest utterance
    """
    events_bot = []

    for event in events:
        if event['event'] == 'bot':
            events_bot.append(event)

    if (len(events_bot) != 0
            and 'metadata' in events_bot[-1]
            and 'utter_action' in events_bot[-1]['metadata']):
        last_utterance = events_bot[-1]['metadata']['utter_action']
    else:
        last_utterance = None

    return last_utterance


def check_session_not_done_before(cur, prolific_id, session_num):
    
    query = ("SELECT * FROM sessiondata WHERE prolific_id = %s and session_num = %s")
    cur.execute(query, [prolific_id, session_num])
    done_before_result = cur.fetchone()
    
    not_done_before = True

    # user has done the session before
    if done_before_result is not None:
        not_done_before = False
        
    return not_done_before
    


class ActionLoadSessionFirst(Action):
    
    def name(self) -> Text:
        return "action_load_session_first"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        prolific_id = tracker.current_state()['sender_id']
        
        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)
        
        session_loaded = check_session_not_done_before(cur, prolific_id, 1)
        
        conn.close()

        return [SlotSet("session_loaded", session_loaded)]


class ActionLoadSessionNotFirst(Action):

    def name(self) -> Text:
        return "action_load_session_not_first"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        prolific_id = tracker.current_state()['sender_id']
        session_num = tracker.get_slot("session_num")
        session_loaded = True
        mood_prev = ""
        
        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)
        
        # get user name from database
        # should be possible
        query = ("SELECT name FROM users WHERE prolific_id = %s")
        cur.execute(query, [prolific_id])
        user_name_result = cur.fetchone()
        
        if user_name_result is None:
            session_loaded = False
            
        else:
            # check if user has done previous session before '
            # (i.e., if session data is saved from previous session)
            query = ("SELECT * FROM sessiondata WHERE prolific_id = %s and session_num = %s and response_type = %s")
            cur.execute(query, [prolific_id, str(int(session_num) - 1), "state_5"])
            done_previous_result = cur.fetchone()
            
            if done_previous_result is None:
                session_loaded = False
                
            else:
                # check if user has not done this session before
                # checks if some data on this session is already saved in database
                # this basically means that it checks whether the user has already 
                # completed the session part until the dropout question before,
                # since that is when we first save something to the database
                session_loaded = check_session_not_done_before(cur, prolific_id, 
                                                               session_num)
                
                if session_loaded:
                    # Get mood from previous session
                    query = ("SELECT response_value FROM sessiondata WHERE prolific_id = %s and session_num = %s and response_type = %s")
                    cur.execute(query, [prolific_id, str(int(session_num) - 1), "mood"])
                    mood_prev = cur.fetchone()
        
        conn.close()

        
        return [SlotSet("user_name_slot_not_first", user_name_result[0]),
                SlotSet("mood_prev_session", mood_prev[0]),
                SlotSet("session_loaded", session_loaded)]
        
        
    
class ActionSaveNameToDB(Action):

    def name(self) -> Text:
        return "action_save_name_to_db"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)
        query = "INSERT INTO users(prolific_id, name, time) VALUES(%s, %s, %s)"
        queryMatch = [tracker.current_state()['sender_id'], 
                      tracker.get_slot("user_name_slot"),
                      formatted_date]
        cur.execute(query, queryMatch)
        conn.commit()
        conn.close()

        return []
    

class ActionSaveActivityExperienceMood(Action):
    def name(self):
        return "action_save_activity_experience_mood"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)
        
        prolific_id = tracker.current_state()['sender_id']
        session_num = tracker.get_slot("session_num")
        
        slots_to_save = ["mood", "effort", "activity_experience_slot",
                         "activity_experience_mod_slot",
                         "dropout_response"]
        for slot in slots_to_save:
        
            save_sessiondata_entry(cur, conn, prolific_id, session_num,
                                   slot, tracker.get_slot(slot),
                                   formatted_date)

        conn.close()
    
    
def save_sessiondata_entry(cur, conn, prolific_id, session_num, response_type,
                           response_value, time):
    query = "INSERT INTO sessiondata(prolific_id, session_num, response_type, response_value, time) VALUES(%s, %s, %s, %s, %s)"
    cur.execute(query, [prolific_id, session_num, response_type,
                        response_value, time])
    conn.commit()
    

class ActionSaveSession(Action):
    def name(self):
        return "action_save_session"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        conn = mysql.connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database='db'
        )
        cur = conn.cursor(prepared=True)
        
        prolific_id = tracker.current_state()['sender_id']
        session_num = tracker.get_slot("session_num")
        
        slots_to_save = ["state_1", "state_2", "state_3",
                         "state_4", "state_5", "state_6", "state_7",
                         "state_8", "state_9", "state_busy", "state_energy",
                         "activity_new_index"]
        for slot in slots_to_save:
        
            save_sessiondata_entry(cur, conn, prolific_id, session_num,
                                   slot, tracker.get_slot(slot),
                                   formatted_date)

        conn.close()
        

def get_previous_activity_indices_from_db(prolific_id):
    
    conn = mysql.connector.connect(
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database='db'
    )
    cur = conn.cursor(prepared=True)
    
    # get user name from database
    # should be possible
    query = ("SELECT response_value FROM sessiondata WHERE prolific_id = %s")
    cur.execute(query, [prolific_id])
    result = cur.fetchall()
    
    conn.close()
    
    return result


class ActionChooseActivity(Action):
    def name(self):
        return "action_choose_activity"

    async def run(self, dispatcher, tracker, domain):
        
        prolific_id = tracker.current_state()['sender_id']
        num_act = len(df_act)
        
        # get indices of previously assigned activities
        curr_act_ind_list = get_previous_activity_indices_from_db(prolific_id)
        
        if curr_act_ind_list is None:
            curr_act_ind_list = []
        
        # check excluded activities for previously assigned activities
        excluded = []
        for i in curr_act_ind_list:
            excluded += df_act.loc[i, 'Exclusion']
            
        # get eligible activities (not done before and not excluded)
        remaining_indices = [i for i in range(num_act) if not str(i) in curr_act_ind_list and not str(i) in excluded]
            
        # Check if prerequisites for remaining activities are met
        for i in remaining_indices:
            # Get prerequisites that are met
            preq = [j for j in df_act.loc[i, 'Prerequisite'] if j in curr_act_ind_list]
            # Exclude activities for which there is at least one prerequisite and
            # not at least one prerequisite is met.
            if (len(df_act.loc[i, 'Prerequisite']) > 0 and len(preq) == 0):
                excluded.append(str(i))
            
        # Get activities that also meet the prerequisites
        remaining_indices = [i for i in remaining_indices if not str(i) in excluded]
        
        # reset random seed
        random.seed(datetime.now())
        # chose random new activity
        act_index = random.choice([i for i in remaining_indices])
        
        return [SlotSet("activity_formulation_new_session", df_act.loc[act_index, 'Formulation Session']), 
                SlotSet("activity_formulation_new_email", df_act.loc[act_index, 'Formulation Email']),
                SlotSet("activity_new_index", act_index),
                SlotSet("activity_new_verb", df_act.loc[act_index, "Verb"])]
    

class ValidateUserNameForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_user_name_form'

    def validate_user_name_slot(
            self, value: Text, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        # pylint: disable=unused-argument
        """Validate user_name_slot input."""
        last_utterance = get_latest_bot_utterance(tracker.events)

        if last_utterance != 'utter_ask_user_name_slot':
            return {"user_name_slot": None}

        if not len(value) >= 1:
            dispatcher.utter_message(response="utter_longer_name")
            return {"user_name_slot": None}

        return {"user_name_slot": value}
    

class ValidateActivityExperienceForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_activity_experience_form'

    def validate_activity_experience_slot(
            self, value: Text, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        # pylint: disable=unused-argument
        """Validate activity_experience_slot input."""
        last_utterance = get_latest_bot_utterance(tracker.events)

        if last_utterance != 'utter_ask_activity_experience_slot':
            return {"activity_experience_slot": None}

        # people should either type "none" or say a bit more
        if not (len(value) >= 10 or "none" in value.lower()):
            dispatcher.utter_message(response="utter_provide_more_detail")
            return {"activity_experience_slot": None}

        return {"activity_experience_slot": value}
    

class ValidateActivityExperienceModForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_activity_experience_mod_form'

    def validate_activity_experience_mod_slot(
            self, value: Text, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        # pylint: disable=unused-argument
        """Validate activity_experience_mod_slot input."""
        last_utterance = get_latest_bot_utterance(tracker.events)

        if last_utterance != 'utter_ask_activity_experience_mod_slot':
            return {"activity_experience_slot": None}

        # people should either type "none" or say a bit more
        if not (len(value) >= 5 or "none" in value.lower()):
            dispatcher.utter_message(response="utter_provide_more_detail")
            return {"activity_experience_mod_slot": None}

        return {"activity_experience_mod_slot": value}
