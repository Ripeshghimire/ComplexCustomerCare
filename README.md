
Overview
This FastAPI application serves as a chatbot interface capable of processing both text and audio inputs. It utilizes Elasticsearch for information retrieval and integrates Google Text-to-Speech (gTTS) for converting text responses back into audio.

Features
Text Query Handling: Users can submit text questions, and the system provides text responses.
Audio Query Handling: Users can submit audio questions, and the system converts the audio to text, processes the query, and returns both text and audio responses.
CORS Support: Allows specific origins to interact with the API.
Logging: Captures and logs errors and other significant events for debugging purposes.
Setup
Prerequisites
Docker (for running Elasticsearch)
Python 3.8+
Virtual Environment (recommended)
Installation
Clone the repository:

bash
Copy code
git clone <repository_url>
cd <repository_directory>
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up environment variables:

Create a .env file in the root directory of the project and add the following:

bash
Copy code
ELASTICSEARCH_KEY=<your_elasticsearch_password>
Run the Elasticsearch container:

bash
Copy code
docker-compose up
Running the Application
Start the FastAPI application using Uvicorn:

bash
Copy code
uvicorn app:app --reload
The application will be available at http://127.0.0.1:8000.

API Endpoints
GET /
Returns an HTML page.

POST /query
Processes text input from the user.

Request:

JSON payload containing the question field.
Response:

JSON containing the response field with the chatbot's answer.
POST /queryaudio
Processes audio input from the user.

Request:

Form data containing the audio file.
Response:

JSON containing the response (text), query (converted text from audio), and audio_response (base64 encoded audio).
Code Explanation
Main Components
Imports and Setup:

Necessary libraries and modules are imported.
FastAPI instance is created.
Logging is configured.
Templates are set up using Jinja2.
Environment variables are loaded using dotenv.
Elasticsearch password is retrieved from environment variables.
CORS Middleware:

Configured to allow specific origins.
Conversation Chain:

Initialized using get_conversation_chain function.
Routes:

GET /: Renders the index.html template.
POST /query: Handles text queries.
POST /queryaudio: Handles audio queries. Converts audio to text, processes the query, and converts the response back to audio.
Error Handling
Errors during query processing are logged, and an appropriate JSON response with a status code is returned.

Audio Handling
Audio to Text: Converts the submitted audio file to text.
Text to Audio: Converts the chatbot's text response to an audio file using gTTS, which is then encoded in base64 for the response.
Additional Information
For further details, refer to the official FastAPI documentation and the Docker documentation.