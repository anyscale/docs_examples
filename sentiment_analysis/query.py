import requests

resp = requests.get(
    "http://localhost:8000/predict", params={"text": "Anyscale workspaces are great!"}
)
print(resp.json())
