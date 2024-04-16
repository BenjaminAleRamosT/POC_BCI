
import os
import base64
import requests
import streamlit as st
import json
import pandas as pd
import textwrap
from PIL import Image
from io import BytesIO

from pymongo import MongoClient

from tempfile import NamedTemporaryFile

from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from  Backend.credentials.Mongo import get_mongo_client
from Backend.emp.empresa import Empresa


def add_file(filename=None, empresa=None, sector=None, periodo=None, year=None, trimestre=None, doc=None, key=None, resumen=None ):
    st.title('Aplicación de prueba')
    st.subheader('Lectura de archivos csv')
    # Leer el archivo csv
    df = pd.read_csv('files.csv')
    # Desplegar el dataframe
    st.write(df)



# añadimos una nueva fila al df
    new_row = {'filename': filename,
                'empresa': empresa,
                'sector': sector,
                'periodo': periodo,
                'year': year,
                'trimestre': trimestre,
                'doc': doc,
                'key': key,
                'resumen': resumen}
    
    df = df.append(new_row, ignore_index=True) 
    st.write(df)

# editar la fila añadida añadiendo nueva información
    # df.loc[df['filename'] == 'file1', 'empresa'] = 'epico'

    st.write(df)


def get_files(filename='Empresa', period='3Q23', api_key= 'api', client=None):

    # print(f">> Getting files for {filename} in the period {period} using the api")

    # print(os.listdir('../files'))
    # ruta_files = './files.csv'
    year = '20' + period.split('Q')[1]
    quarter = period.split('Q')[0]

    if int(quarter) < 10:
        quarter = '0' + quarter

    #dummy files
    # with open('./dummy_files.csv', 'r') as file:
    #     print(set(file.read().split(',')))


    # print(f"Year: {year}, Quarter: {quarter}, Empresa: {filename}")

    # path
    # path = ruta_files + name + '/' + year 
    # # print(os.listdir(ruta_files + name + '/' + year + '/' + year +quarter))
    # list_files = os.listdir(ruta_files + name + '/' + year + '/' + year +quarter)

    name = 'Empresa'
    if name=='Empresa':
        
        # Lista con 10 archivos falsos pdf con namefile, summary, and url
        fake_files = {
            "file1": {
                "name": "file1",
                "summary": "Resumen del archivo 1",
                "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                "status": "ready"
            },
            "file2": {
                "name": "file2",
                "summary": "Resumen del archivo 2",
                "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                "status": "pending"
            },
            "file3": {
                "name": "file3",
                "summary": "Resumen del archivo 3",
                "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                "status": "ready"
            },  
        }
        # print(f"Fake files: {fake_files.keys()}")


    dict_files = dict()

    client = client
    db = client['ibmclouddb']
    col_pdf = db['pdf']

    # obtenemos todos los files
    for doc in col_pdf.find({'empresa': filename, 'periodo': period}):
       dict_files[doc['filename']] = {
          "id": doc['id'],
           "name": doc['filename'],
          "summary": doc['resumen'],
           "keypoints": doc['keypoints'],
           "url": doc['doc'],
           "status": doc['status']
       }

    # print(f"Files__: {dict_files}")
 
    return dict_files

        
def clear_submit():
    st.session_state["submit"] = False


def create_summary(emp:Empresa,filename:str):
    # buscaremos en la base de datos el te


    


def displayPDF(uploaded_file):
    
    
    # Read file as bytes:
    # bytes_data = uploaded_file.getvalue()
    abrido = False
    if type(uploaded_file) == str:
        if uploaded_file[-3:] != 'pdf':
            uploaded_file = requests.get(uploaded_file).content
        else:
            # print(os.listdir('../files'))
            with open(uploaded_file, 'rb') as file:
                uploaded_file = file.read()

    # Convert to utf-8
    base64_pdf = base64.b64encode(uploaded_file).decode('utf-8')

    # Keep the file on a temp file
    # with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
    #     tmp_file.write(uploaded_file)
    #     abrido = True
    #     print(tmp_file.name)

    # Embed PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width=100% height="600" type="application/pdf"></iframe>'

    # Display file
    st.markdown(pdf_display, unsafe_allow_html=True)
    # st.markdown(f"""
    # <embed src="{tmp_file.name}" width="800" height="800">
    # """, unsafe_allow_html=True)

def get_summary(name='Empresa', period='3Q23', api_key= 'api'):
    return "As riun metrius sintus"

def get_keypoints(transcript, name='Empresa', period='3Q', api_key= 'api'):
    return "Key points"

def get_transcript(file_id, filename, empresa, year, quarter):
    return "transcript"

def get_upload_discovery(uploaded_file, emp, periodo='3Q23'):
    file_ = uploaded_file.getvalue()
    filename = uploaded_file.name
    empresa = emp.name
    periodo = periodo
    year = '20' + periodo.split('Q')[1]
    quarter = periodo.split('Q')[0]

    if int(quarter) < 10:
        quarter = '0' + quarter

    # Watson API credentials
    api_aim = 'YFaSBR1grvzWsCDYxr0ifGafpIl325eVSJFQzGO314mW'
    api_wd = '6EKwQ3DwjeXO5RnsfvG8wAK8A0cVlN6xCReGeXKeeHNz'

    # Watson Discovery credentials
    authenticator = IAMAuthenticator(api_wd)
    discovery = DiscoveryV2(
        version='2024-01-01', #'2020-08-30',
        authenticator=authenticator
    )

    discovery.set_service_url('https://api.us-south.discovery.watson.cloud.ibm.com')

    discovery.list_projects().get_result()['projects']

    # Get the project
    pj_name = 'Onlytext-testing'

    try:
        project = [pj for pj in discovery.list_projects().get_result()['projects'] if pj['name'] == pj_name][0]
    except:
        # print('No se encontró el proyecto')
        return
    # Get the collection
    col_name = 'Onlytext-testing Collection 1'
    try:
        collection = [col for col in discovery.list_collections(project_id=project['project_id']).get_result()['collections'] if col['name'] == col_name][0]
    except:
        # print('No se encontró la colección')
        return

    # print(f"Project: {project['project_id']}")
    # print(f"Collection: {collection['collection_id']}")

    # Guardar temporalmente el archivo
    with NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file_)
    with open(tmp_file.name, 'rb') as fileinfo:
        add_doc = discovery.add_document(
            project_id=project['project_id'],
            collection_id=collection['collection_id'],
            file=fileinfo,
            filename=filename,
        ).get_result()

        # Sube a la bd
        client = get_mongo_client()

        db = client['ibmclouddb']
        col_pdf = db['pdf']

        col_pdf.insert_one({
            'id': add_doc['document_id'],
            'filename': filename,
            'empresa': empresa,
            'sector': emp.sector,
            'periodo': periodo,
            'year': year,
            'trimestre': quarter,
            'doc': file_,
            'keypoints': None,
            'resumen': None,
            'status': add_doc['status']
        })


    

    

    os.remove(tmp_file.name) # Eliminar el archivo temporal
    # print(add_doc)

    return 'response'
    # Wait until is process
    while True:
        try:
            env = discovery.list_environments(project_id=project['project_id']).get_result()['environments'][0]
            break
        except:
            pass

    return


# @st.cache_data
def create_pdf(_emp):
    emp = _emp
    # Creamos un buffer en memoria
    pdf_buffer = BytesIO()

    # Generamos el PDF en el buffer
    with PdfPages(pdf_buffer) as pdf_pages:
        background_image_path = os.path.join( "DATA","img","nuevo_logo_gather_grande.png")

        ################################### Pagina 1 ###################################
        # Cargamos la imagen de fondo
        bg_image = Image.open(background_image_path)
        # Reducimos la opacidad de la imagen
        bg_image.putalpha(int(255 * 0.1))  # Ajusta el 0.1 para cambiar la opacidad
        # Ajustamos la altura de la imagen a 600px
        bg_image = bg_image.resize((int(bg_image.width * 600 / bg_image.height), 400))
        # Creamos una sola figura para el título y la fecha
        plt.figure(figsize=(12, 15))
        # Agregamos la imagen de fondo
        plt.imshow(bg_image, extent=[0, 1, 0, 1], aspect="auto", zorder=-1, transform=plt.gca().transAxes)
        # Agregamos titulo al PDF
        plt.text(0.5, 0.5, f"PoC Resumen {emp.name}", horizontalalignment='center', verticalalignment='center', fontsize=42, fontweight='bold')
        # Agregamos fecha al PDF
        plt.text(0.5, 0.1, 'Fecha de creación: 13-03-2024\nEquipo de trabajo:\nJefa de proyecto: Veronica Tapia\nDesarrolladores: Joaquin Cabello - Juan Manuel Zapata - Joaquin Burdiles'
                 , horizontalalignment='center', verticalalignment='baseline', fontsize=10, fontweight='bold')
        # Desactivamos los ejes
        plt.axis('off')
        # Guardamos la figura en el PDF
        pdf_pages.savefig()
        # Cerramos la figura
        plt.close()

        ################################### Pagina 2 ###################################
        # Creamos una figura nueva para la segunda página
        plt.figure(figsize=(12, 15))
        # Agregamos el título para la segunda página
        plt.text(0.5, 1.1, 'Resumen generado por IBM WatsonX AI', horizontalalignment='center', verticalalignment='top', fontsize=22, fontweight='bold')

        # plt.rcParams['text.usetex'] = True
        # plt.rcParams['text.latex.preamble'] = r'\usepackage{ragged2e}'

        # Creamos una figura nueva para la segunda página
        plt.figure(figsize=(12, 15))
        # Preprocesamos el resumen para evitar interpretación de "$" como fórmulas matemáticas
        # resumen = emp.resumenes[-1]['resumen'].replace('$', '\$')
        # Utilizamos textwrap para ajustar cada párrafo del resumen a un ancho fijo
        # ancho_linea = 70  # Número de caracteres por línea
        # parrafos = resumen.split('\n')
        # resumen_ajustado = '\n'.join(['\n'.join(textwrap.wrap(parrafo, width=ancho_linea)) for parrafo in parrafos])
        # # Agregamos el resumen justificado usando el entorno justify de LaTeX
        # plt.text(0.5, 0.5, r'\justify{' + resumen_ajustado + '}', horizontalalignment='center', verticalalignment='center', fontsize=14)
        # # Desactivamos los ejes
        # plt.axis('off')
        # # Guardamos la figura en el PDF
        # pdf_pages.savefig()
        # # Cerramos la figura

        # Preprocesamos el resumen para evitar interpretación de "$" como fórmulas matemáticas
        resumen = emp.resumenes[-1]['resumen'].replace('$', '\$')
        # Utilizamos textwrap para ajustar cada párrafo del resumen a un ancho fijo
        ancho_linea = 70  # Número de caracteres por línea
        parrafos = resumen.split('\n')
        resumen_ajustado = '\n'.join(['\n'.join(textwrap.wrap(parrafo, width=ancho_linea)) for parrafo in parrafos])
        # Agregamos el resumen escrito en texto con margen simétrico y alineado a la izquierda
        plt.text(0.5, 0.5, resumen_ajustado, horizontalalignment='center', verticalalignment='center', fontsize=14, multialignment='left')
        # Desactivamos los ejes
        plt.axis('off')
        # Guardamos la figura en el PDF
        pdf_pages.savefig()
        # Cerramos la figura
        plt.close()

        ################################### Pagina 3 ###################################
        # Ajustamos el número de subplots para dejar espacio para el título
        fig, axs = plt.subplots(5, 2, figsize=(12, 15))
        # Convertir axs a una lista plana si es necesario
        axs = axs.flatten()
        columnas_graficar = emp.table.columns[1:]
        # Ajustamos el loop para dejar el primer subplot vacío para el título
        for ax, column in zip(axs[0:], columnas_graficar):
            if column != 'Trimestre':
                ax.plot(emp.table['Trimestre'], emp.table[column])
                ax.set_title(column)
                ax.set_xlabel('Trimestre')
                # Colocamos markers en los puntos
                ax.scatter(emp.table['Trimestre'], emp.table[column], color='red')
                # ax.set_xticklabels(emp.table['Trimestre'], rotation=45)
                # Modificamos el ylabel según la condición
                if "Ratio" not in column and "Margen" not in column:
                    ax.set_ylabel(f"{column} (M$)")
                else:
                    ax.set_ylabel(column)
                ax.grid(True)
                # Bajamos la opacidad de la grid
                ax.grid(alpha=0.2)
                # Dejamos en la grid solamente las líneas horizontales y verticales hasta que intersectan en un punto
                ax.grid(which='major', linestyle='-', linewidth='0.2', color='black', alpha=0.2)

        plt.tight_layout()

        # Guardar la figura en el PDF
        pdf_pages.savefig(fig)

        # Cerrar la figura para liberar memoria
        plt.close(fig)

    # Desplazamos el puntero al inicio del buffer
    pdf_buffer.seek(0)

    # Retornamos los bytes del PDF
    return pdf_buffer.getvalue()
