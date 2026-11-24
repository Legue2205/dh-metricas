"""Etapa A (24/11): planos de foco automáticos — o rendimento de um eixo só."""
from dh import plano_auto


def test_valores_so_um_eixo():
    linhas = {'bless': {'dano': {'nivel_eq': 4.0}, 'suporte': {'nivel_eq': 6.0}},
              'smite': {'dano': {'nivel_eq': 8.0}, 'suporte': {'nivel_eq': 0.5}}}
    v = plano_auto.valores_linhas(linhas, so='dano')
    assert v['smite'] > v['bless']
    v = plano_auto.valores_linhas(linhas, so='suporte')
    assert v['bless'] > v['smite']
    assert set(plano_auto.FOCOS) == {'dano', 'controle', 'area', 'suporte'}


def test_moeda_de_paladin():
    """Etapa B (24/11): em dano equivalente, voto+smite vence Bless no Paladin sem party que precise do Bless."""
    from dh import moeda
    bless = {'dano': {'dpr': {'CA 15': 16.7}}, 'suporte': {'total': 16.06}, 'controle': {'vidas_total': 0}, 'area': {}}
    smite = {'dano': {'dpr': {'CA 15': 32.2}}, 'suporte': {'total': 2.94}, 'controle': {'vidas_total': 0}, 'area': {}}
    assert moeda.de_linha(smite, 7)['total'] > moeda.de_linha(bless, 7)['total']
