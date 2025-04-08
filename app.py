from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import requests


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
search_id = os.getenv("SEARCH_ENGINE_ID")
search_api_key = os.getenv("SEARCH_API_KEY")


def get_gemini_resp(input_prompt,response):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt,response])
    return response.text

st.set_page_config("Find your house")
st.header("Find your dream house")
input_text = st.text_input("Enter the query wrt house type, location and budget")


def fetch_property_data():
    property_data =[]
    for start in range(1, 101, 10):  # Paginate 10 results at a time
        url = f"https://www.googleapis.com/customsearch/v1?q={input_text}&cx={search_id}&key={search_api_key}&start={start}"
        search_data = requests.get(url).json()
        for item in search_data.get('items', []):
            property_data.append({
            "title": item["title"],
            "link": item["link"],
            "description": item["snippet"]

        })

    # Format extracted data for Gemini prompt
    return  "\n".join(
        [f"{idx+1}. {prop['title']} - {prop['link']} \nDescription: {prop['description']}"
        for idx, prop in enumerate(property_data)]
    )



new_input_prompt= f"""
You are a specialist in finding houses for rent, so based on the provided data, suggest the best
possible matches. Optimize the search results based on the user's budget and preferences.

Please analyze the listings and provide a summary of the best available options, highlighting:

1.  Show the selected listing details (title, description).
2.  Show the selected exact matching listing URLs.
3.  If possible display the price of the house if available in description or title.
4.  Show URL of listing under heading URL

Be concise and easy to understand. Only include the BEST listing available and try to provide top 5 options

Data:
"""
submit_btn = st.button("Submit")

if submit_btn:
    if input_text is not None:
        property_info = fetch_property_data()
        response = get_gemini_resp(new_input_prompt,property_info)
        st.write(response)
    else:
        st.error("enter the listing details")    


def fetch_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch content from {url}. Status Code: {response.status_code}")
        return None
