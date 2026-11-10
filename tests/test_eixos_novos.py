"""Saves, área, suporte, reações de defesa e orçamento de recursos."""
import copy
import json
from pathlib import Path

import pytest

from dh import area, orcamento, saves, suporte
from dh.build import validar
from dh.controle.campo import MAGIAS
from dh.defesa import avaliar as defesa

B = Path(__file__).resolve().parents[1] / 'builds'
SV = lambda *v: dict(zip(('for', 'des', 'con', 'int', 'sab', 'car'), v))


def test_saves_paridade_abdul():   # planilha de defesa, abas Resiliência e Vontade: 6,07 e 8,03
    r = saves.avaliar({}, dict(pv=63, ca=21, saves=dict(sv=SV(6, 1, 5, 1, 5, 7), ataques=2)))
    assert (r['resiliencia']['nivel_eq'], r['vontade']['nivel_eq']) == (6.07, 8.03)


def test_saves_sem_reacao_perde_counterspell():
    corpo = dict(pv=53, ca=14, saves=dict(sv=SV(-1, 1, 2, 6, 4, 2), contra=1, contra_mod=3, conjurador=True))
    assert saves.avaliar({}, corpo, 1.0)['vontade']['nivel_eq'] > saves.avaliar({}, corpo, 0.0)['vontade']['nivel_eq']


@pytest.mark.parametrize('a,esperado', [
    ({"usos": [{"alvos": 4, "dano": "8d6", "cd": 14}]}, 8.1),                                  # Amadeus, Fireball
    ({"usos": [{"alvos": 2, "dano": "3d8", "cd": 16}]}, 4.02),                                 # Marcus, Shatter
    ({"tipo": "cleave_ataque", "bonus": 7, "dano": "1d8+14", "p": [0.4, 0.75, 1.0]}, 4.5),     # John, Horde Breaker
])
def test_area(a, esperado):
    assert abs(area.avaliar([a], 'rapido')['nivel_eq'] - esperado) <= 0.3


def test_suporte_regua_e_linhas():
    assert [round(x, 2) for x in suporte.REGUAS[2][:5]] == [5.28, 6.29, 7.86, 9.6, 14.48]
    k = suporte.avaliar({'fontes': [{'lado': 'of', 'modelo': 'vantagem', 'alvos': 3, 'fracao': 0.34}]}, 7)
    assert (k['ofensivo'], k['nivel_eq'], k['rank']) == (9.28, 3.8, 'C-')
    a = suporte.avaliar({'fontes': [{'lado': 'def', 'modelo': 'aura_saves', 'bonus': 2},
                                    {'lado': 'def', 'modelo': 'cura', 'usos_dia': 1, 'pv': 35}]}, 7)
    assert (a['defensivo'], a['nivel_eq'], a['rank']) == (2.88, 0.5, 'E')


def test_shield_e_uncanny_dodge():
    c = dict(pv=53, ca=14)
    b = [defesa({'reacoes': [{'tipo': 'shield', 'usos_luta': u}]} if u else {}, c)['blindagem'] for u in (0, 1, 2, 4)]
    assert b == sorted(b) and b[0] < b[1] < b[3]            # mais Shields, mais blindagem; recurso finito
    t = dict(pv=54.5, ca=17); ud = {'reacoes': [{'tipo': 'uncanny_dodge'}]}
    livre, meio, nada = (defesa(ud, t, x)['blindagem'] for x in (1.0, 0.5, 0.0))
    assert livre > meio > nada == defesa({}, t)['blindagem']  # reação gasta em outro eixo não defende


def test_reacao_nao_duplica():
    b = json.loads((B / 'caleb-14.json').read_text(encoding='utf-8'))
    assert validar(b) == []
    p = next(l for l in b['linhas'] if l['id'] == 'principal')
    assert orcamento.reacao_livre(p) == 0                    # 2º Sneak usa a reação: sem Uncanny Dodge
    x = copy.deepcopy(b); t = next(l for l in x['linhas'] if l['id'] == 'tanque')
    t['reacao'].append({"uso": "Riposte", "fracao": 0.8, "eixos": ["dano"]})
    assert any('reação está contada mais de uma vez' in e for e in validar(x))
    y = copy.deepcopy(b); next(l for l in y['linhas'] if l['id'] == 'tanque').pop('reacao')
    assert any('usa a reação' in e for e in validar(y))


def test_tags_de_orcamento():
    b = json.loads((B / 'amadeus-7.json').read_text(encoding='utf-8'))
    L = {l['id']: l for l in b['linhas']}
    assert orcamento.tag(L['principal'], b, MAGIAS)[0] == 'hypercharged_1.5'   # 5 espaços de 3º+ contra 4 no dia
    assert orcamento.tag(L['shield-total'], b, MAGIAS)[0] == 'combate_unico'    # 4 Shields de 1º numa luta
    assert orcamento.fracoes({}) == {'comum': 1 / 6, 'prioritaria': 1 / 3, 'combate_unico': 1.0}
    erros, avisos = orcamento.checar(b, MAGIAS)
    assert erros == [] and any('hypercharged' in a for a in avisos)
