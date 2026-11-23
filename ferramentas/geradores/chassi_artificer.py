"""Chassi do Artificer (mini-mutirão 22/11). Features das subclasses reaproveitadas de art.py; régua comum:
Int > Con > Des (compra padrão +2/+1), meia-armadura + escudo (Armorer: placas + escudo), infusões Enhanced Defense
(armadura), Enhanced Weapon (arma, quem ataca com arma) e Enhanced Arcane Focus (truque/canhão) — +1 no 7, +2 no 11;
truque base Fire Bolt; magia base de controle Web. Shield só onde a subclasse o dá (Artillerist, Battle Smith).
Feat da subclasse (1º não racial da build do RPGBot): Skill Expert (Battle Smith, Armorer) e Fey Touched
(Artillerist, Alchemist), ambos meio-feat de Int, no 4. Fey Touched: Bless (o Artillerist do RPGBot pega Bane; aqui
Bless nos dois para a mesma régua, Bane não tem entrada). Skill Expert não tem mecânica no motor (nao_modelado).
Rodar da raiz: python ferramentas/geradores/chassi_artificer.py && python -m dh expandir
"""
import json
import sys
sys.path.insert(0, 'ferramentas/geradores'); sys.path.insert(0, '.')
import chassi as C  # noqa: E402
import wiz  # noqa: E402
from wiz import area_sp, HYP, WEB, FB, SH, RE  # noqa: E402
from dh.premissas import P as _P  # noqa: E402

P_CAIDO = _P('suporte.h.P_CAIDO')
ART = {7: {"1": 4, "2": 3}, 11: {"1": 4, "2": 3, "3": 3}}        # meio-conjurador arredondado para cima
wiz.espacos = lambda cl, wl, mage_armor=True: dict(ART[cl])
ORDEM = ('int', 'con', 'des', 'sab', 'for', 'car')
PROF = ('con', 'int')
BLESS = {"nome": "Bless", "lado": "of", "modelo": "bonus_continuo", "alvos": 3, "bonus": 2.5, "concentracao": "bless"}
URL = "https://rpgbot.net/dnd5/characters/classes/artificer/subclasses/{}/"
FEATS = {'battle-smith': 'Skill Expert', 'armorer': 'Skill Expert', 'artillerist': 'Fey Touched', 'alchemist': 'Fey Touched'}


def base(L, feat):
    s = C.atributos('artificer', L, ORDEM, feat=feat, meio_feat='int' if feat else None); m = C.mods(s)
    i = m['int']; p = C.pb(L); E = 1 if L < 10 else 2                    # infusões +1 → +2 no 10
    return s, m, i, p, E, 8 + p + i


def k(L): return 1 + (L >= 5) + (L >= 11)


def fire_bolt(L, bon, extra=''):
    return lambda x: {"ataques": [{"n": round(x, 4), "bonus": bon, "dano": f"{k(L)}d10{extra}",
                                   "nota": "Fire Bolt (Enhanced Arcane Focus)"}]}


def pos(f, posicao, front=None):
    for l in f['linhas']:
        if 'controle' in l:
            l['controle']['atencao'] = C.atencao(posicao, **({} if front is None else {"front": front}))
        l.setdefault('hipotese', l['id'])
    return f


def com_inv(f, inv, gasto=None):
    """gasto = espaços por luta que a invocação custa (P1.9, 22/11: o Eldritch Cannon sai grátis 1×/descanso longo e
    depois custa um espaço; sem gasto, ele ficava de graça em todas as lutas). Com gasto, a linha principal (anel
    interno, grátis) fica sem a invocação e ganha uma irmã "<id>+inv" com ela."""
    novas = []
    for l in f['linhas']:
        if gasto and l.get('principal'):
            c = json.loads(json.dumps(l)); c.pop('principal', None); c.pop('custo', None)
            c.update(id=l['id'] + '+inv', herda=l['id'], hipotese=l.get('hipotese', l['id']) + ' + ' + inv['nome'])
            c['invocacoes'] = [inv] + c.get('invocacoes', []); c['gasta'] = {"espacos": dict(gasto)}
            novas.append(c); continue
        l['invocacoes'] = [inv] + [x for x in l.get('invocacoes', []) if x is not inv]
        if gasto:
            g = dict(l.get('gasta', {})); e = dict(g.get('espacos', {}))
            for k, v in gasto.items(): e[k] = round(e.get(k, 0) + v, 3)
            g['espacos'] = e; l['gasta'] = g
    f['linhas'] += novas
    return f


def bless_linha(f, cant):
    b = json.loads(json.dumps(f['linhas'][0])); b.pop('principal', None); b.pop('custo', None)
    b.update(id="bless", herda="principal", hipotese="Bless (Fey Touched) no round 1", dano=cant(0.75),
             suporte={"fontes": b.get('suporte', {}).get('fontes', []) + [BLESS]}, gasta={"espacos": {"1": 1}})
    f['linhas'].append(b)


def hp(L, m): return C.hp(8, L, m['con'])


def battle_smith(L, feat):
    s, m, i, p, E, cd = base(L, feat); n = 2
    def arma(x):
        at = [{"n": round(n * x, 4), "bonus": p + i + E, "dano": f"1d8+{i + E}", "nota": "espada longa (Battle Ready, Enhanced Weapon)"}]
        if L >= 9: at.append({"n": round(x * i / 4 / 4, 4), "bonus": p + i + E, "dano": "2d6", "nota": "Arcane Jolt (Int/dia ÷ 4 lutas ÷ 4 rounds)"})
        return {"ataques": at}
    f = wiz.fatia(L, L, 0, m, PROF, 18 + E, hp(L, m), arma, ctrl=[WEB(cd)], shield=True, papel='striker', front=True)
    for l in f['linhas']:      # Deflect Attack: reação do Defender, desvantagem no 1º ataque do round contra a build
        d = dict(l.get('defesa', {})); l['defesa'] = d
        d['reacoes'] = d.get('reacoes', []) + [{"tipo": "desvantagem", "usos_luta": 4, "propria": True}]
    sd = {"nome": "Steel Defender", "quantidade": 1, "pv": 2 + i + 5 * L, "ca": 15,
          "ataque": {"n": 1, "bonus": p + i, "dano": f"1d8+{p}"}}
    return pos(com_inv(f, sd), 'striker'), s


def _armorer_areas(cd, L):
    return [area_sp("Thunderwave", 2, "2d8", cd, 1), area_sp("Shatter", 2, "3d8", cd, 2)] + \
        ([area_sp("Lightning Bolt", 2, "8d6", cd, 3)] if L >= 9 else [])


def guardian(L, feat):
    s, m, i, p, E, cd = base(L, feat); n = 2
    tg = lambda x: {"ataques": [{"n": round(n * x, 4), "bonus": p + i + E, "dano": f"1d8+{i + E}",
                                 "nota": "Thunder Gauntlets (Int, Enhanced Weapon)"}]}
    ga = {"tipo": "ancestral_protectors", "nome": "Thunder Gauntlets (desvantagem contra outros)", "bonus": p + i + E,
          "resistencia": False}
    ctrl = [WEB(cd)] + ([HYP(cd)] if L >= 9 else [])
    f = wiz.fatia(L, L, 0, m, PROF, 20 + E, hp(L, m), tg, ctrl=ctrl, areas=_armorer_areas(cd, L), shield=False,
                  papel='tank', front=True, ctl_extra=[ga])
    f['corpo']['pvt_luta'] = round(p * L / 4, 2)          # Defensive Field: PB/dia × nível de PV temp ÷ 4 lutas
    return pos(f, 'defensor'), s


def infiltrator(L, feat):
    s, m, i, p, E, cd = base(L, feat); n = 2
    ll = lambda x: {"ataques": [
        {"n": round(n * x, 4), "bonus": p + i + E, "dano": f"1d6+{i + E}", "nota": "Lightning Launcher (Int, Enhanced Weapon)"},
        {"n": round(x, 4), "bonus": p + i + E, "dano": "1d6", "nota": "Lightning Launcher: +1d6 uma vez por turno (1 rolagem/turno)"}]}
    ctrl = [WEB(cd)] + ([HYP(cd)] if L >= 9 else [])
    f = wiz.fatia(L, L, 0, m, PROF, 20 + E, hp(L, m), ll, ctrl=ctrl, areas=_armorer_areas(cd, L), shield=False, papel='atirador')
    return pos(f, 'atirador'), s


def artillerist(L, feat):
    s, m, i, p, E, cd = base(L, feat)
    cant = fire_bolt(L, p + i + E, "+1d8")                # Arcane Firearm (5): +1d8 numa rolagem de dano
    ar = [area_sp("Thunderwave", 2, "2d8+4", cd, 1), area_sp("Shatter", 2, "3d8+4", cd, 2)] + ([FB(cd, extra=4)] if L >= 9 else [])
    f = wiz.fatia(L, L, 0, m, PROF, 18 + E, hp(L, m), cant, ctrl=[WEB(cd)], areas=ar, shield=True)
    if feat: bless_linha(f, cant)
    can = {"nome": "Eldritch Cannon (Force Ballista)", "quantidade": 1, "pv": 5 * L, "ca": 18,
           "ataque": {"n": 1, "bonus": p + i + E, "dano": "3d8" if L >= 9 else "2d8"}}
    return pos(com_inv(f, can, {"1": 0.75}), 'retaguarda'), s   # 1 grátis/descanso longo + 3 espaços de 1º nas 4 lutas


def alchemist(L, feat):
    s, m, i, p, E, cd = base(L, feat)
    cant = fire_bolt(L, p + i + E, f"+{i}")               # Alchemical Savant (5): +Int no dano de fogo
    f = wiz.fatia(L, L, 0, m, PROF, 18 + E, hp(L, m), cant, ctrl=[WEB(cd)], shield=False)
    if feat: bless_linha(f, cant)
    hw = {"nome": "Healing Word (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
          "acao": "bonus", "usos_luta": 1, "pv": round(2.5 + 2 * i, 2)}   # 1d4 + Int + Int (Savant)
    for l in f['linhas']:
        l['suporte'] = {"fontes": l.get('suporte', {}).get('fontes', []) + [hw]}
        g = dict(l.get('gasta', {})); e = dict(g.get('espacos', {})); e["1"] = round(e.get("1", 0) + P_CAIDO, 3)
        g['espacos'] = e; l['gasta'] = g
    return pos(f, 'retaguarda'), s


NM = ["Infusões além de Enhanced Defense/Weapon/Arcane Focus", "Spell-Storing Item (11)",
      "Faerie Fire, Grease, Haste e Cure Wounds (lista base sem entrada ou fora da régua)", "Tool Expertise e utilitários"]
NM_FEAT = {'Skill Expert': ["Skill Expert: perícia e expertise (sem mecânica no motor; a variante só difere no atributo)"],
           'Fey Touched': ["Fey Touched: Misty Step", "Fey Touched: magia de 1º círculo grátis 1×/dia (aqui gasta espaço)"]}
SUBS = [
    ('battle-smith', 'battle-smith', battle_smith, 'striker',
     "Artificer (Battle Smith), striker de espada longa + escudo, meia-armadura, Steel Defender",
     "Chassi do Battle Smith: arma com Int e Extra Attack, Steel Defender com Deflect Attack, Shield e Web.",
     ["Montaria no Steel Defender", "Arcane Jolt como cura", "Heroism, Branding Smite, Warding Wind, Aura of Vitality"]),
    ('armorer', 'armorer', guardian, 'defensor',
     "Artificer (Armorer, Guardian), defensor de placas + escudo, Thunder Gauntlets, Defensive Field",
     "Chassi do Armorer no modelo Guardian: Thunder Gauntlets com Int (marca sem resistência), PV temporários do "
     "Defensive Field, magias de área da subclasse e Web; Hypnotic Pattern no 9.",
     ["Mirror Image, Magic Missile, Fire Shield (sem entrada)", "Homunculus", "Troca de modelo no descanso",
      "Defensive Field como ação bônus (PB/dia; aqui carga média por luta)"]),
    ('armorer-infiltrator', 'armorer', infiltrator, 'atirador',
     "Artificer (Armorer, Infiltrator), atirador de placas + escudo, Lightning Launcher",
     "Chassi do Armorer no modelo Infiltrator: Lightning Launcher com Int e Extra Attack (+1d6 1×/turno), magias de "
     "área da subclasse e Web; Hypnotic Pattern no 9.",
     ["Powered Steps e Dampening Field (furtividade)", "Mirror Image, Magic Missile (sem entrada)", "Homunculus"]),
    ('artillerist', 'artillerist', artillerist, 'retaguarda',
     "Artificer (Artillerist), retaguarda de meia-armadura + escudo, Fire Bolt com Arcane Firearm, Force Ballista",
     "Chassi do Artillerist: Fire Bolt com Arcane Firearm, canhão Force Ballista na ação bônus, Shield, Web, "
     "Thunderwave/Shatter e Fireball no 9.",
     ["Protector e Flamethrower (só Force Ballista)", "Explosão do canhão", "Scorching Ray, Wind Wall (sem entrada)"]),
    ('alchemist', 'alchemist', alchemist, 'retaguarda',
     "Artificer (Alchemist), retaguarda de meia-armadura + escudo, Fire Bolt com Alchemical Savant, Healing Word",
     "Chassi do Alchemist: Fire Bolt com Alchemical Savant, Healing Word com +Int e Web.",
     ["Experimental Elixir", "Restorative Reagents", "Ray of Sickness, Flaming Sphere, Melf's Acid Arrow, Mass Healing Word",
      "Homunculus"]),
]

if __name__ == '__main__':
    for sid, sub, fn, posicao, build, resumo, nm in SUBS:
        for feat in (None, FEATS[sub]):
            fat = {}
            for L in C.NIV:
                f, s = fn(L, feat); f['_texto'] = f"atributos {s}"; fat[L] = f
                if L >= 7:   # M8 (23/11): Flash of Genius: reação, +Int num teste/save de um aliado, Int usos/descanso longo
                    ii = base(L, feat)[2]
                    fg = {"nome": "Flash of Genius", "lado": "def", "modelo": "bonus_por_uso", "bonus": ii,
                          "usos_luta": round(ii / 4, 3), "acao": "reacao"}
                    for l in f['linhas']:
                        fs = [x for x in (l.get('suporte') or {}).get('fontes', []) if x.get('nome') != 'Flash of Genius']
                        l['suporte'] = dict(l.get('suporte') or {}, fontes=fs + [fg])
            b = build + (f"; {feat} no 4 (Int +1)" if feat else "; sem feat")
            desc = {"resumo": resumo, "nao_modelado": NM + nm + (NM_FEAT[feat] if feat else [])}
            if feat: desc["feat"] = f"{feat}: 1º feat não racial da build do RPGBot ({sub})."
            id_ = C.escrever('artificer', sid, posicao, fat, build=b, desc=desc, feat=feat, url=URL.format(sub))
            if sid != sub:      # 2º modelo da mesma subclasse: id próprio, subclasse = a do gabarito
                pth = C.OUT + id_ + '.json'; P = json.load(open(pth))
                P.update(subclasse=sub, modelo='infiltrator',
                         nome="Armorer (Infiltrator) Artificer — chassi" + (f" + {feat}" if feat else ''))
                json.dump(P, open(pth, 'w'), ensure_ascii=False, indent=1)
