"""Monk (passada 1, 21/11): as 10 builds do RPGBot. Rodar da raiz:
python ferramentas/geradores/mon.py && python -m dh expandir progressoes/rpgbot-monk-*.json
Convenções: calibracao/convencoes-passada1.md (seção Monk)."""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import marcial
from marcial import *
marcial.CLASSE = 'monk'


def die(L): return 4 if L < 5 else 6 if L < 11 else 8
def U(n, b, mod_, L, extra='', **k): return A(n, b, f'1d{die(L)}', mod_, extra, **k)   # golpe desarmado


def ss_monk(L, m, extra_profs=(), **k):
    d = dict(sv=sv(L, m, ('for', 'des') + tuple(extra_profs)), **k)
    if L >= 7: d.update(evasion=True, stillness=True)
    if L >= 11: d['imune'] = sorted(set(d.get('imune', [])) | {'veneno'})
    return d


def stun(L, b, wis, golpes, usos=2):
    return {"tipo": "condicao_no_acerto", "nome": "Stunning Strike (ki)", "efeito": "cond_atordoado_um_turno",
            "cd": 8 + pb(L) + wis, "bonus": [b] * golpes, "usos": usos}


def base_monk(L, papel, arma, b, mod_, ub, umod, wis, n_arma=None, defesa=None, saves=None, extra_ctrl=(), sufixo=''):
    """Linhas padrão do monge: sem ki, meia rajada (2 ki), rajada (4 ki) e, a partir do 5, Stunning Strike (4 ki).
    arma = string do dado da arma do ataque (ou None para desarmado); ub/umod = bônus e modificador do desarmado."""
    n = n_arma if n_arma is not None else (1 if L < 5 else 2)
    def at(k):   # k = golpes desarmados na ação bônus por round
        a = [A(n, b, arma, mod_)] if arma else [U(n, ub, umod, L)]
        return {"ataques": a + [U(k, ub, umod, L, nota="ação bônus (Martial Arts / Flurry of Blows)")]}
    d = defesa or {}
    ls = [linha('principal', 'sem ki: ataque + golpe desarmado na ação bônus' + sufixo, at(1), d, saves=saves, papel=papel,
                controle=ctrl(papel, extra_ctrl)),
          linha('meia-rajada', 'Flurry of Blows em 2 dos 4 rounds (2 ki)' + sufixo, at(1.5), d, saves=saves, papel=papel,
                controle=ctrl(papel, extra_ctrl), gasta={"ki": 2}),
          linha('rajada', 'Flurry of Blows todo round (4 ki)' + sufixo, at(2), d, saves=saves, papel=papel,
                controle=ctrl(papel, extra_ctrl), gasta={"ki": 4})]
    if L >= 5:
        golpes = int(n + 2)
        ls.append(linha('atordoar', 'Flurry em 2 rounds + 2 tentativas de Stunning Strike (4 ki)' + sufixo, at(1.5), d,
                        saves=saves, controle=ctrl(papel, [stun(L, ub if not arma else b, wis, golpes)] + list(extra_ctrl)),
                        gasta={"ki": 4}))
    return ls


def rec(L, **extra):
    o = {"ki": {"qtd": L if L >= 2 else 0, "volta": "curto"}}
    o.update(extra)
    return {"espacos": {}, "outros": o}


def corpo_m(L, dx, cn, ws, m, ss, dados=None, bonus_ca=0):
    return dict(ca=10 + mod(dx) + mod(ws) + bonus_ca, pv=hp(dados or [8] * L, mod(cn)), saves=ss)


# ---------------------------------------------------------------- Mercy (Stuck Halfway)
def mercy(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn, ws = 16, 16; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(-1, d, 3, -1, w, -1); b = P + d
    ss = ss_monk(L, m)
    ls = base_monk(L, 'striker', None, b, d, b, d, w, sufixo=' (chicote com o dado de Martial Arts)')
    harm = {"dano": f"1d{die(L)}+{w}", "nota": "Hand of Harm (1 ki, 1× por turno num golpe desarmado)"}
    n = 1 if L < 5 else 2
    cura = {"nome": "Hand of Healing (troca um golpe do Flurry)", "lado": "def", "modelo": "cura_na_luta", "alcance": "toque",
            "acao": "bonus", "usos_luta": 1, "pv": die(L) / 2 + 0.5 + w}
    if L < 11:   # Flurry em 2 rounds (2 ki) + Hand of Harm em 2 acertos (2 ki); um golpe do Flurry vira Hand of Healing
        dano = {"ataques": [U(n, b, d, L), U(1.25, b, d, L, nota="ação bônus (Flurry em 2 rounds, um golpe vira cura)")],
                "por_luta": [dict(harm, usos=2)]}
        usos_p, gasto, hip = 2, 4, 'Flurry em 2 rounds + Hand of Harm em 2 acertos + 1 Hand of Healing (4 ki)'
    else:        # Flurry of Healing and Harm: Hand of Harm sem ki 1× por turno quando usa o Flurry
        dano = {"ataques": [U(n, b, d, L), U(1.75, b, d, L, nota="ação bônus (Flurry todo round, um golpe vira cura)")],
                "por_turno": [harm]}
        usos_p, gasto, hip = 4, 4, 'Flurry todo round com Hand of Harm grátis + 1 Hand of Healing (4 ki)'
    fontes = []
    if L >= 7:
        fontes = [{"tipo": "condicao_no_acerto", "nome": "Physician's Touch (envenenado, sem save)", "efeito": "cond_envenenado_um_turno",
                   "cd": 99, "bonus": [b] * (n + 1), "usos": usos_p}]
    ls.append(linha('mao-da-morte', hip, dano, {}, saves=ss, controle=ctrl('striker', fontes), gasta={"ki": gasto}, suporte=[cura]))
    for l in ls: l['saves'] = {}
    txt = {3: "Hand of Healing e Hand of Harm; chicote como arma dedicada (dado de Martial Arts, alcance).",
           5: "Extra Attack, Stunning Strike; Slasher (Des 18, 4); Martial Arts d6.",
           7: "Physician's Touch (6: envenenado no Hand of Harm); Evasion, Stillness of Mind.",
           9: "Des 20 (8).", 11: "Flurry of Healing and Harm; Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=rec(L), linhas=ls)


escrever('rpgbot-monk-mercy', 'way-of-mercy', 'Mercy Monk (RPGBot: Stuck Halfway)',
         'Monk (Mercy), meio-elfo da floresta, chicote como arma dedicada; Slasher 4, Des 20 8, Sab 18 12',
         {"resumo": "Monge da Misericórdia: Hand of Harm para dano necrótico e veneno sem save, Hand of Healing para levantar aliados.",
          "estrategia": "Ataca com o chicote, gasta ki em Flurry com Hand of Harm; troca um golpe do Flurry por cura quando alguém cai.",
          "nao_modelado": "Alcance do chicote e Slasher; remoção de condições (Physician's Touch na cura); cura fora de luta com o ki que sobra; Deflect Missiles; Hand of Ultimate Mercy (17); vantagem do atordoado para os aliados."},
         {L: mercy(L) for L in NIV})

# ---------------------------------------------------------------- Long Death (Vulture)
def longd(L):
    dx, ws = 16, 16; cn = {3: 16, 5: 18, 7: 18, 9: 20, 11: 20}[L]; d, w, c, P = mod(dx), mod(ws), mod(cn), pb(L)
    m = M(-1, d, c, -1, w, -1); bd, bc = P + d, P + c
    ss = ss_monk(L, m, humanoide=True)
    defesa = {"golpes_extras_a_0pv": 1} if L >= 11 else {}
    if L < 5:
        ls = base_monk(L, 'tank', '1d8', bd, d, bd, d, w, defesa=defesa, sufixo=' (lança)')
    else:   # morde com Constituição (arma de monge com o dado de Martial Arts) na ação; golpes desarmados de Destreza
        ls = base_monk(L, 'tank', f'1d{die(L)}', bc, c, bd, d, w, defesa=defesa, sufixo=' (mordida de Dhampir com Con)')
    if L >= 7:
        ls.append(linha('ceifa', 'Hour of Reaping na ação todo round (amedronta em 30 pés) + golpe desarmado na ação bônus',
                        {"ataques": [U(1, bd, d, L, nota="ação bônus (Martial Arts)")]}, defesa,
                        controle=ctrl('tank', [{"tipo": "area", "nome": "Hour of Reaping", "magia": "hour_of_reaping",
                                                "cd": 8 + P + w, "so_grupos": True}])))
    txt = {3: "Touch of Death (PV temporários ao derrubar: não modelado); lança.", 5: "Extra Attack, Stunning Strike; Con 18 (4): morde com Con.",
           7: "Hour of Reaping (6); Evasion, Stillness of Mind.", 9: "Con 20 (8).", 11: "Mastery of Death (1 ki: fica com 1 PV); Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=rec(L), linhas=ls)


escrever('rpgbot-monk-long-death', 'way-of-the-long-death', 'Long Death Monk (RPGBot: Vulture)',
         'Monk (Long Death), Dhampir (base Aarakocra), lança e depois mordida de Con; Con 18 4, Con 20 8, Piercer 12',
         {"resumo": "Monge da Morte Longa: tanque que vive de PV temporários ao derrubar inimigos e amedronta multidões de graça.",
          "estrategia": "Segura os inimigos no corpo a corpo; Hour of Reaping contra grupos; Mastery of Death a partir do 11.",
          "nao_modelado": "Touch of Death (PV temporários ao derrubar, inclusive o 'saco de ratos'); vantagem da mordida abaixo da metade da vida (condição de julgamento); cura da mordida; voo do Aarakocra e Spider Climb; Touch of the Long Death (17)."},
         {L: longd(L) for L in NIV})

# ---------------------------------------------------------------- Open Hand (The Launch Pad)
def openh(L):
    dx = {3: 16, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn, ws = 16, 16; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(-1, d, 3, -1, w, -1); b = P + d; n = 1 if L < 5 else 2
    ss = ss_monk(L, m)
    ls = base_monk(L, 'striker', '1d8', b, d, b, d, w, sufixo=' (bordão com as duas mãos)')
    cd = 8 + P + w
    def oht(k):
        return {"tipo": "condicao_no_acerto", "nome": "Open Hand Technique (derruba/arremessa no Flurry)", "efeito": "cond_derrubado",
                "cd": cd, "bonus": [b, b], "usos": k}
    for l in ls:
        kfl = {"meia-rajada": 4, "rajada": 8, "atordoar": 4}.get(l['id'])
        if kfl: l['controle']['fontes'].insert(0, oht(kfl))
        k = n + {"principal": 1, "meia-rajada": 1.5, "rajada": 2, "atordoar": 1.5}[l['id']]
        pc = round(1 - 0.95 ** k, 3)
        l['suporte'] = {"fontes": [{"nome": "Crusher (crítico: vantagem de todos contra o alvo)", "lado": "of", "modelo": "vantagem",
                                    "alvos": 3, "fracao": pc}]}
    txt = {3: "Open Hand Technique; Crusher (Variant Human).", 5: "Extra Attack, Stunning Strike; Des 18 (4).",
           7: "Wholeness of Body (6); Evasion, Stillness of Mind.", 9: "Des 20 (8).", 11: "Tranquility; Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=rec(L), linhas=ls)


escrever('rpgbot-monk-open-hand', 'open-hand', 'Open Hand Monk (RPGBot: The Launch Pad)',
         'Monk (Open Hand), Variant Human (Crusher), bordão; Des 18 4, Des 20 8, Sab 18 12',
         {"resumo": "Monge da Mão Aberta: o Flurry derruba e arremessa inimigos; Crusher empurra e dá vantagem à party no crítico.",
          "estrategia": "Flurry nos alvos com Força/Destreza fracas para derrubar e lançar ao alto; Stunning Strike nos que têm Con fraca.",
          "nao_modelado": "Dano de queda e reposicionamento (Crusher + Open Hand Technique para o alto); empurrão do Crusher; Wholeness of Body; Tranquility; Quivering Palm (17); vantagem do atordoado para os aliados."},
         {L: openh(L) for L in NIV})

# ---------------------------------------------------------------- Astral Self (Yes, This IS A Jojo's Reference)
def astral(L):
    dx, cn = 16, 16; ws = {3: 16, 5: 18, 7: 18, 9: 19, 11: 19}[L]; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(-1, d, 3, -1, w, -1); bd, bw = P + d, P + w; n = 1 if L < 5 else 2; cd = 8 + P + w
    ss = ss_monk(L, m)
    ls = base_monk(L, 'striker', '1d8', bd, d, bd, d, w, sufixo=' (lança, sem os braços astrais)')
    corpo11 = L >= 11
    extra = {"por_turno": [{"dano": f"1d{die(L)}", "nota": "Empowered Arms (Body of the Astral Self)"}]} if corpo11 else {}
    k0 = 2 if corpo11 else 1   # braços (+ visage a partir do 11, para o Body)
    def bra(kba, gasta_extra, hip, ctrl_extra=()):
        dano = {"ataques": [U(n, bw, w, L, nota="braços astrais (Sab, alcance 10)"),
                            U(kba, bw, w, L, nota="ação bônus (rounds 2–4: o 1º round invoca os braços)")],
                "com_save": [{"n": 0.25, "cd": cd, "save": "Des", "dano": f"2d{die(L)}", "meio": False,
                              "nota": "invocação dos braços (1× por luta)"}], **extra}
        area = [{"nome": "Arms of the Astral Self (invocação)", "tipo": "explosao",
                 "usos": [{"alvos": 2, "dano": f"2d{die(L)}", "cd": cd, "save": "Des", "metade": False}]}]
        return linha('bracos' + gasta_extra[0], hip, dano, {}, controle=ctrl('striker', ctrl_extra), area=area,
                     gasta={"ki": k0 + gasta_extra[1]})
    ls.append(bra(0.75, ('', 0), f'Arms of the Astral Self ({k0} ki, 10 minutos = 1 luta): ataques de Sab com alcance; Martial Arts nos rounds 2–4'))
    ls.append(bra(1.5, ('-rajada', 3), f'braços astrais + Flurry nos rounds 2–4 ({k0 + 3} ki)'))
    if L >= 5:
        ls.append(bra(1.25, ('-atordoar', 2), f'braços astrais + Flurry em 1 round + 1 Stunning Strike ({k0 + 2} ki)',
                      [stun(L, bw, w, n + 1, usos=1)]))
    txt = {3: "Arms of the Astral Self (ataques de Sab, alcance 10, dano de força).", 5: "Extra Attack, Stunning Strike; Sab 18 (4).",
           7: "Visage of the Astral Self (6); Evasion, Stillness of Mind.", 9: "Skill Expert (Sab 19, expertise em Atletismo, 8).",
           11: "Body of the Astral Self (Empowered Arms, Deflect Energy); Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=rec(L), linhas=ls)


escrever('rpgbot-monk-astral-self', 'astral-self', "Astral Self Monk (RPGBot: Yes, This IS A Jojo's Reference)",
         'Monk (Astral Self), Dhampir, lança e braços astrais de Sabedoria; Sab 18 4, Skill Expert 8, Observant 12',
         {"resumo": "Monge do Eu Astral: braços espectrais que batem com Sabedoria, com alcance, e sobem a CD do Stunning Strike.",
          "estrategia": "Invoca os braços no começo da luta (dano em área ao redor) e luta com Sabedoria; Flurry e Stunning Strike com o ki que sobra.",
          "nao_modelado": "Agarrão e empurrão com Sabedoria (Atletismo com expertise: o combo agarrar+derrubar custa ataques); Visage (visão no escuro mágico, Intimidação); Deflect Energy (11, reação); duração de 10 minutos cobrindo duas lutas seguidas; Awakened Astral Self (17)."},
         {L: astral(L) for L in NIV})

# ---------------------------------------------------------------- Shadow (Shadow Boxer)
def shadow(L):
    dx = {3: 16, 5: 16, 7: 16, 9: 18, 11: 18}[L]; cn, ws = 15, 16; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(-1, d, 2, -1, w, -1); b = P + d; n = 1 if L < 5 else 2
    ss = ss_monk(L, m)
    sent = L >= 5
    fontes = [{"tipo": "sentinela", "nome": "Sentinel", "bonus": b}] if sent else []
    ls = base_monk(L, 'tank' if sent else 'striker', '1d8', b, d, b, d, w, extra_ctrl=fontes, sufixo=' (lança)')
    oa = [A(0.5, b, '1d8', d, nota="ataque de oportunidade (Sentinel), reação em 50% dos rounds")] if sent else []
    for l in ls:
        if sent: l['dano']['ataques'] += oa; l['reacao'] = [{"uso": "ataque de oportunidade (Sentinel)", "fracao": 0.5, "eixos": ["dano", "controle"]}]
    def esc(k, gasta, hip, extra_ctrl=()):
        at = [A(n, b, '1d8', d, vantagem=1.0), U(k, b, d, L, vantagem=1.0, nota="ação bônus")] + \
             ([dict(oa[0], vantagem=1.0)] if sent else [])
        l = linha('escuridao' + gasta[0], hip, {"ataques": at}, {"adv": -1},
                  controle=ctrl('tank' if sent else 'striker', list(extra_ctrl) + fontes), gasta={"ki": 2 + gasta[1]})
        if sent: l['reacao'] = [{"uso": "ataque de oportunidade (Sentinel)", "fracao": 0.5, "eixos": ["dano", "controle"]}]
        return l
    ls.append(esc(1, ('', 0), 'Darkness (2 ki, concentração, 10 minutos = 1 luta) + Devil\'s Sight: vantagem nos ataques, desvantagem contra ele'))
    ls.append(esc(1.5, ('-rajada', 2), 'Darkness + Flurry em 2 rounds (4 ki)'))
    txt = {3: "Shadow Arts (Darkness com 2 ki); Devil's Sight (Eldritch Adept, Variant Human).", 5: "Extra Attack, Stunning Strike; Sentinel (4).",
           7: "Shadow Step (6); Evasion, Stillness of Mind.", 9: "Des 18 (8).", 11: "Cloak of Shadows; Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=rec(L), linhas=ls)


escrever('rpgbot-monk-shadow', 'shadow', 'Shadow Monk (RPGBot: Shadow Boxer)',
         "Monk (Shadow), Variant Human (Eldritch Adept: Devil's Sight), lança; Sentinel 4, Des 18 8, Des 20 12",
         {"resumo": "Monge da Sombra: lança Darkness e enxerga dentro dela com Devil's Sight; Sentinel segura quem tenta sair.",
          "estrategia": "Darkness em volta de si nas lutas, ataques com vantagem e inimigos com desvantagem; Sentinel prende na bola de escuridão.",
          "nao_modelado": "A Darkness também atrapalha os aliados (e bloqueia magias com alvo que exige ver, dos dois lados); Pass Without Trace, Silence, Minor Illusion; Shadow Step (6) e Cloak of Shadows (11); Opportunist (17)."},
         {L: shadow(L) for L in NIV})

# ---------------------------------------------------------------- Drunken Master (The Reveler)
def drunk(L):
    dx = {3: 16, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn, ws = 16, 16; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(-1, d, 3, -1, w, -1); b = P + d
    ss = ss_monk(L, m, adv_mental_magia=True, humanoide=False)
    ls = base_monk(L, 'striker', '1d8', b, d, b, d, w, sufixo=' (lança; Flurry com Disengage grátis)')
    txt = {3: "Drunken Technique (Flurry + Disengage).", 5: "Extra Attack, Stunning Strike; Des 18 (4).",
           7: "Tipsy Sway (6: Redirect Attack); Evasion, Stillness of Mind.", 9: "Des 20 (8).", 11: "Drunkard's Luck; Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=rec(L), linhas=ls)


escrever('rpgbot-monk-drunken-master', 'drunken-master', 'Drunken Master Monk (RPGBot: The Reveler)',
         'Monk (Drunken Master), Satyr, lança; Des 18 4, Des 20 8, Crusher 12',
         {"resumo": "Monge Bêbado: bate e foge, com Flurry e Disengage pelo mesmo ki.",
          "estrategia": "Entra, gasta ki em Flurry e sai sem levar ataque de oportunidade.",
          "nao_modelado": "Disengage e deslocamento do Drunken Technique (mobilidade); Redirect Attack (reação: desvia um ataque que errou para outro inimigo); Leap to Your Feet; Drunkard's Luck; Intoxicated Frenzy (17). Magic Resistance do Satyr aproximada por vantagem em saves mentais contra magia."},
         {L: drunk(L) for L in NIV})

# ---------------------------------------------------------------- Four Elements (Destroyer of Cabbages)
def four(L):
    dx = {3: 16, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn, ws = 16, 16; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(-1, d, 3, -1, w, -1); b = P + d; n = 1 if L < 5 else 2; cd = 8 + P + w
    ss = ss_monk(L, m)
    ls = base_monk(L, 'striker', '1d8', b, d, b, d, w, sufixo=' (lança)')
    def disc(id_, hip, ki, area=None, com_save=None, fontes=()):
        dano = {"ataques": [A(n * 0.75, b, '1d8', d, nota="ação nos rounds 2–4"),
                            U(1, b, d, L, nota="ação bônus (Martial Arts / Ki-Fueled Attack no round da disciplina)")]}
        if com_save: dano['com_save'] = [com_save]
        return linha(id_, hip, dano, {}, controle=ctrl('striker', fontes), area=area, gasta={"ki": ki})
    ls.append(disc('punho', 'Fist of Unbroken Air no 1º round (2 ki): 3d10, empurra e derruba', 2,
                   com_save={"n": 0.25, "cd": cd, "save": "For", "dano": "3d10", "meio": True, "nota": "Fist of Unbroken Air (1× por luta)"},
                   fontes=[{"tipo": "condicao_no_acerto", "nome": "Fist of Unbroken Air (derrubado)", "efeito": "cond_derrubado",
                            "cd": cd, "usos": 1, "no_acerto": False}]))
    if 7 <= L < 11:
        ls.append(disc('gongo', 'Gong of the Summit (Shatter, 3 ki) no 1º round', 3,
                       area=[{"nome": "Gong of the Summit", "tipo": "explosao",
                              "usos": [{"alvos": 2, "dano": "3d8", "cd": cd, "save": "Con", "metade": True}]}],
                       com_save={"n": 0.25, "cd": cd, "save": "Con", "dano": "3d8", "meio": True, "nota": "Gong of the Summit"}))
    if L >= 11:
        ls.append(disc('fenix', 'Flames of the Phoenix (Fireball, 4 ki) no 1º round', 4,
                       area=[{"nome": "Flames of the Phoenix", "tipo": "explosao",
                              "usos": [{"alvos": 4, "dano": "8d6", "cd": cd, "save": "Des", "metade": True}]}],
                       com_save={"n": 0.25, "cd": cd, "save": "Des", "dano": "8d6", "meio": True, "nota": "Flames of the Phoenix"}))
    txt = {3: "Fist of Unbroken Air; Ki-Fueled Attack.", 5: "Extra Attack, Stunning Strike; Des 18 (4).",
           7: "Gong of the Summit (6); Evasion, Stillness of Mind.", 9: "Des 20 (8).",
           11: "Flames of the Phoenix; Gong trocado por Ride the Wind; Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=rec(L), linhas=ls)


escrever('rpgbot-monk-four-elements', 'four-elements', 'Four Elements Monk (RPGBot: Destroyer of Cabbages)',
         'Monk (Four Elements), goblin, lança; Des 18 4, Des 20 8, Sab 18 12; todas as opcionais de classe',
         {"resumo": "Monge dos Quatro Elementos: disciplinas que gastam muito ki para empurrar, derrubar e, no 11, soltar Fireball.",
          "estrategia": "Fist of Unbroken Air para reposicionar e derrubar; área com Gong of the Summit e, depois, Flames of the Phoenix.",
          "nao_modelado": "Upcast das disciplinas com ki extra; empurrão de 20 pés; Ride the Wind (voo); Fury of the Small e Nimble Escape do goblin; Elemental Attunement."},
         {L: four(L) for L in NIV}, fonte={"tipo": "rpgbot", "url": "https://rpgbot.net/dnd5/characters/classes/monk/four-elements/", "nota": NOTA})

# ---------------------------------------------------------------- Kensei (Why don't you just shoot it?) — Fighter 1 / Monk
def kensei(L):
    mk = L - 1; dx = 16 if L < 9 else 18; cn, ws = 14, 16; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(0, d, 2, -1, w, -1); b = P + d + 2   # Archery
    n = 1 if mk < 5 else 2
    profs = ('for', 'con')
    ss = dict(sv=sv(L, m, profs))
    if mk >= 7: ss.update(evasion=True, stillness=True)
    pw = {"poder": [-5, 10]} if L >= 5 else {}
    dado = f'1d{max(6, die(mk))}'
    at = [A(n, b, dado, d, **pw), A(1, b, dado, d, nota="Crossbow Expert (ação bônus)", **pw)]
    ls = [linha('principal', 'besta de mão com Crossbow Expert' + (' e Sharpshooter' if pw else '') + ', sem ki',
                {"ataques": at}, {}, papel='atirador')]
    if mk >= 6:
        ls.append(linha('deft', f'+ Deft Strike (1 ki por acerto: +1d{die(mk)}) com o ki da luta ({mk // 2} ki)',
                        {"ataques": at, "por_luta": [{"dano": f"1d{die(mk)}", "usos": mk // 2, "nota": "Deft Strike"}]}, {},
                        papel='atirador', gasta={"ki": mk // 2}))
    rec_ = {"espacos": {}, "outros": {"ki": {"qtd": mk if mk >= 2 else 0, "volta": "curto"}}}
    txt = {3: "Fighter 1 (Archery) / Monk 2: besta de mão com Crossbow Expert (Variant Human).",
           5: "Monk 4: Way of the Kensei (3), Sharpshooter (4).", 7: "Monk 6: Extra Attack, One with the Blade (Deft Strike).",
           9: "Monk 8: Des 18; Evasion, Stillness of Mind.", 11: "Monk 10: Purity of Body."}[L]
    return dict(_texto=txt, corpo=dict(ca=10 + d + w, pv=hp([10] + [8] * mk, mod(cn)), saves=ss), recursos=rec_, linhas=ls)


escrever('rpgbot-monk-kensei', 'kensei', "Kensei Monk (RPGBot: Why don't you just shoot it?)",
         'Fighter 1 (Archery) / Monk (Kensei), Variant Human (Crossbow Expert), besta de mão; Sharpshooter no Monk 4, Des 18 no Monk 8',
         {"resumo": "Kensei atirador: besta de mão com Crossbow Expert e Sharpshooter, Archery do Fighter 1.",
          "estrategia": "Atira de longe com ação e ação bônus; Deft Strike com o ki; Sharpen the Blade só a partir do Monk 11 (nível 12).",
          "nao_modelado": "Agile Parry e Kensei's Shot (competem com o Crossbow Expert); Deflect Missiles devolvido com Archery; Second Wind; Sharpen the Blade (nível 12); Action Surge (nível 20)."},
         {L: kensei(L) for L in NIV})

# ---------------------------------------------------------------- Sun Soul (The Prince of All Hadozee)
def sun(L):
    dx = {3: 16, 5: 17, 7: 17, 9: 18, 11: 18}[L]; cn, ws = 16, 16; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(-1, d, 3, -1, w, -1); b = P + d; n = 1 if L < 5 else 2; cd = 8 + P + w
    ss = ss_monk(L, m)
    ls = base_monk(L, 'striker', '1d8', b, d, b, d, w, sufixo=' (lança, corpo a corpo)')
    def raio(k, nm):
        return A(k, b, f'1d{die(L)}', d, nota=nm)
    ls.append(linha('raios', 'Radiant Sun Bolt na ação (30 pés), sem ki', {"ataques": [raio(n, "Radiant Sun Bolt")]}, {}, papel='atirador'))
    ls.append(linha('raios-rajada', 'Radiant Sun Bolt + dois raios na ação bônus todo round (4 ki)',
                    {"ataques": [raio(n, "Radiant Sun Bolt"), raio(2, "raios na ação bônus (1 ki)")]}, {}, papel='atirador', gasta={"ki": 4}))
    if L >= 7:
        ls.append(linha('arco', 'Searing Arc Strike (Burning Hands na ação bônus, 2 ki) no 1º round, raios na ação',
                        {"ataques": [raio(n, "Radiant Sun Bolt"), raio(1, "raios na ação bônus (rounds 2–4: 1,5 ki em média)")],
                         "com_save": [{"n": 0.25, "cd": cd, "save": "Des", "dano": "3d6", "meio": True, "nota": "Searing Arc Strike"}]},
                        {}, papel='atirador', gasta={"ki": 4},
                        area=[{"nome": "Searing Arc Strike", "tipo": "explosao",
                               "usos": [{"alvos": 2, "dano": "3d6", "cd": cd, "save": "Des", "metade": True}]}]))
    if L >= 11:
        ls.append(linha('sunburst', 'Searing Sunburst na ação (grátis, 20 pés de raio, Con anula) + raios na ação bônus nos rounds em que sobra ki',
                        {"ataques": [], "com_save": [{"n": 1, "cd": cd, "save": "Con", "dano": "2d6", "meio": False, "nota": "Searing Sunburst"}]},
                        {}, papel='atirador',
                        area=[{"nome": "Searing Sunburst (grátis)", "tipo": "cleave_save", "dano": "2d6", "cd": cd, "save": "Con",
                               "alvos": [3, 4, 4], "metade": False}]))
    txt = {3: "Radiant Sun Bolt (ataque de magia a distância).", 5: "Extra Attack, Stunning Strike; Gunner (Des 17, 4).",
           7: "Searing Arc Strike (6); Evasion, Stillness of Mind.", 9: "Skill Expert (Des 18, 8).", 11: "Searing Sunburst; Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=rec(L), linhas=ls)


escrever('rpgbot-monk-sun-soul', 'sun-soul', 'Sun Soul Monk (RPGBot: The Prince of All Hadozee)',
         'Monk (Sun Soul), Hadozee, raios radiantes; Gunner 4, Skill Expert 8, Des 20 12',
         {"resumo": "Monge da Alma Solar: raios radiantes a 30 pés, Burning Hands na ação bônus e uma explosão grátis no 11.",
          "estrategia": "Fica atrás e dispara Radiant Sun Bolt; gasta ki nos raios da ação bônus; Searing Sunburst contra grupos no 11.",
          "nao_modelado": "Hadozee Resilience (reação: reduz dano, PB/dia); planar; mosquete com Gunner e Ki-Fueled Attack; upcast do Searing Sunburst com ki; Sun Shield (17)."},
         {L: sun(L) for L in NIV})

# ---------------------------------------------------------------- Ascendant Dragon (Double Dragon)
def drag(L):
    dx = {3: 17, 5: 19, 7: 19, 9: 20, 11: 20}[L]; cn = 14; ws = 16 if L < 9 else 17; d, w, c, P = mod(dx), mod(ws), mod(cn), pb(L)
    m = M(-1, d, c, -1, w, 0); b = P + d; n = 1 if L < 5 else 2; cd = 8 + P + w; cdr = 8 + P + c
    ss = ss_monk(L, m)
    ls = base_monk(L, 'striker', '1d8', b, d, b, d, w, sufixo=' (lança)')
    dn_monk = f'2d{die(L)}' if L < 11 else f'3d{die(L)}'
    dn_rac = '1d10' if L < 5 else '2d10' if L < 11 else '3d10'
    usos = [{"alvos": 2, "dano": dn_monk, "cd": cd, "save": "Des", "metade": True}]
    gasta = {"sopro": 1}
    hip = 'Breath of the Dragon (cone de 20 pés) no lugar de um ataque do 1º round'
    if L >= 5:
        usos.append({"alvos": 2, "dano": dn_rac, "cd": cdr, "save": "Des", "metade": True})
        gasta["sopro_racial"] = 1; hip += ' + o sopro do Dragonborn no outro ataque'
    nb = len(usos)
    dano = {"ataques": [A(n - 0.25 * nb, b, '1d8', d), U(1, b, d, L, nota="ação bônus")],
            "com_save": [{"n": 0.25, "cd": u['cd'], "save": "Des", "dano": u['dano'], "meio": True, "nota": "sopro no alvo principal"} for u in usos]}
    ls.append(linha('sopro', hip, dano, {}, area=[{"nome": "Breath of the Dragon" + (" + sopro racial" if nb > 1 else ""),
                                                   "tipo": "explosao", "usos": usos}], gasta=gasta))
    out = rec(L, sopro={"qtd": P, "volta": "longo"})
    if L >= 5: out['outros']['sopro_racial'] = {"qtd": P, "volta": "longo"}
    if L >= 11:
        ls.append(linha('aspecto', 'Aspect of the Wyrm (Frightful Presence: amedronta 1 criatura a 10 pés por round na ação bônus)',
                        {"ataques": [A(n, b, '1d8', d)]}, {},
                        controle=ctrl('striker', [{"tipo": "condicao_no_acerto", "nome": "Frightful Presence", "efeito": "cond_amedrontado",
                                                   "cd": cd, "usos": 4, "no_acerto": False}]), gasta={"aspecto": 1}))
        out['outros']['aspecto'] = {"qtd": 1, "volta": "longo"}
    txt = {3: "Breath of the Dragon (PB/dia); Draconic Disciple.", 5: "Extra Attack, Stunning Strike; Des 19 (4): os dois sopros no mesmo turno.",
           7: "Wings Unfurled (6); Evasion, Stillness of Mind.", 9: "Des 20, Sab 17 (8).", 11: "Aspect of the Wyrm; sopro 3 dados; Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=corpo_m(L, dx, cn, ws, m, ss), recursos=out, linhas=ls)


escrever('rpgbot-monk-ascendant-dragon', 'ascendant-dragon', 'Ascendant Dragon Monk (RPGBot: Double Dragon)',
         "Monk (Ascendant Dragon), Dragonborn (Fizban's), lança; Des 19 4, Des 20/Sab 17 8, Gift of the Gem Dragon 12",
         {"resumo": "Monge do Dragão Ascendente: sopros em cone contra grupos, o do monge e o do Dragonborn no mesmo turno.",
          "estrategia": "Posiciona para pegar 2–3 inimigos no cone e sopra os dois; no 11, Frightful Presence na ação bônus.",
          "nao_modelado": "Sopros com ki depois dos usos diários; Wings Unfurled (voo curto, sopro de cima); resistência do Aspect of the Wyrm para os aliados; Draconic Strike; voo e resistência do Dragonborn."},
         {L: drag(L) for L in NIV},
         fonte={"tipo": "rpgbot", "url": "https://rpgbot.net/dnd5/characters/classes/monk/subclasses/ascendant-dragon/",
                "nota": NOTA + " O Doc no Drive tem a URL da versão 2024, mas o conteúdo é o do guia 2014 (Fizban's)."})
