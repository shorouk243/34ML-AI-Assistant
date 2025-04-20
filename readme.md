# 🤖 34ML AI Assistant

A Streamlit-powered AI assistant for 34ML, featuring:
- Natural language chat about company info (scraped from the 34ML website)
- LinkedIn post generation with approval/edit workflow
- Image generation via Hugging Face models
- Persistent memory of past chats
- Environment-based API key management

## Features

- **Chatbot**: Ask questions about 34ML or request content (e.g., "Write a LinkedIn post about our new feature X").
- **Web Scraping**: Automatically crawls and summarizes the 34ML website using Firecrawl.
- **Image Generation**: Generate images from text prompts using Hugging Face's Inference API.
- **Approval Workflow**: Approve, edit LinkedIn posts.
- **Memory**: Remembers past chat history for context-aware responses.
- **Environment Variables**: Securely manage API keys via a `.env` file.


## Tech Stack

- **Python 3.9+**
- **Streamlit** – for the interactive web UI
- **OpenAI / OpenRouter** – for LLM-powered chat and LinkedIn post generation (`meta-llama/llama-4-maverick:free`)
- **Firecrawl** – for website crawling and content extraction
- **Hugging Face Hub** – for text-to-image generation (`ByteDance/SDXL-Lightning`)
- **LangChain** – for chat memory management
- **python-dotenv** – for environment variable management

---

## Setup

1. **Clone the repository**

    ```sh
    git clone https://github.com/shorouk243/34ml-ai-assistant.git
    cd 34ml-ai-assistant
    ```

2. **Install dependencies**

    ```sh
    pip install -r requirements.txt
    ```

3. **Create a `.env` file** in the project root with your API keys:

    ```
    FIRECRAWL_KEY=your_firecrawl_api_key
    OPENROUTER_KEY=your_openrouter_api_key
    HF_API_KEY=your_huggingface_api_key
    ```

4. **Run the app**

    ```sh
    streamlit run scrape_34ml.py
    ```

## Usage

- **Chat**: Type your question or request in the chat box.
- **Generate LinkedIn Post**: Ask for a LinkedIn post. After generation, you can approve or edit the post.
- **Generate Images**: Type prompts like `Generate an image of a robot in Cairo`.
- **Memory**: The assistant remembers your previous messages for a more natural conversation.

## Project Structure

```
├── scrape_34ml.py        # Main Streamlit app
├── requirements.txt      # Python dependencies
├── .env                  # API keys (not committed)
└── README.md             # This file
```

## Notes

- The first run will crawl the 34ML website and cache the content in `site_content.txt` for faster subsequent runs.
- API keys are required for Firecrawl, OpenRouter, and Hugging Face services.

## License

MIT License

---

**Made with ❤️ for 34ML**