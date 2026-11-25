"""Paladin (passada 1, 21/11 mutirão): as 8 builds do RPGBot com página (Oathbreaker sem build colada).
Rodar da raiz: python ferramentas/geradores/pal.py && python -m dh expandir progressoes/rpgbot-paladin-*.json
Convenções: calibracao/convencoes-passada1.md + seção Paladin no relatório do mutirão (relatorio-paladin.md)."""
import sys, math
sys.path.insert(0, 'ferramentas/geradores')
import marcial
from marcial import *
marcial.CLASSE = 'paladin'

FULL = {1: {"1": 2}, 2: {"1": 3}, 3: {"1": 4, "2": 2}, 4: {"1": 4, "2": 3}, 5: {"1": 4, "2": 3, "3": 2},
        6: {"1": 4, "2": 3, "3": 3}}
OA = [{"uso": "ataque de oportunidade", "fracao": 0.5, "eixos": ["dano", "controle"]}]


def k(L): return 1 + (L >= 5) + (L >= 11)       # escala de truque pelo nível de personagem
def esp_pal(pal, extra_cl=0):
    cl = pal // 2 if extra_cl else math.ceil(pal / 2)   # multiclasse: metade arredondada para baixo
    e = dict(FULL.get(cl + extra_cl, {}))
    return e


def smite_d(s): return f"{min(s, 4) + 1}d8"


def sup_base(pal, cha):
    s = []
    if pal >= 6: s.append({"nome": "Aura of Protection", "lado": "def", "modelo": "aura_saves", "bonus": cha})
    s.append({"nome": "Lay on Hands (levanta um caído; pool ÷ 4 lutas)", "lado": "def", "modelo": "cura_na_luta",
              "alcance": "toque", "acao": "acao", "usos_luta": 1, "pv": round(5 * pal / 4, 2)})
    return s


def saves_pal(L, m, pal, cha, profs=('sab', 'car'), **kw):
    s = sv(L, m, profs)
    if pal >= 6: s = {kk: v + max(cha, 1) for kk, v in s.items()}       # Aura of Protection em si mesmo
    return dict(sv=s, conjurador=True, **kw)


def BLESS(): return {"nome": "Bless", "lado": "of", "modelo": "bonus_continuo", "alvos": 3, "bonus": 2.5, "concentracao": "bless"}


def montar(L, pal, atk, corpo, esp, cha, papel='tank', smite=True, extras=(), outros=None, controle_extra=(),
           area=None, smite_extra=None, sup_extra=(), bless=True):
    """atk(bonus=0, frac=1.0, vant=0.0, dano_extra='') -> dict de dano (ataques e afins) da linha.
    extras: linhas da subclasse (dicts de `linha`); cada uma ganha a variante '+smite' (2 smites de 1º) se smite."""
    sup = sup_base(pal, cha) + list(sup_extra)
    rec = {"espacos": esp, "outros": dict(outros or {})}
    base_ctl = ctrl(papel, controle_extra)
    def mk(id_, hip, dano, gasta=None, **kw):
        kw.setdefault('controle', base_ctl)
        su = kw.pop('suporte', None)
        l = linha(id_, hip, dano, kw.pop('defesa', {}), papel=papel, gasta=gasta,
                  suporte=sup + list(su or []), **kw)
        if papel != 'atirador' and 'reacao' not in l: l['reacao'] = OA
        return l
    L_ = [mk('principal', 'só armas, sem gastar espaço', atk())]
    if smite:
        for s in sorted(esp):
            if esp[s] >= 2:
                d = atk(); d['por_luta'] = [{"usos": 2, "dano": smite_d(int(s)), "nota": f"Divine Smite ({s}º) ×2"}]
                L_.append(mk(f'smite-{s}', f'2 Divine Smites de {s}º na luta', d, gasta={"espacos": {s: 2}}))
    if bless and esp:
        L_.append(mk('bless', 'Bless no round 1 (ação), ataques nos rounds 2–4', atk(frac=0.75),
                     gasta={"espacos": {"1": 1}}, suporte=[BLESS()]))
        # 25/11 (usuário): o paladino de mesa conjura Bless E continua dando smite com o resto dos espaços
        if smite and esp.get("1", 0) >= 3:
            d = atk(frac=0.75); d['por_luta'] = [{"usos": 2, "dano": smite_d(1), "nota": "Divine Smite (1º) ×2"}]
            L_.append(mk('bless+smite', 'Bless no round 1 (ação) + 2 Divine Smites de 1º nos rounds 2–4', d,
                         gasta={"espacos": {"1": 3}}, suporte=[BLESS()]))
    for x in extras:
        x = dict(x); g = x.pop('gasta', None)
        l = mk(x.pop('id'), x.pop('hip'), x.pop('dano'), gasta=g, **x); L_.append(l)
        if smite and esp.get("1", 0) >= 2 + (g or {}).get('espacos', {}).get('1', 0):
            v = json.loads(json.dumps(l)); v['id'] += '+smite'; v['hipotese'] += ' + 2 Divine Smites de 1º'
            v['dano'].setdefault('por_luta', []).append({"usos": 2, "dano": "2d8", "nota": "Divine Smite (1º) ×2"})
            gg = dict(v.get('gasta', {})); e = dict(gg.get('espacos', {})); e["1"] = e.get("1", 0) + 2
            gg['espacos'] = e; v['gasta'] = gg; L_.append(v)
    if area:
        for l in L_: l['area'] = list(area)
    return dict(corpo=corpo, recursos=rec, linhas=L_)


def canal(pal, p): return {"canal": {"qtd": 1, "volta": "curto", "valor": math.ceil(p / 2)}} if pal >= 3 else {}


# ---------------------------------------------------------------- Vengeance (Deep Striker)
def vengeance(L):
    pal = L; P = pb(L); s = 3 if L < 5 else 4; cha = 3; con = 2 if L < 9 else 3
    m = M(s, -1, con, -1, -1, cha); b = P + s; n = 1 if L < 5 else 2; ex = '+1d8' if L >= 11 else ''
    ca = 18 if L < 7 else 20
    profs = ('sab', 'car') + (('con',) if L >= 9 else ())
    def atk(bonus=0, frac=1.0, vant=0.0, de='', ba=1.0):
        a = [A(n * frac, b + bonus, '1d6', s + 2, ex + de, vantagem=vant, nota="lança (Dueling)"),
             A(ba, b + bonus, '1d4', s + 2, ex + de, vantagem=vant, nota="cabo (Polearm Master, ação bônus)"),
             A(0.5, b + bonus, '1d6', s + 2, ex + de, nota="ataque de oportunidade (Polearm Master, reação em 50%)")]
        return {"ataques": a}
    cd = 8 + P + cha
    ext = [dict(id='voto', hip='Vow of Enmity (ação bônus no round 1): vantagem contra o alvo a luta toda',
                dano=atk(vant=1.0, ba=0.75), gasta={"canal": 1}),
           dict(id='marca', hip="Hunter's Mark (1 hora: 0,5 espaço de 1º por luta; ação bônus no round 1)",
                dano=atk(de='+1d6', ba=0.75), gasta={"espacos": {"1": 0.5}})]
    if L >= 5:
        ext.append(dict(id='controle', hip='Hold Person no round 1 (ação), ataques nos rounds 2–4',
                        dano=atk(frac=0.75), gasta={"espacos": {"2": 1}},
                        controle=ctrl('tank', [{"tipo": "alvo_unico", "nome": "Hold Person", "cd": cd, "slots": [2],
                                                 "magias": ["hold_person"], "modo": "melhor"}])))
    if L >= 9:   # Passada 2: Haste (magia de juramento do 9) em si, como no Glory
        ext.append(dict(id='haste', hip='Haste em si (3º) no round 1 (ação): +1 ataque e +2 de CA nos rounds 2–4',
                        dano={"ataques": [dict(a, n=round(a['n'] * 0.75 + (0.75 if i == 0 else 0), 4)) if i == 0 else a
                                          for i, a in enumerate(atk()['ataques'])]},
                        defesa={"ca": ca + 2}, gasta={"espacos": {"3": 1}}))
    esp = esp_pal(pal)
    fat = montar(L, pal, atk, dict(ca=ca, pv=hp([10] * L, con), saves=saves_pal(L, m, pal, cha, profs, ataques=n + 1)),
                 esp, cha, extras=ext, outros=canal(pal, P))
    fat['_texto'] = {3: "Variant Human (Polearm Master); lança + escudo, Dueling; cota de malha + escudo (18).",
                     5: "For 18 (4); Extra Attack; Hold Person/Misty Step.", 7: "Placas (20); Relentless Avenger.",
                     9: "Resilient Con (8); magias de 3º.", 11: "Improved Divine Smite."}[L]
    return fat


# ---------------------------------------------------------------- Devotion (Curseedge: Pal 3 / Sorcerer 2 / Pal)
def devotion(L):
    pal, so = {3: (3, 0), 5: (3, 2), 7: (5, 2), 9: (7, 2), 11: (9, 2)}[L]
    P = pb(L); s = 2; cha = 3; con = 3; m = M(s, -1, con, -1, -1, cha); b = P + s
    n = 2 if pal >= 5 else 1; ex = '+1d8' if pal >= 11 else ''
    ca = 16 if L < 7 else 18
    pw = {"poder": [-5, 10]} if L >= 11 else {}
    pontos = 0 if so == 0 else (2 if L < 7 else 4)
    def atk(bonus=0, frac=1.0, vant=0.0, de='', bb_r1=0.0):
        if L >= 5 and n == 1:          # Booming Blade como ataque principal (truque do Sorcerer)
            a = [A(frac, b + bonus, '2d6', s, f'+{k(L) - 1}d8' + de, vantagem=vant, nota="Booming Blade (espadão)", **pw)]
        else:
            a = [A(n * frac, b + bonus, '2d6', s, ex + de, vantagem=vant, nota="espadão", **pw)]
        if bb_r1: a.append(A(bb_r1, b + bonus, '2d6', s, ex + f'+{k(L) - 1}d8', nota="Booming Blade acelerado no round 1", **pw))
        a.append(A(0.5, b, '2d6', s, ex, nota="ataque de oportunidade (reação em 50%)", **pw))
        return {"ataques": a}
    ext = [dict(id='arma-sagrada', hip='Sacred Weapon (ação no round 1: +Car no acerto a luta toda); '
                                       + ('Booming Blade acelerado no round 1 (2 pontos de feitiçaria)' if pontos else 'sem ataque no round 1'),
                dano=atk(bonus=cha, frac=0.75, bb_r1=0.25 if pontos else 0.0),
                gasta=dict({"canal": 1}, **({"feiticaria": 2} if pontos else {}),
                           **({"espacos": {"1": 1}} if so else {})),
                **({"defesa": {"reacoes": [{"tipo": "shield", "usos_luta": 1}]}} if so else {}))]   # Passada 2: Shield (Sorcerer 1)
    out = canal(pal, P)
    if pontos: out["feiticaria"] = {"qtd": pontos, "volta": "longo"}
    esp = esp_pal(pal, extra_cl=so)
    pv = hp([10] * pal + [6] * so, con) if so == 0 else hp([10] * 3 + [6] * 2 + [10] * (pal - 3), con)
    fat = montar(L, pal, atk, dict(ca=ca, pv=pv, saves=saves_pal(L, m, pal, cha, ataques=n)), esp, cha,
                 extras=ext, outros=out)
    fat['_texto'] = {3: "Paladin 3: Sacred Weapon; espadão, Blessed Warrior; cota de malha (16).",
                     5: "Paladin 3 / Sorcerer 2 (Wild Magic): Booming Blade, Shield, Silvery Barbs, 2 pontos de feitiçaria.",
                     7: "Paladin 5 / Sorcerer 2: Metamagic Adept (Quicken; 4 pontos), Extra Attack; placas (18).",
                     9: "Paladin 7 / Sorcerer 2: Aura of Protection, Aura of Devotion.",
                     11: "Paladin 9 / Sorcerer 2: Great Weapon Master (10); magias de 3º."}[L]
    return fat


# ---------------------------------------------------------------- Conquest (Variant Human Shield Master; Pal 8 / Warlock 2)
def conquest(L):
    pal, wl = {3: (3, 0), 5: (5, 0), 7: (7, 0), 9: (8, 1), 11: (8, 2)}[L]
    P = pb(L); s = 3 if L < 5 else 4; cha = 3 if L < 9 else 4; con = 2
    m = M(s, 0, con, -1, -1, cha); b = P + s; n = 1 if pal < 5 else 2
    ca = 18 if L < 7 else 20; cd = 8 + P + cha
    def atk(bonus=0, frac=1.0, vant=0.0, de=''):
        return {"ataques": [A(n * frac, b + bonus, '1d8', s + 2, de, vantagem=vant, nota="espada longa (Dueling)"),
                            A(0.5, b, '1d8', s + 2, '', nota="ataque de oportunidade (reação em 50%)")]}
    # Passada 2: Aura of Conquest (Paladin 7) = dano psíquico de metade do nível de paladino no começo do turno do
    # amedrontado; aproximado como com_save (Sab) no alvo principal nos rounds 2–4 (falha no save do medo).
    aoc = [{"n": 0.75, "cd": cd, "save": "Sab", "dano": str(pal // 2), "meio": False,
            "nota": "Aura of Conquest no amedrontado"}] if pal >= 7 else []
    def com_aoc(dn): return dict(dn, com_save=dn.get('com_save', []) + aoc) if aoc else dn
    ext = [dict(id='conquista', hip='Conquering Presence no round 1 (ação), ataques nos rounds 2–4',
                dano=com_aoc(atk(frac=0.75)), gasta={"canal": 1},
                controle=ctrl('tank', [{"tipo": "area", "nome": "Conquering Presence", "magia": "conquering_presence",
                                        "cd": cd, "so_corpo_a_corpo": True}])),
           dict(id='agathys', hip='Armor of Agathys (1º) antes da luta: 5 PV temporários', dano=atk(),
                defesa={"pvt_luta": 5}, gasta={"espacos": {"1": 1}})]
    if pal >= 5:
        ext.append(dict(id='arma-espiritual', hip='Spiritual Weapon (2º; ação bônus, rounds 2–4)',
                        dano={"ataques": atk()['ataques'] + [A(0.75, P + cha, '1d8', cha, nota="Spiritual Weapon")]},
                        gasta={"espacos": {"2": 1}}))
    out = canal(pal, P)
    if wl:
        out["pacto"] = {"qtd": wl, "volta": "curto"}
        out["pavor"] = {"qtd": P, "volta": "longo"}
        ext.append(dict(id='pavor', hip='Form of Dread (ação bônus no round 1): PV temporários e medo no 1º acerto de cada turno; '
                                         'smites com os espaços de pacto',
                        dano=com_aoc(dict(atk(), por_luta=[{"usos": wl, "dano": "2d8", "nota": "Divine Smite com espaço de pacto (1º)"}])),
                        defesa={"pvt_luta": 5.5 + wl}, gasta={"pavor": 1, "pacto": wl},
                        controle=ctrl('tank', [{"tipo": "condicao_no_acerto", "nome": "Form of Dread (amedrontado)",
                                                "efeito": "cond_amedrontado", "cd": cd, "bonus": [b] * n, "usos": 4}])))
    esp = esp_pal(pal, extra_cl=0) if not wl else dict(FULL[pal // 2])
    pv = hp([10] * pal + [8] * wl, con)
    fat = montar(L, pal, atk, dict(ca=ca, pv=pv, saves=saves_pal(L, m, pal, cha, ataques=n, **({"adv": ["Des"]} if False else {}))),
                 esp, cha, extras=ext, outros=out)
    fat['_texto'] = {3: "Variant Human (Shield Master); espada longa + escudo, Dueling; cota de malha + escudo (18).",
                     5: "For 18 (4); Extra Attack; Spiritual Weapon/Hold Person.", 7: "Placas (20); Aura of Conquest.",
                     9: "Paladin 8 (Car 18) / Warlock 1 (Undead): Form of Dread (PB/dia), espaço de pacto.",
                     11: "Paladin 8 / Warlock 2: Hex, Agonizing Blast, 2 espaços de pacto."}[L]
    return fat


# ---------------------------------------------------------------- Ancients (Celebrant Hunter: atirador)
def ancients(L):
    pal = L; P = pb(L); d = 3; cha = 3; con = 2; m = M(1, d, con, -1, -1, cha)
    arch = 2 if L >= 5 else 0; b = P + d + arch; n = 1 if L < 5 else 2
    arma = '1d10' if L < 5 else '1d12'
    pw = {"poder": [-5, 10]} if L >= 9 else {}
    ca = 15; cd = 8 + P + cha
    def atk(bonus=0, frac=1.0, vant=0.0, de=''):
        return {"ataques": [A(n * frac, b + bonus, arma, d, de, vantagem=vant,
                              nota=("besta pesada" if L < 5 else "mosquete (Firearms Mastery)"), **pw)]}
    esp = esp_pal(pal)
    hdp = (1 if L < 7 else 2) if L >= 3 else 0; sl = str(math.ceil(P / 2))
    esp[sl] = esp.get(sl, 0) + hdp                      # Harness Divine Power (o guia usa as opcionais; Channel vira espaço)
    ext = [dict(id='enredar', hip='Ensnaring Strike (ação bônus) no 1º acerto: impedido até escapar',
                dano=atk(), gasta={"espacos": {"1": 1}},
                controle=ctrl('atirador', [{"tipo": "alvo_unico", "nome": "Ensnaring Strike", "cd": cd, "slots": [1],
                                            "magias": ["ensnaring_strike"], "modo": "melhor"}]))]
    fat = montar(L, pal, atk, dict(ca=ca, pv=hp([10] * L, con), saves=saves_pal(L, m, pal, cha, ataques=n)),
                 esp, cha, papel='atirador', smite=False, extras=ext)
    fat['_texto'] = {3: "Giff; besta pesada, Protection; couro batido (15); Harness Divine Power 1/dia.",
                     5: "Fighting Initiate (Archery) (4); Extra Attack; mosquete.", 7: "Aura of Warding; Harness 2/dia.",
                     9: "Sharpshooter (8); magias de 3º.", 11: "Improved Divine Smite (sem uso à distância)."}[L]
    return fat


# ---------------------------------------------------------------- Crown (Bodyguard: truques com Blessed Warrior)
def crown(L):
    pal = L; P = pb(L); cha = 3 if L < 5 else 4; con = 3 if L < 9 else 4
    m = M(2, -1, con, -1, -1, cha); cd = 8 + P + cha; ca = 18 if L < 7 else 20
    profs = ('sab', 'car') + (('con',) if L >= 9 else ())
    def atk(bonus=0, frac=1.0, vant=0.0, de=''):
        return {"com_save": [{"n": frac, "cd": cd, "save": "Sab", "dano": f"{k(L)}d12", "meio": False,
                              "nota": "Toll the Dead (Blessed Warrior, alvo ferido)"}],
                "ataques": [A(0.5, P + 2, '1d8', 2, '+1d8' if L >= 11 else '', nota="ataque de oportunidade (reação em 50%)")]}
    wor = {"nome": "Word of Radiance", "tipo": "cleave_save", "dano": f"{k(L)}d6", "cd": cd, "save": "Con", "alvos": [1, 2, 3]}
    ext = []
    if L >= 9:
        ext.append(dict(id='guardioes', hip='Spirit Guardians (3º) no round 1, truque nos rounds 2–4',
                        dano=dict(atk(frac=0.75), **{}), gasta={"espacos": {"3": 1}},
                        area=[{"nome": "Spirit Guardians (3º)", "tipo": "aura", "alvos": 3, "dano": "3d8", "cd": cd, "metade": True}, wor]))
        ext[-1]['dano']['com_save'] = ext[-1]['dano']['com_save'] + [{"n": 0.75, "cd": cd, "save": "Sab", "dano": "3d8",
                                                                     "meio": True, "nota": "Spirit Guardians no alvo"}]
    esp = esp_pal(pal)
    fat = montar(L, pal, atk, dict(ca=ca, pv=hp([10] * L, con), saves=saves_pal(L, m, pal, cha, profs, ataques=1)),
                 esp, cha, smite=False, extras=ext, outros=canal(pal, P))
    for l in fat['linhas']:
        if l['id'] != 'guardioes': l['area'] = [wor]
    fat['_texto'] = {3: "Orc; Blessed Warrior (Toll the Dead, Word of Radiance); cota de malha + escudo (18).",
                     5: "Con 17 / Car 18 (4); truques com 2 dados.", 7: "Placas (20); Divine Allegiance.",
                     9: "Resilient Con (8); Spirit Guardians.", 11: "Truques com 3 dados."}[L]
    return fat


# ---------------------------------------------------------------- Glory (Athasian Gladiator)
def glory(L):
    pal = L; P = pb(L); s = 3 if L < 5 else 4; cha = 2 if L < 5 else 3; con = 3
    m = M(s, -1, con, -1, -1, cha); b = P + s; n = 1 if L < 5 else 2; ex = '+1d8' if L >= 11 else ''
    ca = 18 if L < 7 else 20; pam = L >= 9
    def atk(bonus=0, frac=1.0, vant=0.0, de='', extra_n=0.0):
        arma = '1d6' if pam else '1d8'
        a = [A(n * frac + extra_n, b + bonus, arma, s + 2, ex + de, vantagem=vant, nota="lança (Dueling)" if pam else "espada longa (Dueling)")]
        if pam: a.append(A(1.0, b + bonus, '1d4', s + 2, ex + de, vantagem=vant, nota="cabo (Polearm Master)"))
        a.append(A(0.5, b, arma, s + 2, ex, nota="ataque de oportunidade (reação em 50%)"))
        return {"ataques": a}
    ext = [dict(id='inspirador', hip='Inspiring Smite: 1 Divine Smite de 1º e 2d8 + nível de PV temporários para um aliado',
                dano=dict(atk(), por_luta=[{"usos": 1, "dano": "2d8", "nota": "Divine Smite (1º)"}]),
                gasta={"canal": 1, "espacos": {"1": 1}},
                suporte=[{"nome": "Inspiring Smite (PV temporários)", "lado": "def", "modelo": "pv_temporario",
                          "usos_luta": 1, "alvos": 1, "pv": 9 + L}])]
    if L >= 9:
        ext.append(dict(id='haste', hip='Haste em si (3º) no round 1 (ação): +1 ataque e +2 de CA nos rounds 2–4',
                        dano=atk(frac=0.75, extra_n=0.75), defesa={"ca": ca + 2}, gasta={"espacos": {"3": 1}}))
    esp = esp_pal(pal)
    fat = montar(L, pal, atk, dict(ca=ca, pv=hp([10] * L, con), saves=saves_pal(L, m, pal, cha, ('sab', 'car', 'con'), ataques=n)),
                 esp, cha, extras=ext, outros=canal(pal, P))
    fat['_texto'] = {3: "Custom Lineage (Resilient Con); espada longa + escudo, Dueling; cota de malha + escudo (18).",
                     5: "For 18 / Car 16 (4); Extra Attack.", 7: "Placas (20); Aura of Alacrity.",
                     9: "Polearm Master (8) com lança + escudo; Haste.", 11: "Improved Divine Smite."}[L]
    return fat


# ---------------------------------------------------------------- Redemption (Apostle of Peace)
def redemption(L):
    pal = L; P = pb(L); s = 2; cha = 3 if L < 5 else (4 if L < 9 else 5); con = 3
    m = M(s, -1, con, -1, -1, cha); b = P + s; cd = 8 + P + cha; ca = 18 if L < 7 else 20
    ex = '+1d8' if L >= 11 else ''
    def atk(bonus=0, frac=1.0, vant=0.0, de=''):
        oa = A(0.5, b, '1d8', s, ex, nota="ataque de oportunidade (reação em 50%)")
        if L < 5:
            return {"com_save": [{"n": frac, "cd": cd, "save": "Con", "dano": f"{k(L)}d6", "meio": False,
                                  "nota": "Word of Radiance (Blessed Warrior)"}], "ataques": [oa]}
        return {"ataques": [A(2 * frac, b + bonus, '1d8', s, ex + de, vantagem=vant, nota="espada longa"), oa]}
    wor = {"nome": "Word of Radiance", "tipo": "cleave_save", "dano": f"{k(L)}d6", "cd": cd, "save": "Con", "alvos": [1, 2, 3]}
    ext = []
    if L >= 5:
        ops = [{"tipo": "alvo_unico", "nome": "Hold Person", "cd": cd, "slots": [2], "magias": ["hold_person"], "modo": "melhor"}]
        ext.append(dict(id='controle', hip='Hold Person no round 1 (ação), ataques nos rounds 2–4', dano=atk(frac=0.75),
                        gasta={"espacos": {"2": 1}}, controle=ctrl('tank', ops)))
    if L >= 9:
        ext.append(dict(id='padrao-hipnotico', hip='Hypnotic Pattern (3º) no round 1 (ação), ataques nos rounds 2–4',
                        dano=atk(frac=0.75), gasta={"espacos": {"3": 1}},
                        controle=ctrl('tank', [{"tipo": "area", "nome": "Hypnotic Pattern", "magia": "hypnotic_pattern", "cd": cd}])))
    esp = esp_pal(pal)
    fat = montar(L, pal, atk, dict(ca=ca, pv=hp([10] * L, con), saves=saves_pal(L, m, pal, cha, ataques=1 if L < 5 else 2)),
                 esp, cha, extras=ext, outros=canal(pal, P), smite=L >= 5)
    for l in fat['linhas']: l['area'] = [wor]
    fat['_texto'] = {3: "Duergar; Blessed Warrior (Word of Radiance); espada longa + escudo; cota de malha + escudo (18).",
                     5: "Telekinetic (Car 18) (4); Extra Attack; Hold Person, Calm Emotions.",
                     7: "Placas (20); Aura of the Guardian.", 9: "Car 20 (8); Hypnotic Pattern, Counterspell.",
                     11: "Improved Divine Smite."}[L]
    return fat


# ---------------------------------------------------------------- Watchers (Invoke the Cerulean Sign)
def watchers(L):
    pal = L; P = pb(L); s = 3 if L < 5 else (4 if L < 9 else 5); cha = 3; con = 2
    m = M(s, -1, con, -1, -1, cha); b = P + s; n = 1 if L < 5 else 2; ex = '+1d8' if L >= 11 else ''
    ca = 16 if L < 7 else 18
    def atk(bonus=0, frac=1.0, vant=0.0, de=''):
        return {"ataques": [A(n * frac, b + bonus, '2d4', s, '+1.0' + ex + de, vantagem=vant, nota="cimitarra de duas lâminas (GWF +1,0)"),
                            A(1.0, b + bonus, '1d4', s, '+0.5' + ex + de, vantagem=vant, nota="outra lâmina (ação bônus)"),
                            A(0.5, b, '2d4', s, '+1.0' + ex, nota="ataque de oportunidade (reação em 50%)")]}
    esp = esp_pal(pal)
    fat = montar(L, pal, atk, dict(ca=ca, pv=hp([10] * L, con), saves=saves_pal(L, m, pal, cha, ataques=n + 1)),
                 esp, cha, outros=canal(pal, P))
    fat['_texto'] = {3: "Harengon; cimitarra de duas lâminas, Great Weapon Fighting; cota de malha (16).",
                     5: "Skill Expert (For 18) (4); Extra Attack.", 7: "Placas (18); Aura of the Sentinel.",
                     9: "For 20 (8); magias de 3º.", 11: "Improved Divine Smite."}[L]
    return fat


DESC_COMUM = "Comum: Aura of Courage, Find Steed, curas fora de luta, smite guardado para o crítico."
B = [
    ('vengeance', 'oath-of-vengeance', 'Oath of Vengeance Paladin (RPGBot: Deep Striker)',
     'Paladin (Vengeance), Variant Human, Polearm Master 1, For 18 4, Resilient Con 8; lança + escudo, Dueling', vengeance,
     {"resumo": "Atacante de linha de frente: lança com Polearm Master, Vow of Enmity e Hunter's Mark.",
      "estrategia": "Vow of Enmity no alvo principal; smites nos acertos; Hold Person quando couber.",
      "nao_modelado": "Relentless Avenger, Misty Step, Haste (concentração), Abjure Enemy, Shield of Faith; 2º guia (Bugbear) não ingerido. " + DESC_COMUM}),
    ('devotion', 'oath-of-devotion', 'Oath of Devotion Paladin (RPGBot: Curseedge)',
     'Paladin 3 / Sorcerer 2 (Wild Magic) / Paladin, Astral Elf, Metamagic Adept 6, GWM 10; espadão, Blessed Warrior', devotion,
     {"resumo": "Paladino de Sacred Weapon (+Car no acerto) com dip de Sorcerer para Booming Blade acelerado.",
      "estrategia": "Sacred Weapon no round 1 com Booming Blade acelerado; GWM a partir do 10.",
      "nao_modelado": "Shield, Silvery Barbs, Tides of Chaos (vantagem), Absorb Elements, Aura of Devotion, efeito secundário do Booming Blade. " + DESC_COMUM}),
    ('conquest', 'oath-of-conquest', 'Oath of Conquest Paladin (RPGBot: Variant Human Paladin)',
     'Paladin 8 / Warlock 2 (Undead), Variant Human, Shield Master 1, For 18 4, Car 18 8; espada longa + escudo, Dueling', conquest,
     {"resumo": "Tanque do medo: Conquering Presence, Form of Dread e Aura of Conquest; Shield Master para derrubar.",
      "estrategia": "Form of Dread no round 1 a partir do 9; Armor of Agathys; smites com os espaços de pacto.",
      "nao_modelado": "Shield Master (derrubar: disputa), Aura of Conquest, Guided Strike, Hex/Eldritch Blast, retorno do Armor of Agathys, Hellish Rebuke, Fear (Paladin 9 fora). " + DESC_COMUM}),
    ('ancients', 'oath-of-the-ancients', 'Oath of the Ancients Paladin (RPGBot: Celebrant Hunter)',
     'Paladin (Ancients), Giff, Fighting Initiate Archery 4, Sharpshooter 8; besta pesada → mosquete, Protection', ancients,
     {"resumo": "Paladino atirador: Ensnaring Strike à distância e auras para a retaguarda.",
      "estrategia": "Ensnaring Strike no primeiro acerto; Harness Divine Power converte o Channel em espaço.",
      "nao_modelado": "Protection (estilo), Aura of Warding (resistência a magia), Hippo Build/empurrão, Misty Step, Branding Smite, recarga do mosquete. " + DESC_COMUM}),
    ('crown', 'oath-of-the-crown', 'Oath of the Crown Paladin (RPGBot: The Bodyguard)',
     'Paladin (Crown), Orc, Con/Car 4, Resilient Con 8; truques com Blessed Warrior', crown,
     {"resumo": "Guarda-costas: Toll the Dead e Word of Radiance, Divine Allegiance e Champion Challenge.",
      "estrategia": "Truques à distância ao lado do protegido; Spirit Guardians a partir do 9.",
      "nao_modelado": "Divine Allegiance (absorver dano de aliado), Champion Challenge, Compelled Duel, Turn the Tide, Warding Bond, Aid, Adrenaline Rush/Relentless Endurance. " + DESC_COMUM}),
    ('glory', 'oath-of-glory', 'Oath of Glory Paladin (RPGBot: Athasian Gladiators)',
     'Paladin (Glory), Custom Lineage (Resilient Con), For 18/Car 16 4, Polearm Master 8; espada longa/lança + escudo, Dueling', glory,
     {"resumo": "Gladiador: Inspiring Smite (PV temporários), Peerless Athlete para agarrar e Haste em si.",
      "estrategia": "Inspiring Smite no 1º smite da luta; Haste a partir do 9.",
      "nao_modelado": "Peerless Athlete (agarrar/empurrar), Aura of Alacrity, +2 de CA do Haste, montaria. " + DESC_COMUM}),
    ('redemption', 'oath-of-redemption', 'Oath of Redemption Paladin (RPGBot: Apostle of Peace)',
     'Paladin (Redemption), Duergar, Telekinetic 4 (Car 18), Car 20 8; espada longa + escudo, Blessed Warrior', redemption,
     {"resumo": "Paladino de Carisma com Word of Radiance, Hold Person e Hypnotic Pattern; absorve dano dos aliados.",
      "estrategia": "Word of Radiance até o 4; depois espada; controle com magias de save.",
      "nao_modelado": "Aura of the Guardian (absorver dano de aliado), Rebuke the Violent, Emissary of Peace, Sleep, Calm Emotions, Counterspell, "
                      "Telekinetic (empurrão), magias de Duergar (Enlarge/Invisibility). " + DESC_COMUM}),
    ('watchers', 'oath-of-the-watchers', 'Oath of the Watchers Paladin (RPGBot: Invoke the Cerulean Sign)',
     'Paladin (Watchers), Harengon, Skill Expert 4 (For 18), For 20 8; cimitarra de duas lâminas, GWF', watchers,
     {"resumo": "Paladino de Força com a cimitarra de duas lâminas (ataque na ação bônus sem feat).",
      "estrategia": "Ataques e smites; Watcher's Will contra conjuradores.",
      "nao_modelado": "Watcher's Will (vantagem em saves mentais), Aura of the Sentinel (iniciativa), Abjure the Extraplanar, Counterspell. " + DESC_COMUM}),
]

if __name__ == '__main__':
    for slug, url, nome, build, fn, desc in B:
        escrever(f'rpgbot-paladin-{slug}', url, nome, build, desc, {L: fn(L) for L in NIV})
