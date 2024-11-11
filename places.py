from config import OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY

def main(activity_pref):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access to GPT-4
        messages=[
            {"role": "system", "content": "You are an assistant that classifies intents based on user queries."},
            {"role": "user", "content": f"Convert the following query into a category: '{activity_pref}'"},
        ]
    )

    # Extract the intent category from the response
    intent = response['choices'][0]['message']['content'].strip()
    print("Detected Intent:", intent)
    return intent

