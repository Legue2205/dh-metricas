"""Controle declarativo: transforma a lista "fontes" do build.json numa função fn(E, topo) -> {fonte: negação}.

Cada fonte é um dicionário com "tipo". Tipos disponíveis (ver README para exemplos):
  ameaca            corpo que atrai ataques (taunt soft)
  sentinela         taunt hard por ataque de oportunidade que para o movimento (Sentinel)
  parada_oa         taunt hard por probabilidade fixa de parar quem passa
  area              magia/efeito em área da biblioteca (Web, Hypnotic Pattern, Conquering Presence…)
  alvo_unico        magias de alvo único relançadas com os espaços dados (modo combinar ou melhor)
  alvo_unico_direto efeito de alvo único sem relançar (ex.: Wall of Force num alvo)
  ataque_com_save   save no acerto (Stunning Strike e afins)
  melhor_de         escolhe a opção que mais nega (ex.: concentração exclusiva Fear OU Polymorph)
  plano             roteiro round a round (Virgil), executado por um motor genérico
  esqueletos, agarrao, ancestral_protectors, command_fixo, ataque_nega_turno   (casos especiais registrados)
"""
import numpy as np

from ..base import R, TOPO, p_acerto, save
from . import campo as C


def _corpo_t(corpo, nivel):
    return dict(nivel=nivel, ca=corpo['ca'], pv=corpo['pv'], res=corpo.get('res', 1), adv=corpo.get('adv', 0),
                red=corpo.get('red', 0))


def _mag(nome, sobre=None):
    return C.magia(nome, **(sobre or {}))


# ---------------- tipos simples ----------------
def _ameaca(f, E, topo, t): return C.soft(E, t)


def _sentinela(f, E, topo, t):
    b, n = f.get('bonus', 8), f.get('tentativas', 2)
    return np.array([c['wb'] * TOPO[topo]['cruza'] * (1 - (1 - p_acerto(b, c['ca'])) ** n) * C.dil(t, c)
                     if c['melee'] else 0 for c in E])


def _parada_oa(f, E, topo, t):
    return np.array([c['wb'] * TOPO[topo]['cruza'] * f.get('p', C.H['p_disengage']) if c['melee'] else 0 for c in E])


def _area(f, E, topo, t):
    m = _mag(f['magia'], f.get('sobre'))
    if f.get('so_grupos') and len(E) <= 1: return C.zero(E)
    if f.get('so_corpo_a_corpo') and not any(c['melee'] for c in E): return C.zero(E)
    v = C.area(E, f.get('alvos', m.get('alvos', 1)), C.f_area(f['cd'], m, f.get('atraso', 0)), topo,
               m.get('mult', 'area'))
    if f.get('so_corpo_a_corpo'): v = np.where([c['melee'] for c in E], v, 0)
    return v


def _alvo_unico(f, E, topo, t):
    cd, slots = f['cd'], tuple(f['slots'])
    ms = [_mag(n, f.get('sobre', {}).get(n)) for n in f['magias']]
    if f.get('modo', 'combinar') == 'combinar':
        sp = tuple(C._tupla(m) for m in ms)
        return C.unico(E, lambda c: C.seq1(C.ckey(c), cd, slots, sp)[0])
    best = None
    for m in ms:
        sl = tuple(s for s in slots if s >= m['nivel'])
        v = C.unico(E, lambda c, m=m, sl=sl: C.seq1(C.ckey(c), cd, sl, (C._tupla(m),))[0])
        if best is None or C.tot(E, v) > C.tot(E, best): best = v
    return best


def _alvo_unico_direto(f, E, topo, t):
    m = _mag(f['magia'], f.get('sobre'))
    return C.unico(E, C.f_area(f['cd'], m, f.get('atraso', 0)))


def _ataque_com_save(f, E, topo, t):
    b, cd, atr, pen = tuple(f['bonus']), f['cd'], f['save'], f.get('penalidade_por_round', 0)
    return C.unico(E, lambda c: C.stun(c['ca'], round(save(c, atr), 2), c['lr'], b, cd, pen))


def _melhor_de(f, E, topo, t):
    best = None
    for op in f['opcoes']:
        v = C.jv(*_avalia_fonte(op, E, topo, t).values()) if op['tipo'] != 'melhor_de' else _melhor_de(op, E, topo, t)
        if best is None or C.tot(E, v) > C.tot(E, best): best = v
    return best


# ---------------- casos especiais registrados ----------------
def _esqueletos(f, E, topo, t): return C.esqueletos(E, f.get('pv', 133), f.get('ca_alvo', 18))


def _agarrao(f, E, topo, t):
    return C.unico(E, lambda c: C.agarra(round(c['fo'] + c['sb'], 2),
                                         C.H['reach_grande'] if c['cr'] >= 5 else C.H['reach_pequeno'],
                                         round(C.dil(t, c), 3), f.get('bonus', 7)),
                   filtro=lambda c: c['melee'])


def _ancestral(f, E, topo, t):
    pa = TOPO[topo]['alc_miau']; b = f.get('bonus', 8)

    def g(c):
        p1 = p_acerto(b, c['ca']); p1a = p_acerto(b, c['ca'], 1); pn = p_acerto(c['atk'], 15)
        marc = (1 - pa) * (1 - 0.5 * pn) + pa * C.dil(t, c)
        turnos = sum((1 - (1 - (p1 if r == 0 else p1a)) ** 2) * (1 if r < R - 1 else 0.5) for r in range(R))
        return turnos / R * marc
    return C.unico(E, g)


def _command_fixo(f, E, topo, t):
    alvos = sorted(range(len(E)), key=lambda i: -E[i]['dn'])[:f.get('alvos', 5)]
    v = C.zero(E)
    for i in alvos:
        c = E[i]; pf = 1 - min(1, max(0, (21 - (f['cd'] - save(c, f.get('save', 'Sab')))) / 20))
        x = 0.0
        for r in range(1, R):
            ef = pf if not c['lr'] else pf * (0 if r == 1 else 1)
            x += ef * (1 if r < R - 1 else 0.5)
        v[i] = x / R
    return v


def _ataque_nega_turno(f, E, topo, t):
    return C.unico(E, lambda c: p_acerto(f['bonus'], c['ca']) * f.get('turnos', 1) / R)


# ---------------- plano round a round ----------------
def _fails(mod, cd, uw, lr_left, dado):
    """Falha no save; uw = penalidade −1dX (Unsettling Words). Gasta Legendary Resistance na falha."""
    n = C.N
    pen = np.where(uw, C.rng.integers(1, dado + 1, n), 0) if dado else 0
    fa = C.rng.integers(1, 21, n) + mod - pen < cd
    usa = fa & (lr_left > 0); fa &= ~usa; lr_left -= usa
    return fa


def _plano_solo(f, c):
    s = f['solo']; m = _mag(s['magia']); cd = f['cd']; dado = f.get('penalidade', {}).get('dado', 0)
    n = C.N; lr = np.full(n, c['lr']); depois = C.rng.random(n) < 0.5; neg = np.zeros(n)
    preso = np.zeros(n, bool)
    for r in range(R):
        tent = ~preso
        preso |= ~preso & _fails(save(c, m['save']), cd, s.get('penalidade_lancamento', True), lr, dado)
        ativo = np.ones(n, bool) if r > 0 else depois
        neg += preso * ativo * m['peso']
        if m['termino'] == 'fim_turno':
            uw = ~tent if s.get('penalidade_manutencao', True) else np.zeros(n, bool)
            sai = ~_fails(save(c, m['save']), cd, uw, lr, dado); preso &= ~(sai & ativo)
    return np.array([neg.mean() / R])


def _plano(f, E, topo, t):
    """Roteiro: cada ação tem round (1..R), magia, nº de alvos, seleção e uso da penalidade no save.
    Persistentes (fim_turno/luta/escape) valem até o save; um_turno vale só aquele round (meio turno no último).
    O valor por criatura em cada round é o MAIOR peso ativo nela."""
    if len(E) == 1 and 'solo' in f: return _plano_solo(f, E[0])
    cd = f['cd']; dado = f.get('penalidade', {}).get('dado', 0)
    n, N = len(E), C.N
    dn = np.array([c['dn'] for c in E])
    grp = max(C.clusters(E), key=lambda g: dn[g].sum()); ordem = sorted(grp, key=lambda i: -dn[i])
    acoes = [dict(a, m=_mag(a['magia'], a.get('sobre'))) for a in f['acoes']]
    persist = [a for a in acoes if a['m']['termino'] != 'um_turno']
    estado = {id(a): np.zeros((n, N), bool) for a in persist}
    presos = set(); principais = {}
    neg = np.zeros((n, N)); depois = C.rng.random(N) < 0.5; lr = [np.full(N, c['lr']) for c in E]
    man = set(r - 1 for r in f.get('penalidade_manutencao', {}).get('rounds', []))
    for r in range(R):
        inc = np.zeros((n, N))
        for a in (a for a in acoes if a['round'] - 1 == r):
            k = a.get('alvos', 1)
            if a.get('escala_area'): k = max(1, int(round(k * TOPO[topo]['area'])))
            base = [i for i in ordem if i not in presos] if a.get('selecao') == 'livre' else ordem
            alvos = (base or ordem)[:k]
            uw = a.get('penalidade', 'nao')
            for j, i in enumerate(alvos):
                usa_uw = uw == 'todos' or (uw == 'primeiro' and j == 0)
                fa = _fails(save(E[i], a['m']['save']), cd, usa_uw, lr[i], dado)
                if a['m']['termino'] == 'um_turno':
                    inc[i] = np.maximum(inc[i], fa * a['m']['peso'] * (0.5 if r == R - 1 else 1.0))
                else:
                    estado[id(a)][i] |= fa
            if a['m']['termino'] != 'um_turno':
                if a['m']['peso'] >= 1: presos.update(alvos)  # 'livre' = fora de efeito que nega o turno inteiro
                if uw == 'primeiro': principais[id(a)] = alvos[0]
        ativo = np.ones(N, bool) if r > 0 else depois
        for i in range(n):
            w = inc[i].copy()
            for a in persist: w = np.maximum(w, estado[id(a)][i] * a['m']['peso'])
            neg[i] += w * ativo
            for a in persist:
                st = estado[id(a)]
                if a['m']['termino'] == 'fim_turno':
                    uw = r in man and principais.get(id(a)) == i
                    sai = ~_fails(save(E[i], a['m']['save']), cd, uw, lr[i], dado if uw else 0)
                    st[i] &= ~(sai & ativo)
    return neg.mean(1) / R


TIPOS = dict(ameaca=_ameaca, sentinela=_sentinela, parada_oa=_parada_oa, area=_area, alvo_unico=_alvo_unico,
             alvo_unico_direto=_alvo_unico_direto, ataque_com_save=_ataque_com_save, melhor_de=_melhor_de,
             plano=_plano, esqueletos=_esqueletos, agarrao=_agarrao, ancestral_protectors=_ancestral,
             command_fixo=_command_fixo, ataque_nega_turno=_ataque_nega_turno)


def _avalia_fonte(f, E, topo, t):
    return {f.get('nome', f['tipo']): TIPOS[f['tipo']](f, E, topo, t)}


def compilar(fontes, corpo, nivel):
    """fontes do build.json -> fn(E, topo) -> {nome da fonte: vetor de negação por criatura}."""
    t = _corpo_t(corpo, nivel)
    for f in fontes:
        if f['tipo'] not in TIPOS: raise ValueError(f"tipo de fonte desconhecido: {f['tipo']}")

    def fn(E, topo):
        out = {}
        for f in fontes: out.update(_avalia_fonte(f, E, topo, t))
        return out or {'(nenhuma)': C.zero(E)}
    return fn
