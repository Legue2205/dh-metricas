"""Barbarian (passada 1, 21/11): as 8 builds do RPGBot + Berserker (sem build no RPGBot; RAW e homebrew da mesa).
Rodar da raiz: python ferramentas/geradores/bar.py && python -m dh expandir progressoes/rpgbot-barbarian-*.json
Convenções: calibracao/convencoes-passada1.md (seção Barbarian)."""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import marcial
from marcial import *
marcial.CLASSE = 'barbarian'

DS = {"adv": ["Des"]}          # Danger Sense (Barbarian 2)
RES = {"resist": True}
OA = [{"uso": "ataque de oportunidade", "fracao": 0.5, "eixos": ["dano", "controle"]}]

# ---------------------------------------------------------------- Beast (Wrathful Leaps)
def beast(L):
    st = {3: 17, 5: 18, 7: 18, 9: 20, 11: 20}[L]; s = mod(st); con = 16; P = pb(L)
    m = M(s, 2, 3, -1, 0, -1); b = P + s; n = 1 if L < 5 else 2; bc = 1 if L >= 9 else 0
    ca = 18 if L < 5 else 19
    ss = dict(sv=sv(L, m), ataques=n + 1, adv_mental_magia=True, humanoide=False, **DS)
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}}}
    sem = linha('principal', 'sem fúria: martelo de guerra com escudo, Reckless Attack',
                {"ataques": [A(n, b, '1d8', s, bc=bc, vantagem=1.0)]}, {"adv": 1}, papel='tank')
    gar = {"ataques": [A(n + 1, b, '1d6', s + rdano(L), bc=bc, vantagem=1.0)]}
    if L >= 11:
        gar['com_save'] = [{"n": 0.25, "cd": 8 + P + mod(con), "save": "Sab", "dano": "2d12", "meio": False,
                            "nota": "Infectious Fury (PB/dia ÷ 4 lutas, 1 por luta)"}]
    fur = linha('furia-garras', 'fúria com Form of the Beast (garras: um ataque extra na ação), Reckless Attack',
                gar, {"adv": 1, **RES}, papel='tank', gasta={"furia": 1})
    txt = {3: "Form of the Beast; For 17; escama + escudo (18).", 5: "Extra Attack (3 ataques de garra); Skill Expert (For 18); meia-armadura + escudo (19).",
           7: "Bestial Soul, Feral Instinct.", 9: "For 20 (8); Brutal Critical; fúria +3.", 11: "Infectious Fury (10); Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=ca, pv=hp([12] * L, 3), saves=ss), recursos=rec, linhas=[sem, fur])


escrever('rpgbot-barbarian-beast', 'beast', 'Beast Barbarian (RPGBot: Wrathful Leaps)',
         'Barbarian (Beast), Satyr, garras + escudo; Skill Expert 4 (For 18), For 20 8, Con 18 12',
         {"resumo": "Bárbaro da Fera com escudo: na fúria ataca com garras (um ataque extra na ação) sem largar o escudo.",
          "estrategia": "Fúria em toda luta com garras e Reckless Attack; Infectious Fury a partir do 10.",
          "nao_modelado": "Form of the Beast (mordida: cura; cauda: +1d8 de CA por reação) — só as garras; saltos e agarrão (Skill Expert); Bestial Soul; força ataque de Infectious Fury; Relentless Rage; Danger Sense entra nos saves; Magic Resistance do Satyr aproximada por vantagem em saves mentais contra magia; Feral Instinct."},
         {L: beast(L) for L in NIV})

# ---------------------------------------------------------------- Ancestral Guardian (Furious About Mediocre Strength)
def ag(L):
    # nível de personagem → (Bb, Wz, Fi): 1-4 Bb, 5 W1, 6-7 Bb5-6, 8 W2, 9-10 Bb7-8, 11 F1
    bb, wz, fi = {3: (3, 0, 0), 5: (4, 1, 0), 7: (6, 1, 0), 9: (7, 2, 0), 11: (8, 2, 1)}[L]
    dx = {3: 16, 5: 17, 7: 17, 9: 17, 11: 19}[L]; d = mod(dx); P = pb(L)
    m = M(1, d, 3, 1, -1, -1); b = P + d; n = 2 if bb >= 5 else 1
    duel = 2 if fi else 0; ca = 10 + d + 3 + 2
    pv = hp([12] * bb + [6] * wz + [10] * fi, 3)
    ss = dict(sv=sv(L, m), ataques=n, **DS)
    ataques = []
    if wz:   # Find Familiar (coruja) usa Help: vantagem no 1º ataque do turno, com Elven Accuracy
        ataques.append(A(1, b, '1d8', d + duel, vantagem=1.0, elven_accuracy=True, nota="1º ataque com Help do familiar"))
        if n > 1: ataques.append(A(n - 1, b, '1d8', d + duel))
    else:
        ataques.append(A(n, b, '1d8', d + duel))
    dano = {"ataques": ataques}
    sem = linha('principal', 'sem fúria: rapieira e escudo, sem Reckless Attack (ataque de Destreza)', dano, {}, papel='tank')
    fontes = [{"tipo": "ancestral_protectors", "nome": "Ancestral Protectors", "bonus": b}]
    sup = None; reac = None
    if bb >= 6:
        sup = [{"nome": "Spirit Shield (reação: −2d6 no dano de um aliado)", "lado": "def", "modelo": "cura",
                "usos_luta": 2, "pv": 7}]
        reac = [{"uso": "Spirit Shield", "fracao": 0.5, "eixos": ["suporte"]}]
    fur = linha('furia', 'fúria em toda luta: Ancestral Protectors no 1º alvo atingido (a fúria não soma dano: ataque de Destreza)',
                dano, RES, controle=ctrl('tank', fontes), gasta={"furia": 1}, suporte=sup, reacao=reac)
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(bb), "volta": "longo"}}}
    txt = {3: "Barbarian 3: Ancestral Protectors; Unarmored Defense com escudo (18).",
           5: "Barbarian 4 (Elven Accuracy, Des 17) / Wizard 1: Find Familiar (Help no 1º ataque).",
           7: "Barbarian 6 / Wizard 1: Extra Attack, Spirit Shield 2d6.",
           9: "Barbarian 7 / Wizard 2: Arcane Deflection, Feral Instinct.",
           11: "Barbarian 8 (Des 19) / Wizard 2 / Fighter 1: Dueling."}[L]
    return dict(_texto=txt, corpo=dict(ca=ca, pv=pv, saves=ss), recursos=rec, linhas=[sem, fur])


escrever('rpgbot-barbarian-ancestral-guardian', 'ancestral-guardian',
         'Ancestral Guardian Barbarian (RPGBot: Furious About Mediocre Strength)',
         'Barbarian 8 / Wizard 2 / Fighter 1 (nível de personagem 11), Shadar-Kai, rapieira + escudo de Destreza; Elven Accuracy 4, Wizard 1 no 5, Wizard 2 no 8, Fighter 1 no 11',
         {"resumo": "Guardião Ancestral defensor de Destreza: rapieira e escudo, marca o alvo com Ancestral Protectors e protege aliados com Spirit Shield.",
          "estrategia": "Fúria em toda luta, acerta a maior ameaça para marcá-la; reação em Spirit Shield; o familiar dá vantagem no 1º ataque.",
          "nao_modelado": "Arcane Deflection (compete com Spirit Shield pela reação); Consult the Spirits; Second Wind; teleporte do Shadar-Kai; Booming Blade; Arcane Recovery e rituais; Relentless Rage; Feral Instinct."},
         {L: ag(L) for L in NIV})

# ---------------------------------------------------------------- Battlerager (The Drop Hawk, versão anão)
def br(L):
    st = 17 if L < 5 else 18; cn = 17 if L < 9 else 19; s, c = mod(st), mod(cn); P = pb(L)
    m = M(s, 2, c, -1, 0, -1); b = P + s; n = 1 if L < 5 else 2; bc = 1 if L >= 9 else 0
    ss = dict(sv=sv(L, m), ataques=n + 1, **DS)
    sem = linha('principal', 'sem fúria: martelo e escudo, Reckless Attack (espinhos só na fúria)',
                {"ataques": [A(n, b, '1d8', s, bc=bc, vantagem=1.0)]}, {"adv": 1}, papel='tank')
    gr = s + 2 * P if L >= 5 else s + P   # Skill Expert (Atletismo) no 4
    fur = linha('furia-agarrao', 'fúria: agarra com o 1º ataque do 1º round (3 de dano no agarrão, ÷ 4 rounds), bate com a arma e com os espinhos (ação bônus) com Reckless Attack',
                {"ataques": [A(n - 0.25, b, '1d8', s + rdano(L), bc=bc, vantagem=1.0),
                             A(0.75, b, '1d4', s + rdano(L), bc=bc, vantagem=1.0, nota="espinhos (ação bônus; o 1º round vai na fúria)")],
                 "automatico": "0.75"},
                {"adv": 1, **RES}, controle=ctrl('tank', [{"tipo": "agarrao", "nome": "Agarrão (Atletismo com vantagem na fúria)", "bonus": gr}]),
                gasta={"furia": 1})
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}}}
    txt = {3: "Battlerager Armor (espinhos, CA 16 + escudo = 18).", 5: "Extra Attack; Skill Expert (For 18, expertise em Atletismo).",
           7: "Reckless Abandon (PV temporários, não modelados); Feral Instinct.", 9: "Con 19 (8); Brutal Critical; fúria +3.",
           11: "Battlerager Charge (10); Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=18, pv=hp([12] * L, c), saves=ss), recursos=rec, linhas=[sem, fur])


escrever('rpgbot-barbarian-battlerager', 'battlerager', 'Battlerager Barbarian (RPGBot: The Drop Hawk)',
         'Barbarian (Battlerager), anão da montanha, armadura de espinhos + escudo; Skill Expert 4 (For 18), Con 19 8, Mobile 12',
         {"resumo": "Bárbaro agarrador de armadura de espinhos: agarra, bate com a arma e com os espinhos como ação bônus.",
          "estrategia": "Fúria em toda luta, agarra a ameaça principal e mantém o agarrão (Atletismo com expertise e vantagem).",
          "nao_modelado": "Reckless Abandon (PV temporários próprios, como Second Wind); vantagem de Força no teste de agarrão (o motor usa só o bônus); derrubar após agarrar (combo agarrar+empurrar custa ataque); versão Owlin voadora (soltar do alto); Battlerager Charge; Spiked Retribution (14); resistência a veneno do anão; Relentless Rage."},
         {L: br(L) for L in NIV})

# ---------------------------------------------------------------- Giant (Stature-esque)
def giant(L):
    st = {3: 16, 5: 17, 7: 17, 9: 18, 11: 18}[L]; s = mod(st); P = pb(L)
    m = M(s, 2, 2, 1, -1, 0); b = P + s; n = 1 if L < 5 else 2; bc = 1 if L >= 9 else 0
    ca = 16 if L < 5 else 17
    ss = dict(sv=sv(L, m), ataques=n, **DS)
    cloud = [{"dano": "1d4", "usos_dia": P, "nota": "Strike of the Giants (Cloud): +1d4 trovão, PB/dia"}]
    sem = linha('principal', 'sem fúria: machado grande, Reckless Attack',
                {"ataques": [A(n, b, '1d12', s, bc=bc, vantagem=1.0)], "por_luta": cloud},
                {"adv": 1})
    ele = '+1d6' if L >= 7 else ''
    dano = {"ataques": [A(n, b, '1d12', s + rdano(L), ele, bc=bc, vantagem=1.0)], "por_luta": cloud}
    fontes = []
    if L >= 11:
        dano['com_save'] = [{"n": 0.75, "cd": 8 + P + s, "save": "For", "dano": "3d6", "meio": False,
                             "nota": "Mighty Impel (ação bônus, rounds 2–4): arremessa 30 pés para o alto (queda)"}]
        fontes = [{"tipo": "condicao_no_acerto", "nome": "Mighty Impel (derrubado pela queda)", "efeito": "cond_derrubado",
                   "cd": 8 + P + s, "usos": 3, "no_acerto": False}]
    fur = linha('furia', 'fúria (Giant Stature, alcance +5)' + (', Elemental Cleaver +1d6' if ele else '') +
                (', Mighty Impel na ação bônus' if L >= 11 else '') + ', Reckless Attack',
                dano, {"adv": 1, **RES}, controle=ctrl('striker', fontes), gasta={"furia": 1})
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}}}
    txt = {3: "Giant's Havoc (Giant Stature: Grande, alcance +5); Strike of the Giants (Cloud) do Variant Human.",
           5: "Extra Attack; Guile of the Cloud Giant (For 17); meia-armadura.", 7: "Elemental Cleaver (6); Feral Instinct.",
           9: "Skill Expert (For 18, 8); Brutal Critical; fúria +3.", 11: "Mighty Impel (10); Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=ca, pv=hp([12] * L, 2), saves=ss), recursos=rec, linhas=[sem, fur])


escrever('rpgbot-barbarian-giant', 'path-of-the-giant', 'Giant Barbarian (RPGBot: Stature-esque)',
         'Barbarian (Giant), Variant Human (Strike of the Giants: Cloud), machado grande, armadura média; Guile of the Cloud Giant 4, Skill Expert 8, For 20 12',
         {"resumo": "Bárbaro Gigante: cresce na fúria, ganha dano elemental e arma que volta quando arremessada; a partir do 10 arremessa inimigos.",
          "estrategia": "Fúria em toda luta com Reckless Attack; Mighty Impel na ação bônus para derrubar pela queda.",
          "nao_modelado": "Arremesso à distância com Elemental Cleaver (o motor mede só corpo a corpo; vale como mobilidade); invisibilidade do Cloud Strike; teleporte do Guile; agarrão a 10 pés (Skill Expert); Giant's Power; Crushing Throw; Relentless Rage; Feral Instinct. Guile of the Cloud Giant (resistência por reação, PB/dia; na fúria é quase redundante)."},
         {L: giant(L) for L in NIV}, fonte=None)

# ---------------------------------------------------------------- Storm Herald (Fireball Me in the Face, Desert)
def storm(L):
    st = {3: 17, 5: 18, 7: 18, 9: 18, 11: 18}[L]; s = mod(st); dx = 16 if L >= 9 else 15; P = pb(L)
    m = M(s, mod(dx), 2, -1, 1, -1); b = P + s; n = 1 if L < 5 else 2; bc = 1 if L >= 9 else 0
    ca = 16 if L < 5 else 17
    profs = ('for', 'con', 'des') if L >= 9 else ('for', 'con')
    ss = dict(sv=sv(L, m, profs), ataques=n, **DS)
    aura = 2 if L < 5 else 3 if L < 10 else 4
    sem = linha('principal', 'sem fúria: glaive, Reckless Attack', {"ataques": [A(n, b, '1d10', s, bc=bc, vantagem=1.0)]}, {"adv": 1})
    fur = linha('furia-deserto', f'fúria com Storm Aura (Desert): {aura} de fogo automático em quem escolher a 10 pés, todo turno (ação bônus)',
                {"ataques": [A(n, b, '1d10', s + rdano(L), bc=bc, vantagem=1.0)], "automatico": str(aura)},
                {"adv": 1, **RES}, gasta={"furia": 1},
                area=[{"nome": f"Storm Aura (Desert) no 2º alvo", "tipo": "cleave_ataque", "bonus": 99, "dano": str(aura), "p": [1, 1, 1]},
                      {"nome": f"Storm Aura (Desert) no 3º alvo", "tipo": "cleave_ataque", "bonus": 99, "dano": str(aura), "p": [1, 1, 1]}])
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}}}
    txt = {3: "Storm Aura (Desert, 2 de fogo).", 5: "Extra Attack; Slasher (For 18); aura 3; meia-armadura.",
           7: "Storm Soul (resistência a fogo, 6); Feral Instinct.", 9: "Resilient Des (16, 8); Brutal Critical; fúria +3.",
           11: "Shielding Storm (10); aura 4; Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=ca, pv=hp([12] * L, 2), saves=ss), recursos=rec, linhas=[sem, fur])


escrever('rpgbot-barbarian-storm-herald', 'storm-herald', 'Storm Herald Barbarian (RPGBot: Fireball Me in the Face)',
         'Barbarian (Storm Herald, Desert), Dragonborn cromático, glaive, armadura média; Slasher 4, Resilient Des 8, For 20 12',
         {"resumo": "Arauto da Tempestade do deserto: aura de fogo automático em volta e resistência a fogo para os aliados lançarem área em cima dele.",
          "estrategia": "Mergulha no meio dos inimigos, liga a aura todo turno e pede Fireball em cima de si.",
          "nao_modelado": "Slasher (redução de deslocamento e debuff no crítico); Storm Soul e Shielding Storm (resistência a fogo: a sinergia com o blaster aliado não é medida); sopro do Dragonborn; Raging Storm (14); Relentless Rage; Feral Instinct. A aura entra como dano automático no alvo principal e, na Área, como dois acertos garantidos em mais dois alvos por round (cleave_ataque com bônus 99)."},
         {L: storm(L) for L in NIV})

# ---------------------------------------------------------------- Totem Warrior (What is Nature's Call?, Wolf)
def totem(L):
    st = {3: 16, 5: 16, 7: 16, 9: 18, 11: 18}[L]; s = mod(st); P = pb(L)
    m = M(s, 3, 2, -1, -1, -1); b = P + s; n = 1 if L < 5 else 2; bc = 1 if L >= 9 else 0
    ss = dict(sv=sv(L, m), ataques=n + (1 if L >= 5 else 0), **DS)
    pam = L >= 5
    def at(r):
        x = [A(n, b, '1d10', s + r, bc=bc, vantagem=1.0)]
        if pam:
            x += [A(0.75, b, '1d4', s + r, vantagem=1.0, nota="Polearm Master (ação bônus; 1º round na fúria)"),
                  A(0.5, b, '1d10', s + r, bc=bc, nota="ataque de oportunidade do Polearm Master, reação em 50% dos rounds")]
        return {"ataques": x}
    sem = linha('principal', 'sem fúria: alabarda' + (' com Polearm Master' if pam else '') + ', Reckless Attack', at(0),
                {"adv": 1}, reacao=OA if pam else None)
    if pam: sem['dano']['ataques'][1]['n'] = 1.0
    fur = linha('furia-lobo', 'fúria com Totem Spirit (Wolf): aliados com vantagem corpo a corpo contra quem está a 5 pés dele',
                at(rdano(L)), {"adv": 1, **RES}, gasta={"furia": 1}, reacao=OA if pam else None,
                suporte=[{"nome": "Totem Spirit (Wolf)", "lado": "of", "modelo": "vantagem", "alvos": 1, "fracao": 0.5}])
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}}}
    txt = {3: "Totem Spirit (Wolf); Unarmored Defense (15).", 5: "Extra Attack; Polearm Master (4).", 7: "Aspect of the Beast (Eagle); Feral Instinct.",
           9: "For 18 (8); Brutal Critical; fúria +3.", 11: "Spirit Walker (10); Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=15, pv=hp([12] * L, 2), saves=ss), recursos=rec, linhas=[sem, fur])


escrever('rpgbot-barbarian-totem-warrior', 'totem-warrior', "Totem Warrior Barbarian (RPGBot: What is Nature's Call?)",
         'Barbarian (Totem Warrior: Wolf), Eladrin, alabarda, Unarmored Defense; Polearm Master 4, For 18 8, For 20 12',
         {"resumo": "Guerreiro Totêmico do Lobo: dá vantagem aos aliados corpo a corpo e bate com Polearm Master.",
          "estrategia": "Fúria em toda luta colado nos inimigos que os aliados atacam; Polearm Master na ação bônus e na reação.",
          "nao_modelado": "Fey Step do Eladrin (teleporte de aliado); totem do Urso (alternativa defensiva citada pelo guia); Aspect of the Beast; Totemic Attunement (14); Relentless Rage; Feral Instinct. Totem do Lobo: 1 aliado corpo a corpo da party de referência, em metade das lutas/ataques junto dele (fração 0,5: julgamento a calibrar)."},
         {L: totem(L) for L in NIV})

# ---------------------------------------------------------------- Zealot (Starbarian)
def zealot(L):
    st = {3: 17, 5: 17, 7: 17, 9: 18, 11: 18}[L]; s = mod(st); P = pb(L)
    m = M(s, 2, 3, -1, 0, -1); b = P + s; n = 1 if L < 5 else 2; bc = 1 if L >= 9 else 0
    ca = 15 if L < 5 else 17
    ss = dict(sv=sv(L, m), ataques=n, **DS)
    pw = {"poder": [-5, 10]} if L >= 5 else {}
    sem = linha('principal', 'sem fúria: machado grande' + (' com GWM' if pw else '') + ', Reckless Attack',
                {"ataques": [A(n, b, '1d12', s, bc=bc, vantagem=1.0, **pw)]}, {"adv": 1})
    df = {"dano": f"1d6+{L // 2}", "nota": "Divine Fury (1º acerto do turno na fúria)"}
    sfur = dict(ss, rerolagens=1) if L >= 7 else None
    sup = [{"nome": "Zealous Presence (1/dia: vantagem para a party por um round)", "lado": "of", "modelo": "vantagem",
            "alvos": 3, "fracao": 0.0625}] if L >= 11 else None
    fur = linha('furia', 'fúria com Divine Fury' + (' e GWM' if pw else '') + ', Reckless Attack',
                {"ataques": [A(n, b, '1d12', s + rdano(L), bc=bc, vantagem=1.0, **pw)], "por_turno": [df]},
                {"adv": 1, **RES}, saves=({"rerolagens": 1} if L >= 7 else None), gasta={"furia": 1}, suporte=sup)
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}}}
    txt = {3: "Divine Fury (1d6+1), Warrior of the Gods; Unarmored Defense (15).", 5: "Extra Attack; Great Weapon Master (4); meia-armadura (17).",
           7: "Fanatical Focus (6: refaz um save falho por fúria); Feral Instinct.", 9: "Slasher (For 18, 8); Brutal Critical; fúria +3.",
           11: "Zealous Presence (10); Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=ca, pv=hp([12] * L, 3), saves=ss), recursos=rec, linhas=[sem, fur])


escrever('rpgbot-barbarian-zealot', 'zealot', 'Zealot Barbarian (RPGBot: Starbarian)',
         'Barbarian (Zealot), Astral Elf, machado grande, Unarmored Defense e depois meia-armadura; GWM 4, Slasher 8, For 20 12',
         {"resumo": "Zelote: dano radiante extra no 1º acerto de cada turno na fúria e quase impossível de tirar da luta.",
          "estrategia": "Fúria em toda luta com Reckless Attack e GWM; Zealous Presence uma vez por dia.",
          "nao_modelado": "Warrior of the Gods (ressurreição sem componente); Slasher; Starlight Step; Rage Beyond Death (14); Relentless Rage; Feral Instinct. Fanatical Focus = 1 rerolagem de save por luta, só na fúria."},
         {L: zealot(L) for L in NIV})

# ---------------------------------------------------------------- Wild Magic ("Did he just slap me with a giant spork?")
def wild(L):
    st = {3: 17, 5: 18, 7: 18, 9: 18, 11: 18}[L]; s = mod(st); P = pb(L)
    m = M(s, 2, 3, -1, 0, -1); b = P + s; n = 1 if L < 5 else 2; bc = 1 if L >= 9 else 0
    ca = 15 if L < 5 else 16
    ss = dict(sv=sv(L, m), ataques=n, **DS)
    pw = {"poder": [-5, 10]} if L >= 9 else {}
    sem = linha('principal', 'sem fúria: malho' + (' com GWM' if pw else '') + ', Reckless Attack',
                {"ataques": [A(n, b, '2d6', s, bc=bc, vantagem=1.0, **pw)]}, {"adv": 1})
    pc = round(1 - (1 - 0.0975) ** n, 3)   # Crusher: chance de ≥ 1 crítico no turno com vantagem
    crush = [{"nome": "Crusher (crítico: vantagem de todos contra o alvo)", "lado": "of", "modelo": "vantagem",
              "alvos": 3, "fracao": pc}] if L >= 5 else None
    def fdano(bonus_extra):
        return {"ataques": [A(n, b + bonus_extra, '2d6', s + rdano(L), '+0.44', bc=bc, vantagem=1.0, **pw)],
                "com_save": [{"n": 0.094, "cd": 8 + P + 3, "save": "Con", "dano": "1d6", "meio": False,
                              "nota": "Wild Surge 8 (raio de luz na ação bônus, rounds 2–4, 1/8 das fúrias)"}]}
    fur = linha('furia', 'fúria com Wild Surge (valor esperado das opções de dano 4 e 8), Reckless Attack', fdano(0),
                {"adv": 1, **RES}, gasta={"furia": 1}, suporte=crush)
    ls = [sem, fur]
    out = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}}}
    if L >= 7:
        ls.append(linha('furia-bolstering', 'fúria + Bolstering Magic em si (+1d3 nos ataques por 10 minutos)', fdano(2),
                        {"adv": 1, **RES}, gasta={"furia": 1, "bolstering": 1}, suporte=crush))
        out['outros']['bolstering'] = {"qtd": P, "volta": "longo"}
    txt = {3: "Wild Surge, Magic Awareness; camisão de malha (15).", 5: "Extra Attack; Crusher (For 18, 4); peitoral (16).",
           7: "Bolstering Magic (6, PB/dia); Feral Instinct.", 9: "Great Weapon Master (8); Brutal Critical; fúria +3.",
           11: "Unstable Backlash (10); Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=ca, pv=hp([12] * L, 3), saves=ss), recursos=out, linhas=ls)


escrever('rpgbot-barbarian-wild-magic', 'path-of-wild-magic', 'Wild Magic Barbarian (RPGBot: "Did he just slap me with a giant spork?")',
         'Barbarian (Wild Magic), Tiefling alado, malho, armadura média; Crusher 4, GWM 8, For 20 12',
         {"resumo": "Bárbaro da Magia Selvagem: um efeito aleatório a cada fúria e Bolstering Magic para acertar mais.",
          "estrategia": "Fúria em toda luta com Reckless Attack; Crusher dá vantagem à party no crítico; Bolstering Magic nas lutas importantes.",
          "nao_modelado": "Wild Surge: só o valor esperado das opções 4 (+1d6 de força por acerto, 1/8) e 8 (raio de 1d6 na ação bônus, 1/8); as outras (explosão necrótica, teleporte, espírito explosivo, retaliação, +1 CA aos aliados, terreno difícil) e a cegueira da 8 não; empurrão do Crusher; voo do Tiefling e agarrar-e-soltar; restaurar espaços de aliados com Bolstering Magic; Unstable Backlash e Controlled Surge; Relentless Rage; Feral Instinct."},
         {L: wild(L) for L in NIV})

# ---------------------------------------------------------------- Berserker (sem build no RPGBot: chassi padrão do Handbook)
def bers(L, homebrew):
    st = {3: 17, 5: 17, 7: 17, 9: 18, 11: 18}[L]; cn = 16 if L < 9 else 17; s, c = mod(st), mod(cn); P = pb(L)
    m = M(s, 2, c, -1, 0, -1); b = P + s; n = 1 if L < 5 else 2; bc = 1 + (1 if L >= 9 else 0)   # Savage Attacks + Brutal
    ca = 16 if L < 5 else 17
    ss = dict(sv=sv(L, m), ataques=n + 1, **DS)
    pw = {"poder": [-5, 10]} if L >= 5 else {}
    sem = linha('principal', 'sem fúria: machado grande' + (' com GWM' if pw else '') + ', Reckless Attack',
                {"ataques": [A(n, b, '1d12', s, bc=bc, vantagem=1.0, **pw)]}, {"adv": 1})
    smr = {"imune": ["encanto", "medo"]} if L >= 7 else None
    r = rdano(L)
    fur = linha('furia', 'fúria sem Frenzy, Reckless Attack', {"ataques": [A(n, b, '1d12', s + r, bc=bc, vantagem=1.0, **pw)]},
                {"adv": 1, **RES}, saves=smr, gasta={"furia": 1})
    fre = linha('furia-frenesi', 'fúria com Frenzy: ataque extra na ação bônus dos rounds 2–4 (exaustão no fim)',
                {"ataques": [A(n, b, '1d12', s + r, bc=bc, vantagem=1.0, **pw),
                             A(0.75, b, '1d12', s + r, bc=bc, vantagem=1.0, nota="Frenzy (ação bônus)", **pw)]},
                {"adv": 1, **RES}, saves=smr, gasta={"furia": 1, "frenesi": 1}, plano='prioritaria')
    fq = {"qtd": 2, "volta": "curto"} if homebrew else {"qtd": 1, "volta": "longo"}
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}, "frenesi": fq}}
    txt = {3: "Frenzy; meia-orc (Savage Attacks); escama (16).", 5: "Extra Attack; GWM (4); meia-armadura (17).",
           7: "Mindless Rage (6: imune a encantado e amedrontado na fúria); Feral Instinct.", 9: "For 18, Con 17 (8); Brutal Critical; fúria +3.",
           11: "Intimidating Presence (10); Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=ca, pv=hp([12] * L, c), saves=ss), recursos=rec, linhas=[sem, fur, fre])


BD = 'Barbarian (Berserker), meia-orc, machado grande, armadura média; GWM 4, For 18/Con 17 8, For 20 12 (chassi do Barbarian Handbook; o RPGBot não tem build de Berserker)'
DESC_B = lambda hb: {"resumo": "Berserker com machado grande e Frenzy (ataque extra na ação bônus).",
                     "estrategia": ("Homebrew da mesa: a exaustão do Frenzy sai no descanso curto, então frenesi em toda fúria (2 por metade do dia; só exaustão 1 numa luta)."
                                    if hb else "RAW: a exaustão só sai no descanso longo; um frenesi por dia, na luta prioritária."),
                     "nao_modelado": "Exaustão (nível 1: desvantagem em testes; o plano limita o frenesi); Intimidating Presence (Car 8); Retaliation (14); Relentless Rage; Feral Instinct."}
escrever('rpgbot-barbarian-berserker', 'berserker', 'Berserker Barbarian (sem build do RPGBot; RAW)', BD, DESC_B(False),
         {L: bers(L, False) for L in NIV},
         fonte={"tipo": "rpgbot", "url": "https://rpgbot.net/dnd5/characters/classes/barbarian/subclasses/berserker/",
                "nota": "O RPGBot não tem build de Berserker (exaustão punitiva demais). Build montada por nós no chassi do Handbook, RAW."})
escrever('rpgbot-barbarian-berserker-homebrew', 'berserker', 'Berserker Barbarian (homebrew: exaustão sai no descanso curto)', BD, DESC_B(True),
         {L: bers(L, True) for L in NIV}, grupo="Homebrew",
         fonte={"tipo": "homebrew", "url": "https://rpgbot.net/dnd5/characters/classes/barbarian/subclasses/berserker/",
                "nota": "Mesma build do Berserker RAW, com a homebrew da mesa DragonHeist: a exaustão do Frenzy sai no descanso curto."})
