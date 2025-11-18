import asyncio
import os
import ssl
from typing import Any, Dict, List
import certifi
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_tavily import TavilyCrawl, TavilyExtract, TavilyMap
from logger import *
from langchain_ollama import OllamaEmbeddings


load_dotenv()


# Configure SSL context to use certifi cerfificates
ssl_context=ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUEST_CA_BUNDLE"]=certifi.where()

embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vectorestore=PineconeVectorStore(index_name="documentation-helper",embedding=embeddings)
tavily_extract = TavilyExtract()
tavily_map = TavilyMap(max_depth=5,max_breadth=20,max_pages=1000)
tavily_crawl = TavilyCrawl()

async def index_documents_async(documents: List[Document], batch_size: int = 50):
        """Process documents in batches asynchronously"""
        log_header("VECTOR STORAGE PHASE")
        log_info(
            f"VectoreStore Indexing: Preparing to add {len(documents)} documents to vector store",
            Colors.DARKCYAN,
        )

        # Create batches
        batches = [
             documents[i : i+batch_size] for i in range(0,len(documents),batch_size)
        ] 

        log_info(
             f"VectoreStore Indexing: Split into {len(batches)} batches of {batch_size} documents each"
        )

        # Process all batches concurrently
        async def add_batches(batch: List[Document],batch_num:int):
            try:
                  await vectorestore.aadd_documents(batch)
                  log_success(
                       f"Vectorestore Indexing: Successfully added batch {batch_num}/{len(batch)} documents)"
                  )
            except Exception as e:
                 log_error(f"VectoreStore Indexing: Failed to add batch {batch_num} - {e}")
                 return False 
            return True 

        # Process batches concurrently 
        tasks = [add_batches(batch,i+1) for i, batch in enumerate(batches)]
        results = await asyncio.gather(*tasks,return_exceptions=True)

        # Count successful batches
        successful = sum(1 for result in results if result is True)

        if successful == len(batches):
             log_success(
                  f"VectoreStore Indexing: All batches processed successfully! ({successful}/{len(batches)}"
             )
        else:
             log_warning(
                  f"VectoreStore Indexing: Processed {successful}/{len(batches)} batches successfully"
             )
             



async def main():
    """Main async function to orchestrate the entire process."""
    log_header("DOCUMENTATION INGESTION PIPELINE")

    log_info(
        "TavilyCrawl: Starting to Crawl documentation from https://python.langchain.com",
        Colors.PURPLE,
    )

    # Crawl the documentation site

    res = tavily_crawl.invoke({
        "url": "https://python.langchain.com/",
        "max_depth":2,
        "extract_depth":"advanced",
    })

    all_docs = [Document(page_content=result["raw_content"],metadata={"source":result["url"]}) for result in res["results"]]
    log_success(
        f"TavilyCrawl: Successfully crawled {len(all_docs)} URLs from documentation site"
    )

    # Split documents into chunks
    log_header("DOCUMENT CHUNK PHASE")
    log_info(
        f"Text Splitter: Processing {len(all_docs)} documents with 4000 chunk size and 200 overlap",
        Colors.YELLOW,
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000,chunk_overlap=200)
    splitted_docs = text_splitter.split_documents(all_docs)
    log_success(
        f"Text Splitter: Created {len(splitted_docs)} chunks from {len(all_docs)} documents"
    )

    # Process documents asyncronously
    await index_documents_async(splitted_docs,batch_size=500)

    log_header("PIPELINE COMPLETE")
    log_success("Documentation ingestion pipeline finished sccessfully!")
    log_info("Summary:",Colors.BOLD)
    log_info(f"Documents extracted: {len(all_docs)}")
    log_info(f"Chunks created: {len(splitted_docs)}")
    



if __name__ == "__main__":
    asyncio.run(main())