from typing import Any, Text, Dict, List
from datetime import datetime
import requests
import geocoder
import pytz
import json
import os

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from . import ModelHandler
from geopy.exc import GeocoderTimedOut

API_KEY = "enter key here"

# --------------------------------------------------------- SETUP CONFIGURE --------------------------------------------------------- 
class ActionConfigureSetup(Action):
  def name(self) -> Text:
    return "action_configure_setup"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    # Check if user_config.json exists in the parent directory
    parent_directory = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(parent_directory, "..", "user_config.json")
        
    if os.path.isfile(config_file):
      with open(config_file, "r") as file:
        config_data = json.load(file)
            
      # Set slots with the values from user_config.json
      user_name = config_data.get("user_name")
      fav_color = config_data.get("fav_color")
      persona_prompt = config_data.get("persona_prompt")
      feedback_response = config_data.get("feedback_response")
      communication_response = config_data.get("communication_response")
      empathy_response = config_data.get("empathy_response")
      setup_response = config_data.get("setup_response")

      return [
        SlotSet("user_name", user_name),
        SlotSet("favorite_colour", fav_color),
        SlotSet("persona_prompt", persona_prompt),
        SlotSet("feedback_response", feedback_response),
        SlotSet("communication_response", communication_response),
        SlotSet("empathy_response", empathy_response),
        SlotSet("setup_response", setup_response)
      ]
        
    return []

# --------------------------------------------------------- SETUP SUBMIT --------------------------------------------------------- 
class ActionGenerateSetup(Action):
  def __init__(self):
    super().__init__()
    self.model_handler = ModelHandler()

  def name(self) -> Text:
    return "action_generate_setup"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    required_slots = [
      "user_name",
      "persona_prompt",
      "feedback_response",
      "communication_response",
      "empathy_response",
    ]

    if all(tracker.get_slot(slot) for slot in required_slots) and (tracker.get_slot("setup_response") is None):

      # Get user input from tracker
      username = tracker.get_slot("user_name")
      fav_color = tracker.get_slot("favorite_colour")
      bot_persona = tracker.get_slot("persona_prompt")
      bot_feedback = tracker.get_slot("feedback_response")
      bot_communication = tracker.get_slot("communication_response")
      bot_empathy = tracker.get_slot("empathy_response")

      user_input = (
        f"{username}: Hi! My name is {username}. Who are you?\n"
        f"HYDE: {bot_persona}\n"
        f"{username}: Nice to meet you! How do you handle criticism or feedback?\n"
        f"HYDE: {bot_feedback}\n"
        f"{username}: Okay! Now tell me this. How would you describe your communication style?\n"
        f"HYDE: {bot_communication}\n"
        f"{username}: Interesting, and how would you describe your level of empathy and understanding?\n"
        f"HYDE: {bot_empathy}\n"
        f"{username}: Great! Are you ready to work with me?\n"
        f"HYDE:"
      )

      # Generate response
      response = self.model_handler.generate_chat_response(user_input, username)

      # Save slot values to a file
      user_config = {
        "user_name": username,
        "fav_color": fav_color,
        "persona_prompt": bot_persona,
        "feedback_response": bot_feedback,
        "communication_response": bot_communication,
        "empathy_response": bot_empathy,
        "setup_response": response
      }
      parent_directory = os.path.dirname(os.path.abspath(__file__))
      file_path = os.path.join(parent_directory, "..", "user_config.json")
      with open(file_path, "w") as file:
        json.dump(user_config, file)

      # Send the response back to the user
      return [SlotSet("setup_response", response)]

    return []

# --------------------------------------------------------- CHAT FALLBACK ---------------------------------------------------------   
class ActionChitChatFallback(Action):
  def __init__(self):
    super().__init__()
    self.model_handler = ModelHandler()

  def name(self) -> Text:
    return "action_chitchat_fallback"
  
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    call_required = tracker.latest_message['intent'].get('name') == 'nlu_fallback'

    if call_required:

      # Get user input from tracker
      username = tracker.get_slot("user_name")
      bot_persona = tracker.get_slot("persona_prompt")
      bot_feedback = tracker.get_slot("feedback_response")
      bot_communication = tracker.get_slot("communication_response")
      bot_empathy = tracker.get_slot("empathy_response")

      # Get user input from tracker
      user_input = tracker.latest_message.get("text")

      input_prompt = (
        f"{username}: Hi! My name is {username}. Who are you?\n"
        f"HYDE: {bot_persona}\n"
        f"{username}: Nice to meet you! How do you handle criticism or feedback?\n"
        f"HYDE: {bot_feedback}\n"
        f"{username}: Okay! Now tell me this. How would you describe your communication style?\n"
        f"HYDE: {bot_communication}\n"
        f"{username}: Interesting, and how would you describe your level of empathy and understanding?\n"
        f"HYDE: {bot_empathy}\n"
        f"{username}: {user_input}\n"
        f"HYDE:"
      )

      # Generate a response using the model handler
      bot_response = self.model_handler.generate_chat_response(input_prompt, username)

      # Send the response back to the user
      dispatcher.utter_message(bot_response)

      return []
    
    return []
  
# --------------------------------------------------------- QA --------------------------------------------------------- 
class ActionAnswerQuestion(Action):
  def __init__(self):
    super().__init__()
    self.model_handler = ModelHandler()

  def name(self) -> Text:
    return "action_answer_question"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    call_required = (tracker.get_slot("qa_context") is not None) and (tracker.get_slot("qa_question") is not None)

    if call_required:

      # Get user input from tracker
      question = tracker.get_slot("qa_question")
      context = tracker.get_slot("qa_context")
      
      # Generate a response using the model handler
      bot_response = self.model_handler.generate_qa_response(question, context)

      # Send the text to the user
      dispatcher.utter_message(bot_response)

      return [
        SlotSet("qa_context", None),
        SlotSet("qa_question", None)  
      ]
    
    return []

# --------------------------------------------------------- SUMMARIZE ---------------------------------------------------------   
class ActionSummarizeText(Action):
  def __init__(self):
    super().__init__()
    self.model_handler = ModelHandler()

  def name(self) -> Text:
    return "action_summarize_text"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    call_required = (tracker.get_slot("summarization_text") is not None)

    if call_required:

      # Get user input from tracker
      text = tracker.get_slot("summarization_text")

      # Generate a response using the model handler
      summary = self.model_handler.generate_summarization_response(text)

      # Send the text to the user
      dispatcher.utter_message(summary)

      return [SlotSet("summarization_text", None)]

    return []

# --------------------------------------------------------- GENERATE ---------------------------------------------------------   
class ActionGenerateText(Action):
  def __init__(self):
    super().__init__()
    self.model_handler = ModelHandler()

  def name(self) -> Text:
    return "action_generate_text"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    call_required = (tracker.get_slot("generation_prompt") is not None) and (tracker.get_slot("generation_goal") is not None)

    if call_required:

      # Get user input from tracker
      goal = tracker.get_slot("generation_goal")
      text = tracker.get_slot("generation_prompt")
      
      # Generate a response using the model handler
      generated_text = self.model_handler.generate_generation_response(goal, text)

      # Send the text to the user
      dispatcher.utter_message(generated_text)

      return [SlotSet("generation_goal", None), SlotSet("generation_prompt", None)]

    return []

# --------------------------------------------------------- PARAPHRASE --------------------------------------------------------- 
class ActionParaphraseText(Action):
  def __init__(self):
    super().__init__()
    self.model_handler = ModelHandler()

  def name(self) -> Text:
    return "action_paraphrase_text"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    call_required = (tracker.get_slot("paraphrasing_text") is not None)

    if call_required:

      # Get user input from tracker
      text = tracker.get_slot("paraphrasing_text")

      # Generate a response using the model handler
      paraphrased_text = self.model_handler.generate_paraphrase_response(text)

      # Send the text to the user
      dispatcher.utter_message(paraphrased_text)

      return [SlotSet("paraphrasing_text", None)]

    return []
  

# --------------------------------------------------------- LOCAL ---------------------------------------------------------
# --------------------------------- WEATHER ---------------------------------
class ActionGetLocalWeather(Action):
  def name(self) -> Text:
    return "action_get_local_weather"
  
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    api_call_required = tracker.latest_message['intent'].get('name') == 'request_local_weather'

    if api_call_required:

      geo = geocoder.ip('me')
      if not geo.ok:
        dispatcher.utter_message(f"There was an issue requesting your current coordinates for the weather.")
        return []

      latitude = geo.latlng[0]
      longitude = geo.latlng[1]

      base_url = "https://api.openweathermap.org/data/2.5/weather"
      params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric"
      }

      try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        temperature = round(weather_data["main"]["temp"])
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"]

        return [
          SlotSet("local_temperature", temperature),
          SlotSet("local_humidity", humidity),
          SlotSet("local_weather_description", description)
        ]
      except requests.exceptions.RequestException as e:
        dispatcher.utter_message(f"There was an issue getting the current weather information: {e}")
        return []
      
    return []

# --------------------------------------------------------- LOCAL ---------------------------------------------------------
# --------------------------------- FORECAST --------------------------------
class ActionGetLocalForecast(Action):
  def name(self) -> Text:
    return "action_get_local_forecast"
  
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
    api_call_required = tracker.latest_message['intent'].get('name') == 'request_local_forecast'

    if api_call_required:

      geo = geocoder.ip('me')
      if not geo.ok:
        dispatcher.utter_message(f"There was an issue requesting your current coordinates for the forecast.")
        return []

      latitude = geo.latlng[0]
      longitude = geo.latlng[1]

      base_url = "https://api.openweathermap.org/data/2.5/forecast"
      params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric"
      }

      try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        forecast_data = response.json()
      
        forecasts = {}
        for entry in forecast_data["list"]:
          timestamp = entry["dt"]
          forecast_date = datetime.fromtimestamp(timestamp).date()
          if forecast_date not in forecasts:
            forecasts[forecast_date] = entry

        if forecasts:
          forecast_response = ""
          for date, entry in forecasts.items():
            forecast_response += f"Date: {date}\n"
            forecast_response += f"Weather: {entry['weather'][0]['main']}\n"
            forecast_response += f"Temperature: {round(entry['main']['temp'])}°C\n"
            forecast_response += f"Probability of Precipitation: {entry['pop'] * 100}%\n"
            forecast_response += f"Humidity: {entry['main']['humidity']}%\n\n"

          return [SlotSet("local_forecast", forecast_response)]
        else:
          dispatcher.utter_message("Failed to parse the forecast.")
        return []
      except requests.exceptions.RequestException as e:
        dispatcher.utter_message(f"There was an issue getting the forecast information: {e}")
        return []    
      
    return []    

# --------------------------------------------------------- LOCAL ---------------------------------------------------------
# --------------------------------- SUNRISE --------------------------------
class ActionGetLocalSunrise(Action):
  def name(self) -> Text:
    return "action_get_local_sunrise"
    
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
    api_call_required = tracker.latest_message['intent'].get('name') == 'request_local_sunrise'

    if api_call_required:

      geo = geocoder.ip('me')
      if not geo.ok:
        dispatcher.utter_message(f"There was an issue requesting your current coordinates for the sunrise.")
        return []

      latitude = geo.latlng[0]
      longitude = geo.latlng[1]

      base_url = "https://api.sunrise-sunset.org/json"
      params = {
        "lat": latitude,
        "lng": longitude,
        "formatted": 0
      }
    
      try:
        response = requests.get(base_url, params=params)
        data = response.json()
    
        sunrise_str = data['results']['sunrise']
        sunrise_time = datetime.fromisoformat(sunrise_str)
        current_timezone = pytz.timezone('America/Winnipeg')
        sunrise = sunrise_time.astimezone(current_timezone)

        return [SlotSet("local_sunrise", str(sunrise))]

      except (AttributeError, GeocoderTimedOut):
        dispatcher.utter_message(f"There was an issue requesting the locations coordinates for the sunrise.")
        return []
    
    return []

# --------------------------------------------------------- LOCAL ---------------------------------------------------------
# --------------------------------- SUNSET --------------------------------
class ActionGetLocalSunset(Action):
  def name(self) -> Text:
    return "action_get_local_sunset"
    
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
    api_call_required = tracker.latest_message['intent'].get('name') == 'request_local_sunset'

    if api_call_required:

      geo = geocoder.ip('me')
      if not geo.ok:
        dispatcher.utter_message(f"There was an issue requesting your current coordinates for the sunset.")
        return []

      latitude = geo.latlng[0]
      longitude = geo.latlng[1]

      base_url = "https://api.sunrise-sunset.org/json"
      params = {
        "lat": latitude,
        "lng": longitude,
        "formatted": 0
      }
    
      try:
        response = requests.get(base_url, params=params)
        data = response.json()
    
        sunset_str = data['results']['sunset']
        sunset_time = datetime.fromisoformat(sunset_str)
        current_timezone = pytz.timezone('America/Winnipeg')
        sunset = sunset_time.astimezone(current_timezone)

        return [SlotSet("local_sunset", str(sunset))]

      except (AttributeError, GeocoderTimedOut):
        dispatcher.utter_message(f"There was an issue requesting the locations coordinates for the sunset.")
        return []
      
    return []
    
# --------------------------------------------------------- LOCAL ---------------------------------------------------------
# --------------------------------- TIMEZONE --------------------------------
class ActionGetLocalTimezone(Action):
  def name(self) -> Text:
    return "action_get_local_timezone"
    
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
    api_call_required = tracker.latest_message['intent'].get('name') == 'request_local_timezone'

    if api_call_required:

      current_time = datetime.now()
      timezone = current_time.astimezone().tzinfo

      return [SlotSet("local_timezone", str(timezone))]
  
    return []

# --------------------------------------------------------- LOCAL ---------------------------------------------------------
# --------------------------------- DATE --------------------------------
class ActionGetLocalDate(Action):
  def name(self) -> Text:
    return "action_get_local_date"
    
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    api_call_required = tracker.latest_message['intent'].get('name') == 'request_local_date'

    if api_call_required:

      current_date = datetime.now().strftime("%B %d, %Y")  # Get current date

      return [SlotSet("local_date", current_date)]
    
    return []
  
# --------------------------------------------------------- LOCAL ---------------------------------------------------------
# --------------------------------- TIME --------------------------------
class ActionGetLocalTime(Action):
  def name(self) -> Text:
    return "action_get_local_time"
    
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    api_call_required = tracker.latest_message['intent'].get('name') == 'request_local_time'

    if api_call_required:

      current_time = datetime.now().strftime("%I:%M %p")  # Get current time

      return [SlotSet("local_time", current_time)]
    
    return []

# --------------------------------------------------------- LOCAL ---------------------------------------------------------
# --------------------------------- COORDINATES --------------------------------
class ActionGetLocalCoordinates(Action):
  def name(self) -> Text:
    return "action_get_local_coordinates"
  
  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    api_call_required = tracker.latest_message['intent'].get('name') == 'request_local_coordinates'

    if api_call_required:

      geo = geocoder.ip('me')
      if not geo.ok:
        dispatcher.utter_message(f"There was an issue requesting your current coordinates.")
        return []

      latitude = geo.latlng[0]
      longitude = geo.latlng[1]

      return [
        SlotSet("local_latitude", latitude), 
        SlotSet("local_longitude", longitude)
      ]
    
    return []