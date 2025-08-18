from openai import OpenAI
from openai import RateLimitError
import os
from dotenv import load_dotenv
import fitz

load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

def load_questions_from_pdf(path="downloads/Questions.pdf"):
    with fitz.open(path) as doc:
        text = "\n".join(page.get_text() for page in doc)
    questions = [line.strip() for line in text.strip().split("\n") if line.strip()]
    return questions

EXAMPLE_PROMPT_TEMPLATE_ASSISTANT = """

Frage zum Thema Yoga: „{question}“
Antwort: „{answer}“
Bewerte, ob die Antwort zur Frage passt.
Die Antwort muss inhaltlich mit der Frage zusammenhängen und eine sinnvolle Reaktion darauf darstellen.

Wenn die Antwort korrekt ist, musst du ausschließlich mit „Great!“ antworten – verwende keine anderen Wörter oder Sätze.

Wenn die Antwort unklar, unpassend oder nicht mit der Frage verbunden ist, beginne mit:
„Die Antwort passt nicht zur Frage.“

Ziehe dazu die Beispiele aus „Example Answers.pdf“ heran und gib alle dort gelisteten Antwortmöglichkeiten für die entsprechende Frage als Orientierung zurück.
Du musst Beispielantworten angeben.
Wenn die Antwort falsch ist, schreibe nach den Beispielantworten am Ende ausschließlich: „Bitte schreibe die korrekte Antwort.“

⚠️ Gib keine weiteren Kommentare, Erklärungen oder Antworten aus. Reagiere ausschließlich entsprechend dieser Anweisung.
"""

def init_thread(assistant_id):
    thread = client.beta.threads.create()
    return thread.id

def send_user_message(thread_id, message):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

def run_assistant(thread_id, assistant_id):
    try:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id)
            message_content = messages.data[0].content[0].text
            annotations = message_content.annotations

            return messages.data[0].content[0].text.value
        
        return "Failed to get a response from the assistant."
    
    except RateLimitError as e:
        # You could return a fallback response or a helpful message
        print("Ratenlimit der OpenAI-API überschritten:", str(e))
        return "Leider ist derzeit viel Verkehr vorhanden. Bitte versuchen Sie es in Kürze erneut."

def next_question(index, QUESTIONS):
    return QUESTIONS[index] if index < len(QUESTIONS) else None

def validate_answer_with_assistant(thread_id, question_index, user_answer, assistant_id, QUESTIONS):
    prompt = EXAMPLE_PROMPT_TEMPLATE_ASSISTANT.format(
        question=QUESTIONS[question_index],
        answer=user_answer
    )
    send_user_message(thread_id, prompt)
    reply = run_assistant(thread_id, assistant_id)

    if reply.strip() == "Great!":
        return True, None
    return False, reply