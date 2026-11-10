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


def _caster():
    """Build sintética: bardo que luta de espada nos combates comuns e gasta feitiços nos prioritários."""
    at = {"papel": "conjurador", "front": True, "conc": True, "dpr": 16}
    return {"id": "t", "nome": "T", "grupo": "Teste", "nivel": 7, "corpo": {"ca": 17, "pv": 45},
            "recursos": {"espacos": {"1": 4, "2": 3, "3": 3, "4": 1}, "outros": {"inspiracao": {"qtd": 3, "volta": "curto"}}},
            "linhas": [
                {"id": "marcial", "principal": True, "hipotese": "espada; abre com 1 feitiço de 1º",
                 "dano": {"ataques": [{"n": 2, "bonus": 7, "dano": "1d8+4"}]},
                 "controle": {"atencao": at, "fontes": [{"tipo": "ameaca"}], "usa": {"espacos": {"1": 1}}}},
                {"id": "caster", "herda": "marcial", "hipotese": "um feitiço por round", "usa": {"inspiracao": 2},
                 "dano": {"ataques": [{"n": 1, "bonus": 7, "dano": "1d8+4"}]},
                 "controle": {"atencao": dict(at, front=False), "fontes": [
                     {"tipo": "alvo_unico", "cd": 15, "slots": [3, 2], "magias": ["hold_person"]}]}}],
            "planos": {"padrao": {"combates": ["marcial", "caster", "marcial", "caster"]}}}


def test_plano_livro_caixa_e_media():
    from dh import planos
    from dh.base import letra
    b = _caster(); assert validar(b) == []
    erros, combates, sobra = planos.livro_caixa(b, 'padrao', MAGIAS)
    assert erros == [] and [c['categoria'] for c in combates] == ['np', 'p', 'np', 'p']
    assert sobra['espacos'] == {'1': 2, '2': 1, '3': 1, '4': 1} and sobra['inspiracao'] == 1   # sobra para utilidade
    res = {'marcial': {'dano': {'nivel_eq': 6.0}, 'controle': {'nivel_eq': 1.0}},
           'caster': {'dano': {'nivel_eq': 3.0}, 'controle': {'nivel_eq': 7.0}, 'area': {'nivel_eq': 4.0}}}
    e = planos.agregar(b, res, MAGIAS, letra)['padrao']['eixos']
    assert e['dano'] == dict(nivel_eq=4.0, rank='C', por_categoria={'np': 6.0, 'p': 3.0})     # prioritário pesa 2
    assert e['controle']['nivel_eq'] == 5.0 and e['controle']['por_categoria'] == {'np': 1.0, 'p': 7.0}
    assert e['area']['por_categoria'] == {'np': 0.0, 'p': 4.0}                                 # não fez área no comum


def test_plano_estouro_e_hypercharged():
    b = _caster(); assert validar(b) == []
    b['linhas'][1]['controle']['fontes'][0]['slots'] = [3, 3, 3]             # 6 de 3º+ no dia contra 4: não cabe
    assert any('faltam' in e and 'nível 3+' in e for e in validar(b))
    b['planos']['padrao']['hypercharged'] = 2
    assert validar(b) == []
    b['planos']['dia_longo'] = {'combates': ['marcial'] * 7}
    assert any('precisa de 8 combates' in e for e in validar(b))


def test_descanso_curto_devolve():
    from dh import planos
    b = _caster(); b['recursos'] = {"espacos": {"3": 2}, "espacos_volta": "curto", "outros": {"inspiracao": {"qtd": 2, "volta": "curto"}}}
    b['linhas'][0]['controle']['usa'] = {}
    b['planos'] = {'padrao': {'combates': ['marcial', 'caster', 'marcial', 'caster']}}   # 2 de 3º antes e 2 depois do descanso
    assert planos.livro_caixa(b, 'padrao', MAGIAS)[0] == []


def test_invocacoes():
    from dh.dano import avaliar
    spec = {"ataques": [{"n": 1, "bonus": 6, "dano": "2d8"}]}
    inv = [{"nome": "esqueletos", "quantidade": 7, "pv": 19, "ca": 16, "ataque": {"bonus": 4, "dano": "1d6+5"}}]
    assert avaliar(spec, 4, inv)['dpr']['CA 15'] > avaliar(spec)['dpr']['CA 15'] + 25
    from dh import motor
    _, r = motor.avaliar(B / 'amadeus-7.json', 'rapido', forcar=True, eixos=['controle'], linhas=['principal'])
    c = r['linhas']['principal']['controle']                                 # paridade mantida lendo de "invocacoes"
    assert abs(c['nivel_eq'] - 6.0) <= 0.4 and abs(c['nivel_atencao'] - 3.8) <= 0.4
    assert any('esqueletos' in k for k in c['negacao_por_fonte']['Horda'])


@pytest.mark.parametrize('arq,tol', [('john-7', 0.03), ('tinbin-7', 0.045), ('abdul-7', 0.08), ('marcus-7', 0.01), ('amadeus-7', 0.01)])
def test_dano_calculado_bate_com_o_medido(arq, tol):
    """O dano saiu de 'medido' para 'ataques'; os 9 DPRs antigos ficam em 'conferencia'. (John: só até CA 22;
    acima disso o motor desliga o Sharpshooter, que rende mais, e a planilha não desligava.)"""
    from dh import dano
    b = json.loads((B / f'{arq}.json').read_text(encoding='utf-8')); l = b['linhas'][0]
    v = list(dano.avaliar(l['dano'], 4, l.get('invocacoes', []))['dpr'].values()); c = l['dano']['conferencia']
    n = 7 if arq == 'john-7' else 9
    assert max(abs(x - y) / y for x, y in zip(v[:n], c[:n])) <= tol


def test_concentracao_e_acao_bonus():
    b = _caster(); b['linhas'][1]['dano']['concentracao'] = 'hex'            # Hex + Hold Person na mesma linha
    assert any('mais de uma concentração' in e for e in validar(b))
    b['linhas'][1]['dano']['concentracao'] = 'hold_person'                   # a mesma concentração em dois eixos: ok
    assert validar(b) == []
    b['linhas'][0]['acao_bonus'] = [{"uso": "a", "fracao": 0.7, "eixos": ["dano"]}, {"uso": "b", "fracao": 0.5, "eixos": ["controle"]}]
    assert any('ação bônus está contada mais de uma vez' in e for e in validar(b))
