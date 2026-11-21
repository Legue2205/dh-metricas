"""Sorcerer (RPGBot, 2014) — passada 1 cega (21/11, mutirão). Reusa wiz.py (fatia/escrever).
Convenções desta classe:
- Espaços = tabela de conjurador pleno + Flexible Casting: TODOS os pontos de feitiçaria viram espaços (guloso, do
  maior círculo disponível até o 5º; custo 2/3/5/6/7). Metamagia não é modelada na passada 1 (os pontos iriam para ela).
- Mage Armor consome um espaço de 1º quando a build o usa (mesma convenção dos wizards).
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import wiz as W
from wiz import *

CUSTO = {1: 2, 2: 3, 3: 5, 4: 6, 5: 7}
def esp_sor(cl, sp, mage_armor=True):
    e = dict(SL[cl]); top = min(5, max(int(k) for k in e)); r = sp
    while r >= 2:
        s = max(x for x in range(1, top + 1) if CUSTO[x] <= r)
        e[str(s)] = e.get(str(s), 0) + 1; r -= CUSTO[s]
    if mage_armor: e["1"] -= 1
    return e
W.espacos = esp_sor
W.FONTE = lambda slug: {"tipo": "rpgbot", "url": f"https://rpgbot.net/dnd5/characters/classes/sorcerer/subclasses/{slug}/",
                        "nota": "Build exemplo do guia de subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."}
def dc(L, c): return 8 + prof(L) + c
def at(L, c): return prof(L) + c
def fb(L, a, n, extra=0):
    return {"ataques": [{"n": n, "bonus": a, "dano": f"{k(L)}d10" + (f"+{extra}" if extra else ""), "nota": "Fire Bolt" + (" + Elemental Affinity" if extra else "")}]}
def sp(L): return L if L >= 2 else 0
def draconic_spirit(lv, a):
    return {"nome": f"Summon Draconic Spirit ({lv}º)", "quantidade": 1, "pv": 50 + 10 * (lv - 5), "ca": 14 + lv,
            "ataque": {"n": lv // 2, "bonus": a, "dano": f"1d6+{4 + lv}"}}
BLESS = {"nome": "Bless", "lado": "of", "modelo": "bonus_continuo", "alvos": 3, "bonus": 2.5, "concentracao": "bless"}
PL = lambda cd: U("Raulothim's Psychic Lance", "psychic_lance", cd, 4)
POLY = lambda cd: U("Polymorph", "polymorph", cd, 4)

# ---------- Draconic Bloodline ----------
F = {}
for L, c in ((3, 3), (5, 3), (7, 3), (9, 4), (11, 4)):
    cd = dc(L, c); a = at(L, c); m = M(-1, 2, 3, -1, 0, c)
    ea = c if L >= 6 else 0
    pv = hpcalc([6] * L, 3) + L
    ctrl = []; ar = []; inv = None
    if L >= 5: ar = [FB(cd, ea)]
    if L >= 7: ar = [FB(cd, ea), area_sp("Wall of Fire", 3, f"5d8+{ea}", cd, 4)]
    if L >= 9: ctrl = [PL(cd)]; inv = dict(i=draconic_spirit(5, a), slot=5)
    if L >= 11: ctrl = [PL(cd), HM(cd)]; inv = dict(i=draconic_spirit(6, a), slot=6)
    F[L] = fatia(L, L, sp(L), m, ('con', 'car'), 13 + 2, pv, lambda n, L=L, a=a, ea=ea: fb(L, a, n, ea), ctrl, None, ar, inv, mage_armor=False)
    F[L]['_texto'] = f"Sorcerer {L}; Draconic Resilience (CA 13+Des, +1 PV/nível)" + ("; Elemental Affinity (+Car no fogo)" if ea else "") + "."
escrever('rpgbot-sorcerer-draconic', 'draconic-bloodline', 'Draconic Bloodline Sorcerer (RPGBot: Dungeons and Several Dragons)',
 "Sorcerer (Draconic, ancestral de fogo), Dragonborn metálico (Fizban), Elemental Adept 4, Gift of the Chromatic Dragon 8; Car 17 → 18 (8)",
 {"resumo": "Blaster de fogo com CA de armadura natural e PV extra; Elemental Affinity soma o Carisma no Fire Bolt e nas áreas de fogo.",
  "estrategia": "Fire Bolt no dia a dia; Fireball e Wall of Fire nas lutas com grupos; Summon Draconic Spirit e Psychic Lance/Hold Monster nos níveis altos.",
  "nao_modelado": "Metamagia (Heightened, Transmuted; Quickened/Twinned no 10); Elemental Adept (ignorar resistência); Dragon's Breath; Ice Knife; Raulothim's Binding Ice; Ashardalon's Stride; sopro racial; Gift of the Chromatic Dragon; resistência a fogo."}, F)

# ---------- Wild Magic ----------
F = {}
for L, c in ((3, 3), (5, 4), (7, 4), (9, 4), (11, 4)):
    cd = dc(L, c); a = at(L, c); m = M(-1, 3, 2, -1, -1, c)
    pv = hpcalc([6] * L, 2)
    ctrl = []; ar = []
    if L >= 9: ctrl = [POLY(cd)]; ar = [area_sp("Insect Plague", 4, "4d10", cd, 5)]
    F[L] = fatia(L, L, sp(L), m, ('con', 'car'), 16, pv, lambda n, L=L, cd=cd: sliver(L, cd, n), ctrl, None, ar)
    F[L]['_texto'] = f"Sorcerer {L}; Mage Armor." + (" Car 18 (Second Chance)." if L >= 5 else "")
escrever('rpgbot-sorcerer-wild-magic', 'wild-magic', 'Wild Magic Sorcerer (RPGBot: Maximum Chaos)',
 "Sorcerer (Wild Magic), Halfling (origem customizada), Second Chance 4, Fey Touched 8; Car 17 → 18 (4) → 19 (8)",
 {"resumo": "Conjurador do caos: magias imprevisíveis, Tides of Chaos e Bend Luck; ofensiva quase toda de truques.",
  "estrategia": "Mind Sliver e Chaos Bolt; Polymorph e Insect Plague nos níveis altos; Bend Luck para virar saves por 1–2.",
  "nao_modelado": "Wild Magic Surge e Tides of Chaos; Bend Luck; Chaos Bolt; Tasha's Caustic Brew; Nathair's Mischief, Vortex Warp, Enemies Abound, Sleet Storm, Confusion, Scatter (fora da biblioteca); Quickened/Twinned; Second Chance; Bane do Fey Touched."}, F)

# ---------- Clockwork Soul ----------
F = {}
for L, c in ((3, 3), (5, 4), (7, 4), (9, 5), (11, 5)):
    cd = dc(L, c); a = at(L, c); m = M(-1, 2, 3, -1, 1, c)
    pv = hpcalc([6] * L, 3); ca = 16 if L < 5 else 17
    ctrl = []; ar = []; bar = None
    if L >= 5: ctrl = [HYP(cd), WEB(cd)]; bar = WEB(cd)
    if L >= 7: ar = [FB(cd)]
    if L >= 9: ctrl = [HYP(cd), WEB(cd), POLY(cd), WOF(cd)]
    if L >= 11: ctrl = ctrl + [HM(cd)]
    F[L] = fatia(L, L, sp(L), m, ('con', 'car'), ca, pv, lambda n, L=L, cd=cd: sliver(L, cd, n), ctrl, bar, ar, mage_armor=False)
    F[L]['_texto'] = f"Sorcerer {L}; armadura média (anão da montanha), CA {ca}."
escrever('rpgbot-sorcerer-clockwork-soul', 'clockwork-soul', 'Clockwork Soul Sorcerer (RPGBot: Precision Engineering)',
 "Sorcerer (Clockwork Soul), Anão da Montanha (origem customizada, armadura média), Fey Touched 4, Car +2 8; Car 17 → 18 (4) → 20 (8)",
 {"resumo": "Sorcerer de suporte e controle com armadura média e 10 magias extras (Aid, Web, Hypnotic Pattern, Wall of Force).",
  "estrategia": "Mind Sliver/Fire Bolt; Web e Hypnotic Pattern para controlar; Wall of Force e Polymorph; Shield na reação.",
  "nao_modelado": "Restore Balance; Bastion of Law (ward com pontos de feitiçaria); Trance of Order; Twinned/Extended; Silvery Barbs; Aid; Tasha's Mind Whip; Dissonant Whispers; Greater Invisibility; Protection from Evil and Good."}, F)

# ---------- Aberrant Mind ----------
F = {}
for L, c in ((3, 3), (5, 4), (7, 4), (9, 5), (11, 5)):
    cd = dc(L, c); a = at(L, c); m = M(-1, 2, 3, -1, 0, c)
    pv = hpcalc([6] * L, 3)
    ctrl = []; ar = []; inv = None; bar = None
    if L >= 5: ctrl = [HP_(cd), WEB(cd)]; bar = WEB(cd); ar = [FB(cd)]
    if L >= 7: ctrl = [HP_(cd), WEB(cd), EBT(cd)]; inv = dict(i=summon('aberration', 4, a), slot=4)
    if L >= 9: ctrl = ctrl + [POLY(cd)]; inv = dict(i=summon('aberration', 5, a), slot=5)
    if L >= 11: ctrl = [HP_(cd), EBT(cd), POLY(cd), HM(cd)]; bar = HP_(cd); inv = dict(i=summon('aberration', 6, a), slot=6)
    F[L] = fatia(L, L, sp(L), m, ('con', 'car'), 13, pv, lambda n, L=L, a=a: fb(L, a, n), ctrl, bar, ar, inv, mage_armor=False)
    F[L]['_texto'] = f"Sorcerer {L}; Warforged (+1 CA, sem armadura)."
escrever('rpgbot-sorcerer-aberrant-mind', 'aberrant-mind', 'Aberrant Mind Sorcerer (RPGBot: Herald of the Abolithid)',
 "Sorcerer (Aberrant Mind), Warforged, Telekinetic 4, Car +2 8; Car 17 → 18 (4) → 20 (8)",
 {"resumo": "Sorcerer psiônico com magias extras de controle (Hold Person, Web, Black Tentacles) e invocação (Summon Aberration).",
  "estrategia": "Fire Bolt/Mind Sliver; Hold Person e Web; Fireball em grupos; Summon Aberration a partir do 7.",
  "nao_modelado": "Psionic Sorcery (conjurar com pontos, sem componentes); Hex + Scorching Ray; Silvery Barbs; Hunger of Hadar; Enemies Abound; Telekinetic (ação bônus); Quickened/Extended; Psychic Defenses; Revelation in Flesh."}, F)

# ---------- Divine Soul (Cleric 1 Order / Sorcerer) ----------
F = {}
for L, c in ((3, 3), (5, 4), (7, 4), (9, 5), (11, 5)):
    cd = dc(L, c); a = at(L, c); m = M(-1, -1, 3, 0, 2, c); sl = L - 1
    pv = hpcalc([8] + [6] * (L - 1), 3); ca = 16 if L < 7 else 18
    ctrl = []; ar = []
    if L >= 7: ar = [FB(cd)]
    if L >= 9: ctrl = [POLY(cd)]
    f = fatia(L, L, sp(sl), m, ('sab', 'car'), ca, pv, lambda n, L=L, a=a: fb(L, a, n), ctrl, None, ar, mage_armor=False)
    f['linhas'].append(dict(id="bless", herda="principal", hipotese="Bless nos aliados", dano=fb(L, a, 0.75),
                            suporte={"fontes": [BLESS]}, gasta={"espacos": {"1": 1}}))
    f['_texto'] = f"Cleric 1 (Order) / Sorcerer {sl}; armadura pesada (CA {ca})."
    F[L] = f
escrever('rpgbot-sorcerer-divine-soul', 'divine-soul', 'Divine Soul Sorcerer (RPGBot: 5e Mystic Theurge)',
 "Cleric 1 (Order) / Sorcerer (Divine Soul), Shifter, Telekinetic 5, Car +2 9; armadura pesada; Car 17 → 18 (5) → 20 (9)",
 {"resumo": "Suporte divino-arcano: Bless, Healing Word, Silvery Barbs com Voice of Authority (ataque de reação do aliado), Haste e Polymorph geminados.",
  "estrategia": "Bless/Shield of Faith no 1º round; Silvery Barbs e Healing Word para disparar Voice of Authority; Fireball em grupos; Polymorph.",
  "nao_modelado": "Voice of Authority (ataque de reação do aliado); Silvery Barbs; Twinned (Haste, Polymorph, Death Ward); Favored by the Gods; Healing Word; Shield of Faith; Guiding Bolt; Bestow Curse; Mass Cure Wounds; Telekinetic."}, F)
