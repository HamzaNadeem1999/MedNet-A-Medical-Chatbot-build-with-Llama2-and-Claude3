# -*- coding: utf-8 -*-
"""Building Medical Chatbot with Claude3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EXf2kgNJTB7VVc0VkIosTmA2IYzfXXzV
"""

!pip install boto3

!pip install streamlit

import json
import os
import sys
import boto3
import streamlit as st

!pip install langchain

from langchain.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

import numpy as np
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFDirectoryLoader

# Vector Embedding and vector store
from langchain.vectorstores import FAISS

#LLms Models
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

region_name = 'us-east-1'

bedrock = boto3.client(service_name='bedrock-runtime', region_name=region_name)
bedrock_embeddings=BedrockEmbeddings(model_id='amazon.titan-embed-text-v1',client=bedrock)

# prompt: write code to ingest data from my system

def ingest_data(directory_path):
  loader = PyPDFDirectoryLoader(directory_path)
  documents = loader.load()
  return documents

documents = ingest_data('/Users/hamzanadeemsiddiqui/Desktop/NLP Medical Chatbot/Data')

## Data ingestion
def data_ingestion():
  loader=PyPDFDirectoryLoader("Data")
  documents=loader.load()

  text_splitter=RecursiveCharacterTextSplitter(chunk_size=10000,chunk_overlap=1000)
  docs=text_splitter.split_documents(documents)
  return docs

#Vector Embedding and vector score
def get_vector_store(docs):
  vectorstore_false=FAISS.from_documents(,bedrock_embeddings)
  vectorstores_faiss.save_local('faiss_index')

def get_claude_llm():
  # create_anthropic_model
  llm = Bedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0", client=Bedrock,
                model_kwargs={'maxTokens':512})
  return llm

def get_llama2_llm():
  # create_anthropic_model
  llm = Bedrock(model_id="meta.llama2-70b-chat-v1", client=Bedrock,
                model_kwargs={'max_gen_len':512})
  return llm

prompt_template = """
Human: Use the following pieces of context to provide a
concise answer to the question at the end but usse atleast summarize with
250 words with detailed explaantions. If you don't know the answer,
just say that you don't know, don't try to make up an answer.
<context>
{context}
</context
Question: {question}

Assistant:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

def get_response_llm(llm,vectorstore_faiss,query):
  qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore_faiss.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    ),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)
  answer=qa({"query":query})
  return answer['result']

def main():
    st.set_page_config("MedChat")

    st.header("Chat with AI Medical Assistant")

    user_question = st.text_input("Ask any Health related Question ")

    with st.sidebar:
        st.title("Update Or Create Vector Store:")

        if st.button("Vectors Update"):
            with st.spinner("Processing..."):
                docs = data_ingestion()
                get_vector_store(docs)
                st.success("Done")

    if st.button("Claude_3 Output"):
        with st.spinner("Processing..."):
            faiss_index = FAISS.load_local("faiss_index", bedrock_embeddings)
            llm=get_claude_llm()

            #faiss_index = get_vector_store(docs)
            st.write(get_response_llm(llm,faiss_index,user_question))
            st.success("Done")

    if st.button("Llama2 Output"):
        with st.spinner("Processing..."):
            faiss_index = FAISS.load_local("faiss_index", bedrock_embeddings)
            llm=get_llama2_llm()

            #faiss_index = get_vector_store(docs)
            st.write(get_response_llm(llm,faiss_index,user_question))
            st.success("Done")

if __name__ == "__main__":
    main()