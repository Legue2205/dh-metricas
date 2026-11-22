"""Chassi do Barbarian (mini-mutirão 22/11): 8 caminhos do gabarito, sem feat e com o feat da subclasse. Fatias 7 e 11.
Rodar da raiz: python ferramentas/geradores/chassi_barbarian.py && python -m dh expandir
Régua comum: For principal, Con secundário (compra padrão: For 17, Con 15, Des 13); meia-armadura (CA 16, 18 com
escudo; Battlerager: armadura de espinhos 14+Des); Reckless Attack em todas as linhas; fúria = linhas `furia*`
com `gasta` furia 1; Danger Sense nos saves; Brutal Critical no 9. Features de subclasse = as de bar.py.
"""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402
from marcial import A, linha, furias, rdano  # noqa: E402

ORDEM = ('for', 'con', 'des', 'sab', 'car', 'int')
DS = {"adv": ["Des"]}
RES = {"resist": True}
URL = "https://rpgbot.net/dnd5/characters/classes/barbarian/subclasses/{}/"
NM = "Relentless Rage; Feral Instinct; Fast Movement; Primal Path 14 (fora das fatias)."


def base(L, feat, meio=None):
    s = C.atributos('barbarian', L, ORDEM, feat=feat, meio_feat=meio); m = C.mods(s); P = C.pb(L)
    return s, m, P, m['for'] + P, (1 if L < 5 else 2), (1 if L >= 9 else 0)


def ctl(pos, fontes=()):
    return {"atencao": C.atencao(pos), "fontes": list(fontes) + [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}


def corpo(L, m, ca, n_ataques, **extra):
    return dict(ca=ca, pv=C.hp(12, L, m['con']), saves=dict(sv=C.sv(L, m, ('for', 'con')), ataques=n_ataques, **DS), **extra)


def rec(L, **outros):
    return {"espacos": {}, "outros": dict(furia={"qtd": furias(L), "volta": "longo"}, **outros)}


def gw(feat):   # Great Weapon Master
    return {"poder": [-5, 10]} if feat == 'Great Weapon Master' else {}


# ------------------------------------------------------------------ Ancestral Guardian: defensor, espada longa + escudo
def ag(L, feat):
    s, m, P, b, n, bc = base(L, feat); pos = 'defensor'; r = rdano(L)
    sent = feat == 'Sentinel'
    def ats(rr, oa):
        x = [A(n, b, '1d8', m['for'] + rr, bc=bc, vantagem=1.0)]
        if sent: x.append(A(oa, b, '1d8', m['for'] + rr, bc=bc, nota=f"ataque de oportunidade (Sentinel), reação em {oa:.0%} dos rounds"))
        return {"ataques": x}
    fs = [{"tipo": "sentinela", "nome": "Sentinel", "bonus": b}] if sent else []
    c0 = ctl(pos, fs)
    if sent: c0['atencao']['hard'] = {"sentinela": b}
    sem = linha('principal', 'sem fúria: espada longa e escudo, Reckless Attack' + (', Sentinel' if sent else ''),
                ats(0, 0.5), {"adv": 1}, controle=c0,
                reacao=[{"uso": "ataque de oportunidade (Sentinel)", "fracao": 0.5, "eixos": ["dano", "controle"]}] if sent else None)
    ss = 7 if L < 10 else 10.5
    sup = [{"nome": f"Spirit Shield (reação: −{2 if L < 10 else 3}d6 no dano de um aliado)", "lado": "def", "modelo": "cura",
            "usos_luta": 2, "pv": ss}]
    reac = [{"uso": "Spirit Shield", "fracao": 0.5, "eixos": ["suporte"]}]
    if sent: reac.append({"uso": "ataque de oportunidade (Sentinel)", "fracao": 0.25, "eixos": ["dano", "controle"]})
    c1 = ctl(pos, [{"tipo": "ancestral_protectors", "nome": "Ancestral Protectors", "bonus": b}] + fs)
    if sent: c1['atencao']['hard'] = {"sentinela": b}
    fur = linha('furia', 'fúria em toda luta: Ancestral Protectors no 1º alvo atingido, Spirit Shield na reação, Reckless Attack',
                ats(r, 0.25), {"adv": 1, **RES}, controle=c1, gasta={"furia": 1}, suporte=sup, reacao=reac)
    return dict(corpo=corpo(L, m, 18, n), recursos=rec(L), linhas=[sem, fur], _texto=f"atributos {s}; meia-armadura + escudo (18)")


# ------------------------------------------------------------------ Battlerager: defensor agarrador, espinhos + escudo
def br(L, feat):
    meio = 'for' if feat else None
    s, m, P, b, n, bc = base(L, feat, meio); pos = 'defensor'; r = rdano(L); c = m['con']
    sem = linha('principal', 'sem fúria: martelo de guerra e escudo, Reckless Attack (espinhos só na fúria)',
                {"ataques": [A(n, b, '1d8', m['for'], bc=bc, vantagem=1.0)]}, {"adv": 1}, controle=ctl(pos))
    gr = m['for'] + (2 * P if feat == 'Skill Expert' else P)
    fur = linha('furia-agarrao', 'fúria: agarra com o 1º ataque do 1º round (3 de espinhos no agarrão, ÷ 4 rounds), arma + espinhos (ação bônus), Reckless Attack',
                {"ataques": [A(n - 0.25, b, '1d8', m['for'] + r, bc=bc, vantagem=1.0),
                             A(0.75, b, '1d4', m['for'] + r, bc=bc, vantagem=1.0, nota="espinhos (ação bônus; o 1º round vai na fúria)")],
                 "automatico": "0.75"},
                {"adv": 1, **RES, "pvt_round": c},
                controle=ctl(pos, [{"tipo": "agarrao", "nome": "Agarrão (Atletismo" + (" com expertise" if feat else "") + ")", "bonus": gr}]),
                gasta={"furia": 1})
    ca = 14 + min(2, m['des']) + 2
    return dict(corpo=corpo(L, m, ca, n + 1, pvt_round=c), recursos=rec(L), linhas=[sem, fur],
                _texto=f"atributos {s}; armadura de espinhos + escudo ({ca}); Reckless Abandon (Con em PV temporários)")


# ------------------------------------------------------------------ Beast: defensor, garras + escudo
def beast(L, feat):
    meio = 'for' if feat else None
    s, m, P, b, n, bc = base(L, feat, meio); pos = 'defensor'; r = rdano(L); f = m['for']
    sem = linha('principal', 'sem fúria: martelo de guerra com escudo, Reckless Attack',
                {"ataques": [A(n, b, '1d8', f, bc=bc, vantagem=1.0)]}, {"adv": 1}, controle=ctl(pos))
    gar = {"ataques": [A(n + 1, b, '1d6', f + r, bc=bc, vantagem=1.0)]}
    if L >= 10:
        gar['com_save'] = [{"n": 0.25, "cd": 8 + P + m['con'], "save": "Sab", "dano": "2d12", "meio": False,
                            "nota": "Infectious Fury (PB/dia ÷ 4 lutas, 1 por luta)"}]
    fur = linha('furia-garras', 'fúria com Form of the Beast (garras: um ataque extra na ação), Reckless Attack',
                gar, {"adv": 1, **RES}, controle=ctl(pos), gasta={"furia": 1})
    cau = linha('furia-cauda', 'fúria com Form of the Beast (cauda: alcance, reação +1d8 de CA contra um ataque), Reckless Attack',
                {"ataques": [A(n, b, '1d8', f + r, bc=bc, vantagem=1.0)]},
                {"adv": 1, **RES, "reacoes": [{"tipo": "bloqueio", "dado": 8}]}, controle=ctl(pos), gasta={"furia": 1})
    return dict(corpo=corpo(L, m, 18, n + 1),
                recursos=rec(L), linhas=[sem, fur, cau], _texto=f"atributos {s}; meia-armadura + escudo (18)")


# ------------------------------------------------------------------ Berserker (RAW): striker, machado grande
def bers(L, feat):
    s, m, P, b, n, bc = base(L, feat); pos = 'striker'; r = rdano(L); f = m['for']; pw = gw(feat)
    sem = linha('principal', 'sem fúria: machado grande, Reckless Attack' + (', GWM' if pw else ''),
                {"ataques": [A(n, b, '1d12', f, bc=bc, vantagem=1.0, **pw)]}, {"adv": 1}, controle=ctl(pos))
    smr = {"imune": ["encanto", "medo"]} if L >= 6 else None
    fur = linha('furia', 'fúria sem Frenzy, Reckless Attack', {"ataques": [A(n, b, '1d12', f + r, bc=bc, vantagem=1.0, **pw)]},
                {"adv": 1, **RES}, saves=smr, controle=ctl(pos), gasta={"furia": 1})
    fre = linha('furia-frenesi', 'fúria com Frenzy: ataque extra na ação bônus dos rounds 2–4 (exaustão no fim)',
                {"ataques": [A(n, b, '1d12', f + r, bc=bc, vantagem=1.0, **pw),
                             A(0.75, b, '1d12', f + r, bc=bc, vantagem=1.0, nota="Frenzy (ação bônus)", **pw)]},
                {"adv": 1, **RES}, saves=smr, controle=ctl(pos), gasta={"furia": 1, "frenesi": 1}, plano='prioritaria')
    return dict(corpo=corpo(L, m, 16, n), recursos=rec(L, frenesi={"qtd": 1, "volta": "longo"}), linhas=[sem, fur, fre],
                _texto=f"atributos {s}; meia-armadura (16)")


# ------------------------------------------------------------------ Storm Herald (Desert): striker, glaive
def storm(L, feat):
    meio = 'for' if feat else None
    s, m, P, b, n, bc = base(L, feat, meio); pos = 'striker'; r = rdano(L); f = m['for']
    aura = 3 if L < 10 else 4
    sem = linha('principal', 'sem fúria: glaive, Reckless Attack', {"ataques": [A(n, b, '1d10', f, bc=bc, vantagem=1.0)]},
                {"adv": 1}, controle=ctl(pos))
    fur = linha('furia-deserto', f'fúria com Storm Aura (Desert): {aura} de fogo automático em quem escolher a 10 pés (ação bônus)',
                {"ataques": [A(n, b, '1d10', f + r, bc=bc, vantagem=1.0)], "automatico": str(aura)},
                {"adv": 1, **RES}, controle=ctl(pos), gasta={"furia": 1},
                area=[{"nome": f"Storm Aura (Desert) no {k}º alvo", "tipo": "cleave_ataque", "bonus": 99, "dano": str(aura),
                       "p": [1, 1, 1]} for k in (2, 3)])
    return dict(corpo=corpo(L, m, 16, n), recursos=rec(L), linhas=[sem, fur], _texto=f"atributos {s}; meia-armadura (16)")


# ------------------------------------------------------------------ Totem Warrior (Urso): defensor, alabarda
def totem(L, feat):
    s, m, P, b, n, bc = base(L, feat); pos = 'defensor'; r = rdano(L); f = m['for']
    pam = feat == 'Polearm Master'
    OA = [{"uso": "ataque de oportunidade (Polearm Master)", "fracao": 0.5, "eixos": ["dano", "controle"]}] if pam else None
    def at(rr, bonus_n):
        x = [A(n, b, '1d10', f + rr, bc=bc, vantagem=1.0)]
        if pam:
            x += [A(bonus_n, b, '1d4', f + rr, vantagem=1.0, nota="Polearm Master (ação bônus)"),
                  A(0.5, b, '1d10', f + rr, bc=bc, nota="ataque de oportunidade do Polearm Master, reação em 50% dos rounds")]
        return {"ataques": x}
    sem = linha('principal', 'sem fúria: alabarda' + (' com Polearm Master' if pam else '') + ', Reckless Attack', at(0, 1.0),
                {"adv": 1}, controle=ctl(pos), reacao=OA)
    res = ["fogo", "frio", "eletrico", "trovao", "acido", "radiante", "necrotico", "forca", "veneno"]
    fur = linha('furia-urso', 'fúria com Totem Spirit (Bear): resistência a tudo menos psíquico', at(r, 0.75),
                {"adv": 1, **RES}, saves={"res": res}, controle=ctl(pos), gasta={"furia": 1}, reacao=OA)
    return dict(corpo=corpo(L, m, 16, n + (1 if pam else 0)), recursos=rec(L), linhas=[sem, fur],
                _texto=f"atributos {s}; meia-armadura (16), alabarda (sem escudo)")


# ------------------------------------------------------------------ Wild Magic: striker, malho
def wild(L, feat):
    meio = 'for' if feat else None
    s, m, P, b, n, bc = base(L, feat, meio); pos = 'striker'; r = rdano(L); f = m['for']
    sem = linha('principal', 'sem fúria: malho, Reckless Attack', {"ataques": [A(n, b, '2d6', f, bc=bc, vantagem=1.0)]},
                {"adv": 1}, controle=ctl(pos))
    pc = round(1 - (1 - 0.0975) ** n, 3)
    crush = [{"nome": "Crusher (crítico: vantagem de todos contra o alvo)", "lado": "of", "modelo": "vantagem",
              "alvos": 3, "fracao": pc}] if feat == 'Crusher' else None
    def fd(bx):
        return {"ataques": [A(n, b + bx, '2d6', f + r, '+0.44', bc=bc, vantagem=1.0)],
                "com_save": [{"n": 0.094, "cd": 8 + P + m['con'], "save": "Con", "dano": "1d6", "meio": False,
                              "nota": "Wild Surge 8 (raio de luz na ação bônus, rounds 2–4, 1/8 das fúrias)"}]}
    fur = linha('furia', 'fúria com Wild Surge (valor esperado das opções de dano 4 e 8), Reckless Attack', fd(0),
                {"adv": 1, **RES}, controle=ctl(pos), gasta={"furia": 1}, suporte=crush)
    bol = linha('furia-bolstering', 'fúria + Bolstering Magic em si (+1d3 nos ataques por 10 minutos)', fd(2),
                {"adv": 1, **RES}, controle=ctl(pos), gasta={"furia": 1, "bolstering": 1}, suporte=crush)
    return dict(corpo=corpo(L, m, 16, n), recursos=rec(L, bolstering={"qtd": P, "volta": "longo"}), linhas=[sem, fur, bol],
                _texto=f"atributos {s}; meia-armadura (16)")


# ------------------------------------------------------------------ Zealot: striker, machado grande
def zealot(L, feat):
    s, m, P, b, n, bc = base(L, feat); pos = 'striker'; r = rdano(L); f = m['for']; pw = gw(feat)
    sem = linha('principal', 'sem fúria: machado grande' + (' com GWM' if pw else '') + ', Reckless Attack',
                {"ataques": [A(n, b, '1d12', f, bc=bc, vantagem=1.0, **pw)]}, {"adv": 1}, controle=ctl(pos))
    df = {"dano": f"1d6+{L // 2}", "nota": "Divine Fury (1º acerto do turno na fúria)"}
    sup = [{"nome": "Zealous Presence (1/dia: vantagem para a party por um round)", "lado": "of", "modelo": "vantagem",
            "alvos": 3, "fracao": 0.0625}] if L >= 10 else None
    fur = linha('furia', 'fúria com Divine Fury' + (' e GWM' if pw else '') + ', Reckless Attack',
                {"ataques": [A(n, b, '1d12', f + r, bc=bc, vantagem=1.0, **pw)], "por_turno": [df]},
                {"adv": 1, **RES}, saves={"rerolagens": 1}, controle=ctl(pos), gasta={"furia": 1}, suporte=sup)
    return dict(corpo=corpo(L, m, 16, n), recursos=rec(L), linhas=[sem, fur], _texto=f"atributos {s}; meia-armadura (16)")


# ------------------------------------------------------------------ tabela: sub → (função, posição, build, feats, resumo, não modelado)
SUBS = {
    'ancestral-guardian': (ag, 'defensor', 'espada longa + escudo, meia-armadura', ['Sentinel'],
        "Guardião Ancestral defensor: marca o alvo com Ancestral Protectors e protege aliados com Spirit Shield.",
        "Consult the Spirits (10). Feat: a build do RPGBot só tem Elven Accuracy (racial) até o 11, então o feat é o natural de defensor, Sentinel."),
    'battlerager': (br, 'defensor', 'martelo de guerra + escudo, armadura de espinhos', ['Skill Expert'],
        "Battlerager agarrador: arma, espinhos na ação bônus e agarrão na fúria.",
        "Vantagem de Força no agarrão (o motor usa só o bônus); derrubar após agarrar; Battlerager Charge (10); Skill Expert: a perícia extra."),
    'beast': (beast, 'defensor', 'martelo de guerra + escudo; garras na fúria, meia-armadura', ['Skill Expert'],
        "Bárbaro da Fera com escudo: na fúria ataca com garras (um ataque extra na ação).",
        "Mordida (cura); Bestial Soul (6); força o ataque de Infectious Fury; Skill Expert: expertise em Atletismo e a perícia (sem agarrão modelado: só o +1 de For conta)."),
    'berserker': (bers, 'striker', 'machado grande, meia-armadura', ['Great Weapon Master'],
        "Berserker RAW com machado grande e um Frenzy por dia (exaustão só sai no descanso longo).",
        "Exaustão (o plano limita o frenesi a 1/dia); Intimidating Presence (10). Feat: sem build no RPGBot; GWM, o natural de machado grande (o mesmo do nosso Berserker)."),
    'storm-herald': (storm, 'striker', 'glaive, meia-armadura', ['Slasher'],
        "Arauto da Tempestade do deserto: aura de fogo automático em volta.",
        "Storm Soul e Shielding Storm (resistência a fogo); Slasher (redução de deslocamento e debuff no crítico: só o +1 de For conta)."),
    'totem-warrior': (totem, 'defensor', 'alabarda, meia-armadura', ['Polearm Master'],
        "Guerreiro Totêmico do Urso (resistência a tudo menos psíquico na fúria), defensor de alabarda.",
        "Totem do Lobo (o RPGBot usa Lobo; o chassi usa o Urso, o padrão defensivo do caminho); Aspect of the Beast (6); Spirit Walker (10)."),
    'wild-magic': (wild, 'striker', 'malho, meia-armadura', ['Crusher'],
        "Bárbaro da Magia Selvagem: um efeito aleatório a cada fúria e Bolstering Magic para acertar mais.",
        "Wild Surge além das opções 4 e 8; Magic Awareness; restaurar espaços com Bolstering Magic; Unstable Backlash (10); empurrão do Crusher."),
    'zealot': (zealot, 'striker', 'machado grande, meia-armadura', ['Great Weapon Master'],
        "Zelote: dano radiante extra no 1º acerto de cada turno na fúria e Fanatical Focus.",
        "Warrior of the Gods (ressurreição); Zealous Presence só como 1/16 de vantagem para 3 aliados."),
}

if __name__ == '__main__':
    for sub, (fn, pos, eq, feats, resumo, nm) in SUBS.items():
        for feat in [None] + feats:
            C.escrever('barbarian', sub, pos, {L: fn(L, feat) for L in C.NIV},
                       build=f"Barbarian ({sub}), {pos}, {eq}; For > Con > Des" + (f"; {feat} no 4" if feat else "; sem feat"),
                       desc={"resumo": "Chassi: " + resumo,
                             "estrategia": "Fúria nas lutas que o plano automático escolher; Reckless Attack sempre.",
                             "nao_modelado": nm + " " + NM},
                       feat=feat, url=URL.format(sub))
