"""Diff do τ por régua contra a baseline congelada (TASKS.md).
Uso (da raiz): python calibracao/diff_baseline.py [--visao padrao|externo] [--base calibracao/baseline/p1-chassi-<visao>.json]
Mostra o τ por régua (pista, dentro da classe) antes → depois, no geral e por classe, só onde mudou."""
import json, os, subprocess, sys

RAIZ = os.path.join(os.path.dirname(__file__), '..')
a = sys.argv
vis = a[a.index('--visao') + 1] if '--visao' in a else 'externo'
base = a[a.index('--base') + 1] if '--base' in a else os.path.join(RAIZ, 'calibracao', 'baseline', f'p1-chassi-{vis}.json')
B = json.load(open(base))
D = json.loads(subprocess.run([sys.executable, os.path.join(RAIZ, 'calibracao', 'comparar_chassi.py'), '--json', '--visao', vis],
                              capture_output=True, text=True, check=True, cwd=RAIZ).stdout)
print(f'== τ por régua, visão {vis}: baseline → agora')
for nv in D['tau_eixos']:
    for e, x in D['tau_eixos'][nv].items():
        p, q = (B['tau_eixos'].get(nv, {}).get(e) or {}).get('pista') or {}, x.get('pista') or {}
        if p.get('tau') != q.get('tau') or p.get('agrupado') != q.get('agrupado'):
            print(f"  nv{nv} {e:9s} {p.get('tau')} → {q.get('tau')}   agrup. {p.get('agrupado')} → {q.get('agrupado')}")
        for cl in sorted(set(p.get('por_classe', {})) | set(q.get('por_classe', {}))):
            t0, t1 = (p.get('por_classe', {}).get(cl) or {}).get('tau'), (q.get('por_classe', {}).get(cl) or {}).get('tau')
            if t0 != t1: print(f"      {cl:10s} {t0} → {t1}")
for cl in D['tau']:
    for nv in D['tau'][cl]:
        t0 = (B['tau'].get(cl, {}).get(nv) or {}).get('tau'); t1 = D['tau'][cl][nv]['tau']
        if t0 != t1: print(f'  τ médio {cl} nv{nv}: {t0} → {t1}')
