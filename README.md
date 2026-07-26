# AI Tutor: Coursework RAG & Quiz Generator

This tool allows students to query course materials with source citations and enables instructors/TAs to auto-generate quizzes from lecture slides.

---

## Core Features

1. **Coursework Knowledge Base (RAG & Source Citation)**
   - Upload course syllabus, lecture slides (PDF/Markdown).
   - Context-aware QA with direct page/paragraph citations to prevent hallucination.

2. **AI Quiz & Flashcard Generator**
   - Auto-generate multiple-choice questions (MCQs) and quiz from lecture note.
   - Structured JSON outputs for interactive test-taking and immediate feedback.

---

## Tech Stack (Target)

- **Frontend:** React / Next.js, Tailwind CSS
- **Backend:** Python (FastAPI)
- **AI & RAG:** GEMINI API / LangChain, ChromaDB (Vector Store)
