"""Defesa: Blindagem (contra horda) e Durabilidade (contra boss) — fórmula fechada.

Motor reconstruído em 03/11 (patch do Jamal/Virgil) e conferido com a planilha nas linhas de referência.
Blindagem/Durabilidade = maior CR de horda/boss que o personagem aguenta 4 rounds sem cair (busca binária).
O nível equivalente segue a aba Rampas da planilha "Ranks de defesa".
"""
from .base import interp_degraus, letra

T_DMG = [(0, 3, 0.5), (0.125, 3, 2.5), (0.25, 3, 4.5), (0.5, 3, 7), (1, 3, 11.5), (2, 3, 17.5), (3, 4, 23.5),
         (4, 5, 29.5), (5, 6, 35.5), (6, 6, 41.5), (7, 6, 47.5), (8, 7, 53.5), (9, 7, 59.5), (10, 7, 65.5),
         (11, 8, 71.5), (12, 8, 77.5), (13, 8, 83.5), (14, 8, 89.5), (15, 8, 95.5), (16, 9, 101.5),
         (17, 10, 107.5), (18, 10, 113.5), (19, 10, 119.5), (20, 10, 125.5), (21, 11, 137.5), (22, 11, 149.5),
         (23, 11, 161.5), (24, 12, 173.5)]
NIVEIS = [0.5, 1, 3, 4, 5, 6, 7, 8, 10, 11, 13, 16]
LIM_BLINDAGEM = [0.47, 0.94, 2.92, 3.75, 5.07, 5.86, 6.61, 7.33, 8.69, 10.16, 11.44, 14.21]
LIM_DURABILIDADE = [0.33, 0.66, 2.15, 2.73, 3.54, 4.05, 4.54, 5.0, 6.33, 7.39, 8.31, 10.63]


def _i(cr, k):
    for a, b in zip(T_DMG, T_DMG[1:]):
        if a[0] <= cr <= b[0]: return a[k] + (cr - a[0]) / (b[0] - a[0]) * (b[k] - a[k])
    return T_DMG[-1][k]


def _atk(bonus, ac, d, adv, resist, red, magico, F=0.6):
    p = min(0.95, max(0.05, (21 - (ac - bonus)) / 20)); c = 0.05
    if adv == 1: p, c = 1 - (1 - p) ** 2, 1 - 0.95 ** 2
    if adv == -1: p, c = p * p, 0.0025
    hit, crit = d, d * (1 + F)
    if not magico: hit, crit = max(0, hit - red), max(0, crit - red)
    if resist: hit, crit = hit / 2, crit / 2
    return (p - c) * hit + c * crit


def boss(cr, ac, adv, resist, red):
    n = 2 if cr <= 4 else (3 if cr <= 16 else 4); D = _i(cr, 2)
    return n * _atk(_i(cr, 1) + 3, ac, D / n, adv, resist, red, cr >= 10)


def horda(cr, ac, adv, resist, red):
    """Horda: o dano por round do CR dividido entre 3 e 10 atacantes de (4 + CR/2) de dano cada.
    O nº de atacantes importa para quem tem redução fixa (Heavy Armor Master): mais golpes menores = mais redução.
    (A reconstrução de 03/11 usava 4 + CR/2 atacantes e superestimava o Abdul: 10,69 em vez de 9,89.)"""
    D = _i(cr, 2); n = max(3, min(10, round(D / (4 + cr / 2))))
    return n * _atk(3 + cr / 3, ac, D / n, adv, resist, red, False)


def _resolve(fn, pv, ac, adv, resist, red):
    lo, hi = 0.0, 30.0
    for _ in range(60):
        m = (lo + hi) / 2
        if 4 * fn(m, ac, adv, resist, red) <= pv: lo = m
        else: hi = m
    return round(lo, 2)


def avaliar(spec, corpo):
    """spec: {"pv_efetivo", "ca", "adv" (−1/0/1: ataques contra ele), "resist" (bool), "red"}; o que faltar vem do corpo."""
    pv = spec.get('pv_efetivo', corpo['pv']); ac = spec.get('ca', corpo['ca'])
    adv = spec.get('adv', 0); resist = spec.get('resist', False); red = spec.get('red', corpo.get('red', 0))
    if 'medido' in spec:  # linhas cuja mecânica o motor ainda não modela (Shield, Absorb Elements, "barrado"…)
        bl, du = spec['medido']['blindagem'], spec['medido']['durabilidade']
    else:
        bl, du = _resolve(horda, pv, ac, adv, resist, red), _resolve(boss, pv, ac, adv, resist, red)
    nb = round(interp_degraus(bl, LIM_BLINDAGEM, NIVEIS), 1)
    nd = round(interp_degraus(du, LIM_DURABILIDADE, NIVEIS), 1)
    lb, ld = letra(nb), letra(nd)
    perfil = 'Equilibrado' if lb == ld else ('Blindado' if nb > nd else 'Durável')
    return dict(pv_efetivo=pv, ca=ac, blindagem=bl, durabilidade=du, nivel_blindagem=nb,
                nivel_durabilidade=nd, nivel_eq=max(nb, nd), rank=letra(max(nb, nd)), perfil=perfil)
