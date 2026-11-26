"""26/11 (G2): redirecionar o dano para o aliado ligado mais resistente (Protective Bond) × para si (Divine Allegiance)."""
from dh.controle import atencao


def _party(para=None):
    cler = dict(papel='conjurador', ca=16, pv=50, front=False, dpr=10, redireciona=0.3)
    if para: cler['redireciona_para'] = para
    tank = dict(papel='frontliner', ca=20, pv=90, front=True, dpr=15)
    fragil = dict(papel='conjurador', ca=13, pv=40, front=False, dpr=12)
    return [cler, tank, fragil]


def test_para_si_e_para_o_mais_resistente():
    e = dict(melee=False, mal=1, cr=3, dn=20, atk=6, ca=14)
    p0 = atencao.distribui(e, [dict(x, redireciona=0) for x in _party()], 0)
    si = atencao.distribui(e, _party(), 0)
    res = atencao.distribui(e, _party('mais_resistente'), 0)
    assert abs(si.sum() - 1) < 1e-9 and abs(res.sum() - 1) < 1e-9
    assert si[0] > p0[0] and si[1] < p0[1]                  # para si: o clérigo puxa
    assert res[1] > p0[1] and res[0] < p0[0] and res[2] < p0[2]   # ligação: o tanque leva, o clérigo também é poupado
