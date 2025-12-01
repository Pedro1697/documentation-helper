from backend.core import run_llm
import streamlit as st 
from types import Set 

def main():
    def create_sources_string(source_urls:Set[str]) -> str:
        if not source_urls:
            return ""
        source_list = list(source_urls)
        source_list.sort()
        source_string = "sources:\n"
        for i, source in enumerate(source_list):
            source_string += f"{i+1}. {source}\n"
        return source_string



    st.header("Documentation Helper Bot")

    prompt = st.text_input("Prompt",placeholder="Enter your prompt here ...")
    
    if prompt:
        with st.spinner("Generating response..."):
            generated_response = run_llm(query=prompt)
            sources = set([doc.metadata["source"] for doc in generated_response["source_documents"]])

            formatted_response = (
                f"{generated_response['result']} \n\n {create_source_string(sources)}"
            )


if __name__ == "__main__":
    main()
