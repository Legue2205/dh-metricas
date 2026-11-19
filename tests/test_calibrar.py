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


def test_premissas_resolver_e_registro():
    from dh import premissas
    premissas.inicio()
    v = premissas.resolver({'x': {'$p': 'controle.peso_no_controle.sentinela'}, 'y': [1, {'$p': 'suporte.lutas_dia'}]})
    assert v == {'x': premissas.valor('controle.peso_no_controle.sentinela'), 'y': [1, 4]}
    assert set(premissas.usadas()) == {'controle.peso_no_controle.sentinela', 'suporte.lutas_dia'}


def test_peso_de_corpo_no_controle():
    from dh.controle import efeitos
    fn = efeitos.compilar([{'tipo': 'sentinela', 'nome': 'S'}, {'tipo': 'ameaca', 'nome': 'A'}], {'ca': 18, 'pv': 60}, 7)
    from dh.premissas import valor
    assert fn.peso_ctrl == {'S': valor('controle.peso_no_controle.sentinela'), 'A': 0.0} and fn.corpo == {'S', 'A'}


def test_migracao_reproduz_constantes_antigas():
    """As premissas migradas têm os mesmos valores das constantes que existiam no código (refatoração neutra)."""
    from dh import base, planos, suporte, tatico
    assert base.PERFIL == base.PERFIL_ANTIGO and base.TOPO == base.TOPO_ANTIGO
    assert {k: v for k, v in suporte.H_ANTIGO.items() if k not in ('VANT', 'LUTAS_SR', 'LUTAS_DIA')} == \
           {k: v for k, v in suporte.H.items() if k != 'VANT' and k in suporte.H_ANTIGO}   # premissas novas (19/11) à parte
    assert planos.TAGS == planos.TAGS_ANTIGO and tatico.COMPOSICOES == tatico.COMPOSICOES_ANTIGO
