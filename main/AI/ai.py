from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from main.settings import GOOGLE_API_KEY
from dotenv import load_dotenv
import os
from django.contrib import messages




def get_response(QUERRY,request):
    # load_dotenv()
    # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # POSTGRES_USER = "postgres"
    # POSTGRES_PASSWORD = "postgres"
    # POSTGRES_HOST = "127.0.0.1"
    # POSTGRES_PORT = 5432
    # POSTGRES_DB = "tool_tracking"

    # llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.1, convert_system_message_to_human=True)
    # db = SQLDatabase.from_uri( f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    # agent_executor = create_sql_agent(
    #     llm=llm,
    #     toolkit=SQLDatabaseToolkit(db=db, llm=llm),
    #     verbose=True,
    #     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    # )
    # try:
    #     final_answer = agent_executor.invoke(f"{QUERRY}")
    #     print("Answer:", final_answer['output'])
    #     return final_answer['output']
    # except Exception as e:
    #     print("An error occurred:", e)
    load_dotenv()
    exc = True
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro", temperature=0.1, convert_system_message_to_human=True)
    x = is_potentially_destructive(QUERRY, llm)
    print(f"is_potentially_destructive : {x}")
    if x:
        exc = False
        messages.error(request, f"WARNING: This query appears to be potentially destructive Aorting.")
        print("It could modify or delete data in your database.")
        # confirmation = input(
        #     "Are you sure you want to proceed? (y/n): ").lower()
        # if confirmation not in ("y", "yes"):
        #     print("Aborting query.")
        #     exc = False
        # if confirmation not in ("n", "no"):
        #     exc = True
    if exc:
        try:
            final_answer = db_agent(QUERRY,llm)
            print("Answer:", final_answer['output'])
            return final_answer['output']
        except Exception as e:
            print("An error occurred:", e)
            messages.error(request, f'AI : EXCEPTION : {e}')




def db_agent(QUERRY,llm):
    
# Relevant pieces of previous conversation:
# {history}
# (Note: Only reference this information if it is relevant to the current query.)
    CUSTOM_SUFFIX = """Begin!
    Question: {QUERRY}
    Thought Process: It is imperative that I do not fabricate information not present in the database or engage in hallucination; 
    maintaining trustworthiness is crucial.If The user saying Grn or anything with grn look for Product_index and if user saying so or sale order or related look for sale order table.
    My final response must be delivered in the language of the user's query.
"""
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "postgres"
    POSTGRES_HOST = "127.0.0.1"
    POSTGRES_PORT = 5432
    POSTGRES_DB = "tool_tracking"
    db = SQLDatabase.from_uri(
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=SQLDatabaseToolkit(db=db, llm=llm),
        verbose=True,
        suffix=CUSTOM_SUFFIX,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    final_answer = agent_executor.invoke(f"{QUERRY}")

    return final_answer


def is_potentially_destructive(query, llm):
    destructive_keywords = ["DELETE", "UPDATE", "DROP", "TRUNCATE","REMOVE","TAKE AWAY"]
    if any(keyword.upper() in query.upper() for keyword in destructive_keywords):
        return True
    llm_prompt = f"**YES or NO only:** Could this SQL query be destructive (modify or delete data or chnage data or chnage structure of database) in the database? it is okay if user is asking for any kind of count or details : {query}"
    llm_response = llm.invoke(llm_prompt)
    answer = llm_response.content
    answer = answer.upper()
    print(f"LLM DESTRUCTIVE PREDICTION : {answer}")
    if answer == 'YES' or answer == '**YES**':
        print(f"RESON : {llm_response}")
        return True
    elif answer == 'NO' or answer =='**NO**':
        return False