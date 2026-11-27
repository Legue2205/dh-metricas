"""G4 (sprint 26/11): τ da nota geral do RPGBot (cor 1–4) × valor total da build (P3, dh/valor.py), dentro da classe
e agrupado. Referências: média simples dos eixos (o baseline ingênuo do G6) e só o DPR.

Uso (da raiz): python calibracao/comparar_global.py [--nivel 7|11] [--com-holdout] [--fonte chassi|rpgbot] [--json]
  chassi (padrão): chassi sem feat de cada subclasse; rpgbot: as builds de exemplo (sem as variantes "-puro")."""
import glob
import json
import os
import sys

RAIZ = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, RAIZ); sys.path.insert(0, os.path.dirname(__file__))
from comparar_chassi import HOLDOUT  # noqa: E402
from comparar_rpgbot import tau_b  # noqa: E402
from dh import valor as V  # noqa: E402

E6 = ('dano', 'defesa', 'controle', 'area', 'suporte')


def _nivel_eixos(res):
    p = (res.get('planos') or {}).get('padrao', {}).get('eixos', {})
    def g(k):
        v = p.get(k); v = v.get('nivel_eq') if isinstance(v, dict) else v
        return float(v or 0)
    return g


def linhas(nivel, fonte='chassi', com_holdout=False):
    gab = {}
    for f in glob.glob(os.path.join(RAIZ, 'calibracao', 'rpgbot-*.json')):
        c = os.path.basename(f)[7:-5]
        if com_holdout or c not in HOLDOUT: gab[c] = json.load(open(f, encoding='utf-8'))['subclasses']
    out = []
    padrao = f'chassi-*-{nivel}.json' if fonte == 'chassi' else f'rpgbot-*-{nivel}.json'
    for f in glob.glob(os.path.join(RAIZ, 'resultados', padrao)):
        r = json.load(open(f, encoding='utf-8'))
        bid = r['id']; resto = bid.split('-', 1)[1].rsplit('-', 1)[0]
        if fonte == 'chassi':
            b = json.load(open(os.path.join(RAIZ, 'builds', bid + '.json'), encoding='utf-8'))
            if b.get('variante') != 'sem-feat': continue
            cl, sub = b.get('classe'), b.get('subclasse')
        else:
            if resto.endswith('-puro'): continue
            cl = resto.split('-')[0]; sub = resto[len(cl) + 1:]
        if cl not in gab or sub not in gab[cl] or gab[cl][sub].get('nota') is None: continue
        v = V.valor(r); g = _nivel_eixos(r)
        out.append(dict(classe=cl, sub=sub, nota=gab[cl][sub]['nota'], p3=v['dia'],
                        media=sum(g(k) for k in E6) / len(E6) + g('corpo') / 6, dpr=g('dano')))
    return out


def medir(nivel, fonte='chassi', com_holdout=False):
    xs = linhas(nivel, fonte, com_holdout)
    res = {}
    for k in ('p3', 'media', 'dpr'):
        num = den = 0; por = {}
        for cl in sorted({x['classe'] for x in xs}):
            g = [x for x in xs if x['classe'] == cl]
            if len(g) < 3 or len({x['nota'] for x in g}) < 2: continue
            t = tau_b([x['nota'] for x in g], [x[k] for x in g]); por[cl] = round(t, 2); num += t * len(g); den += len(g)
        res[k] = dict(tau=round(num / den, 2) if den else None, agrupado=round(tau_b([x['nota'] for x in xs], [x[k] for x in xs]), 2),
                      por_classe=por, n=len(xs))
    return res


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    fonte = a[a.index('--fonte') + 1] if '--fonte' in a else 'chassi'
    out = {nv: medir(nv, fonte, '--com-holdout' in a) for nv in nvs}
    if '--json' in a: print(json.dumps(out, ensure_ascii=False, indent=1)); return
    for nv, r in out.items():
        print(f"== G4 nv{nv} ({fonte}, {'com' if '--com-holdout' in a else 'sem'} holdout, n={r['p3']['n']})")
        for k, nome in (('p3', 'valor total P3'), ('media', 'média dos eixos (baseline)'), ('dpr', 'só dano (baseline)')):
            print(f"  {nome:28s} τ dentro {r[k]['tau']}  agrupado {r[k]['agrupado']}   {r[k]['por_classe']}")


if __name__ == '__main__':
    main()
