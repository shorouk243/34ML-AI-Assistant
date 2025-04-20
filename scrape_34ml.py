import streamlit as st # for UI
from openai import OpenAI # for OpenRouter API
from firecrawl import FirecrawlApp # for web crawling
from langchain.memory import ConversationBufferMemory # for memory management
from huggingface_hub import InferenceClient # for image generation
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
FIRECRAWL_KEY = os.getenv("FIRECRAWL_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
TARGET_URL = "https://34ml.com/"
MAX_PAGES = 50
SITE_CONTENT_FILE = "site_content.txt" 

# --- Firecrawl Setup ---
@st.cache_resource(show_spinner="Crawling the website ...") 
def crawl_site():
    app = FirecrawlApp(api_key=FIRECRAWL_KEY)
    crawl_result = app.crawl_url(
        url=TARGET_URL,
        params={
            "limit": MAX_PAGES,
            "scrapeOptions": {"formats": ["markdown"]}
        }
    )
    pages = getattr(crawl_result, "data", [])
    all_content = []
    for page in pages:
        content = getattr(page, "markdown", "") if hasattr(page, "markdown") else page.get("markdown", "")
        if content and content.strip():
            all_content.append(content)
    full_content = "\n\n".join(all_content)
    return full_content

def load_or_scrape_site():
    if os.path.exists(SITE_CONTENT_FILE):
        with open(SITE_CONTENT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    else:
        content = crawl_site()
        with open(SITE_CONTENT_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        return content

# --- OpenRouter Setup ---
def ask_openrouter(messages):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY
    )
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-maverick:free",
        messages=messages,
        stream=True
    )
    # Stream response as chunks
    for chunk in completion:
        if hasattr(chunk, "choices") and chunk.choices:
            yield chunk.choices[0].delta.content or ""

# --- Hugging Face Setup ---
hf_client = InferenceClient(
    provider="fal-ai",
    api_key=HF_API_KEY,
)

def generate_image(prompt):
    image = hf_client.text_to_image(
        prompt,
        model="ByteDance/SDXL-Lightning",
    )
    return image

# --- Streamlit UI ---
st.set_page_config(page_title="34ML AI Assistant", page_icon="🤖")
st.title("🤖 34ML AI Assistant")
st.info("Ask anything about the company or request content (e.g., 'Write a LinkedIn post about our new feature X').")

# --- Load site content once ---
if "site_content" not in st.session_state:
    with st.spinner("Analyzing website content..."):
        st.session_state["site_content"] = load_or_scrape_site()

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content":
         "You are a helpful assistant that always responds in English. "
         "Base your answers on the following company website content:\n"
         + st.session_state["site_content"]}
    ]

# --- Initialize memory ---
memory = ConversationBufferMemory(return_messages=True)

# --- Display chat history ---
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat input ---
if prompt := st.chat_input("Type your question or request here..."):
    memory.chat_memory.add_user_message(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if the user wants to generate an image
    if prompt.lower().startswith("generate an image of") or prompt.lower().startswith("create an image of"):
        image_prompt = prompt.split("of", 1)[-1].strip()
        with st.chat_message("assistant"):
            st.markdown(f"Generating image for: **{image_prompt}** ...")
            image = generate_image(image_prompt)
            st.image(image)
            response = f"[Image generated for: {image_prompt}]"
    else:
        # Generate assistant response (streamed)
        with st.chat_message("assistant"):
            response = st.write_stream(ask_openrouter(st.session_state.messages))
        memory.chat_memory.add_ai_message(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # --- Approval System Prompt ---
        st.markdown("""
**Here’s your LinkedIn post:**

---
""" + response + """

---

What would you like to do?  
1. ✅ Approve  
2. ✏️ Edit  
""")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve"):
                st.success("Post approved and saved!")
        with col2:
            if st.button("✏️ Edit"):
                edited = st.text_area("Edit your post:", value=response)
                if st.button("Save Edit"):
                    st.session_state.messages.append({"role": "user", "content": edited})
                    st.rerun()
