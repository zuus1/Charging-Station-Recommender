from config import OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY

######################################################
# Prompt to classify the type of activity
######################################################

# def classify_type(activity_pref):
#     response = openai.chat.completions.create(
#         model="gpt-3.5-turbo",  
#         messages=[
#             {"role": "system", "content": "You are an assistant that converts the user query into a place type to be used in Google Places API. Return 1 type."},
#             {"role": "user", "content": f"Convert the following query into a category: '{activity_pref}'"},
#         ]
#     )

#     # Extract the intent category from the response
#     classified_type = response.choices[0].message.content.strip()
#     print("Type:", classified_type)
#     return classified_type

######################################################
# Prompt to extract keywords
######################################################

def extract_keywords(activity_pref):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": """You are an assistant that 
             extracts keywords from the user query. Return 1 to 3 words."""},
            {"role": "user", "content": f"""Convert the following query 
             into keywords: '{activity_pref}'"""},
        ]
    )

    # Extract the intent category from the response
    keywords = response.choices[0].message.content.strip()
    print("Keywords:", keywords)
    return keywords