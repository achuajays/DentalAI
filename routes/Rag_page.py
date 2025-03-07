import numpy as np
import os
from dotenv import load_dotenv
import psycopg2
from google import genai
from google.genai import types
load_dotenv()

class RAGSystem:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            self.cur = self.conn.cursor()
        except psycopg2.DatabaseError as e:
            print(f"Database connection error: {e}")
            raise
        except Exception as e:
            print(f"Error initializing Gemini client or database: {e}")
            raise

    def get_embedding(self, text):
        try:


            client = genai.Client(api_key=os.getenv("Gemini_api_key"))

            result = client.models.embed_content(
                model="text-embedding-004",
                contents=text)

            print(result.embeddings[0].values)
        except Exception as e:
            print(f"Error retrieving embedding: {e}")
            raise

    def fetch_relevant_text(self, type , query_text):
        try:
            query_embedding = self.get_embedding(query_text)
            embedding_vector = np.array(query_embedding, dtype=np.float32).tolist()

            self.cur.execute("""
                SELECT text 
                FROM evaluation WHERE type = %s
                ORDER BY vector <=> %s::vector
                LIMIT 5;
            """, (type,query_embedding,))

            results = self.cur.fetchall()
            if not results:
                return None
            print("*"*100)
            print(results)
            print("*"*100)
            context_text = " ".join(result[0] for result in results)
            print(context_text)
            return context_text
        except psycopg2.Error as e:
            print(f"SQL execution error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def get_answer_from_gpt(self, query_text, context_text):
        try:


            client = genai.Client(api_key=os.getenv("Gemini_api_key"))

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"""
I will provide you with a current Medical Report analysis and a past Medical Report
analysis of the same problem. Your task is to compare both analyses,
 identify any changes or consistencies, and provide a detailed yet concise
  summary of the findings. Highlight any significant improvements, deteriorations, or unchanged aspects.
   Ensure your response is medically accurate and formatted clearly for easy interpretation.
current Medical Report analysis: {query_text} , 
Past  Medical Report: {context_text}
. if Past  Medical Report analysis is missing or irrelevant dont consider it . only return the analysis
""")
            print(response.text)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            raise

    def close(self):
        if self.conn:
            self.cur.close()
            self.conn.close()
