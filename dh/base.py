"""Tabelas e funções comuns a todos os eixos (D&D 5e 2014).

Tudo o que é premissa compartilhada mora aqui, uma vez só: medianas de CR do Monster Manual, perfis de
comportamento, topologias, orçamento de XP do DMG, montagem de encontros e a rampa de letras.
Antes estas tabelas estavam copiadas em control_enc.py, control_atencao.py e no patch do Jamal/Virgil.
"""
from functools import lru_cache

import numpy as np

R = 4  # rounds por luta em todos os eixos

# CR: (CA, HP, save fraco, save forte, ataque, dano por round) — medianas do Monster Manual
CRT = {0: (12, 2.5, -2.5, 0.5, 3, 1.5), 0.125: (13, 10, -1.5, 1.5, 3, 4), 0.25: (13, 14.5, -1.5, 1.5, 4, 5.5),
       0.5: (13, 21.5, -1.5, 1.5, 4, 8), 1: (14, 32, -1.6, 1.6, 5, 14.5), 2: (14, 49, -0.6, 2.6, 5, 20),
       3: (15, 66, -0.7, 2.7, 5, 25.5), 4: (15, 83, 0.3, 3.7, 6, 31.5), 5: (15, 100, 0.3, 3.8, 6, 37.5),
       6: (16, 117, 1.2, 4.8, 7, 43.5), 7: (16, 134, 1.2, 4.9, 7, 49), 8: (16, 151, 2.1, 5.9, 8, 54.5),
       9: (17, 168, 2.1, 6.0, 8, 60.5), 10: (17, 184.5, 3.0, 7.0, 9, 66.5), 11: (17, 201, 3.0, 7.1, 9, 72.5),
       12: (17, 218, 3.9, 8.1, 10, 78), 13: (18, 235, 3.9, 8.2, 10, 83.5), 14: (18, 252, 4.8, 9.2, 11, 89.5),
       15: (18, 269, 4.8, 9.3, 11, 95.5), 16: (19, 286, 4.7, 9.3, 12, 101.5), 17: (19, 303, 5.7, 10.4, 12, 107)}

# Perfis (aba Comportamento): fração que quer a backline, malícia (0–3), corpo a corpo
PERFIL = {
    'Instintivo': (0.2, 0, True), 'Fera': (0.3, 1, True), 'Oportunista': (0.7, 2, True),
    'Soldado disciplinado': (0.5, 2, True), 'Atirador': (0.0, 3, False), 'Cavaleiro noviço': (0.1, 1, True),
    'Veterano defensor': (0.3, 2, True), 'Veterano agressor': (0.8, 2, True),
    'Conjurador tático': (0.0, 3, False), 'Comandante': (0.2, 3, True), 'Chefe (perfil próprio)': (0.4, 2, True),
}

# Topologias: peso, multiplicador de alvos em área, quem passa no alcance do tank, alcance da Miau,
# fator do Plant Growth, multiplicador de alvos do Wall of Force
TOPO = {
    'Campo aberto': dict(peso=0.25, area=0.8, cruza=0.3, alc_miau=0.10, pg=1.0, wall=1.0),
    'Ruínas ou cidade': dict(peso=0.35, area=1.0, cruza=0.6, alc_miau=0.15, pg=1.0, wall=1.0),
    'Sala de dungeon': dict(peso=0.40, area=1.2, cruza=0.9, alc_miau=0.60, pg=0.5, wall=1.5),
}
TOPOS = list(TOPO)

SAVE_TIPO = {'For': 1, 'Con': 1, 'Des': 0.5, 'Int': 0, 'Sab': 0, 'Car': 0}
H = dict(lr_n=1, lr_cr=10, chefe_save=2)


def n_ataques(cr):
    return 1 if cr <= 1 else 2 if cr <= 4 else 3 if cr <= 16 else 4


def p_acerto(bonus, ca, adv=0):
    p = min(0.95, max(0.05, (21 - (ca - bonus)) / 20))
    return 1 - (1 - p) ** 2 if adv > 0 else (p * p if adv < 0 else p)


def criatura(cr, papel, perfil, solo):
    ca, hp, fr, fo, atk, dn = CRT[cr]
    wb, mal, melee = PERFIL[perfil]
    return dict(cr=cr, papel=papel, perfil=perfil, ca=ca, hp=hp, fr=fr, fo=fo, atk=atk, dn=dn, wb=wb, mal=mal,
                melee=melee, sb=H['chefe_save'] if solo else 0,
                lr=H['lr_n'] if (solo and cr >= H['lr_cr']) else 0)


def save(c, atr):
    t = SAVE_TIPO[atr]
    return c['fr'] + (c['fo'] - c['fr']) * t + c['sb']


# ---------------- encontros (orçamento Difícil do DMG para 4 personagens) ----------------
BUD = {1: 300, 2: 600, 3: 900, 4: 1500, 5: 3000, 6: 3600, 7: 4400, 8: 5600, 9: 6400, 10: 7600, 11: 9600,
       12: 12000, 13: 13600, 14: 15200, 15: 17200, 16: 19200, 17: 23600, 18: 25200, 19: 29200, 20: 34000}
XP = {0: 10, 0.125: 25, 0.25: 50, 0.5: 100, 1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800, 6: 2300, 7: 2900,
      8: 3900, 9: 5000, 10: 5900, 11: 7200, 12: 8400, 13: 10000, 14: 11500, 15: 13000, 16: 15000, 17: 18000}
TIPOS = [('Minions + minibosses', 0.25, [('Minion', 'Oportunista', 4, .25), ('Bruiser', 'Fera', 1, .25),
                                         ('Tank inimigo', 'Veterano defensor', 1, .25),
                                         ('Conjurador', 'Conjurador tático', 1, .25)]),
         ('Party de elite', 0.15, [('Bruiser', 'Veterano agressor', 1, .25), ('Tank inimigo', 'Veterano defensor', 1, .25),
                                   ('Artilheiro', 'Atirador', 1, .25), ('Conjurador', 'Conjurador tático', 1, .25)]),
         ('Horda + chefe', 0.15, [('Minion', 'Soldado disciplinado', 6, .5), ('Chefe', 'Comandante', 1, .5)]),
         ('Horda', 0.10, [('Minion', 'Oportunista', 6, 1.0)]),
         ('Dupla', 0.05, [('Bruiser', 'Fera', 1, .5), ('Conjurador', 'Conjurador tático', 1, .5)]),
         ('Chefe sozinho', 0.30, [('Chefe', 'Chefe (perfil próprio)', 1, 1.0)])]
PESO_TIPO = {t: p for t, p, _ in TIPOS}
NIVEIS_TESTE = [1, 3, 4, 5, 7, 8, 10, 11, 13, 16]  # níveis do rank absoluto


def mult(n):
    return 1 if n == 1 else 1.5 if n == 2 else 2 if n <= 6 else 2.5 if n <= 10 else 3 if n <= 14 else 4


@lru_cache(maxsize=None)
def _encontro(tipo, L):
    _, comp = next((p, c) for t, p, c in TIPOS if t == tipo)
    b = BUD[L]; n = sum(q for _, _, q, _ in comp); m = mult(n); raw = b / m; crs = sorted(XP)

    def maxcr(x): return max([c for c in crs if XP[c] <= x] or [0])
    if tipo == 'Horda':
        picks = [(p, pf, q, maxcr(raw / q)) for p, pf, q, fr in comp]
    else:
        picks = [(p, pf, q, maxcr(raw * fr / q)) for p, pf, q, fr in comp]

        def total(pk): return sum(XP[c] * q for _, _, q, c in pk) * m
        mudou = True
        while mudou:
            mudou = False
            for i, (p, pf, q, c) in enumerate(picks):
                j = crs.index(c)
                if j + 1 < len(crs):
                    t = picks[:i] + [(p, pf, q, crs[j + 1])] + picks[i + 1:]
                    if total(t) <= b: picks = t; mudou = True; break
    return tuple(tuple(sorted(criatura(c, p, pf, tipo == 'Chefe sozinho').items()))
                 for p, pf, q, c in picks for _ in range(q))


def encontro(tipo, L):
    """Lista de criaturas (dicts novos a cada chamada, para ninguém alterar o cache)."""
    return [dict(c) for c in _encontro(tipo, L)]


# ---------------- rampa de letras (igual em todos os eixos) ----------------
RAMPA = [('E', 0.5), ('D', 1), ('C-', 3), ('C', 4), ('C+', 5), ('B-', 6), ('B', 7), ('B+', 8),
         ('A-', 10), ('A', 11), ('A+', 13), ('S', 16)]
ORDEM = ['F'] + [r for r, _ in RAMPA]


def letra(nivel_eq):
    if nivel_eq is None: return '-'
    out = 'F'
    for r, lim in RAMPA:
        if nivel_eq >= lim - 1e-9: out = r
    return out


def interp_degraus(x, limiares, niveis):
    """Interpolação usada nas planilhas: abaixo do 1º degrau é proporcional (0,5 × x / t1);
    acima do último extrapola com a última inclinação, até 20."""
    t, lv = list(limiares), list(niveis); n = len(t)
    k = next((i for i, ti in enumerate(t) if x < ti), n)  # degraus passados
    if k == 0: return 0.5 * x / t[0]
    if k == n: return min(20.0, lv[-1] + (x - t[-1]) / (t[-1] - t[-2]) * (lv[-1] - lv[-2]))
    return lv[k - 1] + (x - t[k - 1]) / (t[k] - t[k - 1]) * (lv[k] - lv[k - 1])


# ---------------- eixos compostos do painel ----------------
def defesa_fisica(defesa, resiliencia):
    """2/3 Defesa (blindagem/durabilidade) + 1/3 Resiliência. Sem saves cadastrados: só a Defesa."""
    if defesa is None: return None
    return defesa if resiliencia is None else (2 * defesa + resiliencia) / 3


def defesa_magica(vontade, resiliencia):
    """2/3 Vontade + 1/3 Resiliência. Sem saves cadastrados: sem nota."""
    if vontade is None: return None
    return vontade if resiliencia is None else (2 * vontade + resiliencia) / 3
