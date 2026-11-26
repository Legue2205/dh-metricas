"""G3 (sprint DragonHeist): top-10 / fundo-10 de cada eixo contra a lista de consenso (calibracao/meta-consenso.json).

A lista foi escrita ANTES de olhar os rankings (pré-registro). Este script só mede; não use a saída para editar a lista.

Uso (da raiz): python calibracao/meta_consenso.py [--nivel 7|11] [--com-holdout] [--visao misto] [--json] [--mostrar]
  sem --com-holdout, Artificer/Rogue/Sorcerer saem do ranking e das listas (holdout congelado até o G6).
  --mostrar imprime o top-10 e o fundo-10 de cada eixo (só depois de a lista estar aprovada).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

RAIZ = os.path.join(os.path.dirname(__file__), '..')
K, MIN_FORTE = 10, 7


def avaliar(valores, forte, fraco, k=K, min_forte=MIN_FORTE):
    """valores: {subclasse: número}. Ordem estável: valor decrescente, depois id. Devolve o veredito do eixo."""
    ordem = sorted(valores, key=lambda s: (-valores[s], s))
    topo, fundo = ordem[:k], ordem[-k:]
    forte, fraco = set(forte), set(fraco)
    r = dict(topo=topo, fundo=fundo,
             topo_forte=sum(s in forte for s in topo), topo_fraco=sum(s in fraco for s in topo),
             fundo_fraco=sum(s in fraco for s in fundo), fundo_forte=sum(s in forte for s in fundo), n=len(ordem))
    r['passa_topo'] = r['topo_forte'] >= min_forte and r['topo_fraco'] == 0
    r['passa_fundo'] = r['fundo_fraco'] >= min_forte and r['fundo_forte'] == 0
    r['passa'] = r['passa_topo'] and r['passa_fundo']
    return r


def medir(nivel, com_holdout=False, visao='misto'):
    from comparar_chassi import dados, rotulos, val
    meta = json.load(open(os.path.join(RAIZ, 'calibracao', 'meta-consenso.json'), encoding='utf-8'))
    hold = set(meta['holdout'])
    d, rot = dados(visao), rotulos()
    base = {b: f"{r['classe']}-{r['subclasse']}" for b, r in rot.items()
            if r['variante'] == 'sem-feat' and (com_holdout or r['classe'] not in hold)}
    out = {}
    for e, m in meta['eixos'].items():
        vs = {s: val(d, e, b, nivel) for b, s in base.items() if val(d, 'dano', b, nivel) is not None}
        vs = {s: (v or 0) for s, v in vs.items()}
        if not any(vs.values()): out[e] = dict(medido=False); continue
        nv = str(nivel)
        forte, fraco = list(m['forte'][nv]), list(m['fraco'][nv])
        if com_holdout: forte += m['forte_holdout'][nv]; fraco += m['fraco_holdout'][nv]
        out[e] = dict(medido=True, **avaliar(vs, forte, fraco))
    return out


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    visao = a[a.index('--visao') + 1] if '--visao' in a else 'misto'
    res = {nv: medir(nv, '--com-holdout' in a, visao) for nv in nvs}
    if '--json' in a: print(json.dumps(res, ensure_ascii=False, indent=1)); return
    for nv, r in res.items():
        print(f'== G3 nv{nv}' + (' (com holdout)' if '--com-holdout' in a else ' (sem holdout)'))
        for e, x in r.items():
            if not x['medido']: print(f'  {e:9s} não medido'); continue
            print(f"  {e:9s} topo {x['topo_forte']}/10 forte, {x['topo_fraco']} fraco · fundo {x['fundo_fraco']}/10 fraco, "
                  f"{x['fundo_forte']} forte  → {'PASSA' if x['passa'] else 'não passa'}")
            if '--mostrar' in a:
                print('     topo : ' + ', '.join(x['topo'])); print('     fundo: ' + ', '.join(x['fundo']))


if __name__ == '__main__':
    main()
