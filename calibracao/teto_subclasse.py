"""Teto da subclasse (24/11, análise A2): o RPGBot avalia a subclasse BEM construída; o chassi é uma build só.

Para cada subclasse com pista de dano no gabarito, compara quatro valores do eixo (visão misto por padrão):
  piso   = chassi sem feat (o que o teste de régua usa hoje)
  chassi = melhor variante de chassi (com ou sem feat)
  rpgbot = melhor build original do RPGBot (original ou -puro; muitas com multiclasse)
  teto   = máximo de todos
e calcula o τ por régua (pista × valor, dentro da classe, ponderado por n — mesmo método de comparar_chassi.tau_eixos)
para cada um. Com --lista mostra as subclasses em que o teto passa o piso por mais de 1 nível.

Uso (da raiz): python calibracao/teto_subclasse.py [--nivel 7] [--eixo dano] [--visao misto] [--lista] [--json]
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from comparar_chassi import pista, PISTA_EIXO  # noqa: E402
from comparar_rpgbot import tau_b, CLASSES  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), '..')
FONTES = ('piso', 'chassi', 'rpgbot', 'teto')


def comparar(grupo, visao):
    cmd = [sys.executable, '-m', 'dh', 'comparar', '--grupo', grupo, '--json', '--visao', visao]
    return json.loads(subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, check=True).stdout)


def gabaritos():
    out = {}
    for cl in CLASSES:
        f = os.path.join(RAIZ, 'calibracao', f'rpgbot-{cl}.json')
        if os.path.exists(f): out[cl] = json.load(open(f, encoding='utf-8'))['subclasses']
    return out


def candidatos(eixo, nv, visao):
    """{(classe, subclasse): {fonte: (valor, build)}}"""
    dc, dr = comparar('Chassi', visao).get(eixo, {}), comparar('RPGBot', visao).get(eixo, {})
    out = {}
    for f in glob.glob(os.path.join(RAIZ, 'builds', f'chassi-*-{nv}.json')):
        b = json.load(open(f, encoding='utf-8')); base = b['id'].rsplit('-', 1)[0]
        v = dc.get(base, {}).get(str(nv))
        if v is None: continue
        c = out.setdefault((b['classe'], b['subclasse']), {})
        if b.get('variante') == 'sem-feat': c['piso'] = (v, base)
        if v > c.get('chassi', (-1, ''))[0]: c['chassi'] = (v, base)
    for (cl, sub), c in out.items():
        for bid in (f'rpgbot-{cl}-{sub}', f'rpgbot-{cl}-{sub}-puro'):
            v = dr.get(bid, {}).get(str(nv))
            if v is not None and v > c.get('rpgbot', (-1, ''))[0]: c['rpgbot'] = (v, bid)
        c['teto'] = max((c[k] for k in ('chassi', 'rpgbot') if k in c), key=lambda x: x[0])
    return out


def tau(cands, gabs, eixo_gab, fonte, so_com_rpgbot=False):
    por_cl, pesos, todos = {}, 0, []
    for cl, gab in gabs.items():
        xs = []
        for sub, g in gab.items():
            p = pista((g.get('eixos') or {}).get(eixo_gab, '') or '') if (g.get('eixos') or {}).get(eixo_gab) else None
            c = cands.get((cl, sub))
            if p is None or not c or 'piso' not in c or (so_com_rpgbot and 'rpgbot' not in c): continue
            v = c.get(fonte, c['piso'])[0]      # sem build do RPGBot, a fonte "rpgbot" cai no piso
            xs.append((p, v))
        todos += xs
        if len(xs) >= 3 and len({x[0] for x in xs}) > 1 and len({x[1] for x in xs}) > 1:
            por_cl[cl] = (tau_b([x[0] for x in xs], [x[1] for x in xs]), len(xs)); pesos += len(xs)
    media = sum(t * n for t, n in por_cl.values()) / pesos if pesos else None
    agr = tau_b([x[0] for x in todos], [x[1] for x in todos]) if len(todos) >= 5 else None
    return dict(tau=media, n=pesos, agrupado=agr, por_classe={k: (round(t, 2), n) for k, (t, n) in por_cl.items()})


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    eixo = a[a.index('--eixo') + 1] if '--eixo' in a else 'dano'
    visao = a[a.index('--visao') + 1] if '--visao' in a else 'misto'
    eixo_gab = next(g for g, m in PISTA_EIXO.items() if m == eixo)
    gabs, res = gabaritos(), {}
    for nv in nvs:
        cands = candidatos(eixo, nv, visao)
        res[nv] = dict(todas={f: tau(cands, gabs, eixo_gab, f) for f in FONTES},
                       com_rpgbot={f: tau(cands, gabs, eixo_gab, f, True) for f in FONTES},
                       lista=sorted(([cl, sub, round(c['piso'][0], 1), round(c['teto'][0], 1), c['teto'][1]]
                                     for (cl, sub), c in cands.items() if 'piso' in c and c['teto'][0] - c['piso'][0] > 1),
                                    key=lambda r: r[2] - r[3]))
    if '--json' in a: print(json.dumps(res, ensure_ascii=False, indent=1)); return
    for nv, r in res.items():
        print(f'\n== {eixo} nv{nv} (visão {visao}) — τ pista × valor, dentro da classe')
        for grupo, rot in (('todas', 'todas as subclasses com pista (sem build RPGBot → piso)'), ('com_rpgbot', 'só subclasses com build do RPGBot')):
            print(f'  {rot}')
            for f in FONTES:
                t = r[grupo][f]
                print(f"    {f:7s} τ {t['tau']:+.2f} (n={t['n']})  agrup. {t['agrupado']:+.2f}" if t['tau'] is not None else f'    {f:7s} —')
        if '--lista' in a:
            print(f'  teto − piso > 1 nível ({len(r["lista"])}):')
            for cl, sub, p, t, b in r['lista']: print(f'    {cl:10s} {sub:24s} piso {p:5.1f} → teto {t:5.1f}  ({b})')


if __name__ == '__main__':
    main()
