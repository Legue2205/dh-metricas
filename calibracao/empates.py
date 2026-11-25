"""Empates dentro da classe (25/11): por que duas subclasses têm o mesmo valor num eixo, e se isso faz sentido.

Para cada classe e nível, agrupa as subclasses (chassi sem feat; dano com pacote_vh como no gate) com o MESMO valor no
eixo (visão misto, 0,1 de tolerância). Em cada grupo compara a linha usada no dia de foco daquele eixo:
  idêntico  — a parte da linha que conta no eixo é igual entre as builds (a subclasse não muda nada naquele eixo:
              empate legítimo se o RPGBot também não as separa, mecânica faltando se separa)
  diferente — specs diferentes que dão o mesmo número (coincidência ou teto/piso da régua)
e marca os grupos em que as pistas do RPGBot DISCORDAM (esses pares custam τ).

Uso (da raiz): python calibracao/empates.py [--nivel 7] [--eixo dano] [--so-discordantes]
"""
import collections
import glob
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from comparar_chassi import dados, pista, PISTA_EIXO  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), '..')
CHAVE = {'dano': 'dano', 'controle': 'controle', 'area': 'area', 'suporte': 'suporte'}
SPEC = {'dano': ('dano',), 'controle': ('controle',), 'area': ('area', 'dano'), 'suporte': ('suporte',)}


def _spec(b, lid, eixo):
    ls = {l['id']: l for l in b['linhas']}
    l = ls.get(lid) or b['linhas'][0]
    partes = {}
    for k in SPEC[eixo]:
        v = l.get(k)
        if v is None and l.get('herda'): v = ls.get(l['herda'], {}).get(k)
        partes[k] = v
    s = json.dumps(partes, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(s.encode()).hexdigest()[:8], s


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    eixos = [a[a.index('--eixo') + 1]] if '--eixo' in a else list(CHAVE)
    d = dados('misto')
    gab = {}
    for f in glob.glob(os.path.join(RAIZ, 'calibracao', 'rpgbot-*.json')):
        g = json.load(open(f, encoding='utf-8'))
        for s, x in g.get('subclasses', {}).items(): gab[(g['classe'], s)] = x.get('eixos') or {}
    resumo = collections.Counter()
    for nv in nvs:
        for eixo in eixos:
            eg = next(g for g, m in PISTA_EIXO.items() if m == eixo)
            grupos = collections.defaultdict(list)
            for f in sorted(glob.glob(os.path.join(RAIZ, 'builds', f'chassi-*-{nv}.json'))):
                b = json.load(open(f, encoding='utf-8'))
                if b.get('variante') != 'sem-feat': continue
                bid = b['id'].rsplit('-', 1)[0]
                v = d.get(CHAVE[eixo], {}).get(bid, {}).get(str(nv))
                if v is None: continue
                r = json.load(open(os.path.join(RAIZ, 'resultados', os.path.basename(f)), encoding='utf-8'))
                pl = r['planos'].get(f'foco_{eixo}') or r['planos']['padrao']
                lid = collections.Counter(c.get('linha') for c in pl.get('combates', [])).most_common(1)[0][0]
                h, _ = _spec(b, lid, eixo)
                p = gab.get((b['classe'], b['subclasse']), {}).get(eg)
                grupos[(b['classe'], round(v, 1))].append((b['subclasse'], lid, h, p, pista(p) if p else None))
            for (cl, v), xs in sorted(grupos.items()):
                if len(xs) < 2: continue
                ps = {x[4] for x in xs if x[4] is not None}
                disc = len(ps) > 1
                ident = len({x[2] for x in xs}) == 1
                resumo[(nv, eixo, 'idêntico' if ident else 'diferente', 'discorda' if disc else 'ok')] += len(xs)
                if '--so-discordantes' in a and not disc: continue
                print(f"nv{nv} {eixo:8s} {cl:10s} {v:5.1f} {'IDÊNTICO ' if ident else 'diferente'} {'PISTAS DISCORDAM' if disc else ''}")
                for sub, lid, h, p, pn in xs:
                    print(f"      {sub:22s} linha {lid:22s} spec {h}  pista {p or '—'}")
    print('\nResumo (nº de subclasses em grupos empatados):')
    for k, n in sorted(resumo.items()): print('  nv%s %-9s %-9s %-8s %d' % (*k, n))


if __name__ == '__main__':
    main()
