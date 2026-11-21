"""Reação de outra criatura (21/11, Deflect Attack do Steel Defender): "propria" não gasta a reação da build."""
from dh import defesa


def _cr(reacoes, livre=1.0):
    return defesa._resolve_sim('boss', 60, 17, [0, 0, 0, 0], False, 0, reacoes, livre)


def test_propria_nao_compete_com_shield():
    sh = {"tipo": "shield", "usos_luta": 1}
    comum = _cr([{"tipo": "desvantagem", "usos_luta": 4}, sh])
    propria = _cr([{"tipo": "desvantagem", "usos_luta": 4, "propria": True}, sh])
    assert propria > comum


def test_propria_vale_mesmo_sem_reacao_livre():
    d = {"tipo": "desvantagem", "usos_luta": 4, "propria": True}
    assert _cr([d], livre=0.0) > _cr([], livre=0.0)
