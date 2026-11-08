"""Controle de campo: fração dos turnos inimigos negada (Monte Carlo vetorizado).

Porta fiel de control_enc.py (efeito1, seq1, área, alvo único, Sleep, ameaça) com duas mudanças:
  - N e a semente vêm de configurar() (modo rápido usa N menor);
  - os efeitos das magias vêm de magias.json (uma tabela só, usada pelos personagens E pela régua).
"""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from ..base import R, SAVE_TIPO, TOPO, n_ataques, p_acerto, save

ARQ_MAGIAS = Path(__file__).parent / 'magias.json'
MAGIAS = {k: v for k, v in json.loads(ARQ_MAGIAS.read_text(encoding='utf-8')).items() if not k.startswith('_')}
H = dict(golpes_party=2, taunt_ameaca=0.15, taunt_summon=0.4, p_disengage=0.5, reach_grande=0.5, reach_pequeno=0.2)
FIM = {'fim_turno': 0, 'luta': 1, 'inicio_turno': 2, 'escape': 3}

N = 8000
rng = np.random.default_rng(11)


def configurar(n=8000, semente=11):
    global N, rng
    N = n; rng = np.random.default_rng(semente)
    for f in (efeito1, seq1, stun, agarra):
        f.cache_clear()


def passa(mod, cd, adv=False, n=None):
    n = n or N
    a = rng.integers(1, 21, n)
    if adv: a = np.maximum(a, rng.integers(1, 21, n))
    return a + mod >= cd


def magia(nome, **sobre):
    """Efeito de uma magia da biblioteca, com sobrescritas da build (ex.: ataque, peso)."""
    m = dict(MAGIAS[nome]); m.update(sobre); m['id'] = nome
    return m


# ---------------- efeito numa criatura ----------------
@lru_cache(maxsize=None)
def efeito1(mod, cd, peso, fim, lr=0, sem_save=False, adv_resave=False, resave_fora=False, esc=0.0, saves_dano=0,
            atraso=0):
    """Fração dos R turnos de UMA criatura negada (ponderada pelo peso). atraso: rounds até a magia sair."""
    afet = np.ones(N, bool) if sem_save else ~passa(mod, cd)
    lr_left = np.full(N, lr)
    if lr and not sem_save:
        usa = afet & (lr_left > 0); afet &= ~usa; lr_left -= usa
    neg = np.zeros(N); depois = rng.random(N) < 0.5
    for r in range(atraso, R):
        ativo = np.ones(N, bool) if r > atraso else depois
        if resave_fora and r > atraso: afet |= ~afet & ~passa(mod, cd)
        if fim == 'inicio_turno':
            perde = afet & ~passa(mod, cd)
            if lr: usa = perde & (lr_left > 0); perde &= ~usa; lr_left -= usa
            neg += perde * ativo * peso; continue
        for _ in range(saves_dano): afet &= ~passa(mod, cd, True)
        neg += afet * ativo * peso
        if fim == 'fim_turno':
            sai = passa(mod, cd, adv_resave)
            if lr: usa = afet & ~sai & (lr_left > 0); sai |= usa; lr_left -= usa
            afet &= ~(sai & ativo)
        elif fim == 'escape':
            afet &= ~(passa(esc, cd) & ativo)
    return float(neg.mean() / R)


def ckey(c): return (c['ca'], round(c['fr'], 2), round(c['fo'], 2), c['sb'], c['lr'], c['cr'])


def _tupla(m):
    """Magia -> tupla hashable (nível, nome, atr, peso, fim, ataque, adv_resave, saves_dano, sem_save)."""
    sd = H['golpes_party'] if m.get('saves_dano') == 'golpes_party' else int(m.get('saves_dano', 0))
    return (m['nivel'], m['id'], m.get('save'), m.get('peso'), m['termino'], m.get('ataque', 0),
            bool(m.get('adv_resave', False)), sd, bool(m.get('sem_save', False)))


@lru_cache(maxsize=None)
def seq1(ck, cd, slots, spells):
    """Uma criatura: relança sempre que não há efeito ativo, do maior espaço para o menor."""
    ca, fr, fo, sb, lr, cr = ck

    def smod(atr): return fr + (fo - fr) * SAVE_TIPO[atr] + sb
    peso_slow = max(0.25, 1 - 1 / n_ataques(cr) + 0.05)

    def val(m):
        lv, nome, atr, p, f, atq, adv_r, sd, ss = m
        p = peso_slow if p is None else p
        v = efeito1(round(smod(atr or 'Car'), 2), cd, p, f, 0, ss, adv_r, False, round(smod('For') - 2, 2), sd)
        return v * (p_acerto(atq, ca) if atq else 1)
    rank = {m[1]: val(m) for m in spells}
    escolha = {s: max((m for m in spells if m[0] <= s), key=lambda m: rank[m[1]], default=None) for s in set(slots)}
    act = np.zeros(N, bool); peso = np.zeros(N); fim = np.zeros(N, int); mod = np.zeros(N)
    adv = np.zeros(N, bool); esc = np.zeros(N); sd = np.zeros(N, int)
    idx = np.zeros(N, int); neg = np.zeros(N); q = np.zeros(N); lr_left = np.full(N, lr)
    depois = rng.random(N) < 0.5

    def turno(mask):
        nonlocal act, neg, lr_left, q
        for t in range(H['golpes_party']):
            qq = mask & act & (sd > t)
            act &= ~(qq & (np.maximum(rng.integers(1, 21, N), rng.integers(1, 21, N)) + mod >= cd))
        m = mask & act
        ini = m & (fim == 2); falha = ini & ~(rng.integers(1, 21, N) + mod >= cd)
        usa = falha & (lr_left > 0); falha &= ~usa; lr_left -= usa; q += usa
        neg += falha * peso
        out = m & (fim != 2); neg += out * peso
        a = rng.integers(1, 21, N); a = np.where(adv, np.maximum(a, rng.integers(1, 21, N)), a)
        fs = out & (fim == 0); sai = a + mod >= cd
        usa = fs & ~sai & (lr_left > 0); lr_left -= usa; q += usa
        act &= ~(fs & (sai | usa))
        fe = out & (fim == 3); act &= ~(fe & (rng.integers(1, 21, N) + esc >= cd))
    for r in range(R):
        turno(~depois)
        cast = ~act & (idx < len(slots))
        for j, s in enumerate(slots):
            m = escolha[s]
            if m is None: continue
            sel = cast & (idx == j)
            if not sel.any(): continue
            lv, nome, atr, p, f, atq, adv_r, sdn, ss = m
            p = peso_slow if p is None else p
            ok = sel.copy()
            if atq:
                a = rng.integers(1, 21, N); ok &= (a == 20) | ((a != 1) & (a + atq >= ca))
            if not ss:
                ok &= ~(rng.integers(1, 21, N) + smod(atr) >= cd)
                usa = ok & (lr_left > 0); ok &= ~usa; lr_left -= usa; q += usa
            act |= ok
            peso = np.where(ok, p, peso); fim = np.where(ok, FIM[f], fim)
            mod = np.where(ok, smod(atr) if atr else 0, mod); adv = np.where(ok, adv_r, adv)
            esc = np.where(ok, smod('For') - 2, esc); sd = np.where(ok, sdn, sd)
        idx += cast
        turno(depois)
    return float(neg.mean() / R), float(q.mean())


# ---------------- alvos ----------------
def clusters(E):
    melee = [i for i, c in enumerate(E) if c['melee']]; back = [i for i, c in enumerate(E) if not c['melee']]
    return [g for g in (melee, back) if g]


def tot(E, v):
    w = np.array([c['dn'] for c in E]); return float((v * w).sum() / w.sum())


def jv(*vs):
    out = np.ones(len(vs[0]))
    for v in vs: out *= (1 - v)
    return 1 - out


def zero(E): return np.zeros(len(E))


def area(E, k, f, topo, mult_key='area'):
    """Aplica f(c) nos k alvos de maior dano do melhor grupo (corpo a corpo ou backline)."""
    k = max(1, int(round(k * TOPO[topo][mult_key])))
    best = None
    for g in clusters(E):
        alvos = sorted(g, key=lambda i: -E[i]['dn'])[:k]
        v = np.zeros(len(E))
        for i in alvos: v[i] = f(E[i])
        if best is None or tot(E, v) > tot(E, best): best = v
    return best if best is not None else zero(E)


def unico(E, f, filtro=None):
    """Aplica f no alvo único que mais rende."""
    best = zero(E)
    for i, c in enumerate(E):
        if filtro and not filtro(c): continue
        v = zero(E); v[i] = f(c)
        if tot(E, v) > tot(E, best): best = v
    return best


def f_area(cd, m, atraso=0):
    """Efeito de área de uma magia da biblioteca numa criatura."""
    def f(c):
        return efeito1(round(save(c, m.get('save') or 'Des'), 2), cd, m['peso'], m['termino'], c['lr'],
                       bool(m.get('sem_save', False)), False, bool(m.get('resave_fora', False)),
                       round(save(c, 'For') - 2, 2), 0, atraso)
    return f


def sleep(E, topo):
    pool = rng.integers(1, 9, (5, N)).sum(0)
    v = zero(E); dorm = 0
    for i in sorted(range(len(E)), key=lambda i: E[i]['hp']):
        if E[i]['lr']: break
        dorm += E[i]['hp']; v[i] = float((pool >= dorm).mean()) * (R - 0.5) / R
    return v


# ---------------- corpo: ameaça e taunts ----------------
def dil(t, c):
    """Quanto o personagem 'aguenta' o ataque de c comparado a um corpo frágil do mesmo nível (0 = nada)."""
    d = c['dn'] / n_ataques(c['cr']); red = 0 if c['cr'] >= 10 else t.get('red', 0)
    fhp = 8 + 6 * (t['nivel'] - 1)
    pt = p_acerto(c['atk'], t['ca'], t.get('adv', 0)) * max(0, d * t.get('res', 1) - red) / t['pv']
    pf = p_acerto(c['atk'], 15) * d / fhp
    return max(0.0, 1 - pt / pf)


def soft(E, t):
    return np.array([c['wb'] * H['taunt_ameaca'] * (1 - c['mal'] / 3) * dil(t, c) if c['melee'] else 0 for c in E])


@lru_cache(maxsize=None)
def stun(ca, mod, lr, bonus, cd, penalidade):
    """Save no acerto (Stunning Strike e afins): 1 tentativa por turno no 1º acerto; nega o turno seguinte."""
    lr_left = np.full(N, lr); depois = rng.random(N) < 0.5; neg = np.zeros(N)
    for r in range(R):
        algum = np.zeros(N, bool)
        for b in bonus:
            a = rng.integers(1, 21, N); algum |= (a == 20) | ((a != 1) & (a + b - penalidade * r >= ca))
        falha = algum & ~passa(mod, cd)
        usa = falha & (lr_left > 0); falha &= ~usa; lr_left -= usa
        neg += falha & (depois | (r < R - 1))
    return float(neg.mean() / R)


def esqueletos(E, pv=133, ca_alvo=18):
    capt = np.array([c['wb'] * H['taunt_summon'] * (1 - c['mal'] / 3) if c['melee'] else 0 for c in E])
    dano = sum(capt[i] * p_acerto(c['atk'], ca_alvo) * c['dn'] for i, c in enumerate(E))
    rounds = min(R, pv / max(1e-9, dano))
    return capt * rounds / R


@lru_cache(maxsize=None)
def agarra(fmod, p_reach, d, bonus=7):
    agarrado = np.zeros(N, bool); depois = rng.random(N) < 0.5; neg = np.zeros(N)

    def fj(): return np.maximum(rng.integers(1, 21, N), rng.integers(1, 21, N)) + bonus

    def ini(mask):
        nonlocal agarrado, neg
        m = mask & agarrado; reach = rng.random(N) < p_reach
        neg += np.where(m & reach, d, 0) + np.where(m & ~reach, 1.0, 0)
        agarrado &= ~(m & ~reach & (rng.integers(1, 21, N) + fmod > fj()))
    for r in range(R):
        ini(~depois if r == 0 else np.zeros(N, bool))
        agarrado |= ~agarrado & (fj() > rng.integers(1, 21, N) + fmod)
        ini(depois if r == 0 else np.ones(N, bool))
    return float(neg.mean() / R)
