"""Mecânicas do Rogue (mutirão 21/11): dado_no_erro (Homing Strikes)."""
from dh.dano import dpr, _dado_no_erro


def _spec(**k):
    s = {"ataques": [{"n": 1, "bonus": 9, "dano": "1d6+5"}], "por_turno": [{"dano": "5d6", "prob": 1.0}]}
    s.update(k); return s


def test_dado_no_erro_soma_e_respeita_orcamento():
    base = dpr(_spec(), 18)
    com = dpr(_spec(dado_no_erro={"dado": 8, "usos": 2.5}), 18)
    assert com > base
    # orçamento minúsculo limita o ganho: U/R conversões por round
    pouco = dpr(_spec(dado_no_erro={"dado": 8, "usos": 0.1}), 18)
    assert base < pouco < com


def test_dado_no_erro_conta_conversao_exata():
    # bonus 9 contra CA 18: erra com 2..8 (r+9<18); converte se r+9+j>=18
    s = _spec()
    g = _dado_no_erro({"dado": 8, "usos": 99}, s['ataques'], s['por_turno'], 18)
    conv = sum(sum(1 for j in range(1, 9) if r + 9 + j >= 18) / 8 for r in range(2, 9)) / 20
    assert abs(g - conv * (8.5 + 17.5)) < 1e-9


def test_dado_no_erro_so_sem_acerto_antes():
    s2 = {"ataques": [{"n": 1, "bonus": 9, "dano": "1d6+5"}, {"n": 1, "bonus": 9, "dano": "1d4+5"}],
          "por_turno": [{"dano": "5d6", "prob": 1.0}]}
    g1 = _dado_no_erro({"dado": 8, "usos": 99}, s2['ataques'][1:], s2['por_turno'], 18)
    g2 = _dado_no_erro({"dado": 8, "usos": 99}, s2['ataques'], s2['por_turno'], 18)
    assert g2 < g1
