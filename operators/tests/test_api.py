import requests


def authenticate_operator(login, password):
    url = "http://127.0.0.1:8000/operators/authenticate_machine/"
    payload = {
        "login": login,
        "password": password,
    }
    response = requests.post(url, json=payload)

    print(f"Status: {response.status_code}, Response: {response.text}")

    if response.status_code == 200:
        try:
            data = response.json()
            unique_id = data.get("unique_id")
            print("Аутентификация успешна")
            return unique_id
        except ValueError:
            print("Ошибка: сервер вернул невалидный JSON")
            return None
    else:
        print(f"Ошибка аутентификации (HTTP {response.status_code})")
        try:
            error_msg = response.json().get("message", response.text)
        except ValueError:
            error_msg = response.text
        print("Подробности:", error_msg)
        return None


authenticate_operator(
    "user2", 
    "nqOSwzSVo_%]"
)