"""Diagnóstico de uma régua (sprint 26/11): por classe, pista do gabarito × valor do motor e os pares discordantes.

Uso (da raiz): python calibracao/diag_eixo.py --eixo suporte [--nivel 7] [--visao misto] [--sem-holdout]
  --eixo usa o nome do gabarito (dano, defesa, controle, area, suporte, corpo)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from comparar_chassi import HOLDOUT, PISTA_EIXO, RAIZ, dados, pista, rotulos, val  # noqa: E402


def main():
    a = sys.argv
    ge = a[a.index('--eixo') + 1]; me = PISTA_EIXO[ge]
    nv = int(a[a.index('--nivel') + 1]) if '--nivel' in a else 7
    visao = a[a.index('--visao') + 1] if '--visao' in a else 'misto'
    d, rot = dados(visao), rotulos('--sem-holdout' in a)
    todos = []
    for cl in sorted({r['classe'] for r in rot.values()}):
        try: g = json.load(open(os.path.join(RAIZ, 'calibracao', f'rpgbot-{cl}.json'), encoding='utf-8'))['subclasses']
        except FileNotFoundError: continue
        xs = []
        for b, r in rot.items():
            if r['classe'] != cl or r['variante'] != 'sem-feat' or r['subclasse'] not in g: continue
            t = (g[r['subclasse']].get('eixos') or {}).get(ge)
            if t is None or pista(t, nv) is None: continue
            xs.append((pista(t, nv), val(d, me, b, nv) or 0, r['subclasse'], t))
        if not xs: continue
        todos += [(p, v, f'{cl}-{s}') for p, v, s, _ in xs]
        print(f'== {cl} (n={len(xs)})')
        for p, v, s, t in sorted(xs, key=lambda x: -x[1]): print(f'   {v:8.1f}  pista {p:3.1f}  {s:22s} {t[:70]}')
        disc = [(x[2], y[2]) for x in xs for y in xs if x[0] > y[0] and x[1] < y[1]]
        if disc: print('   discordantes (pista maior, valor menor): ' + '; '.join(f'{p}<{q}' for p, q in disc))
    print('== agrupado (valor decrescente)')
    for p, v, s in sorted(todos, key=lambda x: -x[1]): print(f'   {v:8.1f}  pista {p:3.1f}  {s}')


if __name__ == '__main__':
    main()
