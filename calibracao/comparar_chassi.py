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


# Pistas por eixo do gabarito ("eixos": {"dano": "alto (…)"}) -> escala ordinal; eixo do gabarito -> eixo do motor.
ESCALA = {'nenhum': 0, 'fraco': 1, 'baixo': 1, 'básico': 1, 'baixo-médio': 1.5, 'médio': 2, 'média': 2,
          'médio-alto': 2.5, 'média-alta': 2.5, 'alto': 3, 'alta': 3, 'muito': 3, 'altíssimo': 3.5}
PISTA_EIXO = {'dano': 'dano', 'defesa': 'deff', 'controle': 'controle', 'area': 'area', 'suporte': 'suporte', 'corpo': 'corpo'}


def pista(txt):
    import re
    return ESCALA.get(re.split(r'[ (,;]', txt.strip().lower())[0])


def tau_eixos(d, rot, gabs, nv):
    """τ por régua: (a) eixo do motor × pista daquele eixo no gabarito, dentro de cada classe, combinado pela soma dos pares
    (média dos τ por classe ponderada por n) e agrupado entre classes (todas juntas; pistas são relativas à classe, então
    é só uma pista grosseira, útil para corpo/área, que têm poucas pistas por classe); (b) eixo do motor × nota geral da subclasse (o que a nota do RPGBot 'enxerga')."""
    out = {}
    for ge, me in PISTA_EIXO.items():
        por_cl, pesos, tot_n, todos = {}, 0, 0, []
        for cl, gab in gabs.items():
            xs = [(pista(gab[r['subclasse']]['eixos'][ge]), val(d, me, b, nv) or 0, r['subclasse'])
                  for b, r in rot.items() if r['classe'] == cl and r['variante'] == 'sem-feat' and r['subclasse'] in gab
                  and ge in (gab[r['subclasse']].get('eixos') or {}) and val(d, 'dano', b, nv) is not None]
            xs = [x for x in xs if x[0] is not None]
            tot_n += len(xs); todos.extend(xs)
            if len(xs) >= 3 and len({x[0] for x in xs}) > 1 and len({x[1] for x in xs}) > 1:
                t = tau_b([x[0] for x in xs], [x[1] for x in xs])
                por_cl[cl] = dict(tau=round(t, 2), n=len(xs)); pesos += len(xs)
        media = round(sum(x['tau'] * x['n'] for x in por_cl.values()) / pesos, 2) if pesos else None
        agr = round(tau_b([x[0] for x in todos], [x[1] for x in todos]), 2) if len(todos) >= 5 else None
        out[me] = dict(pista=dict(tau=media, n_usado=pesos, n_pistas=tot_n, por_classe=por_cl, agrupado=agr))
    for me in EIXOS:
        ts, ns = [], 0
        for cl, gab in gabs.items():
            xs = [(gab[r['subclasse']]['nota'], val(d, me, b, nv) or 0) for b, r in rot.items()
                  if r['classe'] == cl and r['variante'] == 'sem-feat' and r['subclasse'] in gab and val(d, 'dano', b, nv) is not None]
            if len(xs) >= 3 and len({x[1] for x in xs}) > 1:
                ts.append((tau_b([x[0] for x in xs], [x[1] for x in xs]), len(xs)))
        out.setdefault(me, {})['nota'] = dict(tau=round(sum(t * n for t, n in ts) / sum(n for _, n in ts), 2) if ts else None,
                                              n=sum(n for _, n in ts))
    return out


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    so = a[a.index('--classe') + 1] if '--classe' in a else None
    d, rot = dados(), rotulos()
    res = {'tau': {}, 'tau_eixos': {}, 'posicao': {}, 'feat': []}
    classes = sorted({r['classe'] for r in rot.values() if r['classe'] and (not so or r['classe'] == so)})
    gabs = {}
    for cl in classes:
        try:
            g = json.load(open(os.path.join(RAIZ, 'calibracao', f'rpgbot-{cl}.json'), encoding='utf-8'))
            gab = dict(g['subclasses'], **{s: {'nota': n} for s, n in g.get('sem_build', {}).items()})
        except FileNotFoundError: gab = {}
        gabs[cl] = gab
        for nv in nvs:
            xs = [(gab[r['subclasse']]['nota'], st.mean(val(d, e, b, nv) or 0 for e in EIXOS5), r['subclasse'])
                  for b, r in rot.items() if r['classe'] == cl and r['variante'] == 'sem-feat' and r['subclasse'] in gab
                  and val(d, 'dano', b, nv) is not None]
            if len(xs) >= 3:
                res['tau'].setdefault(cl, {})[nv] = dict(tau=round(tau_b([x[0] for x in xs], [x[1] for x in xs]), 2), n=len(xs),
                                                         ordem=sorted(([s, n, round(m, 1)] for n, m, s in xs), key=lambda r: -r[2]))
    for nv in nvs:
        res['tau_eixos'][nv] = tau_eixos(d, rot, gabs, nv)
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
    print('\n== τ por régua (variante sem feat; média dos τ dentro de cada classe, ponderada por n)')
    print('   pista = eixo × pista daquele eixo no gabarito (o teste da régua); nota = eixo × nota geral da subclasse')
    for nv, t in res['tau_eixos'].items():
        print(f'  nv{nv}')
        for e in EIXOS:
            p, n = t[e].get('pista'), t[e]['nota']
            sp = (f"pista {p['tau']:+.2f} (n={p['n_usado']}/{p['n_pistas']}, {len(p['por_classe'])} cl)"
                  if p and p['tau'] is not None else 'pista   —' + (f" (n={p['n_pistas']})" if p else ''))
            if p and p.get('agrupado') is not None: sp += f"  agrup. {p['agrupado']:+.2f}"
            sn = f"nota {n['tau']:+.2f} (n={n['n']})" if n['tau'] is not None else 'nota —'
            print(f'    {e:9s} {sp:52s} {sn}')
        if so:
            for e in EIXOS:
                for cl, x in (t[e].get('pista') or {}).get('por_classe', {}).items():
                    print(f'      {e} {cl}: {x["tau"]:+.2f} (n={x["n"]})')
    for nv, g in res['posicao'].items():
        print(f'\n== Por posição, nv{nv} (médias, sem feat)\n  {"posição":11s} {"n":>3s} ' + ' '.join(f'{e:>8s}' for e in EIXOS))
        for p, x in g.items(): print(f'  {p:11s} {x["n"]:3d} ' + ' '.join(f'{x[e]:8.1f}' for e in EIXOS))
    if res['feat']:
        print('\n== Feat (com − sem), por subclasse\n  ' + f'{"build":44s} {"nv":>3s} ' + ' '.join(f'{e:>8s}' for e in EIXOS))
        for x in sorted(res['feat'], key=lambda x: (x['build'], x['nv'])):
            print(f"  {x['build']:44s} {x['nv']:3d} " + ' '.join(f'{x[e]:+8.1f}' for e in EIXOS))


if __name__ == '__main__':
    main()
