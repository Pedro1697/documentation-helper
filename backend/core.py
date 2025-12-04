from dotenv import load_dotenv
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever 
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from typing import Dict,Any,  List

load_dotenv()

INDEX_NAME = "documentation-helper"

def run_llm(query:str,chat_history:List[Dict[str,Any]]):
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    docsearch = PineconeVectorStore(index_name=INDEX_NAME,embedding=embeddings)
    chat = GoogleGenerativeAI( model="gemini-2.5-flash")

    retrival_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    stuff_documents_chain = create_stuff_documents_chain(chat,retrival_qa_chat_prompt)

    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    history_aware_retriever = create_history_aware_retriever(
        llm=chat,retriever=docsearch.as_retriever(),prompt=rephrase_prompt
    )

    qa = create_retrieval_chain(
        retriever=history_aware_retriever,combine_docs_chain=stuff_documents_chain
    )

    result = qa.invoke(input={"input":query,"chat_history":chat_history})
    new_result = {
        "query":result["input"],
        "result":result["answer"],
        "source_documents":result["context"]
    }
    return new_result

if __name__ == "__main__":
    res = run_llm(query="What is a LangChain Chain?")
    print(res["result"])