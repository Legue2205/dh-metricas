"""Progressão por nível (dh/progressao.py) e plano automático (dh/plano_auto.py)."""
import json
from pathlib import Path

from dh import plano_auto, progressao
from dh.build import validar

RAIZ = Path(__file__).resolve().parents[1]


def test_mesclar_linhas_por_id_e_null_apaga():
    a = {'corpo': {'ca': 15, 'pv': 20, 'x': 1}, 'linhas': [{'id': 'p', 'dano': {'n': 1}}, {'id': 'q'}], 'lista': [1, 2]}
    b = {'corpo': {'pv': 30, 'x': None}, 'linhas': [{'id': 'p', 'dano': {'n': 2}}, {'id': 'q', '_remover': True}, {'id': 'r'}], 'lista': [3]}
    m = progressao.mesclar(a, b)
    assert m['corpo'] == {'ca': 15, 'pv': 30} and [l['id'] for l in m['linhas']] == ['p', 'r']
    assert m['linhas'][0]['dano'] == {'n': 2} and m['lista'] == [3] and a['corpo']['pv'] == 20


def test_fatias_cumulativas_validas_e_com_plano_auto():
    prog = json.loads((RAIZ / 'progressoes' / 'exemplo-guerreiro.json').read_text(encoding='utf-8'))
    f = progressao.fatias(prog)
    assert sorted(f) == [3, 5, 7]
    assert f[7]['corpo'] == {'ca': 19, 'pv': 60}                        # patch do 7 sobre o do 5
    assert f[7]['linhas'][0]['dano']['ataques'][0]['n'] == 2             # herdado do patch do 5
    assert f[3]['id'] == 'exemplo-guerreiro-3' and f[3]['nivel'] == 3
    for b in f.values():
        assert validar(json.loads(json.dumps(b))) == []
        p = b['planos']['padrao']
        assert p['auto'] and p['combates'].count('surge') == 2          # 1 Action Surge por descanso → nas prioritárias
        assert [c for c, (cat, _) in zip(p['combates'], [('np', 1), ('p', 2), ('np', 1), ('p', 2)]) if cat == 'p'] == ['surge', 'surge']


def test_plano_auto_nao_sobrescreve_plano_escrito():
    b = {'linhas': [{'id': 'a', 'dano': {}}], 'corpo': {'ca': 10, 'pv': 10}, 'planos': {'padrao': {'combates': ['a'] * 4}}}
    assert plano_auto.aplicar(b) == [] and 'auto' not in b['planos']['padrao']
