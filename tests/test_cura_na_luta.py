"""Cura na luta (19/11): Healing Word (distância, ação bônus) vale mais que Cure Wounds (toque, ação)."""
from dh import suporte


def _v(**kw):
    return suporte.valor(dict(dict(nome='x', lado='def', modelo='cura_na_luta', pv=7, usos_luta=1), **kw), 7)


def test_healing_word_maior_que_cure_wounds():
    hw = _v(alcance='distancia', acao='bonus'); cw = _v(alcance='toque', acao='acao')
    assert hw > cw > 0


def test_usos_limitados_pelos_caidos():
    assert _v(usos_luta=5) == _v(usos_luta=suporte.H['P_CAIDO'])
