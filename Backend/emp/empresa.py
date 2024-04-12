import streamlit as st
from .tools import get_files
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math

class Empresa:
    def __init__(self, name, sector, periodo,cliente):
        self.name = name
        self.sector = sector
        # self.page = page
        self.periodo = periodo

        self.table = None

        # Diccionario para rastrear los archivos seleccionados, la clave es el archivo y el valor es un booleano de su estado
        self.archivos_seleccionados = None

        self.files = None

        self.displayer = 2

        self.pending_files = []


        self.resumenes = []

        self.last_comparation = None

        self.client = cliente
        
    def __str__(self):
        return f"{self.name} is a company in the {self.sector} sector"

    def __repr__(self):
        return f"{self.name} is a company in the {self.sector} sector"
    
    

    # def show_page(self):
    #     self.page(self.name)
    def generar_resumen(self):
        # Creamos una base de datos llamada 'test_resumenes'
        db = self.client['test_pdf']
        col_pdf = db['pdf']
        # Creamos una colección llamada 'resumenes'
        col_resumenes = db['resumenes']
        resumen = {'empresa': self.name, 'periodo': self.periodo, 'files': [x for x in col_pdf.find({'empresa': self.name, 'periodo': self.periodo, 'status':'ready'})], 'resumen': 'XXX'}
        col_resumenes.insert_one(resumen)
        return
    
    def get_files(self):
        print('getting files')
        
        if self.files == None:
            # print(f"khgkjgjkhg {self.archivos_seleccionados} no está en archivos seleccionados")
            print('>>>>>>>>>>>>>No tiene archivos')
            self.files = get_files(self.name, client=self.client)
            self.archivos_seleccionados = []
        else:
            print('Ya tiene archivos')
            self.files = get_files(self.name, client=self.client)
            # for archivo in self.files:
            #     if archivo not in self.archivos_seleccionados:
            #         print(f"Archivo {self.archivos_seleccionados} no está en archivos seleccionados")
            #         self.archivos_seleccionados[archivo] = False

    def get_table(self):
        self.table = "table"

    def get_resumen(self):
        print('obtenemos resumenes')
        # Creamos una base de datos llamada 'test_resumenes'
        db = self.client['test_pdf']
        print('db')
        # Creamos una colección llamada 'resumenes'
        col_resumenes = db['resumenes']
        print('col')

        self.resumenes = list(col_resumenes.find({"empresa": self.name, "periodo": self.periodo}).sort("_id", -1).limit(2))
        
        print('resumenes')
    def get_last_comparation(self):
        db = self.client["test_pdf"]
        col = db["comparaciones"]
        print(f"Buscando comparaciones de {self.name}")
        self.last_comparation = [x for x in col.find({"empresa": self.name})]

        

    #<----------------- XBRL----------------->
    def process_data(self,path_general):

        empresa = self.name

        df = pd.read_csv(path_general)
        df = df[df["Empresa"] == empresa].drop(columns=["Empresa"])
        df.index.name = None
        
        df = df.reset_index(drop=True)
        discri = ["Mg","Margen","Ratio","Trimestre","Empresa"]

        for col in df.columns:
            if not any(x in col for x in discri):
                df[col] = df[col].str.replace(",", ".").astype(float)
                # Pasemos los valores a millones
                if df[col].max() > 1000:
                    df[col] = df[col].apply(lambda x: x/1000000)
                    
                    
            else:
                if col not in ["Trimestre","Empresa"]:
                        # transformar a float
                        df[col] = df[col].str.replace(",", ".").astype(float)
                

        self.table = df


    def empresa_graph(self):
        df = self.table

        fig = make_subplots(
            rows=1, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            specs=[[{"type": "scatter"}]]
        )

        columns_to_compare = [col for col in df.columns if col not in ['Trimestre', 'Unidad']]

        # Añadir trazos para Bar y Scatter inicialmente
        for column in columns_to_compare:
            fig.add_trace(go.Bar(x=df['Trimestre'], y=df[column], name=column, marker=dict(line=dict(color='black', width=1))), row=1, col=1)

        for column in columns_to_compare:
            fig.add_trace(go.Scatter(x=df['Trimestre'], y=df[column], mode='lines+markers', name=column, visible=False, marker=dict(line=dict(color='black', width=1))), row=1, col=1)

        traces_per_type = len(columns_to_compare)

        # Configurar la visibilidad de las trazas para cada tipo de gráfico
        bar_visibility = [True] * traces_per_type + [False] * traces_per_type
        scatter_visibility = [False] * traces_per_type + [True] * traces_per_type

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=list([
                        dict(label="Barplot", method="update",
                            args=[{"visible": bar_visibility},
                                {"title": "Barplot por Trimestre", "showlegend": True}]),
                        dict(label="Scatter Plot", method="update",
                            args=[{"visible": scatter_visibility},
                                {"title": "Scatter Plot por Trimestre", "showlegend": True}])
                    ]),
                    direction="right", pad={"r": 10, "t": 10}, showactive=True, x=0, xanchor="left", y=-0.15, yanchor="top"
                ),
            ],
            showlegend=True
        )

        fig.update_layout(height=800, title_text="Análisis de EE.FF por Trimestre")

        return fig




    