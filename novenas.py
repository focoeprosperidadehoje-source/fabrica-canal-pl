# -*- coding: utf-8 -*-
"""novenas.py — Slot 06:00 (Novenas) — gerado a partir do padrão do PT (aprovado por Leandro em 2026-09-25). Somente personas marianas do canal."""
import datetime

CFG = {
 "canal": "PL", "tz": "Europe/Warsaw", "lang_name": "Polish (język polski)",
 "ativacao": datetime.date(2026, 9, 30), "epoca_pedidos": datetime.date(2026, 9, 30),
 "status_pronto": "Ready for Audio", "invocacao_padrao": "Matko Boża Częstochowska",
 "promessa_regra": 'MUST start with "Matka Boża". Ex: "Matka Boża Uzdrawia Twój Dom", "Matka Boża Otwiera Drzwi".',
 "festas": [
   {"id": "krolowa", "inicio": (4, 24), "nome": "Nowenna do Matki Bożej Królowej Polski", "invocacao": "Maryjo, Królowo Polski",
    "festa": "Uroczystość Najświętszej Maryi Panny Królowej Polski (3 maja)"},
   {"id": "czestochowa", "inicio": (8, 17), "nome": "Nowenna do Matki Bożej Częstochowskiej", "invocacao": "Matko Boża Częstochowska",
    "festa": "Uroczystość Najświętszej Maryi Panny Częstochowskiej (26 sierpnia)"},
   {"id": "niepokalane", "inicio": (11, 29), "nome": "Nowenna do Niepokalanego Poczęcia NMP", "invocacao": "Maryjo Niepokalana",
    "festa": "Uroczystość Niepokalanego Poczęcia Najświętszej Maryi Panny (8 grudnia)"},
   {"id": "bozenarodzenie", "inicio": (12, 16), "nome": "Nowenna przed Bożym Narodzeniem z Maryją", "invocacao": "Matko Boża",
    "festa": "Boże Narodzenie (25 grudnia) — Maryja, Matka oczekująca Dzieciątka Jezus"},
 ],
 "intencoes_festa": ["uzdrowienie z chorób i zdrowie bliskich", "jedność i odnowienie rodziny", "pojednanie, przebaczenie i pokój",
   "uwolnienie od nałogów i wszelkich zniewoleń", "opieka nad dziećmi i ich przyszłość", "praca, utrzymanie i otwarte drzwi",
   "duchowa ochrona domu przed wszelkim złem", "sprawy niemożliwe i beznadziejne", "wdzięczność za otrzymane łaski i zawierzenie Maryi"],
 "categorias": {
   "saude": ("Nowenna o Uzdrowienie i Zdrowie", "choroby, zdrowie fizyczne, leczenie i operacje"),
   "familia": ("Nowenna o Odnowienie Rodziny", "kłótnie, oddalenie i odnowienie rodziny i małżeństwa"),
   "emprego": ("Nowenna o Pracę", "bezrobocie, praca, utrzymanie i otwarte drzwi"),
   "dividas": ("Nowenna o Wyjście z Długów", "długi, trudności finansowe i Boża opatrzność"),
   "filhos": ("Nowenna za Dzieci", "opieka, droga życia i nawrócenie dzieci"),
   "vicios": ("Nowenna o Uwolnienie od Nałogów", "nałogi, uzależnienia i zniewolenia bliskich"),
   "ansiedade": ("Nowenna o Pokonanie Lęku", "lęk, niepokój, głęboki smutek i pokój serca"),
   "protecao": ("Nowenna o Duchową Ochronę", "ochrona przed złem, zazdrością i atakami duchowymi"),
   "causas": ("Nowenna w Sprawach Beznadziejnych", "sprawy niemożliwe, pilne i beznadziejne"),
   "luto": ("Nowenna o Pocieszenie w Żałobie", "żałoba, tęsknota i pocieszenie po stracie bliskiej osoby")},
 "meses": ["Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec","Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"],
 "completa": "(Cała)", "dia_label": "Dzień {n}", "thumb_fmt": "NOWENNA DZIEŃ {n}",
 "data_no_titulo_festa": False, "data_fmt": "",
 "periodo": "tego poranka",
 "desc_link": "📿 Odmów całą nowennę, dzień po dniu: {url}",
 "cap_titulo": "⏱️ Rozdziały nowenny:",
 "cap": ["Otwarcie i intencja dnia", "Rozważanie Słowa", "Modlitwa nowenny", "Błaganie dnia", "Ojcze nasz, Zdrowaś Maryjo i Chwała Ojcu", "Zakończenie i błogosławieństwo"],
 "sinal_da_cruz": "W imię Ojca... i Syna... i Ducha Świętego... Amen...",
 "ato_contricao": "Odmówmy razem akt żalu... Ach, żałuję za me złości... jedynie dla Twej miłości... bądź miłościw mnie grzesznemu... dla Ciebie odpuść bliźniemu... Amen...",
 "pai_nosso": ("Ojcze nasz, który jesteś w niebie... święć się imię Twoje... przyjdź królestwo Twoje... bądź wola Twoja jako w niebie, tak i na ziemi... "
   "Chleba naszego powszedniego daj nam dzisiaj... i odpuść nam nasze winy... jako i my odpuszczamy naszym winowajcom... "
   "i nie wódź nas na pokuszenie... ale nas zbaw ode złego... Amen..."),
 "ave_maria": ("Zdrowaś Maryjo, łaski pełna... Pan z Tobą... błogosławionaś Ty między niewiastami... "
   "i błogosławiony owoc żywota Twojego Jezus... Święta Maryjo, Matko Boża... módl się za nami grzesznymi... teraz i w godzinę śmierci naszej... Amen..."),
 "gloria": "Chwała Ojcu... i Synowi... i Duchowi Świętemu... Jak była na początku, teraz i zawsze, i na wieki wieków... Amen...",
 "oracoes_festa": {
   "bozenarodzenie": ("Odmówmy teraz modlitwę tej nowenny... Maryjo... Matko nadziei... "
     "Ty, która nosiłaś w sercu Dzieciątko mające się narodzić... przygotuj także moje serce na przyjęcie Jezusa w te Święta... "
     "W tym dniu nowenny powierzam Ci moją intencję i moją rodzinę... niech światło Betlejem wejdzie do naszego domu... i przyniesie pokój... uzdrowienie... i jedność... Amen...")},
 "oracao_festa_generica": ("Odmówmy teraz modlitwę tej nowenny... O {inv}... Matko naszego narodu i naszych rodzin... "
   "spójrz na moje zmęczone serce... Ty, która powiedziałaś Bogu tak... naucz mnie ufać tak, jak Ty zaufałaś... "
   "W tym dniu Twojej nowenny powierzam Ci moją intencję... Okryj mnie swoim płaszczem... chroń mój dom... ulecz to, co zranione... "
   "i przedstaw moją prośbę Twojemu Synowi Jezusowi... Amen..."),
 "oracao_pedido": ("Odmówmy teraz modlitwę tej nowenny... Matko Boża Częstochowska... Matko Boga i nasza Matko... "
   "w tej nowennie przychodzę do Twoich stóp z prośbą, która ciąży mi na sercu... Ty znasz mój ból... zanim go wypowiem... "
   "W tym dniu nowenny powierzam Ci moją intencję... i proszę, zanieś ją Twojemu Synowi Jezusowi... jak zaniosłaś potrzebę nowożeńców w Kanie... "
   "Niech się dzieje wola Boża... a mnie daj siłę, by czekać z wiarą... Amen..."),
 "jaculatoria": "{inv}... módl się za nami...",
 "cta_pista": "invite them to write in the comments their intention or the name of the person they entrust to Our Lady of Częstochowa, because these intentions are prayed in our 24-hour live stream",
}

# ─────────────────────── MOTOR (idêntico em todos os canais) ───────────────────────
import datetime

CANAL = CFG["canal"]
TZ = CFG["tz"]
ATIVACAO_06H = CFG["ativacao"]
EPOCA_PEDIDOS = CFG["epoca_pedidos"]
FESTAS = CFG["festas"]
INTENCOES_FESTA = CFG["intencoes_festa"]
CATEGORIAS = CFG["categorias"]
ROTACAO_FALLBACK = ["saude", "familia", "emprego", "ansiedade", "filhos", "protecao", "vicios", "dividas", "causas", "luto"]
JANELA_ANTI_REPETICAO = 3
MIN_COMENTARIOS_RANKING = 5
STATUS_PRONTO = CFG["status_pronto"]
LANG_NAME = CFG["lang_name"]
PROGRESSAO_PEDIDO = {
    1: "Day of SURRENDER: present the pain honestly and open the heart.",
    2: "Day of SURRENDER: admit what we cannot carry alone.",
    3: "Day of SURRENDER: forgive and let go of what weighs, to receive grace.",
    4: "Day of PERSEVERANCE: keep faith even when nothing seems to change.",
    5: "Day of PERSEVERANCE: the strength of Mary at the foot of the cross.",
    6: "Day of PERSEVERANCE: fight discouragement and the voice of fear.",
    7: "Day of TRUST: signs that grace is already on its way.",
    8: "Day of TRUST: give thanks in advance for what God will do.",
    9: "Day of GRATITUDE and CONSECRATION: entrust life and the cause to Our Lady.",
}
ABA_NOVENAS = "NOVENAS"
ABA_TEMAS = "TEMAS_COMENTARIOS"


def _festas_do_ano(ano):
    out = []
    for f in FESTAS:
        ini = datetime.date(ano, f["inicio"][0], f["inicio"][1])
        out.append((ini, ini + datetime.timedelta(days=8), ini + datetime.timedelta(days=9), f))
    return sorted(out, key=lambda x: x[0])


def _festa_em(d):
    for ano in (d.year - 1, d.year):
        for ini, fim, dia_festa, f in _festas_do_ano(ano):
            if ini <= d <= fim:
                return ("festa", f, (d - ini).days + 1, ini)
            if d == dia_festa:
                return ("dia_festa", f, None, ini)
    return None


def _proxima_festa_inicio(d):
    for ano in (d.year, d.year + 1):
        for ini, _, _, _ in _festas_do_ano(ano):
            if ini >= d:
                return ini
    return None


def plano_do_dia(d):
    if d < ATIVACAO_06H:
        return None
    fe = _festa_em(d)
    if fe:
        tipo, f, n, ini = fe
        if tipo == "festa":
            return {"tipo": "festa", "dia": n, "festa": f, "ciclo_inicio": ini}
        return {"tipo": "avulsa", "motivo": f"dia da festa ({f['id']})"}
    if d < EPOCA_PEDIDOS:
        return {"tipo": "avulsa", "motivo": "antes da época de pedidos"}
    cursor = EPOCA_PEDIDOS
    guard = 0
    while cursor <= d and guard < 2000:
        guard += 1
        fe_c = _festa_em(cursor)
        if fe_c:
            cursor = fe_c[3] + datetime.timedelta(days=10)
            continue
        prox = _proxima_festa_inicio(cursor)
        fim_ciclo = cursor + datetime.timedelta(days=8)
        if prox is None or fim_ciclo < prox:
            if cursor <= d <= fim_ciclo:
                return {"tipo": "pedido", "dia": (d - cursor).days + 1, "ciclo_inicio": cursor}
            cursor = fim_ciclo + datetime.timedelta(days=1)
        else:
            if cursor <= d < prox:
                return {"tipo": "avulsa", "motivo": "intervalo antes de novena de festa"}
            cursor = prox
    return {"tipo": "avulsa", "motivo": "fallback"}


def nome_mes(d):
    return f"{CFG['meses'][d.month - 1]} {d.year}"


def nome_playlist(plano, categoria=None):
    if plano["tipo"] == "festa":
        return f"{plano['festa']['nome']} {plano['ciclo_inicio'].year} {CFG['completa']}"
    if plano["tipo"] == "pedido":
        return f"{CATEGORIAS[categoria][0]} — {nome_mes(plano['ciclo_inicio'])}"
    return None


def montar_titulo(plano, promessa, categoria=None, data=None):
    """[Palavra-chave de busca] + [Dia N] + 🙏 + [Dor/Promessa]."""
    promessa = (promessa or "").strip().strip(".").strip()
    n = plano["dia"]
    dia_lbl = CFG["dia_label"].format(n=n)
    if plano["tipo"] == "festa":
        base = f"{plano['festa']['nome']} {dia_lbl} 🙏"
        if CFG.get("data_no_titulo_festa") and data is not None:
            base += " " + CFG["data_fmt"].format(d=data.day, m=CFG["meses"][data.month - 1])
            base += " |"
    else:
        base = f"{CATEGORIAS[categoria][0]} – {dia_lbl} 🙏"
    titulo = f"{base} {promessa}".strip()
    if len(titulo) > 100:
        titulo = base.rstrip(" |")
    return titulo


def texto_thumb(plano):
    return CFG["thumb_fmt"].format(n=plano["dia"])


def tema_codificado(plano, categoria=None):
    chave = plano["festa"]["id"] if plano["tipo"] == "festa" else categoria
    return f"NOVENA|{nome_playlist(plano, categoria)}|{plano['dia']}|{plano['tipo']}|{chave}"


def montar_roteiro(plano, gancho, reflexao, suplica, encerramento):
    if plano["tipo"] == "festa":
        f = plano["festa"]
        oracao = CFG["oracoes_festa"].get(f["id"], CFG["oracao_festa_generica"]).format(inv=f["invocacao"])
        jac = CFG["jaculatoria"].format(inv=f["invocacao"])
    else:
        oracao = CFG["oracao_pedido"]
        jac = CFG["jaculatoria"].format(inv=CFG["invocacao_padrao"])
    partes = [gancho.strip(), CFG["sinal_da_cruz"], CFG["ato_contricao"], reflexao.strip(), oracao,
              suplica.strip(), CFG["pai_nosso"], CFG["ave_maria"], CFG["gloria"], jac,
              encerramento.strip(), CFG["sinal_da_cruz"]]
    return "\n\n".join(p for p in partes if p)


def _aba(planilha, nome, cabecalho):
    try:
        return planilha.worksheet(nome)
    except Exception:
        ws = planilha.add_worksheet(title=nome, rows=1000, cols=len(cabecalho))
        ws.update(values=[cabecalho], range_name="A1")
        return ws


def escolher_tema_pedido(planilha, ciclo_inicio):
    ws_nov = _aba(planilha, ABA_NOVENAS, ["Canal", "Inicio", "Tipo", "Categoria", "Fonte", "Criado_em"])
    linhas = ws_nov.get_all_values()[1:]
    ciclo_str = str(ciclo_inicio)
    do_canal = [l for l in linhas if len(l) >= 4 and l[0] == CANAL and l[2] == "pedido"]
    for l in do_canal:
        if l[1] == ciclo_str and l[3] in CATEGORIAS:
            return l[3]
    usados = [l[3] for l in sorted(do_canal, key=lambda x: x[1]) if l[1] < ciclo_str][-JANELA_ANTI_REPETICAO:]
    escolha, fonte = None, "fallback"
    try:
        ws_t = _aba(planilha, ABA_TEMAS, ["Canal", "Data", "Categoria", "Contagem"])
        rows = [r for r in ws_t.get_all_values()[1:] if len(r) >= 4 and r[0] == CANAL]
        if rows:
            ultima = max(r[1] for r in rows)
            dt_ult = datetime.datetime.strptime(ultima, "%Y-%m-%d").date()
            if (ciclo_inicio - dt_ult).days <= 30:
                lote = []
                for r in rows:
                    if r[1] == ultima and r[2] in CATEGORIAS:
                        try: lote.append((r[2], int(r[3])))
                        except ValueError: pass
                if sum(c for _, c in lote) >= MIN_COMENTARIOS_RANKING:
                    for cat, cnt in sorted(lote, key=lambda x: -x[1]):
                        if cnt > 0 and cat not in usados:
                            escolha, fonte = cat, f"comentarios {ultima}"
                            break
    except Exception as e:
        print(f"[WARN] Ranking de comentários indisponível: {e}")
    if not escolha:
        idx = len(do_canal)
        for i in range(len(ROTACAO_FALLBACK)):
            cand = ROTACAO_FALLBACK[(idx + i) % len(ROTACAO_FALLBACK)]
            if cand not in usados:
                escolha = cand
                break
    ws_nov.append_row([CANAL, ciclo_str, "pedido", escolha, fonte,
                       datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")])
    print(f"📿 Novo ciclo de pedido {ciclo_str}: '{escolha}' ({fonte})")
    return escolha
