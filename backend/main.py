import os
import sys
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

print(f"Python {sys.version} | Starting up...")

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("FATAL: GEMINI_API_KEY is missing!")
    raise ValueError("Please set GEMINI_API_KEY in .env!")

print("API key found")

app = FastAPI(title="AI Course TA System API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://smartta-rag-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

# global var (in-memo)
vectorstore = None
raw_docs = []
embeddings = None
llm = None


def _init_embeddings():
    global embeddings
    if embeddings is None:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print("Initializing embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        print("Embeddings initialized OK")
    return embeddings


def _init_llm():
    global llm
    if llm is None:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("Initializing LLM...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=api_key,
            temperature=0.2
        )
        print("LLM initialized OK")
    return llm


# Request Pydantic Model
class ChatRequest(BaseModel):
    question: str


# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "AI Course TA System API is running!"}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Receives uploaded PDF, splits text, and builds in-memory ChromaDB."""
    global vectorstore, raw_docs

    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed!")

    temp_pdf_path = f"temp_{file.filename}"
    with open(temp_pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        loader = PyPDFLoader(temp_pdf_path)
        raw_docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(raw_docs)

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=_init_embeddings()
        )

        os.remove(temp_pdf_path)

        return {
            "status": "success",
            "filename": file.filename,
            "total_pages": len(raw_docs),
            "total_chunks": len(chunks)
        }

    except Exception as e:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=None)
async def chat(request: ChatRequest):
    """RAG Question Answering Endpoint."""
    global vectorstore

    from service.rag_service import answer_question_from_rag

    if vectorstore is None:
        raise HTTPException(status_code=400, detail="please upload pdf file first!")

    try:
        result = answer_question_from_rag(
            user_query=request.question,
            vectorstore=vectorstore,
            llm=_init_llm()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz", response_model=None)
async def generate_quiz():
    """Generates a 5-question MCQ Quiz in structured JSON format."""
    global raw_docs

    from service.quiz_service import generate_quiz_from_docs

    if not raw_docs:
        raise HTTPException(status_code=400, detail="please upload pdf file first!")

    try:
        quiz_data = generate_quiz_from_docs(docs=raw_docs, llm=_init_llm(), num_questions=5)
        return quiz_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

print("App module loaded successfully, ready for uvicorn")
