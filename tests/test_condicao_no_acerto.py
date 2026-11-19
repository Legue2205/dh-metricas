from dh.controle import campo as C, efeitos


def _E(lr=0):
    return [dict(ca=15, fr=1, fo=5, sb=0, lr=lr, cr=5, w=1.0, dn=10, hp=100, melee=True, atk=6)]


def _v(**f):
    base = dict(tipo='condicao_no_acerto', efeito='cond_impedido', cd=14, bonus=[7, 7], usos=1)
    base.update(f)
    return float(efeitos._condicao_no_acerto(base, _E(f.pop('lr', 0)), 'padrao', None).sum())


def test_mais_usos_e_cd_valem_mais():
    C.configurar(4000)
    assert _v(usos=2) > _v(usos=1) > _v(usos=0.5) > 0
    assert _v(cd=17) > _v(cd=12)


def test_um_turno_repete_e_sem_ataque():
    C.configurar(4000)
    um = _v(efeito='cond_derrubado', usos=4)
    assert 0 < um < _v(efeito='cond_derrubado', usos=4, no_acerto=False) <= 0.25


def test_marca_sem_resistencia_vale_menos():
    C.configurar(4000)
    E = _E()
    com = float(efeitos._ancestral(dict(bonus=8), E, 'Campo aberto', dict(nivel=5, ca=18, pv=50)).sum())
    sem = float(efeitos._ancestral(dict(bonus=8, resistencia=False), E, 'Campo aberto', dict(nivel=5, ca=18, pv=50)).sum())
    assert 0 < sem < com
