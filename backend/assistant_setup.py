from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def upload_files(paths):
    file_ids = []
    for path in paths:
        with open(path, "rb") as f:
            file = client.files.create(file=f, purpose="assistants")
            file_ids.append(file.id)
    return file_ids

def create_vector_store(file_ids):
    vs = client.vector_stores.create(name="YogaCourseStore")
    client.vector_stores.file_batches.create_and_poll(
        vector_store_id=vs.id,
        file_ids=file_ids
    )
    return vs.id

def create_assistant(file_ids, vector_store_id):
    assistant = client.beta.assistants.create(
        name="Yoga Berater",
        instructions = """
        Du bist Yogalehrer:in und unterstützt Kund:innen dabei, die passende Yoga-Ausbildung zu finden.

        Dir werden 7 Fragen und die jeweiligen Antworten der Kund:innen bereitgestellt.
        Analysiere diese Antworten, um die passende Yoga-Ausbildung zu identifizieren.
        Nutze file_search, um relevante Informationen aus den Ausbildungsunterlagen zu finden.

        Wenn du Informationen aus den Ausbildungsunterlagen verwendest, gib keine Quellverweise wie „ “ oder ähnliche an. Formuliere die Antwort natürlich und ohne solche Markierungen.

        Wenn keine passenden Informationen in den Ausbildungsunterlagen gefunden werden, beantworte die Frage mit deinem allgemeinen Wissen als Yogalehrer:in.

        Empfehle basierend auf den Antworten eine oder mehrere geeignete Ausbildungen.
        Wenn du Informationen aus den Ausbildungsunterlagen gibst, füge am Ende der Antwort folgenden Satz hinzu:
        „Bei Fragen einfach fragen – ich helfe dir gerne weiter.“

        Beantworte danach alle Folgefragen der Kund:innen:
        – Bezieht sich die Frage auf Inhalte der Ausbildungen, nutze file_search.  
        – Geht es um andere Themen, verwende dein allgemeines OpenAI-Wissen.

        Sei dabei stets klar, präzise und direkt auf die jeweilige Frage fokussiert.
        """,
        tools=[{"type": "file_search"}],
        model="gpt-3.5-turbo",
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
    )
    return assistant.id


def delete_assistant_and_vector_store(assistant_id=None, vector_store_id=None):
    if assistant_id:
        client.beta.assistants.delete(assistant_id)
        print(f"Deleted assistant: {assistant_id}")

    if vector_store_id:
        client.vector_stores.delete(vector_store_id)
        print(f"Deleted vector store: {vector_store_id}")