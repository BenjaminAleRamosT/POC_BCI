import streamlit as st
import streamlit.components.v1 as components

def render_js(selected_option):
    # Define el código HTML/JavaScript con la variable de Python



    if selected_option == 'Resumen Sectorial':
        selected_option =  "Falabella', 'Cencosud', 'SMU', 'Hites', 'Forus', 'Tricot', 'Ripley', 'Hites"


    html_code = """<script src="https://cdnjs.cloudflare.com/ajax/libs/powerbi-client/2.23.1/powerbi.js"></script>

      <div id="powerbi-container" style="display: flex; height: 500px; width: 100%"></div>

      <script language="javascript">
      var models = window['powerbi-client'].models;

  var embedConfiguration = {
      type: 'report',
      tokenType: models.TokenType.Aads,
      accessToken: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6InEtMjNmYWxldlpoaEQzaG05Q1Fia1A1TVF5VSIsImtpZCI6InEtMjNmYWxldlpoaEQzaG05Q1Fia1A1TVF5VSJ9.eyJhdWQiOiJodHRwczovL2FuYWx5c2lzLndpbmRvd3MubmV0L3Bvd2VyYmkvYXBpIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvYjA0Njc5NGEtMDgxOS00MWY2LTk1MTUtYjgwOTI2NjA2YTFiLyIsImlhdCI6MTcxMjkzODQxNiwibmJmIjoxNzEyOTM4NDE2LCJleHAiOjE3MTI5NDMzMTEsImFjY3QiOjAsImFjciI6IjEiLCJhaW8iOiJBVlFBcS84V0FBQUF4Y1plVnFzTWxHam1WL1NmczFxTk5XVVFLZlc4RmdnQTllSVdMNmk5U3FqbFExOVB1Tm5XazdKV0FEY0cxMDRZYUxWRjZBYVFZeC9zcktheGRlTUpNemNzV3BFMEM2ZFhMaEJhYkZHZ3ZYWT0iLCJhbXIiOlsicHdkIiwicnNhIiwibWZhIl0sImFwcGlkIjoiODcxYzAxMGYtNWU2MS00ZmIxLTgzYWMtOTg2MTBhN2U5MTEwIiwiYXBwaWRhY3IiOiIwIiwiZGV2aWNlaWQiOiIzZGJhOTk2NC00ZTE4LTQ0MjktYmRmNy1jZjhhMjdmOTMzNDMiLCJmYW1pbHlfbmFtZSI6IlJhbW9zIiwiZ2l2ZW5fbmFtZSI6IkJlbmphbWluIiwiaXBhZGRyIjoiMjAwLjgzLjIwNy4yNDEiLCJuYW1lIjoiQmVuamFtaW4gUmFtb3MiLCJvaWQiOiJkNmZiMjljMS1lZTFmLTQ2Y2YtOGMxZS01MDEyYmRkNThlYjYiLCJwdWlkIjoiMTAwMzIwMDM2RUIzNDRFMSIsInJoIjoiMC5BUzBBU25sR3NCa0k5a0dWRmJnSkptQnFHd2tBQUFBQUFBQUF3QUFBQUFBQUFBRDNBR1UuIiwic2NwIjoidXNlcl9pbXBlcnNvbmF0aW9uIiwic2lnbmluX3N0YXRlIjpbImttc2kiXSwic3ViIjoiNVFPY283ZVQzZElEMHI1a3hBQ0I3VnlRN18xWUlUWjZFUmFNR184WTAzUSIsInRpZCI6ImIwNDY3OTRhLTA4MTktNDFmNi05NTE1LWI4MDkyNjYwNmExYiIsInVuaXF1ZV9uYW1lIjoiYmVuamFtaW4ucmFtb3NAZ2F0aGVyY29uc3VsdG9yZXNsdGRhLm9ubWljcm9zb2Z0LmNvbSIsInVwbiI6ImJlbmphbWluLnJhbW9zQGdhdGhlcmNvbnN1bHRvcmVzbHRkYS5vbm1pY3Jvc29mdC5jb20iLCJ1dGkiOiJYU01ZTEl4eHAwbUQ1UDFJWFdvTkFBIiwidmVyIjoiMS4wIiwid2lkcyI6WyJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXX0.CSX1JDfn_jaoac-iLmqx39AxF4Wm8eEn1z9ChnQ8_bLzLEOON7F_zF8I2fPUoLcQGwacUUUwzcKP4omSqUWbUBZ9dcTOaE7enhKevhi5ZP4fpKql04o94Uis5mepR1zAjcyrXA0OQ7N2VhYUaR5b7DOp4axZUvEyzpvKhlKU3sBe8tCmRaSfQED18345U6o-ahQxLdcim6a9gv2Cmpm_R2DjZnRXN8WsejL3eprvIec8C41TUPVXBN2mfwodVRXgKNc7INB9jrR-xA21epuAGt6bXGd11OXXweY3dCzuxzeg2RbxzjE3vRI5GHLOMUqPJpVxy9NtKiuuwqnpTQKthQ',
      embedUrl: 'https://app.powerbi.com/reportEmbed?reportId=03e320e4-9d78-464f-a88e-53fca11121ea&groupId=48485820-2463-4595-b7e3-851c901e537d&w=2&config=eyJjbHVzdGVyVXJsIjoiaHR0cHM6Ly9XQUJJLVNPVVRILUNFTlRSQUwtVVMtQy1QUklNQVJZLXJlZGlyZWN0LmFuYWx5c2lzLndpbmRvd3MubmV0IiwiZW1iZWRGZWF0dXJlcyI6eyJ1c2FnZU1ldHJpY3NWTmV4dCI6dHJ1ZX19',
      id: '8d5d11b5-12ab-4944-ab6f-9361b8258ed2',
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
              for (var i = 0; i < visuals.length; i++) {
                  var visual = visuals[i];
                  console.log("Visual ID:", visual.type, i);
                  // Puedes trabajar con cada visual aquí
              }
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