import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, timedelta
from threading import Thread
import uuid

from backend.drive_sync import download_pdfs_from_drive
from backend.assistant_setup import *
from backend.chat_logic import *

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    session_id: str | None = None
    message: str

assistant_id = None
vector_store_id = None
SESSION_TIMEOUT = timedelta(minutes=30)

QUESTIONS = []
user_sessions = {}

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat_route(input: ChatInput):
    global assistant_id
    session_id = input.session_id or str(uuid.uuid4())
    message = input.message

    now = datetime.utcnow()
    expired = [sid for sid, s in user_sessions.items() if now - s.get("last_active", now) > SESSION_TIMEOUT]
    for sid in expired:
        del user_sessions[sid]

    if input.session_id is None:
        thread_id = init_thread(assistant_id)
        user_sessions[session_id] = {"step": 0, "answers": [], "thread_id": thread_id}
        q = QUESTIONS[0]
        intro = (
            "Hallo 👋<br /><br />"
            "Lass uns gemeinsam das Angebot entdecken, das deine nächste Entwicklungsstufe im Yoga und darüber hinaus freisetzt. "
            "Bitte beantworte dazu einige Fragen:<br /><br />" + q
        )
        return {"reply": intro, "session_id": session_id}

    session = user_sessions[session_id]
    session["last_active"] = datetime.utcnow()

    if session["step"] < len(QUESTIONS):
        # valid, suggestion = validate_answer(session["step"], message)
        valid, suggestion = validate_answer_with_assistant(session["thread_id"], session["step"], message, assistant_id, QUESTIONS)
        if not valid:
            return {"reply": suggestion, "session_id": session_id}
        
        send_user_message(session["thread_id"], message)
        session["answers"].append(message)
        session["step"] += 1
        q = next_question(session["step"], QUESTIONS)
        if q:
            return {"reply": q, "session_id": session_id}
        else:
            send_user_message(session["thread_id"], "Bitte empfehle einen passenden Kurs.")
            answer = run_assistant(session["thread_id"], assistant_id)
            return {"reply": answer, "session_id": session_id, "done": True}
    else:
        send_user_message(session["thread_id"], message)
        answer = run_assistant(session["thread_id"], assistant_id)
        return {"reply": answer, "session_id": session_id}

def clean_download_folder():
    folder = "downloads"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("Downloads folder cleaned.")

def get_existing_download_paths():
    folder = "downloads"
    if not os.path.exists(folder):
        return []  # or raise an error if you prefer

    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(".pdf")
    ]

def update_assistant():
    global assistant_id, vector_store_id, QUESTIONS
    clean_download_folder()

    delete_assistant_and_vector_store(assistant_id, vector_store_id)

    paths = download_pdfs_from_drive(DRIVE_FOLDER_ID)
    paths = get_existing_download_paths()

    file_ids = upload_files(paths)
    vector_store_id = create_vector_store(file_ids)
    assistant_id = create_assistant(file_ids, vector_store_id)
    print("Assistant created:", assistant_id)

    # assistant_id = os.getenv("YOGA_ASSISTANT_ID")
    QUESTIONS = []
    QUESTIONS = load_questions_from_pdf()

def schedule_updates():
    while True:
        update_assistant()
        time.sleep(86400)  # 24 hours

# Initial assistant creation
Thread(target=schedule_updates, daemon=True).start()
