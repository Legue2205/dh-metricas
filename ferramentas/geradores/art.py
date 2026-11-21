"""Passada 1 cega do Artificer (mutirão 21/11). Gerador no molde de wiz.py, com espaços de meio-conjurador
arredondados para cima, Steel Defender / Eldritch Cannon como `invocacoes` e Shield só onde a subclasse o tem."""
import sys, json
sys.path.insert(0, 'ferramentas/geradores'); sys.path.insert(0, '.')
import wiz
from dh.premissas import P as _P
P_CAIDO = _P('suporte.h.P_CAIDO')
BLESS = {"nome": "Bless", "lado": "of", "modelo": "bonus_continuo", "alvos": 3, "bonus": 2.5, "concentracao": "bless"}
from wiz import fatia, hpcalc, M, WEB, HYP, area_sp, FB, _anula

ART = {3: {"1": 3}, 5: {"1": 4, "2": 2}, 7: {"1": 4, "2": 3}, 9: {"1": 4, "2": 3, "3": 2}, 11: {"1": 4, "2": 3, "3": 3}}
wiz.espacos = lambda cl, wl, mage_armor=True: dict(ART[cl])
wiz.FONTE = lambda slug: {"tipo": "rpgbot", "url": f"https://rpgbot.net/dnd5/characters/classes/artificer/subclasses/{slug}/",
                          "nota": "Build exemplo do guia de subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."}
NIV = (3, 5, 7, 9, 11)
def pb(L): return 2 + (L - 1) // 4
def intm(L): return 3 if L < 4 else 4 if L < 8 else 5          # Int 17 → 18 (meio-feat 4) → 20 (8)
def mods(L, bs=False):
    i = 3 if L < 4 else 4 if (bs or L < 8) else 5               # Battle Smith: Mounted Combatant no 8 (Int 18 até o 12)
    return M(-1, 2, 3, i, 0, -1), i
def cd(L, i): return 8 + pb(L) + i
def ca(L, base=20): return base + (1 if L >= 10 else 0)          # Enhanced Defense +1 → +2 no 10
def k(L): return 1 + (L >= 5) + (L >= 11)
def pv(L): return hpcalc([8] * L, 3)
PROF = ('con', 'int')
TW = lambda c: area_sp("Thunderwave", 2, "2d8", c, 1)
SHAT = lambda c: area_sp("Shatter", 2, "3d8", c, 2)
LB = lambda c: area_sp("Lightning Bolt", 2, "8d6", c, 3)


def com_inv(f, inv):
    for l in f['linhas']: l['invocacoes'] = [inv] + [x for x in l.get('invocacoes', []) if x is not inv]
    return f


def battle_smith(L):
    m, i = mods(L, bs=True); p = pb(L); n = 1 if L < 5 else 2
    def arma(x):
        at = [{"n": round(n * x, 4), "bonus": p + i + 1, "dano": f"1d8+{i + 1}", "nota": "espada longa +1 (Enhanced Weapon, Int)"}]
        if L >= 9: at.append({"n": round(x * i / 4 / 4, 4), "bonus": p + i + 1, "dano": "2d6", "nota": "Arcane Jolt (Int/dia ÷ 4 lutas ÷ 4 rounds)"})
        return {"ataques": at}
    f = fatia(L, L, 0, m, PROF, ca(L), pv(L), arma, ctrl=[WEB(cd(L, i))] if L >= 5 else (), papel='striker', front=True)
    sd = {"nome": "Steel Defender", "quantidade": 1, "pv": 2 + i + 5 * L, "ca": 15,
          "ataque": {"n": 1, "bonus": p + i, "dano": f"1d8+{p}"}}
    for l in f['linhas']:      # Deflect Attack (reação do Defender, 1/round): desvantagem no 1º ataque do round contra a build
        d = dict(l.get('defesa', {})); l['defesa'] = d; d['reacoes'] = d.get('reacoes', []) + [{"tipo": "desvantagem", "usos_luta": 4, "propria": True}]
    return com_inv(f, sd)


def armorer(L):
    # Guia: Infiltrator, Dex 16/Con 14/Int 17; peitoral + escudo (CA 18, sem Enhanced Defense); Lightning Launcher +1
    m = M(-1, 3, 2, 3 if L < 4 else 4 if L < 8 else 5, 0, -1); i = m['int']; p = pb(L); n = 1 if L < 5 else 2
    def ll(x):
        return {"ataques": [{"n": round(n * x, 4), "bonus": p + i + 1, "dano": f"1d6+{i + 1}", "nota": "Lightning Launcher +1 (Int)"},
                            {"n": round(x, 4), "bonus": p + i + 1, "dano": "1d6", "nota": "Lightning Launcher: +1d6 uma vez por turno (aprox.: 1 rolagem/turno)"}]}
    ar = [TW(cd(L, i))] + ([SHAT(cd(L, i))] if L >= 5 else []) + ([LB(cd(L, i))] if L >= 9 else [])
    ct = [HYP(cd(L, i))] if L >= 9 else []
    return fatia(L, L, 0, m, PROF, 18, hpcalc([8] * L, 2), ll, ctrl=ct, areas=ar, shield=False, papel='atirador')


def artillerist(L):
    # Guia: centauro, Con 16/Int 17, escamas + escudo (CA 18; Repulsion Shield +1 a partir do 7), Acid Splash + Force Ballista
    m, i = mods(L); p = pb(L)
    fbx = "+1d8" if L >= 5 else ""                      # Arcane Firearm (5): +1d8 numa rolagem de dano da magia
    cant = lambda x: {"com_save": [{"n": x, "cd": cd(L, i), "save": "Des", "dano": f"{k(L)}d6{fbx}", "meio": False,
                                    "nota": "Acid Splash (1 alvo contado)"}]}
    ar = [TW(cd(L, i))] + ([SHAT(cd(L, i))] if L >= 5 else []) + ([FB(cd(L, i), extra=4)] if L >= 9 else [])
    f = fatia(L, L, 0, m, PROF, 18 + (L >= 7), pv(L), cant, areas=ar)
    can = {"nome": "Eldritch Cannon (Force Ballista)", "quantidade": 1, "pv": 5 * L, "ca": 18,
           "ataque": {"n": 1, "bonus": p + i + 1, "dano": "3d8" if L >= 9 else "2d8"}}
    return com_inv(f, can)


def alchemist(L):
    # Guia: fada, Dex 16/Con 14/Int 17; couro batido + escudo (CA 17); Acid Splash (+Int no 5); Healing Word; Bless (Fey Touched 4)
    m = M(-1, 3, 2, 3 if L < 4 else 4 if L < 8 else 5, 0, -1); i = m['int']; p = pb(L)
    sav = f"+{i}" if L >= 5 else ""
    cant = lambda x: {"com_save": [{"n": x, "cd": cd(L, i), "save": "Des", "dano": f"{k(L)}d6{sav}", "meio": False,
                                    "nota": "Acid Splash (Alchemical Savant no 5; 1 alvo contado)"}]}
    f = fatia(L, L, 0, m, PROF, 17, hpcalc([8] * L, 2), cant, shield=False)
    hw = {"nome": "Healing Word (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
          "acao": "bonus", "usos_luta": 1, "pv": round(2.5 + i + (i if L >= 5 else 0), 2)}
    if L >= 5:
        b = dict(f['linhas'][0]); b = json.loads(json.dumps(b)); b.pop('principal', None); b.pop('custo', None)
        b.update(id="bless", herda="principal", hipotese="Bless (Fey Touched) no round 1", dano=cant(0.75),
                 suporte={"fontes": [BLESS]}, gasta={"espacos": {"1": 1}})
        f['linhas'].append(b)
    for l in f['linhas']:
        l['suporte'] = {"fontes": l.get('suporte', {}).get('fontes', []) + [hw]}
        g = dict(l.get('gasta', {})); e = dict(g.get('espacos', {})); e["1"] = round(e.get("1", 0) + P_CAIDO, 3)
        g['espacos'] = e; l['gasta'] = g
    return f


NM_COMUM = ["Infusões além de Enhanced Defense/Weapon/Focus", "Flash of Genius (7)", "Spell-Storing Item (11)",
            "Faerie Fire e Grease (sem entrada na biblioteca de controle)", "Cure Wounds / Healing Word"]
B = {
 "battle-smith": (battle_smith, "Battle Smith", "Artificer (Battle Smith) autognomo, meia-armadura + escudo, espada longa +1 (Int); Skill Expert 4 (Int 18), Mounted Combatant 8",
     {"resumo": "Build Super Fighting Robot: arma com Int, Steel Defender, Shield e Web.",
      "nao_modelado": NM_COMUM + ["Montaria no Steel Defender (a build monta; aqui o Defender ataca)", "Arcane Jolt como cura"]}),
 "armorer": (armorer, "Armorer", "Artificer (Armorer, Infiltrator) vedalken, peitoral + escudo, Lightning Launcher +1 (Int); Skill Expert 4 (Int 18), Int 20 (8)",
     {"resumo": "Infiltrator de distância: Lightning Launcher com Int e Extra Attack, magias de área da subclasse, Hypnotic Pattern no 9.",
      "nao_modelado": NM_COMUM + ["Homunculus", "Vantagem em Furtividade", "Heat Metal e Tasha's Caustic Brew (sem entrada)", "Resistant Armor (10)"]}),
 "artillerist": (artillerist, "Artillerist", "Artificer (Artillerist) centauro, escamas + escudo, Acid Splash com Arcane Firearm, Force Ballista; Fey Touched 4 (Int 18), Int 20 (8)",
     {"resumo": "Build Practical Problem Solver: Acid Splash, canhão Force Ballista na ação bônus, Shield, Shatter e Fireball.",
      "nao_modelado": NM_COMUM + ["Protector cannon (PV temporários)", "Flamethrower (plano declarado do guia)", "Explosão do canhão", "Bane (Fey Touched)", "Acid Splash no 2º alvo"]}),
 "alchemist": (alchemist, "Alchemist", "Artificer (Alchemist) fada, couro batido + escudo, Acid Splash com Alchemical Savant, Healing Word; Fey Touched 4 (Int 18, Bless), Int 20 (8)",
     {"resumo": "Build Here, Drink This: Acid Splash, Healing Word e Bless; elixires e Aid como apoio.",
      "nao_modelado": NM_COMUM + ["Experimental Elixir", "Aid", "Restorative Reagents", "Homunculus", "Voo (fada)", "Acid Splash no 2º alvo"]}),
}
if __name__ == '__main__':
    for slug, (fn, nome, build, desc) in B.items():
        wiz.escrever(f"rpgbot-artificer-{slug}", slug, f"Artificer — {nome} (RPGBot)", build, desc, {L: fn(L) for L in NIV})
