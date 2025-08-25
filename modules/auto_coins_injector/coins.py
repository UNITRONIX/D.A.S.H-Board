import requests

requests.get("http://localhost:8080/api/coin_inject", params={"coins_amount": 200})