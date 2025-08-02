import requests

move_data = {"move": "e2e4"}  # example move

try:
    response = requests.post("http://localhost:8000/update-move", json=move_data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("❌ Failed to send request:", e)
