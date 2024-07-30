import requests

url = "https://8cc4-118-235-88-137.ngrok-free.app/hihi"

# get method
response = requests.get(url)
print(response.text)