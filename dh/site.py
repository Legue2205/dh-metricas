"""Gera o site estático (docs/index.html) a partir de resultados/*.json. Sem servidor: um arquivo só."""
import json
from pathlib import Path

from .planos import CATEGORIAS, TAGS

RAIZ = Path(__file__).resolve().parents[1]
MODELO = Path(__file__).with_name('site.html')


def gerar(destino=None):
    builds = [json.loads(f.read_text(encoding='utf-8')) for f in sorted((RAIZ / 'resultados').glob('*.json'))]
    for b in builds:                                  # só o que a página usa
        for l in b['linhas'].values():
            for e in ('controle', 'area', 'suporte'):
                if e in l: l[e] = {k: v for k, v in l[e].items() if k in ('nivel_eq', 'rank', 'nivel_absoluto', 'melhor', 'perfil')}
            if 'dano' in l: l['dano'] = {k: l['dano'][k] for k in ('nivel_eq', 'rank', 'perfil')}
    dados = dict(builds=builds, tags=list(TAGS), categorias=CATEGORIAS)
    html = MODELO.read_text(encoding='utf-8').replace('/*DADOS*/null', json.dumps(dados, ensure_ascii=False).replace('</', '<\\/'))
    destino = Path(destino or RAIZ / 'docs' / 'index.html'); destino.parent.mkdir(exist_ok=True)
    destino.write_text(html, encoding='utf-8')
    return destino
