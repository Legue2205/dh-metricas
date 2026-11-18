"""Tabelas de comparação entre builds (para análise, não para o site): por eixo, builds × níveis.

Builds de progressão (`gerado_de` / id "<base>-<nível>") viram uma linha com uma coluna por nível, para ver a curva.
Uso: python -m dh comparar [eixos…] [--visao padrao] [--grupo RPGBot] [--json]
"""
import json
import re

from .calibrar import EIXOS, NOME, valores


def _base(bid):
    m = re.fullmatch(r'(.+)-(\d+)', bid)
    return (m.group(1), int(m.group(2))) if m else (bid, None)


def tabela(dados, eixos=None, visao='padrao', grupos=None, como_json=False):
    vals = valores(dados, visao)
    sel = {b: v for b, v in vals.items() if not grupos or dados['builds'][b]['grupo'] in grupos}
    niveis = sorted({dados['builds'][b]['nivel'] for b in sel})
    linhas = {}
    for b, (ev, marca) in sel.items():
        base, _ = _base(b); nv = dados['builds'][b]['nivel']
        linhas.setdefault(base, {'grupo': dados['builds'][b]['grupo'], 'marca': '', 'v': {}})
        linhas[base]['v'][nv] = ev; linhas[base]['marca'] = linhas[base]['marca'] or marca
    eixos = [e for e in (eixos or EIXOS) if e in EIXOS]
    if como_json: return json.dumps({e: {b: {nv: x.get(e) for nv, x in l['v'].items()} for b, l in linhas.items()} for e in eixos}, ensure_ascii=False)
    f = lambda x: '   –' if x is None else f'{x:4.1f}'.replace('.', ',')
    out = [f'Visão: {visao}. ~ = sem esse plano (linha principal). Eixo ausente na build = –.']
    for e in eixos:
        out += ['', f'== {NOME[e]}', f"{'build':34s} {'grupo':10s} " + ' '.join(f'nv{n:<3d}' for n in niveis)]
        ordem = sorted(linhas.items(), key=lambda kv: -max([x.get(e, 0) for x in kv[1]['v'].values()] or [0]))
        for b, l in ordem:
            out.append(f"{(l['marca'] + b)[:34]:34s} {l['grupo'][:10]:10s} " + ' '.join(f"{f(l['v'].get(n, {}).get(e)) if n in l['v'] else '    '}  " for n in niveis))
    return '\n'.join(out)
