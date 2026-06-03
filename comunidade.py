import os, json, time, datetime, gspread
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as YTCredentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.genai import Client

GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_PL")
YT_TOKEN_JSON = os.environ.get("YOUTUBE_TOKEN_PL")
CHAVE_API_GEMINI = os.environ.get("GEMINI_API_KEY")

creds_sheets = Credentials.from_service_account_info(json.loads(GOOGLE_JSON), scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(creds_sheets)

creds_yt = YTCredentials.from_authorized_user_info(json.loads(YT_TOKEN_JSON))
if creds_yt and creds_yt.expired and creds_yt.refresh_token: creds_yt.refresh(Request())
youtube = build('youtube', 'v3', credentials=creds_yt)
gemini_client = Client(api_key=CHAVE_API_GEMINI, http_options={'api_version': 'v1'})

def obter_modelo_lite():
    try:
        modelos = gemini_client.models.list()
        lite_models = [m.name for m in modelos if 'generateContent' in m.supported_generation_methods and 'flash-lite' in m.name]
        return sorted(lite_models, reverse=True)[0] if lite_models else 'gemini-2.5-flash'
    except:
        return 'gemini-2.5-flash-lite'

modelo_comunidade = obter_modelo_lite()
print(f"Model AI dla Spolecznosci: {modelo_comunidade}")

canal_response = youtube.channels().list(part='id,contentDetails', mine=True).execute()
MEU_CANAL_ID = canal_response['items'][0]['id']
UPLOADS_PLAYLIST_ID = canal_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

print("Uruchamianie Menedzera Spolecznosci (Przypinane komentarze)")

texto_fixo = "Bog zaplac za Twoja obecnosc. Twoja modlitwa jest blogoslawienistwem dla calej naszej wspolnoty wiary. Zostaw swoje Amen w komentarzach i podziel sie z kims, kto potrzebuje cudu dzisiaj. Aktywuj dzwonek, aby nie przegapic zadnej modlitwy."

limite_24h = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
playlist_req = youtube.playlistItems().list(part='snippet', playlistId=UPLOADS_PLAYLIST_ID, maxResults=15).execute()
video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_req.get('items', [])]

if video_ids:
    videos_req = youtube.videos().list(part='snippet', id=','.join(video_ids)).execute()
    for video in videos_req.get('items', []):
        v_id, v_titulo = video['id'], video['snippet']['title']
        pub_time = datetime.datetime.strptime(video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        if pub_time >= limite_24h:
            try:
                comentarios = youtube.commentThreads().list(part='snippet', videoId=v_id, maxResults=100).execute()
                if not any(t['snippet']['topLevelComment']['snippet'].get('authorChannelId', {}).get('value') == MEU_CANAL_ID for t in comentarios.get('items', [])):
                    if "#shorts" in v_titulo.lower():
                        comentario_final = f"{texto_fixo}\n\nNiech ta krotka modlitwa blogoslawi Twoj dzien! Odwiedz nasz kanal po pelne modlitwy."
                    else:
                        link_playlist = "PLACEHOLDER_MORNING_PL"
                        if "wieczor" in v_titulo.lower() or "noc" in v_titulo.lower() or "sen" in v_titulo.lower(): link_playlist = "PLACEHOLDER_EVENING_PL"
                        comentario_final = f"{texto_fixo}\n\nKontynuuj modlitwe z nami: {link_playlist}"
                    youtube.commentThreads().insert(part="snippet", body={"snippet": {"videoId": v_id, "topLevelComment": {"snippet": {"textOriginal": comentario_final}}}}).execute()
                    print(f"Przypiety komentarz dodany do: {v_titulo[:30]}")
                    time.sleep(2)
            except: pass

print("\nRozpoczynam Cyfrowego Duszpasterza (Polubienia i spersonalizowane odpowiedzi)")
try:
    threads = youtube.commentThreads().list(part="snippet,replies", allThreadsRelatedToChannelId=MEU_CANAL_ID, maxResults=20).execute()
    for thread in threads.get('items', []):
        top = thread['snippet']['topLevelComment']['snippet']
        comentario_id = thread['snippet']['topLevelComment']['id']
        if top.get('authorChannelId', {}).get('value') == MEU_CANAL_ID: continue
        try: youtube.comments().rate(id=comentario_id, rating='like').execute()
        except: pass
        ja_respondi = any(r['snippet'].get('authorChannelId', {}).get('value') == MEU_CANAL_ID for r in thread.get('replies', {}).get('comments', []))
        if not ja_respondi:
            nome, texto = top.get('authorDisplayName', 'Drogi Bracie/Droga Siostro'), top.get('textOriginal', '')
            prompt = f"""Dzialaj jako empatyczny katolicki duszpasterz cyfrowy. Uzytkownik o imieniu '{nome}' skomentował: '{texto}'.
REGULA 1 (NIENAWISTNE KOMENTARZE): Jesli to komentarz pelen nienawisci lub krytyki AI, odpowiedz z wielka uprzejmoscia.
REGULA 2 (WIERNI): Jesli to prosba o modlitwe lub podziekowanie, odpowiedz W WYSOCE SPERSONALIZOWANY SPOSOB. Potwierdz bol lub sytuacje i zaoferuj konkretne slowo pociechy.
Maksymalnie 3 do 4 wierszy. Ciepły ton. BEZ cudzyslowow. Pisz po polsku."""
            try:
                resposta = gemini_client.models.generate_content(model=modelo_comunidade, contents=prompt).text.strip()
                youtube.comments().insert(part="snippet", body={"snippet": {"parentId": thread['id'], "textOriginal": resposta}}).execute()
                print(f"Odpowiedziano i polubiono: {nome}")
                time.sleep(3)
            except: pass
except: pass
print("Etap Spolecznosci zakonczony!")
