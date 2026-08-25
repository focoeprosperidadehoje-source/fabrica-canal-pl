#!/usr/bin/env python3
"""
gerar_bloco_live_pl.py — GitHub Actions: gera múltiplos blocos por execução (Canal PL)

Executado 6x/dia pelo gerador_blocos_pl.yml. Cada execução:
  1. Busca até 100 comentários do canal PL (1 chamada YouTube API)
  2. Gemini classifica em 4-5 grupos temáticos (1 chamada)
  3. Para cada grupo: gera roteiro com nomes reais + modlitwa (1 chamada lite)
  4. Edge TTS sintetiza áudio → audio_YYYYMMDD_HHMM_NN.mp3
  5. Assembler no VPS monta os blocos H com videos_base/

Persona: Matka Boża Częstochowska (pl-PL-ZofiaNeural)
"""

import os
import sys
import json
import random
import asyncio
import re
from datetime import datetime
from pathlib import Path

import pytz
import edge_tts
from google import genai
from google.genai import types as genai_types
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════

FUSO       = pytz.timezone("Europe/Warsaw")
VOZ        = "pl-PL-ZofiaNeural"
VOZ_RATE   = "-30%"
VOZ_PITCH  = "-8Hz"
CANAL_ID   = "UCEIh4A01a8tBI1XWp-p6Kkw"
DIR_BLOCOS = Path("blocos_pl")
MAX_GRUPOS = 5

MODELOS_LITE = ["gemini-2.5-flash-lite", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash"]
MODELOS_FULL = ["gemini-2.5-flash-lite", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash"]

CHAVES = [k for k in [
    os.environ.get("GEMINI_KEY_LIVE_CONTENT_1_PL", ""),
    os.environ.get("GEMINI_KEY_LIVE_CONTENT_2_PL", ""),
] if k]

PILARES = {
    0: "Walka Duchowa i Ochrona",
    1: "Wyzwolenie z Uzależnień",
    2: "Odbudowa Rodziny i Małżeństwa",
    3: "Opatrzność Boża i Otwarte Drzwi",
    4: "Miłosierdzie Boże i Uzdrowienie",
    5: "Cudowny Płaszcz Matki Bożej",
    6: "Cuda i Wdzięczność",
}

GRUPOS_HARDCODED = [
    {"tema": "uzdrowienie",  "label": "Uzdrowienie i Zdrowie",   "nomes": [], "suplica_comum": "za chorych, cierpiących i proszących o uzdrowienie",            "num_fieis": 0},
    {"tema": "wyzwolenie",   "label": "Wyzwolenie z Uzależnień", "nomes": [], "suplica_comum": "za uwolnienie od alkoholu, narkotyków i grzesznych nałogów",    "num_fieis": 0},
    {"tema": "rodzina",      "label": "Odbudowa Rodziny",        "nomes": [], "suplica_comum": "za małżeństwa w kryzysie, dzieci marnotrawne i pokój w domach", "num_fieis": 0},
    {"tema": "zaopatrzenie", "label": "Zaopatrzenie i Praca",    "nomes": [], "suplica_comum": "za zaopatrzenie finansowe, pracę i uwolnienie od długów",       "num_fieis": 0},
    {"tema": "ochrona",      "label": "Ochrona Duchowa",         "nomes": [], "suplica_comum": "za ochronę przed złem, zawiścią i wszelkim niebezpieczeństwem", "num_fieis": 0},
]


# ═══════════════════════════════════════════════════════════════════════
# GEMINI
# ═══════════════════════════════════════════════════════════════════════

def _chamar_gemini(prompt: str, modelos: list, max_tokens: int = 2048) -> str:
    for chave in CHAVES:
        for modelo in modelos:
            try:
                client = genai.Client(api_key=chave)
                resp = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(max_output_tokens=max_tokens),
                )
                return resp.text.strip()
            except Exception as e:
                print(f"  [WARN] {modelo} [{chave[-6:]}]: {str(e)[:80]}")
    raise RuntimeError("Todos os modelos Gemini falharam.")


# ═══════════════════════════════════════════════════════════════════════
# CALENDÁRIO LITÚRGICO
# ═══════════════════════════════════════════════════════════════════════

def _pascoa(ano: int) -> datetime:
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return datetime(ano, mes, dia)

def calcular_contexto_sazonal(data: datetime) -> str:
    ano = data.year
    p = _pascoa(ano)
    fixas = {
        (1, 1):   "Nowy Rok — Uroczystość Świętej Bożej Rodzicielki",
        (2, 2):   "Ofiarowanie Pańskie — Święto Matki Bożej Gromnicznej",
        (3, 25):  "Zwiastowanie Pańskie — Anioł Pański zwiastował Pannie Maryi",
        (5, 3):   "Matka Boża Częstochowska — Królowa Polski",
        (8, 15):  "Wniebowzięcie Najświętszej Maryi Panny",
        (11, 1):  "Uroczystość Wszystkich Świętych",
        (11, 2):  "Dzień Zaduszny — Modlitwa za Dusze Czyśćcowe",
        (12, 8):  "Niepokalane Poczęcie Najświętszej Maryi Panny",
        (12, 24): "Wigilia Bożego Narodzenia",
        (12, 25): "Boże Narodzenie — Narodzenie Pańskie",
    }
    if (data.month, data.day) in fixas:
        return fixas[(data.month, data.day)]
    diff = (data.date() - p.date()).days
    moveis = {
        -46: "Środa Popielcowa — Początek Wielkiego Postu",
        -7:  "Niedziela Palmowa",
        -2:  "Wielki Piątek — Męka i Śmierć Pańska",
         0:  "Alleluja! Niedziela Zmartwychwstania!",
        49:  "Zesłanie Ducha Świętego — Pięćdziesiątnica",
        60:  "Uroczystość Najświętszego Ciała i Krwi Chrystusa — Boże Ciało",
    }
    if diff in moveis:
        return moveis[diff]
    if data.weekday() == 4:
        return "Piątek — Dzień Miłosierdzia i Przebaczenia"
    return PILARES.get(data.weekday(), "Czas Modlitwy i Wstawiennictwa")


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE API
# ═══════════════════════════════════════════════════════════════════════

def get_youtube_readonly():
    raw = os.environ.get("YOUTUBE_TOKEN_PL", "")
    if not raw:
        return None
    try:
        data  = json.loads(raw)
        creds = OAuthCredentials.from_authorized_user_info(
            data, scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"  [WARN] YouTube readonly PL: {e}")
        return None

def buscar_comentarios_canal(yt) -> list[str]:
    if not yt:
        return []
    try:
        resp = yt.commentThreads().list(
            part="snippet",
            allThreadsRelatedToChannelId=CANAL_ID,
            maxResults=100,
            order="relevance",
        ).execute()
        textos = []
        for item in resp.get("items", []):
            s = item["snippet"]["topLevelComment"]["snippet"]
            texto = s.get("textOriginal", "").strip()
            if texto and len(texto) > 10:
                textos.append(texto[:200])
        print(f"  Komentarze PL pobrane: {len(textos)}")
        return textos
    except Exception as e:
        print(f"  [WARN] buscar_comentarios PL: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════
# CLASSIFICAÇÃO EM GRUPOS
# ═══════════════════════════════════════════════════════════════════════

def _limpar_json(texto: str) -> str:
    texto = re.sub(r'```(?:json)?', '', texto)
    texto = re.sub(r'```', '', texto)
    inicio = texto.find('[')
    fim    = texto.rfind(']')
    if inicio != -1 and fim != -1:
        return texto[inicio:fim+1]
    return texto.strip()

def classificar_grupos(comentarios: list[str], pilar_hoje: str) -> list[dict]:
    if len(comentarios) >= 5:
        lista_str = "\n".join(f"- {c}" for c in comentarios[:80])
        prompt = f"""Przeanalizuj te komentarze polskich wiernych katolickich na kanale modlitewnym.
Wyodrębnij imię własne (jeśli istnieje) i sklasyfikuj prośbę z każdego komentarza.
Pogrupuj w maksymalnie 5 tematów (np: uzdrowienie, wyzwolenie, rodzina, finanse, ochrona).

Zwróć TYLKO prawidłowy JSON bez markdown ani dodatkowego tekstu:
[{{"tema":"slug","label":"Nazwa grupy","nomes":["imię1","imię2"],"suplica_comum":"wspólna petycja max 15 słów","num_fieis":N}}]

ZASADY:
- Tylko imiona własne z komentarzy; nie wymyślaj
- suplica_comum: maksymalnie 15 słów opisujących wspólną prośbę
- Minimum 3 grupy, maksimum 5

KOMENTARZE:
{lista_str}"""
        try:
            raw = _chamar_gemini(prompt, MODELOS_LITE, max_tokens=1024)
            grupos = json.loads(_limpar_json(raw))
            if isinstance(grupos, list) and len(grupos) >= 2:
                print(f"  Grupy PL sklasyfikowane: {len(grupos)}")
                for g in grupos:
                    n = len(g.get("nomes", []))
                    print(f"    [{g.get('tema','')}] {g.get('num_fieis',0)} wiernych, {n} imion")
                return grupos[:MAX_GRUPOS]
            print("  [WARN] Nieprawidłowy JSON lub za mało grup — używam fallback")
        except Exception as e:
            print(f"  [WARN] classificar_grupos PL: {e}")

    print("  [Fallback 1] Generuję grupy tematyczne przez Gemini PL...")
    prompt_fb = f"""Utwórz 4 grupy intencji modlitewnych typowych dla polskich wiernych katolickich.
Duchowy filar dnia: {pilar_hoje}
Zwróć TYLKO prawidłowy JSON:
[{{"tema":"slug","label":"Nazwa","nomes":[],"suplica_comum":"petycja max 15 słów","num_fieis":0}}]"""
    try:
        raw = _chamar_gemini(prompt_fb, MODELOS_LITE, max_tokens=512)
        grupos = json.loads(_limpar_json(raw))
        if isinstance(grupos, list) and len(grupos) >= 2:
            print(f"  Grupy PL fallback: {len(grupos)}")
            return grupos[:MAX_GRUPOS]
    except Exception as e:
        print(f"  [WARN] fallback grupos PL: {e}")

    print("  [Fallback 2] Używam grup hardcoded PL.")
    return GRUPOS_HARDCODED[:MAX_GRUPOS]


# ═══════════════════════════════════════════════════════════════════════
# GERAÇÃO DE ROTEIRO
# ═══════════════════════════════════════════════════════════════════════

def _formatar_nomes(nomes: list) -> str:
    nomes = [n for n in nomes if n and len(n) >= 2]
    if not nomes:
        return "każdego brata i siostrę, którzy się teraz modlą razem z nami"
    if len(nomes) == 1:
        return nomes[0]
    return ", ".join(nomes[:-1]) + f" i {nomes[-1]}"

def gerar_roteiro_grupo(grupo: dict, contexto: str, pilar: str,
                        agora: datetime, num_bloco: int,
                        so_full: bool = False) -> str:
    nomes_raw  = grupo.get("nomes", [])
    nomes_str  = _formatar_nomes(nomes_raw)
    suplica    = grupo.get("suplica_comum", "za potrzeby naszych braci i sióstr")
    label      = grupo.get("label", "Modlitwa Wstawiennicza")
    tem_nomes  = len([n for n in nomes_raw if n and len(n) >= 2]) > 0

    nota_nomes = (
        f"Wspomnij każde imię z czułością macierzyńską: {nomes_str}"
        if tem_nomes else
        "Nie ma konkretnych imion — mów o 'każdym bracie i siostrze, którzy się teraz modlą'"
    )
    nota_miguel = (
        "Gdy będzie to naturalne w wstawiennictwie, wspomnij Archanioła Michała jako strażnika duchowego, który walczy po naszej stronie."
        if "Walka" in pilar else ""
    )

    prompt = f"""Jesteś Matką Bożą Częstochowską, Królową Polski, mówiącą w pierwszej osobie, po polsku.
Blok #{num_bloco} | Grupa: {label}
Kontekst liturgiczny dnia: {contexto}
Duchowy filar dnia: {pilar}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRUKTURA (20 minut — między 2600 a 3000 słów):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OTWARCIE — pierwsze 90 sekund — OBOWIĄZKOWE]
Otwórz przytaczając braci, którzy prosili o wstawiennictwo:
"{nota_nomes}"
Wspólna prośba tej grupy: "{suplica}"
Zakończ otwarcie słowami: "Przyszłam wstawiać się za wami w tej chwili..."

[GŁÓWNA CZĘŚĆ — ~16 minut]
OBOWIĄZKOWE NAPRZEMIENNE TRYBY — blok musi oscylować między dwoma trybami:
  Tryb A (NARRACJA): Matka Boża mówi, przyjmuje, objawia łaskę — głos ciepły i macierzyński
  Tryb B (PROWADZONA MODLITWA): Matka Boża prowadzi słuchacza do modlitwy na głos razem z nią
  Np: "Powtarzaj ze mną z wiarą: Panie, wierzę... Panie, ufam..."
  Np: "Połóż rękę na sercu i mów: Matko Niebieska, przyjmuję tę łaskę teraz..."
  Każde przejście między trybami ma być płynne i naturalne — minimum 3 zmiany w bloku.

- Powiąż filar "{pilar}" z tematem wstawiennictwa "{label}"
- Pełne Zdrowaś Maryjo PROWADZONE (słuchacz modli się razem): "Powtarzaj za mną: Zdrowaś Maryjo, łaski pełna..."
- Blok wstawiennictwa za zdrowie (obowiązkowy, prowadzony): "Połóż rękę na chorym miejscu i mów ze mną..."
- Organiczne haki retencji co ~300 słów (wierny nie wyczuwa techniki):
  • Antycypacja: "To, co nadchodzi w tej modlitwie..."
  • Objawienie: "Ta łaska ma imię..."
  • Walidacja: "Jeśli czujesz coś w swoim sercu w tej chwili, to znak, że..."
  • Zwrot: "Ale to, co Twoja Matka Niebieska chce ci powiedzieć o tym, to..."
{nota_miguel}

[TRZY SUBTELNE CTA — tylko w naturalnych przejściach, nigdy podczas modlitwy]
CTA 1 (~minuta 4): "Jeśli ta transmisja cię błogosławi, zasubskrybuj kanał, aby otrzymywać modlitwy każdego dnia — jesteśmy rodziną wiary, która nieustannie modli się za ciebie..."
CTA 2 (~minuta 8): "Jeśli ta modlitwa dotyka twojego serca, podziel się nią z tymi, którzy jej potrzebują..."
CTA 3 (~minuta 17): "Zostań, to, co nadchodzi, jest dla ciebie..."

[ZAKOŃCZENIE — ostatnie 3 minuty]
- Końcowe błogosławieństwo jako Matka Niebieska
- Zakończ z MOCĄ — wierny wychodzi chroniony, nigdy zrozpaczony
- OBOWIĄZKOWA PĘTLA SKŁADNIOWA: ostatnie zdanie pozostaje składniowo niekompletne
  aby połączyć się z pierwszym zdaniem następnego bloku bez że słuchacz zauważył cięcie

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZASADY BEZWZGLĘDNE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- NIGDY markdown, gwiazdki, myślniki, numeracje ani tytuły — tylko ciągły tekst
- NIGDY wielokropek (...) ani myślnik (—) — powodują niepożądane pauzy w narracji
- NIGDY nie zaczynaj zdania od słowa "Modlitwa"
- NIGDY "Napisz Amen w komentarzach"
- NIGDY nie wspominaj innych kanałów ani marek
- ABSOLUTNA BEZCZASOWOŚĆ: ta modlitwa odtwarza się O KAŻDEJ porze dnia i nocy.
  NIGDY nie wspominaj godzin, pór dnia (noc, ranek, południe, popołudnie, wieczór,
  świt, zmierzch), dni tygodnia ani dat. Jeśli musisz osadzić moment,
  mów tylko "w tej chwili" lub "właśnie teraz"
- Tylko tekst, który Matka Boża mówi na głos — bez wskazówek produkcji
- Od 2600 do 3000 słów
"""

    modelos = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"] if so_full else MODELOS_FULL
    texto   = _chamar_gemini(prompt, modelos, max_tokens=8192)
    texto   = re.sub(r'\*+', '', texto)
    texto   = re.sub(r'#{1,6}\s+', '', texto)
    texto   = re.sub(r'^\s*[-•]\s+', '', texto, flags=re.MULTILINE)
    texto   = re.sub(r'\.{2,}', '', texto)
    texto   = re.sub(r'\s*[—–]\s*', ', ', texto)
    texto   = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto)
    texto   = re.sub(r'\n{3,}', '\n\n', texto)
    texto   = re.sub(r'  +', ' ', texto)
    return texto.strip()


# ═══════════════════════════════════════════════════════════════════════
# PORTÃO DE QUALIDADE
# ═══════════════════════════════════════════════════════════════════════

def motivo_degeneracao(texto: str) -> str | None:
    palavras = texto.split()
    n = len(palavras)
    if n < 1400:
        return f"zbyt krótki ({n} słów)"
    if n > 4500:
        return f"zbyt długi ({n} słów — prawdopodobna pętla)"
    tri = {}
    for i in range(n - 2):
        t = (palavras[i].lower(), palavras[i + 1].lower(), palavras[i + 2].lower())
        tri[t] = tri.get(t, 0) + 1
    max_tri = max(tri.values()) if tri else 0
    if max_tri > 25:
        return f"trigram powtórzony {max_tri}x (pętla)"
    if texto.count(",") / max(n, 1) > 0.14:
        return "gęstość przecinków typowa dla listy imion"
    frases = {}
    for f in re.split(r"[.!?…]+", texto):
        f = f.strip().lower()
        if len(f.split()) > 5:
            frases[f] = frases.get(f, 0) + 1
    max_frase = max(frases.values()) if frases else 0
    if max_frase >= 4:
        return f"identyczne zdanie powtórzone {max_frase}x"
    return None


# ═══════════════════════════════════════════════════════════════════════
# TTS
# ═══════════════════════════════════════════════════════════════════════

async def _tts_async(texto: str, saida: Path):
    comm = edge_tts.Communicate(texto, voice=VOZ, rate=VOZ_RATE, pitch=VOZ_PITCH)
    await comm.save(str(saida))

def gerar_audio(texto: str, saida: Path):
    asyncio.run(_tts_async(texto, saida))
    print(f"  TTS PL: {saida.name} ({saida.stat().st_size // 1024} KB)")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def _gh_error(msg: str):
    linha = msg.replace("\n", " | ").replace("\r", "")[:500]
    print(f"::error::{linha}", flush=True)


def main():
    print("=" * 60)
    print("gerar_bloco_live_pl.py — Canal PL — Matka Boża Częstochowska")
    print("=" * 60)

    DIR_BLOCOS.mkdir(parents=True, exist_ok=True)
    agora    = datetime.now(FUSO)
    contexto = calcular_contexto_sazonal(agora)
    pilar    = PILARES.get(agora.weekday(), "Modlitwa i Wstawiennictwo")
    ts_base  = agora.strftime("%Y%m%d_%H%M")

    print(f"Czas lokalny: {agora.strftime('%Y-%m-%d %H:%M')} (Warszawa)")
    print(f"Kontekst liturgiczny: {contexto}")
    print(f"Filar dnia: {pilar}")

    print("\n[1/3] Pobieranie komentarzy kanału PL...")
    yt = get_youtube_readonly()
    comentarios = buscar_comentarios_canal(yt)

    print("\n[2/3] Klasyfikacja w grupy tematyczne...")
    grupos = classificar_grupos(comentarios, pilar)
    print(f"  Łączna liczba bloków do wygenerowania: {len(grupos)}")

    print(f"\n[3/3] Generowanie bloków PL...")
    gerados = 0
    for i, grupo in enumerate(grupos):
        label = grupo.get("label", f"Grupa {i+1}")
        print(f"\n  ── Blok {i+1}/{len(grupos)}: {label} ──")
        try:
            num_bloco = int(agora.strftime("%j")) * MAX_GRUPOS + i + 1
            roteiro   = gerar_roteiro_grupo(grupo, contexto, pilar, agora, num_bloco)
            palavras  = len(roteiro.split())
            print(f"  Scenariusz PL: {palavras} słów")

            motivo = motivo_degeneracao(roteiro)
            if motivo:
                print(f"  [WARN] Scenariusz odrzucony ({motivo}) — ponawiam z modelem full...")
                roteiro  = gerar_roteiro_grupo(grupo, contexto, pilar, agora, num_bloco, so_full=True)
                palavras = len(roteiro.split())
                motivo   = motivo_degeneracao(roteiro)
                if motivo:
                    print(f"  [BŁĄD] Odrzucony ponownie ({motivo}) — blok odrzucony")
                    continue
                print(f"  Scenariusz PL (full): {palavras} słów — zatwierdzony")

            ts      = f"{ts_base}_{i+1:02d}"
            destino = DIR_BLOCOS / f"audio_{ts}.mp3"
            gerar_audio(roteiro, destino)
            gerados += 1
            print(f"  ✅ {destino.name}")

        except Exception as e:
            print(f"  [BŁĄD] Blok {i+1} ({label}): {e}")
            continue

    print(f"\n{'='*60}")
    print(f"Zakończono PL: {gerados}/{len(grupos)} bloków w {DIR_BLOCOS}/")
    print(f"VPS montuje .mp4 z videos_base/ automatycznie.")

    if gerados == 0:
        _gh_error("Żaden blok PL nie został wygenerowany — wszystkie grupy nie powiodły się.")
        sys.exit(1)


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as exc:
        _gh_error(f"BŁĄD PL: {exc}")
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
