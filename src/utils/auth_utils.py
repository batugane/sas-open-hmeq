import requests
import os
import base64
import swat
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Configuration ===
CLIENT_ID = os.getenv("SAS_CLIENT_ID", "api.client")
CLIENT_SECRET = os.getenv("SAS_CLIENT_SECRET", "api.secret")
BASE_URL = os.getenv("SAS_BASE_URL", "https://create.demo.sas.com")
CERT_PATH = os.getenv("SAS_CERT_PATH", "C:/sas/model-manager/demo-rootCA-Intermidiates_4CLI.pem")
TOKEN_DIR = os.getcwd()

# === Token Handling ===
def _get_base64_auth_string():
    client_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    return base64.b64encode(client_string.encode('ascii')).decode('ascii')


def save_token(token_str: str, filename: str):
    with open(os.path.join(TOKEN_DIR, filename), 'w') as f:
        f.write(token_str)


def load_token(filename: str) -> str:
    with open(os.path.join(TOKEN_DIR, filename)) as f:
        return f.read().strip()


# === Access Token Generation ===
def generate_access_token():
    auth_url = f"{BASE_URL}/SASLogon/oauth/authorize?client_id={CLIENT_ID}&response_type=code"
    logger.info("* Open in incognito: %s", auth_url)
    logger.info("* Authenticate with SAS credentials, check all boxes, and copy the resulting short code.")
    code = input("Paste the authorization code: ").strip()

    token_url = f"{BASE_URL}/SASLogon/oauth/token#authorization_code"
    payload = f"grant_type=authorization_code&code={code}"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': "Basic " + _get_base64_auth_string()
    }

    try:
        response = requests.post(token_url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        data = response.json()
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        save_token(access_token, 'access_token.txt')
        save_token(refresh_token, 'refresh_token.txt')
        logger.info("✔ Access and refresh tokens saved.")
        return access_token
    except Exception as e:
        logger.error("Failed to generate access token: %s", e)
        raise


def refresh_access_token():
    token_url = f"{BASE_URL}/SASLogon/oauth/token#refresh_token"
    refresh_token = load_token("refresh_token.txt")

    payload = f"grant_type=refresh_token&refresh_token={refresh_token}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': "Basic " + _get_base64_auth_string()
    }

    try:
        response = requests.post(token_url, headers=headers, data=payload, verify=False)
        response.raise_for_status()  # raises if status is not 2xx
        data = response.json()
        access_token = data['access_token']
        save_token(access_token, 'access_token.txt')
        logger.info("✔ Access token refreshed and saved.")
        return access_token
    except Exception as e:
        logger.error("Failed to refresh access token: %s", e)
        raise


def get_token():
    """
    Get an access token by attempting to refresh first, then generating new if needed.
    """
    try:
        token = refresh_access_token()
        logger.info("✔ Access token refreshed.")
    except Exception:
        logger.warning("⚠️ Refresh failed; generating new access token.")
        token = generate_access_token()
    return token


# === SWAT CAS Connection ===
def connect_cas_https(access_token: str):
    return swat.CAS(
        "https://create.demo.sas.com/cas-shared-default-http",
        username=None,
        password=access_token,
        ssl_ca_list=CERT_PATH,
        protocol="https"
    )
