"""Reações defensivas genéricas (19/11): desvantagem num ataque e anula crítico."""
from dh import defesa


def _cr(reacoes):
    return defesa._resolve_sim('boss', 60, 17, [0, 0, 0, 0], False, 0, reacoes, 1.0)


def test_desvantagem_melhora_defesa():
    assert _cr([{"tipo": "desvantagem", "usos_luta": 2}]) > _cr([])


def test_anula_critico_melhora_pouco():
    sem = _cr([]); com = _cr([{"tipo": "anula_critico", "usos_luta": 2}])
    assert sem < com < _cr([{"tipo": "desvantagem", "usos_luta": 2}]) + 5
