import os, sys, json, time, re, datetime
from google.genai import Client
from google.oauth2.service_account import Credentials
import gspread

CHAVE_API = os.environ.get("GEMINI_API_KEY")
GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_PL")

print("Uwierzytelnianie z Google Sheets (SHORTS PL)...")
credenciais_dict = json.loads(GOOGLE_JSON)
escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credenciais = Credentials.from_service_account_info(credenciais_dict, scopes=escopos)
gc = gspread.authorize(credenciais)

client = Client(api_key=CHAVE_API, http_options={'api_version': 'v1'})

def obter_modelo_lite():
    try:
        modelos = client.models.list()
        lite_models = [m.name for m in modelos if 'generateContent' in m.supported_generation_methods and 'flash-lite' in m.name]
        return sorted(lite_models, reverse=True)[0] if lite_models else 'gemini-2.5-flash'
    except:
        return 'gemini-2.5-flash'

modelo_usina = obter_modelo_lite()

ID_PLANILHA = "1KgIjWrLUVlllhlZB1R9fkHGxxZlLsax1aOVGZrYwgnU"
PILARES = {
    0: "Duchowa walka i ochrona",
    1: "Wyzwolenie z nalokow i wiezow",
    2: "Odnowa rodziny i malzenstwa",
    3: "Opatrznosc Boza i otwarte drzwi",
    4: "Milosierdzie Boze i uzdrowienie fizyczne",
    5: "Plaszcz Matki Bozej Czestochowskiej",
    6: "Cuda i wdziecznosc"
}
GRADE_SHORTS = [
    {"horario": "14:00", "personagem": "Maria", "idioma": "PL", "foco": "Poludnie: Wstawiennictwo, uzdrowienie i cuda.", "ref": "18:00"}
]

aba_shorts = gc.open_by_key(ID_PLANILHA).worksheet("PL_SHORTS")
aba_longos = gc.open_by_key(ID_PLANILHA).worksheet("PL")

todas_linhas = aba_shorts.get_all_values()
if len(todas_linhas) > 500:
    aba_shorts.delete_rows(2, 100)
    todas_linhas = aba_shorts.get_all_values()

proxima_linha_vazia = len(todas_linhas) + 1
valores_coluna_a = [linha[0].strip() for linha in todas_linhas[1:] if len(linha) > 0]
valores_coluna_b = [linha[1].strip() for linha in todas_linhas[1:] if len(linha) > 1]

dias_existentes = {}
hoje = datetime.date.today()
limite_passado = hoje - datetime.timedelta(days=2)

for d_str, h_str in zip(valores_coluna_a, valores_coluna_b):
    if d_str and h_str:
        try:
            d_obj = datetime.datetime.strptime(d_str, '%Y-%m-%d').date()
            if d_obj >= limite_passado:
                if d_obj not in dias_existentes: dias_existentes[d_obj] = []
                dias_existentes[d_obj].append(h_str)
        except: pass

meta_estoque = hoje + datetime.timedelta(days=5)
data_alvo = None
grade_para_processar = []

data_check = limite_passado
while data_check <= meta_estoque:
    horarios_presentes = dias_existentes.get(data_check, [])
    if len(horarios_presentes) < 1:
        data_alvo = data_check
        grade_para_processar = [v for v in GRADE_SHORTS if v["horario"] not in horarios_presentes]
        break
    data_check += datetime.timedelta(days=1)

if not data_alvo:
    print(f"Magazyn Shorts gotowy do {meta_estoque}. Koncze.")
    sys.exit(0)

pilar_do_dia = PILARES[data_alvo.weekday()]
print(f"\nData docelowa Shorts: {data_alvo} | Filar: {pilar_do_dia}")

dados_longos = aba_longos.get_all_values()

for video in grade_para_processar:
    horario, persona, idioma, foco_teologico = video["horario"], video["personagem"].upper(), video["idioma"], video["foco"]
    print(f"Produkuje Short: {horario} | {persona}")

    horario_longo_ref = video["ref"]
    titulo_referencia = ""
    for linha in dados_longos[1:]:
        if len(linha) > 6 and linha[0].strip() == str(data_alvo) and linha[1].strip() == horario_longo_ref:
            titulo_referencia = linha[6].strip()
            break

    contexto_eco = f"Odpowiadajacy dlagi film na dzis ma tytul: '{titulo_referencia}'. Short MUSI byc echem tego tematu." if titulo_referencia else ""

    oracao_padrao = "Zdrowas Maryjo, laskit pelna... Pan z Toba... Blogoslawionas Ty miedzy niewiastami... i blogoslawiony owoc zywota Twojego, Jezus... Swieta Maryjo, Matko Boza... modl sie za nami grzesznymi... teraz i w godzine smierci naszej... Amen."

    prompt_principal = f"""
Dzialaj jako katolicki przewodnik duchowy. Stworz skrypt do YouTube SHORT (maks. 35 sekund mowy) po polsku.
Temat dnia: {pilar_do_dia}. Fokus: {foco_teologico}. Skierowany do: Matki Bozej Czestochowskiej.
{contexto_eco}

OBOWIAZKOWA STRUKTURA SKRYPTU (IDEALNY LOOP):
1. HOOK (Poczatek): Pierwsza fraza. OBOWIAZKOWO zaczyna sie od malej litery z wielokropkiem. Jest SYNTAKTYCZNYM UZUPELNIENIEM zdania koncowego.
2. MODLITWA: Napisz DOKLADNIE te modlitwe: "{oracao_padrao}"
3. ZDANIE LOOP (Koniec): Ostatnia fraza. OBOWIAZKOWO konczy sie wielokropkiem. MUSI byc SYNTAKTYCZNIE NIEKOMPLETNA.

ZASADY: Pisz plynnie po polsku z wielokropkami. Tytul: "Krotka Modlitwa: [temat] - #Shorts". BEZ gwiazdek.

DOKLADNY FORMAT:
TITLE: [Krotka Modlitwa: Temat - #Shorts]
SCRIPT: [Kompletny skrypt z efektem loop po polsku]
DESC: [Krotki opis zapraszajacy do kanalu]
TAGS: [Tagi po polsku oddzielone przecinkami]
"""

    texto_ia = None
    for _ in range(3):
        try:
            texto_ia = client.models.generate_content(model=modelo_usina, contents=prompt_principal).text
            break
        except Exception as gemini_err: print(f"Blad Gemini: {gemini_err}"); time.sleep(10)

    if not texto_ia: continue

    try:
        t_match = re.search(r'TITLE:\s*(.*?)(?=SCRIPT:|DESC:|TAGS:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        g_match = re.search(r'SCRIPT:\s*(.*?)(?=DESC:|TAGS:|TITLE:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        d_match = re.search(r'DESC:\s*(.*?)(?=TAGS:|TITLE:|SCRIPT:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        tg_match = re.search(r'TAGS:\s*(.*?)(?=TITLE:|SCRIPT:|DESC:|$)', texto_ia, re.IGNORECASE | re.DOTALL)

        titulo_final = re.sub(r'[*"\[\]]', '', t_match.group(1)).strip() if t_match else "Krotka Modlitwa #Shorts"
        roteiro_final = g_match.group(1).strip() if g_match else texto_ia
        desc_final = d_match.group(1).strip() if d_match else "Odwiedz nasz kanal po pelna modlitwe!"
        tags_final = re.sub(r'[*\[\]]', '', tg_match.group(1)).strip() if tg_match else "shorts, modlitwa, wiara"

        nova_linha = [str(data_alvo), horario, "Ready for Audio", persona, idioma, pilar_do_dia, titulo_final, roteiro_final, tags_final, desc_final, "N/A", "N/A"]
        aba_shorts.update(values=[nova_linha], range_name=f"A{proxima_linha_vazia}:L{proxima_linha_vazia}")
        print(f"Sukces! Wiersz Short {proxima_linha_vazia} wypelniony.")
        proxima_linha_vazia += 1
        time.sleep(3)
    except Exception as e: print(f"Blad zapisu: {e}")
