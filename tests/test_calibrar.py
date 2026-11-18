"""Gabarito de calibração (dh/calibrar.py)."""
from dh import calibrar


def _vals(**k): return {b: ({'dano': v}, '') for b, v in k.items()}


def test_ordem_concorda_inverte_e_empate_tecnico():
    v = _vals(a=10.0, b=8.0, c=8.3, d=2.0)
    r = calibrar.avaliar_eixo('dano', {'ordem': ['a', 'b', 'c', ['d']]}, v, tol=0.5)
    # pares: a>b ok, a>c ok, a>d ok, b>c 8,0 < 8,3 (empate técnico), b>d ok, c>d ok
    assert (r['concordantes'], r['invertidos'], r['empates_tecnicos']) == (5, 0, 1)
    r = calibrar.avaliar_eixo('dano', {'ordem': ['d', 'a']}, v)
    assert r['invertidos'] == 1 and r['tau'] == -1.0 and r['inversoes'][0]['esperado_maior'] == 'd'


def test_empate_declarado_nao_conta_e_faixa():
    v = _vals(a=10.0, b=3.0)
    r = calibrar.avaliar_eixo('dano', {'ordem': [['a', 'b']], 'faixa': {'a': ['B', 'A'], 'b': ['B', 'A'], 'z': ['C', 'B']}}, v)
    assert r['tau'] is None and [x['build'] for x in r['faixas']] == ['b'] and r['ausentes'] == ['z']


def test_eixo_ausente_na_build_vale_zero():
    v = {'a': ({}, ''), 'b': ({'area': 4.0}, '')}
    assert calibrar.avaliar_eixo('area', {'ordem': ['b', 'a']}, v)['concordantes'] == 1
