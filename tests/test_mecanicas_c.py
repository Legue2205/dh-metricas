"""Pacote C (27/11): ataque em área (Volley), buff com cobertura (Bladesong), reação de proteção de aliado (Projected
Ward, Protective Field), Portent dividido, Order's Wrath, Hand of Healing."""
import copy

from dh import horda, suporte
from dh.build import resolver, validar
from dh.controle import efeitos


def _l(**k):
    base = {"dano": {"ataques": [{"n": 2, "bonus": 9, "dano": "1d8+4"}]}}
    base.update(k); return base


VOLLEY = {"nome": "Volley", "tipo": "ataque_area", "bonus": 9, "dano": "1d8+4", "seletiva": True}


def test_ataque_area_rende_com_alvos():
    so = horda.avaliar(_l())['rounds'][11]
    dois = horda.avaliar(_l(area=[dict(VOLLEY, alvos=2)]))['rounds'][11]
    quatro = horda.avaliar(_l(area=[dict(VOLLEY, alvos=4)]))['rounds'][11]
    assert abs(dois - so) < 0.15            # 2 alvos ≈ os 2 ataques do Extra Attack (tabela do DMG: raio 10 = 2)
    assert quatro < so - 0.2                 # com mais alvos a ação de área vence e a luta acaba antes
    um = horda.avaliar(_l(dano={"ataques": [{"n": 1, "bonus": 9, "dano": "1d8+4"}]}, area=[dict(VOLLEY, alvos=2)]))['rounds'][11]
    assert um < horda.avaliar(_l(dano={"ataques": [{"n": 1, "bonus": 9, "dano": "1d8+4"}]}))['rounds'][11]


def _b(**k):
    b = {"id": "t", "nome": "t", "grupo": "Teste", "nivel": 7, "corpo": {"ca": 15, "pv": 50},
         "recursos": {"espacos": {"1": 4}}, "linhas": [
             {"id": "principal", "principal": True, "dano": {"ataques": [{"n": 1, "bonus": 7, "dano": "1d10"}]}, "defesa": {}},
             {"id": "shield", "dano": {"ataques": []}, "defesa": {}, "reacao": [{"uso": "Shield", "fracao": 0.9, "eixos": ["defesa"]}],
              "corpo": {"ca": 16}}]}
    b.update(k); return b


def test_cobertura_soma_ca_proporcional_aos_usos():
    b = resolver(_b(patches_linhas=[{"origem": "Bladesong", "cobertura": {"usos": 3, "volta": "longo"}, "corpo": {"ca": 4}}]))
    p, s = b['linhas']
    assert p['corpo']['ca'] == 15 + 3                       # 3 usos ÷ 4 lutas × 4
    assert s['corpo']['ca'] == 16 + 3                       # soma ao corpo da própria linha
    b2 = resolver(copy.deepcopy(b))                         # idempotente
    assert b2['linhas'][0]['corpo']['ca'] == 18


def test_reacao_do_patch_respeita_a_reacao_livre():
    ward = {"origem": "Ward", "fator": 0.5, "corpo": {"pv": -20},
            "reacao": {"uso": "Ward", "fracao": 0.25, "eixos": ["suporte"]},
            "anexar": {"suporte.fontes": [{"nome": "Ward", "lado": "def", "modelo": "pv_temporario", "pv": 20, "usos_luta": 1, "fator": 0.5}]}}
    b = _b(patches_linhas=[ward]); assert validar(copy.deepcopy(b)) == []
    p, s = resolver(b)['linhas']
    assert p['corpo']['pv'] == 40 and p['suporte']['fontes'][0]['fator'] == 0.5
    assert abs(s['reacao'][-1]['fracao'] - 0.1) < 1e-9      # só 0,1 livre: 40% do patch
    assert abs(s['corpo']['pv'] - (50 - 20 * 0.5 * 0.4)) < 1e-9 and abs(s['suporte']['fontes'][0]['fator'] - 0.2) < 1e-9


def test_fator_e_complemento_no_suporte():
    f = {"lado": "def", "modelo": "pv_temporario", "pv": 20, "usos_luta": 1}
    v = suporte.valor(f, 7)
    assert abs(suporte.valor(dict(f, fator=0.25), 7) - v / 4) < 1e-9
    assert abs(suporte.valor(dict(f, fator=0.25, complemento=True), 7) - 0.75 * v) < 1e-9


def test_portent_vira_e_sem_acao():
    f = {"lado": "def", "modelo": "dado_multiuso", "vira": 0.5, "mix": {"acerto": 0.5, "ca": 0.5}, "usos_luta": 0.5}
    v = suporte.valor(dict(f, acao="nenhuma"), 11)
    assert v > 0 and v > suporte.valor(dict(f, acao="bonus"), 11)         # sem custo de ação bônus
    assert suporte.valor(dict(f, vira=1.0, acao="nenhuma"), 11) > v


def test_order_s_wrath_um_acerto_por_round():
    f = {"lado": "of", "modelo": "dano_por_acerto", "alvos": 1, "dano_extra": 9}
    v1 = suporte.valor(dict(f, por_round=True), 11); vt = suporte.valor(f, 11)
    assert 0 < v1 < vt                                                    # 1×/round, não em todo ataque do aliado
    assert suporte.valor(dict(f, por_round=True, p_gatilho=1.0), 11) > v1


def test_cura_de_toque_paga_o_acesso():
    f = {"lado": "def", "modelo": "cura", "pv": 10, "usos_luta": 3}
    assert abs(suporte.valor(dict(f, alcance="toque"), 7) - suporte.valor(f, 7) * suporte.H['ACESSO_TOQUE']) < 1e-9


def test_forcar_falha_fator_fica_entre_sem_e_com():
    from dh.controle import campo as C
    C.configurar(4000)
    E = [dict(ca=15, fr=1, fo=5, sb=0, lr=0, cr=5, w=1.0, dn=10, hp=100, melee=True, atk=6, papel='Bruto',
              **{k: 1 for k in ('fo_s', 'de', 'co', 'in', 'sa', 'ca_s')})]
    f = {"tipo": "alvo_unico_direto", "nome": "Hold", "magia": "hold_person", "cd": 13}
    t = dict(nivel=7, ca=15, pv=50, res=1, adv=0, red=0)
    v = lambda **k: float(efeitos._avalia_fonte(dict(f, **k), E, 'padrao', t)['Hold'].sum())
    sem, cheio, meio = v(), v(forcar_falha=1.0), v(forcar_falha=1.0, forcar_falha_fator=0.5)
    assert sem < meio < cheio and abs(meio - (sem + cheio) / 2) < 0.02 * cheio + 1e-6
