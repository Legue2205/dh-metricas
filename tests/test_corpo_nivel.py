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


# ---- Motor real: consistência com a tag, propriedade nota < nível ⇔ T < 0 e tendência de T em L' ----
import numpy as np
import pytest
from pathlib import Path

from dh import eixos
from dh.build import carregar
from dh.controle import atencao, campo, efeitos

B = Path(__file__).resolve().parents[1] / 'builds'


def _linha(arq):
    b = carregar(B / arq); linha = b['linhas'][0]
    if linha.get('tatico'): linha, _ = eixos.expande_tatico(b, linha)
    campo.configurar(2000, 11)
    corpo = eixos.corpo_da(b, linha); c = linha['controle']
    fn = efeitos.compilar(c.get('fontes', []), corpo, b['nivel'])
    return fn, atencao.ficha(dict(c['atencao']), corpo), b['nivel']


@pytest.mark.parametrize('arq', ['rpgbot-fighter-cavalier-7.json', 'rpgbot-fighter-champion-7.json',
                                 'rpgbot-fighter-eldritch-knight-11.json', 'rpgbot-wizard-evocation-7.json'])
def test_corpo_motor_real(arq):
    fn, ficha, L0 = _linha(arq)
    g, _ = total.avaliar_nivel(fn, ficha, L0, total.Regua())
    t0 = g['vidas_atencao']
    assert abs(total.t_atencao(fn, ficha, L0) - t0) < 1e-9          # o T da busca é o mesmo T da tag
    nv = total.nivel_corpo(fn, ficha, L0, t0)[0]
    assert (nv < L0) == (t0 < -total.LIMIAR_T)                       # nota < nível ⇔ tag T negativa
    assert (nv > L0) == (t0 > total.LIMIAR_T)
    ts = np.array([total.t_atencao(fn, ficha, L) for L in range(1, 21)])
    assert ts[0] > ts[-1] and np.polyfit(np.arange(1, 21), ts, 1)[0] < 0   # T cai com o nível da party/encontro
    assert np.diff(ts).max() < 0.12                                  # só degraus pequenos (tabela de CR)
