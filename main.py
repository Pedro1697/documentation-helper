from backend.core import run_llm
import streamlit as st 

def main():
    def create_sources_string(source_urls:set[str]) -> str:
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

    if "user_prompt_history" not in st.session_state:
        st.session_state["user_prompt_history"] = []
    
    if "chat_answer_history"not in st.session_state:
        st.session_state["chat_answer_history"] = []
    
    if prompt:
        with st.spinner("Generating response..."):
            generated_response = run_llm(query=prompt)
            sources = set([doc.metadata["source"] for doc in generated_response["source_documents"]])

            formatted_response = (
                f"{generated_response['result']} \n\n {create_sources_string(sources)}"
            )

            st.session_state["user_prompt_history"].append(prompt)
            st.session_state["chat_answer_history"].append(formatted_response)

    if st.session_state["chat_answer_history"]:
        for generated_responses, user_query in zip(st.session_state["chat_answer_history"],st.session_state["user_prompt_history"]):
            st.chat_message("user").write(user_query)
            st.chat_message("assitant").write(generated_responses)


if __name__ == "__main__":
    main()
