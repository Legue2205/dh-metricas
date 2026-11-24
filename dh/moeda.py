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


def de_linha(x, nv):
    """Dano equivalente por luta de uma linha (resultado do motor), por parcela e total."""
    from . import area
    from .controle import atencao
    R = P('base.rounds_por_luta'); w = P('moeda.peso')
    pv = atencao.ref_padrao('conjurador', nv)['pv']
    hp0 = area.CR[area.HORDA[nv]][0]
    out = dict(
        dano=w['dano'] * _dpr(x.get('dano'), nv) * R,
        suporte=w['suporte'] * float((x.get('suporte') or {}).get('total') or 0) * R,
        controle=w['controle'] * float((x.get('controle') or {}).get('vidas_total') or 0) * pv,
        area=w['area'] * _frac_area(float((x.get('area') or {}).get('nivel_eq') or 0)) * area.NH * hp0)
    out['total'] = sum(out.values())
    return out
