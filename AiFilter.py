"""
AiFilter.py
-------------
Sends Data to Gemini, gives score for relevance.
"""

import environment
import json
from google import genai


# Configuration 
# -----------------------------------------------------------------
prompt = """
    System Instructions:
    You are a Senior Energy Markets Analyst. Evaluate Polymarket questions for their impact on the Gas and Electricity Markets. 
    
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
    for i in range(0, len(question_list), batch_size):
        batch = question_list[i:i+batch_size]

        full_prompt = prompt + json.dumps(batch, indent = 2)
        
        client = genai.Client(api_key= environment.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview', contents=full_prompt)
    
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






