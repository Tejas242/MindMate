# MindMate – AI Early-Intervention Companion for Student Mental Health

## 👨‍💻 Team – HackHustlers
## 🌟 Overview
**MindMate** is an AI-powered, privacy-first mental health companion built for **students and campuses**.  
Unlike generic wellness chatbots, MindMate is **campus-ready, culturally aware, and ethically designed** — bridging the gap between students, counsellors, and institutions.

---

## 🚨 The Problem
- 1B+ people globally live with mental health conditions, students are the most affected.
- 80% of campuses lack adequate support & counsellors.
- Barriers: stigma, lack of privacy, limited access, poor digital fit in low-resource settings.
- Existing tools (Wysa, Woebot) are consumer-first, not campus-first.

---

## 💡 Our Solution
MindMate delivers **early, anonymous, and scalable intervention**:
1. **Anonymous Chat** – empathetic AI companion for early screening.  
2. **Dynamic Risk Scoring** – maps conversations to PHQ-2/9, GAD-7 standards.  
3. **Micro-Interventions** – quick exercises (CBT-style prompts, breathing, journaling).  
4. **Safe Escalation** – connect students with campus counsellors/hotlines when risk is high.  
5. **Counsellor Dashboard** – explainable summaries with AI confidence levels.  
6. **Campus Insights (Future)** – anonymized trend data for institutions.  

---

## 🧠 Why AI?
- **Empathic Dialogue** – LLM for natural, stigma-free conversations.  
- **Risk Scoring** – automated, explainable, auditable.  
- **Personalization** – context-aware, culturally adapted interventions.  
- **Explainability Layer** – ensures safety & trust.  
- **Campus Integration** – retrieval of localized resources (helplines, events).  

---

## 🎯 Hackathon MVP Features
- Conversational AI chat with a student-friendly persona.
- 5–7 validated screening questions + risk scoring.
- Library of 6 micro-interventions (text-based).
- Crisis escalation trigger → hotline / counsellor connect.
- Counsellor dashboard → explainable risk snapshots.

---

## 🚀 Tech Stack

### Frontend
- **React + TailwindCSS** → clean, fast UI.
- **Vite** → fast builds.
- **Framer Motion** → smooth animations for UX polish.

### Backend
- **FastAPI (Python)** → lightweight, async, easy API layer.
- **PostgreSQL** (optional for demo: SQLite) → stores anonymized session data.
- **Redis (optional)** → caching sessions if time allows.

### AI/LLM
- **OpenAI API / Hugging Face Hub** → hosted LLM integration.
- **Rule-based safety layer** → to filter/validate responses.
- **RAG (Retrieval-Augmented Generation)** → surface local resources (hotlines/events).

### Deployment
- **Dockerized** (easy portability).
- **Railway / Render / Vercel** → quick deploy for demo.

### Testing & Quality
- **Pytest** for backend tests.
- **Jest + React Testing Library** for frontend.
- **ESLint + Prettier** → code consistency.

---

## 🏗 Directory Structure
```bash
mindmate/
│── README.md
│── package.json # Frontend deps
│── requirements.txt # Backend deps
│── docker-compose.yml # For containerized setup
│── .env.example # Env variables template
│
├── frontend/ # React frontend
│ ├── src/
│ │ ├── components/ # UI components
│ │ ├── pages/ # Chat, Dashboard
│ │ ├── hooks/ # Custom hooks
│ │ ├── utils/ # Helpers
│ │ └── App.jsx
│ └── public/
│
├── backend/ # FastAPI backend
│ ├── app/
│ │ ├── main.py # Entry point
│ │ ├── api/ # Route handlers
│ │ │ ├── chat.py
│ │ │ ├── risk.py
│ │ │ └── counsellor.py
│ │ ├── core/ # Config, security
│ │ ├── models/ # DB models
│ │ ├── services/ # LLM, scoring logic
│ │ ├── utils/ # Helpers
│ │ └── tests/ # Unit tests
│ └── Dockerfile
│
├── database/
│ ├── schema.sql # Initial schema
│ └── migrations/ # Future migrations
│
├── docs/ # Pitch + design docs
│ ├── wireframes/
│ └── architecture.md
│
└── scripts/ # Deployment, setup scripts
```

---

## 📊 Competitive Advantage
- **Campus-first** → designed for institutions, not just individuals.
- **Culturally aware** → beyond translations, interventions fit local context.
- **Privacy-first** → anonymized sessions, explainable outputs.
- **Low-bandwidth ready** → text-first design, offline fallback.

---

## 🎤 Pitch One-Liner
> “While others stop at a chatbot, **MindMate creates a safe ecosystem** connecting students, AI, and counsellors — campus-first, culturally aware, and explainable.”

---

## 🛠 Setup Instructions

### 1. Clone Repo
```bash
git clone https://github.com/hackhustlers/mindmate.git
cd mindmate
```
### 2. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)
pip install -r requirements.txt
uvicorn app.main:app --reload
```
### 3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
### 4. Environment Variables
Create .env file:
```bash
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./mindmate.db
```

---

## 📌 Future Roadmap
- Offline-first fallback (preloaded interventions).
- Multilingual support.
- Analytics for campus trends.
- Voice-based interaction.
- Institutional portal.
---

### 🔹 Scalable Product Roadmap (Post-Hackathon)

#### Frontend Enhancements
- **react-i18next** → multilingual + culturally adapted interventions.  
- **PWA (Progressive Web App)** → offline-first fallback for low-bandwidth campuses.  

#### Backend Enhancements
- **Celery / RQ** → background tasks (risk scoring, notifications).  
- **PostgreSQL with migrations** → robust production database.  
- **Kubernetes / AWS Fargate** → scalable infra for institutional rollout.  

#### AI/LLM Enhancements
- **LangChain / LlamaIndex** → modular orchestration of RAG, safety, and explainability.  
- **Fine-tuned LLMs** → domain adaptation for student conversations.  
- **Explainability module** → “why this risk score?” transparency for counsellors.  

#### Security & Privacy
- **End-to-end encryption** for chat sessions.  
- **Audit logs + monitoring** → Sentry, Prometheus, Grafana.  
- **GDPR & HIPAA-inspired compliance layer** → for institutional trust.  

#### Testing & Monitoring
- **Playwright / Cypress** → end-to-end UX testing.  
- **CI/CD pipelines** → automated tests, deployments.  



## 🏗 Directory Structure
