# AI Tutor: Coursework RAG & Quiz Generator

This tool allows students to query course materials with source citations and enables instructors/TAs to auto-generate quizzes from lecture slides.

---
<img width="1148" height="795" alt="image" src="https://github.com/user-attachments/assets/3a75ab6a-4760-456e-a332-369d4d1886a4" />

## Core Features

1. **Coursework Knowledge Base (RAG & Source Citation)**
   - Upload course syllabus, lecture slides (PDF/Markdown).
   - Context-aware QA with direct page/paragraph citations to prevent hallucination.

2. **AI Quiz & Flashcard Generator**
   - Auto-generate multiple-choice questions (MCQs) and quiz from lecture note.
   - Structured JSON outputs for interactive test-taking and immediate feedback.

---

## Tech Stack (Target)

- **Frontend:** React, Vite
- **Backend:** Python (FastAPI)
- **AI & RAG:** GEMINI API / LangChain, ChromaDB (Vector Store)

## How to Run (You might need a VPN to use gemini api)

1. Create a venv

2. `cd backend` then run `pip install -r requirements.txt`

3. Create a `.env` file inside `backend/` and fill in your own `GEMINI_API_KEY`

4. Inside `backend/`, run `uvicorn main:app --reload`

5. `cd frontend`

6. `npm install`

7. `npm run dev`


