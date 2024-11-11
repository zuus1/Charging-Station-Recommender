from config import OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY

def classify_type(activity_pref):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are an assistant that converts the user query into a place type to be used in Google Places API. Return the type."},
            {"role": "user", "content": f"Convert the following query into a category: '{activity_pref}'"},
        ]
    )

    # Extract the intent category from the response
    classified_type = response.choices[0].message.content.strip()
    # print("Type:", classified_type)
    return classified_type

