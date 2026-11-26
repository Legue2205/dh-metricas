import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'calibracao'))
from meta_consenso import avaliar  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), '..')


def test_avaliar_topo_e_fundo():
    vs = {f's{i:02d}': 100 - i for i in range(30)}
    forte = [f's{i:02d}' for i in range(8)]
    fraco = [f's{i:02d}' for i in range(22, 30)]
    r = avaliar(vs, forte, fraco)
    assert r['topo_forte'] == 8 and r['topo_fraco'] == 0 and r['fundo_fraco'] == 8 and r['passa']
    r = avaliar(dict(vs, s29=1000), forte, fraco)       # um fraco no topo derruba
    assert r['topo_fraco'] == 1 and not r['passa_topo']


def test_lista_consistente():
    m = json.load(open(os.path.join(RAIZ, 'calibracao', 'meta-consenso.json'), encoding='utf-8'))
    for e, x in m['eixos'].items():
        for nv in ('7', '11'):
            assert not set(x['forte'][nv]) & set(x['fraco'][nv]), (e, nv)
            assert not any(s.split('-')[0] in m['holdout'] for s in x['forte'][nv] + x['fraco'][nv]), (e, nv)
