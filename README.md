# Yoga Chatbot 🤖🧘

An intelligent AI-powered chatbot designed to help users find the perfect yoga training program. The chatbot uses OpenAI's GPT models with file search capabilities to provide personalized recommendations based on user responses to a series of questions.

## 🌟 Features

- **Interactive Q&A Flow**: Guides users through a series of questions to understand their yoga goals and preferences
- **AI-Powered Recommendations**: Uses OpenAI Assistant API with file search to recommend suitable yoga courses
- **Voice Input Support**: Includes speech recognition for hands-free interaction (German language)
- **Dynamic Content Sync**: Automatically syncs course materials from Google Drive
- **Session Management**: Maintains user sessions with automatic timeout handling
- **Answer Validation**: Validates user answers against example responses before proceeding
- **Real-time Chat Interface**: Modern, responsive chat UI with smooth animations

## 🏗️ Architecture

The application consists of:

- **Backend**: FastAPI-based REST API
- **Frontend**: Vanilla JavaScript with HTML/CSS
- **AI Integration**: OpenAI Assistant API with vector store for document search
- **Storage**: Google Drive integration for course materials
- **Session Management**: In-memory session storage with timeout

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Google Cloud Service Account credentials (for Drive access)
- Google Drive folder ID containing course PDFs

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/apollodev1107-star/Yoga-Chatbot.git
   cd yoga_chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DRIVE_FOLDER_ID=your_google_drive_folder_id_here
   ```

6. **Set up Google Drive credentials**
   
   - Create a Google Cloud Service Account
   - Download the credentials JSON file
   - Place it as `backend/credentials.json`
   - Share your Google Drive folder with the service account email

7. **Prepare course materials**
   
   - Upload course PDFs to your Google Drive folder
   - Ensure `Questions.pdf` and `Example Answers.pdf` are in the folder
   - The system will automatically download and process these files

## 🎯 Usage

1. **Start the server**
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Access the application**
   
   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

3. **Interact with the chatbot**
   - Click the chat button to start a conversation
   - Answer the questions about your yoga preferences
   - The chatbot will validate your answers and provide recommendations
   - Use the microphone button for voice input (German)

## 📁 Project Structure

```
yoga_chatbot/
├── backend/
│   ├── main.py              # FastAPI application and routes
│   ├── chat_logic.py        # Chat logic and validation
│   ├── assistant_setup.py   # OpenAI Assistant configuration
│   ├── drive_sync.py        # Google Drive integration
│   └── credentials.json     # Google Service Account (not in repo)
├── static/
│   ├── script.js           # Frontend JavaScript
│   ├── style.css           # Styling
│   └── Icon_Chatbot.png    # Chatbot icon
├── templates/
│   └── index.html          # Main HTML template
├── downloads/              # Auto-downloaded PDFs (gitignored)
├── .env                    # Environment variables (gitignored)
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for Assistant API access
- `DRIVE_FOLDER_ID`: Google Drive folder ID containing course materials

### Assistant Settings

The assistant is configured with:
- **Model**: `gpt-3.5-turbo`
- **Tool**: File search with vector store
- **Update Frequency**: Every 24 hours (automatic)

### Session Management

- **Session Timeout**: 30 minutes of inactivity
- **Session Storage**: In-memory (resets on server restart)

## 🔒 Security Notes

- **Never commit** `credentials.json` or `.env` files
- The `.gitignore` file is configured to exclude sensitive files
- Regenerate credentials if they were accidentally committed
- Use environment variables for all API keys

## 🛠️ API Endpoints

### `GET /`
Returns the main HTML page with the chatbot interface.

### `POST /chat`
Handles chat interactions.

**Request Body:**
```json
{
  "session_id": "optional-session-id",
  "message": "user message"
}
```

**Response:**
```json
{
  "reply": "bot response",
  "session_id": "session-id",
  "done": false
}
```

## 📝 How It Works

1. **Initialization**: On startup, the system downloads PDFs from Google Drive and creates an OpenAI Assistant with file search capabilities.

2. **Question Flow**: Users are presented with questions from `Questions.pdf`, one at a time.

3. **Answer Validation**: Each answer is validated against `Example Answers.pdf` using the Assistant API.

4. **Recommendation**: After all questions are answered, the Assistant searches through course materials to provide personalized recommendations.

5. **Follow-up**: Users can ask follow-up questions, which are answered using either the course materials or general knowledge.

## 🔄 Auto-Update System

The system automatically:
- Downloads latest PDFs from Google Drive every 24 hours
- Recreates the vector store with updated documents
- Updates the Assistant with new course information

## 🐛 Troubleshooting

### Common Issues

1. **"Assistant not created" error**
   - Check your OpenAI API key
   - Ensure you have sufficient API credits

2. **Google Drive sync fails**
   - Verify `credentials.json` is in the correct location
   - Check that the service account has access to the Drive folder
   - Confirm the `DRIVE_FOLDER_ID` is correct

3. **PDFs not loading**
   - Ensure `Questions.pdf` exists in the Drive folder
   - Check that the `downloads` folder is writable

4. **Session issues**
   - Sessions are stored in memory and reset on server restart
   - For production, consider using Redis or a database

## 🚧 Future Improvements

- [ ] Persistent session storage (database/Redis)
- [ ] Multi-language support
- [ ] User authentication
- [ ] Analytics and conversation tracking
- [ ] Admin dashboard for managing courses
- [ ] Email notifications for recommendations
- [ ] Integration with booking systems

## 📄 License

This project is private and proprietary.

## 👥 Contributing

This is a private project. For contributions or questions, please contact the repository owner.

## 🙏 Acknowledgments

- OpenAI for the Assistant API
- FastAPI for the web framework
- Google Drive API for document storage

---

**Note**: This chatbot is specifically designed for yoga course recommendations and uses German language for interactions. Modify the language settings in `static/script.js` and `backend/main.py` for other languages.

