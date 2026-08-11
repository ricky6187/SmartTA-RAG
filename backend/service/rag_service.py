from pydantic import BaseModel, Field

class Answer(BaseModel):
    answer: str = Field(description="answer in trad. chinese with page citation")

def answer_question_from_rag(user_query: str, vectorstore, llm) -> Answer:
    # find most 5 relevant chunks
    retriever = vectorstore.as_retriever(
    search_type="mmr", # avoid all the same
    search_kwargs={
        "k": 5, # final no. of chunk
        "fetch_k": 10, # first fetch no. and filter most different
        "lambda_mult": 0.7 # 1.0 = more the same. 0 = most different
        }
    )
    relevant_docs = retriever.invoke(user_query)

    context_text = "\n\n---\n\n".join([
        f"[from page {doc.metadata.get('page', 0) + 1} ]:\n{doc.page_content}"
        for doc in relevant_docs
    ])

    structured_llm = llm.with_structured_output(Answer)

    prompt = f"""
    You are a TA in a university course. Please answer the following question with the following information
    if the information does not help. Please answer "not mentioned"

    information: {context_text}
    question: {user_query}
    format: answer the qusetion in trad. chinese and with citation (eg. [page x])
    """

    return structured_llm.invoke(prompt)

# embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# vectorstore = Chroma.from_documents(
#     documents=chunks,
#    embedding=embeddings
#)
