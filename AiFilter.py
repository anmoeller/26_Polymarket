"""
AiFilter.py
-------------
Sends Data to Gemini, gives score for relevance.
"""

import json
from google import genai
import os
import time


# Configuration 
# -----------------------------------------------------------------
prompt = """
    System Instructions:
    You are a Senior Energy Markets Analyst. Evaluate Polymarket questions for their impact on the German Gas and Electricity Markets. 
    
    Analysis Framework:
    - Gas: Driven by weather (heating), LNG arrivals, Storage, and geopolitics.
    - Power: Driven by weather (renewables), fuel costs (Gas/Coal), and industrial load.

    Task:
    Assign a 'relevance_score' (0-10) to each question. 
    Strictness Protocol: Most questions should score 0. Only assign a score above 0 if there is a logical, causal link to energy supply, demand, or price formation. Entertainment, celebrity news, and sports must be scored 0.

    Output Requirement:
    Return strictly a valid JSON array of objects. No filler text.
    Fields: "id", "relevance_score", "reasoning", "impact_type".

    Input List:
    """


# Gemini
# -----------------------------------------------------------------

def AiFilterFunction(markets: list[dict]) -> dict[str, tuple[int, str, str]]:
    batch_size = 15

    question_list =  []
    for item in markets:
        question_list.append({
            "id":item["id"],
            "question":item["question"]
        })

    result = {}
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            import environment
            api_key = environment.GEMINI_API_KEY
        except ImportError:
            print("No API-Key found")

    for i in range(0, len(question_list), batch_size):
        batch = question_list[i:i+batch_size]

        full_prompt = prompt + json.dumps(batch, indent = 2)
        
        max_retries = 3
        attempt = 0
        success = False

        while attempt < max_retries and not success:
            try: 
                client = genai.Client(api_key= api_key)
                response = client.models.generate_content(
                    model='gemini-3.1-flash-lite-preview', contents=full_prompt)
                success = True
            except Exception as e:
                attempt += 1
                if "503" in str(e) or "overloaded" in str(e).lower():
                    wait_time = attempt * 10
                    print(f"Server not reachable (503). Attempt {attempt}/{max_retries}. Wait {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"{e}")
                    break
        if not success:
            print(f"Batch {i} skipped, AI not available")
            continue


        try:
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_response)

            for item in data:
                result[item["id"]] = (
                    item["relevance_score"],
                    item["reasoning"],
                    item["impact_type"]
                )
        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der KI-Antwort: {e}")
            continue

    return result






