"""Ranking da régua de dano (24/11): quem lidera, por nível, nas builds de chassi.

Para cada build de chassi (todas as variantes, com e sem feat): nível de dano nas visões misto / plano / externo, a linha
com mais dano (id, hipótese, DPR na CA de referência), as linhas que o plano usa, e as pistas do RPGBot (dano e nota).

Uso (da raiz): python calibracao/ranking_dano.py [--nivel 7] [--top 20] [--sem-feat] [--csv saida.csv]
"""
import csv
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from comparar_chassi import pista  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), '..')
CA_REF = {7: 'CA 15', 11: 'CA 16'}


def visao(v):
    cmd = [sys.executable, '-m', 'dh', 'comparar', '--grupo', 'Chassi', '--json', '--visao', v]
    return json.loads(subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, check=True).stdout)['dano']


def gabaritos():
    out = {}
    for f in glob.glob(os.path.join(RAIZ, 'calibracao', 'rpgbot-*.json')):
        g = json.load(open(f, encoding='utf-8'))
        for s, x in g.get('subclasses', {}).items():
            out[(g['classe'], s)] = (x.get('nota'), (x.get('eixos') or {}).get('dano'))
        for s, n in g.get('sem_build', {}).items():
            out.setdefault((g['classe'], s), (n, None))
    return out


def linhas(nv):
    rows = []
    vm, vp, ve, gab = visao('misto'), visao('padrao'), visao('externo'), gabaritos()
    for f in sorted(glob.glob(os.path.join(RAIZ, 'resultados', f'chassi-*-{nv}.json'))):
        r = json.load(open(f, encoding='utf-8'))
        b = json.load(open(os.path.join(RAIZ, 'builds', os.path.basename(f)), encoding='utf-8'))
        base = b['id'].rsplit('-', 1)[0]
        fora = {l['id'] for l in b['linhas'] if l.get('plano', True) is False and l.get('aneis', True) is False}
        ls = {k: v for k, v in r['linhas'].items() if 'dano' in v and k not in fora}
        melhor = max(ls, key=lambda k: ls[k]['dano']['nivel_eq'])
        plano = [c['linha'] for c in r['planos']['padrao']['combates']]
        nota, pd = gab.get((b['classe'], b['subclasse']), (None, None))
        rows.append(dict(
            build=base, classe=b['classe'], subclasse=b['subclasse'], feat=b.get('feat') or '-', posicao=b.get('posicao'),
            misto=vm.get(base, {}).get(str(nv)), plano=vp.get(base, {}).get(str(nv)), externo=ve.get(base, {}).get(str(nv)),
            melhor=melhor, dpr=ls[melhor]['dano']['dpr'].get(CA_REF[nv]), hipotese=ls[melhor]['hipotese'],
            linhas_plano='/'.join(dict.fromkeys(plano)), nota_rpgbot=nota, pista_dano=pd, pista_num=pista(pd) if pd else None))
    return [x for x in rows if x['misto'] is not None]


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    top = int(a[a.index('--top') + 1]) if '--top' in a else 20
    todas = []
    for nv in nvs:
        rs = linhas(nv)
        if '--sem-feat' in a: rs = [x for x in rs if x['feat'] == '-']
        rs.sort(key=lambda x: -x['misto'])
        for i, x in enumerate(rs, 1): x.update(nivel=nv, pos=i)
        todas += rs
        print(f'\n== nv{nv}: {len(rs)} builds, top {top} e últimas 10 (misto = nível de dano do teste de régua)')
        print(f'  {"#":>3s} {"build":46s} {"misto":>5s} {"plano":>5s} {"ext":>5s} {"DPR":>5s}  {"pista":14s} nota  melhor linha | plano')
        for x in rs[:top] + [None] + rs[-10:]:
            if x is None: print('  ...'); continue
            print(f"  {x['pos']:3d} {x['build'][7:]:46s} {x['misto']:5.1f} {x['plano'] or 0:5.1f} {x['externo'] or 0:5.1f} "
                  f"{x['dpr'] or 0:5.1f}  {(x['pista_dano'] or '—')[:14]:14s} {x['nota_rpgbot'] or '—'!s:>4}  "
                  f"{x['melhor']} | {x['linhas_plano']}")
    if '--csv' in a:
        with open(a[a.index('--csv') + 1], 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(todas[0])); w.writeheader(); w.writerows(todas)


if __name__ == '__main__':
    main()
