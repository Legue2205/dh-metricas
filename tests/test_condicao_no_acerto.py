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


def test_forcar_falha_aumenta_controle():
    C.configurar(4000)
    E = _E() + _E()
    f = dict(tipo='alvo_unico', nome='Hold', cd=14, slots=[2], magias=['hold_person'], modo='melhor')
    base = float(efeitos._avalia_fonte(f, E, 'Campo aberto', None)['Hold'].sum())
    com = float(efeitos._avalia_fonte(dict(f, forcar_falha=0.5), E, 'Campo aberto', None)['Hold'].sum())
    assert com > base


def test_um_turno_lr_exata_nao_zera():
    """Sprint D: 2 tentativas de um efeito de um turno contra 1 Legendary Resistance. E[X] = 0,5 ≤ lr, mas a 2ª falha
    passa: E[max(0, X − 1)] = P(X = 2) = 0,0625 (antes o valor esperado menos lr dava 0)."""
    from dh.controle.efeitos import _lr_gastas
    assert abs(_lr_gastas(1.0, 0.25, 2, 1.0, 1) - (1 - 0.75 ** 2)) < 1e-12
    assert abs(_lr_gastas(1.0, 0.25, 1, 1.0, 1) - 0.25) < 1e-12      # 1 uso: a LR come tudo
    C.configurar(4000)
    f = dict(efeito='cond_atordoado_um_turno', cd=14, bonus=[7, 7], usos=2)
    com, sem, um = _v(lr=1, **f), _v(**f), _v(lr=1, **dict(f, usos=1))
    assert 0 < com < sem and um < 1e-3   # 1 uso: a LR come quase tudo (resto = chance de errar os 4 turnos)
