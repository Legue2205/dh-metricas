"""Efeito de um turno (Command) como alvo único: roda e vale menos que Hold Person com o mesmo espaço."""
from dh.controle import efeitos, campo as C


def _tot(fonte, L=5):
    from dh.controle.total import encontro
    E = encontro('Chefe sozinho', L)
    return C.tot(E, efeitos._alvo_unico(fonte, E, 'Campo aberto', None))


def test_command_roda_e_vale_menos_que_hold_person():
    cmd = _tot({'cd': 14, 'slots': [1], 'magias': ['command']})
    hp = _tot({'cd': 14, 'slots': [2], 'magias': ['hold_person']})
    assert 0 < cmd < hp


def test_mistura_pega_o_melhor():
    mix = _tot({'cd': 14, 'slots': [2], 'magias': ['command', 'hold_person']})
    hp = _tot({'cd': 14, 'slots': [2], 'magias': ['hold_person']})
    assert abs(mix - hp) < 1e-9 or mix > hp
