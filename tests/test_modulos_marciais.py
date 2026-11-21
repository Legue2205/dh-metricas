"""Módulos de 21/11: PV temporários próprios, reação de bloqueio (CA contra um ataque) e Focused Aim."""
from dh import dano, defesa
from dh.base import pv_com_pvt

CORPO = {"ca": 16, "pv": 60}


def test_pvt_luta_soma_ao_pv():
    a = defesa.avaliar({}, CORPO); b = defesa.avaliar({"pvt_luta": 20}, CORPO)
    assert b['pv_efetivo'] == 80 and b['blindagem'] > a['blindagem'] and b['durabilidade'] > a['durabilidade']


def test_pvt_round_ajuda_mais_na_horda_que_um_pvt_luta_igual():
    a = defesa.avaliar({}, CORPO); r = defesa.avaliar({"pvt_round": 4}, CORPO)
    assert r['blindagem'] > a['blindagem'] and r['durabilidade'] > a['durabilidade']


def test_pvt_round_tambem_na_simulacao_com_reacoes():
    sp = {"reacoes": [{"tipo": "uncanny_dodge"}]}
    assert defesa.avaliar(dict(sp, pvt_round=4), CORPO)['blindagem'] > defesa.avaliar(sp, CORPO)['blindagem']


def test_bloqueio_melhora_e_fica_abaixo_do_shield():
    a = defesa.avaliar({}, CORPO)
    b = defesa.avaliar({"reacoes": [{"tipo": "bloqueio", "dado": 8}]}, CORPO)
    s = defesa.avaliar({"reacoes": [{"tipo": "shield", "usos_luta": 99}]}, CORPO)
    assert a['durabilidade'] < b['durabilidade'] <= s['durabilidade']


def test_pv_do_corpo_conta_pvt():
    assert pv_com_pvt({"pv": 50, "pvt_luta": 10, "pvt_round": 2}) == 66


def test_focused_aim_cresce_com_o_ki_e_satura():
    sp = {"ataques": [{"n": 3, "bonus": 7, "dano": "1d8+4"}]}
    v = [dano.dpr(dict(sp, focused_aim={"ki": k}), 18) for k in (0, 1, 2, 100)]
    assert v[0] < v[1] < v[2] < v[3]
    assert v[3] - v[0] < 3 * 8.5 * 0.3 + 1   # no máximo os erros por até 6 viram acerto
