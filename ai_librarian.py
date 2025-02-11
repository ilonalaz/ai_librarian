import requests
import openai
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables and set API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

MDZ_BASE_URL = "https://api.digitale-sammlungen.de/iiif/presentation/v2/collection/top?cursor=initial"

def fetch_books(query):
    response = requests.get(MDZ_BASE_URL)
    if response.status_code == 200:
        data = response.json()
        results = []
        for book in data.get("manifests", []):
            title = book.get("label", "Unknown Title")
            description = "No description available"
            thumbnail = book.get("thumbnail", {}).get("@id", "")
            view_link = book.get("@id", "")
            if query.lower() in title.lower():
                results.append({
                    "title": title,
                    "description": description,
                    "thumbnail": thumbnail,
                    "view_link": view_link
                })
        return results[:10]  # Return top 10 matches
    return []

def chat_with_librarian(user_input, conversation_history):
    # Append the user's message
    conversation_history.append({"role": "user", "content": user_input})
    
    # Build the full message list (system instruction + conversation history)
    messages = [{"role": "system", "content": "You are an AI librarian. Answer user queries and find relevant books."}] + conversation_history
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ai_reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": ai_reply})
    return ai_reply, conversation_history

def main():
    st.title("📚 KI-Bibliothekar")

    # Initialize conversation and an input key counter in session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0

    # Display conversation history
    for message in st.session_state.conversation:
        role = "You" if message["role"] == "user" else "Librarian"
        st.write(f"**{role}:** {message['content']}")

    # Use a form for user input so that the entire form resets after submission.
    with st.form(key="input_form"):
        # Assign a dynamic key using the counter; this key will change after each submission.
        user_input = st.text_input("Geben Sie Ihre Frage ein:", key=f"user_input_{st.session_state.input_key}")
        submit_button = st.form_submit_button(label="Absenden")

    # If the form is submitted and input is not empty, process the query.
    if submit_button and user_input.strip():
        ai_reply, updated_conversation = chat_with_librarian(user_input, st.session_state.conversation)
        st.session_state.conversation = updated_conversation
        # Increment the counter to change the widget key, forcing the input field to be cleared.
        st.session_state.input_key += 1

if __name__ == "__main__":
    main()