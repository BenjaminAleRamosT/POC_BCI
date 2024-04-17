import requests

def beavertoken():
    """
    token_endpoint = 'https://login.microsoftonline.com/b046794a-0819-41f6-9515-b80926606a1b/oauth2/v2.0/token'
    request_body = {
        'grant_type': 'client_credentials',
        'client_id': 'a63011af-07ff-4088-b397-a4195012a4b3',
        'client_secret': 'XHa8Q~sw7nNTeIFb-cHtmXtIlDsjRWy~gEWt4cm7',
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
    }
    
    """
    token_endpoint = 'https://login.microsoftonline.com/b046794a-0819-41f6-9515-b80926606a1b/oauth2/token'
    request_body = {
        'grant_type': 'client_credentials',
        'client_id': 'a63011af-07ff-4088-b397-a4195012a4b3',
        #'client_id': '90d38be2-472b-4870-8aaa-9722c1713b8b',
        'client_secret': 'XHa8Q~sw7nNTeIFb-cHtmXtIlDsjRWy~gEWt4cm7',
        'scope': 'Report.Read.All',
        'resource': 'https://analysis.windows.net/powerbi/api'
    }
    
    response = requests.post(token_endpoint, data=request_body)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
    else:
        pass
        #print('Error en la solicitud:', response.text)
    
    return access_token

def accessToken():

    url = 'https://api.powerbi.com/v1.0/myorg/groups/48485820-2463-4595-b7e3-851c901e537d/reports/03e320e4-9d78-464f-a88e-53fca11121ea/GenerateToken'

    headers = {
        'Authorization': 'Bearer ' + beavertoken(),
        'Content-Type': 'application/json'
    }

    body = {
        "accessLevel": "Edit"
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        token_data = response.json()
        #print("Token generado:", token_data["token"])
        return token_data["token"]
    else:
        pass
        #print("Error:", response.text)

    return 0