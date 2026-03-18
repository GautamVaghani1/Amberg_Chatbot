import streamlit as st
import os
import json
import faiss
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta

# =========================
# API CONFIGURATION (TEMPORARY DEBUG - ROTATE AFTER 1 DAY!)
# =========================
GOOGLE_API_KEY = "AIzaSyBx-5xIgPYbr6ees-lHigiu79uWaZXWhqs"
genai.configure(api_key=GOOGLE_API_KEY)

# Page config
st.set_page_config(page_title="Amberg Chatbot", page_icon="🏰", layout="centered")

# =========================
# LOAD DATA (CACHED)
# =========================
@st.cache_resource
def load_system():
    all_snippets = []
    folder_path = "data/"

    for file in os.listdir(folder_path):
        category = file.replace(".json", "")
        with open(os.path.join(folder_path, file)) as f:
            data = json.load(f)
            for snippet in data["snippets"]:
                all_snippets.append({
                    "text": snippet,
                    "category": category
                })

    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = [item["text"] for item in all_snippets]
    embeddings = model.encode(texts, show_progress_bar=False)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return all_snippets, model, index

all_snippets, embedding_model, faiss_index = load_system()

# =========================
# GET AVAILABLE MODELS
# =========================
@st.cache_resource
def get_available_models():
    """Fetch all available Gemini models that support content generation"""
    try:
        models = genai.list_models()
        suitable_models = []

        for model in models:
            if "generateContent" in model.supported_generation_methods:
                model_name = model.name.replace("models/", "")
                suitable_models.append(model_name)

        if suitable_models:
            return sorted(suitable_models)
        else:
            return ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        return ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

available_models = get_available_models()

# =========================
# INITIALIZE SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-1.5-flash"

if "request_counts" not in st.session_state:
    st.session_state.request_counts = {}

# =========================
# REQUEST TRACKING
# =========================
def get_request_count(model_name):
    today = datetime.now().date()
    key = f"{model_name}_{today}"
    return st.session_state.request_counts.get(key, 0)

def increment_request_count(model_name):
    today = datetime.now().date()
    key = f"{model_name}_{today}"
    if key not in st.session_state.request_counts:
        st.session_state.request_counts[key] = 0
    st.session_state.request_counts[key] += 1

def check_request_limit(model_name, limit=20):
    count = get_request_count(model_name)
    return count >= limit

def get_next_reset_time():
    now = datetime.now()
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    time_diff = next_midnight - now
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60
    return f"{hours}h {minutes}m"

# =========================
# FUNCTIONS
# =========================
def retrieve(query, k=15):
    query_embedding = embedding_model.encode([query])
    D, I = faiss_index.search(query_embedding, k)
    results = [all_snippets[i]["text"] for i in I[0]]
    return results

def chatbot(query, model_name):
    retrieved_chunks = retrieve(query)
    context = "\n".join(retrieved_chunks)

    prompt = f"""
You are a friendly, knowledgeable, and professional tourism guide for Amberg, Germany.

Your goal is to help visitors by giving clear, natural, and engaging answers — just like a real human tour guide would.

Context:
{context}

Question:
{query}

Answer:
"""

    model_gemini = genai.GenerativeModel(model_name)
    response = model_gemini.generate_content(prompt)
    return response.text

# =========================
# HEADER
# =========================
st.markdown("<h1 style='text-align: center;'>🏰 Amberg Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Your AI Tourism Guide</p>", unsafe_allow_html=True)

# Important note
st.info("""
📢 **Important Note:** This chatbot uses the Gemini Free API. There is a possibility that some models might not work due to request limits. Each model has a **20 request limit per day**. When a model reaches its limit, please switch to another model from the dropdown above.
""")

st.divider()

# =========================
# MODEL SELECTION (TOP)
# =========================
st.markdown("### Choose Model")

selected_model = st.selectbox(
    "Select AI Model:",
    available_models,
    index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0,
    label_visibility="collapsed"
)

if selected_model != st.session_state.selected_model:
    st.session_state.selected_model = selected_model

# Show current model status
count = get_request_count(selected_model)
remaining = 20 - count

if count >= 20:
    st.error(f"🔴 Limit reached for {selected_model} (20/20)")
    st.info(f"Try another model or wait {get_next_reset_time()} for reset")
else:
    st.success(f"✅ {selected_model} - Requests: {count}/20 (Remaining: {remaining})")

st.divider()

# =========================
# ASK QUESTION (MIDDLE)
# =========================
st.markdown("### Ask Question")

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# =========================
# INPUT (BOTTOM)
# =========================
with st.form("chat_form"):
    col1, col2 = st.columns([5, 1], gap="small")

    with col1:
        user_input = st.text_input(
            "Your question:",
            placeholder="Ask about attractions, hotels, food, activities...",
            label_visibility="collapsed"
        )

    with col2:
        send_btn = st.form_submit_button("Send", use_container_width=True)

# =========================
# PROCESS INPUT
# =========================
if send_btn and user_input.strip():
    if check_request_limit(st.session_state.selected_model, limit=20):
        st.error(f"""
⚠️ **Limit Reached for {st.session_state.selected_model}**

You have used 20 requests today.

✅ Choose another model from above, or wait {get_next_reset_time()} for reset.
        """)
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.spinner("🤔 Getting answer... (this may take a moment)"):
            try:
                response = chatbot(user_input, st.session_state.selected_model)
                increment_request_count(st.session_state.selected_model)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                st.rerun()

            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: {str(e)}"
                })
                st.error(f"Failed to get response: {str(e)}")
                st.rerun()

# =========================
# BOTTOM OPTIONS
# =========================
st.divider()

if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()
