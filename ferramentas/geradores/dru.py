"""Druid (passada 1 cega, mutirão 21/11): Dreams, Land, Moon, Shepherd, Spores, Stars, Wildfire sobre um druida base.
Convenções no relatório da sessão (seção "Druidas"). Rodar da raiz do repo; depois `python -m dh expandir`."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
import wiz
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dh.premissas import P as _P
P_CAIDO = _P('suporte.h.P_CAIDO')
LPDC = _P('suporte.lutas_por_descanso_curto')
from wiz import SL, prof, k, merge, U, area_sp, area_pico, AT, hpcalc, M, escrever, controle_fonte

URL = {s: f'https://rpgbot.net/dnd5/characters/classes/druid/subclasses/{u}/' for s, u in
       dict(dreams='circle-of-dreams', land='circle-of-the-land', moon='moon', shepherd='circle-of-the-shepherd',
            spores='circle-of-spores', stars='circle-of-stars', wildfire='circle-of-wildfire').items()}
NOTA = "Build exemplo do guia de subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."
wiz.FONTE = lambda slug: {"tipo": "rpgbot", "url": URL[slug], "nota": NOTA}
FATIAS = (3, 5, 7, 9, 11)
FORMA = {"qtd": 2, "volta": "curto"}            # Wild Shape: 2 usos por descanso curto


# ---------- peças ----------
def produce_flame(L, atk, n, extra=''): return {"ataques": [{"n": n, "bonus": atk, "dano": f"{k(L)}d8{extra}", "nota": "Produce Flame"}]}
def thorn_whip(L, atk, n): return {"ataques": [{"n": n, "bonus": atk, "dano": f"{k(L)}d6", "nota": "Thorn Whip"}]}
def thunderclap(L, cd): return {"nome": "Thunderclap", "tipo": "cleave_save", "dano": f"{k(L)}d6", "cd": cd, "save": "Con", "alvos": [1, 2, 3]}
ENT = lambda cd: U("Entangle", "entangle", cd, 1, area=True)
HP = lambda cd: U("Hold Person", "hold_person", cd, 2)
POLY = lambda cd: U("Polymorph", "polymorph", cd, 4)
def ice_knife(cd): return area_sp("Ice Knife", 2, "2d6", cd, 1)
def erupting(cd): return area_sp("Erupting Earth", 2, "3d12", cd, 3)
def wall_fire(cd, extra=''): return area_sp("Wall of Fire", 3, "5d8" + extra, cd, 4)


def summon_beast(lv, atk):
    """Summon Beast (Tasha), opção Land: CA 11 + nível, PV 30 + 5/nível acima do 2º, lv//2 ataques de 1d8+4+nível."""
    return {"nome": f"Summon Beast (Land, {lv}º)", "quantidade": 1, "pv": 30 + 5 * (lv - 2), "ca": 11 + lv,
            "ataque": {"n": max(1, lv // 2), "bonus": atk, "dano": f"1d8+{4 + lv}"}}


def espacos(L, fora=0, extra=None):
    e = dict(SL[L])
    if fora: e["1"] -= fora
    for s, q in (extra or {}).items(): e[s] = e.get(s, 0) + q
    return e


def maior(esp): return max(int(s) for s, q in esp.items() if q > 0)


def fatia(L, mods, profs, ca, pv, cant, cd, atk, wis, papel, front, nm, esp=None, ctrl=(), areas=(), livres=(), sup=(),
          inv=None, extras=(), outros=None, reac=None, cura=None, forma_var=None):
    """nm = maior círculo de magia de druida conhecido. cura = fonte de cura na luta (padrão: Healing Word com 1º × P_CAIDO).
    forma_var = (sufixo, função linha->linha, gasto de forma) para a variante de Wild Shape de cada linha (Stars/Spores/Wildfire)."""
    p = prof(L); sv = {kk: mods[kk] + (p if kk in profs else 0) for kk in mods}
    corpo = dict(ca=ca, pv=pv, saves=dict(sv=sv, conjurador=True))
    esp = esp or espacos(L); top = maior(esp)
    rec = {"espacos": esp, "outros": dict({"forma_selvagem": dict(FORMA)}, **(outros or {}))}
    def S(*fs): return {"fontes": list(sup) + list(fs)}
    base_ctl = {"atencao": AT(front, papel), "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}
    L_ = []
    def ln(id_, dn, **kw):
        l = {"id": id_, "dano": dn}; l.update(kw)
        if id_ != 'principal': l.setdefault('herda', 'principal')
        L_.append(l)
    dfs, rq = ({"reacoes": [{"tipo": reac[1], "usos_luta": reac[2]}]}, [{"uso": reac[0], "fracao": round(reac[2], 3), "eixos": ["defesa"]}]) if reac else ({}, None)
    ln("principal", cant(1.0), controle=base_ctl, defesa=dfs, saves={}, area=list(livres), invocacoes=[], suporte=S())
    if rq: L_[0]['reacao'] = rq
    if ctrl:
        t = max(o['slot'] for o in ctrl)
        ln("controle", cant(0.75), controle={"atencao": AT(front, papel), "fontes": [controle_fonte(list(ctrl))]},
           gasta={"espacos": {str(t): 1}})
        b = min(ctrl, key=lambda o: o['slot'])
        if b['slot'] < t:
            ln("controle-barato", cant(0.75), controle={"atencao": AT(front, papel), "fontes": [b['f']]},
               gasta={"espacos": {str(b['slot']): 1}})
    if areas:
        ap, sp = area_pico(list(areas), esp)
        if ap:
            g = {}
            for x in sp: g[str(x)] = g.get(str(x), 0) + 1
            ln("area", cant(0.5 if len(ap) > 1 else 0.75), area=ap + list(livres), gasta={"espacos": g})
    if inv:
        ln("invocacao", cant(0.75), invocacoes=[inv['i']], gasta={"espacos": {str(inv['slot']): 0.5}})   # 1 hora = 2 lutas
    for x in extras:
        x = dict(x); x.setdefault('herda', 'principal'); L_.append(x)
    if forma_var:
        suf, fn, g_f = forma_var
        for l in list(L_):
            if 'forma_selvagem' in l.get('gasta', {}): continue
            v = fn(json.loads(json.dumps(l))); v['id'] = l['id'] + suf; v['herda'] = 'principal'
            v.pop('principal', None)
            v['hipotese'] = l.get('hipotese', 'só truques' if l['id'] == 'principal' else l['id']) + f" + {suf.strip('+')}"
            g = dict(l.get('gasta', {})); g['forma_selvagem'] = g_f; v['gasta'] = g
            L_.append(v)
    # Cura na luta (convenção do Cleric, 19/11): Healing Word em todas as linhas, 1º × P_CAIDO por luta.
    hw = cura or {"nome": "Healing Word (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
                  "acao": "bonus", "usos_luta": 1, "pv": round(2.5 + wis, 2)}
    custo_hw = cura is None
    for l in L_:
        if 'suporte' in l and not any(f.get('modelo') == 'cura_na_luta' for f in l['suporte']['fontes']):
            l['suporte'] = {"fontes": l['suporte']['fontes'] + [hw]}
        if custo_hw:
            g = dict(l.get('gasta', {})); e = dict(g.get('espacos', {})); e["1"] = round(e.get("1", 0) + P_CAIDO, 3)
            g['espacos'] = e; l['gasta'] = g
    return dict(corpo=corpo, recursos=rec, linhas=L_)


def emit(id_, slug, nome, build, desc, F):
    for L in FATIAS:
        for l in F[L]['linhas']:
            if l['id'] != 'principal': l.setdefault('hipotese', l['id'])
    escrever(id_, slug, nome, build, desc, F)


def forma_linha(L, nome, ca, pv_forma, pv, ataques, saves_extra=None, gasto=1):
    d = {"ataques": ataques}
    if saves_extra: d["com_save"] = saves_extra
    return {"id": "forma" if gasto == 1 else "elemental", "herda": "principal",
            "hipotese": f"Wild Shape de combate ({nome}, ação bônus); PV da forma somados aos do druida",
            "corpo": {"ca": ca, "pv": pv + pv_forma}, "dano": d,
            "controle": {"atencao": {"papel": "tank", "front": True, "soft": 0.15, "dpr": "auto", "conc": True},
                         "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]},
            "area": [], "invocacoes": [], "gasta": {"forma_selvagem": gasto}}


# ---------- Moon: "Moon Sailor" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 4 else 4 if L < 8 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    pv = hpcalc([8] * L, 2)
    cant = lambda n, L=L, atk=atk: produce_flame(L, atk, n)
    if L < 6: fl = [forma_linha(L, "Dire Wolf", 14, 37, pv, [{"n": 1, "bonus": 5, "dano": "2d6+3", "nota": "Dire Wolf, mordida (derruba: não modelado)"}])]
    elif L < 9: fl = [forma_linha(L, "Saber-Toothed Tiger", 12, 52, pv, [{"n": 1, "bonus": 6, "dano": "1d10+5", "nota": "tigre, mordida"},
                                                                         {"n": 1, "bonus": 6, "dano": "2d6+5", "nota": "tigre, garra"}])]
    else: fl = [forma_linha(L, "Giant Scorpion", 15, 52, pv, [{"n": 2, "bonus": 4, "dano": "1d8+2", "nota": "escorpião, pinças (agarra)"},
                                                               {"n": 1, "bonus": 4, "dano": "1d10+2", "nota": "escorpião, ferrão"}],
                                [{"n": 0.6, "cd": 12, "save": "Con", "dano": "4d10", "meio": True, "nota": "veneno do ferrão (≈ chance de acerto)"}])]
    if L >= 10:
        fl.append(forma_linha(L, "Fire Elemental (Elemental Wild Shape, 2 usos)", 13, 102, pv,
                              [{"n": 2, "bonus": 6, "dano": "2d6+3", "nota": "Fire Elemental, toque (incendeia: não modelado)"}], gasto=2))
    ctrl = [ENT(cd), HP(cd)] + ([POLY(cd)] if L >= 8 else [])
    # Passada 2 (21/11): o plano automático põe UMA linha por luta e a forma isolada perdia para o controle (o druida
    # terminava o dia com as 2 formas sobrando). Variante "+forma" de cada linha: a magia no round 1 e a forma (ação
    # bônus no mesmo turno) com os ataques nos rounds seguintes (0,75 quando a linha lançou uma magia).
    fb = fl[0]
    def forma(l, fb=fb):
        lanca = l['id'] != 'principal'
        l['corpo'] = dict(fb['corpo']); l['controle'] = dict(l.get('controle', {}), atencao=fb['controle']['atencao'])
        if 'fontes' not in l['controle']: l['controle']['fontes'] = fb['controle']['fontes']
        d = json.loads(json.dumps(fb['dano']))
        for x in d.get('ataques', []) + d.get('com_save', []): x['n'] = round(x['n'] * (0.75 if lanca else 1.0), 3)
        l['dano'] = d
        return l
    f = fatia(L, M(-1, 2, 2, 1, w, -1), ('int', 'sab'), 16, pv, cant, cd, atk, w, 'conjurador', False, (L + 1) // 2,
              ctrl=ctrl, areas=[ice_knife(cd)] + ([wall_fire(cd)] if L >= 7 else []), extras=fl[1:], forma_var=("+forma", forma, 1))
    if L >= 10:                                                   # mesma variante com o Fire Elemental (2 usos)
        el = fl[1]
        for l in [x for x in f['linhas'] if x['id'] in ('controle', 'controle-barato', 'area')]:
            v = forma(json.loads(json.dumps(l)), fb=el); v['id'] = l['id'] + '+elemental'; v['herda'] = 'principal'
            v['hipotese'] = l.get('hipotese', l['id']) + ' + Fire Elemental (Elemental Wild Shape)'
            g = dict(l.get('gasta', {})); g['forma_selvagem'] = 2; v['gasta'] = g
            f['linhas'].append(v)
    f['_texto'] = f"Druid {L}; Sab {10 + 2 * w}; forma de combate: " + ("Dire Wolf" if L < 6 else "tigre" if L < 9 else "escorpião") + (" ou Fire Elemental" if L >= 10 else "") + "."
    F[L] = f
emit('rpgbot-druid-moon', 'moon', 'Circle of the Moon Druid (RPGBot: Moon Sailor)',
     "Druid (Moon), Halfling Robusto (Custom Origin), gibão de peles + escudo; Telekinetic 4 (Sab 18), Sab 20 (8)",
     {"resumo": "Druida da lua que luta transformado: Wild Shape como ação bônus em formas de CR alto, com os PV da forma por cima dos seus.",
      "estrategia": "Lutas importantes em forma de combate (Dire Wolf, tigre, escorpião, Fire Elemental a partir do 10); fora da forma, Produce Flame, Entangle/Hold Person e Healing Word.",
      "nao_modelado": "Derrubar/agarrar das formas; Hold Person seguido de ataques automáticos críticos; Deinonychus; reverter para a 2ª forma na mesma luta; Lucky e Brave; Telekinetic; Flaming Sphere, Tidal Wave; Stoneskin; Primal Strike (resistência)."}, F)


# ---------- Land (Grassland): "Wise Old Owl" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 4 else 4 if L < 8 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    esp = wiz.espacos(L, L, mage_armor=False)                     # Natural Recovery = Arcane Recovery (ceil(nível/2), até 5º)
    cant = (lambda n, L=L, atk=atk: thorn_whip(L, atk, n)) if L < 4 else (lambda n, L=L, atk=atk: produce_flame(L, atk, n))
    ctrl = [ENT(cd), HP(cd)] + ([POLY(cd)] if L >= 7 else [])
    s = maior(esp); sb = min(s, 6)
    inv = dict(i=summon_beast(sb, atk), slot=sb)
    extras = []
    if L >= 5:
        extras.append(dict(id="haste", hipotese="Haste (Grassland) no melhor marcial do grupo + truques",
                           dano=cant(0.75), suporte={"fontes": [{"nome": "Haste (ataque extra num aliado)", "lado": "of", "modelo": "ataque_extra", "alvos": 1, "concentracao": "haste"}]},
                           gasta={"espacos": {"3": 1}}))
    f = fatia(L, M(-1, 3, 2, -1, w, -1), ('int', 'sab'), 16 if L < 5 else 17, hpcalc([8] * L, 2), cant, cd, atk, w,
              'conjurador', False, (L + 1) // 2, esp=esp, ctrl=ctrl, areas=[erupting(cd)] if L >= 6 else [], inv=inv, extras=extras)
    f['_texto'] = f"Druid {L} (Land: Grassland); Sab {10 + 2 * w}; Natural Recovery somado ao pool; Summon Beast no {sb}º."
    F[L] = f
emit('rpgbot-druid-land', 'land', 'Circle of the Land Druid (RPGBot: Wise Old Owl)',
     "Druid (Land, Grassland), Owlin, couro → couro batido + escudo; Telekinetic 4 (Sab 18), Sab 20 (8)",
     {"resumo": "Druida conjurador de controle e invocação: Entangle, Hold Person, Summon Beast, Haste do círculo e Natural Recovery.",
      "estrategia": "Thorn Whip/Produce Flame; Entangle ou Hold Person nas lutas de controle; Summon Beast de 1 hora; Haste no marcial.",
      "nao_modelado": "Wild Companion (coruja dando Help); Faerie Fire; Spike Growth e combos de arrastar (Thorn Whip, Telekinetic); Invisibility e Pass Without Trace; Maelstrom; Wall of Stone; voo do Owlin; Goodberry."}, F)


# ---------- Shepherd: "Little Bo-Peep, the GOAT" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 4 else 4 if L < 8 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    cant = lambda n, L=L, atk=atk: thorn_whip(L, atk, n)
    frac = round(1 / LPDC, 3)
    hawk = {"nome": "Spirit Totem: Hawk (vantagem em 1 ataque aliado por round, reação)", "lado": "of", "modelo": "vantagem",
            "alvos": 1, "fracao": round(0.5 * frac, 3), "nota": f"1 dos ~2 ataques do aliado × {frac} das lutas (1/descanso curto)"}
    ms = 2 if L >= 6 else 0                                       # Mighty Summoner: +2 PV por dado de vida
    if L < 5: inv = dict(i=summon_beast(2, atk), slot=2)
    elif L < 9: inv = dict(i={"nome": "Conjure Animals (8 lobos)", "quantidade": 8, "pv": 11 + 2 * ms, "ca": 13,
                              "ataque": {"n": 1, "bonus": 4, "dano": "2d4+2"}}, slot=3)
    else: inv = dict(i={"nome": "Conjure Elemental (Earth Elemental)", "quantidade": 1, "pv": 126 + 8 * ms, "ca": 17,
                        "ataque": {"n": 2, "bonus": 8, "dano": "2d8+5"}}, slot=5)
    bear = {"nome": "Spirit Totem: Bear (PV temporários)", "lado": "def", "modelo": "pv_temporario", "usos_descanso_curto": 1, "alvos": 3, "pv": 5 + L}
    extras = [dict(id="totem-urso", hipotese="Spirit Totem (Bear) no lugar do Hawk + invocação", dano=cant(0.75),
                   invocacoes=[inv['i']], suporte={"fontes": [bear]}, gasta={"espacos": {str(inv['slot']): 0.5}})]
    f = fatia(L, M(-1, 3, 2, 0, w, -1), ('int', 'sab'), 16, hpcalc([8] * L, 2), cant, cd, atk, w, 'conjurador', False,
              (L + 1) // 2, ctrl=[ENT(cd), HP(cd)], sup=[hawk], inv=inv, extras=extras)
    f['_texto'] = f"Druid {L} (Shepherd); Sab {10 + 2 * w}; invocação: {inv['i']['nome']}" + ("; Mighty Summoner" if L >= 6 else "") + "."
    F[L] = f
emit('rpgbot-druid-shepherd', 'shepherd', 'Circle of the Shepherd Druid (RPGBot: Little Bo-Peep, the GOAT)',
     "Druid (Shepherd), Sátiro, couro + escudo; Fey Touched 4 (Sab 18), Sab 20 (8)",
     {"resumo": "Druida invocador: Summon Beast, Conjure Animals (8 lobos) e Conjure Elemental, reforçados pelo Mighty Summoner, com Spirit Totem como ação bônus.",
      "estrategia": "Invocação de 1 hora nas lutas que importam; Spirit Totem (Hawk) para vantagem nos ataques do grupo, Bear para PV temporários; Thorn Whip para puxar inimigos.",
      "nao_modelado": "Unicorn Spirit (cura em área em cada magia de cura) e Guardian Spirit; ataques mágicos do Mighty Summoner; PV temporários do Bear nas invocações; Conjure Woodland Beings; Faithful Summons; Fey Touched (Misty Step, Sleep); resistência a magia do Sátiro."}, F)


# ---------- Spores: "Tortle Druid" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 4 else 4 if L < 8 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    halo = "1d4" if L < 6 else "1d6" if L < 10 else "1d8"
    def cant(n, L=L, atk=atk, w=w, cd=cd, halo=halo, se=False):
        d = {"ataques": [{"n": n, "bonus": atk, "dano": f"1d8+{w}" + ("+1d6" if se else ""), "nota": "Shillelagh (bordão)" + (" + Symbiotic Entity" if se else "")}],
             "com_save": [{"n": 0.75, "cd": cd, "save": "Con", "dano": halo if not se else halo.replace("1d", "2d"), "meio": False,
                           "nota": "Halo of Spores (reação, alvo a 10 pés)" + (" dobrado" if se else "")}]}
        return d
    def simb(l, L=L, cant=cant):
        n = l['dano']['ataques'][0]['n'] if 'ataques' in l['dano'] else 0.75
        l['dano'] = cant(n, se=True); l['corpo'] = {"pvt_luta": 4 * L}
        return l
    livres = [thunderclap(L, cd)] if L >= 4 else []
    ctrl = [ENT(cd), HP(cd)] + ([POLY(cd)] if L >= 7 else [])
    f = fatia(L, M(0, 1, 2, 1, w, -1), ('int', 'sab'), 19, hpcalc([8] * L, 2), cant, cd, atk, w, 'frontliner', True,
              (L + 1) // 2, ctrl=ctrl, livres=livres, reac=None, forma_var=("+simbionte", simb, 1))
    f['_texto'] = f"Druid {L} (Spores); Tortle (CA 17) + escudo; Sab {10 + 2 * w}; Halo of Spores {halo}."
    F[L] = f
emit('rpgbot-druid-spores', 'spores', 'Circle of Spores Druid (RPGBot: Tortle Druid)',
     "Druid (Spores), Tortle, escudo, Shillelagh; Sab 18 (4), Sab 20 (8); Resilient Con 12",
     {"resumo": "Druida de corpo a corpo com Shillelagh e Halo of Spores na reação; Symbiotic Entity (Wild Shape) dá 4 PV temporários por nível e dobra os esporos.",
      "estrategia": "Symbiotic Entity antes das lutas, bordão com Shillelagh e esporos como reação; Thunderclap contra grupos; Entangle/Hold Person quando precisa controlar.",
      "nao_modelado": "Ação para ativar a Symbiotic Entity e Shillelagh (ação bônus) no 1º round; Fungal Infestation; Spreading Spores; Fungal Body; Chill Touch; Thorn Whip; Spike Growth, Warding Wind, Healing Spirit, Guardian of Nature, Giant Insect."}, F)


# ---------- Stars: "Elephant Brain Energy" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 4 else 4; c = 3 if L < 8 else 4; p = prof(L); cd = 8 + p + w; atk = p + w
    gb = {"n": round(p / 4, 2), "bonus": atk, "dano": "4d6", "nota": "Guiding Bolt grátis (PB/dia ÷ 4 lutas; vantagem seguinte não modelada)"}
    def cant(n, L=L, atk=atk, gb=gb):
        d = produce_flame(L, atk, n); d["ataques"] = d["ataques"] + [dict(gb)]; return d
    arq = {"n": 1.0, "bonus": atk, "dano": f"{'2d8' if L >= 10 else '1d8'}+{w}", "nota": "Starry Form: Archer (ação bônus)"}
    def estrela(l, arq=arq):
        l['dano'] = dict(l['dano']); l['dano']['ataques'] = list(l['dano'].get('ataques', [])) + [dict(arq)]; return l
    sup = [{"nome": "Cosmic Omen (±1d6 por reação)", "lado": "of", "modelo": "bonus_por_uso", "bonus": 3.5, "usos_luta": round(p / 4, 2)}] if L >= 6 else []
    ctrl = [ENT(cd), HP(cd)] + ([POLY(cd)] if L >= 7 else [])
    f = fatia(L, M(-1, 0, c, 2, w, -1), ('int', 'sab') + (('con',) if L >= 8 else ()), 14 + c, hpcalc([8] * L, c), cant, cd, atk, w,
              'conjurador', False, (L + 1) // 2, ctrl=ctrl, areas=[wall_fire(cd)] if L >= 7 else [], sup=sup,
              forma_var=("+estrelas", estrela, 1))
    f['_texto'] = f"Druid {L} (Stars); Loxodon (CA 12 + Con) + escudo; Sab {10 + 2 * w}; Con {10 + 2 * c}" + (" (Resilient)" if L >= 8 else "") + "."
    F[L] = f
emit('rpgbot-druid-stars', 'stars', 'Circle of Stars Druid (RPGBot: Elephant Brain Energy)',
     "Druid (Stars), Loxodon (armadura natural 12 + Con), escudo; Sab 18 (4), Resilient Con 8",
     {"resumo": "Druida das estrelas que atira com a Starry Form (Archer) como ação bônus junto das magias, com Guiding Bolt grátis e Cosmic Omen.",
      "estrategia": "Starry Form (Archer) em toda luta relevante; Produce Flame e Guiding Bolt; Entangle, Hold Person, Polymorph e Wall of Fire.",
      "nao_modelado": "Chalice (cura extra) e Dragon (piso 10 na concentração); trocar de constelação (Twinkling Constellations); Full of Stars; Faerie Fire, Spike Growth, Pass Without Trace, Maelstrom, Wall of Stone; vantagem do Guiding Bolt."}, F)


# ---------- Wildfire: "Gamera" ----------
F = {}
for L in FATIAS:
    dl = L if L < 5 else L - 1                                   # Cleric 1 (Arcana) no personagem 5
    w = 3 if dl < 8 else 4; p = prof(L); cd = 8 + p + w; atk = p + w; mel = p + 3
    eb = "+1d8" if dl >= 6 else ""
    if L < 5: cant = lambda n, mel=mel: {"ataques": [{"n": n, "bonus": mel, "dano": "1d6+3", "nota": "lança"}]}
    else: cant = lambda n, L=L, mel=mel, eb=eb: {"ataques": [{"n": n, "bonus": mel, "dano": f"1d6+3+{'1d8' if L < 11 else '2d8'}{eb}", "nota": "Green-Flame Blade (lança)" + (" + Enhanced Bond" if eb else "")}]}
    esp_ = {"nome": "Wildfire Spirit", "quantidade": 1, "pv": 5 + 5 * dl, "ca": 13,
            "ataque": {"n": 1, "bonus": atk, "dano": f"1d6+{p}"}}
    def espirito(l, esp_=esp_):
        l['invocacoes'] = [esp_] + [x for x in l.get('invocacoes', [])]; return l
    ea = "+4" if eb else ""                                      # Enhanced Bond na área: média 4,5 arredondada para baixo (o parser de área só aceita bônus fixo)
    areas = [area_sp("Burning Hands", 2, "3d6" + ea, cd, 1)] + ([wall_fire(cd, ea)] if dl >= 7 else []) + \
            ([area_sp("Flame Strike", 2, "8d6" + ea, cd, 5)] if dl >= 9 else [])
    sup = [{"nome": "Cauterizing Flames (cura na reação)", "lado": "def", "modelo": "cura", "usos_luta": round(p / 4, 2), "pv": 11 + w}] if dl >= 10 else []
    cura = {"nome": "Healing Word (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
            "acao": "bonus", "usos_luta": 1, "pv": round(2.5 + w + (4.5 if eb else 0), 2)}
    f = fatia(L, M(3, -1, 3, -1, w, -1), ('int', 'sab'), 19, hpcalc([8] * L, 3), cant, cd, atk, w, 'frontliner', True,
              (L + 1) // 2, ctrl=[ENT(cd), HP(cd)], areas=areas, sup=sup, forma_var=("+espirito", espirito, 0.5))
    # Healing Word com Enhanced Bond: troca a fonte padrão (mesmo custo).
    for l in f['linhas']:
        if 'suporte' in l:
            l['suporte']['fontes'] = [cura if x.get('modelo') == 'cura_na_luta' else x for x in l['suporte']['fontes']]
    f['_texto'] = f"Druid {dl}" + (" / Cleric 1 (Arcana)" if L >= 5 else "") + f"; Tortle (CA 17) + escudo; Sab {10 + 2 * w}" + ("; Enhanced Bond" if eb else "") + "."
    F[L] = f
emit('rpgbot-druid-wildfire', 'wildfire', 'Circle of Wildfire Druid (RPGBot: Gamera)',
     "Druid (Wildfire) / Cleric 1 (Arcana, personagem 5), Tortle, lança + escudo; War Caster 4; Sab 18 (personagem 9)",
     {"resumo": "Druida do fogo selvagem de linha de frente: lança com Green-Flame Blade, Wildfire Spirit (Wild Shape, 1 hora) atirando como ação bônus, magias de fogo com Enhanced Bond.",
      "estrategia": "Espírito invocado antes ou no início da luta; Green-Flame Blade de lança; Burning Hands, Wall of Fire e Flame Strike; Healing Word potencializado.",
      "nao_modelado": "Fiery Teleport (área e reposicionamento); dano secundário do Green-Flame Blade; Booming Blade; magias saindo do espírito; Create Bonfire; Scorching Ray, Flaming Sphere, Plant Growth, Fire Shield, Aura of Life; Blazing Revival; ação bônus disputada entre o espírito e Healing Word."}, F)


# ---------- Dreams: "Lucidity" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 4 else 4 if L < 8 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    cant = lambda n, L=L, atk=atk: produce_flame(L, atk, n)
    balm = {"nome": "Balm of the Summer Court (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
            "acao": "bonus", "usos_luta": 1, "pv": float(2 * L),
            "nota": "pool de L d6/dia; ~2 usos/dia (P_CAIDO × 4 lutas), cada um com L/2 dados: 3,5 + 1 PV temporário por dado"}
    ctrl = [ENT(cd), HP(cd)] + ([POLY(cd)] if L >= 7 else [])
    f = fatia(L, M(-1, 2, 3, 0, w, -1), ('int', 'sab'), 16, hpcalc([8] * L, 3), cant, cd, atk, w, 'conjurador', False,
              (L + 1) // 2, ctrl=ctrl, areas=[area_sp("Thunderwave", 2, "2d8", cd, 1)] + ([wall_fire(cd)] if L >= 7 else []),
              reac=("Shield (Githzerai, 1/dia)", "shield", 0.25), cura=balm)
    f['_texto'] = f"Druid {L} (Dreams); Githzerai; Sab {10 + 2 * w}; Balm of the Summer Court {L}d6/dia."
    F[L] = f
emit('rpgbot-druid-dreams', 'dreams', 'Circle of Dreams Druid (RPGBot: Lucidity)',
     "Druid (Dreams), Githzerai (Shield 1/dia), gibão de peles + escudo; Chef 4 (Sab 18), Sab 20 (8)",
     {"resumo": "Druida curandeiro de retaguarda: Balm of the Summer Court (cura a distância como ação bônus, sem espaço) no lugar do Healing Word.",
      "estrategia": "Produce Flame e magias de controle; Balm para levantar aliados caídos; Polymorph e Wall of Fire no 7.",
      "nao_modelado": "Hearth of Moonlight and Shadow; Hidden Paths (10); Chef; Aura of Vitality; Faerie Fire, Spike Growth, Pass Without Trace; Absorb Elements; PV temporários do Balm somados à cura."}, F)
