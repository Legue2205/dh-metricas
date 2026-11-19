"""Corpo como nível equivalente de neutralidade (19/11)."""
from dh.controle import total


def _com(monkeypatch, f):
    monkeypatch.setattr(total, 't_atencao', lambda fn, ficha, L: f(L))


def test_neutro_no_proprio_nivel(monkeypatch):
    _com(monkeypatch, lambda L: 99)
    assert total.nivel_corpo(None, None, 7, 0.05)[0] == 7.0


def test_positivo_cruza_acima(monkeypatch):
    _com(monkeypatch, lambda L: 0.3 - 0.1 * (L - 7))      # zero em 10
    assert abs(total.nivel_corpo(None, None, 7, 0.3)[0] - 10.0) < 1e-9


def test_negativo_cruza_abaixo(monkeypatch):
    _com(monkeypatch, lambda L: -0.2 + 0.1 * (7 - L))     # zero em 5
    assert abs(total.nivel_corpo(None, None, 7, -0.2)[0] - 5.0) < 1e-9


def test_positivo_no_20_extrapola(monkeypatch):
    _com(monkeypatch, lambda L: 1.0 - 0.02 * (L - 15))    # zero em 65 → 20+
    nv = total.nivel_corpo(None, None, 15, 1.0)[0]
    assert nv > 20


def test_negativo_no_1_nunca_zero_fixo(monkeypatch):
    _com(monkeypatch, lambda L: -1.0 + 0.1 * (3 - L))     # zero em −7 → piso 0,1
    nv = total.nivel_corpo(None, None, 3, -1.0)[0]
    assert 0 < nv < 1
