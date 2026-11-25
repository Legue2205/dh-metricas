"""Escolhas dos conjuradores (25/11): o que o plano padrão (moeda DE, concentração) manda cada build conjurar, e de onde
vem o valor de cada luta (dano, suporte, controle, área). Para olhar se as escolhas fazem sentido de mesa.

Uso (da raiz): python calibracao/escolhas_casters.py [--nivel 7] [--classe wizard] [--detalhe]
"""
import collections
import glob
import json
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from dh import moeda  # noqa: E402

CASTERS = ('wizard', 'sorcerer', 'cleric', 'druid', 'bard', 'warlock', 'paladin', 'ranger', 'artificer')


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    cls = [a[a.index('--classe') + 1]] if '--classe' in a else CASTERS
    for nv in nvs:
        print(f'\n== nv{nv}: plano padrão (4 lutas: 2 prioritárias pesam 2) — fonte do valor em dano equivalente')
        for cl in cls:
            fontes = collections.Counter(); linhas = collections.Counter(); n = 0
            for f in sorted(glob.glob(f'builds/chassi-{cl}-*-{nv}.json')):
                b = json.load(open(f, encoding='utf-8'))
                if b.get('variante') != 'sem-feat': continue
                r = json.load(open('resultados/' + os.path.basename(f), encoding='utf-8'))
                comb = [c.get('linha') for c in r['planos']['padrao'].get('combates', [])]
                n += 1
                det = []
                for lid in comb:
                    de = moeda.de_linha(r['linhas'][lid], nv)
                    for k in ('dano', 'suporte', 'controle', 'area'): fontes[k] += de[k]
                    linhas[lid] += 1
                    det.append(f"{lid}({de['total']:.0f}: d{de['dano']:.0f} s{de['suporte']:.0f} c{de['controle']:.0f} a{de['area']:.0f})")
                if '--detalhe' in a: print(f"   {b['subclasse']:22s} " + ' | '.join(det))
            tot = sum(fontes.values()) or 1
            print(f"  {cl:9s} ({n:2d}) valor vem de: " + ', '.join(f"{k} {v / tot:.0%}" for k, v in fontes.most_common())
                  + ' | linhas mais usadas: ' + ', '.join(f'{k}×{v}' for k, v in linhas.most_common(5)))


if __name__ == '__main__':
    main()
