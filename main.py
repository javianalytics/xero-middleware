from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
TENANT_ID = os.getenv("TENANT_ID")

TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_API_URL = "https://api.xero.com/api.xro/2.0/Invoices"


def refresh_access_token():
    global REFRESH_TOKEN

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )

    token_data = response.json()

    access_token = token_data["access_token"]
    new_refresh_token = token_data["refresh_token"]

    # Save new refresh token to .env
    with open(".env", "r") as file:
        lines = file.readlines()

    with open(".env", "w") as file:
        for line in lines:
            if line.startswith("REFRESH_TOKEN="):
                file.write(f"REFRESH_TOKEN={new_refresh_token}\n")
            else:
                file.write(line)

    REFRESH_TOKEN = new_refresh_token

    return access_token


@app.get("/xero/invoices")
def get_invoices():
    access_token = refresh_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": TENANT_ID,
        "Accept": "application/json",
    }

    all_invoices = []
    page = 1

    while True:
        response = requests.get(
            XERO_API_URL,
            headers=headers,
            params={
                "page": page,
                "pageSize": 1000
            }
        )

        data = response.json()
        invoices = data.get("Invoices", [])

        if not invoices:
            break

        all_invoices.extend(invoices)

        # stop when last page
        if len(invoices) < 1000:
            break

        page += 1

    return {"Invoices": all_invoices}