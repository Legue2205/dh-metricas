"""Chassi do Druid (mini-mutirão 22/11): uma build sem feat por círculo do gabarito (conjurador pleno), fatias 7 e 11.
Rodar da raiz: python ferramentas/geradores/chassi_druid.py && python -m dh expandir
Peças (truques, magias, formas, fatia com Healing Word) reaproveitadas de dru.py; raça, feats e atributos do RPGBot descartados.

Régua comum (igual para os 7 círculos): Sab > Con > Des (compra padrão +2/+1), gibão de peles + escudo (CA 15),
Produce Flame, Entangle / Hold Person / Polymorph, Ice Knife + Wall of Fire, Summon Beast (1 hora) e Healing Word.
O círculo escolhe a posição (meia: Moon, Spores, Wildfire; retaguarda: os outros) e soma suas features e magias.
"""
import json
import os
import sys

sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402


def pecas_dru():
    """Executa só a parte de peças de dru.py (antes da 1ª build), sem escrever as builds do RPGBot."""
    arq = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dru.py')
    src = open(arq, encoding='utf-8').read().split('# ---------- Moon')[0]
    ns = {'__file__': arq, '__name__': 'dru_pecas'}
    exec(compile(src, arq, 'exec'), ns)
    return ns


D = pecas_dru()
ORDEM = ('sab', 'con', 'des', 'int', 'car', 'for')
PROFS = ('int', 'sab')
CA = 15                                                   # gibão de peles (12 + Des 1) + escudo
POS = dict(moon='meia', spores='meia', wildfire='meia', land='retaguarda', shepherd='retaguarda',
           stars='retaguarda', dreams='retaguarda')


def base(L):
    s = C.atributos('druid', L, ORDEM); m = C.mods(s); p = C.pb(L); w = m['sab']
    return dict(s=s, m=m, p=p, w=w, cd=8 + p + w, atk=p + w, pv=C.hp(8, L, m['con']))


def ctrl_base(cd): return [D['ENT'](cd), D['HP'](cd), D['POLY'](cd)]


def inv_base(L, atk, esp=None):
    sb = min(D['maior'](esp or D['espacos'](L)), 6)
    return dict(i=D['summon_beast'](sb, atk), slot=sb)


def montar(sub, L, b, cant, ctrl=None, areas=None, esp=None, inv=None, _t='', **kw):
    f = D['fatia'](L, b['m'], PROFS, CA, b['pv'], cant, b['cd'], b['atk'], b['w'], 'conjurador', False, (L + 1) // 2,
                   esp=esp, ctrl=ctrl or ctrl_base(b['cd']),
                   areas=areas if areas is not None else [D['ice_knife'](b['cd']), D['wall_fire'](b['cd'])],
                   inv=inv or inv_base(L, b['atk'], esp), **kw)
    for l in f['linhas']:
        a = l.get('controle', {}).get('atencao')
        if a is not None and a.get('papel') != 'tank':     # linhas da forma de combate ficam na frente (tank)
            l['controle']['atencao'] = C.atencao(POS[sub])
        if l['id'] != 'principal': l.setdefault('hipotese', l['id'])
    f['_texto'] = f"Druid {L}; atributos {b['s']}; " + _t
    return f


# ---------- círculos ----------
def moon(L, b):
    cant = lambda n: D['produce_flame'](L, b['atk'], n)
    pv = b['pv']; FL = D['forma_linha']
    if L < 9: fl = [FL(L, "Saber-Toothed Tiger", 12, 52, pv, [{"n": 1, "bonus": 6, "dano": "1d10+5", "nota": "tigre, mordida"},
                                                               {"n": 1, "bonus": 6, "dano": "2d6+5", "nota": "tigre, garra"}])]
    else: fl = [FL(L, "Giant Scorpion", 15, 52, pv, [{"n": 2, "bonus": 4, "dano": "1d8+2", "nota": "escorpião, pinças (agarra)"},
                                                      {"n": 1, "bonus": 4, "dano": "1d10+2", "nota": "escorpião, ferrão"}],
                   [{"n": 0.6, "cd": 12, "save": "Con", "dano": "4d10", "meio": True, "nota": "veneno do ferrão (≈ chance de acerto)"}])]
    if L >= 10:
        fl.append(FL(L, "Fire Elemental (Elemental Wild Shape, 2 usos)", 13, 102, pv,
                     [{"n": 2, "bonus": 6, "dano": "2d6+3", "nota": "Fire Elemental, toque (incendeia: não modelado)"}], gasto=2))

    def forma(l, fb=fl[0]):                               # mesma regra de dru.py: ×0,75 quando a linha lança magia
        lanca = l['id'] != 'principal'
        l['corpo'] = dict(fb['corpo']); l['controle'] = dict(l.get('controle', {}), atencao=fb['controle']['atencao'])
        l['controle'].setdefault('fontes', fb['controle']['fontes'])
        d = json.loads(json.dumps(fb['dano']))
        for x in d.get('ataques', []) + d.get('com_save', []): x['n'] = round(x['n'] * (0.75 if lanca else 1.0), 3)
        l['dano'] = d
        return l
    f = montar('moon', L, b, cant, extras=fl[1:], forma_var=("+forma", forma, 1),
               _t="forma de combate: " + ("tigre" if L < 9 else "escorpião ou Fire Elemental") + ".")
    if L >= 10:
        for l in [x for x in f['linhas'] if x['id'] in ('controle', 'controle-barato', 'area', 'invocacao')]:
            v = forma(json.loads(json.dumps(l)), fb=fl[1]); v['id'] = l['id'] + '+elemental'; v['herda'] = 'principal'
            v['hipotese'] = l.get('hipotese', l['id']) + ' + Fire Elemental (Elemental Wild Shape)'
            g = dict(l.get('gasta', {})); g['forma_selvagem'] = 2; v['gasta'] = g
            f['linhas'].append(v)
    return f


def land(L, b):
    esp = D['wiz'].espacos(L, L, mage_armor=False)       # Natural Recovery = Arcane Recovery
    cant = lambda n: D['produce_flame'](L, b['atk'], n)
    extras = [dict(id="haste", hipotese="Haste (Grassland) no melhor marcial do grupo + truques", dano=cant(0.75),
                   suporte={"fontes": [{"nome": "Haste (ataque extra num aliado)", "lado": "of", "modelo": "ataque_extra",
                                        "alvos": 1, "concentracao": "haste"}]}, gasta={"espacos": {"3": 1}})]
    areas = [D['ice_knife'](b['cd']), D['wall_fire'](b['cd'])] + \
        ([D['area_sp']("Insect Plague (Grassland)", 4, "4d10", b['cd'], 5)] if L >= 9 else [])
    return montar('land', L, b, cant, esp=esp, areas=areas, extras=extras,
                  _t="Grassland; Natural Recovery somado ao pool" + ("; Insect Plague." if L >= 9 else "."))


def shepherd(L, b):
    cant = lambda n: D['produce_flame'](L, b['atk'], n)
    frac = round(1 / D['LPDC'], 3)
    hawk = {"nome": "Spirit Totem: Hawk (vantagem em 1 ataque aliado por round, reação)", "lado": "of", "modelo": "vantagem",
            "alvos": 1, "fracao": round(0.5 * frac, 3), "nota": f"1 dos ~2 ataques do aliado × {frac} das lutas (1/descanso curto)"}
    bear = {"nome": "Spirit Totem: Bear (PV temporários)", "lado": "def", "modelo": "pv_temporario", "usos_descanso_curto": 1,
            "alvos": 3, "pv": 5 + L}
    ms = 2                                                # Mighty Summoner (6): +2 PV por dado de vida
    if L < 9: cj, sl = {"nome": "Conjure Animals (8 lobos, Mighty Summoner)", "quantidade": 8, "pv": 11 + 2 * ms, "ca": 13,
                        "ataque": {"n": 1, "bonus": 4, "dano": "2d4+2"}}, 3
    else: cj, sl = {"nome": "Conjure Elemental (Earth Elemental, Mighty Summoner)", "quantidade": 1, "pv": 126 + 8 * ms, "ca": 17,
                    "ataque": {"n": 2, "bonus": 8, "dano": "2d8+5"}}, 5
    inv = inv_base(L, b['atk'])
    extras = [dict(id="conjurar", hipotese=f"{cj['nome']} (1 hora) + truques", dano=cant(0.75), invocacoes=[cj],
                   gasta={"espacos": {str(sl): 0.5}}),
              dict(id="totem-urso", hipotese="Spirit Totem (Bear) no lugar do Hawk + Summon Beast", dano=cant(0.75),
                   invocacoes=[inv['i']], suporte={"fontes": [bear]}, gasta={"espacos": {str(inv['slot']): 0.5}})]
    return montar('shepherd', L, b, cant, sup=[hawk], inv=inv, extras=extras, _t=f"Mighty Summoner; {cj['nome']}.")


def spores(L, b):
    w, cd, atk = b['w'], b['cd'], b['atk']
    halo = "1d6" if L < 10 else "1d8"

    def cant(n):
        d = D['produce_flame'](L, atk, n)
        d["com_save"] = [{"n": 0.75, "cd": cd, "save": "Con", "dano": halo, "meio": False, "nota": "Halo of Spores (reação, alvo a 10 pés)"}]
        return d

    def simb(l):                                          # Symbiotic Entity: bordão com Shillelagh (+1d6) e esporos dobrados
        n = l['dano']['ataques'][0]['n'] if 'ataques' in l['dano'] else 0.75
        l['dano'] = {"ataques": [{"n": n, "bonus": atk, "dano": f"1d8+{w}+1d6", "nota": "Shillelagh (bordão) + Symbiotic Entity"}],
                     "com_save": [{"n": 0.75, "cd": cd, "save": "Con", "dano": halo.replace("1d", "2d"), "meio": False,
                                   "nota": "Halo of Spores dobrado (reação)"}]}
        l['corpo'] = {"pvt_luta": 4 * L}
        l['controle'] = dict(l.get('controle', {}), atencao=dict(C.atencao('meia'), front=True))
        return l
    ctrl = ctrl_base(cd) + [D['U']("Blindness/Deafness (Spores)", "blindness", cd, 2)]
    areas = [D['ice_knife'](cd), D['wall_fire'](cd)] + ([D['area_sp']("Cloudkill (Spores)", 3, "5d8", cd, 5)] if L >= 9 else [])
    return montar('spores', L, b, cant, ctrl=ctrl, areas=areas, forma_var=("+simbionte", simb, 1),
                  _t=f"Halo of Spores {halo}; Symbiotic Entity com bordão + Shillelagh.")


def stars(L, b):
    p, atk, w = b['p'], b['atk'], b['w']
    gb = {"n": round(p / 4, 2), "bonus": atk, "dano": "4d6", "nota": "Guiding Bolt grátis (PB/dia ÷ 4 lutas; vantagem seguinte não modelada)"}

    def cant(n):
        d = D['produce_flame'](L, atk, n); d["ataques"] = d["ataques"] + [dict(gb)]; return d
    arq = {"n": 1.0, "bonus": atk, "dano": f"{'2d8' if L >= 10 else '1d8'}+{w}", "nota": "Starry Form: Archer (ação bônus)"}

    def estrela(l):
        l['dano'] = dict(l['dano']); l['dano']['ataques'] = list(l['dano'].get('ataques', [])) + [dict(arq)]; return l
    sup = [{"nome": "Cosmic Omen (±1d6 por reação)", "lado": "of", "modelo": "bonus_por_uso", "bonus": 3.5, "usos_luta": round(p / 4, 2)}]
    return montar('stars', L, b, cant, sup=sup, forma_var=("+estrelas", estrela, 1),
                  _t="Starry Form (Archer); Guiding Bolt grátis; Cosmic Omen" + ("; Twinkling Constellations." if L >= 10 else "."))


def wildfire(L, b):
    p, w, cd, atk = b['p'], b['w'], b['cd'], b['atk']
    cant = lambda n: D['produce_flame'](L, atk, n, '+1d8')            # Enhanced Bond (6): +1d8 no dano de fogo
    esp_ = {"nome": "Wildfire Spirit", "quantidade": 1, "pv": 5 + 5 * L, "ca": 13, "ataque": {"n": 1, "bonus": atk, "dano": f"1d6+{p}"}}

    def espirito(l):
        l['invocacoes'] = [esp_] + list(l.get('invocacoes', [])); return l
    ea = "+4"                                               # Enhanced Bond na área (parser só aceita fixo), como dru.py
    areas = [D['ice_knife'](cd), D['wall_fire'](cd, ea), D['area_sp']("Burning Hands (Wildfire)", 2, "3d6" + ea, cd, 1)] + \
        ([D['area_sp']("Flame Strike (Wildfire)", 2, "8d6" + ea, cd, 5)] if L >= 9 else [])
    sup = [{"nome": "Cauterizing Flames (cura na reação)", "lado": "def", "modelo": "cura", "usos_luta": round(p / 4, 2), "pv": 11 + w}] if L >= 10 else []
    cura = {"nome": "Healing Word (levanta um caído; Enhanced Bond)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
            "acao": "bonus", "usos_luta": 1, "pv": round(2.5 + w + 4.5, 2)}
    f = montar('wildfire', L, b, cant, areas=areas, sup=sup, forma_var=("+espirito", espirito, 0.5),
               _t="Wildfire Spirit; Enhanced Bond" + ("; Cauterizing Flames." if L >= 10 else "."))
    for l in f['linhas']:                                   # Healing Word com Enhanced Bond (mesmo custo de espaço)
        if 'suporte' in l:
            l['suporte']['fontes'] = [cura if x.get('modelo') == 'cura_na_luta' else x for x in l['suporte']['fontes']]
    return f


def dreams(L, b):
    cant = lambda n: D['produce_flame'](L, b['atk'], n)
    balm = {"nome": "Balm of the Summer Court (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
            "acao": "bonus", "usos_luta": 1, "pv": float(2 * L),
            "nota": "pool de L d6/dia; ~2 usos/dia, cada um com L/2 dados: 3,5 + 1 PV temporário por dado"}
    return montar('dreams', L, b, cant, cura=balm, _t=f"Balm of the Summer Court {L}d6/dia.")


SUBS = {
    'moon': (moon, "Wild Shape de combate (ação bônus) com os PV da forma por cima dos seus; Elemental Wild Shape no 10.",
             "Derrubar/agarrar das formas; Primal Strike; reverter para a 2ª forma na mesma luta; Hold Person + ataques automáticos críticos da forma."),
    'land': (land, "Grassland (terreno da build do RPGBot): Haste e Insect Plague do círculo; Natural Recovery no pool.",
             "Land's Stride; Nature's Ward; Invisibility, Pass without Trace, Daylight, Freedom of Movement, Divination, Dream."),
    'shepherd': (shepherd, "Spirit Totem (Hawk ou Bear) e Mighty Summoner: Conjure Animals no 7 e Conjure Elemental no 11.",
                 "Unicorn Spirit; Guardian Spirit; ataques mágicos do Mighty Summoner; Bear nos PV das invocações; Faithful Summons."),
    'spores': (spores, "Halo of Spores na reação; Symbiotic Entity (Wild Shape) com bordão + Shillelagh, PV temporários e esporos dobrados.",
               "Chill Touch; Fungal Infestation; Spreading Spores; Fungal Body; Animate Dead, Gaseous Form, Blight, Confusion, Contagion; ação para ativar a Symbiotic Entity e Shillelagh."),
    'stars': (stars, "Starry Form (Archer) como ação bônus em toda luta relevante; Guiding Bolt grátis; Cosmic Omen.",
              "Chalice e Dragon; trocar de constelação; Full of Stars; vantagem do Guiding Bolt."),
    'wildfire': (wildfire, "Wildfire Spirit (1 hora) e Enhanced Bond em Produce Flame, Wall of Fire, Burning Hands, Flame Strike e Healing Word; Cauterizing Flames no 10.",
                 "Fiery Teleport; magias saindo do espírito; Cure Wounds, Flaming Sphere, Scorching Ray, Plant Growth, Revivify, Aura of Life, Fire Shield, Mass Cure Wounds; ação bônus disputada entre espírito e Healing Word."),
    'dreams': (dreams, "Balm of the Summer Court (cura a distância, ação bônus, sem espaço) no lugar do Healing Word.",
               "Hearth of Moonlight and Shadow; Hidden Paths; PV temporários do Balm somados à cura."),
}
REGUA = ("Régua comum do chassi: Sab > Con > Des, gibão de peles + escudo, Produce Flame, Entangle/Hold Person/Polymorph, "
         "Ice Knife + Wall of Fire, Summon Beast e Healing Word; sem feat (conjurador pleno).")


if __name__ == '__main__':
    for sub, (fn, res, nm) in SUBS.items():
        C.escrever('druid', sub, POS[sub], {L: fn(L, base(L)) for L in C.NIV},
                   build=f"Druid ({sub.title()}), {POS[sub]}, gibão de peles + escudo, Sab > Con > Des; sem feat",
                   desc={"resumo": f"Chassi do Circle of {sub.title()}: " + res, "estrategia": REGUA,
                         "nao_modelado": nm + " Comuns: Wild Shape fora de combate; Goodberry; Faerie Fire, Spike Growth, Moonbeam, Conjure Animals (fora do Shepherd)."},
                   url=D['URL'][sub])
