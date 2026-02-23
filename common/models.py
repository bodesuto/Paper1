from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from .config import AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_EMBEDDING_DEPLOYMENT
from .env_setup import apply_env

def get_llm():
    apply_env()
    return AzureChatOpenAI(azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME)


def get_llm_with_trace(trace_handler: BaseCallbackHandler):
    """
    Get LLM with trace handler and callback manager.
    Returns tuple of (llm, trace_handler).
    """
    apply_env()
    
    cb_manager = CallbackManager([trace_handler])
    
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        callbacks=cb_manager
    )
    
    return llm


def get_embeddings():
    apply_env()
    return AzureOpenAIEmbeddings(azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT)
