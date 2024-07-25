from langchain_community.embeddings import OpenAIEmbeddings
from typing import Dict
from langchain_elasticsearch import ElasticsearchRetriever
from elasticsearch import Elasticsearch
import logging
import os 
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
load_dotenv('.env.example')
logger = logging.getLogger(__name__)
embedding = OpenAIEmbeddings()
es_pass = os.getenv('ELASTICSEARCH_KEY')
class Retrival:
    def __init__(self, es_pass, index_name="vector_index"):
        self.es = Elasticsearch(
            "https://localhost:9200",
            basic_auth=('elastic', es_pass),
            request_timeout=10,
            verify_certs=False,  
            ssl_show_warn=False
        )
        self.index_name = index_name

        if self.es.ping():
            logger.info("Connection with the database established")
        else:
            logger.error("Failed to connect to elasticsearch")
    def vector_query(self,search_query: str) -> Dict:
        '''
        Function-> Mapping function for the dense vector field using langchain_elasticsearch
        '''
        try:
            vector = embedding.embed_query(search_query)  
            return {
                "knn": {
                    "field": "vector",
                    "query_vector": vector,
                    "k":10 ,
                    "num_candidates": 10
                }
            }
        except KeyError as e:
            print(f"KeyError: {e}")
            return {}
    def retrieve_text(self):
        '''
        Function -> Retrieves the most similar text according to the user query
        '''
        retriever = ElasticsearchRetriever(
            es_client = self.es,
            index_name = "vector_index",
            body_func = self.vector_query,
            content_field = 'text'
        )
        return retriever
    
