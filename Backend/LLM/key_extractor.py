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

def llm_setup(ibm_api_key=ibm_api_key, openai_api_key=openai_api_key,company="IBM"):
    company = "IBM"
    if company == 'IBM':
        # print('IBM')
#         api_key = ibm_api_key
#         model = 'meta-llama/llama-2-70b-chat'
#         parameters = {
#     "decoding_method": "sample",
#     "max_new_tokens": 4000,
#     "min_new_tokens": 1,
#     "temperature": 0.7,
#     "top_k": 50,
#     "top_p": 1,
# }
#         llm = WatsonxLLM(
#     model_id=model,
#     url="https://us-south.ml.cloud.ibm.com",
#     project_id="c4faff81-af63-4f31-820d-4e0bf3808f93",
#     params=parameters,
# )
    # Paste your Watson Machine Learning service apikey here
        apikey = "5z1h-psruiL1HejXYzjOW0glrUC8CAGA4FEDXb_db1jF"

        # Get an IAM token from IBM Cloud
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
        response = requests.post(url, headers=headers, data=data)
        iam_token = response.json()["access_token"]

        return iam_token

 
        
    elif company == 'OpenAI':
        api_key = openai_api_key
        model = 'gpt-3.5-turbo-0125'
    
    return llm

# <- Función de extracción de keypoints ->
def keypoints_extr(file_, company=company, chunk_size=4500, chunk_overlap=1000, prints=False):
    
    keyparts = list()

    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    template = """<|text|>
{topic}.

<|system|>
Performs a comprehensive and objective analysis of the provided TEXT, identifying and highlighting all key events, important data, and relevant facts without adding personal interpretations or additional information. Ensure to fully address all topics covered in the article and provide a detailed and clear summary of each relevant aspect. You always have to answer in Spanish.

<|important|>
- The format of the output must be identical to the FORMAT OUTPUT. Indicate with '->' the beginning of each important point.
- Do not add titles or headings, only complete sentences are allowed.
- The characters '->' should only be used to indicate the beginning of each key point. Do not use it anywhere else in the summary, and you cannot use another symbol to indicate the start of another point. All should be at the same level to respect the structure.
- Each key point must be a complete sentence; do not add titles or general concepts. You cannot divide a sentence into two key points, nor can you divide a key point into sub-points.
- Each key point must be relevant to the article.
- You cannot add information not in the article. You can only extract information from the article.
- Do not repeat key points.
- Always consider important data related to a person from the company, such as the CEO, CFO, or any other relevant person.
- The output must be translated to Spanish.

<|format outpu|>
-> <Key point 1>.
-> <Key point 2>.
-> <Key point 3>.
...

<|output|>
"""

    llm = llm_setup(company=company, openai_api_key=openai_api_key, ibm_api_key=ibm_api_key)
    
    prompt= PromptTemplate.from_template(template)
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    texto_split = r_splitter.split_text(file_)

    # if prints:
    #     print(f'Total of chunks: {len(texto_split)}')
    
    for i, chunk in enumerate(texto_split):
        # check time for each iteration
        start = time.time()

        res = llm_chain.invoke(chunk)['text'].strip('\n')

        # if prints:
        #     for head in res.split('->')[:4]:
        #         print(f'- {head.strip()}')
        
        keyparts = keyparts + res.split('->')

        # if prints:
        #     print(f'Chunk {i}: Time{time.time() - start}')
        #     print('-----------')

    return keyparts



def keypoints_resum(keyparts,company=company, ibm_api_key= ibm_api_key ,openai_api_key=openai_api_key, chunk_size=4500, chunk_overlap=1000, prints=False):

    keyparts_filtered = [x.strip('\n').strip(' ') for x in keyparts if len(x) > 10]
    
    template = """<|text|>
    "{topic}".

    <|system|>
    Provide a comprehensive and objective analysis of the provided list of key points, identifying and highlighting all key events, important data, and relevant facts without adding personal interpretations or additional information. Ensure to fully address all topics covered in the list and provide a detailed and clear summary of each relevant aspect.
    The output must be at leats three pargraphs long and max five paragraph. Use the most amount of words possible to provide a detailed and clear summary of each relevant aspect. 
    If the information is enough the output must be at least 1500 words long.

    <|important|>
    - You cannot add information not in the key points. You can only extract information from the list of key points.
    - The output must be translated to Spanish.
    - Only provide the text of the key points, do not add any additional information.
    - Topics like: REVENUE, EBITDA, NET INCOME, DEBT, CASH, must be included in the output. If the information is not provided in the key points, say "Information not provided".
    - Always consider important data related to a person from the company, such as the CEO, CFO, or any other relevant person.

    <|output|>
    """

    test_keyparts = ''
    llm = llm_setup(ibm_api_key=ibm_api_key,openai_api_key=openai_api_key, company=company)
    prompt_resumen = PromptTemplate.from_template(template)
    open_chain_resumen = LLMChain(prompt=prompt_resumen, llm=llm)

    for x in keyparts_filtered:
        test_keyparts += x + '\n'

    # if prints:
    #     print(f'Total of chunks: {len(test_keyparts)}')
    # check time for each iteration
    start = time.time()

    resumen = open_chain_resumen.invoke(test_keyparts)['text']

    # if prints:
    #     print(f'Chunk: Time{time.time() - start}')
    #     print('-----------')

    return resumen

def resumen_empresarial(res_pen, company="IBM", ibm_api_key=ibm_api_key, openai_api_key=openai_api_key, chunk_size=4500, chunk_overlap=1000, prints=False):

    id_ = res_pen['_id']
    empresa = res_pen['empresa']
    periodo = res_pen['periodo']
    files = res_pen['files']
    
    resumenes = ""
    for file_ in files:
        # print(file_['filename'])

        resumenes += f"- {file_['filename']}: \n {file_['resumen']}" + '\n'
    
    template = """<|files|>
    "{topic}".

    ##SYSTEM: Your job is to provide a comprehensive and objective analysis of the provided list files, identifying and highlighting all key events, important data, and relevant facts without adding personal interpretations or additional information. Ensure to fully address all topics covered in the list and provide a detailed and clear summary of each relevant aspect.
    The output must be at leats five pargraphs long and max ten paragraph. Use the most amount of words possible to provide a detailed and clear summary of each relevant aspect. 
    If the information is enough the output must be at least 1500 words long. Is more important information about Chile than the rest of the world.
   
    <|important|>
    - The output must be at leats five pargraphs long and max ten paragraph.
    - You cannot add information that is not in the files. You can only extract information from the list of files.
    - Always consider important data related to a person from the company, such as the CEO, CFO, or any other relevant person.
    - The output must be translated to Spanish.
    - Topics like: REVENUE, EBITDA, NET INCOME, DEBT, CASH, must be included in the output. If the information is not provided in the key points, say "Information not provided".

    <|output|>
    """

    test_keyparts = ''
    llm = llm_setup(ibm_api_key=ibm_api_key,openai_api_key=openai_api_key, company=company)
    prompt_resumen = PromptTemplate.from_template(template)
    open_chain_resumen = LLMChain(prompt=prompt_resumen, llm=llm)

    # if prints:
    #     print(f'Total of chunks: {len(test_keyparts)}')
    # check time for each iteration
    start = time.time()

    resumen = open_chain_resumen.invoke(resumenes)['text']

    # if prints:
    #     print(f'Chunk: Time{time.time() - start}')
    #     print('-----------')

    # print(resumen)
    # actualizamos
    col_res.update_one({'_id': id_}, {'$set': {'resumen': resumen}})
    return resumen

def comparator_model(text_1_dict,text_2_dict,empresa,openai_api_key=openai_api_key, ibm_api_key=ibm_api_key, company=company):

    text_1 = text_1_dict["summary"]
    text_2 = text_2_dict["summary"]

    name_1 = text_1_dict["name"]
    name_2 = text_2_dict["name"]

    # print('comparando')

#     template = f"""<|text 1 |>
# {name_1}: "{{text_1}}".

# <|text 2 |>
# {name_2}: "{{text_2}}".

# <|system|>
# Perform a comparison between '{name_1}' and '{name_2}', highlighting the key differences in both general and specific contents, including the type of document each text represents (e.g., financial statement, call transcript, interview format). Focus on significant statistical variations related to their temporal contexts, if available, and explicitly mention and compare statistical percentages when discussing increases or decreases. Present your findings in a format that emphasizes the crucial points of distinction without using titles or headings. Ensure that the comparison delves into how these differences contribute to the overall understanding of the context and implications of each summary. Assess the sentiment of each document concerning the highlights in the data of each document and contrast these analyses. The output must adhere strictly to the specified format, beginning each important point with '->' and excluding titles or headings in favor of complete sentences. Use '->' solely to mark the start of each key point, maintaining uniformity in the structure. Every key difference should form a complete sentence, devoid of titles or general concepts, and must be directly relevant to the article without introducing external information. Refrain from repeating key differences and always mention the document by its name. The output should be consistently translated into Spanish, and the summary should be coherent and aligned with the context of the documents.

# <|important|>
# - The output format must be identical to the OUTPUT FORMAT. Indicate with '->' the beginning of each important point.
# - Do not add titles or headings, only complete sentences are allowed.
# - The characters '->' should only be used to indicate the beginning of each key point. Do not use them elsewhere in the summary, and you cannot use another symbol to indicate the start of another point. All should be at the same level to respect the structure.
# - Each key difference must be a complete sentence; do not add titles or general concepts. You cannot divide a sentence into two key points, nor can you divide a key point into sub-points.
# - Each key difference must be relevant to the article.
# - You cannot add information that is not in the article. You can only extract information from the texts.
# - Do not repeat key differences.
# - Always refer to the document by its name.
# - The summary must be coherent and consistent with the context of the documents.
# - The output format of Verbose key differences don´t need to call all the time the name of the document, only the first time.
# - The output must always be translated into Spanish.

# <|output format|>
# **DIFERENCIAS:**
# -> <Verbose key difference 1>.
# -> <Verbose key difference 2>.
# -> <Verbose key difference 3>.
# -> <Verbose key difference 4>.
# -> <Verbose key difference 5>.
# -> ...

# -> **DOCUMENTO 1:**

# <Verbose content analysis of {name_1}>.

# -> **DOCUMENTO 2:**

# <Verbose content analysis of {name_2}>.

# #### RESUMEN DE LAS DIFERENCIAS:
# <Summary of differences content>.

# <|output|>
# """ 
    
#     llm = llm_setup(ibm_api_key=ibm_api_key,openai_api_key=openai_api_key, company=company)
#     prompt = PromptTemplate.from_template(template)
#     open_chain = LLMChain(prompt=prompt , llm=llm)

#     diferencias = open_chain.invoke(input={"text_1":text_1,"text_2":text_2})["text"]
#     print(diferencias)
    iam_token = llm_setup(ibm_api_key=ibm_api_key,openai_api_key=openai_api_key, company=company)
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
        # print("Ultima comparación actualizada")
    else:
        col_comp.insert_one(comp_to_db)
        # print("Se ha creado la última comparación")

    return "\n".join(diferencias.split("->"))



while False:
    df_pending = [x for x in col_pdf.find({'status': {'$ne': 'ready'}})]
    print([x['filename'] for x in df_pending])  
    if len(df_pending) == 0:
        print('No hay archivos pendientes')
    else:
        print('Hay archivos pendientes')
        for index, row in enumerate(df_pending):
            print(f"Archivo: {row['filename']}, Status: {row['status']}")
            print(row['id'])
            # preguntamos al discovery si ya terminó
            r = discovery.get_document(
                project_id=project_id,
                collection_id=collection_id,
                document_id=row['id'],
                ).get_result()
            if r['status'] == 'available':
                print('El archivo ya está disponible')
                response = discovery.query(project_id=project_id, collection_ids=[collection_id], natural_language_query='', count=100).get_result()
                # seleccionamos solo la que corresponde al archivo
                
                selected = [i for i in response['results'] if i['document_id'] == row['id']][0]
                doc_ = dict()
                # Resultados -> response['results'][X]
                # Documentos -> document_id
                # Metadata -> extracted_metadata
                #                      -> numPages
                #                      -> filename
                #                      -> file_type
                # Texto extraido -> only_text
                doc_['id'] = selected['document_id']
                doc_['num_pages'] = selected['extracted_metadata']['numPages']
                doc_['filename'] = selected['extracted_metadata']['filename']
                doc_['filetype'] = selected['extracted_metadata']['file_type']
                doc_['text'] = '\n'.join(selected['only_text'])
                # print(doc_['text']) 

                # Actualizamos en la base de datos
                # col_pdf.update_one({'id': row['id']}, {'$set': {'status': 'ready', 'text': doc_['text']}})

                # Generamos keypoints
                print('Generando keypoints')
                keypoints = keypoints_extr(doc_['text'], openai_api_key, prints=False)
                print('Generando resumen')
                resumen = keypoints_resum(keypoints, openai_api_key, prints=False)
                doc_['keypoints'] = keypoints # lista con keypoints
                doc_['resumen'] = resumen
                print('------------------')
                
                # abrimos el archivo
                # with open(f'{row["doc"]}'[1:], 'rb') as file:
                # #     # encoded_string = base64.b64encode(file.read()).decode('utf-8')
                # #     # doc_['doc'] = encoded_string
                #     pass

                print('Actualizando en la base de datos')
                
                # Actualizamos en la base de datos
                col_pdf.update_one({'id': row['id']}, {'$set': {'keypoints': doc_['keypoints'], 'resumen': doc_['resumen'], 'status': 'ready', 'texto': doc_['text']}})
                print('------------------')
                
    #         break
    resumenes_pendientes = [x for x in col_res.find({'resumen': 'XXX'})]
    for res_pen in resumenes_pendientes:
        print('Generando resumen empresarial')
        print(f'Empresa: {res_pen["empresa"]}, Periodo: {res_pen["periodo"]}')
        resumen = resumen_empresarial(res_pen, openai_api_key, prints=False)
    time.sleep(60)
    


# <- FastAPI ->



