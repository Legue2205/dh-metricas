"""Modelo de anéis (ROADMAP, 13/11): cada build é um conjunto de linhas-opção.

Por eixo do painel (dano, deff, defm, controle, area, suporte):
  externo = máximo entre as linhas  (potencial: um eixo por vez, não todos juntos)
  interno = mínimo entre as linhas  (teste de estresse)
  intermediário = linha equilibrada = média do dia do plano `padrao` (o ranking padrão da build)
  misto = plano + α·(externo − plano), α = premissa aneis.alfa_versatilidade (D2, 23/11): visão do teste de régua
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
    def dia(p):
        def get(k, sub=None):
            x = p['eixos'].get(sub or k)
            return None if x is None else x['nivel_eq']
        return {k: v['n'] for k, v in eixos(get).items()}
    planos = res.get('planos', {})
    eq = dia(planos['padrao']) if 'padrao' in planos else None
    focos = {t: dia(p) for t, p in planos.items() if t.startswith('foco_')}
    if focos and eq is not None:
        # Planos de foco (16/11): os anéis viram dias inteiros — externo = melhor dia focado no eixo, interno = pior dia.
        dias = [eq] + list(focos.values()); mn, mx = {}, {}
        for k in EIXOS:
            vs = [d[k] if k in d else (0.0 if k in ATIVOS else None) for d in dias]
            vs = [v for v in vs if v is not None]
            if vs and any(k in d for d in dias): mn[k], mx[k] = min(vs), max(vs)
    fmt = lambda d: {k: dict(n=v, r=base.letra(v)) for k, v in d.items()}
    mi = None
    if eq is not None:
        from .premissas import P
        a = P('aneis.alfa_versatilidade')
        mi = {k: round(eq[k] + a * (mx[k] - eq[k]), 1) if k in mx else eq[k] for k in eq}
    return dict(interno=fmt(mn), externo=fmt(mx), equilibrado=fmt(eq) if eq is not None else None,
                misto=fmt(mi) if mi is not None else None, linhas=linhas,
                fonte='planos de foco' if focos and eq is not None else 'linhas',
                focos={t: fmt(d) for t, d in focos.items()})
