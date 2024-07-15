from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchStore
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
import logging
from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import urllib3

# Disable insecure HTTPS warnings (only for development/testing)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('.env.example')
es_pass = os.getenv('ELASTICSEARCH_KEY')
logger.info(f"Elasticsearch password: {es_pass}")

class DataIngestion:
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

    def preprocess_pdf(self, pdf):
        '''
        Function -> extracts text from the pdf
        parameters -> takes pdf file as parameter
        '''
        try:
            with pdfplumber.open(pdf) as pdf:
                return ' '.join(page.extract_text() for page in pdf.pages)
        except FileNotFoundError:
            logger.error(f'File not found {pdf}')
            return None

    def chunk_text(self, text):
        '''
        Function -> Chunks text on the based of recursive character splitter from langchain
        Parameters ->
        text-> text from the preprocess function and chunks it
        '''
        if not text:
            logger.error("No text to chunk")
            return None
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50,
            length_function=len,
        )
        return text_splitter.split_text(text)

    def embed_text(self, chunks):
        '''
        Function ->embeds the text based on open ai embeddings
        paramter -> chunks from the chunk_text function 
        '''
        if not chunks:
            logger.error("No chunks to embed")
            return None
        embedding = OpenAIEmbeddings()
        store = ElasticsearchStore(
            embedding=embedding,
            es_connection=self.es,
            index_name=self.index_name
        )
        store.add_texts(chunks)
        return store

    def ingest_data(self, pdf_path):
        '''
        ingests the data and uses all the function of the class
        params-> takes pdf_path as input 4
        '''
        text = self.preprocess_pdf(pdf_path)
        if not text:
            return None
        chunked_docs = self.chunk_text(text)
        if not chunked_docs:
            return None
        embed = self.embed_text(chunked_docs)
        if embed:
            logger.info("Data Ingestion successful")
            return embed
        else:
            logger.error("Data Ingestion failed")
            return None

if __name__ == '__main__':
    ingestion = DataIngestion(es_pass=es_pass)
    store = ingestion.ingest_data('Customer_Support_Guide.pdf')
    if store:
        logger.info("Process completed successfully")
    else:
        logger.error("Process failed")