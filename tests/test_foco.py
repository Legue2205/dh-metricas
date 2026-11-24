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
