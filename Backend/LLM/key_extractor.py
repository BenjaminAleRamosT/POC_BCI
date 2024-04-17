import time
import json
import base64
import os
import requests

import streamlit as st

# IBM Watson Discovery
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from Backend.credentials.Mongo import get_mongo_client

# Langchain IBM
# from langchain_ibm import WatsonxLLM

WatsonxLLM = 'WatsonxLLM'

# Langchain OpenAI
# from langchain_openai import ChatOpenAI

# Langchain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

# <- FastAPI ->
from fastapi import FastAPI, File, UploadFile

# <- MongoDB ->
from pymongo import MongoClient

client = get_mongo_client()

db = client['test_pdf']
col_pdf = db['pdf']
col_res = db['resumenes']
col_comp = db['comparaciones']


# <- IBM Watson Discovery ->
api_aim = 'YFaSBR1grvzWsCDYxr0ifGafpIl325eVSJFQzGO314mW'
api_wd = '6EKwQ3DwjeXO5RnsfvG8wAK8A0cVlN6xCReGeXKeeHNz'

authenticator = IAMAuthenticator(api_wd)
discovery = DiscoveryV2(
    version='2024-01-01', #'2020-08-30',
    authenticator=authenticator
)
discovery.set_service_url('https://api.us-south.discovery.watson.cloud.ibm.com')

# <- IBM Discovery Project&Collection ->
project_id = '8bd1a7c6-5daf-4b69-a9ef-377ad5344e62'
collection_id = 'e519f857-5d5a-39bf-0000-018d7a7ce6e9'

# <-------- LLM Set-up -------->

# <- OpenAI Credentials ->

openai_api_key = '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'

# <- IBM WatsonX Credentials ->
ibm_api_key = 'QXwzfMU-jwKyrua2POVBElKDVs5fMW610R1hehaj7QNK'
os.environ["WATSONX_APIKEY"] = ibm_api_key

company = "IBM"


def comparator_model(text_1_dict,text_2_dict,empresa,openai_api_key=openai_api_key, ibm_api_key=ibm_api_key, company=company):

    text_1 = text_1_dict["summary"]
    text_2 = text_2_dict["summary"]

    name_1 = text_1_dict["name"]
    name_2 = text_2_dict["name"]

    iam_token = get_iam_token()
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": """[INST] <<SYS>>
    <|text 1 |>
    {name_1}: \"{{text_1}}\".

    <|text 2 |>
    {name_2}: \"{{text_2}}\".

    <|system|>
    Perform a comparison between '\''{name_1}'\'' and '\''{name_2}'\'', highlighting the key differences in both general and specific contents, including the type of document each text represents (e.g., financial statement, call transcript, interview format). Focus on significant statistical variations related to their temporal contexts, if available, and explicitly mention and compare statistical percentages when discussing increases or decreases. Present your findings in a format that emphasizes the crucial points of distinction without using titles or headings. Ensure that the comparison delves into how these differences contribute to the overall understanding of the context and implications of each summary. Assess the sentiment of each document concerning the highlights in the data of each document and contrast these analyses. The output must adhere strictly to the specified format, beginning each important point with '\''->'\'' and excluding titles or headings in favor of complete sentences. Use '\''->'\'' solely to mark the start of each key point, maintaining uniformity in the structure. Every key difference should form a complete sentence, devoid of titles or general concepts, and must be directly relevant to the article without introducing external information. Refrain from repeating key differences and always mention the document by its name. The output should be consistently translated into Spanish, and the summary should be coherent and aligned with the context of the documents.

    <|important|>
    - The output format must be identical to the OUTPUT FORMAT. Indicate with '\''->'\'' the beginning of each important point.
    - Do not add titles or headings, only complete sentences are allowed.
    - The characters '\''->'\'' should only be used to indicate the beginning of each key point. Do not use them elsewhere in the summary, and you cannot use another symbol to indicate the start of another point. All should be at the same level to respect the structure.
    - Each key difference must be a complete sentence; do not add titles or general concepts. You cannot divide a sentence into two key points, nor can you divide a key point into sub-points.
    - Each key difference must be relevant to the article.
    - You cannot add information that is not in the article. You can only extract information from the texts.
    - Do not repeat key differences.
    - Always refer to the document by its name.
    - The summary must be coherent and consistent with the context of the documents.
    - The output format of Verbose key differences don´t need to call all the time the name of the document, only the first time.
    - The output must always be translated into Spanish.

    <|output format|>
    **DIFERENCIAS:**
    -> <Verbose key difference 1>.
    -> <Verbose key difference 2>.
    -> <Verbose key difference 3>.
    -> <Verbose key difference 4>.
    -> <Verbose key difference 5>.
    -> ...

    -> **DOCUMENTO 1:**
    <Verbose content analysis of {name_1}>.

    -> **DOCUMENTO 2:**
    <Verbose content analysis of {name_2}>.

    #### RESUMEN DE LAS DIFERENCIAS:
    <Summary of differences content>.

    <|output|>
    <</SYS>>


    name_1 : Análisis_Razonado90749000_202309.pdf

    text_1: Los ingresos consolidados de la compañía cayeron un 9,6% a/a, principalmente debido a la disminución en los negocios de Mejoramiento del Hogar en Chile, Tiendas por Departamento en Chile y Negocios de Retail en Perú. En Chile, los ingresos de los formatos de retail disminuyeron un 15,3% a/a, con un impacto negativo en Mejoramiento del Hogar, Tiendas por Departamento y Supermercados. La venta online de retailers y sellers alcanzó MM\$291.119 millones, con una caída del 16% a/a y una penetración online del 20%. Mallplaza registró un aumento del 16,9% a/a en ingresos debido a una mayor ocupación y la indexación a UF. En Perú, los ingresos de Mejoramiento del Hogar, Tiendas por Departamento y Supermercados experimentaron caídas, contrarrestadas parcialmente por el negocio bancario.

    En cuanto al resultado operacional, este fue de MM$64.877, un 3,1% menor que en el trimestre anterior, atribuido a la caída en la ganancia bruta consolidada. En Chile, el resultado operacional de los negocios retail fue una pérdida de MM$59.588, con un aumento del 170,2% a/a, principalmente por la caída en el margen de Mejoramiento del Hogar. En Banco Falabella Chile, el resultado operacional creció un 280,2%, alcanzando MM$49.942, debido a un aumento en la ganancia bruta por un menor costo por riesgo. En Perú, el resultado operacional fue de MM$42.592, con una disminución del 34,9% a/a, explicado por la caída en la ganancia bruta asociada a varios negocios. En Colombia, el resultado operacional fue una pérdida de MM$24.991, con una ganancia bruta impactada por un aumento en el costo por riesgo del negocio bancario.

    La pérdida neta del trimestre fue MM$4.642, representando una disminución del 72,6% con respecto al periodo comparable, con una menor contribución de algunos negocios compensada por el negocio inmobiliario. En cuanto a la deuda, el endeudamiento de los negocios no bancarios mostró una disminución del 7,7% en la deuda total bruta a MM$4.539.221 en septiembre de 2023, con una deuda neta de MM$3.597.044 y un ratio de endeudamiento neto de 1,0 veces. El patrimonio total aumentó en MM$222.031, principalmente por el resultado total del período y el incremento de las reservas por diferencias de cambio por conversión. La liquidez de la compañía al cierre de septiembre de 2023 fue de MM$2.165.067, con MM$649.839 en negocios no bancarios y MM$1.515.228 en negocios bancarios.

    name_2: Falabella SA Earnings Call 20231116 DN000000003027576234.pdf

    text_2: Falabella SA realizó su llamada de ganancias del tercer trimestre de 2023, donde participaron Alejandro Gonzalez Dale, Director Financiero; Andrea Gonzalez Bayon, Directora de Estrategia y Sostenibilidad; Gaston Bottazzini, CEO; y Raimundo Monge, Jefe de Relaciones con Inversores. Durante la presentación se destacó la apertura de seis tiendas en la región, incluyendo la primera tienda de IKEA en Colombia. Se observó una desaceleración en las tendencias de consumo y altos niveles de inflación que impactaron las operaciones, especialmente en las áreas de Mejoras para el Hogar y Grandes Tiendas en Chile, así como en el negocio minorista en Perú. Los ingresos de las Grandes Tiendas alcanzaron los \$753 millones en el trimestre, mientras que la categoría Electro experimentó la mayor caída en ventas tanto en el canal físico como en línea. Los ingresos de Mejoras para el Hogar alcanzaron los \$1.3 mil millones, con una disminución del 15%, y los ingresos de los Supermercados disminuyeron un 8%, alcanzando los \$587 millones.

    En cuanto al lado bancario, Banco Falabella Chile se destacó como el principal emisor de tarjetas de crédito, con una cartera de préstamos que disminuyó un 9% interanual, alcanzando los $7 mil millones. El uso de tarjetas de crédito y débito aumentó un 3%, a pesar de un entorno de consumo desafiante. El programa de fidelización cuenta con casi 19 millones de participantes, y se implementaron medidas de eficiencia que generaron ahorros de $350 millones al año. Además, se anunció la venta de activos inmobiliarios no fundamentales por un monto estimado entre $800 millones y $1 mil millones, como parte de un plan para fortalecer la posición financiera de la empresa.

    En términos de ganancias, se mencionó que las ganancias brutas disminuyeron un 6% interanual, mientras que el EBITDA creció un 1% interanual, alcanzando los $202 millones. Los gastos de SG&A disminuyeron un 6% interanual, y la deuda financiera neta se redujo en un 5%. Se destacó un plan para aumentar la rentabilidad que incluye un enfoque en el CapEx hasta el 2024, mantener los ahorros logrados, mejorar los márgenes operativos y recaudar entre $800 millones y $1 mil millones de activos no estratégicos en un período de 12 a 15 meses. La estrategia de inversión de Falabella busca un equilibrio entre el crecimiento y la rentabilidad, con un enfoque en la gestión de márgenes y gastos generales y administrativos para lograr mejoras a pesar de las condiciones actuales de demanda. [/INST]""",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 4000,
            "repetition_penalty": 1
        },
        "model_id": "meta-llama/llama-2-70b-chat",
        "project_id": "c4faff81-af63-4f31-820d-4e0bf3808f93"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}"
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )
    # reemplacemos los $ por \$
    diferencias = response.json()["results"][0]["generated_text"]
    diferencias = diferencias.replace("$","\$")
    # guardemos en la mongodb en db['comparaciones']
    comp_to_db = {"id":"Last_comp",
                "empresa": empresa,
                "docs_1": name_1,
                "docs_2": name_2,
                "diferencias": diferencias}

    
    # si ya existe, lo actualizamos
    if col_comp.find_one({"id":"Last_comp"}):
        col_comp.update_one({"id":"Last_comp"}, {"$set": comp_to_db})
        # #print("Ultima comparación actualizada")
    else:
        col_comp.insert_one(comp_to_db)
        # #print("Se ha creado la última comparación")

    return "\n".join(diferencias.split("->"))

def get_iam_token(apikey= "5z1h-psruiL1HejXYzjOW0glrUC8CAGA4FEDXb_db1jF"):



    # Get an IAM token from IBM Cloud
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    response = requests.post(url, headers=headers, data=data)
    iam_token = response.json()["access_token"]

    return iam_token


def dividir_texto(texto, longitud_segmento):
    return [texto[i:i + longitud_segmento] for i in range(0, len(texto), longitud_segmento)]

def LLM_INTRODUCTION_BANCA(texto):
    iam_token = get_iam_token()
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": f"""[INST] <<SYS>>
    Crea un resumen, conciso y coherente de las primeras páginas de un documento en español, destacando los aspectos clave y el propósito del contenido de no mas de 1000 palabras. El idioma del texto generado debe ser en Español.
<</SYS>>
{texto}[/INST]""",
        "parameters": {
		"decoding_method": "greedy",
		"max_new_tokens": 2000,
		"repetition_penalty": 1.05
	},
        "model_id": "meta-llama/llama-2-70b-chat",
        "project_id": "c4faff81-af63-4f31-820d-4e0bf3808f93"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}"}

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    return data["results"][0]["generated_text"]

def obtener_keypoints(texto):
    iam_token = get_iam_token()

    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": f"""[INST] <<SYS>>
    Crea un listado de los puntos claves de el siguiente fragmento de documento, el listado debe ser en español y no debe superar las 1000 palabras.
    El formato debe ser una lista que enumere los puntos claves de el texto con un '-' al inicio de cada punto.
<</SYS>>
{texto}[/INST]""",
        "parameters": {
		"decoding_method": "greedy",
		"max_new_tokens": 2000,
		"repetition_penalty": 1.05
	},
        "model_id": "meta-llama/llama-2-70b-chat",
        "project_id": "c4faff81-af63-4f31-820d-4e0bf3808f93"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}"}

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    return data["results"][0]["generated_text"]

def difference_texts(texto1,texto2):
    iam_token = get_iam_token()

    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": f"""[INST] <<SYS>>
    Crea un parrafo que describa las diferencias del contenido entre los siguientes textos, el parrafo debe ser en español y no debe superar las 1100 palabras.
<</SYS>>
texto 1:{texto1}
texto 2: {texto2}[/INST]""",
        "parameters": {
		"decoding_method": "greedy",
		"max_new_tokens": 3000,
		"repetition_penalty": 1.05
	},
        "model_id": "meta-llama/llama-2-70b-chat",
        "project_id": "c4faff81-af63-4f31-820d-4e0bf3808f93"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}"}

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    return data["results"][0]["generated_text"]