"""Concentração genérica (Etapa C, 24/11): a magia de concentração de uma linha cai com o dano que a build recebe.

Para cada linha com concentração (orcamento.concentracoes, ou controle.atencao.conc), fração média dos rounds em que a
magia ainda está de pé numa luta de R rounds:   f = (1/R) · Σ_{r=1..R} s^(r−1),   s = exp(−acertos · (1 − p)),
  acertos = acertos recebidos por round (premissa concentracao.acertos_por_round, pela posição; "front" se a linha
            declara controle.atencao.front) × concentracao.foco_inimigo
  p       = chance de passar no save de CON (CD 10; o dano por acerto do inimigo de referência quase nunca passa de 20
            até o nível ~15): d20 + CON ≥ 10, com vantagem se a build tem War Caster.
Linha de FORMA (Polymorph, Shapechange, Animal Shapes — tag "forma"): o save usa o CON da forma
(concentracao.forma_con) e ela fica na linha de frente.
Valor ajustado de cada eixo = base + f · (linha − base), base = a linha principal (a própria principal não é ajustada, mesmo
se tiver concentração — lacuna conhecida). Só o GANHO sobre a base cai (eixos em que a linha fica abaixo da base não
mudam: a ação gasta para conjurar não volta). Ajusta dano (DPR e níveis), suporte, área e controle (níveis e vidas). Os resultados das linhas
ficam BRUTOS (só ganham linha.concentracao = f e premissas); o ajuste vale para os planos, anéis e visões.
"""
import copy
import math
import re

from .premissas import P

FORMA = re.compile(r'polymorph|polimorf|shapechange|animal shapes', re.I)
CAMPOS = {'dano': ('dpr', 'dpr_regua', 'nivel_eq', 'nivel_bruta', 'nivel_precisa'),
          'suporte': ('total', 'ofensivo', 'defensivo', 'nivel_eq', 'nivel_ofensivo', 'nivel_defensivo'),
          'area': ('nivel_eq',),
          'controle': ('nivel_eq', 'nivel_campo', 'nivel_controle', 'vidas_total', 'vidas_campo')}
POS = {'defensor': 'front', 'striker': 'front', 'skirmisher': 'meio', 'meia': 'meio', 'atirador': 'tras',
       'retaguarda': 'tras'}


def _tem_conc(l, magias):
    from .orcamento import concentracoes
    return bool(concentracoes(l, magias)) or bool(((l.get('controle') or {}).get('atencao') or {}).get('conc'))


def fator(b, l, R=None):
    R = R or P('base.rounds_por_luta')
    forma = bool(FORMA.search(l.get('hipotese', '') + ' ' + l['id']))
    front = forma or bool(((l.get('controle') or {}).get('atencao') or {}).get('front'))
    grupo = 'front' if front else POS.get(b.get('posicao'), 'meio')
    h = P('concentracao.acertos_por_round')[grupo] * P('concentracao.foco_inimigo')
    con = P('concentracao.forma_con') if forma else (((b.get('corpo') or {}).get('saves') or {}).get('sv') or {}).get('con', 0)
    p = min(1.0, max(0.05, (21 - (10 - con)) / 20))
    if re.search(r'war caster', str(b.get('build', '')) + ' ' + str(b.get('feat', '')), re.I): p = 1 - (1 - p) ** 2
    s = math.exp(-h * (1 - p))
    f = sum(s ** (r - 1) for r in range(1, R + 1)) / R
    return dict(f=round(f, 3), p_save=round(p, 3), acertos=round(h, 2), grupo=grupo, forma=forma)


def _mistura(base, linha, f):
    if isinstance(linha, dict):
        return {k: _mistura((base or {}).get(k) if isinstance(base, dict) else None, v, f) for k, v in linha.items()}
    if isinstance(linha, (int, float)) and not isinstance(linha, bool) and isinstance(base, (int, float)):
        # só o GANHO da concentração cai; o que a linha já perdeu (ex.: a ação do round 1 gasta no Bless) não volta
        return round(base + f * (linha - base), 3) if linha > base else linha
    return linha


def ajustar(b, linhas):
    """(cópia de linhas com os ganhos de concentração ajustados, {linha: info}). Não mexe em linhas: os resultados
    gravados ficam brutos; só os planos (e o que sai deles: anéis, visões) usam a cópia ajustada."""
    from .controle import campo
    L = copy.deepcopy(linhas or {}); infos = {}
    if not P('concentracao.ativa'): return L, infos
    por_id = {l['id']: l for l in b.get('linhas', [])}
    principal = next((l for l in b.get('linhas', []) if l.get('principal')), (b.get('linhas') or [None])[0])
    if not principal or principal['id'] not in L: return L, infos
    xb = L[principal['id']]
    for lid, x in L.items():
        l = por_id.get(lid)
        if not l or lid == principal['id'] or not _tem_conc(l, campo.MAGIAS): continue
        info = fator(b, l)
        for eixo, campos in CAMPOS.items():
            d, db = x.get(eixo), xb.get(eixo)
            if not isinstance(d, dict) or not isinstance(db, dict): continue
            for k in campos:
                if k in d and k in db: d[k] = _mistura(db[k], d[k], info['f'])
        infos[lid] = info
    return L, infos
