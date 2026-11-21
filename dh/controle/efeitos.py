"""Controle declarativo: transforma a lista "fontes" do build.json numa função fn(E, topo) -> {fonte: negação}.

Cada fonte é um dicionário com "tipo". Tipos disponíveis (ver README para exemplos):
  ameaca            corpo que atrai ataques (taunt soft)
  terreno           terreno difícil grande (Plant Growth)
  sentinela         taunt hard por ataque de oportunidade que para o movimento (Sentinel)
  parada_oa         taunt hard por probabilidade fixa de parar quem passa
  area              magia/efeito em área da biblioteca (Web, Hypnotic Pattern, Conquering Presence…)
  alvo_unico        magias de alvo único relançadas com os espaços dados (modo combinar ou melhor)
  alvo_unico_direto efeito de alvo único sem relançar (ex.: Wall of Force num alvo)
  ataque_com_save   save no acerto (Stunning Strike e afins)
  (qualquer fonte) "forcar_falha": Portent/Chronal Shift: chance por luta de o save inicial de 1 alvo falhar
  condicao_no_acerto condição da biblioteca no acerto ou por gatilho, com usos por luta (manobras, runas, flechas)
  counterspell      nega turnos de conjuradores inimigos (usos finitos; gasta reação e espaço)
  melhor_de         escolhe a opção que mais nega (ex.: concentração exclusiva Fear OU Polymorph)
  plano             roteiro round a round (Virgil), executado por um motor genérico
  esqueletos, agarrao, ancestral_protectors, command_fixo, ataque_nega_turno   (casos especiais registrados)
"""
import numpy as np

from ..base import R, TOPO, p_acerto, save, pv_com_pvt
from . import campo as C


def _corpo_t(corpo, nivel):
    return dict(nivel=nivel, ca=corpo['ca'], pv=pv_com_pvt(corpo), res=corpo.get('res', 1), adv=corpo.get('adv', 0),
                red=corpo.get('red', 0))


def _mag(nome, sobre=None):
    return C.magia(nome, **(sobre or {}))


from ..premissas import P, grupo as _grupo
PADROES = _grupo('controle.padroes')   # premissas controle.padroes.*: valores usados quando a fonte não informa


# ---------------- tipos simples ----------------
def _ameaca(f, E, topo, t): return C.soft(E, t)


def _sentinela(f, E, topo, t):
    b, n = f.get('bonus', 8), f.get('tentativas', PADROES['sentinela_tentativas'])
    return np.array([c['wb'] * TOPO[topo]['cruza'] * (1 - (1 - p_acerto(b, c['ca'])) ** n) * C.dil(t, c)
                     if c['melee'] else 0 for c in E])


def _parada_oa(f, E, topo, t):
    return np.array([c['wb'] * TOPO[topo]['cruza'] * f.get('p', C.H['p_disengage']) if c['melee'] else 0 for c in E])


def _terreno(f, E, topo, t):
    """Terreno difícil em área grande (Plant Growth): fração fixa do turno dos inimigos corpo a corpo."""
    if len(E) <= 1: return C.zero(E)
    return np.array([f.get('fator', PADROES['terreno_fator']) * TOPO[topo][f.get('chave_topo', 'pg')] if c['melee'] else 0 for c in E])


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
    um = [n for n, m in zip(f['magias'], ms) if m['termino'] == 'um_turno']
    if um:   # efeito de um turno (Command, Psychic Lance): cada espaço nega um turno se o alvo falhar; sem concentração
        vs = [_condicao_no_acerto({'efeito': n, 'cd': cd, 'usos': len([s for s in slots if s >= _mag(n)['nivel']]),
                                   'no_acerto': False}, E, topo, t) for n in um]
        resto = [n for n in f['magias'] if n not in um]
        if resto: vs.append(_alvo_unico(dict(f, magias=resto), E, topo, t))
        return max(vs, key=lambda v: C.tot(E, v))
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


def _condicao_no_acerto(f, E, topo, t):
    """Condição imposta no acerto (manobras, runas, flechas, empurrão telecinético) ou por gatilho sem ataque
    ("no_acerto": false, ex.: reação). Campos: "efeito" (nome em magias.json: save, peso, termino), "cd",
    "bonus" (lista dos ataques do turno), "usos" (por luta, fracionário ok; gasto no acerto, mesmo que o alvo passe).
    um_turno: cada sucesso nega só aquele turno e a tentativa se repete nos turnos seguintes enquanto houver usos.
    Persistentes: a 1ª falha no save prende até o término; tentativas seguintes só depois de um save bem-sucedido."""
    m = _mag(f['efeito']); cd, u = f['cd'], f['usos']; bonus = f.get('bonus', [])
    k = int(np.ceil(u)); fr = u - (k - 1)

    def g(c):
        p = 1.0 if f.get('no_acerto', True) is False else 1 - np.prod([1 - p_acerto(b, c['ca']) for b in bonus])
        mod = round(save(c, m.get('save') or 'Des'), 2)
        pf = float((~C.passa(mod, cd)).mean())
        if m['termino'] == 'um_turno':
            turnos = min(float(R), u / p if p else 0.0) * p            # turnos com tentativa
            sucesso = turnos * pf; sucesso = max(0.0, sucesso - min(sucesso, c['lr']))
            return sucesso * m['peso'] * (R - 0.5) / R / R
        estado = {0: 1.0}; v = 0.0                                     # usos gastos -> prob. (ainda sem sucesso)
        for r in range(R):
            novo = {}
            for gm, pr in estado.items():
                if gm >= k: novo[gm] = novo.get(gm, 0) + pr; continue
                a = 1.0 if gm < k - 1 else fr
                tent = pr * p * a
                v += tent * C.efeito1(mod, cd, m['peso'], m['termino'], c['lr'], False, False, False,
                                      round(save(c, 'For') - 2, 2), 0, r)
                novo[gm + 1] = novo.get(gm + 1, 0) + tent * (1 - pf)
                novo[gm] = novo.get(gm, 0) + pr - tent
            estado = novo
        return v
    return C.unico(E, g)


# ---------------- casos especiais registrados ----------------
def _esqueletos(f, E, topo, t): return C.esqueletos(E, f.get('pv', 133), f.get('ca_alvo', 18))


def _agarrao(f, E, topo, t):
    return C.unico(E, lambda c: C.agarra(round(c['fo'] + c['sb'], 2),
                                         C.H['reach_grande'] if c['cr'] >= 5 else C.H['reach_pequeno'],
                                         round(C.dil(t, c), 3), f.get('bonus', 7)),
                   filtro=lambda c: c['melee'])


def _ancestral(f, E, topo, t):
    pa = TOPO[topo]['alc_corpo_a_corpo_atras']; b = f.get('bonus', 8)

    def g(c):
        p1 = p_acerto(b, c['ca']); p1a = p_acerto(b, c['ca'], 1); pn = p_acerto(c['atk'], 15)
        marc = (1 - pa) * (1 - 0.5 * pn) + pa * C.dil(t, c)
        turnos = sum((1 - (1 - (p1 if r == 0 else p1a)) ** 2) * (1 if r < R - 1 else 0.5) for r in range(R))
        fator = 1.0 if f.get('resistencia', True) else P('controle.marca.fator_sem_resistencia')
        return turnos / R * marc * fator
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


def _counterspell(f, E, topo, t):
    """Nega o turno de inimigos conjuradores: usos finitos por luta, repartidos entre eles.
    Espaço >= nível da magia inimiga anula direto; abaixo, teste de habilidade (CD 10 + nível)."""
    conj = [i for i, c in enumerate(E) if c['papel'] == 'Conjurador']
    v = C.zero(E)
    if not conj: return v
    slot, mod = f.get('slot', 3), f.get('mod', 0)
    for i in conj:
        nv = min(9, max(1, int(-(-E[i]['cr'] // 2))))          # maior círculo típico de um conjurador desse CR
        p = 1.0 if nv <= slot else min(1.0, max(0.0, (21 - (10 + nv - mod)) / 20))
        v[i] = min(R, f.get('usos_luta', 1) / len(conj)) / R * p * f.get('fracao_conjurando', PADROES['counterspell_fracao_conjurando'])
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


TIPOS = dict(ameaca=_ameaca, terreno=_terreno, sentinela=_sentinela, parada_oa=_parada_oa, area=_area, alvo_unico=_alvo_unico,
             alvo_unico_direto=_alvo_unico_direto, ataque_com_save=_ataque_com_save, melhor_de=_melhor_de,
             plano=_plano, esqueletos=_esqueletos, agarrao=_agarrao, ancestral_protectors=_ancestral,
             command_fixo=_command_fixo, counterspell=_counterspell, ataque_nega_turno=_ataque_nega_turno,
             condicao_no_acerto=_condicao_no_acerto)


def _avalia_fonte(f, E, topo, t):
    """"topos": [...] na fonte = só vale nessas topologias (o personagem escolhe a magia pelo terreno)."""
    nome = f.get('nome', f['tipo'])
    if 'topos' in f and topo not in f['topos']: return {nome: C.zero(E)}
    if f.get('forcar_falha'): return {nome: _forcar_falha(f, E, topo, t)}
    return {nome: TIPOS[f['tipo']](f, E, topo, t)}


def _sem_save(f):
    """Cópia da fonte em que o save INICIAL falha (os resaves continuam normais)."""
    g = {k: v for k, v in f.items() if k != 'forcar_falha'}
    if g['tipo'] in ('area', 'alvo_unico_direto'): g['sobre'] = dict(g.get('sobre') or {}, sem_save=True)
    elif g['tipo'] == 'alvo_unico': g['sobre'] = {m: dict((g.get('sobre') or {}).get(m, {}), sem_save=True) for m in g['magias']}
    else: return None
    return g


def _forcar_falha(f, E, topo, t):
    """Portent, Chronal Shift, Silvery Barbs e afins (19/11): "forcar_falha" = chance, por luta, de transformar o save
    inicial de UM alvo da magia em falha (usos por dia ÷ lutas, no máximo 1). Em área, o ganho vale para 1 dos alvos.
    Em melhor_de, a chance passa para cada opção."""
    u = min(1.0, f['forcar_falha'])
    base = {k: v for k, v in f.items() if k != 'forcar_falha'}
    if f['tipo'] == 'melhor_de':
        base['opcoes'] = [dict(o, forcar_falha=u) for o in f['opcoes']]
        return TIPOS['melhor_de'](base, E, topo, t)
    v0 = TIPOS[f['tipo']](base, E, topo, t); g = _sem_save(base)
    if g is None: return v0
    v1 = TIPOS[g['tipo']](g, E, topo, t)
    k = 1.0
    if f['tipo'] == 'area': k = max(1.0, float(f.get('alvos', _mag(f['magia']).get('alvos', 1))))
    return v0 + u * (v1 - v0) / k


def compilar(fontes, corpo, nivel):
    """fontes do build.json -> fn(E, topo) -> {nome da fonte: vetor de negação por criatura}."""
    t = _corpo_t(corpo, nivel)
    for f in fontes:
        if f['tipo'] not in TIPOS: raise ValueError(f"tipo de fonte desconhecido: {f['tipo']}")
        for tp in f.get('topos', []):
            if tp not in TOPO: raise ValueError(f"topologia desconhecida: {tp} (use {', '.join(TOPO)})")

    def fn(E, topo):
        out = {}
        for f in fontes: out.update(_avalia_fonte(f, E, topo, t))
        return out or {'(nenhuma)': C.zero(E)}
    # Fontes de corpo (ataques desviados para um corpo que aguenta): medidas no eixo Corpo (atenção), não no Controle.
    fn.corpo = {f.get('nome', f['tipo']) for f in fontes if f['tipo'] in TIPOS_CORPO}
    # 18/11: parte da negação de uma fonte de corpo pode contar no Controle (premissa controle.peso_no_controle.<tipo>)
    from ..premissas import P
    fn.peso_ctrl = {f.get('nome', f['tipo']): P(f"controle.peso_no_controle.{f['tipo']}") for f in fontes if f['tipo'] in TIPOS_CORPO}
    # 19/11: marcas entram na atenção como redução do dano do marcado contra os aliados de quem marcou
    fn.marca = {f.get('nome', f['tipo']) for f in fontes if f['tipo'] in TIPOS_MARCA}
    return fn


TIPOS_CORPO = {'ameaca', 'sentinela', 'parada_oa', 'esqueletos', 'ancestral_protectors'}   # marcas no Corpo desde 19/11
TIPOS_MARCA = {'ancestral_protectors'}   # no Corpo: reduzem o dano do marcado contra os outros membros (atencao.vida)
