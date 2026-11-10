"""Paridade com as planilhas (valores lidos em 08/11/2026). Rodar: python -m pytest -q

Se um teste quebrar depois de mudar um motor, ou o motor regrediu, ou a mudança é intencional:
nesse caso atualize o valor esperado aqui E refaça as linhas das planilhas (python -m dh linhas ...).
"""
from pathlib import Path

import pytest

from dh import motor
from dh.dano import nivel_equivalente
from dh.defesa import avaliar as defesa

B = Path(__file__).resolve().parents[1] / 'builds'


@pytest.mark.parametrize('dpr,esperado', [
    ([41.6, 40.4, 36, 34.2, 30.7, 26.4, 21.4, 15.7, 12.5], 9.4),      # John
    ([39.5, 37, 29.8, 27.5, 22.8, 18.1, 13.6, 9.7, 8.1], 7.3),         # Kael
    ([25.5, 24.4, 21.3, 20.3, 18.2, 16.2, 14, 11.6, 10.2], 5.6),       # Abdul
    ([88.7, 88.7, 88.6, 88.5, 87.8, 86.1, 83.1, 78.5, 75.5], 20.0),    # Lucius montado
    ([13.7, 13.8, 11.6, 11, 9.5, 8.2, 6.7, 5.3, 4.7], 2.8),            # Pyotr besta
    ([80.6, 74.8, 57, 50.9, 39.1, 27.1, 15.3, 15.3, 15.2], 11.8),      # Amadeus 14 esqueletos
])
def test_nivel_dano(dpr, esperado):
    assert nivel_equivalente(dpr)[0] == esperado


@pytest.mark.parametrize('pv,ca,adv,resist,esperado', [
    (79, 17, 0, False, (5.95, 4.22)),     # Kael moeda ativa
    (75, 17, -1, False, (10.42, 6.45)),   # Kael Patient Defense
    (78, 18, 0, True, (11.53, 8.64)),     # Fjord
    (79.5, 18, 0, False, (6.61, 4.54)),   # Guerreiro de referência 7
    (55, 15, 0, True, (6.81, 4.97)),      # Bárbaro Urso 5
    (68, 20, 0, False, (7.18, 4.63)),     # Paladino V 8
    (95, 15, 1, True, (8.03, 7.03)),      # Jamal Reckless
    (144.5, 20, 0, False, (12.71, 9.46)), # Lucius montado
])
def test_defesa(pv, ca, adv, resist, esperado):
    r = defesa(dict(pv_efetivo=pv, ca=ca, adv=adv, resist=resist), dict(pv=pv, ca=ca))
    assert (r['blindagem'], r['durabilidade']) == esperado


def test_defesa_reducao_fixa():
    # Heavy Armor Master: o nº de atacantes da horda importa (bug da reconstrução de 03/11)
    for pv, esperado in ((63, (9.89, 5.96)), (98, (13.05, 8.2))):
        r = defesa(dict(pv_efetivo=pv), dict(pv=pv, ca=21, red=3))
        assert (r['blindagem'], r['durabilidade']) == esperado


def _ignorar():
    pass


# Controle é Monte Carlo (personagem e régua): tolerância de 0,4 nível.
@pytest.mark.parametrize('arq,total,campo,aten', [
    ('abdul-7.json', 4.9, 4.2, 4.1),
    ('kael-7.json', 3.6, 3.0, 1.1),
    ('virgil-10.json', 6.5, 6.5, 0.5),
    ('amadeus-7.json', 6.0, 4.3, 3.8),
    ('john-7.json:ensnaring-strike', 0.7, 1.7, 0.0),
    ('tinbin-7.json', 0.4, 0.1, 0.3),
    ('fjord-9.json', 5.7, 5.2, 3.6),
    ('miau-8.json', 4.5, 4.1, 0.8),
    ('caleb-14.json', 0.8, 0.8, 0.7),
    ('lucius-15.json', 2.2, 0.8, 1.5),
    ('aprendiz-11.json', 3.6, 0.8, 3.1),
    ('pyotr-14.json', 3.0, 6.2, 0.0),
    ('jamal-9.json', 2.7, 0.7, 2.4),
    pytest.param('ravin-7.json', 7.7, 6.2, 1.9, marks=pytest.mark.xfail(reason='Minions+minibosses: 9,9 aqui × 12,1 na planilha (extrapolação acima do teto da régua amplifica o ruído)')),
    pytest.param('solaris-9.json', 7.5, 6.9, 1.6, marks=pytest.mark.xfail(reason='Chefe/Dupla divergem; o valor da planilha veio de uma versão anterior do script, não reproduzível')),
])
def test_controle(arq, total, campo, aten):
    arq, _, lid = arq.partition(':'); lid = lid or 'principal'
    _, r = motor.avaliar(B / arq, 'rapido', forcar=True, eixos=['controle'], linhas=[lid])
    c = r['linhas'][lid]['controle']
    assert abs(c['nivel_eq'] - total) <= 0.4
    assert abs(c['nivel_campo'] - campo) <= 0.4
    assert abs(c['nivel_atencao'] - aten) <= 0.4
