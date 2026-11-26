"""Controle de atenção: para onde vão os ataques que sobram (determinístico).

Porta de control_atencao.py + a função vida() do control_total.py (as duas eram cópias quase iguais;
aqui é uma só, com o vetor de negação de campo opcional).
"""
import numpy as np

from ..base import R, TOPO, TOPOS, n_ataques, p_acerto, pv_com_pvt

from ..premissas import P, grupo as _grupo
H = _grupo('controle.atencao')   # premissas controle.atencao.*
DPR_LV = ([1, 3, 4, 5, 6, 7, 8, 10, 11, 13, 16, 20], [8, 12, 15, 20, 22, 26, 31, 37, 45, 60, 80, 100])
# Party de referência (19/11, passada 3): 2 frontliners + atirador + conjurador. Os papéis 'tank' e 'striker' dos
# JSON continuam aceitos e ocupam uma das vagas de frontliner ('frontliner' também vale).
PAPEIS = ['frontliner', 'frontliner', 'atirador', 'conjurador']
VAGA = {'frontliner': 0, 'tank': 0, 'striker': 0, 'atirador': 2, 'conjurador': 3}
FRONT = ('frontliner', 'tank', 'striker')


def posicao(papel):
    """Índice, na party de referência, da vaga que um papel ocupa."""
    return VAGA[papel]


def dpr_ref(L): return float(np.interp(L, *DPR_LV))


def ca_marcial(L): return 16 if L <= 2 else 17 if L <= 4 else 18 if L <= 10 else 19 if L <= 14 else 20


def ref(papel, L):
    """Membro de referência de cada papel no nível L (tank/striker = frontliner, premissas controle.referencia.frontliner.*)."""
    if papel in FRONT:
        def F(k): return P(f'controle.referencia.frontliner.{k}')
        return dict(nome='Frontliner de referência', papel='frontliner', ca=min(F('ca_max'), ca_marcial(L) + F('ca_bonus')),
                    pv=F('pv_base') + (L - 1) * F('pv_por_nivel'), front=True, soft=F('soft'), dpr=F('dpr_fator') * dpr_ref(L))
    if papel == 'atirador':
        return dict(nome='Atirador de referência', papel=papel, ca=16 if L < 5 else 17 if L < 11 else 18,
                    pv=10 + (L - 1) * 7.5, front=False, acc_m=(0.7, 0.8, 1.0), dpr=dpr_ref(L))
    return dict(nome='Conjurador de referência', papel='conjurador', ca=16, pv=8 + (L - 1) * 6, front=False,
                acc_m=(0.8, 0.9, 1.0), conc=True, dpr=0.9 * dpr_ref(L))


def ref_padrao(papel, L):
    """Membro padrão para o Corpo (19/11, premissa controle.corpo.referencia_unica): a referência da vaga, mas com CA e
    PV médios da party de referência. Com a premissa em 0, é a própria referência da vaga (comportamento antigo)."""
    r = ref(papel, L)
    if not P('controle.corpo.referencia_unica'): return r
    todos = [ref(pp, L) for pp in PAPEIS]
    return dict(r, nome='Membro padrão', ca=float(np.mean([x['ca'] for x in todos])), pv=float(np.mean([x['pv'] for x in todos])))


def ficha(spec, corpo):
    """build.json -> ficha de atenção (o formato que o motor usa)."""
    f = dict(papel=spec['papel'], ca=corpo['ca'], pv=pv_com_pvt(corpo), front=spec.get('front', spec['papel'] in FRONT),
             dpr=spec['dpr'])
    for k in ('res', 'adv', 'red'):
        if corpo.get(k): f[k] = corpo[k]
    for k in ('soft', 'conc', 'esqueletos', 'agarra', 'inv_pv', 'inv_ca', 'inv_dpr', 'oculto', 'redireciona', 'redireciona_para'):
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
    vals = [(p['dpr'] / p['pv'] if p['pv'] > 0 else 0.0) * (H['conc_bonus'] if p.get('conc') else 1) for p in party]   # invocação morta: pv 0
    mv = np.mean([v for v, p in zip(vals, party) if not p.get('skel')]) or 1
    w = []
    for p, v in zip(party, vals):
        if p.get('skel'):   # D4 (23/11): burro = mais um corpo na frente; esperto = ameaça por PV, como os membros
            w.append((H['skel_peso'] * (1 - m) + m * v / mv) if (e['melee'] and p['pv'] > 0) else 0); continue
        f = float(p['front'])                 # fração do tempo na linha de frente (bool = 0 ou 1)
        if e['melee']:
            reach = f + (1 - f) * p.get('acc_m', (1, 1, 1))[ti]
            near = f + (1 - f) * H['near_back']
        else:
            reach = p.get('acc_r', (1, 1, 1))[ti]; near = 1.0
        pref = (1 - m) * near + m * v / mv
        w.append(reach * pref * (1 + p.get('soft', 0) * (1 - m)) * (1 - p.get('oculto', 0)))   # oculto: não pode ser alvo
    w = np.array(w); P = w / w.sum() if w.sum() > 0 else w
    if e['melee']:  # taunt hard: parte dos turnos que iam para a backline vai para quem tem 'hard'
        for k, p in enumerate(party):
            h = p.get('hard')
            if not h: continue
            stop = TOPO[TOPOS[ti]]['cruza'] * (h(e) if callable(h) else h)
            back = [(j, 1 - float(q['front'])) for j, q in enumerate(party) if float(q['front']) < 1 and not q.get('skel')]
            mov = sum(P[j] * b for j, b in back) * stop
            for j, b in back: P[j] *= (1 - stop * b)
            P[k] += mov
    for k, p in enumerate(party):   # D13 (24/11): puxa para si o dano mirado nos aliados (Aura of the Guardian, Divine
        r = p.get('redireciona')      # Allegiance, Protective Bond): fração dos turnos contra os outros vira contra ele
        if not r: continue            # (melee e à distância; a reação e o alcance já estão na fração). Como um taunt
        t = k                         # forte: só vale se a build aguenta (CA e PV dela entram na vida).
        if p.get('redireciona_para') == 'mais_resistente':
            # 26/11 (G2): Protective Bond e afins — quem leva o golpe é o membro ligado mais resistente (pode não ser a
            # build): PV ÷ chance de o inimigo acertar, com resistência. A build também pode ter o dano desviado.
            vivos = [j for j, q in enumerate(party) if not q.get('skel') and q['pv'] > 0]
            if vivos:
                t = max(vivos, key=lambda j: party[j]['pv'] / max(0.05, p_acerto(e.get('atk', 7), party[j]['ca'], party[j].get('adv', 0)))
                        / (party[j].get('res', 1) or 1))
        for j, q in enumerate(party):
            if j == t or q.get('skel'): continue
            mov = P[j] * r; P[j] -= mov; P[t] += mov
    if grap is not None and e is grap[0]:  # agarrão: o agarrado só alcança quem o agarra
        k = grap[1]; reach = H['reach_grande'] if e['cr'] >= 5 else H['reach_pequeno']
        P = (1 - reach) * P + reach * np.eye(len(party))[k]
    return P


def perda(F):
    """Vida perdida (até 1) + fração da luta passada caído."""
    return min(F, 1.0) + max(0.0, 1 - 1 / F) if F > 0 else 0.0


_MEMO_VIDA = {}


def _chave(x):
    """Chave hashable e estável de dicts/listas/arrays pequenos (para o memo da vida)."""
    if isinstance(x, dict): return tuple(sorted((k, _chave(v)) for k, v in x.items()))
    if isinstance(x, (list, tuple)): return tuple(_chave(v) for v in x)
    if isinstance(x, np.ndarray): return tuple(np.round(x.astype(float), 12).tolist())
    if isinstance(x, float): return round(x, 12)
    return x


_ESC = (int, float, str, bool, type(None))


def _rasa(lista):
    """Chave barata de uma lista de dicts rasos (ordem de inserção; ordem diferente só custa uma falha de cache)."""
    out = []
    for d in lista:
        it = tuple(d.items())
        out.append(it if all(isinstance(v, _ESC) for _, v in it) else _chave(d))
    return tuple(out)


def vida(E, party, ti, neg=None, detalhe=False, marca=None):
    """Memo (check-up 23/11): a simulação é determinística e a mesma entrada se repete muito (party de referência,
    curva da régua: igual para toda linha e toda build no mesmo nível/encontro/topografia)."""
    kn = None if neg is None else (neg.tobytes() if isinstance(neg, np.ndarray) else _chave(neg))
    k = (_rasa(E), _rasa(party), ti, kn, detalhe, _chave(marca))
    r = _MEMO_VIDA.get(k)
    if r is None:
        if len(_MEMO_VIDA) > 400_000: _MEMO_VIDA.clear()
        r = _MEMO_VIDA[k] = _vida(E, party, ti, neg, detalhe, marca)
    return (r[0], list(r[1])) if detalhe else r


def sobrevivencia(E, party, ti):
    """P2.13 (23/11): fração dos rounds em que as invocações começam vivas (PV > 0), na mesma simulação da vida."""
    k = ('sobrev', _rasa(E), _rasa(party), ti)
    r = _MEMO_VIDA.get(k)
    if r is None: r = _MEMO_VIDA[k] = _vida(E, party, ti, inv=True)
    return r


def _vida(E, party, ti, neg=None, detalhe=False, marca=None, inv=False):
    """Vida perdida pela party em R rounds; cada inimigo causa (1 − negação de campo) do dano dele.
    marca = (k, vetor): marca do membro k (Ancestral Protectors, Unwavering Mark): o dano do inimigo i contra os
    OUTROS membros cai pela fração vetor[i]; contra quem marcou, não (19/11: a marca conta no Corpo)."""
    party = [dict(p) for p in party]
    neg = np.zeros(len(E)) if neg is None else np.asarray(neg)
    km, mv = (None, None) if marca is None else (marca[0], np.asarray(marca[1]))
    grap = None
    fj = [k for k, p in enumerate(party) if p.get('agarra')]
    if fj:
        mel = [e for e in E if e['melee']]
        if mel: grap = (max(mel, key=lambda e: e['dn']), fj[0])
    dano = np.zeros(len(party)); vivo = 0; js = [j for j, p in enumerate(party) if p.get('skel')]
    for r in range(R):
        if js and party[js[0]]['pv'] > 0: vivo += 1
        for ie, e in enumerate(E):
            P = distribui(e, party, ti, grap)
            na = n_ataques(e['cr']); d = e['dn'] / na
            for j, p in enumerate(party):
                if P[j] == 0: continue
                red = 0 if e['cr'] >= 10 else p.get('red', 0)
                dmg = na * p_acerto(e['atk'], p['ca'], p.get('adv', 0)) * max(0, d * p.get('res', 1) - red)
                if km is not None and j != km: dmg *= 1 - mv[ie]
                dano[j] += P[j] * dmg * (1 - neg[ie])
                if p.get('skel'): p['pv'] = max(0, p['pv0'] - dano[j])
    if inv: return vivo / R if js else 1.0
    tot = sum(perda(dano[j] / p['pv']) for j, p in enumerate(party) if not p.get('skel'))
    if detalhe:
        return tot, [perda(dano[j] / p['pv']) for j, p in enumerate(party) if not p.get('skel')]
    return tot


def party_com(membro, L):
    party = [ref(pp, L) for pp in PAPEIS]
    party[posicao(membro['papel'])] = membro
    if membro.get('esqueletos'):
        pv = membro.get('inv_pv', H['skel_pv'])
        party.append(dict(nome='Invocações', skel=True, pv=pv, pv0=pv, ca=membro.get('inv_ca', 16), front=True,
                          dpr=membro.get('inv_dpr', 0.0)))
    return party
