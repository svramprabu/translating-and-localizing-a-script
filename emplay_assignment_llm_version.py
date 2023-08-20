import streamlit as st

import os
import openai
import sys
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
import docx

sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']
# print(os.environ['OPENAI_API_KEY'])

# st.write(os.environ['OPENAI_API_KEY'])

from langchain.document_loaders import Docx2txtLoader

path = '.'

#List only files
files = [f for f in os.listdir(path) if os.path.isfile(f) and f.endswith('.docx')]

file_to_work = st.sidebar.selectbox('Choose the source file from the dropdown',
    files)
# st.write(file_to_work)

# loader = Docx2txtLoader("Demo Script.docx")
loader = Docx2txtLoader(f"{file_to_work}")
data = loader.load()
# data

product = data[0].page_content[590:600]
# product = data
# st.write(product)

lang_to_translate = st.sidebar.text_input("enter your language of choice", value="English") #"spanish"
nationality = st.sidebar.text_input("enter your nationality of choice", value="Indian") #"indian"

def seq_chain(product,lang_to_translate,nationality):
    llm = ChatOpenAI(temperature=0)

    first_prompt = ChatPromptTemplate.from_template(
        "Translate the following {product} to  "
        f"\n\n{lang_to_translate}"
    )
    # first_prompt.format(lang_to_translate="spanish")
    # chain 1: input= Review and output= English_Review
    chain_one = LLMChain(llm=llm, prompt=first_prompt, 
                        output_key="translation"
                        )

    second_prompt = ChatPromptTemplate.from_template(
        "just replace the person names alone in {translation}"
        f"\n\n with names of {nationality} and do nothing else"
    )
    # chain 2: input= English_Review and output= summary
    chain_two = LLMChain(llm=llm, prompt=second_prompt, output_key="output_text" )

    # overall_chain: input= Review 
    # and output= English_Review,summary, followup_message
    # @st.cache_data
    overall_chain = SequentialChain(
        chains=[chain_one, chain_two], #chain_three, chain_four],
        input_variables=["product"],
        output_variables=["translation","output_text"], #,"followup_message"],
        verbose=True
    )

    return overall_chain(product)
st.title('Emplay Assignment')
st.header(' to translate the given script to the user specified language and replace names with respect to the nationality')
st.write(":green[Translating]")
st.write(f":red[This is the input text]")
st.write(product)

response = seq_chain(product,lang_to_translate,nationality)
st.write(f":red[This is the {lang_to_translate} translated text]")
st.write(response['translation'])
st.write(f":red[This is the final output with the {nationality} names.]")
st.write(response['output_text'])

doc = docx.Document()
doc_para = doc.add_paragraph(f'{response}')
doc.save('Localised Demo Script.docx')
st.success(":green[Final output is saved as Localised Demo Script.docx]")

