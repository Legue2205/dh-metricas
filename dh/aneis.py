"""Modelo de anéis (ROADMAP, 13/11): cada build é um conjunto de linhas-opção.

Por eixo do painel (dano, deff, defm, controle, area, suporte):
  externo = máximo entre as linhas  (potencial: um eixo por vez, não todos juntos)
  interno = mínimo entre as linhas  (teste de estresse)
  intermediário = linha equilibrada = média do dia do plano `padrao` (o ranking padrão da build)
Eixo ativo (dano, controle, área, suporte) ausente numa linha = 0 (ela não faz aquilo), como nos planos.
Eixo passivo (deff, defm) ausente = ignorado (a linha não mexeu no corpo).
Linha com "aneis": false fica de fora (linhas antigas, de conferência).
Custo da linha: "gratuita" (postura, troca turno a turno) ou "gasta_recurso"; inferido dos espaços e de "usa"
se a linha não declarar "custo".
"""
from . import base

EIXOS = ('dano', 'deff', 'defm', 'controle', 'corpo', 'area', 'suporte')
ATIVOS = ('dano', 'controle', 'area', 'suporte')       # corpo é passivo: linha sem controle de corpo não conta 0


def eixos(get):
    """get(chave, sub=None) -> nível equivalente ou None. Devolve {eixo: {n, r}} só dos eixos com nota."""
    r = get('saves', 'resiliencia')
    vals = dict(dano=get('dano'), deff=base.defesa_fisica(get('defesa'), r), defm=base.defesa_magica(get('saves', 'vontade'), r),
                controle=get('controle', 'campo'), corpo=get('controle', 'corpo'), area=get('area'), suporte=get('suporte'))
    return {k: dict(n=round(x, 1), r=base.letra(x)) for k, x in vals.items() if x is not None}


def _nv(res, k, sub=None):
    from .planos import _nota
    return _nota((res or {}).get(k), sub)


def eixos_linha(res_linha):
    return eixos(lambda k, s=None: _nv(res_linha, k, s))


def custo(spec, res_linha):
    if spec.get('custo') in ('gratuita', 'gasta_recurso'): return spec['custo']
    o = res_linha.get('orcamento', {})
    gasta = any(o.get('espacos_por_eixo', {}).values()) or bool(o.get('outros'))
    return 'gasta_recurso' if gasta else 'gratuita'


def calcular(b, res):
    """b = build.json, res = resultados/<id>.json. None se nenhuma linha entra."""
    specs = {l['id']: l for l in b['linhas']}
    linhas = {}
    for lid, rl in res['linhas'].items():
        sp = specs.get(lid)
        if sp is None or sp.get('aneis', True) is False: continue
        linhas[lid] = dict(eixos=eixos_linha(rl), custo=custo(sp, rl))
    if not linhas: return None
    mn, mx = {}, {}
    for k in EIXOS:
        vs = [l['eixos'][k]['n'] if k in l['eixos'] else (0.0 if k in ATIVOS else None) for l in linhas.values()]
        vs = [v for v in vs if v is not None]
        if not any(k in l['eixos'] for l in linhas.values()): continue   # a build não tem nota nesse eixo
        mn[k], mx[k] = min(vs), max(vs)
    eq = None
    p = res.get('planos', {}).get('padrao')
    if p:
        def get(k, sub=None):
            x = p['eixos'].get(sub or k)
            return None if x is None else x['nivel_eq']
        eq = {k: v['n'] for k, v in eixos(get).items()}
    fmt = lambda d: {k: dict(n=v, r=base.letra(v)) for k, v in d.items()}
    return dict(interno=fmt(mn), externo=fmt(mx), equilibrado=fmt(eq) if eq is not None else None, linhas=linhas)
