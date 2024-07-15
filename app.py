from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from retrieve import Retrival
from dotenv import load_dotenv
from llminference import get_conversation_chain
from audiohandler import audio_to_text
from io import BytesIO
from gtts import gTTS
import base64
import tempfile

app = FastAPI()
logging.basicConfig(level=logging.INFO)

templates = Jinja2Templates(directory="templates")
load_dotenv()
es_pass = os.getenv('ELASTICSEARCH_KEY')
retrival = Retrival(es_pass=es_pass)

origins = ["http://127.0.0.1:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversation_chain = get_conversation_chain(retrival)

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    '''
    Function -> Gets the sample html for the program
    '''
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query")
async def get_text(request: Request):
    '''
    Function -> Gets the input from the user be it text or audio and gives the response to the user
    '''
    try:
        body = await request.json()
        query = body['question']
        response = conversation_chain({"question": query})
        return JSONResponse(content={'response': response['answer']})
    
    except Exception as e:
        logging.error(f"Error in get_text_audio: {str(e)}")
        return JSONResponse(content={'error': str(e)}, status_code=500) 
@app.post("/queryaudio")
async def get_audio(request: Request):
    '''
    Function -> gets the input from the user as audio converts it into text and gives the response in audio
    '''
    try:
        form = await request.form()
        audio_file = form["audio"].file
        
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            temp_audio.write(audio_file.read())
            temp_audio_path = temp_audio.name

        # Convert audio to text using the audio to text function
        query = audio_to_text(temp_audio_path)
        
        # Delete the temporary file
        os.unlink(temp_audio_path)

        if not query:
            return JSONResponse(content={"error":"Could not understand audio"}, status_code=400)

        response = conversation_chain({"question": query})
        text_response = response['answer']

        # Convert text response to speech
        tts = gTTS(text=text_response, lang='en')
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
    
        audio_base64 = base64.b64encode(audio_io.read()).decode()
        return JSONResponse(content={
            'response': text_response, 
            'query': query,
            'audio_response': audio_base64
        })
    except Exception as e:
        logging.error(f'Error getting audio {str(e)}')
        return JSONResponse(content={'error': str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)