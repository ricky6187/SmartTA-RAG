from typing import List
from pydantic import BaseModel, Field
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_google_genai import ChatGoogleGenerativeAI


def generate_quiz_from_docs(docs, llm, num_questions=5):
    # feed all pages
    context_text = "\n\n".join([
    f"[Page {doc.metadata.get('page', 0) + 1}]:\n{doc.page_content}"
    for doc in docs
    ])

    structured_llm = llm.with_structured_output(Quiz)

    prompt = f"""
    You are a university course teaching assistant. Please design {num_questions} high-quality multiple-choice questions (single-choice) based on the following lecture notes to test the students' level of understanding.
    [Notes]:Questions and options must be strictly based on the lecture notes.Questions and explanations must use "Traditional Chinese".Each question must provide 4 options (A, B, C, D).
    You must include the page citation (page_citation) where the correct answer is referenced in the lecture notes.
    lecture notes:
    {context_text}
    """
    return structured_llm.invoke(prompt)


# define json data structure (Pydantic Schema
class MCQ(BaseModel):
    # = field() give prompt to ai
    id: int = Field(description="Question number starting from 1")
    question: str = Field(description="The question in trad. chinese")
    # eg. ["opt1", "opt2"]
    options: List[str] = Field(description="4 options, eg. ['...', '...', '...', '...']")
    answer: int = Field(description="The index of correct answer eg. '0', '1', '2', or '3'")
    explanation: str = Field(description="The explaination of the answer in trad. chinese")
    page_citation: int = Field(description="the page the question related (eg. 15)")

class Quiz(BaseModel):
    questions: List[MCQ] = Field(description="multiple choice question list")


# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.5-flash",
#     google_api_key=api_key,
#     temperature=0.3
# )


# print("generating 3 questions")
# response = structured_llm.invoke(prompt)

# print("\n generated json data")
# print("=" * 50)

# quiz_json = response.model_dump_json(indent=2)
# print(quiz_json)
# print("=" * 50)
