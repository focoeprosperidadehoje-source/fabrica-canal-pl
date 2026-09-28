import os, sys, json, time, re, datetime
from google.genai import Client
from google.oauth2.service_account import Credentials
import gspread
from zoneinfo import ZoneInfo
import novenas

CHAVE_API = os.environ.get("GEMINI_API_KEY")
CHAVE_API_2 = os.environ.get("GEMINI_API_KEY_2", "")
CHAVES_GEMINI = [k for k in [CHAVE_API, CHAVE_API_2] if k]
GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_PL")

print("Uwierzytelnianie z Google Sheets przez Service Account...")
credenciais_dict = json.loads(GOOGLE_JSON)
escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credenciais = Credentials.from_service_account_info(credenciais_dict, scopes=escopos)
gc = gspread.authorize(credenciais)

client = Client(api_key=CHAVE_API, http_options={'api_version': 'v1'})

def obter_cascata_de_modelos():
    try:
        modelos_disponiveis = client.models.list()
        # Lite/8b = cota generosa no tier gratuito. Prioridade máxima.
        lite_models = [m.name for m in modelos_disponiveis if 'generateContent' in m.supported_generation_methods and 'flash' in m.name and ('lite' in m.name or '8b' in m.name)]
        # Flash regular = fallback de último recurso (cota restrita ~20 RPD)
        flash_models = [m.name for m in modelos_disponiveis if 'generateContent' in m.supported_generation_methods and 'flash' in m.name and 'lite' not in m.name and '8b' not in m.name]
        melhor_lite = sorted(lite_models, reverse=True)[0] if lite_models else 'gemini-2.5-flash-lite'
        melhor_flash = sorted(flash_models, reverse=True)[0] if flash_models else 'gemini-2.5-flash'
        return [melhor_lite, melhor_lite, melhor_lite, melhor_lite, melhor_flash]
    except:
        return ['gemini-2.5-flash-lite', 'gemini-2.5-flash-lite', 'gemini-2.5-flash-lite', 'gemini-2.5-flash-lite', 'gemini-2.5-flash']

modelos_cascata = obter_cascata_de_modelos()

def _gerar(modelo, prompt):
    for chave in CHAVES_GEMINI:
        try:
            c = Client(api_key=chave, http_options={'api_version': 'v1'})
            return c.models.generate_content(model=modelo, contents=prompt).text
        except Exception as e:
            if "429" in str(e) and chave != CHAVES_GEMINI[-1]:
                print(f"[WARN] 429 na kluczu ...{chave[-6:]}. Probuje klucz 2...")
                continue
            raise
    raise RuntimeError("Wszystkie klucze Gemini zawiodly.")

def calcular_contexto_sazonal(data_alvo):
    ano = data_alvo.year
    a = ano % 19; b = ano // 100; c = ano % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; mes = (h + l - 7 * m + 114) // 31; dia = ((h + l - 7 * m + 114) % 31) + 1
    easter = datetime.date(ano, mes, dia)

    ash_wednesday = easter - datetime.timedelta(days=46)
    good_friday = easter - datetime.timedelta(days=2)
    pentecost = easter + datetime.timedelta(days=49)
    corpus_christi = easter + datetime.timedelta(days=60)

    if data_alvo == easter: return "DZIS JEST NIEDZIELA WIELKANOCNA — najwazniejsze swieto chrzescijanstwa. Podkresl Zmartwychwstanie Chrystusa i nadzieje zmartwychwstania dla wszystkich wierzacych."
    if data_alvo == ash_wednesday: return "DZIS JEST SRODA POPIELCOWA — poczatek Wielkiego Postu. Zachec do nawrocenia, pokuty i poglebiania zycia duchowego."
    if data_alvo == good_friday: return "DZIS JEST WIELKI PIATEK — wspomnienie Meki i smierci Chrystusa na krzyzu. Podkresl wielka milosc Boga i sens cierpienia."
    if data_alvo == pentecost: return "DZIS JEST ZESLANIE DUCHA SWIETEGO — pamiatka wylania Ducha Swietego. Zachec do otwarcia na dary Ducha."
    if data_alvo == corpus_christi: return "DZIS JEST BOZE CIALO — uroczystosc Najswietszego Ciala i Krwi Chrystusa. Podkresl rzeczywista obecnosc Jezusa w Eucharystii."
    if data_alvo.month == 5 and data_alvo.day == 3: return "DZIS JEST SWIETO KONSTYTUCJI 3 MAJA oraz wspomnienie NMP Krolowej Polski. Podkresl patronat Maryi nad Polska i wdziecznosc za wiare."
    if data_alvo.month == 5 and data_alvo.day == 26: return "DZIS JEST DZIEN MATKI W POLSCE. Podziekuj za wszystkie matki i szczegolie modl sie za nie przez wstawiennictwo Matki Bozej Czestochowskiej."
    if data_alvo.month == 6 and data_alvo.day == 23: return "DZIS JEST DZIEN OJCA W POLSCE. Modl sie za wszystkich ojcow, proszac Jezusa o blogoslawienstwo dla rodzin."
    if data_alvo.month == 8 and data_alvo.day == 15: return "DZIS JEST WNIEBOWZIECIE NAJSWIETSZEJ MARYI PANNY — wielkie polskie swieto narodowe i koscielne. Sllaw ukoronowanie Maryi i Jej obecnosc w niebie."
    if data_alvo.month == 8 and data_alvo.day == 26: return "DZIS JEST UROCZYSTOSC MATKI BOZEJ CZESTOCHOWSKIEJ — Krolowej Polski i patronki naszego kanalu. To szczegolny dzien modlitwy przed cudownym obrazem na Jasnej Gorze."
    if data_alvo.month == 11 and data_alvo.day == 1: return "DZIS JEST UROCZYSTOSC WSZYSTKICH SWIETYCH — wielkie polskie swieto. Pamietaj o swietych obcowaniu i modlitwie za dusze w czyscci."
    if data_alvo.month == 11 and data_alvo.day == 2: return "DZIS JEST DZIEN ZADUSZNY — wspomnienie wszystkich wiernych zmarlych. Modl sie za dusze w czyscci i za ukochanych, ktorzy odeszli."
    if data_alvo.month == 12 and data_alvo.day == 8: return "DZIS JEST UROCZYSTOSC NIEPOKALANEGO POCZECIA NMP. Sllaw czystosc i swietosc Maryi od pierwszej chwili Jej istnienia."
    if data_alvo.month == 12 and data_alvo.day == 25: return "DZIS JEST BOZE NARODZENIE — narodziny Jezusa Chrystusa. Glos radosc Wcielenia i milosc Boga, ktory stal sie czlowiekiem."
    if data_alvo.month == 12 and data_alvo.day == 26: return "DZIS JEST DRUGI DZIEN BOZEGO NARODZENIA — wspomnienie sw. Szczepana, pierwszego meczennika. Kontynuuj radosc swiat i refleksje o wartosci swiadectwa wiary."
    if data_alvo.month == 12 and data_alvo.day == 31: return "DZIS JEST SYLWESTER — ostatni dzien roku. Zachec do rachunku sumienia, wdziecznosci za miniony rok i zawierzenia nowego roku Bogu."
    if data_alvo.month == 1 and data_alvo.day == 1: return "DZIS JEST NOWY ROK — Uroczystosc Swietej Bozej Rodzicielki Maryi. Powitaj nowy rok w Jej opiece i zawierz wszystkie troski Jej macierzynskiemu sercu."
    return ""

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
GRADE_DIARIA = [
    # Slot 06:00 — Novenas (novenas.py). Sem retroatividade; só a partir de novenas.ATIVACAO_06H.
    {"horario": "06:00", "personagem": "Maria", "idioma": "PL", "foco": "Morning consecration to Our Lady: protection, direction and strength for the day that begins.", "periodo": novenas.CFG["periodo"], "ativacao": novenas.ATIVACAO_06H},
    {"horario": "18:00", "personagem": "Maria", "idioma": "PL", "foco": "HYBRYDOWY: Pierwsza czesc dotyczy bolu Filaru Dnia, ostatnia czesc przechodzi do wieczornej modlitwy — gleboki sen, ulga od leku i nocna ochrona.", "periodo": "tego wieczoru"}
]

aba = gc.open_by_key(ID_PLANILHA).worksheet("PL")

todas_linhas = aba.get_all_values()
if len(todas_linhas) > 500:
    aba.delete_rows(2, 100)
    todas_linhas = aba.get_all_values()

proxima_linha_vazia = len(todas_linhas) + 1
valores_coluna_a = [linha[0].strip() for linha in todas_linhas[1:] if len(linha) > 0]
valores_coluna_b = [linha[1].strip() for linha in todas_linhas[1:] if len(linha) > 1]

dias_existentes = {}
agora_local = datetime.datetime.now(ZoneInfo(novenas.TZ))
hoje = agora_local.date()
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

def slot_exigido(v, d):
    """Travas do slot 06:00: sem retroatividade (evita upload público imediato de vídeo atrasado)."""
    if v.get("ativacao") and d < v["ativacao"]:
        return False
    if v["horario"] == "06:00":
        if d < hoje: return False
        if d == hoje and agora_local.hour >= 4: return False
        if novenas.plano_do_dia(d) is None: return False
    return True
data_alvo = None
grade_para_processar = []

data_check = limite_passado
while data_check <= meta_estoque:
    horarios_presentes = dias_existentes.get(data_check, [])
    faltando = [v for v in GRADE_DIARIA if slot_exigido(v, data_check) and v["horario"] not in horarios_presentes]
    if faltando:
        data_alvo = data_check
        grade_para_processar = faltando
        break
    data_check += datetime.timedelta(days=1)

if not data_alvo:
    print(f"Magazyn gotowy do {meta_estoque}. Koncze.")
    sys.exit(0)

pilar_do_dia = PILARES[data_alvo.weekday()]
contexto_sazonal = calcular_contexto_sazonal(data_alvo)
print(f"\nData docelowa: {data_alvo} | Filar: {pilar_do_dia}")

esperas_exponenciais = [10, 20, 40, 80, 120]

def gerar_novena(data_alvo, plano, contexto_sazonal):
    """Linha da planilha para um dia de novena (festa ou pedido) — rito fixo em novenas.py."""
    C = novenas.CFG
    n = plano["dia"]
    categoria = None
    if plano["tipo"] == "festa":
        f = plano["festa"]
        invocacao = f["invocacao"]
        contexto = (f"This is the '{f['nome']}', preparing for: {f['festa']}. Today is day {n} of 9. "
                    f"INTENTION OF THE DAY (the believer's pain): {novenas.INTENCOES_FESTA[n - 1]}.")
    else:
        categoria = novenas.escolher_tema_pedido(gc.open_by_key(ID_PLANILHA), plano["ciclo_inicio"])
        rotulo, descr = novenas.CATEGORIAS[categoria]
        invocacao = C["invocacao_padrao"]
        contexto = (f"This is the '{rotulo}', a 9-day petition novena to Our Lady ({invocacao}). "
                    f"Single theme of the novena: {descr}. Today is day {n} of 9. {novenas.PROGRESSAO_PEDIDO[n]}")
    if data_alvo.weekday() == 4:
        contexto += " TODAY IS FRIDAY: gently touch on Mercy and Forgiveness."
    if contexto_sazonal:
        contexto += f" Season/feast context: {contexto_sazonal}."
    cta_final = ("Invite them to pray the complete novena in the channel playlist and to keep praying with us live 24 hours."
                 if n == 9 else "Invite them to come back tomorrow morning for the next day of the novena (never say an exact hour).")
    prompt = f"""
    You are an empathetic Catholic spiritual guide, faithful to Church doctrine. Write ONLY the VARIABLE parts of a NOVENA video addressed to {invocacao}.
    WRITE EVERYTHING IN {novenas.LANG_NAME}. Natural, native, devotional language — never translated-sounding.
    The fixed rite (sign of the cross, act of contrition, novena prayer, Our Father, Hail Mary, Glory Be) is ALREADY inserted by the system — DO NOT write those prayers.
    CONTEXT: {contexto}
    Time of day: "{C['periodo']}".

    RULES:
    1. GANCHO (120-180 words) — HOOK 3A: (a) EMPATHIC STATEMENT about the pain of the day's intention, NO direct questions; (b) sensory setting of the morning that begins; (c) announce that today is day {n} of the novena and that {invocacao} has a grace for whoever stays until the end.
    2. REFLEXAO (450-600 words): a short Bible passage (cite book and chapter) linked to the intention, and a warm meditation. Include 1 invisible retention hook (anticipation or partial revelation) without breaking the devotional mood.
    3. SUPLICA (350-500 words): personal first-person supplication for the day's intention; MUST include a block of intercession for health (the sick in the family, physical and emotional healing). Arc: vulnerability → intercession → trust.
    4. ENCERRAMENTO (120-180 words): end in STRENGTH and confidence, never in pleading. {cta_final} Also {C['cta_pista']}. FORBIDDEN: "type Amen" style forced engagement.
    5. PROMESSA (max 40 characters): complement of the title, which already starts with the novena name and the day. Do NOT repeat the novena name. {'Focus on the intention of the day.' if plano['tipo'] == 'festa' else C['promessa_regra']} No quotes, no emoji, no date.
    6. NEVER mention exact hours. Use many ellipses (...) for voice pauses. PLAIN TEXT: no JSON, no asterisks, no brackets, no section titles inside the texts.
    7. FORBIDDEN to mention any saint or devotion other than Our Lady, Jesus and God the Father.

    EXACT FORMAT (keep these English labels, in this order; content in {novenas.LANG_NAME}):
    PROMESSA: ...
    GANCHO: ...
    REFLEXAO: ...
    SUPLICA: ...
    ENCERRAMENTO: ...
    DESC: [3 SEO paragraphs: 1st "Novena — {n}/9" + invitation to the 24h live; 2nd emotional description of the day's intention; 3rd keywords and hashtags including #novena]
    TAGS: [comma-separated tags including the word for novena]
    """
    rotulos = ["PROMESSA", "GANCHO", "REFLEXAO", "SUPLICA", "ENCERRAMENTO", "DESC", "TAGS"]
    def _lab(r): return r"(?:^|\n)[ \t>*_#]*" + r + r"[ \t*_]*:"
    padrao_fim = "|".join(_lab(r) for r in rotulos)
    for i in range(5):
        try:
            texto = _gerar(modelos_cascata[i], prompt)
        except Exception as e:
            print(f"   ⚠️ Gemini: {e}"); time.sleep(esperas_exponenciais[i]); continue
        t = texto.replace("REFLEXÃO", "REFLEXAO").replace("SÚPLICA", "SUPLICA")
        partes = {}
        for r in rotulos:
            m = re.search(_lab(r) + r"\s*(.*?)(?=(?:" + padrao_fim + r")|\Z)", t, re.IGNORECASE | re.DOTALL)
            partes[r] = re.sub(r'[*#\[\]{}]', '', m.group(1)).strip() if m else ""
        palavras = sum(len(partes[k].split()) for k in ["GANCHO", "REFLEXAO", "SUPLICA", "ENCERRAMENTO"])
        if all(partes[k] for k in ["GANCHO", "REFLEXAO", "SUPLICA", "ENCERRAMENTO"]) and palavras >= 700:
            break
        print(f"   ⚠️ Resposta incompleta ({palavras} palavras). Nova tentativa...")
        time.sleep(esperas_exponenciais[i])
    else:
        print("   ❌ Novena não gerada nesta execução — o scanner tenta de novo na próxima.")
        return None
    promessa = partes["PROMESSA"].replace('"', '').strip()[:45]
    titulo = novenas.montar_titulo(plano, promessa, categoria, data_alvo)
    roteiro = novenas.montar_roteiro(plano, partes["GANCHO"], partes["REFLEXAO"], partes["SUPLICA"], partes["ENCERRAMENTO"])
    return [str(data_alvo), "06:00", novenas.STATUS_PRONTO, "MARIA", "PL", novenas.tema_codificado(plano, categoria), titulo, roteiro,
            partes["TAGS"] or "novena", partes["DESC"] or f"Novena {n}/9", "Pending", novenas.texto_thumb(plano)]


for video in grade_para_processar:
    horario, persona, idioma, foco_teologico, periodo = video["horario"], video["personagem"].upper(), video["idioma"], video["foco"], video["periodo"]
    print(f"Produkuje: {horario} | {persona}")

    if horario == "06:00":
        plano = novenas.plano_do_dia(data_alvo)
        if plano and plano["tipo"] in ("festa", "pedido"):
            nova_linha = gerar_novena(data_alvo, plano, contexto_sazonal)
            if nova_linha:
                try:
                    aba.update(values=[nova_linha], range_name=f"A{proxima_linha_vazia}:L{proxima_linha_vazia}")
                    print(f"   ✅ NOVENA salva na linha {proxima_linha_vazia}: {nova_linha[6]}")
                    proxima_linha_vazia += 1
                    time.sleep(5)
                except Exception as e: print(f"   ❌ Falha ao salvar novena: {e}")
            continue
        print(f"   ☀️ Slot 06:00 avulso ({plano.get('motivo') if plano else '-'})")

    if data_alvo.weekday() == 4:
        foco_teologico += " OBOWIAZKOWO: Pogleб temat Milosierdzia i Przebaczenia." if horario == "06:00" else " OBOWIAZKOWO: Polacz temat z Meka Chrystusa i Sakramentem Pojednania."

    persona_prompt = "Jezusa Chrystusa" if persona == 'JESUS' else "Matki Bozej Czestochowskiej"
    persona_nominativo = "Jezus Chrystus" if persona == 'JESUS' else "Matka Boza Czestochowska"

    prompt_tema = f"Dzialaj jako Teolog. Stworz krotki temat (maks. 8 slow) do modlitwy po polsku. Filar: '{pilar_do_dia}', skierowany do '{persona_nominativo}', moment: '{foco_teologico}'. Sezonowosc: '{contexto_sazonal}'. TYLKO temat, bez cudzyslowow ani gwiazdek."
    tema_gerado = None
    for i in range(5):
        try:
            tema_gerado = _gerar(modelos_cascata[i], prompt_tema).replace('*', '').replace('"', '').replace('[', '').replace(']', '').strip()
            break
        except Exception as gemini_err: print(f"Blad Gemini (proba {i+1}/5): {gemini_err}"); time.sleep(esperas_exponenciais[i])

    if not tema_gerado: continue
    time.sleep(5)

    regra_meditacao = "OBOWIAZKOWO: W opisie (DESC) dodaj wyrozniona informacje, ze na koncu filmu sa 5 minut muzyki niebiansiej do snu/medytacji." if horario == "18:00" else ""
    cta_comentarios = "Na koncu poprois sluchacza, aby napisal w komentarzach powod do wdziecznosci." if horario == "18:00" else "Na poczatku naturalnie zapytaj: 'Jesli wierzysz, napisz Amen w komentarzach wlasnie teraz'."
    regra_persona = "OBOWIAZKOWO: Poniewaz zwracasz sie do Jezusa Chrystusa, SUROWO ZABRANIA SIE wspominania Maryi lub Dziewicy." if persona == 'JESUS' else "OBOWIAZKOWO: Poniewaz zwracasz sie do Maryi, MUSISZ uzywac wezwan 'Matka Boza Czestochowska', 'Matka Boza', 'Nasza Pani' lub 'Krolowa Polski'."

    instrucao_titulo = (
        "TITLE:[Magnetyczny tytul. OBOWIAZKOWO zacznij od 'Matka Boza' lub 'Matka Czestochowska'. FORMAT: 'Matka Boza [bol wiernego] [pilna obietnica]'. Np: 'Matka Boza Uzdrawia Twoja Rodzine Dzis Wieczor'. BEZ DATY. BEZ GWIAZDEK ANI NAWIASOW]"
        if persona == 'MARIA' else
        "TITLE:[Magnetyczny tytul. OBOWIAZKOWO zacznij od bolu/sytuacji wiernego, NIGDY od 'Jezus' lub 'Modlitwa'. FORMAT: '[Krytyczny bol wiernego] — [pilna obietnica ulgi]'. Np: 'Twoja Rodzina Cierpi — Zmow Ta Modlitwe TERAZ'. BEZ DATY. BEZ GWIAZDEK ANI NAWIASOW]"
    )

    prompt_principal = f"""
Dzialaj jako empatyczny przewodnik duchowy i brat w wierze. Napisz obszerna modlitwe od 1500 do 1800 slow na temat "{tema_gerado}" skierowana do {persona_prompt}.
KONTEKST: Pora dnia: "{periodo}". Fokus: "{foco_teologico}". Sezonowosc: "{contexto_sazonal}".
JEZYK: Pisz wylacznie po polsku, pieknym, poboznym jezykiem katolickim.

ZASADY RETENCJI I COPYWRITINGU (BARDZO WAZNE):
1. FORMULA TYTULU: Postepuj DOKLADNIE wedlug instrukcji formatu ponizej. Dla Matki Bozej: OBOWIAZKOWO zacznij od 'Matka Boza' lub 'Matka Czestochowska'. Dla Jezusa: zacznij od bolu wiernego. SUROWO ZABRANIA SIE zaczynania od slowa "Modlitwa".
2. FORMULA MINIATURY: Maks. 4 slowa. MUSI byc wyzwalaczem pilnosci powizanym z tematem.
3. REGULA 15 SEKUND (HOOK 3A): Poczatek skryptu MUSI miec 3 szybkie bloki:
   - Uwaga (0-5s): EMPATYCZNE TWIERDZENIE o bolu wiernego.
   - Osadzenie zmyslowe (5-10s): Polacz bol ze scena {periodo}.
   - Autorytet/Agenda (10-15s): Powiedz, ze {persona_nominativo} ma slowo wyzwolenia.
4. NATYCHMIASTOWE CTA: {cta_comentarios}
5. RESET UWAGI (W POLOWIE): Dokladnie w polowie skryptu wstaw mowiaca fraze.
6. NIEWIDOCZNE HACZYKI RETENCJI: Co 300 do 400 slow organicznie wplec jeden z: (a) ANTYCYPACJA; (b) CZESCIOWE OBJAWIENIE; (c) WALIDACJA EMOCJONALNA; (d) ZMIANA BLOKU.

OGOLNE ZASADY:
7. ZABRANIA SIE WSPOMINANIA DOKLADNYCH GODZIN. Uzywaj tylko "{periodo}".
8. PAUZY: OBOWIAZKOWO uzywaj obfitych wielokropkow (...).
9. ANTY-JSON: Pisz CZYSTYM TEKSTEM. ZABRANIA SIE JSON, nawiasow klamrowych ani gwiazdek (*).
{regra_persona}
{regra_meditacao}

DOKLADNY FORMAT:
{instrucao_titulo}
THUMB: [Wyzwalacz pilnosci — maks. 4 slowa po polsku]
SCRIPT: [Kompletna modlitwa 1500-1800 slow po polsku]
DESC: [Opis 3 akapitow z silnym SEO po polsku. PIERWSZY akapit: zaproszenie do transmisji NA ZYWO 24h kanalu ('Wkrotce: modl sie z nami na zywo 24 godziny — aktywuj dzwonek, aby nie przegapic zadnej modlitwy'). DRUGI akapit: emocjonalny opis tej modlitwy. TRZECI akapit: slowa kluczowe i hashtagi.]
TAGS: [Tagi po polsku oddzielone przecinkami]
"""

    texto_ia = None
    for i in range(5):
        try:
            texto_ia = _gerar(modelos_cascata[i], prompt_principal)
            break
        except Exception as gemini_err: print(f"Blad Gemini (proba {i+1}/5): {gemini_err}"); time.sleep(esperas_exponenciais[i])

    if not texto_ia: continue

    try:
        t_match = re.search(r'TITLE:\s*(.*?)(?=THUMB:|SCRIPT:|DESC:|TAGS:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        th_match = re.search(r'THUMB:\s*(.*?)(?=SCRIPT:|DESC:|TAGS:|TITLE:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        g_match = re.search(r'SCRIPT:\s*(.*?)(?=DESC:|TAGS:|TITLE:|THUMB:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        d_match = re.search(r'DESC:\s*(.*?)(?=TAGS:|TITLE:|THUMB:|SCRIPT:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        tg_match = re.search(r'TAGS:\s*(.*?)(?=TITLE:|THUMB:|SCRIPT:|DESC:|$)', texto_ia, re.IGNORECASE | re.DOTALL)

        titulo_final = re.sub(r'[*"\[\]]', '', t_match.group(1)).strip() if t_match else "Potezna Modlitwa"
        thumb_final = re.sub(r'[*"\[\]]', '', th_match.group(1)).strip() if th_match else "CUD DZIS"
        roteiro_final = g_match.group(1).strip() if g_match else texto_ia
        desc_final = d_match.group(1).strip() if d_match else "Codzienna modlitwa."
        tags_final = re.sub(r'[*\[\]]', '', tg_match.group(1)).strip() if tg_match else "modlitwa, wiara, ochrona"

        nova_linha = [str(data_alvo), horario, "Ready for Audio", persona, idioma, tema_gerado, titulo_final, roteiro_final, tags_final, desc_final, "Pending", thumb_final]
        aba.update(values=[nova_linha], range_name=f"A{proxima_linha_vazia}:L{proxima_linha_vazia}")
        print(f"Sukces! Wiersz {proxima_linha_vazia} wypelniony.")
        proxima_linha_vazia += 1
        time.sleep(5)
    except Exception as e: print(f"Blad zapisu: {e}")
