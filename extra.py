from langchain.document_loaders import YoutubeLoader, PyPDFLoader
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
from langchain.memory import ZepMemory
from langchain.document_loaders import WebBaseLoader
from langchain.llms import OpenAI
from langchain.schema import SystemMessage
from zep_python import ZepClient
from zep_python.memory.models import Session, Memory,Message
from zep_python.user.models import CreateUserRequest
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
import re
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import uuid
import os
from zep_python import ZepClient

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ZEP_API_URL = os.getenv('ZEP_API_URL')
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
chat = ChatOpenAI(temperature=0.2, openai_api_key=OPENAI_API_KEY)
client = ZepClient(ZEP_API_URL)


def get_response_from_docs(userid,sessionid, docs_page_content, query):
    """
    Generates a response to a query using a gpt, incorporating session memory and persona.
    """
    session_id = str(userid)+str(sessionid)
    try:
        session = Session(session_id=session_id)
        client.memory.add_session(session)
    except Exception as e:
        session = Session(session_id=session_id)
        client.memory.update_session(session)
         
    metadata = client.memory.get_session(session_id).dict().get("metadata")
    if metadata:
        persona_values= list(metadata.values())
        persona_values = ". ".join(persona_values)
        print(persona_values)
    if not metadata:
        persona_values=""
 
    memory = ZepMemory(
        session_id=session_id,
        url=ZEP_API_URL,
        api_key=OPENAI_API_KEY,
        memory_key="chat_history",
        input_key="question",
        return_messages=False,
    )

 
    text=docs_page_content+persona_values
    
    
    llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0, streaming=0)


    prompt = PromptTemplate(
        input_variables=["question","docs_page_content", "chat_history"],
        template="answer to the query"
    ) 

    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    response = chain.run(question=query, text = text)
    return response

def create_session(userid,sessionid,res):
    """
    Creates or updates a user session with the given user and session identifiers, incorporating optional persona information.
    """
    try:
        session_id = str(userid)+str(sessionid)
        print(session_id)
        ran = uuid.uuid4()
        ran=str(ran)
        if res:
            session = Session(session_id=session_id,metadata={f"persona_{ran}" : res})
            d=client.memory.add_session(session)
        if not res:
            session = Session(session_id=session_id)
            d=client.memory.add_session(session)

    except Exception as e:
        if res:
            session = Session(session_id=session_id, metadata={f"persona_{ran}" : res})
            client.memory.update_session(session)
        if not res:
            session = Session(session_id=session_id)
            client.memory.update_session(session)
    

def json_data_fetch(json_data, *args):
    result = []
    for arg in args:
        try:
            value = json_data[arg]
            result.append(value)
        except KeyError:
            result.append(None)
    
    return tuple(result)



def delete_all_sessions():
    """Deletes all session from the ZEP Memory Server"""
    l = []
    all_sessions = client.memory.list_all_sessions(chunk_size=100)
    for session_chunk in all_sessions:
        for session in session_chunk:
            l.append(session.session_id)
    
    for i in l:
        client.memory.delete_memory(i)
