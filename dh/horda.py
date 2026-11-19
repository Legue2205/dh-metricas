"""Área v2 (19/11/2026): luta contra uma horda com a party de referência.

A party é o personagem + 2 guerreiros de referência. A horda tem um grupo que avança para o corpo a corpo
(premissa area.horda2.corpo) e um grupo separado à distância (area.horda2.distancia), com CR pela tabela de área.
A luta termina quando a party tira area.horda2.fracao_alvo da vida total da horda; a métrica é a velocidade
(1 / rounds). Dano acima do PV de cada criatura é perdido.

Política do personagem em cada round: usa a próxima área disponível se o dano esperado dela passar o dano de
alvo único (truque, ataques, invocações); senão ataca o alvo de menor PV. Round 1: o grupo do corpo a corpo está
agrupado e longe da party. Do round 2 em diante ele está misturado com os aliados: área sem seleção pega
area.fator_round2_nao_seletiva dos alvos, com seleção (Sculpt Spells, alvos escolhidos) area.fator_round2_seletiva.
O grupo à distância vale inteiro sempre. Cleaves somam um ataque num 2º alvo.

Régua: o mesmo combate com o conjurador de referência (1 área no maior espaço, sem seleção, depois truque).
Nível equivalente pela mesma interpolação da área antiga (area.nivel_eq).
"""
import numpy as np

from . import area as A
from .base import p_acerto
from .premissas import valor as _p

R0 = None


def _cfg():
    return dict(nc=int(_p('area.horda2.corpo')), nd=int(_p('area.horda2.distancia')), alvo=_p('area.horda2.fracao_alvo'),
                rmax=int(_p('area.horda2.rounds_max')), g=_p('area.horda2.guerreiros'), N=int(_p('area.horda2.N')),
                f_sel=_p('area.fator_round2_seletiva'), f_nao=_p('area.fator_round2_nao_seletiva'))


def _mod(L): return 3 if L < 4 else 4 if L < 8 else 5
def _n_atq(L, tab): return tab[0] if L < 5 else tab[1] if L < 11 else tab[2] if L < 20 else tab[3]


def _aplica_alvo(hp, dano, grupo):
    """Dano num alvo: o de menor PV vivo do grupo; sem vivos no grupo, o de menor PV da horda. Devolve o dano real."""
    vivos = hp > 0
    m = np.full(hp.shape, np.inf); m[:, grupo] = np.where(vivos[:, grupo], hp[:, grupo], np.inf)
    sem = ~np.isfinite(m).any(1)
    m = np.where(sem[:, None], np.where(vivos, hp, np.inf), m)
    j = np.argmin(m, 1); i = np.arange(len(j)); cur = hp[i, j]
    real = np.where(cur > 0, np.minimum(dano, cur), 0.0); hp[i, j] = cur - real
    return real


def combate(L, usos, dpr_alvo, cleaves=(), livres=(), N=None):
    """Rounds até a fração-alvo da vida da horda. usos: [(alvos, seletiva, gerador, cd, metade)] (gastam recurso);
    livres: idem, sem limite (cleave_save); cleaves: [(bonus, dano, p)] ataque extra num 2º alvo."""
    c = _cfg(); N = N or c['N']
    A.N = N; A.rng = np.random.default_rng(31)
    rng = A.rng
    hp0, ac, sv = A.CR[A.HORDA[L]]
    nc, nd = c['nc'], c['nd']; nh = nc + nd
    corpo, dist = list(range(nc)), list(range(nc, nh))
    hp = np.full((N, nh), float(hp0)); tot = np.zeros(N); meta = c['alvo'] * nh * hp0
    feito = np.full(N, np.nan); restantes = list(usos)
    g = c['g']; mod = _mod(L); bonus_g = A.pb(L) + mod; n_g = g['quantidade'] * _n_atq(L, g['ataques'])
    pf = lambda cd: min(1.0, max(0.0, (cd - sv - 1) / 20))

    def esperado(u, r):
        alvos, sel, ger, cd, metade = u
        f = 1.0 if r == 0 else (c['f_sel'] if sel else c['f_nao'])
        vivos_c = (hp[:, corpo] > 0).sum(1).mean(); vivos_d = (hp[:, dist] > 0).sum(1).mean()
        k = max(min(alvos * f, vivos_c), min(alvos, vivos_d))
        x = ger(); med = float(np.mean(x[0] if isinstance(x, tuple) else x))
        p = pf(cd); return k * min(med, hp0) * (p + (1 - p) * (0.5 if metade else 0))

    def lanca(u, r):
        nonlocal tot
        alvos, sel, ger, cd, metade = u
        f = 1.0 if r == 0 else (c['f_sel'] if sel else c['f_nao'])
        vc = (hp[:, corpo] > 0).sum(1); vd = (hp[:, dist] > 0).sum(1)
        kc = np.minimum(alvos * f, vc); kd = np.minimum(alvos, vd)
        usa_c = kc >= kd; x = np.where(usa_c, kc, kd)
        k = np.floor(x) + (rng.random(N) < x - np.floor(x))
        base = ger(); base, extra = base if isinstance(base, tuple) else (base, 0)
        for grupo, mascara in ((corpo, usa_c), (dist, ~usa_c)):
            vivos = hp[:, grupo] > 0; ordem = np.cumsum(vivos, 1) - 1
            for jj, j in enumerate(grupo):
                alvo = mascara & vivos[:, jj] & (ordem[:, jj] < k)
                ok = rng.integers(1, 21, N) + sv >= cd
                d = np.where(ok, base // 2 if metade else 0, base) + extra
                real = np.where(alvo, np.minimum(d, hp[:, j]), 0); hp[:, j] -= real; tot = tot + real

    for r in range(c['rmax']):
        antes = tot.copy()
        # personagem
        opcoes = [(esperado(u, r), 'uso', u) for u in restantes[:1]] + [(esperado(u, r), 'livre', u) for u in livres]
        melhor = max(opcoes, key=lambda x: x[0]) if opcoes else None
        if melhor and melhor[0] > dpr_alvo:
            lanca(melhor[2], r)
            if melhor[1] == 'uso': restantes.pop(0)
        elif dpr_alvo > 0:
            tot = tot + _aplica_alvo(hp, np.full(N, float(dpr_alvo)), corpo)
        for b, dano, p in cleaves:
            sim = rng.random(N) < p
            d = A.ataque(b, ac, lambda m: A.rola(dano, m)); tot = tot + _aplica_alvo(hp, np.where(sim, d, 0.0), dist if r == 0 else corpo)
        # guerreiros: corpo a corpo a partir do round 2 (o grupo do corpo chega); no 1º, arcos/aproximação (metade)
        for _ in range(n_g):
            d = A.ataque(bonus_g, ac, lambda m: A.rola(g['dano'], m) + mod)
            if r == 0: d = np.where(rng.random(N) < 0.5, d, 0)
            tot = tot + _aplica_alvo(hp, d, corpo)
        novo = np.isnan(feito) & (tot >= meta)
        frac = np.where(tot > antes, (meta - antes) / np.maximum(tot - antes, 1e-9), 1.0)
        feito = np.where(novo, r + np.clip(frac, 0, 1), feito)
    taxa = np.maximum(tot / c['rmax'], 1e-9)
    resto = np.where(np.isnan(feito), np.minimum(c['rmax'] + (meta - tot) / taxa, 2 * c['rmax']), feito)
    return float(resto.mean())


def _regua_ref():
    global R0
    if R0 is not None: return R0
    import hashlib, json
    from pathlib import Path
    from .premissas import hash_prefixos
    h = hashlib.sha1(Path(__file__).read_bytes() + Path(A.__file__).read_bytes() + hash_prefixos('base.', 'area.').encode()).hexdigest()[:10]
    arq = Path(__file__).resolve().parents[1] / 'cache' / f'horda-{h}.json'
    if arq.exists():
        R0 = {int(k): v for k, v in json.loads(arq.read_text()).items()}; return R0
    t = _p('area.horda2.truque_referencia'); R0 = {}
    for L in range(1, 21):
        A.N = _cfg()['N']
        k = 1 + (L >= 5) + (L >= 11); d = float(t.split('d')[1]); med = k * (d + 1) / 2
        hp0, ac, sv = A.CR[A.HORDA[L]]
        dpr = p_acerto(A.pb(L) + _mod(L), ac) * med
        R0[L] = 1.0 / combate(L, A.ref_usos(L, 1), dpr)
    from .arquivos import gravar
    gravar(arq, json.dumps(R0))
    return R0


def _dpr(spec, ca, inv):
    from . import dano as D
    if not spec: return 0.0
    if 'medido' in spec:
        return float(np.interp(ca, D.CAS, spec['medido']))
    return D.dpr(spec, ca, invocacoes=inv)


def avaliar(linha):
    """Velocidade da party (1/rounds) contra hordas de cada nível, comparada com a da régua."""
    from .base import letra
    areas = linha.get('area') or []; inv = linha.get('invocacoes', [])
    usos, livres, cleaves = [], [], []
    for a in areas:
        t = a.get('tipo', 'explosao')
        if t in ('explosao', 'prioritaria'):
            usos += [(u['alvos'], u.get('seletiva', False), A._gerador(u), u['cd'], u.get('metade', True)) for u in a['usos']]
        elif t == 'cleave_save':
            al = a['alvos'][1] if isinstance(a['alvos'], list) else a['alvos']
            livres.append((al, True, A._gerador(dict(dano=a['dano'])), a['cd'], a.get('metade', False)))
        elif t == 'cleave_ataque':
            cleaves.append(a)
    ref = _regua_ref(); fr = {}; rounds = {}
    for L in range(1, 21):
        hp0, ac, sv = A.CR[A.HORDA[L]]
        cl = []
        for a in cleaves:
            p = a['p']
            if p == 'erro': p = 1 - p_acerto(a['bonus'], ac) ** a.get('n_erro', 1)
            elif isinstance(p, list): p = p[1]
            cl.append((a['bonus'], a['dano'], p))
        rd = combate(L, usos, _dpr(linha.get('dano'), ac, inv), cl, livres)
        fr[L] = 1.0 / rd; rounds[L] = round(rd, 2)
    nv = float(A.nivel_eq(fr, ref))
    return dict(nivel_eq=round(nv, 1), rank=letra(nv), rounds=rounds, usos=len(usos))
