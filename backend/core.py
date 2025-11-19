from dotenv import load_dotenv
from langchain.chains.retrieval import create_retrieval_chain
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAI


load_dotenv()

INDEX_NAME = "documentation-helper"

def run_llm(query:str):
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    docsearch = PineconeVectorStore(index_name=INDEX_NAME,embedding=embeddings)
    chat = GoogleGenerativeAI( model="gemini-2.5-flash")

    retrival_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    stuff_documents_chain = create_stuff_documents_chain(chat,retrival_qa_chat_prompt)

    qa = create_retrieval_chain(
        retriever=docsearch.as_retriever(),combine_docs_chain=stuff_documents_chain
    )

    result = qa.invoke(input={"input":query})
    new_result = {
        "query":result["input"],
        "result":result["answer"],
        "source_documents":result["context"]
    }
    return new_result

if __name__ == "__main__":
    res = run_llm(query="What is a LangChain Chain?")
    print(res["result"])