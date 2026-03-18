# 🏰 Amberg Chatbot

An AI-powered tourism chatbot for Amberg, Germany that answers questions about attractions, hotels, food, activities, and more.

## Features

✨ **Optimized for Free Tier**
- Multiple Gemini model support
- 20 requests/day per model
- Easy model switching when limits are reached

🤖 **Intelligent Responses**
- Semantic search using FAISS and embeddings
- Natural language generation with Google Gemini
- Context-aware answers from knowledge base

💬 **User-Friendly Chat Interface**
- Clean, simple Streamlit UI
- Real-time chat history
- Model status and request tracking

## Tech Stack

- **LLM**: Google Generative AI (Gemini)
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
- **Search**: FAISS (semantic similarity)
- **UI**: Streamlit
- **Data**: JSON files with tourism snippets

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Amberg_Chatbot.git
   cd Amberg_Chatbot
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file with your API key**
   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

   Get your Google Generative AI API key from: https://aistudio.google.com/app/apikey

## Usage

Run the chatbot:
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

**How to use:**
1. Select a model from the dropdown at the top
2. Check the request count (shows remaining requests)
3. Ask any question about Amberg
4. Get instant AI-powered responses

## Features Explained

### Model Switching
- Each model has 20 free requests per day
- When limit is reached, switch to another model
- Limits reset daily at midnight

### Available Models
- gemini-1.5-flash (fastest, good for free tier)
- gemini-1.5-pro (more capable)
- gemini-2.5-flash (latest model)
- And more!

### Data Structure
Knowledge base includes:
- General information about Amberg
- Attractions and landmarks
- Food and beverage recommendations
- Accommodation options
- Activities and experiences
- Day trips from Amberg
- And more!

## Project Structure

```
Amberg_Chatbot/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not committed to git)
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── data/              # Knowledge base (JSON files)
    ├── attractions.json
    ├── food_beer.json
    ├── accommodation.json
    ├── culture_museums.json
    └── ... (more JSON files)
```
## Future Improvements

- [ ] Persistent data store for conversation logs
- [ ] Rate limiting per user
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Custom knowledge base management


## License

MIT License - feel free to use this project!

## Author

Made with ❤️ for Amberg Tourism
