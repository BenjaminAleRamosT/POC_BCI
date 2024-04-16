import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv

from Backend.credentials.Mongo import get_mongo_client
from Frontend.retail_pages.retail import main_page, retail_page
from pymongo import MongoClient
from pymongo.server_api import ServerApi


print(os.environ.get("CONNECTION_STRING"))



page_names_to_sector = {
    "Retail": 'main_page',
}

st.set_page_config(layout="wide",
                   page_icon="📈")

# instanciar cliente de mongo
client = get_mongo_client()


selected_sector = st.sidebar.selectbox("Selecciona Sector", page_names_to_sector.keys())

with open('Frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

components.html("""
    
  <script>
  window.watsonAssistantChatOptions = {
    integrationID: "ff24df6c-2bd2-4aa5-8b69-653f6cd4b5a3", // The ID of this integration.
    region: "au-syd", // The region your integration is hosted in.
    serviceInstanceID: "841cdf74-d232-48a9-880d-39c47a091537", // The ID of your service instance.
    onLoad: async (instance) => { await instance.render(); }
  };
  setTimeout(function(){
    const t=document.createElement('script');
    t.src="https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + (window.watsonAssistantChatOptions.clientVersion || 'latest') + "/WatsonAssistantChatEntry.js";
    document.head.appendChild(t);
  });
</script>
                """, height=318)
                
              



# Add logo bottom of the sidebar
img_ = os.path.join('DATA','img','nuevo_logo_gather_grande.png')

if selected_sector == "Retail":
    page_names_to_empresa= {
    "Resumen Sectorial": main_page,
    "otro": retail_page,
    }
    page_names_to_empresa_list = ['Resumen Sectorial', 'Falabella', 'Cencosud', 'SMU', 'Hites', 'Forus', 'Tricot', 'Ripley']
    
    selected_page_2 = st.sidebar.selectbox("Selecciona Empresa", page_names_to_empresa_list)

    # Eliminar del cache
    # st.session_state["file_uploader_key"] += 1

    if selected_page_2 != "Resumen Sectorial":
        
        page_names_to_empresa['otro'](name=selected_page_2, client=client)
else:
    selected_page_2 = st.sidebar.selectbox("Selecciona Empresa", ["Select"])

 

st.sidebar.image(img_, use_column_width=True)


