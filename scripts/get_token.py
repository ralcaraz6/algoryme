#!/usr/bin/env python3
"""
Genera el GA_REFRESH_TOKEN una sola vez, en tu ordenador.

Antes: crea un cliente OAuth de tipo "App de escritorio" en Google Cloud (con la API de
datos de GA4 y la API de Gmail habilitadas, y la pantalla de consentimiento en modo
"Interno"). Ten a mano su client_id y client_secret.

Uso:
    pip install google-auth-oauthlib
    python scripts/get_token.py

Se abrirá el navegador para que inicies sesión como info@algoryme.com y autorices.
Al final imprime los tres valores que hay que pegar como secrets en GitHub.
"""
import sys, json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly",
          "https://www.googleapis.com/auth/gmail.send"]

# Pásale la ruta del JSON del cliente OAuth que descargaste:
#   python3 scripts/get_token.py ~/Downloads/client_secret_XXX.json
if len(sys.argv) > 1:
    flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
    client_id = json.load(open(sys.argv[1]))["installed"]["client_id"]
    client_secret = json.load(open(sys.argv[1]))["installed"]["client_secret"]
else:
    client_id = input("client_id: ").strip()
    client_secret = input("client_secret: ").strip()
    flow = InstalledAppFlow.from_client_config(
        {"installed": {
            "client_id": client_id, "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }}, SCOPES)

creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

if not creds.refresh_token:
    print("\nNo llegó refresh_token. Repite asegurándote de que la app es Interna y "
          "de que aceptas el consentimiento.")
else:
    print("\n===== Pega estos 3 como secrets en GitHub =====")
    print("GA_CLIENT_ID      =", client_id)
    print("GA_CLIENT_SECRET  =", client_secret)
    print("GA_REFRESH_TOKEN  =", creds.refresh_token)
