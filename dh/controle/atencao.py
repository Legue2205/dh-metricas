"""Controle de atenção: para onde vão os ataques que sobram (determinístico).

Porta de control_atencao.py + a função vida() do control_total.py (as duas eram cópias quase iguais;
aqui é uma só, com o vetor de negação de campo opcional).
"""
import numpy as np

from ..base import R, TOPO, TOPOS, n_ataques, p_acerto

H = dict(near_back=0.25, conc_bonus=1.5, skel_peso=1.5, skel_pv=133, reach_grande=0.5, reach_pequeno=0.2)
DPR_LV = ([1, 3, 4, 5, 6, 7, 8, 10, 11, 13, 16, 20], [8, 12, 15, 20, 22, 26, 31, 37, 45, 60, 80, 100])
PAPEIS = ['tank', 'striker', 'atirador', 'conjurador']


def dpr_ref(L): return float(np.interp(L, *DPR_LV))


def ca_marcial(L): return 16 if L <= 2 else 17 if L <= 4 else 18 if L <= 10 else 19 if L <= 14 else 20


def ref(papel, L):
    """Membro de referência de cada papel no nível L."""
    if papel == 'tank':
        return dict(nome='Tank de referência', papel=papel, ca=min(21, ca_marcial(L) + 2), pv=12 + (L - 1) * 8.5,
                    front=True, soft=0.15, dpr=0.7 * dpr_ref(L))
    if papel == 'striker':
        return dict(nome='Striker de referência', papel=papel, ca=ca_marcial(L), pv=10 + (L - 1) * 7.5,
                    front=True, soft=0.15, dpr=dpr_ref(L))
    if papel == 'atirador':
        return dict(nome='Atirador de referência', papel=papel, ca=16 if L < 5 else 17 if L < 11 else 18,
                    pv=10 + (L - 1) * 7.5, front=False, acc_m=(0.7, 0.8, 1.0), dpr=dpr_ref(L))
    return dict(nome='Conjurador de referência', papel='conjurador', ca=16, pv=8 + (L - 1) * 6, front=False,
                acc_m=(0.8, 0.9, 1.0), conc=True, dpr=0.9 * dpr_ref(L))


def ficha(spec, corpo):
    """build.json -> ficha de atenção (o formato que o motor usa)."""
    f = dict(papel=spec['papel'], ca=corpo['ca'], pv=corpo['pv'], front=spec.get('front', spec['papel'] in ('tank', 'striker')),
             dpr=spec['dpr'])
    for k in ('res', 'adv', 'red'):
        if corpo.get(k): f[k] = corpo[k]
    for k in ('soft', 'conc', 'esqueletos', 'agarra', 'inv_pv', 'inv_ca'):
        if k in spec: f[k] = spec[k]
    for k in ('acc_m', 'acc_r'):
        if k in spec: f[k] = tuple(spec[k])
    hard = spec.get('hard')
    if isinstance(hard, dict) and 'sentinela' in hard:
        b = hard['sentinela']; f['hard'] = lambda e, b=b: 1 - (1 - p_acerto(b, e['ca'])) ** 2
    elif isinstance(hard, dict) and 'p' in hard:
        f['hard'] = hard['p']
    return f


def distribui(e, party, ti, grap=None):
    """Probabilidade de cada membro ser o alvo do turno do inimigo e."""
    m = e['mal'] / 3
    vals = [p['dpr'] / p['pv'] * (H['conc_bonus'] if p.get('conc') else 1) for p in party]
    mv = np.mean([v for v, p in zip(vals, party) if not p.get('skel')]) or 1
    w = []
    for p, v in zip(party, vals):
        if p.get('skel'):
            w.append(H['skel_peso'] * (1 - m) if (e['melee'] and p['pv'] > 0) else 0); continue
        if e['melee']:
            reach = 1.0 if p['front'] else p.get('acc_m', (1, 1, 1))[ti]
            near = 1.0 if p['front'] else H['near_back']
        else:
            reach = p.get('acc_r', (1, 1, 1))[ti]; near = 1.0
        pref = (1 - m) * near + m * v / mv
        w.append(reach * pref * (1 + p.get('soft', 0) * (1 - m)))
    w = np.array(w); P = w / w.sum() if w.sum() > 0 else w
    if e['melee']:  # taunt hard: parte dos turnos que iam para a backline vai para quem tem 'hard'
        for k, p in enumerate(party):
            h = p.get('hard')
            if not h: continue
            stop = TOPO[TOPOS[ti]]['cruza'] * (h(e) if callable(h) else h)
            back = [j for j, q in enumerate(party) if not q['front'] and not q.get('skel')]
            mov = sum(P[j] for j in back) * stop
            for j in back: P[j] *= (1 - stop)
            P[k] += mov
    if grap is not None and e is grap[0]:  # agarrão: o agarrado só alcança quem o agarra
        k = grap[1]; reach = H['reach_grande'] if e['cr'] >= 5 else H['reach_pequeno']
        P = (1 - reach) * P + reach * np.eye(len(party))[k]
    return P


def perda(F):
    """Vida perdida (até 1) + fração da luta passada caído."""
    return min(F, 1.0) + max(0.0, 1 - 1 / F) if F > 0 else 0.0


def vida(E, party, ti, neg=None, detalhe=False):
    """Vida perdida pela party em R rounds; cada inimigo causa (1 − negação de campo) do dano dele."""
    party = [dict(p) for p in party]
    neg = np.zeros(len(E)) if neg is None else np.asarray(neg)
    grap = None
    fj = [k for k, p in enumerate(party) if p.get('agarra')]
    if fj:
        mel = [e for e in E if e['melee']]
        if mel: grap = (max(mel, key=lambda e: e['dn']), fj[0])
    dano = np.zeros(len(party))
    for r in range(R):
        for ie, e in enumerate(E):
            P = distribui(e, party, ti, grap)
            na = n_ataques(e['cr']); d = e['dn'] / na
            for j, p in enumerate(party):
                if P[j] == 0: continue
                red = 0 if e['cr'] >= 10 else p.get('red', 0)
                dmg = na * p_acerto(e['atk'], p['ca'], p.get('adv', 0)) * max(0, d * p.get('res', 1) - red)
                dano[j] += P[j] * dmg * (1 - neg[ie])
                if p.get('skel'): p['pv'] = max(0, p['pv0'] - dano[j])
    tot = sum(perda(dano[j] / p['pv']) for j, p in enumerate(party) if not p.get('skel'))
    if detalhe:
        return tot, [perda(dano[j] / p['pv']) for j, p in enumerate(party) if not p.get('skel')]
    return tot


def party_com(membro, L):
    party = [ref(pp, L) for pp in PAPEIS]
    party[PAPEIS.index(membro['papel'])] = membro
    if membro.get('esqueletos'):
        pv = membro.get('inv_pv', H['skel_pv'])
        party.append(dict(nome='Invocações', skel=True, pv=pv, pv0=pv, ca=membro.get('inv_ca', 16), front=True, dpr=0))
    return party
