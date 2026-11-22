"""Chassi do Bard (mini-mutirão de 22/11): um chassi-bard-<colégio> por colégio do gabarito, fatias 7 e 11, só sem feat
(conjurador pleno). Regras em calibracao/convencoes-passada1.md, seções "Bard" e "Chassi".
Mesma régua: Vicious Mockery, lista base (Shatter, Hypnotic Pattern, Greater Invisibility, Hold Monster/Synaptic Static
no 9), Bardic Inspiration e Healing Word em todos. O colégio dá posição, arma/armadura e as features (números do brd.py).
Rodar da raiz: python ferramentas/geradores/chassi_bard.py && python -m dh expandir
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import chassi as C  # noqa: E402
from wiz import SL, k, U, area_sp, area_pico, controle_fonte  # noqa: E402
from dh.premissas import P as _P  # noqa: E402

P_CAIDO = _P('suporte.h.P_CAIDO')
MIX = _P('suporte.mix_dado_multiuso')
B = 'https://rpgbot.net/dnd5/characters/classes/bard/subclasses/'
URL = {'lore': B + 'lore/', 'valor': B + 'valor/', 'whispers': B + 'college-of-whispers/', 'creation': B + 'creation/',
       'eloquence': B + 'eloquence/', 'glamour': B + 'glamour/', 'swords': B + 'college-of-swords/',
       'spirits': B + 'college-of-spirits/'}
ORDEM_CAR = ('car', 'des', 'con', 'sab', 'int', 'for')   # conjurador: Car, Des, Con
ORDEM_DES = ('des', 'car', 'con', 'sab', 'int', 'for')   # Swords: a arma (Blade Flourish) antes da magia
NM_BASE = ("Silvery Barbs, Counterspell, Faerie Fire, Sleep, Dissonant Whispers, Mass Suggestion; Magical Secrets (10); "
           "desvantagem do Vicious Mockery; Song of Rest; Jack of All Trades/Expertise.")


def dado(L): return 3.5 if L < 5 else 4.5 if L < 10 else 5.5
def dstr(L): return 'd6' if L < 5 else 'd8' if L < 10 else 'd10'
def usos_bi(L, car): return round(car / 4 if L < 5 else car / 2, 3)   # por luta (Font of Inspiration no 5)


def BI(L, u, nota='', mix=None):
    f = {"nome": f"Bardic Inspiration ({dstr(L)}){nota}", "lado": "of", "modelo": "dado_multiuso",
         "dado_medio": dado(L), "usos_luta": round(u, 3)}
    if mix: f["mix"] = mix
    return f


def vm(L, cd):
    return lambda r: {"com_save": [{"n": r, "cd": cd, "save": "Sab", "dano": f"{k(L)}d4", "meio": False,
                                    "nota": "Vicious Mockery"}]}


HYP = lambda cd: U("Hypnotic Pattern", "hypnotic_pattern", cd, 3, area=True)
HM = lambda cd: U("Hold Monster", "hold_monster", cd, 5)
SHAT = lambda cd, extra='': area_sp("Shatter", 2, "3d8" + extra, cd, 2)
SYN = lambda cd: area_sp("Synaptic Static", 4, "8d6", cd, 5)
FIRE = lambda cd: area_sp("Fireball", 4, "8d6", cd, 3)


def base(L, ordem):
    s = C.atributos('bard', L, ordem); m = C.mods(s); p = C.pb(L)
    return dict(s=s, m=m, p=p, car=m['car'], des=m['des'], cd=8 + p + m['car'], atk=p + m['car'],
                pv=C.hp(8, L, m['con']))


def fatia(L, c, posicao, ca, cant, sup=(), ctrl_cd=0, areas_extra=(), shat_extra='', extras=(), inv=None,
          outros=None, texto=''):
    """Linhas-base iguais para todos os colégios; o colégio troca o ataque (cant), soma suporte/linhas extras."""
    cd = c['cd']; esp = dict(SL[L]); top = max(int(x) for x in esp)
    corpo = dict(ca=ca, pv=c['pv'], saves=dict(sv=C.sv(L, c['m'], ('des', 'car')), conjurador=True))
    rec = {"espacos": esp}
    if outros: rec["outros"] = dict(outros)
    at = C.atencao(posicao)
    def S(*fs): return {"fontes": list(sup) + list(fs)}
    def ctl(f): return {"atencao": at, "fontes": [f]}
    LS = []
    def ln(id_, dn, hip, **kw):
        l = {"id": id_, "hipotese": hip, "dano": dn}; l.update(kw)
        if LS: l['herda'] = 'principal'
        LS.append(l)
    ln("principal", cant(1.0), "só ataque/truque nos rounds", controle=ctl({"tipo": "ameaca", "nome": "Corpo (ameaça)"}),
       defesa={}, saves={}, area=[], invocacoes=[], suporte=S())
    ops = ([HYP(cd + ctrl_cd)] if L >= 5 else []) + ([HM(cd + ctrl_cd)] if L >= 9 else [])
    if ops:
        t = max(o['slot'] for o in ops)
        ln("controle", cant(0.75), "melhor magia de controle", controle=ctl(controle_fonte(ops)), gasta={"espacos": {str(t): 1}})
        b = min(ops, key=lambda o: o['slot'])
        if b['slot'] < t:
            ln("controle-barato", cant(0.75), "controle mais barato", controle=ctl(b['f']),
               gasta={"espacos": {str(b['slot']): 1}})
    areas = [SHAT(cd, shat_extra)] + ([SYN(cd)] if L >= 9 else []) + list(areas_extra)
    ap, sp = area_pico(areas, esp); g = {}
    for x in sp: g[str(x)] = g.get(str(x), 0) + 1
    ln("area", cant(0.5 if len(ap) > 1 else 0.75), "luta de pico: área", area=ap, gasta={"espacos": g})
    if top >= 4:
        ln("invisibilidade", cant(0.75), "Greater Invisibility num aliado de frente",
           suporte=S({"nome": "Greater Invisibility (aliado: vantagem)", "lado": "of", "modelo": "vantagem", "alvos": 1,
                      "fracao": 1.0, "concentracao": "greater_invisibility"},
                     {"nome": "Greater Invisibility (aliado: desvantagem contra)", "lado": "def",
                      "modelo": "desvantagem_contra", "alvos": 1}),
           gasta={"espacos": {"4": 1}})
    if inv:
        ln("invocacao", cant(0.75), inv['hip'], invocacoes=[inv['i']], gasta={"espacos": inv['gasta']})
    for x in extras:
        x = dict(x); x.setdefault('herda', 'principal'); LS.append(x)
    h = {"nome": "Healing Word (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
         "acao": "bonus", "usos_luta": 1, "pv": round(2.5 + c['car'], 2)}
    for l in LS:   # Healing Word (convenção do Cleric, passada 3) em todas as linhas
        if 'suporte' in l:
            l['suporte'] = {"fontes": l['suporte']['fontes'] + [h]}
        gg = dict(l.get('gasta', {})); e = dict(gg.get('espacos', {})); e["1"] = round(e.get("1", 0) + P_CAIDO, 3)
        gg['espacos'] = e; l['gasta'] = gg
    return dict(corpo=corpo, recursos=rec, linhas=LS, _texto=f"Bard {L}; atributos {c['s']}; CA {ca}. " + texto)


def couro(c): return 12 + c['des']   # couro batido


def emitir(sub, posicao, build, desc, fat):
    desc = dict(desc); desc['nao_modelado'] = desc.get('nao_modelado', '') + ' Todos: ' + NM_BASE
    C.escrever('bard', sub, posicao, {L: fat(L) for L in C.NIV}, build=build, desc=desc, url=URL[sub])


# ---------- Lore: Cutting Words (metade dos dados), Additional Magical Secrets (6): Fireball (+ Counterspell, não modelado)
def lore(L):
    c = base(L, ORDEM_CAR); u = usos_bi(L, c['car'])
    sup = [BI(L, u / 2), BI(L, u / 2, ' como Cutting Words', mix={"ca": 1.0})]
    return fatia(L, c, 'retaguarda', couro(c), vm(L, c['cd']), sup=sup, areas_extra=[FIRE(c['cd'])],
                 texto="Cutting Words com metade dos dados; Fireball (Additional Magical Secrets).")


# ---------- Valor: armadura média + escudo, rapieira, Extra Attack (6), Combat Inspiration no mix padrão
def valor(L):
    c = base(L, ORDEM_CAR); u = usos_bi(L, c['car']); d = min(2, c['des']); n = 2 if L >= 6 else 1
    atk = c['p'] + c['des']
    def rap(r): return {"ataques": [{"n": n * r, "bonus": atk, "dano": f"1d8+{c['des']}", "nota": "rapieira + escudo"}]}
    return fatia(L, c, 'meia', 15 + d + 2, rap, sup=[BI(L, u, ' (Combat Inspiration)')],
                 texto="meia-armadura + escudo; rapieira com Extra Attack.")


# ---------- Whispers: besta leve + Psychic Blades (metade dos dados)
def whispers(L):
    c = base(L, ORDEM_CAR); u = usos_bi(L, c['car']); pbd = 3 if L < 10 else 5; atk = c['p'] + c['des']
    def xb(r): return {"ataques": [{"n": r, "bonus": atk, "dano": f"1d8+{c['des']}", "nota": "besta leve"}],
                       "por_luta": [{"usos": round(u / 2, 3), "dano": f"{pbd}d6", "nota": "Psychic Blades (metade dos dados)"}]}
    return fatia(L, c, 'retaguarda', couro(c), xb, sup=[BI(L, u / 2)], texto=f"besta leve com Psychic Blades {pbd}d6.")


# ---------- Creation: Mote of Potential (riders no mix padrão), Dancing Item (6) = invocação, 0,25 espaço de 3º por luta
def creation(L):
    c = base(L, ORDEM_CAR); u = usos_bi(L, c['car']); d = dado(L)
    p_atq = MIX['acerto'] + MIX['dano']; p_save = MIX['save_dano'] + MIX['save_critico']
    sup = [BI(L, u),
           {"nome": "Mote of Potential (ataque: trovão em volta do alvo)", "lado": "of", "modelo": "valor_por_luta",
            "usos_luta": round(u * p_atq, 3), "valor": round(d * 1.5, 2)},
           {"nome": "Mote of Potential (save: PV temporários)", "lado": "def", "modelo": "pv_temporario",
            "usos_luta": round(u * p_save, 3), "pv": round(d + c['car'], 2)}]
    inv = dict(hip="Dancing Item (Animating Performance)",
               i={"nome": "Dancing Item (Animating Performance)", "quantidade": 1, "pv": 10 + 5 * L, "ca": 16,
                  "ataque": {"n": 0.5, "bonus": c['atk'], "dano": f"1d10+{c['p']}"}}, gasta={"3": 0.25})
    return fatia(L, c, 'retaguarda', couro(c), vm(L, c['cd']), sup=sup, inv=inv, texto="Mote of Potential; Dancing Item.")


# ---------- Eloquence: Unsettling Words (1 dado: CD +dado no controle), Unfailing Inspiration (6)
def eloquence(L):
    c = base(L, ORDEM_CAR); u = usos_bi(L, c['car']); uw = min(1.0, u); cdm = round(dado(L) * uw)
    bi = BI(L, max(0.0, u - uw), ' + Unfailing Inspiration'); bi['volta_se_falhar'] = True
    return fatia(L, c, 'retaguarda', couro(c), vm(L, c['cd']), sup=[bi], ctrl_cd=cdm,
                 texto=f"Unsettling Words antes do controle (CD +{cdm}).")


# ---------- Glamour: Mantle of Inspiration (PV temp. em até 3 aliados), Mantle of Majesty (6) = Command todo round, 1/longo
def glamour(L):
    c = base(L, ORDEM_CAR); u = usos_bi(L, c['car']); um = min(1.0, u); pvt = 8 if L < 10 else 11; cd = c['cd']
    sup = [BI(L, max(0.0, u - um)),
           {"nome": "Mantle of Inspiration (PV temporários)", "lado": "def", "modelo": "pv_temporario",
            "alvos": min(3, c['car']), "usos_luta": round(um, 3), "pv": pvt}]
    ext = [dict(id="majestade", hipotese="Mantle of Majesty: Command (ação bônus) todo round + truque", dano=vm(L, cd)(1.0),
                controle={"atencao": C.atencao('retaguarda'),
                          "fontes": [{"tipo": "alvo_unico", "nome": "Mantle of Majesty (Command todo round)", "cd": cd,
                                      "slots": [1, 1, 1, 1], "magias": ["command"], "modo": "combinar"}]},
                gasta={"majestade": 1})]
    return fatia(L, c, 'retaguarda', couro(c), vm(L, cd), sup=sup, extras=ext,
                 outros={"majestade": {"qtd": 1, "volta": "longo", "valor": 3}},
                 texto=f"Mantle of Inspiration ({pvt} PV temp.); Mantle of Majesty.")


# ---------- Swords: Des primeiro, rapieira com Dueling, Extra Attack (6), Blade Flourish com metade dos dados
def swords(L):
    c = base(L, ORDEM_DES); u = usos_bi(L, c['car']); n = 2 if L >= 6 else 1; atk = c['p'] + c['des']
    def rap(r): return {"ataques": [{"n": n * r, "bonus": atk, "dano": f"1d8+{c['des'] + 2}", "nota": "rapieira (Dueling)"}],
                        "por_luta": [{"usos": round(u / 2, 3), "dano": f"1{dstr(L)}", "nota": "Blade Flourish (metade dos dados)"}]}
    return fatia(L, c, 'skirmisher', couro(c), rap, sup=[BI(L, u / 2)],
                 texto="rapieira com Dueling, Extra Attack, Blade Flourish; couro batido (Des alta).")


# ---------- Spirits: Spiritual Focus (6): +1d6 no Shatter
def spirits(L):
    c = base(L, ORDEM_CAR); u = usos_bi(L, c['car'])
    return fatia(L, c, 'retaguarda', couro(c), vm(L, c['cd']), sup=[BI(L, u)], shat_extra='+3.5',
                 texto="Spiritual Focus (+1d6 no Shatter).")


BLD = "Bard ({}) chassi: Car 17/Des 15/Con 13 (+2/+1), Car 19 (4), Car 20 + Des 16 (8); couro batido; Vicious Mockery; sem feat"
emitir('lore', 'retaguarda', BLD.format('Lore') + "; Fireball/Counterspell no 6",
       {"resumo": "Bardo base de retaguarda com Cutting Words e Fireball por Additional Magical Secrets.",
        "nao_modelado": "Counterspell (2º segredo), Peerless Skill, perícias extras."}, lore)
emitir('valor', 'meia', "Bard (Valor) chassi: Car 17/Des 15/Con 13, Car 19 (4), Car 20 (8); meia-armadura + escudo (CA 19); "
       "rapieira com Extra Attack; sem feat",
       {"resumo": "Bardo de linha média: armadura média e escudo, rapieira com Extra Attack, magias da lista base.",
        "nao_modelado": "Combat Inspiration (dano/CA) além do mix padrão; Battle Magic (14)."}, valor)
emitir('whispers', 'retaguarda', BLD.format('Whispers') + "; besta leve",
       {"resumo": "Bardo base que troca o truque por besta leve para usar Psychic Blades.",
        "nao_modelado": "Words of Terror, Mantle of Whispers, Shadow Lore; utilidade social."}, whispers)
emitir('creation', 'retaguarda', BLD.format('Creation'),
       {"resumo": "Bardo base com Mote of Potential nos dados e Dancing Item (6).",
        "nao_modelado": "Mote em testes; Performance of Creation; aura do Dancing Item (Irrepressible Dance)."}, creation)
emitir('eloquence', 'retaguarda', BLD.format('Eloquence'),
       {"resumo": "Bardo base com Unsettling Words antes do save-or-suck e Unfailing Inspiration.",
        "nao_modelado": "Silver Tongue, Universal Speech, Infectious Inspiration (14)."}, eloquence)
emitir('glamour', 'retaguarda', BLD.format('Glamour'),
       {"resumo": "Bardo base com Mantle of Inspiration (PV temporários) e Mantle of Majesty (Command todo round, 1/dia).",
        "nao_modelado": "Reposicionamento do Mantle of Inspiration; Enthralling Performance; auto-falha do Command em encantado."},
       glamour)
emitir('swords', 'skirmisher', "Bard (Swords) chassi: Des 17/Car 15/Con 13, Des 19 (4), Des 20 + Car 16 (8); couro batido; "
       "rapieira (Dueling) com Extra Attack; sem feat",
       {"resumo": "Bardo duelista que entra e sai: rapieira com Dueling, Extra Attack e Blade Flourish; Des antes de Car.",
        "nao_modelado": "CA do Defensive Flourish, alvos extras do Slashing Flourish, Mobile Flourish (deslocamento), "
                        "Master's Flourish (14)."}, swords)
emitir('spirits', 'retaguarda', BLD.format('Spirits'),
       {"resumo": "Bardo base com Spiritual Focus; Tales from Beyond é aleatório.",
        "nao_modelado": "Tales from Beyond (aleatório), Guiding Whispers, Spirit Session, Spiritual Focus na cura."}, spirits)
