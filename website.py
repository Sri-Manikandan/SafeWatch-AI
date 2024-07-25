import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI

load_dotenv()
client = OpenAI()

def get_text(url):
    loader = WebBaseLoader(url)
    document = loader.load()
    text=document[0].page_content
    refined_text = text.replace("\n", "")
    return refined_text

def moderation_analysis(text):
    response = client.moderations.create(input=text)
    output = response.results[0]
    analysis_result = output.categories
    category_scores = output.category_scores
    analysis_text = f"Analysis results: {analysis_result}. Category scores: {category_scores}."
    return analysis_text

def chat_analysis(text, analysis_text):
    llm = ChatOpenAI(model="gpt-4o")
    prompt = f"""
    Here is the content of the website:
    {text}
    
    and the response of the OpenAI moderation API is:
    {analysis_text}

    Help me find if the given content from the website is kids-friendly or not based on given the content and the response of the OpenAI moderation API.
    Provide the output with only the conclusion whether it is kids-friendly or not and justification to support it in a few sentences.
    """

    messages = [
        (
            "system",
            "You are a helpful assistant that helps find if the given content from the website is kids-friendly or not, using the content and the response of the OpenAI moderation API.",
        ),
        ("human", prompt),
    ]
    ai_msg = llm.invoke(messages)
    st.write(ai_msg.content)


def main():
    st.title("Website AI")
    st.write("The Website AI helps to analyze the content of a website and determine if it contains any harmful or inappropriate content.")

    website_url = st.text_input("Website URL")
    if st.button("Analyze"):
        with st.spinner("Processing..."):
            text = get_text(website_url)
            analysis_text = moderation_analysis(text)
            chat_analysis(text, analysis_text)

        
if __name__ == "__main__":
    main()
