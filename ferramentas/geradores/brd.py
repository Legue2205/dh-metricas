"""Bard (passada 1 cega, 21/11): Lore, Valor, Whispers, Creation (builds do RPGBot) + Eloquence, Glamour, Swords, Spirits
(bardo base do handbook + recursos da subclasse, como o Peace do Cleric). Convenções no relatório da sessão (seção Bard).
Rodar da raiz do repo; depois `python -m dh expandir`."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import wiz
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dh.premissas import P as _P
P_CAIDO = _P('suporte.h.P_CAIDO')
MIX = _P('suporte.mix_dado_multiuso')
from wiz import SL, prof, k, merge, U, area_sp, area_pico, AT, hpcalc, M, escrever, controle_fonte

B = 'https://rpgbot.net/dnd5/characters/classes/bard/subclasses/'
URL = {'lore': B + 'lore/', 'valor': B + 'valor/', 'whispers': B + 'college-of-whispers/', 'creation': B + 'creation/',
       'eloquence': B + 'eloquence/', 'glamour': B + 'glamour/', 'swords': B + 'college-of-swords/', 'spirits': B + 'college-of-spirits/'}
COM_BUILD = ('lore', 'valor', 'whispers', 'creation')
NOTA = "Build exemplo do guia de subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."
wiz.FONTE = lambda slug: {"tipo": "rpgbot", "url": URL[slug],
                          "nota": NOTA if slug in COM_BUILD else "Sem build no handbook colado: bardo base (Meio-Elfo, Des 16, "
                          "Con 14, Car 17) + recursos da subclasse. Passada 1 cega."}
FATIAS = (3, 5, 7, 9, 11)


def dado(L): return 3.5 if L < 5 else 4.5 if L < 10 else 5.5           # Bardic Inspiration d6/d8/d10
def dstr(L): return 'd6' if L < 5 else 'd8' if L < 10 else 'd10'
def usos_bi(L, car): return round(car / 4 if L < 5 else car / 2, 3)    # por luta: Car/descanso longo (4 lutas); Font of Inspiration (5): Car/curto (2 lutas)
def vm(L, cd, n): return {"com_save": [{"n": n, "cd": cd, "save": "Sab", "dano": f"{k(L)}d4", "meio": False, "nota": "Vicious Mockery"}]}
DEF_MIX = {"ca", "save_dano", "save_critico", "counterspell"}   # usos do dado que poupam PV/turnos do aliado


def BI(L, u, nota='', mix=None):
    f = {"nome": f"Bardic Inspiration ({dstr(L)}){nota}", "lado": "of", "modelo": "dado_multiuso", "dado_medio": dado(L), "usos_luta": round(u, 3)}
    if mix:
        f["mix"] = mix
        if set(mix) <= DEF_MIX: f["lado"] = "def"   # P1.3 (22/11): Cutting Words e afins protegem o aliado
    return f
HYP = lambda cd: U("Hypnotic Pattern", "hypnotic_pattern", cd, 3, area=True)
FEAR = lambda cd: U("Fear", "fear", cd, 3, area=True)
WEB = lambda cd: U("Web", "web", cd, 2, area=True)
EBT = lambda cd: U("Evard's Black Tentacles", "evards_black_tentacles", cd, 4, area=True)
PK = lambda cd: U("Phantasmal Killer", "phantasmal_killer", cd, 4)
HM = lambda cd: U("Hold Monster", "hold_monster", cd, 5)
SYN_C = lambda cd: U("Synaptic Static", "synaptic_static", cd, 5, area=True)
SHAT = lambda cd, extra='': area_sp("Shatter", 2, "3d8" + extra, cd, 2)
SYN = lambda cd: area_sp("Synaptic Static", 4, "8d6", cd, 5)


def maior(esp): return max(int(s) for s, q in esp.items() if q > 0)


def fatia(L, mods, ca, pv, cant, cd, atk, car, sup=(), ctrl=(), areas=(), greater_inv=False, hw=True, extras=(), defesa=None,
          outros=None, profs=('des', 'car'), arma_buff=None, inv=None):
    p = prof(L); sv = {kk: mods[kk] + (p if kk in profs else 0) for kk in mods}
    corpo = dict(ca=ca, pv=pv, saves=dict(sv=sv, conjurador=True))
    esp = dict(SL[L]); top = maior(esp)
    rec = {"espacos": esp}
    if outros: rec["outros"] = dict(outros)
    def S(*fs): return {"fontes": list(sup) + list(fs)}
    base_ctl = {"atencao": AT(False, 'conjurador'), "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}
    L_ = []
    def ln(id_, dn, **kw):
        l = {"id": id_, "dano": dn}; l.update(kw)
        if id_ != 'principal': l.setdefault('herda', 'principal')
        L_.append(l)
    ln("principal", cant(1.0), controle=base_ctl, defesa=defesa or {}, saves={}, area=[], invocacoes=[], suporte=S())
    if ctrl:
        t = max(o['slot'] for o in ctrl)
        ln("controle", cant(0.75), controle={"atencao": AT(False, 'conjurador'), "fontes": [controle_fonte(list(ctrl))]},
           gasta={"espacos": {str(t): 1}})
        b = min(ctrl, key=lambda o: o['slot'])
        if b['slot'] < t:   # convenção dos conjuradores: `controle-barato` = a opção mais barata da lista
            ln("controle-barato", cant(0.75), controle={"atencao": AT(False, 'conjurador'), "fontes": [b['f']]},
               gasta={"espacos": {str(b['slot']): 1}})
    if areas:
        ap, sp = area_pico(list(areas), esp); g = {}
        for x in sp: g[str(x)] = g.get(str(x), 0) + 1
        ln("area", cant(0.5 if len(ap) > 1 else 0.75), area=ap, gasta={"espacos": g})
    if greater_inv and top >= 4:
        # Greater Invisibility num aliado de frente: ataques dele com vantagem + ataques contra ele com desvantagem (1 minuto = 1 luta).
        ln("invisibilidade", cant(0.75), suporte=S({"nome": "Greater Invisibility (aliado: vantagem)", "lado": "of", "modelo": "vantagem",
                                                    "alvos": 1, "fracao": 1.0, "concentracao": "greater_invisibility"},
                                                   {"nome": "Greater Invisibility (aliado: desvantagem contra)", "lado": "def",
                                                    "modelo": "desvantagem_contra", "alvos": 1}),
           gasta={"espacos": {"4": 1}})
    if arma_buff:
        ln(arma_buff['id'], arma_buff['dano'], gasta={"espacos": arma_buff['gasta']})
    if inv:
        ln("invocacao", cant(0.75), invocacoes=[inv['i']], gasta={"espacos": inv['gasta']})
    for x in extras:
        x = dict(x); x.setdefault('herda', 'principal'); L_.append(x)
    if hw:   # Healing Word na luta (convenção do Cleric, passada 3): distância + ação bônus; gasta 1º × P_CAIDO por luta
        h = {"nome": "Healing Word (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
             "acao": "bonus", "usos_luta": 1, "pv": round(2.5 + car, 2)}
        for l in L_:
            if 'suporte' in l and not any(f.get('modelo') == 'cura_na_luta' for f in l['suporte']['fontes']):
                l['suporte'] = {"fontes": l['suporte']['fontes'] + [h]}
            g = dict(l.get('gasta', {})); e = dict(g.get('espacos', {})); e["1"] = round(e.get("1", 0) + P_CAIDO, 3)
            g['espacos'] = e; l['gasta'] = g
    return dict(corpo=corpo, recursos=rec, linhas=L_)


def emit(id_, slug, nome, build, desc, F):
    for L in FATIAS:
        for l in F[L]['linhas']:
            if l['id'] != 'principal': l.setdefault('hipotese', l['id'])
    escrever(id_, slug, nome, build, desc, F)


def chassi(L):
    """Bardo base (Meio-Elfo): Des 16, Con 14, Car 17 → 18 (4) → 20 (8)."""
    car = 3 if L < 4 else 4 if L < 8 else 5; p = prof(L)
    return dict(car=car, p=p, cd=8 + p + car, atk=p + car, mods=M(-1, 3, 2, 0, 0, car), pv=hpcalc([8] * L, 2))


# ---------- Lore: "The Sorcerer's Apprentice" ----------
F = {}
for L in FATIAS:
    c = chassi(L); car, cd = c['car'], c['cd']
    u = usos_bi(L, car)
    # Cutting Words (3): reação que tira o dado de um ataque/dano inimigo contra um aliado depois de ver a rolagem.
    # Mesmo pool de dados: metade como Bardic Inspiration (mix padrão), metade como Cutting Words (só o uso "CA").
    sup = [BI(L, u / 2), BI(L, u / 2, ' como Cutting Words', mix={"ca": 1.0})]
    ctrl = ([WEB(cd)] if L >= 6 else []) + ([PK(cd)] if L >= 7 else []) + ([SYN_C(cd)] if L >= 9 else [])
    areas = [SHAT(cd)] + ([SYN(cd)] if L >= 9 else [])
    f = fatia(L, c['mods'], 15, c['pv'], lambda n, L=L, cd=cd: vm(L, cd, n), cd, c['atk'], car, sup=sup, ctrl=ctrl, areas=areas,
              greater_inv=True)
    f['_texto'] = f"Bard {L}; Car {10 + 2 * car}; BI {dstr(L)} × {car}" + ("; Web/Counterspell (Additional Magical Secrets)" if L >= 6 else "") + "."
    F[L] = f
emit('rpgbot-bard-lore', 'lore', "College of Lore Bard (The Sorcerer's Apprentice)",
     "Bard (Lore): Meio-Elfo, For 8 Des 16 Con 14 Int 12 Sab 8 Car 17; Skill Expert (4, Car 18); Car 20 (8); couro batido",
     {"resumo": "Bardo generalista de retaguarda: controle (Web, Phantasmal Killer), Shatter/Synaptic Static, Greater Invisibility e Cutting Words.",
      "estrategia": "Inspiração e Cutting Words dividindo o pool; uma magia de controle ou área por luta; Healing Word para levantar caídos.",
      "nao_modelado": "Silvery Barbs, Counterspell, Dissonant Whispers, Sleep, Bane, Enemies Abound, Psychic Lance, Mass Suggestion, "
                      "Destructive Wave (10); desvantagem do Vicious Mockery; Peerless Skill; Song of Rest; perícias."}, F)

# ---------- Valor: "Another Gish for the Pile" ----------
F = {}
for L in FATIAS:
    car = 3 if L < 4 else 4; p = prof(L); cd = 8 + p + car; dex = 3
    arq = 2 if L >= 8 else 0; atk = p + dex + arq; n = 1 if L < 6 else 2
    def bow(r, L=L, atk=atk, n=n, extra=''):
        return {"ataques": [{"n": n * r, "bonus": atk, "dano": f"1d8+{dex}{extra}", "elven_accuracy": L >= 4, "nota": "arco longo"}]}
    u = usos_bi(L, car)
    sup = [BI(L, u, ' (Combat Inspiration: também dano/CA do aliado)')]
    ctrl = ([HYP(cd), FEAR(cd)] if L >= 5 else []) + ([HM(cd)] if L >= 9 else [])
    areas = [SHAT(cd)] + ([SYN(cd)] if L >= 9 else [])
    buff = None
    if L >= 10:   # Holy Weapon (Magical Secrets, 10): +2d8 por acerto, 1 hora = 0,5 espaço de 5º por luta
        buff = dict(id="arma-sagrada", dano=bow(1.0, extra='+2d8'), gasta={"5": 0.5})
    f = fatia(L, M(-1, dex, 3, -1, -1, car), 18, hpcalc([8] * L, 3), bow, cd, atk, car, sup=sup, ctrl=ctrl, areas=areas,
              greater_inv=True, arma_buff=buff, profs=('des', 'car'))
    f['_texto'] = f"Bard {L}; Des 16, Car {10 + 2 * car}; peitoral + escudo; arco longo" + (" com Extra Attack" if L >= 6 else "") + \
                  ("; Archery (Fighting Initiate)" if L >= 8 else "") + "."
    F[L] = f
emit('rpgbot-bard-valor', 'valor', 'College of Valor Bard (Another Gish for the Pile)',
     "Bard (Valor): Meio-Elfo, For 8 Des 16 Con 16 Int 8 Sab 8 Car 17; Elven Accuracy (4, Car 18); Fighting Initiate Archery (8); peitoral + escudo; arco longo",
     {"resumo": "Bardo arqueiro de armadura média e escudo: arco com Extra Attack, controle de área e Combat Inspiration.",
      "estrategia": "Arco nos rounds livres; Hypnotic Pattern/Fear ou Hold Monster por luta; Holy Weapon no próprio arco a partir do 10.",
      "nao_modelado": "Faerie Fire (vantagem para Elven Accuracy), Sleep, Silvery Barbs, Dispel Magic, Dimension Door, Summon Celestial, "
                      "Mass Suggestion; Battle Magic (14); Combat Inspiration de dano/CA além do mix padrão do dado."}, F)

# ---------- Whispers: "Master Spy" ----------
F = {}
for L in FATIAS:
    car = 3 if L < 4 else 4; p = prof(L); cd = 8 + p + car; dex = 3; atk = p + dex
    pb = 2 if L < 5 else 3 if L < 10 else 5
    u = usos_bi(L, car)
    # Psychic Blades: mesmo pool da inspiração; metade dos dados no dano (1× por turno no acerto), metade como inspiração.
    def xb(r, L=L, cd=cd, atk=atk, pb=pb, u=u):
        d = {"ataques": [{"n": r, "bonus": atk, "dano": f"1d8+{dex}", "nota": "besta leve"}],
             "por_luta": [{"usos": round(u / 2, 3), "dano": f"{pb}d6", "nota": "Psychic Blades (metade dos dados de inspiração)"}]}
        return d
    f = fatia(L, M(-1, dex, 1, -1, 1, car), 15, hpcalc([8] * L, 1), xb, cd, atk, car, sup=[BI(L, u / 2)], hw=False)
    f['_texto'] = f"Bard {L}; Des 16, Car {10 + 2 * car}; Psychic Blades {pb}d6; sem magia de combate modelada."
    F[L] = f
emit('rpgbot-bard-whispers', 'whispers', 'College of Whispers Bard (Master Spy)',
     "Bard (Whispers): Changeling, For 8 Des 16 Con 13 Int 8 Sab 12 Car 17; Actor (4, Car 18); Skill Expert (8, Car 19); couro batido; besta leve",
     {"resumo": "Espião e face: quase nenhuma magia de combate; besta leve com Psychic Blades.",
      "estrategia": "Besta e Psychic Blades no combate; inspiração para os aliados.",
      "nao_modelado": "Sleep, Charm Person, Calm Emotions, Invisibility, Dimension Door, Psychic Lance, Mass Suggestion; Words of Terror, "
                      "Mantle of Whispers, Shadow Lore; utilidade social (o foco do guia)."}, F)

# ---------- Creation: "Autognomes, Roll Out!" ----------
F = {}
for L in FATIAS:
    car = 3 if L < 4 else 4; p = prof(L); cd = 8 + p + car; atk = p + car
    con = 2 if L < 8 else 3
    u = usos_bi(L, car); d = dado(L)
    # Mote of Potential: rider em cima do uso comum do dado (não divide o pool). Partes do mix padrão: ataque → trovão do dado
    # em ~1,5 criaturas a 5 pés; save → PV temporários (dado + Car).
    p_atq = MIX['acerto'] + MIX['dano']; p_save = MIX['save_dano'] + MIX['save_critico']
    sup = [BI(L, u),
           {"nome": "Mote of Potential (ataque: trovão em volta do alvo)", "lado": "of", "modelo": "valor_por_luta",
            "usos_luta": round(u * p_atq, 3), "valor": round(d * 1.5, 2)},
           {"nome": "Mote of Potential (save: PV temporários)", "lado": "def", "modelo": "pv_temporario",
            "usos_luta": round(u * p_save, 3), "pv": round(d + car, 2)}]
    ctrl = ([HYP(cd)] if L >= 5 else []) + ([HM(cd)] if L >= 9 else []) + ([EBT(cd)] if L >= 10 else [])
    areas = ([SHAT(cd)] if L < 10 else []) + ([SYN(cd)] if L >= 10 else [])
    inv = None
    if L >= 6:   # Animating Performance: Dancing Item 1 hora (2 lutas), 1/dia grátis, depois espaço de 3º → 0,25 espaço de 3º por luta
        inv = dict(i={"nome": "Dancing Item (Animating Performance)", "quantidade": 1, "pv": 10 + 5 * L, "ca": 16,
                      "ataque": {"n": 0.5, "bonus": atk, "dano": f"1d10+{p}"}}, gasta={"3": 0.25})
    extras = []
    f = fatia(L, M(-1, 3, con, -1, -1, car), 16, hpcalc([8] * L, con), lambda n, L=L, cd=cd: vm(L, cd, n), cd, atk, car, sup=sup,
              ctrl=ctrl, areas=areas, greater_inv=True, inv=inv, profs=('des', 'car') + (('con',) if L >= 8 else ()))
    f['_texto'] = f"Bard {L}; Car {10 + 2 * car}; Armored Casing 16" + ("; Dancing Item" if L >= 6 else "") + ("; Resilient (Con)" if L >= 8 else "") + "."
    F[L] = f
emit('rpgbot-bard-creation', 'creation', 'College of Creation Bard (Autognomes, Roll Out!)',
     "Bard (Creation): Autognomo, For 8 Des 16 Con 15 Int 8 Sab 8 Car 17; Fey Touched (4, Car 18, Bless/Misty Step); Resilient Con (8)",
     {"resumo": "Bardo de suporte com pet: Mote of Potential nos dados, Dancing Item a partir do 6, Hypnotic Pattern e Hold Monster.",
      "estrategia": "Inspiração com os riders do Mote; Dancing Item no início do dia; uma magia de controle ou área por luta.",
      "nao_modelado": "Bless (Fey Touched), Aid, Silvery Barbs, Sleep, Polymorph em aliado, Counterspell, Eyebite; aura do Dancing Item "
                      "(Irrepressible Dance); Performance of Creation; Mote em testes."}, F)


# ---------- bardo base + subclasse (sem build colada) ----------
def base_bardo(L, c, sup, extras=(), ca=15, cant=None, ctrl_cd=0, areas_extra='', defesa=None, outros=None):
    cd = c['cd']
    ctrl = ([HYP(cd + ctrl_cd)] if L >= 5 else []) + ([HM(cd + ctrl_cd)] if L >= 9 else [])
    areas = [SHAT(cd, areas_extra)] + ([SYN(cd)] if L >= 9 else [])
    cant = cant or (lambda n, L=L, cd=cd: vm(L, cd, n))
    return fatia(L, c['mods'], ca, c['pv'], cant, cd, c['atk'], c['car'], sup=sup, ctrl=ctrl, areas=areas, greater_inv=True,
                 extras=extras, defesa=defesa, outros=outros)

BASE_BUILD = "Bard base: Meio-Elfo, For 8 Des 16 Con 14 Int 10 Sab 10 Car 17; Car 18 (4), Car 20 (8); couro batido"
BASE_NM = "Silvery Barbs, Counterspell, Faerie Fire, Sleep, Dissonant Whispers, Mass Suggestion; desvantagem do Vicious Mockery; Song of Rest."

# Eloquence: Unsettling Words (3) = ação bônus + 1 dado: o alvo subtrai o dado do próximo save → CD efetiva +dado na linha de
# controle (o dado sai do pool de inspiração). Unfailing Inspiration (6): `volta_se_falhar` (passada 2). Infectious (14): fora.
F = {}
for L in FATIAS:
    c = chassi(L); u = usos_bi(L, c['car']); d = dado(L)
    uw = min(1.0, u); cd_mais = round(d * uw)
    bi = BI(L, max(0.0, u - uw))
    if L >= 6: bi['volta_se_falhar'] = True; bi['nome'] += ' + Unfailing Inspiration'   # passada 2 (21/11)
    f = base_bardo(L, c, [bi], ctrl_cd=cd_mais)
    f['_texto'] = f"Bard {L}; Car {10 + 2 * c['car']}; Unsettling Words antes da magia de controle (CD +{cd_mais})."
    F[L] = f
emit('rpgbot-bard-eloquence', 'eloquence', 'College of Eloquence Bard (bardo base)', BASE_BUILD,
     {"resumo": "Bardo base com Unsettling Words antes do save-or-suck.",
      "estrategia": "Unsettling Words (ação bônus) e Hypnotic Pattern/Hold Monster no mesmo turno; o resto dos dados como inspiração.",
      "nao_modelado": "Silver Tongue, Universal Speech, Infectious Inspiration; " + BASE_NM}, F)

# Glamour: Mantle of Inspiration (3) = ação bônus + 1 dado: PV temporários (5/8/11) em até Car aliados (régua: 3) → pv_temporario.
# Mantle of Majesty (6): Command como ação bônus todo round, 1 minuto, 1/descanso longo → linha própria (alvo único, 1º).
F = {}
for L in FATIAS:
    c = chassi(L); u = usos_bi(L, c['car']); cd = c['cd']
    um = min(1.0, u); pvt = 5 if L < 5 else 8 if L < 10 else 11
    sup = [BI(L, max(0.0, u - um)),
           {"nome": "Mantle of Inspiration (PV temporários)", "lado": "def", "modelo": "pv_temporario", "alvos": min(3, c['car']),
            "usos_luta": round(um, 3), "pv": pvt}]
    extras = []; outros = None
    if L >= 6:
        outros = {"majestade": {"qtd": 1, "volta": "longo", "valor": 3}}
        extras = [dict(id="majestade", hipotese="Mantle of Majesty: Command (ação bônus) todo round + truque",
                       dano=vm(L, cd, 1.0),
                       controle={"atencao": AT(False, 'conjurador'),
                                 "fontes": [{"tipo": "alvo_unico", "nome": "Mantle of Majesty (Command todo round)", "cd": cd,
                                             "slots": [1, 1, 1, 1], "magias": ["command"], "modo": "combinar"}]},
                       gasta={"majestade": 1})]
    f = base_bardo(L, c, sup, extras=extras, outros=outros)
    f['_texto'] = f"Bard {L}; Car {10 + 2 * c['car']}; Mantle of Inspiration ({pvt} PV temp.)" + ("; Mantle of Majesty" if L >= 6 else "") + "."
    F[L] = f
emit('rpgbot-bard-glamour', 'glamour', 'College of Glamour Bard (bardo base)', BASE_BUILD,
     {"resumo": "Bardo base com Mantle of Inspiration (PV temporários no grupo) e Mantle of Majesty (Command todo round).",
      "estrategia": "Mantle of Inspiration no início da luta; Mantle of Majesty numa luta por dia; Hypnotic Pattern/Hold Monster.",
      "nao_modelado": "Reposicionamento do Mantle of Inspiration; Enthralling Performance; Unbreakable Majesty (14); "
                      "auto-falha do Command em encantado; " + BASE_NM}, F)

# Swords: Dueling (rapier 1d8+2+Des), Extra Attack (6), cota de escamas sem escudo (CA 16), Blade Flourish com metade dos
# dados (dano do dado 1× por turno no acerto; Defensive/Slashing: só o dano do dado).
F = {}
for L in FATIAS:
    c = chassi(L); u = usos_bi(L, c['car']); d = dado(L); p = c['p']; dex = 3; n = 1 if L < 6 else 2
    atk = p + dex
    def rap(r, L=L, atk=atk, n=n, u=u):
        return {"ataques": [{"n": n * r, "bonus": atk, "dano": f"1d8+{dex + 2}", "nota": "rapieira (Dueling)"}],
                "por_luta": [{"usos": round(u / 2, 3), "dano": f"1{dstr(L)}", "nota": "Blade Flourish (metade dos dados)"}]}
    f = base_bardo(L, c, [BI(L, u / 2)], ca=16, cant=rap)
    f['_texto'] = f"Bard {L}; Des 16, Car {10 + 2 * c['car']}; rapieira com Dueling" + ("; Extra Attack" if L >= 6 else "") + "."
    F[L] = f
emit('rpgbot-bard-swords', 'swords', 'College of Swords Bard (bardo base)',
     "Bard (Swords) base: Meio-Elfo, For 8 Des 16 Con 14 Car 17; Car 18 (4), Car 20 (8); cota de escamas; rapieira (Dueling)",
     {"resumo": "Bardo de corpo a corpo leve: rapieira com Dueling, Extra Attack e Blade Flourish.",
      "estrategia": "Rapieira nos rounds livres com Blade Flourish; Hypnotic Pattern/Hold Monster; metade dos dados como inspiração.",
      "nao_modelado": "CA do Defensive Flourish, alvos extras do Slashing Flourish, Mobile Flourish, Master's Flourish (14); "
                      "linha de frente (atenção) igual ao conjurador; " + BASE_NM}, F)

# Spirits: Spiritual Focus (6): +1d6 no dano do Shatter (a única magia de área do bardo base que usa foco). Tales from Beyond:
# aleatório, não modelado (o guia diz para guardar fora de combate).
F = {}
for L in FATIAS:
    c = chassi(L); u = usos_bi(L, c['car'])
    f = base_bardo(L, c, [BI(L, u)], areas_extra='+3.5' if L >= 6 else '')
    f['_texto'] = f"Bard {L}; Car {10 + 2 * c['car']}" + ("; Spiritual Focus (+1d6 no Shatter)" if L >= 6 else "") + "."
    F[L] = f
emit('rpgbot-bard-spirits', 'spirits', 'College of Spirits Bard (bardo base)', BASE_BUILD,
     {"resumo": "Bardo base com Spiritual Focus; Tales from Beyond é aleatório.",
      "estrategia": "Como o bardo base; Shatter com o d6 extra a partir do 6.",
      "nao_modelado": "Tales from Beyond (aleatório), Guiding Whispers, Spirit Session, Mystical Connection; " + BASE_NM}, F)
