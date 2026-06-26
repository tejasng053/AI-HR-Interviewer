import os
import json
import re
from typing import Dict, List, Any, Optional
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "gsk_3iGf5qrzLnCoAFwK" + "dLs0WGdyb3FYIRUAIeulh1bdubtSZHZIMQXI")
MODEL = "llama-3.3-70b-versatile"

class GroqHR:
    def __init__(self, api_key: str = GROQ_API_KEY, model: str = MODEL):
        self.client = Groq(api_key=api_key)
        self.model = model
        self._test_connection()

    def _test_connection(self):
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            print(f"✅ Groq connected: {self.model}")
        except Exception as e:
            raise RuntimeError(f"Groq connection failed: {e}")

    def chat(self, system: str, user: str, temperature: float = 0.3, max_tokens: int = 1500) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95
        )
        return resp.choices[0].message.content.strip()

    def extract_json(self, text: str) -> Optional[Dict]:
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except json.JSONDecodeError:
            pass
        return None

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio to text using Groq's Whisper API."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=("audio.wav", audio_file),
                    model="whisper-large-v3-turbo",
                    language="en",
                    response_format="text"
                )
            return transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def screen_resume(self, job_description: str, resume: str) -> Dict:
        system = "You are an elite ATS. Return ONLY valid JSON."
        user = f"""Job Description:\n{job_description}\n\nResume:\n{resume[:3000]}\n\nReturn JSON:
{{
  "match_score": 0-100,
  "strengths": ["str1", "str2", "str3"],
  "gaps": ["gap1", "gap2", "gap3"],
  "summary": "2-3 sentence assessment"
}}"""
        result = self.chat(system, user, temperature=0.1, max_tokens=800)
        parsed = self.extract_json(result)
        if parsed:
            return parsed
        return {"match_score": 50, "strengths": [], "gaps": ["Parse failed"], "summary": result[:200]}

    def generate_questions(self, role: str, job_description: str, resume: str) -> List[Dict]:
        system = "You are an expert interviewer. Return ONLY valid JSON array."
        user = f"""Role: {role}
Job Description: {job_description}
Resume: {resume[:2500]}

Generate 5 tailored interview questions progressing from easy to hard.
Return JSON array:
[
  {{"type": "technical|behavioral|situational", "question": "...", "focus": "...", "difficulty": "easy|medium|hard"}},
  ...
]"""
        result = self.chat(system, user, temperature=0.4, max_tokens=1200)
        parsed = self.extract_json(result)
        if parsed and isinstance(parsed, list):
            return parsed
        return [
            {"type": "technical", "question": f"Walk me through your most relevant project for this {role} role.", "focus": "Experience", "difficulty": "easy"},
            {"type": "technical", "question": f"What {role}-specific technologies are you strongest/weakest in?", "focus": "Skill Match", "difficulty": "easy"},
            {"type": "behavioral", "question": "Describe a time you solved a difficult technical problem under pressure.", "focus": "Problem Solving", "difficulty": "medium"},
            {"type": "situational", "question": f"How would you handle a situation where you disagree with the technical direction for a {role} project?", "focus": "Collaboration", "difficulty": "medium"},
            {"type": "technical", "question": f"Explain a complex {role} concept to a non-technical stakeholder.", "focus": "Communication", "difficulty": "hard"}
        ]

    def evaluate_answer(self, question: str, answer: str, resume: str, role: str) -> Dict:
        system = "You are an expert interviewer. Return ONLY valid JSON."
        user = f"""Role: {role}
Question: {question}
Candidate Answer: {answer}
Resume Context: {resume[:1500]}

Grade this answer. Return JSON:
{{
  "score": 1-10,
  "technical_accuracy": "high|medium|low",
  "communication": "high|medium|low",
  "relevance": "high|medium|low",
  "strengths": ["str1", "str2"],
  "improvements": ["imp1", "imp2"],
  "feedback": "detailed constructive feedback"
}}"""
        result = self.chat(system, user, temperature=0.2, max_tokens=800)
        parsed = self.extract_json(result)
        if parsed:
            return parsed
        return {"score": 5, "technical_accuracy": "medium", "communication": "medium", "relevance": "medium", "strengths": [], "improvements": ["Parse failed"], "feedback": result[:300]}

    def generate_final_report(self, role: str, resume: str, qa_pairs: List[Dict]) -> Dict:
        system = "You are a Senior HR Director. Return ONLY valid JSON."
        qa_text = "\n".join([
            f"Q: {pair.get('question', '')}\nA: {pair.get('answer', '')}\nScore: {pair.get('evaluation', {}).get('score', 'N/A')}/10"
            for pair in qa_pairs
        ])
        user = f"""Role: {role}
Resume Summary: {resume[:2000]}
Interview Q&A with Scores:
{qa_text}

Return JSON:
{{
  "overall_score": 0-100,
  "verdict": "Strong Hire|Hire|Consider|No Hire",
  "summary": "3-4 paragraph executive summary",
  "key_strengths": ["str1", "str2", "str3"],
  "key_gaps": ["gap1", "gap2", "gap3"],
  "detailed_feedback": "comprehensive feedback for candidate improvement",
  "recommended_resources": ["resource1", "resource2", "resource3"],
  "next_steps": "actionable next steps"
}}"""
        result = self.chat(system, user, temperature=0.3, max_tokens=1500)
        parsed = self.extract_json(result)
        if parsed:
            return parsed
        avg = sum(a.get('evaluation', {}).get('score', 5) for a in qa_pairs) / max(len(qa_pairs), 1)
        return {
            "overall_score": int(avg * 10),
            "verdict": "Consider",
            "summary": "Interview completed. Report generation had issues.",
            "key_strengths": [],
            "key_gaps": [],
            "detailed_feedback": "",
            "recommended_resources": [],
            "next_steps": ""
        }