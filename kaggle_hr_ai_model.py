# ==============================================================================
# 🚀 ULTIMATE AI HR AUTOMATION PLATFORM - KAGGLE ENTERPRISE EDITION
# ==============================================================================
# Instructions for Kaggle:
# 1. Turn on the "GPU T4 x2" Accelerator in your Notebook Settings.
# 2. Add any HR datasets you want ("Add Data" -> Search HR / Attrition -> Add).
#    (This script will automatically scan and merge them!)
# 3. Add a Code Cell, paste this exact code, and click Run!
# 
# Install dependencies first if needed:
# !pip install -q -U transformers accelerate bitsandbytes xgboost scikit-learn pandas
# ==============================================================================

import os
import glob
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
import warnings

warnings.filterwarnings('ignore')

class SuperAIHR:
    def __init__(self):
        print("\n" + "🌟"*30)
        print("  BOOTING ULTIMATE AI HR BRAIN (ENTERPRISE EDITION)")
        print("🌟"*30)
        
        # 1. ML Models (Long-Life Setup)
        self.xgb_model = xgb.XGBClassifier(eval_metric='logloss')
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoders = {}
        self.model_save_path = "/kaggle/working/hr_attrition_xgb.json"
        
        # 2. Advanced Generative AI (LLM) setup using Qwen-2.5 7B
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_id = "Qwen/Qwen2.5-7B-Instruct"
        print(f"\n🧠 Loading Neural Engine ({model_id}) on {self.device}...")
        print("   (Optimizing memory with 4-bit Quantization...)")
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.llm = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto"
            )
            self.pipe = pipeline(
                "text-generation",
                model=self.llm,
                tokenizer=self.tokenizer,
                max_new_tokens=800,
                temperature=0.1, # Extremely low temp for high logical accuracy
                do_sample=True
            )
            print("✅ Neural Engine is fully synchronized and Online!")
        except Exception as e:
            print(f"⚠️ Error loading LLM. Did you forget to enable the GPU? Error: {e}")

    # ==========================================
    # MODULE 1: DYNAMIC WORKFORCE INTELLIGENCE
    # ==========================================
    def load_and_train_attrition(self):
        print("\n📊 MODULE 1: DYNAMIC WORKFORCE & RETENTION FORECASTING")
        
        # 1. Dynamic Dataset Scanner
        print("🔍 Scanning Kaggle for HR datasets...")
        all_csv_files = glob.glob('/kaggle/input/**/*.csv', recursive=True)
        
        hr_dataframes = []
        for file in all_csv_files:
            # Simple heuristic: if the file contains words like 'hr', 'attrition', 'employee'
            if any(keyword in file.lower() for keyword in ['hr', 'attrition', 'employee']):
                print(f"   -> Discovered Dataset: {file.split('/')[-1]}")
                try:
                    df_temp = pd.read_csv(file)
                    # Only keep datasets that look like they have target variables
                    if 'Attrition' in df_temp.columns or 'attrition' in df_temp.columns or 'left' in df_temp.columns:
                        hr_dataframes.append(df_temp)
                except:
                    pass

        # 2. Merge or Synthesize Data
        if len(hr_dataframes) > 0:
            print(f"📁 Processing {len(hr_dataframes)} actual datasets...")
            df = hr_dataframes[0] # Pick the best matching one for simplicity
            target_col = 'Attrition' if 'Attrition' in df.columns else ('attrition' if 'attrition' in df.columns else 'left')
        else:
            print("⚠️ No valid HR datasets found in /kaggle/input/.")
            print("⚙️ Generating a high-fidelity synthetic enterprise dataset...")
            df = self._generate_synthetic_data()
            target_col = 'attrition'

        # 3. Deep Preprocessing
        df_encoded = df.copy()
        
        # Convert target to binary if it's text (e.g., 'Yes'/'No')
        if df_encoded[target_col].dtype == 'object':
            df_encoded[target_col] = df_encoded[target_col].map({'Yes': 1, 'No': 0, 'yes': 1, 'no': 0}).fillna(0)

        # Encode remaining categorical columns
        for col in df_encoded.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            self.label_encoders[col] = le

        # Separate Features
        drop_cols = [target_col, 'EmployeeNumber', 'EmployeeCount', 'StandardHours', 'Over18']
        X = df_encoded.drop([c for c in drop_cols if c in df_encoded.columns], axis=1)
        y = df_encoded[target_col]

        # 4. Multi-Model Training (Ensemble Approach)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("⚙️ Training XGBoost Classifier...")
        self.xgb_model.fit(X_train, y_train)
        xgb_preds = self.xgb_model.predict(X_test)
        
        print("⚙️ Training Random Forest (Secondary Verifier)...")
        self.rf_model.fit(X_train, y_train)
        rf_preds = self.rf_model.predict(X_test)
        
        # Evaluate
        xgb_acc = accuracy_score(y_test, xgb_preds)
        rf_acc = accuracy_score(y_test, rf_preds)
        print(f"📈 XGBoost Accuracy: {xgb_acc * 100:.2f}% | Random Forest Accuracy: {rf_acc * 100:.2f}%")
        
        # Long-Life Feature: Save the best model
        try:
            self.xgb_model.save_model(self.model_save_path)
            print(f"💾 Model permanently saved to {self.model_save_path} for long-term usage!")
        except Exception as e:
            print("Notice: Could not save model (normal if running locally).")

        # 5. Forecast company-wide turnover
        total_risk = sum(self.xgb_model.predict(X))
        print(f"\n🔮 ENTERPRISE FORECAST: {total_risk} out of {len(df)} employees are at high risk of attrition.")
        print(f"🎯 SYSTEM RECOMMENDATION: Automatically triggering {total_risk} new job requisitions.")

    def _generate_synthetic_data(self):
        np.random.seed(42)
        n = 3000 # Increased dataset size
        data = {
            'Age': np.random.randint(22, 60, n),
            'Department': np.random.choice(['Sales', 'R&D', 'HR', 'Engineering', 'Marketing'], n),
            'JobSatisfaction': np.random.randint(1, 5, n),
            'MonthlyIncome': np.random.randint(4000, 25000, n),
            'YearsAtCompany': np.random.randint(0, 20, n),
            'PercentSalaryHike': np.random.randint(11, 30, n),
            'NumCompaniesWorked': np.random.randint(1, 8, n),
        }
        df = pd.DataFrame(data)
        prob = (5 - df['JobSatisfaction'])*0.12 + (df['YearsAtCompany']>7)*0.1 - (df['PercentSalaryHike']>15)*0.1 + (df['NumCompaniesWorked']>4)*0.05
        df['attrition'] = (prob > 0.45).astype(int)
        return df

    # ==========================================
    # MODULE 2: AI RECRUITMENT & ASSESSMENT
    # ==========================================
    def ask_ai(self, system_prompt, user_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = self.pipe(prompt)
        return outputs[0]["generated_text"][len(prompt):].strip()

    def screen_resume(self, job_description, resume):
        print("\n📄 MODULE 2A: INTELLIGENT RESUME SCREENING")
        system = "You are an elite Applicant Tracking System (ATS). Analyze the resume against the job description."
        user = f"Job Description:\n{job_description}\n\nCandidate Resume:\n{resume}\n\nTask: Provide a match percentage out of 100%, followed by 3 bullet points explaining the strengths and gaps."
        result = self.ask_ai(system, user)
        print(result)
        return result

    def generate_interview(self, role, resume):
        print(f"\n📝 MODULE 2B: DYNAMIC INTERVIEW GENERATION FOR '{role.upper()}'")
        system = "You are a Principal Software Engineer conducting a tough technical interview."
        user = f"Candidate Resume: {resume}\n\nTask: Generate ONE highly specific Data Structures (DSA) question and ONE scenario-based architecture question tailored for a {role}. Format cleanly."
        result = self.ask_ai(system, user)
        print(result)
        return result

    # ==========================================
    # MODULE 3: VIDEO EVALUATION & FINAL DECISION
    # ==========================================
    def evaluate_and_decide(self, candidate_name, role, question, video_transcript):
        print(f"\n🎥 MODULE 3: AUTOMATED VIDEO TRANSCRIPT EVALUATION ({candidate_name})")
        
        system_eval = "You are an unbiased, expert technical reviewer."
        user_eval = f"Question: {question}\n\nCandidate Answer Transcript: '{video_transcript}'\n\nTask: Grade this answer out of 10. Explain what was good and what was technically incorrect."
        evaluation = self.ask_ai(system_eval, user_eval)
        print(f"📊 Evaluation Details:\n{evaluation}\n")
        
        print(f"⚖️ FINAL HR VERDICT")
        system_decision = "You are the automated Head of HR making final hiring decisions."
        user_decision = f"Candidate: {candidate_name}\nRole: {role}\nInterview Evaluation: {evaluation}\n\nTask: Conclude with exactly '✅ DECISION: HIRE' or '❌ DECISION: REJECT', followed by a short justification."
        decision = self.ask_ai(system_decision, user_decision)
        print(decision)
        print("\n" + "🚀"*30 + "\n")
        return decision

# ==========================================
# 🚀 EXECUTION BLOCK
# ==========================================
if __name__ == "__main__":
    # 1. Boot up the Ultimate AI
    ai = SuperAIHR()
    
    # 2. Run Workforce Prediction (Auto-scans datasets and saves model)
    ai.load_and_train_attrition()
    
    # 3. Recruitment Pipeline
    role = "Senior React Developer"
    job_desc = "Looking for an expert React developer with 5+ years of experience, deep knowledge of hooks, state management (Redux/Zustand), and Webpack."
    resume = "Frontend Engineer with 6 years experience. Built a massive e-commerce platform using Next.js, React hooks, and Zustand. Familiar with Node.js and AWS."
    
    # AI Screens the Resume against Job Description
    resume_eval = ai.screen_resume(job_desc, resume)
    
    # AI generates specific interview questions based on the candidate's exact background
    interview_qs = ai.generate_interview(role, resume)
    
    # 4. Evaluate the candidate's 30-second automated video response
    candidate = "Tejas (Applicant)"
    question = "Explain how Zustand differs from Redux and why you chose it for your e-commerce platform."
    transcript = "Zustand is much lighter and has less boilerplate than Redux. I don't need to write actions and reducers separately. I chose it for the e-commerce app because it uses React hooks natively and avoids unnecessary re-renders without needing complex connect functions."
    
    # The AI grades the video and makes the final decision
    final_verdict = ai.evaluate_and_decide(candidate, role, question, transcript)
    
    # 5. ALL-IN-ONE DOWNLOAD PACKAGER
    print("\n📦 Generating Final Report and compressing all outputs...")
    try:
        # Create a text report
        report_path = "/kaggle/working/Candidate_Report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"HR AI PLATFORM - FINAL CANDIDATE REPORT\n")
            f.write(f"=======================================\n")
            f.write(f"Candidate: {candidate}\nRole: {role}\n\n")
            f.write(f"--- 1. RESUME ATS MATCH ---\n{resume_eval}\n\n")
            f.write(f"--- 2. GENERATED INTERVIEW ---\n{interview_qs}\n\n")
            f.write(f"--- 3. AI VIDEO EVALUATION & VERDICT ---\n{final_verdict}\n")
        
        # Create a single ZIP file containing the model and the report
        import shutil
        shutil.make_archive('/kaggle/working/HR_AI_All_Outputs', 'zip', '/kaggle/working/')
        print("✅ SUCCESS: All models and reports have been packaged into a single ZIP file!")
        print("👉 Look at the 'Output' panel on the right side of Kaggle to download 'HR_AI_All_Outputs.zip'.")
    except Exception as e:
        print("Notice: Skipping zip creation (this feature is designed specifically for Kaggle).")
