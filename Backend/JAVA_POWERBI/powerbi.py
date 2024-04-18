import streamlit as st
import streamlit.components.v1 as components
import Backend.JAVA_POWERBI.tokens as tk

def render_js(selected_option):
    # Define el código HTML/JavaScript con la variable de Python

    if selected_option == 'Resumen Sectorial':
        selected_option =  "Falabella', 'Cencosud', 'SMU', 'Hites', 'Forus', 'Tricot', 'Ripley"


    html_code = """<script src="https://cdnjs.cloudflare.com/ajax/libs/powerbi-client/2.23.1/powerbi.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1/jquery.js"></script>

      <div id="powerbi-container" style="display: flex; height: 500px; width: 100%"></div>

      <script language="javascript">
      var models = window['powerbi-client'].models;

  var embedConfiguration = {
      type: 'report',
      id: '03e320e4-9d78-464f-a88e-53fca11121ea',
      tokenType: models.TokenType.Embed,
      permissions: models.Permissions.All,
      viewMode: models.ViewMode.ReadWrite,
      accessToken: '"""+ str(tk.accessToken()) +"""',
      embedUrl: 'https://app.powerbi.com/reportEmbed?reportId=03e320e4-9d78-464f-a88e-53fca11121ea&groupId=48485820-2463-4595-b7e3-851c901e537d&w=2&config=eyJjbHVzdGVyVXJsIjoiaHR0cHM6Ly9XQUJJLVNPVVRILUNFTlRSQUwtVVMtQy1QUklNQVJZLXJlZGlyZWN0LmFuYWx5c2lzLndpbmRvd3MubmV0IiwiZW1iZWRGZWF0dXJlcyI6eyJ1c2FnZU1ldHJpY3NWTmV4dCI6dHJ1ZX19',
      settings: {
          filterPaneEnabled: false,
          navContentPaneEnabled: false,
          background: models.BackgroundType.Transparent
      }};

  var dashboardContainer = document.getElementById('powerbi-container');

  var dashboard = powerbi.embed(dashboardContainer, embedConfiguration);

  var page
  var visual
  const basicFilter = {
        $schema: "http://powerbi.com/product/schema#basic",
        target: {
          table: "Empresas",
          column: "Empresa"
        },
        operator: "In",
        values: ['"""+selected_option+"""'],
        filterType: models.FilterType.BasicFilter
      };

  dashboard.on('loaded', function() {
  dashboard.getPages().then(function (pages) {
      // Supongamos que queremos trabajar con la primera página

      page = pages[0];
      console.log(page);

      page.getVisuals().then(function(visuals) {
              // 'visuals' es un array con todos los visuales de la página
              //for (var i = 0; i < visuals.length; i++) {
              //    var visual = visuals[i];
              //    console.log("Visual ID:", visual.type, i);
                  // Puedes trabajar con cada visual aquí
              //}
          slicerVisual = visuals[1];
          console.log(slicerVisual)

          slicerVisual.getSlicerState().then(function(slicerState) {

              console.log(slicerState);


          }).catch(function(error) {
              console.error("Error getting slicer state:", error);
          });


          slicerVisual.setSlicerState({

                  filters: [basicFilter]

              }).then(function () {
                  console.log("Slicer state set");
              }).catch(function (error) {
                  console.error("Error setting slicer state:", error);
              });

          }).catch(function(error) {
              console.error("Error al obtener los visuales:", error);
          });
  });
  });

      </script>
    """
    components.html(html_code, height=516)