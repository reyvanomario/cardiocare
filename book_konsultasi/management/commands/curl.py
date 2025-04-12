import requests

url = "http://127.0.0.1:8001/api/register/"

data = {
    "email": "athaillahsifaa@gmail.com",
    "username": "athaillah1",
    "password": "Rahasia123!",
    "nomor_telepon": "+628123456789"
}

headers = {
    "Content-Type": "application/json"
}

# Sending POST request to the API with JSON data and headers
response = requests.post(url, json=data, headers=headers)

# Printing the raw response text
print("Raw response:", response.text)

# Printing the status code of the response
print("Status Code:", response.status_code)

# If the response is in JSON format, this will decode it to a dictionary
# If the response is not JSON, it will raise an exception
try:
    print("Response:", response.json())
except ValueError:
    print("Response is not in JSON format")
