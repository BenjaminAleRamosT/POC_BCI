import requests

def beavertoken():

    token_endpoint = 'https://login.microsoftonline.com/b046794a-0819-41f6-9515-b80926606a1b/oauth2/v2.0/token'
    request_body = {
        'grant_type': 'client_credentials',
        'client_id': 'a63011af-07ff-4088-b397-a4195012a4b3',
        'client_secret': 'RnX8Q~8jepy95np7DPCn~PwbtIueGajKMn6haaY_',
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
    }

    response = requests.post(token_endpoint, data=request_body)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
    else:
        print('Error en la solicitud:', response.text)
    
    return access_token

def accessToken():

    url = 'https://api.powerbi.com/v1.0/myorg/groups/48485820-2463-4595-b7e3-851c901e537d/reports/03e320e4-9d78-464f-a88e-53fca11121ea/GenerateToken'

    headers = {
        'Authorization': 'Bearer ' + beavertoken(),
        'Content-Type': 'application/json'
    }

    body = {
        "datasetId": "866b320b-c153-4abe-b045-8b4c5f01d543",
        "accessLevel": "Edit"
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        token_data = response.json()
        print("Token generado:", token_data)
        return token_data["token"]
    else:
        print("Error:", response.text)

    return 0