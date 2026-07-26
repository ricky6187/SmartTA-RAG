import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Import Services
from service.rag_service import answer_question_from_rag, Answer
from service.quiz_service import generate_quiz_from_docs, Quiz


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Please set GEMINI_API_KEY in .env!")

app = FastAPI(title="AI Course TA System API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# global var (in-memo)
vectorstore = None
raw_docs = []

# 初始化 Embedding 與 LLM
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key
)

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=api_key,
    temperature=0.2
)

# Request Pydantic Model
# define the body from frontend
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

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed!")

    temp_pdf_path = f"temp_{file.filename}"
    # create a file and save the uploaded pdf to this file
    with open(temp_pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Load PDF
        loader = PyPDFLoader(temp_pdf_path)
        raw_docs = loader.load()

        # Split Document
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150, # 15% - 20%
            separators=["\n\n", "\n", "。", ".", " ", ""] # separate at these first
        )
        chunks = text_splitter.split_documents(raw_docs)

        # Store in ChromaDB (In-Memory)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
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

# define the data from backend to frontend must like Answer structure (in quiz_service.py)
@app.post("/api/chat", response_model=Answer)
# put the json from frontend to var called request with type ChatRequest (define above)
async def chat(request: ChatRequest): 
    """RAG Question Answering Endpoint."""
    global vectorstore, llm

    if vectorstore is None:
        raise HTTPException(status_code=400, detail="please upload pdf file first!")

    try:
        # Calls rag_service and directly returns the Answer Pydantic object
        result = answer_question_from_rag(
            user_query=request.question,
            vectorstore=vectorstore,
            llm=llm
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz", response_model=Quiz)
async def generate_quiz():
    """Generates a 3-question MCQ Quiz in structured JSON format."""
    global raw_docs, llm

    if not raw_docs:
        raise HTTPException(status_code=400, detail="please upload pdf file first!")

    try:
        # Calls quiz_service and directly returns the Quiz Pydantic object
        quiz_data = generate_quiz_from_docs(docs=raw_docs, llm=llm, num_questions=5)
        return quiz_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))