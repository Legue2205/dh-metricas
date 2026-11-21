"""Defesa: Blindagem (contra horda) e Durabilidade (contra boss) — fórmula fechada.

Motor reconstruído em 03/11 (patch do Jamal/Virgil) e conferido com a planilha nas linhas de referência.
Blindagem/Durabilidade = maior CR de horda/boss que o personagem aguenta 4 rounds sem cair (busca binária).
O nível equivalente segue a aba Rampas da planilha "Ranks de defesa".
"""
import numpy as np

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


from .premissas import valor as _p
FATOR_CRITICO = _p('defesa.fator_critico')
_HG, _HA, _HB = _p('defesa.horda.dano_por_golpe'), _p('defesa.horda.atacantes'), _p('defesa.horda.acerto')
_CH_AT, _CH_B, _CH_MAG = _p('defesa.chefe.ataques_por_cr'), _p('defesa.chefe.acerto_extra'), _p('defesa.chefe.cr_arma_magica')


def _n_horda(D, cr): return max(_HA['min'], min(_HA['max'], round(D / (_HG['base'] + cr * _HG['por_cr']))))
def _n_chefe(cr): return next(n for ate, n in _CH_AT if cr <= ate)


def _atk(bonus, ac, d, adv, resist, red, magico, F=FATOR_CRITICO):
    p = min(0.95, max(0.05, (21 - (ac - bonus)) / 20)); c = 0.05
    if adv == 1: p, c = 1 - (1 - p) ** 2, 1 - 0.95 ** 2
    if adv == -1: p, c = p * p, 0.0025
    hit, crit = d, d * (1 + F)
    if not magico: hit, crit = max(0, hit - red), max(0, crit - red)
    if resist: hit, crit = hit / 2, crit / 2
    return (p - c) * hit + c * crit


def boss(cr, ac, adv, resist, red):
    n = _n_chefe(cr); D = _i(cr, 2)
    return n * _atk(_i(cr, 1) + _CH_B, ac, D / n, adv, resist, red, cr >= _CH_MAG)


def horda(cr, ac, adv, resist, red):
    """Horda: o dano por round do CR dividido entre 3 e 10 atacantes de (4 + CR/2) de dano cada.
    O nº de atacantes importa para quem tem redução fixa (Heavy Armor Master): mais golpes menores = mais redução.
    (A reconstrução de 03/11 usava 4 + CR/2 atacantes e superestimava o Abdul: 10,69 em vez de 9,89.)"""
    D = _i(cr, 2); n = _n_horda(D, cr)
    return n * _atk(_HB['base'] + cr * _HB['por_cr'], ac, D / n, adv, resist, red, False)


def _resolve(fn, pv, ac, adv, resist, red):
    lo, hi = 0.0, 30.0
    for _ in range(60):
        m = (lo + hi) / 2
        if 4 * fn(m, ac, adv, resist, red) <= pv: lo = m
        else: hi = m
    return round(lo, 2)


# ---------------- reações (Shield, Uncanny Dodge, Parry): simulação golpe a golpe ----------------
N_SIM = 4000
GRADE = (0.0, 0.6, 1.0, 1.4, 2.0, 3.0)   # "preço" de guardar a reação, em múltiplos do dano médio de um golpe
REACOES = ('shield', 'uncanny_dodge', 'reduz_dano', 'desvantagem', 'anula_critico', 'bloqueio')


def _sim(tipo, cr, ac, advs, resist, red, reacoes, livre_p, precos, seed=7, pvt_round=0.0):
    """Dano médio em R rounds com reações. O personagem vê o total do ataque (Shield) e o dano rolado
    (Uncanny Dodge / Parry) antes de decidir, e pesa os golpes que ainda faltam no round.
    Shield: gasta um uso se o golpe entra na faixa [CA, CA+5) e (dano evitado agora + esperado nos próximos
    golpes do round) >= preço. Redução: 1 por round, no golpe que passar do preço (ou no último do round)."""
    rng = np.random.default_rng(seed); D = _i(cr, 2)
    if tipo == 'horda': n = _n_horda(D, cr); bonus = _HB['base'] + cr * _HB['por_cr']; magico = False
    else: n = _n_chefe(cr); bonus = _i(cr, 1) + _CH_B; magico = cr >= _CH_MAG
    d = D / n
    def liq(x):
        if not magico: x = np.maximum(0, x - red)
        return x / 2 if resist else x
    dbar = float(liq(np.array(d)))
    p_faixa = sum(1 for f in range(2, 20) if ac <= f + bonus < ac + 5) / 20
    usos = {}
    for i, rc in enumerate(reacoes):
        u = rc.get('usos_luta', 99); usos[i] = np.floor(u) + (rng.random(N_SIM) < u - np.floor(u))
    total = np.zeros(N_SIM)
    for r in range(4):
        adv = advs[r]; livre = rng.random(N_SIM) < livre_p; escudo = np.zeros(N_SIM, bool)
        pool = np.full(N_SIM, float(pvt_round))   # PV temporários que se renovam a cada round (Reckless Abandon)
        for j in range(n):
            a = rng.integers(1, 21, N_SIM)
            if adv: b = rng.integers(1, 21, N_SIM); a = np.maximum(a, b) if adv > 0 else np.minimum(a, b)
            for i, rc in enumerate(reacoes):     # desvantagem (Warding Flare): decidida ANTES do resultado, no 1º golpe do round
                if rc['tipo'] == 'desvantagem' and j == 0:
                    usa = livre & (usos[i] > 0)
                    a = np.where(usa, np.minimum(a, rng.integers(1, 21, N_SIM)), a); usos[i] -= usa; livre &= ~usa
            crit = a == 20; tot = a + bonus
            hit = crit | ((a != 1) & (tot >= ac + 5 * escudo))
            for i, rc in enumerate(reacoes):     # anula crítico (Sentinel at Death's Door): crítico vira acerto normal
                if rc['tipo'] == 'anula_critico':
                    usa = livre & crit & (usos[i] > 0); crit = crit & ~usa; usos[i] -= usa; livre &= ~usa
            dmg = liq(d * (rng.random(N_SIM) + rng.random(N_SIM)) * np.where(crit, 1.6, 1.0)); rest = n - 1 - j
            for i, rc in enumerate(reacoes):
                if rc['tipo'] in ('desvantagem', 'anula_critico'): continue
                pode = livre & hit & (usos[i] > 0)
                if rc['tipo'] == 'shield':
                    usa = pode & ~crit & ~escudo & (tot < ac + 5) & (dmg + rest * p_faixa * dbar >= precos[i] * dbar)
                    escudo |= usa; hit &= ~usa
                elif rc['tipo'] == 'bloqueio':   # +k de CA contra UM ataque, depois de saber que acertou (cauda do Beast: 1d8)
                    kmax = rc.get('dado', 0) or rc.get('valor', 0)
                    usa = pode & ~crit & (tot < ac + 5 * escudo + kmax) & (dmg >= precos[i] * dbar)
                    k = rng.integers(1, rc['dado'] + 1, N_SIM) if rc.get('dado') else rc.get('valor', 0)
                    hit &= ~(usa & (tot < ac + 5 * escudo + k))
                else:
                    usa = pode & ((dmg >= precos[i] * dbar) | (rest == 0))
                    dmg = np.where(usa, dmg * rc.get('fator', 0.5) if rc['tipo'] == 'uncanny_dodge'
                                   else np.maximum(0, dmg - rc.get('valor', 0)), dmg)
                usos[i] -= usa; livre &= ~usa
            absorvido = np.minimum(pool, hit * dmg); pool -= absorvido
            total += hit * dmg - absorvido
    return float(total.mean())


def _golpe(tipo, cr, resist, red):
    """Dano de um golpe (para mecânicas do tipo 'aguenta N golpes a 0 PV')."""
    D = _i(cr, 2)
    if tipo == 'horda': n = _n_horda(D, cr); magico = False
    else: n = _n_chefe(cr); magico = cr >= _CH_MAG
    return max(0.0, D / n - (0 if magico else red)) * (0.5 if resist else 1)


def _resolve_sim(tipo, pv, ac, advs, resist, red, reacoes, livre_p, extras=0, pvt_round=0.0):
    import itertools
    def melhor(cr):   # a política (preços) é otimizada: o jogador escolhe o limiar que mais poupa dano
        idx = [i for i, rc in enumerate(reacoes) if rc['tipo'] not in ('desvantagem', 'anula_critico')]   # sem preço
        def pr_de(g): p = [0.0] * len(reacoes); [p.__setitem__(i, x) for i, x in zip(idx, g)]; return p
        return min(_sim(tipo, cr, ac, advs, resist, red, reacoes, livre_p, pr_de(g), pvt_round=pvt_round)
                   for g in itertools.product(GRADE, repeat=len(idx)))
    lo, hi = 0.0, 30.0
    for _ in range(22):
        m = (lo + hi) / 2
        if melhor(m) <= pv + extras * _golpe(tipo, m, resist, red): lo = m
        else: hi = m
    return round(lo, 2)


def _resolve_rounds(fn, pv, ac, advs, resist, red, extras=0, pvt_round=0.0):
    lo, hi = 0.0, 30.0
    for _ in range(60):
        m = (lo + hi) / 2
        if sum(max(0.0, fn(m, ac, a, resist, red) - pvt_round) for a in advs) <= pv + extras * _golpe(fn.__name__, m, resist, red): lo = m
        else: hi = m
    return round(lo, 2)


def avaliar(spec, corpo, reacao_livre=1.0):
    """spec: {"pv_efetivo", "ca", "adv" (−1/0/1: ataques contra ele) ou "adv_por_round": [4 valores],
    "resist", "red", "reacoes": [{"tipo": "shield", "usos_luta": 2} | {"tipo": "uncanny_dodge"} |
    {"tipo": "reduz_dano", "valor": 8, "usos_luta": 99} | {"tipo": "desvantagem", "usos_luta": 1} (Warding Flare,
    decidida antes do resultado, no 1º golpe do round) | {"tipo": "anula_critico", "usos_luta": 1} (Sentinel at
    Death's Door) | {"tipo": "bloqueio", "dado": 8} ou {"valor": 2} (+CA contra UM ataque depois de acertar: cauda do
    Beast, Arcane Deflection, Defensive Duelist)]}; o que faltar vem do corpo.
    PV temporários próprios: "pvt_luta" (carga que ele já tem no começo da luta, somada ao PV; ex.: Touch of Death)
    e "pvt_round" (renova todo round e absorve o 1º dano do round; ex.: Reckless Abandon). Na linha ou no corpo.
    reacao_livre: fração dos rounds em que a reação NÃO foi gasta em outro eixo da mesma hipótese."""
    pv = spec.get('pv_efetivo', corpo['pv']); ac = spec.get('ca', corpo['ca'])
    pv += spec.get('pvt_luta', corpo.get('pvt_luta', 0)); pvr = spec.get('pvt_round', corpo.get('pvt_round', 0))
    adv = spec.get('adv', 0); resist = spec.get('resist', False); red = spec.get('red', corpo.get('red', 0))
    if 'medido' in spec:  # linhas cuja mecânica o motor ainda não modela (Shield, Absorb Elements, "barrado"…)
        bl, du = spec['medido']['blindagem'], spec['medido']['durabilidade']
    else:
        advs = spec.get('adv_por_round', [adv] * 4)
        reacoes = spec.get('reacoes', []) if reacao_livre > 0 else []
        ex = spec.get('golpes_extras_a_0pv', 0)   # ex.: 'barrado': continua de pé por N golpes depois de zerar
        if reacoes:
            bl = _resolve_sim('horda', pv, ac, advs, resist, red, reacoes, reacao_livre, ex, pvr)
            du = _resolve_sim('boss', pv, ac, advs, resist, red, reacoes, reacao_livre, ex, pvr)
        else:
            bl = _resolve_rounds(horda, pv, ac, advs, resist, red, ex, pvr)
            du = _resolve_rounds(boss, pv, ac, advs, resist, red, ex, pvr)
    nb = round(interp_degraus(bl, LIM_BLINDAGEM, NIVEIS), 1)
    nd = round(interp_degraus(du, LIM_DURABILIDADE, NIVEIS), 1)
    lb, ld = letra(nb), letra(nd)
    perfil = 'Equilibrado' if lb == ld else ('Blindado' if nb > nd else 'Durável')
    return dict(pv_efetivo=pv, ca=ac, blindagem=bl, durabilidade=du, nivel_blindagem=nb,
                nivel_durabilidade=nd, nivel_eq=max(nb, nd), rank=letra(max(nb, nd)), perfil=perfil,
                reacoes_usadas=[r['tipo'] for r in spec.get('reacoes', [])] if reacao_livre > 0 else [])
