import requests

url = "http://127.0.0.1:8000/api/view1"
answer = requests.get(url)
print(answer.headers)
print(answer.json())