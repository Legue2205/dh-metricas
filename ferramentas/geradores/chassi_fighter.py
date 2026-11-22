"""Chassi do Fighter (mini-mutirão de 22/11): 10 subclasses, sem feat e com o feat da subclasse. Fatias 7 e 11.
Rodar da raiz: python ferramentas/geradores/chassi_fighter.py && python -m dh expandir
Features reaproveitadas de fighter_lote2.py / p2.py / puro_fighter.py e dos JSONs do lote 1 (só os números das FEATURES).
Mesma régua: Archery +2 no acerto à distância, Dueling +2 no dano a uma mão, GWF +1,33 no 2d6; placas 18 (+2 escudo);
Des à distância: max(couro batido 12+Des, meia-armadura 15+2) = 17. Action Surge = 1 round de 4 com os ataques da ação.
Champion: igual ao modelo (chassi_exemplo.py), mesmos ids.
"""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402

AS = {"qtd": 1, "volta": "curto"}
URL = "https://rpgbot.net/dnd5/characters/classes/fighter/subclasses/{}/"
PODER = {"poder": [-5, 10]}
SEMPRE = "Second Wind; Indomitable (9)"
REAC_OA = [{"uso": "ataque de oportunidade (Sentinel/Hold the Line)", "fracao": 0.5, "eixos": ["dano", "controle"]}]


def n_atq(L): return 2 if L < 11 else 3


def ficha(L, ordem, feat=None, meio=None, saves=('for', 'con')):
    s = C.atributos('fighter', L, ordem, feat=feat, meio_feat=meio); m = C.mods(s)
    return s, m, C.pb(L), (lambda ca, n: {"ca": ca, "pv": C.hp(10, L, m['con']), "saves": {"sv": C.sv(L, m, saves), "ataques": n}})


def ca_des(m): return max(12 + m['des'], 15 + min(2, m['des']))


def ctl(pos, extra=(), **at):
    return {"atencao": C.atencao(pos, **at), "fontes": list(extra) + [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}


def surge_de(ataques): return [dict(a, n=round(a['n'] / 4, 4)) for a in ataques if not a.get('_bonus')]


def limpa(ataques): return [{k: v for k, v in a.items() if k != '_bonus'} for a in ataques]


def linha0(hip, dano, controle, defesa=None, **k):
    l = {"id": "principal", "hipotese": hip, "dano": dano, "defesa": defesa or {}, "controle": controle, "saves": {}}
    l.update(k); return l


def surge(dano, gasta=None, hip="Action Surge num round"):
    d = dict(dano); d['ataques'] = limpa(dano['_atq']) + surge_de(dano['_atq'])
    return {"id": "surge", "herda": "principal", "plano": "prioritaria", "hipotese": hip, "dano": d,
            "gasta": dict(gasta or {}, action_surge=1)}


def D(atq, **k):
    """dano com a lista crua (_atq) guardada para o surge; limpa antes de escrever."""
    return dict(ataques=limpa(atq), _atq=atq, **k)


def fim(f):
    for l in f['linhas']: l['dano'].pop('_atq', None)
    return f


def piercer(dado):
    g = {'d6': '0.75', 'd8': '1', 'd10': '1.25', 'd12': '1.5'}[dado]
    return [{"dano": g, "nota": f"Piercer: rerrolar o {dado}"}, {"dano": f"1{dado}", "gatilho": "critico", "nota": "Piercer: dado extra no crítico"}]


# ---------------- Champion (igual ao modelo) ----------------
def champion(L, feat=None):
    s, m, p, corpo = ficha(L, ('for', 'con', 'des', 'sab', 'car', 'int'), feat)
    n = n_atq(L); gwm = PODER if feat == 'Great Weapon Master' else {}
    atk = {"n": n, "bonus": m['for'] + p, "dano": f"2d6+{m['for']}+1.33", "crit_em": 19, **gwm}
    linhas = [{"id": "principal", "hipotese": "espadão com GWF todo round", "dano": {"ataques": [atk]}, "defesa": {},
               "controle": {"atencao": C.atencao('striker'), "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}, "saves": {}},
              {"id": "surge", "herda": "principal", "plano": "prioritaria", "hipotese": "Action Surge num round",
               "dano": {"ataques": [atk, dict(atk, n=round(n / 4, 4))]}, "gasta": {"action_surge": 1}}]
    return {"corpo": corpo(18, n), "recursos": {"espacos": {}, "outros": {"action_surge": AS}}, "linhas": linhas,
            "_texto": f"atributos {s}"}


# ---------------- Battle Master: atirador ----------------
def battle_master(L, feat=None):
    s, m, p, corpo = ficha(L, ('des', 'con', 'sab', 'for', 'int', 'car'), feat)
    n = n_atq(L); b = m['des'] + p + 2; dado = '1d8' if L < 10 else '1d10'
    atq = [dict(n=n, bonus=b, dano=f"1d8+{m['des']}", **(PODER if feat == 'Sharpshooter' else {}))]
    pl = [{"usos": 2.5, "dano": dado, "nota": "dado de superioridade no acerto (5 por descanso curto ÷ 2 lutas)"}]
    cf = [{"tipo": "condicao_no_acerto", "nome": "Menacing Attack (dado de superioridade)", "efeito": "cond_amedrontado_um_turno",
           "cd": 8 + p + m['des'], "bonus": [b] * n, "usos": 2.5}]
    d = D(atq, por_luta=pl)
    return fim({"corpo": corpo(ca_des(m), n), "recursos": {"espacos": {}, "outros": {"action_surge": AS}},
                "linhas": [linha0("arco longo todo round; dados de superioridade no acerto (Menacing)", d, ctl('atirador', cf)), surge(d)],
                "_texto": f"atributos {s}; superioridade 5{dado[1:]}"})


# ---------------- Cavalier: defensor ----------------
def cavalier(L, feat=None):
    s, m, p, corpo = ficha(L, ('for', 'con', 'sab', 'des', 'car', 'int'), feat)
    n = n_atq(L); b = m['for'] + p
    atq = [dict(n=n, bonus=b, dano=f"1d8+{m['for']}+2"),
           dict(n=round(m['for'] / 16, 4), bonus=b, dano=f"1d8+{m['for'] + 2 + L // 2}", _bonus=True,
                nota="Unwavering Mark: ataque bônus (For/dia ÷ 4 lutas ÷ 4 rounds)")]
    cf = [{"tipo": "ancestral_protectors", "nome": "Unwavering Mark (marca no acerto)", "bonus": b}]
    extra = {}
    if L >= 10:   # Hold the Line
        atq.append(dict(n=0.5, bonus=b, dano=f"1d8+{m['for']}+2", _bonus=True, nota="ataque de oportunidade (Hold the Line), reação em 50% dos rounds"))
        cf.insert(0, {"tipo": "sentinela", "nome": "Hold the Line", "bonus": b}); extra = {"reacao": REAC_OA}
    c = ctl('defensor', cf, **({"hard": {"sentinela": b}} if L >= 10 else {}))
    d = D(atq)
    return fim({"corpo": corpo(20, n), "recursos": {"espacos": {}, "outros": {"action_surge": AS}},
                "linhas": [linha0("espada longa + escudo na frente; marca o alvo e pune quem bate em outro", d, c, **extra), surge(d)],
                "_texto": f"atributos {s}"})


# ---------------- Eldritch Knight: striker ----------------
def eldritch_knight(L, feat=None):
    s, m, p, corpo = ficha(L, ('for', 'con', 'int', 'des', 'sab', 'car'), feat, meio='for' if feat else None)
    n = n_atq(L); b = m['for'] + p; cd = 8 + p + m['int']
    atq = [dict(n=n, bonus=b, dano=f"2d6+{m['for']}+1.33")]
    k = {}
    if L < 11:   # War Magic: Booming Blade + 1 ataque bônus = 2 ataques; no 11 o Attack (3) rende mais
        k['por_turno'] = [{"dano": "1d8", "nota": "Booming Blade (War Magic): dado de trovão no acerto"}]
    area = [{"nome": "Sword Burst", "tipo": "cleave_save", "dano": "2d6" if L < 11 else "3d6", "cd": cd, "alvos": [1, 2, 3]}]
    if L >= 11: area.append({"nome": "Rime's Binding Ice", "usos": [{"alvos": 3, "dano": "3d8", "cd": cd, "slot": 2}]})
    d = D(atq, **k)
    sh = {"reacoes": [{"tipo": "shield", "usos_luta": 1}]}
    linhas = [linha0("espadão com GWF (War Magic com Booming Blade no 7); Shield 1×/luta", d, ctl('striker'), defesa=sh,
                     gasta={"espacos": {"1": 1}}, reacao=[{"uso": "Shield", "fracao": 0.5, "eixos": ["defesa"]}], area=area),
              {"id": "sem-shield", "hipotese": "sem gastar espaço no Shield", "dano": D(atq, **k), "defesa": {},
               "controle": ctl('striker'), "saves": {}, "area": area},
              dict(surge(d, {"espacos": {"1": 1}}), area=area)]
    return fim({"corpo": corpo(18, n), "recursos": {"espacos": {"1": 4, "2": 2 if L < 11 else 3}, "outros": {"action_surge": AS}},
                "linhas": linhas, "_texto": f"atributos {s}"})


# ---------------- Echo Knight: striker ----------------
def echo_knight(L, feat=None):
    s, m, p, corpo = ficha(L, ('for', 'con', 'des', 'sab', 'car', 'int'), feat)
    n = n_atq(L); b = m['for'] + p; dmg = f"2d6+{m['for']}+1.33"
    atq = [dict(n=n, bonus=b, dano=dmg),
           dict(n=round(m['con'] / 16, 4), bonus=b, dano=dmg, _bonus=True, nota="Unleash Incarnation (Con/dia ÷ 4 lutas ÷ 4 rounds)")]
    cf, at, extra = [], {}, {}
    if feat == 'Sentinel':
        atq.append(dict(n=0.5, bonus=b, dano=dmg, _bonus=True, nota="ataque de oportunidade (Sentinel, também pelo eco), reação em 50% dos rounds"))
        cf = [{"tipo": "sentinela", "nome": "Sentinel (pelo eco)", "bonus": b}]; at = {"hard": {"sentinela": b}}; extra = {"reacao": REAC_OA}
    d = D(atq)
    return fim({"corpo": corpo(18, n), "recursos": {"espacos": {}, "outros": {"action_surge": AS}},
                "linhas": [linha0("espadão com GWF, atacando pelo eco; Unleash Incarnation espalhado pelo dia", d, ctl('striker', cf, **at), **extra),
                           surge(d)], "_texto": f"atributos {s}"})


# ---------------- Psi Warrior: atirador ----------------
def psi_warrior(L, feat=None):
    s, m, p, corpo = ficha(L, ('des', 'con', 'int', 'sab', 'for', 'car'), feat, meio='des' if feat else None)
    n = n_atq(L); b = m['des'] + p + 2; dpsi = '1d8' if L < 11 else '1d10'; dia = 2 * p + 2
    atq = [dict(n=n, bonus=b, dano=f"1d8+{m['des']}")]
    k = {"por_luta": [{"usos_dia": dia, "dano": f"{dpsi}+{m['int']}", "nota": "Psionic Strike: 2×PB + 1 por descanso curto, ÷ 4 lutas"}]}
    if feat == 'Piercer': k['por_turno'] = piercer('d8')
    cf = [{"tipo": "condicao_no_acerto", "nome": "Telekinetic Thrust (Psionic Strike)", "efeito": "cond_derrubado",
           "cd": 8 + p + m['int'], "bonus": [b] * n, "usos": dia / 4}]
    d = D(atq, **k)
    return fim({"corpo": corpo(ca_des(m), n), "recursos": {"espacos": {}, "outros": {"action_surge": AS}},
                "linhas": [linha0("arco longo; dados psiônicos no Psionic Strike (com Telekinetic Thrust), espalhados pelo dia", d, ctl('atirador', cf)),
                           surge(d)], "_texto": f"atributos {s}; {dia} dados {dpsi[1:]}/dia"})


# ---------------- Purple Dragon Knight (Banneret): atirador ----------------
def pdk(L, feat=None):
    s, m, p, corpo = ficha(L, ('des', 'con', 'sab', 'car', 'for', 'int'), feat)
    n = n_atq(L); b = m['des'] + p + 2
    atq = [dict(n=n, bonus=b, dano=f"1d8+{m['des']}", **(PODER if feat == 'Sharpshooter' else {}))]
    sup = {"fontes": [{"nome": "Rallying Cry (Second Wind)", "lado": "def", "modelo": "cura", "usos_descanso_curto": 1, "pv": 3 * L,
                       "nota": "3 aliados × nível de Fighter"}]}
    if L >= 10:
        sup["fontes"].append({"nome": "Inspiring Surge (aliado ataca no Action Surge)", "lado": "of", "modelo": "ataque_extra",
                              "alvos": 0.125, "nota": "0,5 Action Surge por luta ÷ 4 rounds"})
    d = D(atq)
    return fim({"corpo": corpo(ca_des(m), n), "recursos": {"espacos": {}, "outros": {"action_surge": AS}},
                "linhas": [linha0("arco longo todo round; Rallying Cry junto do Second Wind", d, ctl('atirador'), suporte=sup), surge(d)],
                "_texto": f"atributos {s}"})


# ---------------- Rune Knight: defensor agarrador ----------------
def rune_knight(L, feat=None):
    s, m, p, corpo = ficha(L, ('for', 'con', 'des', 'sab', 'car', 'int'), feat, meio='for' if feat else None)
    n = n_atq(L); b = m['for'] + p; cd = 8 + p + m['con']
    atl = m['for'] + p * (2 if feat == 'Skill Expert' else 1)
    gm = '1d6' if L < 10 else '1d8'
    atq = [dict(n=round(n - 0.25, 4), bonus=b, dano=f"1d8+{m['for']}+2", nota="agarrar custa 1 ataque no 1º round")]
    cf = [{"tipo": "agarrao", "nome": "Agarrão (Atletismo)", "bonus": atl},
          {"tipo": "condicao_no_acerto", "nome": "Fire Rune", "efeito": "cond_impedido", "cd": cd, "bonus": [b] * n, "usos": 0.5},
          {"tipo": "condicao_no_acerto", "nome": "Stone Rune (reação)", "efeito": "cond_incapacitado", "cd": cd, "no_acerto": False, "usos": 0.5}]
    g = [{"dano": gm, "nota": "Giant's Might: dano extra 1×/turno"}]
    d = D(atq); dg = D(atq, por_turno=g)
    sur = surge(D([dict(atq[0], n=n)], por_turno=g), {"giants_might": 1, "hill_rune": 1}, "Giant's Might + Hill Rune + Action Surge")
    sur['dano']['ataques'] = limpa(atq) + surge_de([dict(atq[0], n=n)]); sur['defesa'] = {"resist": True}
    linhas = [linha0("espada longa (Dueling) com a outra mão livre: agarra o alvo prioritário e prende com as runas", d,
                     ctl('defensor', cf, agarra=True)),
              {"id": "gigante", "herda": "principal", "hipotese": "Giant's Might + Hill Rune na luta (resistência a dano físico)",
               "dano": dg, "defesa": {"resist": True}, "gasta": {"giants_might": 1, "hill_rune": 1}},
              sur]
    return fim({"corpo": corpo(18, n), "recursos": {"espacos": {}, "outros": {"action_surge": AS, "giants_might": {"qtd": p, "volta": "longo"},
                                                                        "hill_rune": {"qtd": 1, "volta": "curto"}}},
                "linhas": linhas, "_texto": f"atributos {s}; Atletismo +{atl}"})


# ---------------- Samurai: atirador ----------------
def samurai(L, feat=None):
    s, m, p, corpo = ficha(L, ('des', 'con', 'sab', 'for', 'int', 'car'), feat, meio='des' if feat else None, saves=('for', 'con', 'sab'))
    n = n_atq(L); b = m['des'] + p + 2; arma = '1d12' if feat == 'Gunner' else '1d8'
    v0 = 0.25 if L >= 10 else 0.0   # Tireless Spirit: 1 Fighting Spirit garantido por luta
    a = lambda v: [dict(n=n, bonus=b, dano=f"{arma}+{m['des']}", **({"vantagem": v} if v else {}))]
    d = D(a(v0)); de = D(a(min(1.0, v0 + 0.25)))
    linhas = [linha0("atira todo round" + (" (mosquete, Gunner)" if feat else " (arco longo)") + "; Fighting Spirit = vantagem num turno", d, ctl('atirador')),
              {"id": "espirito", "herda": "principal", "hipotese": "Fighting Spirit num round (vantagem nos ataques do turno)",
               "dano": de, "gasta": {"fighting_spirit": 1}},
              surge(de, {"fighting_spirit": 1}, "Fighting Spirit + Action Surge no mesmo round")]
    return fim({"corpo": corpo(ca_des(m), n), "recursos": {"espacos": {}, "outros": {"action_surge": AS, "fighting_spirit": {"qtd": 3, "volta": "longo"}}},
                "linhas": linhas, "_texto": f"atributos {s}"})


# ---------------- Arcane Archer: atirador ----------------
def arcane_archer(L, feat=None):
    s, m, p, corpo = ficha(L, ('des', 'con', 'int', 'sab', 'for', 'car'), feat)
    n = n_atq(L); b = m['des'] + p + 2
    atq = [dict(n=n, bonus=b, dano=f"1d8+{m['des']}", **(PODER if feat == 'Sharpshooter' else {}))]
    pl = [{"usos": 1, "dano": "2d6", "nota": "Arcane Shot (Shadow Arrow): 2 por descanso curto = 1 por luta"}]
    cf = [{"tipo": "condicao_no_acerto", "nome": "Shadow Arrow (Arcane Shot)", "efeito": "cond_cego_um_turno",
           "cd": 8 + p + m['int'], "bonus": [b] * n, "usos": 1}]
    area = [{"nome": "Curving Shot", "tipo": "cleave_ataque", "bonus": b, "dano": f"1d8+{m['des']}", "p": "erro", "n_erro": n}]
    d = D(atq, por_luta=pl)
    return fim({"corpo": corpo(ca_des(m), n), "recursos": {"espacos": {}, "outros": {"action_surge": AS}},
                "linhas": [linha0("arco longo; Shadow Arrow 1×/luta; Curving Shot redireciona um erro", d, ctl('atirador', cf), area=area),
                           dict(surge(d), area=area)], "_texto": f"atributos {s}"})


# sub: (função, posição, build, feats, resumo, nao_modelado, origem do feat)
SUBS = {
    'champion': (champion, 'striker', "striker de espadão, placas, GWF", ['Great Weapon Master'],
                 "Chassi do Champion: o Fighter base de espadão com Improved Critical.",
                 "Remarkable Athlete; Second Wind; Indomitable.",
                 "GWM mantido do modelo (chassi_exemplo.py); pela regra seria Piercer (6), sem efeito com espadão"),
    'battle-master': (battle_master, 'atirador', "atirador de arco longo, couro batido/meia-armadura, Archery", ['Sharpshooter'],
                      "Battle Master arqueiro: dados de superioridade somados no acerto e Menacing Attack para amedrontar.",
                      "Pushing/Trip/Rally/Commander's Strike e as outras manobras; Know Your Enemy; " + SEMPRE + ".",
                      "Sharpshooter (4) da build do RPGBot"),
    'cavalier': (cavalier, 'defensor', "defensor de espada longa + escudo, placas, Dueling", ['Mounted Combatant'],
                 "Cavalier a pé na frente: Unwavering Mark obriga o alvo a bater nele; Hold the Line no 10.",
                 "Montaria e lança (o chassi luta a pé); Mounted Combatant inteiro (vantagem contra menores que a montaria); "
                 "Warding Maneuver; Born to the Saddle; " + SEMPRE + ".",
                 "Mounted Combatant (1, via Custom Lineage) da build do RPGBot; não modelado, diferença só do ASI perdido"),
    'eldritch-knight': (eldritch_knight, 'striker', "striker de espadão, placas, GWF; Booming Blade, Sword Burst, Shield, Rime's Binding Ice",
                        ['Slasher'],
                        "Eldritch Knight de espadão: War Magic com Booming Blade no 7, Shield como reação, Sword Burst e Rime's Binding Ice para área.",
                        "Dano secundário do Booming Blade; Slasher (redução de deslocamento e desvantagem no crítico); Absorb Elements; "
                        "Eldritch Strike (10); controle do Rime's Binding Ice; " + SEMPRE + ".",
                        "Slasher (1, via Custom Lineage) da build do RPGBot, meio-feat em For"),
    'echo-knight': (echo_knight, 'striker', "striker de espadão, placas, GWF, atacando pelo eco", ['Sentinel'],
                    "Echo Knight de espadão: ataca pelo eco e ganha ataques extras com Unleash Incarnation; com Sentinel segura a linha pelo eco.",
                    "O eco como segundo ponto de ameaça e teleporte; Shadow Martyr; Reclaim Potential (PV temporários); " + SEMPRE + ".",
                    "Sentinel (1, via Custom Lineage) da build do RPGBot"),
    'psi-warrior': (psi_warrior, 'atirador', "atirador de arco longo, couro batido/meia-armadura, Archery", ['Piercer'],
                    "Psi Warrior arqueiro: dados psiônicos no Psionic Strike, com Telekinetic Thrust para derrubar.",
                    "Protective Field; Telekinetic Movement; Psi-Powered Leap; Telekinetic Adept fora do Thrust; Guarded Mind; " + SEMPRE + ".",
                    "Piercer (4) da build do RPGBot, meio-feat em Des"),
    'purple-dragon-knight': (pdk, 'atirador', "atirador de arco longo, couro batido/meia-armadura, Archery", ['Sharpshooter'],
                             "Purple Dragon Knight (Banneret) arqueiro: cura em grupo no Second Wind e ataque de aliado no Action Surge (10).",
                             "Royal Envoy; Bulwark (15); o Second Wind próprio; " + SEMPRE + ".",
                             "Sharpshooter (6) da extensão pura da build do RPGBot (a build original só tem Dragon Fear, racial)"),
    'rune-knight': (rune_knight, 'defensor', "defensor de espada longa (mão livre para agarrar), placas, Dueling; runas Fogo, Pedra, Colina",
                    ['Skill Expert'],
                    "Rune Knight agarrador na frente: Giant's Might, Fire Rune para impedir, Stone Rune para incapacitar, Hill Rune para resistir.",
                    "Storm Rune (10); Runic Shield; derrubar e a vantagem que dá; vantagem do Giant's Might no agarrão; "
                    "dano no agarrado; " + SEMPRE + ".",
                    "Skill Expert (4, expertise em Atletismo) da build do RPGBot, meio-feat em For"),
    'samurai': (samurai, 'atirador', "atirador de arco longo (mosquete com Gunner), couro batido/meia-armadura, Archery", ['Gunner'],
                "Samurai atirador: Fighting Spirit dá vantagem num turno; Tireless Spirit garante 1 por luta no 10.",
                "PV temporários do Fighting Spirit; Elegant Courtier fora dos saves; " + SEMPRE + ".",
                "Gunner (4) da build do RPGBot, meio-feat em Des; troca o arco pelo mosquete (armas de fogo da DMG)"),
    'arcane-archer': (arcane_archer, 'atirador', "atirador de arco longo, couro batido/meia-armadura, Archery", ['Sharpshooter'],
                      "Arcane Archer: Shadow Arrow 1×/luta (dano e cegueira) e Curving Shot para não perder o erro.",
                      "Vantagem da cegueira para a party; Magic Arrow; as outras flechas; " + SEMPRE + ".",
                      "Sharpshooter (6) da build do RPGBot (Elven Accuracy no 4 é racial)"),
}

if __name__ == '__main__':
    so = sys.argv[1:]
    for sub, (fn, pos, build, feats, resumo, nm, origem) in SUBS.items():
        if so and sub not in so: continue
        for feat in [None] + feats:
            nome = sub.replace('-', ' ').title()
            if sub == 'champion':
                b = f"Fighter (Champion), striker de espadão, placas, GWF" + (f"; {feat} no 4" if feat else "; sem feat")
                desc = {"resumo": resumo, "nao_modelado": nm}
            else:
                b = f"Fighter ({nome}), {build}" + (f"; {feat} no 4" if feat else "; sem feat")
                desc = {"resumo": resumo, "estrategia": f"Posição {pos}; feat da subclasse: {origem}.", "nao_modelado": nm}
                if feat == 'Mounted Combatant': desc['nao_modelado'] = "Mounted Combatant (sem montaria no chassi); " + nm
            C.escrever('fighter', sub, pos, {L: fn(L, feat) for L in C.NIV}, build=b, desc=desc, feat=feat, url=URL.format(sub))
