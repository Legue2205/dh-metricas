"""Moeda comum "dano equivalente" (DE) por luta — Etapa B, adotada pelo usuário em 24/11 para o plano padrão automático.

Provisória (fase 1): serve para o plano escolher entre linhas de eixos diferentes sem somar níveis de réguas que ainda não
estão calibradas entre si. Dano causado = dano evitado (1:1). Conversões (premissas moeda.*):
  dano     = DPR na CA de referência do nível (moeda.ca_ref_base + nível ÷ moeda.ca_ref_niveis_por_ponto) × rounds
  suporte  = suporte.total (dano equivalente por round: ofensivo + defensivo) × rounds
  controle = vidas da party poupadas por luta (controle.vidas_total) × PV do membro padrão da party de referência
  área     = moeda.peso.area (parcela das lutas que são horda) × fração da horda que a referência tira no nível eq. da
             linha × PV total da horda do nível da build
Cada parcela ainda tem moeda.peso.<eixo>. Defesa e saves ficam de fora (passivos; quase não mudam entre linhas).
"""
from .premissas import P

_R1 = {}


def _ca_ref(nv): return P('moeda.ca_ref_base') + nv // P('moeda.ca_ref_niveis_por_ponto')


def _dpr(d, nv):
    dpr = (d or {}).get('dpr') or {}
    if not dpr: return 0.0
    alvo = _ca_ref(nv)
    k = min(dpr, key=lambda c: abs(int(c.split()[1]) - alvo))
    return float(dpr[k])


def _frac_area(L):
    from . import area
    if not _R1:
        s = area.CENARIOS['padrao']; r1, _ = area._regua_cache(s, area.N_MODO['rapido'])
        _R1.update({int(k): float(v) for k, v in r1.items()})
    if L <= 0: return 0.0
    if L < 1: return L * _R1[1]
    if L >= 20: return _R1[20]
    lo = int(L); a = L - lo
    return _R1[lo] * (1 - a) + _R1[lo + 1] * a


def _por_round(d, nv, R):
    """Dano de cada round na CA de referência (dano.por_round; sem perfil, o DPR em todos os rounds)."""
    pr = (d or {}).get('por_round')
    if pr:
        alvo = _ca_ref(nv); k = min(pr, key=lambda c: abs(int(c.split()[1]) - alvo))
        return [float(v) for v in pr[k]]
    return [_dpr(d, nv)] * R


def de_linha(x, nv):
    """Dano equivalente por luta de uma linha (resultado do motor), por parcela e total.
    25/11 (usuário): dano CAUSADO não vale 1:1 dano EVITADO. Conversão pelo abate: o dano do round r tira inimigos da
    luta e nega a fração dos rounds que faltam, (R − r + 0,5)/R, × moeda.k_abate (dano que o inimigo causa por luta ÷
    PV dele; ≈ 1 nos encontros do motor). Dano cedo vale mais (burst, Wall of Force no round 1); o constante vale
    ~metade. Suporte ofensivo (dano extra dos aliados) converte igual; suporte defensivo e controle já são dano evitado.
    Área: só nas lutas de horda (moeda.peso.area) e sem somar com o dano de alvo único (vale o maior dos dois)."""
    from . import area
    from .controle import atencao
    R = int(P('base.rounds_por_luta')); w = P('moeda.peso')
    conv = P('moeda.conversao') != '1:1'
    k = P('moeda.k_abate') if conv else 1.0
    pv = atencao.ref_padrao('conjurador', nv)['pv']
    hp0 = area.CR[area.HORDA[nv]][0]
    pr = _por_round(x.get('dano'), nv, R)
    tempo = [(R - r + 0.5) / R for r in range(1, R + 1)] if conv else [1.0] * R
    dano = w['dano'] * k * sum(d * t for d, t in zip(pr, tempo))
    sp = x.get('suporte') or {}
    if 'ofensivo' in sp or 'defensivo' in sp:
        sup = float(sp.get('ofensivo') or 0) * R * k * (0.5 if conv else 1.0) + float(sp.get('defensivo') or 0) * R
    else:
        sup = float(sp.get('total') or 0) * R * k * (0.5 if conv else 1.0)
    sup *= w['suporte']
    ctrl = w['controle'] * float((x.get('controle') or {}).get('vidas_total') or 0) * pv
    A = _frac_area(float((x.get('area') or {}).get('nivel_eq') or 0)) * area.NH * hp0 * k * (P('moeda.tempo_area') if conv else 1.0)
    extra_area = w['area'] * max(0.0, A - dano) if conv else w['area'] * A
    out = dict(dano=dano, suporte=sup, controle=ctrl, area=extra_area)
    out['total'] = sum(out.values())
    return out
