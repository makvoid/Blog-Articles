from pydantic import BaseModel, Field
from phi.assistant import Assistant
from phi.llm.ollama import Ollama
from dataclasses import dataclass
from random import randint
import requests
import logfire

# Mock the reply from the server
MOCK_REPLY = True

@dataclass
class SmartHomeAssistantReply(BaseModel):
  response: str = Field(..., description='Your response to the User\'s question.')

@logfire.instrument("Get Climate Sensor", extract_args=True)
def get_climate_sensor(location: str) -> str:
  """Use this function to get the climate (temperature / humidity) of a specific location.
     If the User requests a room that is normally in a residential home, use the value 'interior'.

  Args:
    args (str): The location to get the climate for.
  Returns:
    str: The string representation of the current climate at the specified location.
  """
  if location not in ['garage', 'interior']:
    logfire.error('Invalid location provided')
    return 'Sorry, I do not have information about that location.'

  with logfire.span('Fetching server response'):
    # Mock the reply from the API for testing
    if MOCK_REPLY:
      body = { 'temperature': randint(70, 75), 'humidity': randint(30, 35) }
    else:
      try:
        response = requests.get(f'https://<endpoint-url>/sensor/CLIMATE_{location.upper()}')
        body = response.json()
      except Exception as e:
        logfire.error(f'Error fetching climate values: {str(e)}')
        raise

    # Return the formatted reply
    logfire.info(f'({'mock' if MOCK_REPLY else 'live'}) {{body=}}', body=body)
    return f"{round(body['temperature'])}° F, {round(body['humidity'])}% Humidity"

assistant = Assistant(
  llm=Ollama(
    model='llama3:8b',
    options={ 'temperature': 0.0 }
  ),
  output_model=SmartHomeAssistantReply,
  tools=[get_climate_sensor],
  debug_mode=True
)
