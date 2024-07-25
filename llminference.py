from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler

# class StreamingHandler(BaseCallbackHandler):
#     def __init__(self, queue):
#         self.queue = queue

#     def on_llm_new_token(self, token: str, **kwargs) -> None:
#         self.queue.put(token)

def get_conversation_chain(retrival_instance, streaming_queue=None):
    llm = ChatOpenAI(streaming=True)
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    
    retriever = retrival_instance.retrieve_text()
    
    prompt_template = """
    Suppose you are a customer support system for a bank. You have to determine the intent of the question provided by the user in three categories:
    1. Placing an order
    2. Account inquiries
    3. Technical support
    if the user's greets you like hi,bye,hey etc respond accordingly don't give the answer to the user about 


    Context: {context}
    Human: {question}
    AI: """

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": PROMPT},
    )
    
    return conversation_chain