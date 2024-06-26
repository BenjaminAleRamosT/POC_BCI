import streamlit as st
import pandas as pd

# llamamos la clase empresa ubicada en ../Backend/empresa.py
from Backend.emp.empresa import Empresa

from Backend.emp.empresa import Empresa
from Backend.emp.tools import displayPDF, get_files, clear_submit, get_summary, get_upload_discovery, create_pdf
from Backend.LLM.key_extractor import difference_texts

from pymongo import MongoClient
from Backend.credentials.Mongo import get_mongo_client

import time
from  Backend.JAVA_POWERBI.powerbi import render_js


df = pd.DataFrame({
    'Trimestre actual': [None]*7,
    'YoY': [None]*7,
    'QoQ': [None]*7,
    'Acumulado': [None]*7,
}, index=['Ingresos', 'Mg. Bruto', 'Mg EBITDA', 'Utilidad', 'Deuda Financiera', 'Caja', 'Ratio Deuda Financiera neta/ EBITDA'])

def show_pending_files(emp, files_pending):
    if files_pending:
        st.write("Archivos pendientes:")

        for archivo in files_pending.keys():
            with st.status("Downloading data..."):
                st.write("Searching for data...")
                time.sleep(2)
                st.write("Found URL.")
                time.sleep(1)
                st.write("Downloading data...") 
                time.sleep(1)

            # st.button('Rerun')
            st.success('Done!')
            emp.files[archivo]['status'] = 'ready' 
            # emp.files = get_files(emp.name)
            st.write(f"El archivo {files_pending[archivo]['name']} está pendiente de procesamiento.")


def main_page(emp ,periodo='3Q23'):
    # #print(">> main_page")

    # <------------------------------------| Obtenemos Data |------------------------------------> #
    general_path = "./DATA/Empresas.csv"

    emp.get_table()
    emp.get_files()
    emp.get_resumen()
    # #print('obtenemos ultima comparación')
    emp.get_last_comparation()
    emp.procesar_documentos_pendientes()
    
    # #print(emp.files)

    name=emp.name
    files = emp.files
    files_dispo = {}
    files_pending = {}
    # #print('pasamos')

    # <------------------------------------| Asignamos Data |------------------------------------> #
    ### GENERAMOS LAS TABLAS ###
    emp.process_data(general_path)
    #############################

    # #print('Files:', files.keys())
    # #print(files['file1']['status'])

    for key, value in files.items():
        if value['status'] == 'ready':
            files_dispo[key] = value
            
    
    for key, value in files.items():
        if value['status'] != 'ready':
            files_pending[key] = value

    # #print('Files pending:', files_pending.keys())
    # #print('Files dispo:', files_dispo)

    table = emp.table



    # <------------------------------------| Titulo |------------------------------------> #
    
    
    
    st.markdown(f"# {name} - {periodo} 📊", unsafe_allow_html=True)
    st.markdown('----')
    
    # Ajuste para alinear el título secundario a la izquierda
    st.markdown("##### NOTA: Al momento de subir un documento, se debe esperar a que se procese y generar un resumen, luego se habilitará el comparador de documentos para aquel documento")
    st.markdown("### Resumen Empresarial ‍💼")
    st.markdown("###### Principales Estados Financieros")
    
    
    # <------------------------------------| POWER BI |------------------------------------> #
    # st.markdown("### Power BI 📊")
    render_js(emp.name)

    # <------------------------------------| Tabla |------------------------------------> #

    st.table(emp.table.set_index('Trimestre'))
    st.markdown('----')
    

    # <------------------------------------| Gráfico |------------------------------------> #
    # st.markdown('https://app.powerbi.com/view?r=eyJrIjoiMTAxODExM2MtYjUyZC00YTFiLWI2OTEtY2Y5ZjhjMGYwOGI4IiwidCI6ImIwNDY3OTRhLTA4MTktNDFmNi05NTE1LWI4MDkyNjYwNmExYiIsImMiOjR9', unsafe_allow_html=True)
    
    # fig = emp.empresa_graph()
    # st.plotly_chart(fig, use_container_width=True)
    st.markdown('----')


    # <------------------------------------| Resumen |------------------------------------> #

    st.markdown("### Resumen del trimestre📄✨")

    coliz, colder = st.columns([20,70])

    # Sección izquierda
    with coliz:
        # Boton de "Generar Resumen"
        if st.button("Generar Resumen"):
            if emp.archivos_seleccionados:
                with st.spinner('Generando resumen...'):
                    print(emp.archivos_seleccionados[0][0])
                    archivo = emp.archivos_seleccionados[0][0]
                    summary =  emp.create_summary(archivo)
                    key_points = emp.create_keypoints(archivo)
                    if summary == 1:
                        st.write("No se encontró el archivo seleccionado.")
                    else:
                        st.write("Resumen generado.")
                        # actualizamos el resumen en la base de datos
                        emp.col_pdf.update_one({'filename': archivo}, {'$set': {'resumen': summary, 'keypoints': key_points}})
                
                    
            else:
                with colder:
                    st.write("No hay archivos seleccionados para generar resumen.")
        
        # Mostrar resumen
        if emp.resumenes:
            # Mostrar resumen de archivos
            st.write("| Documentos utilizados para el resumen:")
            for archivo in emp.resumenes[-1]['files']:
                st.write(f"> {archivo['filename']}")
            with colder:
                # Mostrar tabla con archivos
                # #print(len(emp.resumenes))
                if emp.resumenes:
                    # st.write(f"Resumen del {periodo}:")
                    r = emp.resumenes[-1]['resumen'].replace('$', '\$' )
                    if r == 'XXX':
                        
                        st.write("Generando resumen...")
                    else:
                        st.write(f'<div style="text-align: justify;">{r}</div>', unsafe_allow_html=True)
                st.write("")

    if emp.resumenes:
        f= create_pdf(emp)

        btn = st.download_button(
                    label="Descargar PDF",
                    data=f,
                    file_name=f"Resumen_{emp.name}.pdf",
                    mime="application/pdf",
                )
        if btn:
            with st.spinner('Generando PDF...'):
                time.sleep(2)
            st.success('Listo!')
        
        
    
    st.markdown('----')
    # <------------------------------------| Archivos |------------------------------------> #

    # Sección de archivos
    st.markdown("### Administrador de Archivos 📁")
    
    # Creamos dos columnas para las secciones inferiores
    col3, col4 = st.columns([35,65])

    # <------------------------------------| Sección Izquierda |------------------------------------> #

    with col3:
        with st.container():
            st.markdown("""
                <style>
                .stContainer > div > div {
                    overflow-x: auto; /* Habilitar desplazamiento horizontal */
                }
                .stCheckbox > div {
                    border: 2px solid #4CAF50; /* Color del borde */
                    border-radius: 5px; /* Bordes redondeados */
                    padding: 5px; /* Espaciado interior */
                    margin-bottom: 5px; /* Espaciado entre checkboxes */
                    white-space: nowrap; /* Asegurar que el texto no se envuelva */
                }
                </style>
                """, unsafe_allow_html=True)

            

            st.write("Selecciona los archivos:")

            # <------------------------------------| Checkboxes |------------------------------------> #
            
            for archivo in files_dispo.keys():
                # #print(archivo)
                if st.checkbox(files_dispo[archivo]["name"]):
                    if (archivo, files_dispo[archivo]['url'], files_dispo[archivo]['id'], files_dispo[archivo]['summary'], files_dispo[archivo]['keypoints']) not in emp.archivos_seleccionados:
                        emp.archivos_seleccionados.append((archivo, files_dispo[archivo]['url'], files_dispo[archivo]['id'], files_dispo[archivo]['summary'], files_dispo[archivo]['keypoints']))
                else:
                    
                    emp.archivos_seleccionados = [x for x in emp.archivos_seleccionados if x[0] != archivo]
            if not files_dispo:
                st.write("> No hay archivos disponibles.")
            

            # <------------------------------------| Archivos pendientes |------------------------------------> #
            if files_pending:
                st.write("Procesando Archivos: ")

                for archivo in files_pending.keys():
                    st.write(f"🔄 {files_pending[archivo]['name']}")
            #         with st.status("Downloading data..."):
            #             st.write("Searching for data...")
            #             time.sleep(2)
            #             st.write("Found URL.")
            #             time.sleep(1)
            #             st.write("Downloading data...") 
            #             time.sleep(1)
 
            #         # st.button('Rerun')
            #         st.success('Done!')
            #         emp.files[archivo]['status'] = 'ready' 
            #         # emp.files = get_files(emp.name)
            #         st.write(f"El archivo {files_pending[archivo]['name']} está pendiente de procesamiento.")
        # <------------------------------------| Casilla de Subida Archivos |------------------------------------> #

        st.button("Actualizar", on_click=st.balloons)

        if "file_uploader_key" not in st.session_state:
            st.session_state["file_uploader_key"] = 0

        if "uploaded_files" not in st.session_state:
            st.session_state["uploaded_files"] = []

        with st.container(border=True):
            uploaded_file = st.file_uploader(
                "Upload some files",
                accept_multiple_files=False,
                key=st.session_state["file_uploader_key"],
            )


            if st.button("Subir archivo"):
                # Subida de archivos
                if uploaded_file:
                    st.session_state["uploaded_files"].append(uploaded_file)
                    st.write("Archivo subido.")
                # Eliminar del cache
                st.session_state["file_uploader_key"] += 1

                # <--| Función subida de coumento |--> #
                file_upload = get_upload_discovery(uploaded_file, emp)

                emp.pending_files.append(file_upload)
                
                st.rerun()

        

    # <------------------------------------| Sección Derecha |------------------------------------> #       

    # <--| Sección de visualización de archivos |--> #
    with col4:
        st.write("Visualización Archivos")

        col1, _ ,col2 = st.columns([25,50,25], gap="small")

        # Intento de botón "Archivo Anterior" en la primera columna (izquierda)
        with col1:
            st.write("") 
            if st.button("Archivo Anterior"):
                
                if emp.archivos_seleccionados:
                    elemento = emp.archivos_seleccionados.pop(0)
                    # #print(f"Elemento: {elemento}")
                    # #print(f"Archivos seleccionados: {emp.archivos_seleccionados}")
                    emp.archivos_seleccionados.append(elemento)
    
        # Intento de botón "Archivo Siguiente" en la segunda columna (derecha)
        with col2:
            st.write("")
            if st.button("Archivo Siguiente"):
                if emp.archivos_seleccionados:
                    elemento = emp.archivos_seleccionados.pop(-1)
                    emp.archivos_seleccionados = [elemento] + emp.archivos_seleccionados

        # Función despliega el archivo pdf seleccionado
                
        if uploaded_file:
            ar = (uploaded_file.name, uploaded_file.getvalue())
            if ar not in emp.archivos_seleccionados:
                emp.archivos_seleccionados = [ar] + emp.archivos_seleccionados
                
        else:
            emp.archivos_seleccionados = [x for x in emp.archivos_seleccionados if x[0] in files.keys()]
            
        
        if emp.archivos_seleccionados:
            st.markdown(
    f"""
    <div style="background-color:#f0f2f6; padding:10px; border-radius:5px;">
        <h4 style="color:#333;">Desplegando: {emp.archivos_seleccionados[0][0]}</h4>
    </div>
    """,
    unsafe_allow_html=True
)
            # Files desplegar
            if emp.archivos_seleccionados:
                displayPDF(emp.archivos_seleccionados[0][1])

    st.markdown('----')

    # #print('Archivos Seleccionados:',[x[0] for x in emp.archivos_seleccionados])


    # <------------------------------------| Resumen & Keypoints |------------------------------------> #

    st.markdown("### Resumen📝")

    # Sección de resumen y keypoints
    # 3 resumen 
    # 4 keypoints
    if emp.archivos_seleccionados:
        if len(emp.archivos_seleccionados[0]) > 2:
            r = emp.col_pdf.find_one({'filename': emp.archivos_seleccionados[0][0]})['resumen']
            st.write(f'<div style="text-align: justify;">{r}</div>', unsafe_allow_html=True)
            st.markdown("### Puntos Clave🔑")
            keypoint = emp.col_pdf.find_one({'filename': emp.archivos_seleccionados[0][0]})['keypoints']
            # reemplzamos los $ por \$
            keypoint = keypoint.replace('$', '\$')
            # REEMPLAZAMOS LOS a/a por en comparación con el año anterior
            keypoint = keypoint.replace('a/a', 'en comparación con el año anterior')
            puntos_clave = keypoint.split('-')  # Asumiendo que los puntos están separados por '-'
            puntos_clave = [p.strip() for p in puntos_clave if p.strip()]  # Eliminar espacios en blanco y elementos vacíos
            # Crear una lista en Markdown
            markdown_list = '\n'.join([f"- {p}" for p in puntos_clave])
            # spliteamos por - y luego agreagos como puntos en un formato de lista en markdown
            st.write(f'{markdown_list}')


    else:
        st.write("No hay archivos seleccionados")

    st.write("---")
    #----------------------| Comparador de documentos |----------------------#
    to_comparate = {}

    st.markdown("### Comparador de Documentos 📚")
    # creemos dos subcolumnas separadas por una línea vertical
    col5, col6 = st.columns([50,50])
    text_box = st.empty()

    with text_box:
        if emp.last_comparation:
            st.markdown("#### Última comparación:")
            document_1 = emp.last_comparation['Filenames'][0]
            document_2 = emp.last_comparation['Filenames'][1]

            st.write(f"Archivos comparados: {document_1} y {document_2}")
            st.write(f"Diferencias encontradas: {emp.last_comparation['Diferencias']}")
        # Sección izquierda
        # Crear una selectbox en cada columna
        selected_file1 = col5.selectbox('Selecciona un archivo:', files_dispo, key='comparar_1')
        selected_file2 = col6.selectbox('Selecciona otro archivo:', files_dispo, key='comparar_2')

    # veamos si existe una comparación previa con selected_file1 y selected_file2
    # creamos un bloque para futuramente reemplazarlo por la comparación
    
# Diccionario para comparar archivos
    
    # Botón para agregar archivos seleccionados al diccionario
    if st.button('Comparar archivos'):
        if selected_file1 != selected_file2:
            # Seleccionamos el documento
            text_1_dict = files_dispo[selected_file1]
            text_2_dict = files_dispo[selected_file2]

            #Comparar documentos
            # #print("Comparando documentos...")
            summary_1 , summary_2 = text_1_dict["summary"], text_2_dict["summary"]
            differences = difference_texts(summary_1, summary_2)
            # reemplacemos todo lo que tenga escito text_box por el resultado de la comparación
            text_box.empty()

            with text_box:
                st.markdown("### Diferencias encontradas:")
                st.write(f'<div style="text-align: justify;">{differences}</div>', unsafe_allow_html=True)
            ### Subir a base de datos
            emp.last_comparation = {"Filenames":[selected_file1,selected_file2], "Diferencias": differences}

            emp.client['ibmclouddb']["differences"].insert_one(emp.last_comparation)
        else:
            st.write("No es posible comparar el mismo archivo.")


    st.write("---")

#----------------------| Retail |----------------------#
def retail_page(name='Retail', sector='Retail', periodo='3Q23', client=get_mongo_client()):
    # #print('------------------------')
    # #print('>>> ', st.session_state['empresa'])
    # st.session_state["empresa"] = Empresa(name, sector, periodo, page)
    try:
        if st.session_state["empresa"].name != name :
            # #print("Cambio de empresa")
            # Eliminar del cache
            st.session_state["file_uploader_key"] += 1
            

            st.session_state["empresa"] = Empresa(name, sector, periodo)

            # #print('>>> ', st.session_state['empresa'])
            # st.rerun()
        # elif st.session_state["empresa"].sector != sector:
        #     #print("Cambio de sector")
        #     st.session_state["empresa"] = Empresa(name, sector, periodo, page)
        #     st.rerun()
        # elif st.session_state["empresa"].periodo != periodo :
        #     #print("Cambio de periodo")
        #     st.session_state["empresa"] = Empresa(name, sector, periodo, page)
        #     st.rerun()
        else:
            # #print("No hay cambios")
            pass
    except:
        # #print("No hay empresa")
        pass

        st.session_state["empresa"] = Empresa(name, sector, periodo, client)

    emp = st.session_state["empresa"]

    # st.markdown(f"# {name} 🎈")
    st.sidebar.markdown('----')
    st.sidebar.markdown(f"# Información seleccionada")
    st.sidebar.markdown(f"### > {sector} 🛍️")
    st.sidebar.markdown(f"### > {name} 🏢")
    st.sidebar.markdown(f"# Periodo:")
    st.sidebar.markdown(f"# {periodo} ")
    st.sidebar.markdown('----')
    main_page(emp)
