# 🤖 AI HR Interviewer

Free, open-source AI-powered audio interview platform. Conduct structured interviews with automatic transcription, real-time AI evaluation, and detailed reports.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Deploy](https://img.shields.io/badge/Deploy-Streamlit_Cloud-FF4B4B.svg)

---

## ✨ Features

- 📄 **Resume Parsing** - PDF/DOCX upload with automatic text extraction
- 🎯 **Role-Specific Questions** - AI generates tailored questions based on resume + job description
- 🎙️ **Audio Interview** - 30s think time → 90s recording per question
- 🔄 **Auto-Transcription** - Groq Whisper (cloud) or Local Whisper (offline)
- 🤖 **Real-Time AI Evaluation** - Score, feedback, strengths, improvements per answer
- 📊 **Comprehensive Report** - Overall score, verdict, strengths, gaps, resources
- 📥 **Export** - Download full interview report as text file

---

## 🚀 Free Lifetime Deployment (Streamlit Community Cloud)

**Cost: $0 forever** for public repositories.

### Prerequisites
- GitHub account
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Step-by-Step Deploy (3 minutes)

#### 1. Fork/Clone This Repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-hr-interviewer.git
cd ai-hr-interviewer
```

#### 2. Push to Your GitHub
```bash
git init
git add .
git commit -m "Initial commit - AI HR Interviewer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-hr-interviewer.git
git push -u origin main
```

#### 3. Deploy on Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository: `YOUR_USERNAME/ai-hr-interviewer`
5. Branch: `main`
6. Main file path: `app.py`
7. Click **"Deploy!"**

#### 4. Add Groq API Key (Required for AI features)
1. In Streamlit Cloud dashboard, click your app → **Settings** → **Secrets**
2. Add this TOML:
```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
```
3. Click **Save** → App restarts automatically

#### 5. Done! 🎉
Your app is live at: `https://YOUR_USERNAME-ai-hr-interviewer.streamlit.app`

---

## 🛠 Local Development

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ai-hr-interviewer.git
cd ai-hr-interviewer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

Open http://localhost:8501

---

## 🔑 Configuration

### Groq API Key (Required)
Get free key at: https://console.groq.com/keys

- **Free tier**: 14,400 requests/day
- **Models**: Llama 3.3 70B, Mixtral 8x7B, Gemma 2 9B

### Transcription Options
| Engine | Cost | Speed | Accuracy | Best For |
|--------|------|-------|----------|----------|
| **Groq Whisper** | Free* | Fast | High | Production |
| **Local Whisper** | Free | Slow | High | Offline/Privacy |

*Uses Groq API quota

---

## 📁 Project Structure

```
ai-hr-interviewer/
├── app.py                 # Main Streamlit application
├── groq_hr.py            # Groq API wrapper
├── kaggle_hr_ai_model.py # Local LLM (optional, GPU needed)
├── requirements.txt      # Python dependencies
├── packages.txt          # System packages (ffmpeg, etc.)
├── .streamlit/
│   └── config.toml       # Streamlit Cloud config
├── .gitignore
└── README.md
```

---

## 🎯 Usage Flow

1. **Upload Resume** - PDF or DOCX
2. **Enter Job Role** - e.g., "Senior React Developer"
3. **Paste Job Description** (optional) - For better tailored questions
4. **Configure Interview** - Number of questions, difficulty, types
5. **Start Interview** - AI generates role-specific questions
6. **Answer Questions** - 30s think time → Record audio (max 90s)
7. **Auto-Evaluation** - Real-time AI scoring & feedback
8. **View Report** - Overall score, verdict, detailed breakdown
9. **Download Report** - Save for records

---

## 🔧 Troubleshooting

### App won't deploy?
- Check **Manage app → Logs** in Streamlit Cloud
- Ensure `requirements.txt` has no conflicts
- Verify `packages.txt` includes `ffmpeg`

### Transcription fails?
- Use **Groq Whisper (Cloud)** in sidebar (default)
- Local Whisper downloads 140MB model on first run
- Check Groq API key in Secrets

### AI features not working?
- Add `GROQ_API_KEY` to Streamlit Cloud Secrets
- Verify key is valid at console.groq.com

### Audio recording issues?
- Use Chrome/Edge/Firefox (Safari has limited MediaRecorder support)
- Allow microphone permissions
- Keep answers under 90 seconds

---

## 💰 Cost Breakdown (Free Tier)

| Service | Free Limit | Your Usage |
|---------|------------|------------|
| Streamlit Cloud | Unlimited public apps | ✅ Free forever |
| Groq API | 14,400 req/day | ~50 req/interview |
| GitHub | Unlimited public repos | ✅ Free |
| Bandwidth | 100 GB/month | ✅ Plenty |

**Total: $0/month for life**

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

MIT License - Free for personal and commercial use.

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) - Amazing web app framework
- [Groq](https://groq.com) - Lightning-fast LLM inference
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) - Bundled ffmpeg binary

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/ai-hr-interviewer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/ai-hr-interviewer/discussions)

---

**Made with ❤️ for better hiring**