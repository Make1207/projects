import json
import azure.functions as func
import logging
import os

def load_faq():
    file_path = os.path.join(os.path.dirname(__file__), "faq.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

faq_data = load_faq()

def find_answer(user_input):
    user_input = user_input.lower()
    
    # 1. Exakte Übereinstimmung zuerst prüfen
    if user_input in faq_data:
        return faq_data[user_input]
    
    # 2. Falls keine exakte Übereinstimmung, nach Schlagwörtern suchen
    for question, answer in faq_data.items():
        if any(word in user_input for word in question.lower().split()):
            return answer

    # 3. Wenn nichts gefunden
    return "Dazu habe ich leider keine Information."

app = func.FunctionApp()

@app.function_name(name="Chatbot")
@app.route(route="chat", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Chatbot-Anfrage empfangen.")

    frage = req.params.get("frage")
    if not frage:
        try:
            data = req.get_json()
            frage = data.get("frage", "")
        except Exception:
            return func.HttpResponse("Fehlender Parameter 'frage'", status_code=400)

    antwort = find_answer(frage)
    
    return func.HttpResponse(
        json.dumps({"antwort": antwort}),
        mimetype="application/json"
    )
