from fastapi import FastAPI, Request
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import logfire

# Import the assistant we created
from assistant_server.assistant import assistant

app = FastAPI()
logfire.configure(
  project_name='smart-home-assistant',
  pydantic_plugin=logfire.PydanticPlugin(record='all') # Pydantic integration
)
logfire.instrument_fastapi(app) # FastAPI integration
RequestsInstrumentor().instrument() # requests integration

@app.post('/prompt')
async def answer_prompt(request: Request):
  with logfire.span('Decoding the request body'):
    # Parse the JSON body and get the prompt
    body = await request.json()
    logfire.info('{prompt=}', prompt=body['prompt'])

  # Pose the prompt to the model
  with logfire.span('Generating answer to User\'s prompt'):
    answer = assistant.run(body['prompt'])
    logfire.info('{answer=}', answer=answer)

  return { 'message': answer.response }
