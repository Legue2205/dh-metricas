"""Builds de chassi (22/11): comparação por classe (τ contra as cores do RPGBot), por posição e efeito do feat.

  1. τ por classe: nota RPGBot da subclasse × média de 5 eixos da variante SEM feat (o degrau que compara subclasses).
  2. Por posição: média de cada eixo das variantes sem feat, agrupadas pela posição que a subclasse escolheu.
  3. Feat: (com feat − sem feat) por eixo, por subclasse = sinergia daquela subclasse com aquele feat.

Uso (da raiz): python calibracao/comparar_chassi.py [--nivel 11] [--classe rogue] [--json]
Lê resultados via `python -m dh comparar --grupo Chassi --json` e os rótulos (classe/subclasse/posicao/feat) de builds/.
"""
import glob
import json
import os
import statistics as st
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from comparar_rpgbot import tau_b  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), '..')
EIXOS = ('dano', 'deff', 'defm', 'controle', 'area', 'suporte', 'corpo')
EIXOS5 = EIXOS[:5]


def dados():
    cmd = [sys.executable, '-m', 'dh', 'comparar', '--grupo', 'Chassi', '--json']
    return json.loads(subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, check=True).stdout)


def rotulos():
    out = {}
    for f in glob.glob(os.path.join(RAIZ, 'builds', 'chassi-*.json')):
        b = json.load(open(f, encoding='utf-8'))
        base = b['id'].rsplit('-', 1)[0]
        out[base] = {k: b.get(k) for k in ('classe', 'subclasse', 'posicao', 'feat', 'variante')}
    return out


def val(d, e, bid, nv): return d.get(e, {}).get(bid, {}).get(str(nv))


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    so = a[a.index('--classe') + 1] if '--classe' in a else None
    d, rot = dados(), rotulos()
    res = {'tau': {}, 'posicao': {}, 'feat': []}
    classes = sorted({r['classe'] for r in rot.values() if r['classe'] and (not so or r['classe'] == so)})
    for cl in classes:
        try: gab = json.load(open(os.path.join(RAIZ, 'calibracao', f'rpgbot-{cl}.json'), encoding='utf-8'))['subclasses']
        except FileNotFoundError: gab = {}
        for nv in nvs:
            xs = [(gab[r['subclasse']]['nota'], st.mean(val(d, e, b, nv) or 0 for e in EIXOS5), r['subclasse'])
                  for b, r in rot.items() if r['classe'] == cl and r['variante'] == 'sem-feat' and r['subclasse'] in gab
                  and val(d, 'dano', b, nv) is not None]
            if len(xs) >= 3:
                res['tau'].setdefault(cl, {})[nv] = dict(tau=round(tau_b([x[0] for x in xs], [x[1] for x in xs]), 2), n=len(xs),
                                                         ordem=sorted(([s, n, round(m, 1)] for n, m, s in xs), key=lambda r: -r[2]))
    for nv in nvs:
        grupos = {}
        for b, r in rot.items():
            if r['variante'] != 'sem-feat' or (so and r['classe'] != so) or val(d, 'dano', b, nv) is None: continue
            grupos.setdefault(r['posicao'], []).append(b)
        res['posicao'][nv] = {p: dict(n=len(bs), **{e: round(st.mean(val(d, e, b, nv) or 0 for b in bs), 1) for e in EIXOS},
                                      melhores={e: max(bs, key=lambda b: val(d, e, b, nv) or 0) for e in EIXOS})
                              for p, bs in sorted(grupos.items())}
        for b, r in rot.items():
            if r['variante'] != 'feat' or (so and r['classe'] != so): continue
            sem = f"chassi-{r['classe']}-{r['subclasse']}"
            if val(d, 'dano', b, nv) is None or val(d, 'dano', sem, nv) is None: continue
            res['feat'].append(dict(nv=nv, build=b, feat=r['feat'], **{e: round((val(d, e, b, nv) or 0) - (val(d, e, sem, nv) or 0), 1) for e in EIXOS}))
    if '--json' in a: print(json.dumps(res, ensure_ascii=False, indent=1)); return
    print('== τ por classe (nota RPGBot × média de 5 eixos, variante sem feat)')
    for cl, t in res['tau'].items():
        print(f'  {cl:10s} ' + '  '.join(f"nv{nv}: {x['tau']:+.2f} (n={x['n']})" for nv, x in t.items()))
    for nv, g in res['posicao'].items():
        print(f'\n== Por posição, nv{nv} (médias, sem feat)\n  {"posição":11s} {"n":>3s} ' + ' '.join(f'{e:>8s}' for e in EIXOS))
        for p, x in g.items(): print(f'  {p:11s} {x["n"]:3d} ' + ' '.join(f'{x[e]:8.1f}' for e in EIXOS))
    if res['feat']:
        print('\n== Feat (com − sem), por subclasse\n  ' + f'{"build":44s} {"nv":>3s} ' + ' '.join(f'{e:>8s}' for e in EIXOS))
        for x in sorted(res['feat'], key=lambda x: (x['build'], x['nv'])):
            print(f"  {x['build']:44s} {x['nv']:3d} " + ' '.join(f'{x[e]:+8.1f}' for e in EIXOS))


if __name__ == '__main__':
    main()
