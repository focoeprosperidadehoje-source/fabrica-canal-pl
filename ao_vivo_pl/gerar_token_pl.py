#!/usr/bin/env python3
"""
gerar_token_pl.py — Generuje youtube_token.json dla Kanału PL (transmisja na żywo).
Uruchomić jednorazowo na VPS po wstępnej konfiguracji.

Użycie:
  cd /root/ao_vivo_pl
  python3 gerar_token_pl.py

Skrypt wyświetli URL — otwórz w przeglądarce, autoryzuj kontem
canalinteligenciadivina@gmail.com wybierając Kanał PL,
wklej kod tutaj. Token zostanie zapisany automatycznie.
"""

import json
import os
import sys
from pathlib import Path

def _load_env(path: str):
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

_load_env("/root/ao_vivo_pl/.env")

CLIENT_ID     = os.environ.get("YT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET", "")
SAVE_PATH     = Path("/root/ao_vivo_pl/youtube_token.json")
SCOPES        = ["https://www.googleapis.com/auth/youtube"]

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERRO: YT_CLIENT_ID ou YT_CLIENT_SECRET ausentes em /root/ao_vivo_pl/.env")
    print()
    print("Extraia do token ES no VPS antigo e adicione ao .env:")
    print("  No VPS 80.241.213.27:")
    print("    python3 -c \"import json; d=json.load(open('/root/ao_vivo_es/youtube_token.json')); print('YT_CLIENT_ID=' + d.get('client_id','')); print('YT_CLIENT_SECRET=' + d.get('client_secret',''))\"")
    print()
    print("  Depois neste VPS (169.58.220.233), adicione ao /root/ao_vivo_pl/.env:")
    print("    echo 'YT_CLIENT_ID=...' >> /root/ao_vivo_pl/.env")
    print("    echo 'YT_CLIENT_SECRET=...' >> /root/ao_vivo_pl/.env")
    sys.exit(1)

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Instalando google-auth-oauthlib...")
    import subprocess
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "google-auth-oauthlib"],
        check=True
    )
    from google_auth_oauthlib.flow import InstalledAppFlow

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

print("=" * 60)
print("Gerador de Token YouTube — Canal PL")
print("=" * 60)
print()
print("1. Copie a URL abaixo e abra no seu navegador")
print("2. Faça login com canalinteligenciadivina@gmail.com")
print("3. Escolha o Canal PL quando perguntado")
print("4. Autorize e copie o código exibido")
print("5. Cole o código aqui e pressione Enter")
print()

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
print(f"URL para autorizar:\n{auth_url}\n")
code = input("Cole o código aqui: ").strip()
flow.fetch_token(code=code)
creds = flow.credentials

SAVE_PATH.write_text(creds.to_json())
print()
print(f"✅ Token salvo em {SAVE_PATH}")
print()
print("Próximo passo — iniciar a live PL:")
print("  systemctl start ao_vivo_pl")
print("  systemctl status ao_vivo_pl")
