import os, json, time, datetime, gspread
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as YTCredentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.genai import Client

GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_PL")
YT_TOKEN_JSON = os.environ.get("YOUTUBE_TOKEN_PL")
CHAVE_API_GEMINI = os.environ.get("GEMINI_API_KEY", "")
CHAVE_API_GEMINI_2 = os.environ.get("GEMINI_API_KEY_2", "")
CHAVES_GEMINI = [k for k in [CHAVE_API_GEMINI, CHAVE_API_GEMINI_2] if k]

MAX_RESPOSTAS = 30

creds_sheets = Credentials.from_service_account_info(json.loads(GOOGLE_JSON), scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(creds_sheets)

creds_yt = YTCredentials.from_authorized_user_info(json.loads(YT_TOKEN_JSON))
if creds_yt and creds_yt.expired and creds_yt.refresh_token: creds_yt.refresh(Request())
youtube = build('youtube', 'v3', credentials=creds_yt)
gemini_client = Client(api_key=CHAVES_GEMINI[0], http_options={'api_version': 'v1'})

def _gerar_comunidade(prompt):
    for chave in CHAVES_GEMINI:
        try:
            c = Client(api_key=chave, http_options={'api_version': 'v1'})
            return c.models.generate_content(model=modelo_comunidade, contents=prompt).text.strip()
        except Exception as e:
            if "429" in str(e) and chave != CHAVES_GEMINI[-1]:
                print(f"[WARN] 429 na kluczu ...{chave[-6:]}. Probuje klucz 2...")
                continue
            raise
    raise RuntimeError("Wszystkie klucze Gemini nie powiodly sie.")

def obter_modelo_lite():
    # gemini-2.5-flash-lite: free tier, 15 RPM, ~1000 RPD por projeto
    try:
        modelos = gemini_client.models.list()
        nomes = [m.name for m in modelos if 'generateContent' in m.supported_generation_methods]
        for preferido in ['gemini-2.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.1-flash-lite']:
            if any(preferido in n for n in nomes):
                return preferido
        return 'gemini-2.5-flash-lite'
    except:
        return 'gemini-2.5-flash-lite'

modelo_comunidade = obter_modelo_lite()
print(f"Model AI dla Spolecznosci: {modelo_comunidade}")

canal_response = youtube.channels().list(part='id,contentDetails', mine=True).execute()
MEU_CANAL_ID = canal_response['items'][0]['id']
UPLOADS_PLAYLIST_ID = canal_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

LINK_LIVE = f"https://www.youtube.com/channel/{MEU_CANAL_ID}/live"

TEXTO_FIXO_PL = "Bog zaplac za Twoja obecnosc. Twoja modlitwa jest blogoslawienistwem dla calej naszej wspolnoty wiary. Zostaw swoje Amen w komentarzach i podziel sie z kims, kto potrzebuje cudu dzisiaj. Aktywuj dzwonek, aby nie przegapic zadnej modlitwy."

# ── WLACZ KOMENTARZE (filmy z ostatnich 72h) ─────────────────────────────────
print("🔓 WLACZANIE KOMENTARZY na ostatnich filmach...")
try:
    limite_72h = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=72)
    video_ids_72h = []
    page_token_72 = None
    for _ in range(2):
        resp = youtube.playlistItems().list(
            part='snippet', playlistId=UPLOADS_PLAYLIST_ID,
            maxResults=50, pageToken=page_token_72
        ).execute()
        for item in resp.get('items', []):
            pub = item['snippet'].get('publishedAt', '')
            try:
                pt = datetime.datetime.strptime(pub, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
                if pt >= limite_72h:
                    video_ids_72h.append(item['snippet']['resourceId']['videoId'])
            except: pass
        page_token_72 = resp.get('nextPageToken')
        if not page_token_72: break
    for vid in video_ids_72h:
        try:
            youtube.videos().update(
                part="status",
                body={"id": vid, "status": {"selfDeclaredMadeForKids": False, "selfDeclaredMadeWithAlteredContent": True}}
            ).execute()
            print(f"   🔓 Status zaktualizowany: {vid}")
            time.sleep(1)
        except Exception as e:
            print(f"   ⚠️ Nie mozna zaktualizowac {vid}: {e}")
except Exception as e:
    print(f"⚠️ Wlacz komentarze: {e}")

# ── MENEDZER SPOLECZNOSCI ─────────────────────────────────────────────────────
print("\nUruchamianie Menedzera Spolecznosci (Przypinane komentarze)")
limite_24h = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
video_ids = []
page_token_up = None
for _ in range(4):
    resp_up = youtube.playlistItems().list(
        part='snippet', playlistId=UPLOADS_PLAYLIST_ID,
        maxResults=50, pageToken=page_token_up
    ).execute()
    video_ids += [item['snippet']['resourceId']['videoId'] for item in resp_up.get('items', [])]
    page_token_up = resp_up.get('nextPageToken')
    if not page_token_up: break

if video_ids:
    videos_req = youtube.videos().list(part='snippet', id=','.join(video_ids[:50])).execute()
    for video in videos_req.get('items', []):
        v_id, v_titulo = video['id'], video['snippet']['title']
        pub_time = datetime.datetime.strptime(video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        if pub_time >= limite_24h:
            try:
                comentarios = youtube.commentThreads().list(part='snippet', videoId=v_id, maxResults=100).execute()
                if not any(t['snippet']['topLevelComment']['snippet'].get('authorChannelId', {}).get('value') == MEU_CANAL_ID for t in comentarios.get('items', [])):
                    if "#shorts" in v_titulo.lower():
                        comentario_final = f"{TEXTO_FIXO_PL}\n\nNiech ta krotka modlitwa blogoslawi Twoj dzien! Odwiedz nasz kanal po pelne modlitwy.\n\n🔴 NA ZYWO TERAZ 24/7: Twoje intencje sa nieustannie wznoszone w modlitwie. Dolacz: {LINK_LIVE}"
                    else:
                        comentario_final = f"{TEXTO_FIXO_PL}\n\nKontynuuj modlitwe z nami w naszej transmisji 24/7: {LINK_LIVE}"
                    youtube.commentThreads().insert(part="snippet", body={"snippet": {"videoId": v_id, "topLevelComment": {"snippet": {"textOriginal": comentario_final}}}}).execute()
                    print(f"Przypiety komentarz dodany do: {v_titulo[:30]}")
                    time.sleep(2)
            except Exception as e:
                print(f"Blad przy komentarzu {v_id}: {e}")

# ── CYFROWY DUSZPASTERZ ───────────────────────────────────────────────────────
print("\nRozpoczynam Cyfrowego Duszpasterza (Spersonalizowane odpowiedzi)")
try:
    respondidos = 0
    page_token_t = None
    for _pagina in range(10):  # do 1000 watkow na wykonanie
        if respondidos >= MAX_RESPOSTAS:
            print(f"   Osiagnieto limit {MAX_RESPOSTAS} odpowiedzi — nastepne wykonanie kontynuuje.")
            break
        threads_resp = youtube.commentThreads().list(
            part="snippet,replies",
            allThreadsRelatedToChannelId=MEU_CANAL_ID,
            maxResults=100,
            pageToken=page_token_t
        ).execute()
        for thread in threads_resp.get('items', []):
            if respondidos >= MAX_RESPOSTAS:
                break
            top = thread['snippet']['topLevelComment']['snippet']
            autor_id = top.get('authorChannelId', {}).get('value')
            if autor_id == MEU_CANAL_ID:
                continue
            ja_respondi = any(
                r['snippet'].get('authorChannelId', {}).get('value') == MEU_CANAL_ID
                for r in thread.get('replies', {}).get('comments', [])
            )
            if not ja_respondi:
                nome  = top.get('authorDisplayName', 'Drogi Bracie/Droga Siostro')
                texto = top.get('textOriginal', '')
                prompt = (
                    f"Dzialaj jako empatyczny katolicki duszpasterz cyfrowy. Uzytkownik o imieniu '{nome}' skomentował: '{texto}'. "
                    f"REGULA 1 (NIENAWISTNE KOMENTARZE): Jesli to komentarz pelen nienawisci lub krytyki AI, odpowiedz z wielka uprzejmoscia, szanujac roznice, skupiajac sie na milosci Boga. "
                    f"REGULA 2 (WIERNI): Jesli to prosba o modlitwe, wyznanie lub podziekowanie, odpowiedz W WYSOCE SPERSONALIZOWANY SPOSOB. Potwierdz bol/sytuacje i zaoferuj konkretne slowo pociechy lub modlitwe. "
                    f"Jesli wspomina chorobe, cierpienie lub wstawiennictwo, organicznie zaproś do naszej transmisji 24/7: {LINK_LIVE} "
                    f"Maksymalnie 3-4 wiersze. Ciepły i ludzki ton. BEZ cudzyslowow. Pisz po polsku."
                )
                try:
                    resposta = _gerar_comunidade(prompt)
                    youtube.comments().insert(
                        part="snippet",
                        body={"snippet": {"parentId": thread['id'], "textOriginal": resposta}}
                    ).execute()
                    print(f"Odpowiedziano: {nome}")
                    respondidos += 1
                    time.sleep(3)
                except Exception as e:
                    print(f"Blad odpowiedzi {nome}: {e}")
        page_token_t = threads_resp.get('nextPageToken')
        if not page_token_t:
            break
    print(f"Lacznie odpowiedziano w tym wykonaniu: {respondidos}")
except Exception as e:
    print(f"CYFROWY DUSZPASTERZ blad ogolny: {e}")
print("Etap Spolecznosci zakonczony!")
