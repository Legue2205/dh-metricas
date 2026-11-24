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


def test_concentracao_fator():
    """Etapa C (24/11): quem apanha mais e tem CON pior segura menos a concentração; forma usa o CON da besta."""
    from dh import concentracao
    front = concentracao.fator({'posicao': 'striker', 'corpo': {'saves': {'sv': {'con': 3}}}}, {'id': 'bless'})
    tras = concentracao.fator({'posicao': 'retaguarda', 'corpo': {'saves': {'sv': {'con': 3}}}}, {'id': 'bless'})
    wc = concentracao.fator({'posicao': 'striker', 'build': 'War Caster', 'corpo': {'saves': {'sv': {'con': 3}}}}, {'id': 'x'})
    forma = concentracao.fator({'posicao': 'retaguarda', 'corpo': {'saves': {'sv': {'con': 9}}}},
                               {'id': 'polimorfo', 'hipotese': 'Polymorph em si mesmo'})
    assert 0 < front['f'] < tras['f'] < 1 and wc['f'] > front['f']
    assert forma['forma'] and forma['grupo'] == 'front' and forma['f'] < tras['f']


def test_concentracao_so_o_ganho_cai():
    from dh import concentracao
    assert concentracao._mistura(5.0, 9.0, 0.5) == 7.0      # ganho sobre a base cai pela metade
    assert concentracao._mistura(5.0, 4.0, 0.5) == 4.0      # abaixo da base: não muda
