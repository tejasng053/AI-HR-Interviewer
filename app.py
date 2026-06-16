import streamlit as st
import streamlit.components.v1 as components
import pdfplumber
import docx
import os
import json
import tempfile
import time
import re
import subprocess
from datetime import datetime

# Setup ffmpeg path globally for whisper
try:
    import imageio_ffmpeg
    _ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["PATH"] = os.path.dirname(_ffmpeg_path) + os.pathsep + os.environ.get("PATH", "")
    os.environ["FFMPEG_PATH"] = _ffmpeg_path
    # Monkey-patch whisper to use full ffmpeg path
    import whisper.audio as whisper_audio
    _original_load_audio = whisper_audio.load_audio
    def _patched_load_audio(file, sr=16000):
        cmd = [
            _ffmpeg_path,
            "-nostdin", "-threads", "0", "-i", file,
            "-f", "s16le", "-ac", "1", "-acodec", "pcm_s16le",
            "-ar", str(sr), "-"
        ]
        try:
            out = subprocess.run(cmd, capture_output=True, check=True).stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e
        import numpy as np
        return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0
    whisper_audio.load_audio = _patched_load_audio
except Exception as _e:
    print(f"ffmpeg setup warning: {_e}")

try:
    from kaggle_hr_ai_model import SuperAIHR
except ImportError:
    SuperAIHR = None

try:
    from groq_hr import GroqHR
    class LocalGroqHR(GroqHR):
        def ask_ai(self, system_prompt, user_prompt):
            return self.chat(system_prompt, user_prompt)
except ImportError:
    LocalGroqHR = None

import whisper

st.set_page_config(page_title="AI HR Interviewer", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better UI
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .question-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .recording-active {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        border: 2px solid #fc8181;
        border-radius: 12px;
        padding: 1.5rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(252, 129, 129, 0.4); }
        50% { box-shadow: 0 0 0 10px rgba(252, 129, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(252, 129, 129, 0); }
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .sidebar .stSelectbox > div > div { background: #f7fafc; }
    .stProgress > div > div > div { background: linear-gradient(90deg, #667eea, #764ba2); }
    h1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; }
    div[data-testid="stAudioInput"] { margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Load Offline Whisper (cached, loads only once) ──
@st.cache_resource
def load_offline_whisper():
    return whisper.load_model("base")

# ── Sidebar: Configuration ──
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    
    available_backends = []
    if LocalGroqHR:
        available_backends.append("Groq Cloud API (Llama 3.1 70B)")
    if SuperAIHR:
        available_backends.append("Local Qwen-2.5-7B (GPU)")
    if not available_backends:
        backend_choice = st.selectbox("AI Backend", ["Mock Mode (No AI)"])
    else:
        backend_choice = st.selectbox("AI Backend", available_backends)
    
    st.divider()
    st.subheader("🎙️ Transcription")
    audio_backend = st.selectbox("Transcription Engine", ["Local Whisper (Offline)", "Groq Whisper (Cloud)"], index=0)

# ── Backend Connection ──
if "current_backend" not in st.session_state or st.session_state.current_backend != backend_choice or st.session_state.get("last_groq_key") != groq_key:
    st.session_state.current_backend = backend_choice
    st.session_state.last_groq_key = groq_key
    
    if backend_choice == "Groq Cloud API (Llama 3.1 70B)":
        with st.spinner("Connecting to Groq API..."):
            try:
                kwargs = {}
                if groq_key and groq_key.strip():
                    kwargs["api_key"] = groq_key.strip()
                st.session_state.ai_hr = LocalGroqHR(**kwargs)
            except Exception as e:
                st.session_state.ai_hr = None
                st.error(f"Groq connection failed: {e}")
    elif backend_choice == "Local Qwen-2.5-7B (GPU)":
        with st.spinner("Loading Qwen model..."):
            try:
                st.session_state.ai_hr = SuperAIHR()
            except Exception as e:
                st.session_state.ai_hr = None
                st.error(f"Qwen load failed: {e}")
    else:
        st.session_state.ai_hr = None

# ── Session State Init ──
if "interview_state" not in st.session_state:
    st.session_state.interview_state = {
        "stage": "upload",
        "resume_text": "", "job_role": "", "job_description": "",
        "questions": [], "current_q": 0,
        "answers": [], "evaluations": [],
        "question_phase": "ready",
        "audio_bytes": None,
        "num_questions": 5, "difficulty": "Progressive",
        "q_types": "Technical, Behavioral, Situational",
    }

# ══════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════
def extract_resume_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.strip()

def transcribe_audio(audio_bytes, audio_backend_choice):
    """Transcribe audio bytes. Falls back to Local Whisper if Groq fails."""
    tmp_path = os.path.join(tempfile.gettempdir(), "hr_interview_audio.wav")
    with open(tmp_path, "wb") as f:
        f.write(audio_bytes)

    transcript = ""
    
    # Try primary method
    try:
        if audio_backend_choice == "Groq Whisper (Cloud)":
            ai = st.session_state.get("ai_hr")
            if ai and hasattr(ai, "transcribe_audio"):
                transcript = ai.transcribe_audio(tmp_path)
            else:
                raise Exception("Groq offline, falling back to Local Whisper")
        else:
            model = load_offline_whisper()
            result = model.transcribe(tmp_path)
            transcript = result["text"].strip()
    except Exception as e:
        # Fallback: always try Local Whisper if primary failed
        if audio_backend_choice != "Local Whisper (Offline)":
            st.warning(f"⚠️ Groq Whisper failed ({e}). Using Local Whisper as fallback...")
        try:
            model = load_offline_whisper()
            result = model.transcribe(tmp_path)
            transcript = result["text"].strip()
        except Exception as e2:
            st.error(f"Transcription failed: {e2}")
    finally:
        try: os.remove(tmp_path)
        except: pass
    
    return transcript

def extract_key_skills(text, role):
    skill_keywords = {
        "frontend": ["react", "vue", "angular", "javascript", "typescript", "html", "css", "sass", "webpack", "vite", "next.js", "nuxt", "redux", "zustand", "context api", "hooks", "tailwind", "bootstrap"],
        "backend": ["python", "java", "node.js", "go", "rust", "c#", ".net", "spring", "django", "flask", "fastapi", "express", "nestjs", "sql", "postgresql", "mysql", "mongodb", "redis", "rabbitmq", "kafka", "docker", "kubernetes", "aws", "gcp", "azure"],
        "mobile": ["swift", "kotlin", "flutter", "react native", "xamarin", "ios", "android", "objective-c"],
        "devops": ["docker", "kubernetes", "jenkins", "github actions", "gitlab ci", "terraform", "ansible", "prometheus", "grafana", "elk", "aws", "gcp", "azure", "linux", "bash"],
        "data": ["python", "r", "sql", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "spark", "hadoop", "airflow", "dbt", "snowflake", "bigquery", "tableau", "powerbi"],
        "qa": ["selenium", "cypress", "playwright", "pytest", "junit", "testng", "postman", "jmeter", "cucumber", "appium"],
        "security": ["owasp", "burp suite", "metasploit", "nmap", "wireshark", "kali", "penetration testing", "vulnerability assessment"],
    }
    text_lower = text.lower()
    found_skills = []
    for category, skills in skill_keywords.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.append(skill)
    return list(set(found_skills))[:15]

def generate_questions(resume, role, job_desc, num_qs, difficulty, q_types):
    key_skills = extract_key_skills(resume + " " + job_desc, role)
    skills_context = ", ".join(key_skills) if key_skills else "general software engineering"
    
    fallback = [
        {"type": "technical", "question": f"Walk me through a challenging project from your resume relevant to {role}. What was your specific contribution?", "focus": "Experience"},
        {"type": "technical", "question": f"Given your experience with {skills_context}, what are you most and least comfortable with? How do you bridge gaps?", "focus": "Skill Match"},
        {"type": "behavioral", "question": "Describe a time you disagreed with a team decision on a technical approach. How did you handle it and what was the outcome?", "focus": "Collaboration"},
        {"type": "situational", "question": f"You're joining a {role} team mid-project. The codebase uses {skills_context}. How do you get up to speed in your first two weeks?", "focus": "Adaptability"},
        {"type": "technical", "question": f"Explain a complex {role} concept (e.g., {skills_context.split(', ')[0] if key_skills else 'state management'}) to a non-technical stakeholder.", "focus": "Communication"},
        {"type": "behavioral", "question": "Tell me about a time you had to meet a tight deadline with technical constraints. What was your strategy?", "focus": "Time Management"},
        {"type": "situational", "question": f"If you joined a {role} team midway through a sprint with unfamiliar tech stack, how would you approach onboarding?", "focus": "Onboarding"},
        {"type": "technical", "question": f"What's the most complex bug you've debugged in a {role} context involving {skills_context.split(', ')[0] if key_skills else 'core technologies'}?", "focus": "Debugging"},
        {"type": "behavioral", "question": "Describe a situation where you had to mentor a junior team member on a technical concept.", "focus": "Leadership"},
        {"type": "situational", "question": f"How would you handle conflicting priorities from multiple stakeholders in a {role} role?", "focus": "Prioritization"},
    ]
    fallback = fallback[:num_qs]
    if not st.session_state.get("ai_hr"):
        return fallback
    
    prompt = f"""You are an expert HR interviewer. Generate exactly {num_qs} interview questions for a {role} position.

Job Description: {job_desc}
Candidate Resume: {resume[:3000]}
Key Skills Detected: {skills_context}
Difficulty: {difficulty}
Question Types to include: {q_types}

Create questions that:
1. Are HIGHLY SPECIFIC to the {role} role and the candidate's actual resume/skills ({skills_context})
2. Test real technical depth, not generic knowledge
3. Reference specific technologies from the resume: {skills_context}
4. Progress in difficulty: {difficulty}
5. Cover these types: {q_types}
6. Include follow-up style questions that probe depth

Return ONLY a valid JSON array: [{{"type": "technical|behavioral|situational", "question": "...", "focus": "..."}}]"""
    try:
        result = st.session_state.ai_hr.ask_ai(
            "You are an expert HR interviewer. Return ONLY a valid JSON array, no extra text.", prompt)
        match = re.search(r'\[.*\]', result, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            if parsed and len(parsed) > 0:
                return parsed[:num_qs]
    except:
        pass
    return fallback

def evaluate_answer(question, answer, resume):
    default = {"score": 5, "feedback": "Evaluation unavailable", "strengths": [], "improvements": [], "technical_accuracy": "medium", "communication": "medium"}
    if not st.session_state.get("ai_hr") or not answer.strip():
        return default
    prompt = f"""Evaluate this interview answer. Be thorough but fair.
Question: {question}
Candidate Answer: {answer}
Candidate Background: {resume[:2000]}

Return ONLY valid JSON: {{"score": <1-10>, "feedback": "detailed evaluation", "strengths": ["s1", "s2"], "improvements": ["i1", "i2"], "technical_accuracy": "high/medium/low", "communication": "high/medium/low"}}"""
    try:
        result = st.session_state.ai_hr.ask_ai(
            "You are an expert interviewer. Return ONLY valid JSON.", prompt)
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            if isinstance(parsed, dict) and "score" in parsed:
                return parsed
    except:
        pass
    return default

def generate_final_report(state):
    fallback = {
        "overall_score": int(sum(e.get("score", 5) for e in state["evaluations"]) * 10 / max(len(state["evaluations"]), 1)),
        "verdict": "Consider", "summary": "Interview completed.",
        "key_strengths": [], "key_gaps": [], "detailed_feedback": "",
        "recommended_resources": [], "next_steps": ""
    }
    if not st.session_state.get("ai_hr"):
        return fallback
    qa_pairs = "\n".join([
        f"Q: {q['question']}\nA: {a}\nScore: {e.get('score', 'N/A')}/10"
        for q, a, e in zip(state["questions"], state["answers"], state["evaluations"])
    ])
    prompt = f"""Generate a comprehensive interview report for a {state['job_role']} candidate.
Resume: {state['resume_text'][:2000]}
Interview Q&A:
{qa_pairs}

Return ONLY valid JSON: {{"overall_score": <0-100>, "verdict": "Strong Hire|Hire|Consider|No Hire", "summary": "executive summary", "key_strengths": ["s1","s2","s3"], "key_gaps": ["g1","g2","g3"], "detailed_feedback": "feedback", "recommended_resources": ["r1","r2","r3"], "next_steps": "next steps"}}"""
    try:
        result = st.session_state.ai_hr.ask_ai(
            "You are a Senior HR Director. Return ONLY valid JSON.", prompt)
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            if isinstance(parsed, dict):
                for k in fallback:
                    if k not in parsed:
                        parsed[k] = fallback[k]
                return parsed
    except:
        pass
    return fallback

def render_countdown_timer(seconds, label):
    placeholder = st.empty()
    progress = st.progress(0.0)
    for i in range(seconds, 0, -1):
        mins, secs = divmod(i, 60)
        placeholder.markdown(f"""
        <div style="text-align:center; padding:30px 0;">
            <div style="font-size:80px; font-weight:bold; color:#FFD700; font-family:monospace;">{mins:02d}:{secs:02d}</div>
            <div style="font-size:22px; color:#aaa; margin-top:10px;">{label}</div>
        </div>""", unsafe_allow_html=True)
        progress.progress((seconds - i) / seconds)
        time.sleep(1)
    placeholder.empty()
    progress.empty()

def render_recording_timer_js():
    components.html("""
    <div style="text-align:center; padding:15px; font-family:'Segoe UI',Arial,sans-serif;">
        <div style="display:inline-flex; align-items:center; gap:12px; background:rgba(255,50,50,0.1); border:2px solid #ff4444; border-radius:16px; padding:16px 32px;">
            <div id="dot" style="width:16px;height:16px;border-radius:50%;background:#ff4444;animation:pulse 1s infinite;"></div>
            <div id="timer" style="font-size:42px;font-weight:bold;color:#ff4444;font-family:monospace;">01:30</div>
        </div>
        <div id="status" style="font-size:16px;color:#999;margin-top:12px;">🎙️ Recording in progress — speak clearly</div>
    </div>
    <style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}</style>
    <script>
        let t=90;
        const iv=setInterval(()=>{
            t--;
            const m=Math.floor(t/60),s=t%60;
            document.getElementById('timer').textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');
            if(t<=10){document.getElementById('timer').style.color='#ff0000';document.getElementById('dot').style.background='#ff0000';}
            if(t<=0){clearInterval(iv);document.getElementById('status').textContent="⏹ Time's up! Click stop on the recorder.";document.getElementById('dot').style.animation='none';document.getElementById('dot').style.background='#888';}
        },1000);
    </script>""", height=140)

# ══════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════
st.title("🤖 AI HR Interviewer")
st.caption("Upload resume → Audio interview → AI evaluation & detailed report")

state = st.session_state.interview_state

# ── STAGE 1: Upload & Configure ──
if state["stage"] == "upload":
    st.header("📄 Step 1: Upload Resume & Job Details")
    col1, col2 = st.columns(2)
    with col1:
        resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
        job_role = st.text_input("Target Job Role", placeholder="e.g., Senior React Developer")
    with col2:
        job_description = st.text_area("Job Description (optional)", height=120,
            placeholder="Paste the job description for better tailored questions...")

    st.markdown("---")
    st.subheader("🎯 Interview Settings")
    c1, c2, c3 = st.columns(3)
    with c1:
        num_questions = st.select_slider("Number of Questions", options=[3, 5, 7, 10], value=5)
    with c2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Progressive (Easy → Hard)"], index=3)
    with c3:
        q_types = st.multiselect("Question Types", ["Technical", "Behavioral", "Situational", "System Design"], default=["Technical", "Behavioral", "Situational"])

    if st.button("🚀 Start Audio Interview", type="primary", disabled=not (resume_file and job_role)):
        with st.spinner("Parsing resume..."):
            state["resume_text"] = extract_resume_text(resume_file)
            state["job_role"] = job_role
            state["job_description"] = job_description or f"Standard {job_role} position"
            state["num_questions"] = num_questions
            state["difficulty"] = difficulty
            state["q_types"] = ", ".join(q_types) if q_types else "Technical, Behavioral, Situational"
        with st.spinner("Generating tailored interview questions..."):
            state["questions"] = generate_questions(
                state["resume_text"], job_role, state["job_description"],
                num_questions, difficulty, state["q_types"])
            state["stage"] = "interview"
            state["current_q"] = 0
            state["answers"] = []
            state["evaluations"] = []
            state["question_phase"] = "ready"
            state["audio_bytes"] = None
        st.rerun()

# ── STAGE 2: Audio Interview ──
elif state["stage"] == "interview":
    total_qs = len(state["questions"])
    if total_qs == 0:
        st.error("No questions generated. Please restart.")
        if st.button("🔄 Restart"):
            state["stage"] = "upload"
            st.rerun()
    else:
        idx = state["current_q"]
        q = state["questions"][idx]
        phase = state.get("question_phase", "ready")

        # Progress bar
        st.progress(idx / total_qs, text=f"Question {idx + 1} of {total_qs}")

        # Question card
        with st.container(border=True):
            st.markdown(f"**Q{idx+1}** · {q.get('type','general').upper()} · Focus: {q.get('focus','General')}")
            st.markdown(f"### {q['question']}")

        # ── Phase: READY ──
        if phase == "ready":
            st.info("📖 Read the question above carefully. When you're ready, click below to start your **30-second think time**, after which recording will begin.")
            if st.button("🎯 I'm Ready", type="primary", use_container_width=True):
                state["question_phase"] = "thinking"
                state["audio_bytes"] = None
                st.rerun()

        # ── Phase: THINKING (30s countdown) ──
        elif phase == "thinking":
            st.warning("🧠 **THINK TIME** — Organize your thoughts. Recording starts after the countdown!")
            render_countdown_timer(30, "⏳ Think Time — Prepare Your Answer")
            state["question_phase"] = "recording"
            st.rerun()

        # ── Phase: RECORDING ──
        elif phase == "recording":
            render_recording_timer_js()
            st.markdown("##### 🎙️ Click the microphone to start recording. Click stop when finished. Max **90 seconds**.")
            audio_data = st.audio_input("Record your answer", key=f"audio_q{idx}")

            # Auto-advance when audio is captured (user clicked stop)
            if audio_data is not None:
                state["audio_bytes"] = audio_data.getvalue()
                state["question_phase"] = "processing"
                st.rerun()
            
            # Manual skip option
            if st.button("⏭️ Skip This Question", use_container_width=True):
                state["answers"].append("[Skipped]")
                state["evaluations"].append({"score": 0, "feedback": "Skipped", "strengths": [], "improvements": [], "technical_accuracy": "N/A", "communication": "N/A"})
                if idx == total_qs - 1:
                    state["stage"] = "results"
                    state["question_phase"] = "ready"
                else:
                    state["current_q"] += 1
                    state["question_phase"] = "ready"
                state["audio_bytes"] = None
                st.rerun()

        # ── Phase: PROCESSING (auto-transcribe + auto-evaluate) ──
        elif phase == "processing":
            audio_bytes = state.get("audio_bytes")
            if not audio_bytes:
                st.error("No audio captured. Please try again.")
                if st.button("🔁 Try Again"):
                    state["question_phase"] = "recording"
                    st.rerun()
            else:
                # Transcribe
                with st.spinner("🔄 Transcribing your answer..."):
                    transcript = transcribe_audio(audio_bytes, audio_backend)

                if not transcript:
                    st.error("❌ Transcription failed. Please re-record.")
                    if st.button("🔁 Try Again"):
                        state["question_phase"] = "recording"
                        state["audio_bytes"] = None
                        st.rerun()
                else:
                    st.success("✅ Transcription complete!")
                    with st.container(border=True):
                        st.markdown("**Your Answer (Transcribed):**")
                        st.write(transcript)

                    # Evaluate
                    with st.spinner("🤖 AI is evaluating your answer..."):
                        eval_result = evaluate_answer(q['question'], transcript, state["resume_text"])

                    state["answers"].append(transcript)
                    state["evaluations"].append(eval_result)

                    # Show evaluation
                    sc = eval_result.get("score", "N/A")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Score", f"{sc}/10")
                    with col2:
                        st.metric("Technical", str(eval_result.get("technical_accuracy", "N/A")).title())
                    with col3:
                        st.metric("Communication", str(eval_result.get("communication", "N/A")).title())

                    st.markdown(f"**Feedback:** {eval_result.get('feedback', 'N/A')}")

                    # Auto-advance to next question after 3 seconds
                    progress_placeholder = st.empty()
                    for i in range(3, 0, -1):
                        progress_placeholder.info(f"⏳ Moving to next question in {i}...")
                        time.sleep(1)
                    progress_placeholder.empty()
                    
                    if idx == total_qs - 1:
                        state["stage"] = "results"
                        state["question_phase"] = "ready"
                        state["audio_bytes"] = None
                    else:
                        state["current_q"] += 1
                        state["question_phase"] = "ready"
                        state["audio_bytes"] = None
                    st.rerun()

# ── STAGE 3: Results ──
elif state["stage"] == "results":
    st.header("📊 Interview Results")
    with st.spinner("Generating comprehensive report..."):
        report = generate_final_report(state)

    score = report.get("overall_score", 0)
    verdict = report.get("verdict", "N/A")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{score}/100")
    with col2:
        vc = {"Strong Hire": "🟢", "Hire": "🟢", "Consider": "🟡", "No Hire": "🔴"}
        st.metric("Verdict", f"{vc.get(verdict, '')} {verdict}")
    with col3:
        avg = sum(e.get("score", 0) for e in state["evaluations"]) / max(len(state["evaluations"]), 1)
        st.metric("Avg Question Score", f"{avg:.1f}/10")

    st.divider()
    st.subheader("📋 Executive Summary")
    st.write(report.get("summary", "No summary available"))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Key Strengths")
        for s in report.get("key_strengths", []):
            st.write(f"• {s}")
    with col2:
        st.subheader("⚠️ Areas for Improvement")
        for g in report.get("key_gaps", []):
            st.write(f"• {g}")

    st.subheader("📝 Detailed Feedback")
    st.write(report.get("detailed_feedback", "N/A"))

    if report.get("recommended_resources"):
        st.subheader("📚 Recommended Resources")
        for r in report["recommended_resources"]:
            st.write(f"• {r}")

    if report.get("next_steps"):
        st.subheader("🎯 Next Steps")
        st.write(report["next_steps"])

    with st.expander("🔍 Question-by-Question Breakdown"):
        for i, (q, a, e) in enumerate(zip(state["questions"], state["answers"], state["evaluations"])):
            st.markdown(f"**Q{i+1} [{q.get('type','general')}]:** {q['question']}")
            st.markdown(f"*Your Answer:* {a[:300]}{'...' if len(a) > 300 else ''}")
            st.markdown(f"*Score:* {e.get('score','N/A')}/10 | *Technical:* {e.get('technical_accuracy','N/A')} | *Communication:* {e.get('communication','N/A')}")
            st.markdown(f"*Feedback:* {e.get('feedback','N/A')}")
            st.divider()

    # Download report
    report_text = f"""AI HR INTERVIEW REPORT
========================
Role: {state['job_role']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Score: {score}/100 | Verdict: {verdict}

SUMMARY:\n{report.get('summary','')}

KEY STRENGTHS:\n{chr(10).join('• '+s for s in report.get('key_strengths',[]))}

GAPS:\n{chr(10).join('• '+g for g in report.get('key_gaps',[]))}

FEEDBACK:\n{report.get('detailed_feedback','')}

RESOURCES:\n{chr(10).join('• '+r for r in report.get('recommended_resources',[]))}

NEXT STEPS:\n{report.get('next_steps','')}

---\nQUESTION BREAKDOWN:\n"""
    for i, (q, a, e) in enumerate(zip(state["questions"], state["answers"], state["evaluations"])):
        report_text += f"\nQ{i+1}: {q['question']}\nAnswer: {a}\nScore: {e.get('score','N/A')}/10\nFeedback: {e.get('feedback','N/A')}\n"

    st.download_button("📥 Download Full Report", report_text,
        file_name=f"interview_{state['job_role'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")

    if st.button("🔄 New Interview", use_container_width=True):
        st.session_state.interview_state = {
            "stage": "upload", "resume_text": "", "job_role": "", "job_description": "",
            "questions": [], "current_q": 0, "answers": [], "evaluations": [],
            "question_phase": "ready", "audio_bytes": None,
            "num_questions": 5, "difficulty": "Progressive", "q_types": "Technical, Behavioral, Situational",
        }
        st.rerun()

# ── Sidebar Info ──
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    **Audio-First AI Interviewer:**
    - 📄 Parses resume (PDF/DOCX)
    - 🎯 Generates role-specific questions
    - ⏳ 30s think time before each question
    - 🎙️ 90s audio recording per answer
    - 🔄 Auto-transcription (Whisper AI)
    - 🤖 Real-time AI evaluation
    - 📊 Full report with verdict
    """)
    st.divider()
    backend = st.session_state.get("current_backend", "None")
    st.caption(f"Backend: {backend}")
    if st.session_state.get("ai_hr"):
        st.success("✅ AI Connected")
    else:
        st.warning("⚠️ AI Offline — Transcription still works via Local Whisper")