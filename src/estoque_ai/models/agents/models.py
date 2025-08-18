from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

key_gemini = os.getenv("GOOGLE_API_KEY")
key_grok = os.getenv("GROQ_API_KEY")

llm_gemini = ChatGoogleGenerativeAI(
    api_key = key_gemini,
    model ="gemini-2.5-flash",
    temperature=0.7,
)

llm_groq = ChatGroq(
    api_key = key_grok,
    model ="llama3-70b-8192",
    temperature=0.7,
)

