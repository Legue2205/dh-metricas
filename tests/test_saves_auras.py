"""Sprint D (27/11): defesa mental — auras do Paladin no próprio save e listas do corpo somadas às da linha."""
import sys

from dh import saves

sys.path.insert(0, 'ferramentas/geradores')


def _corpo(**extra):
    return dict(ca=18, pv=81, saves=dict(sv={'for': 8, 'des': 3, 'con': 4, 'int': 2, 'sab': 8, 'car': 10},
                                         conjurador=True, ataques=2, **extra))


def test_imunidade_do_corpo_soma_com_a_da_linha():
    """Aura of Courage no corpo (medo) + imunidade da linha (encanto) = as duas; antes a linha substituía a lista."""
    so_linha = saves._avaliar({'imune': ['encanto']}, _corpo())
    soma = saves._avaliar({'imune': ['encanto']}, _corpo(imune=['medo']))
    as_duas = saves._avaliar({'imune': ['encanto', 'medo']}, _corpo())
    assert soma['vontade']['turnos_livres'] == as_duas['vontade']['turnos_livres']
    assert soma['vontade']['nivel_eq'] >= so_linha['vontade']['nivel_eq']


def test_imunidade_a_encanto_e_medo_sobe_a_vontade():
    base = saves._avaliar({}, _corpo())['vontade']['nivel_eq']
    assert saves._avaliar({}, _corpo(imune=['medo']))['vontade']['nivel_eq'] >= base
    assert saves._avaliar({}, _corpo(imune=['encanto']))['vontade']['nivel_eq'] > base + 2


def test_auras_do_paladin_por_nivel_e_juramento():
    import pal
    assert pal.auras_saves(6) == {}
    assert pal.auras_saves(7, 'devotion') == {'imune': ['encanto']}
    assert pal.auras_saves(10, 'devotion') == {'imune': ['encanto', 'medo']}
    assert pal.auras_saves(11, 'vengeance') == {'imune': ['medo']}
    assert 'psiquico' in pal.auras_saves(7, 'ancients')['res']
    s = pal.saves_pal(11, {'for': 4, 'des': 0, 'con': 1, 'int': -1, 'sab': 1, 'car': 3}, 11, 3, sub='devotion')
    assert s['sv']['sab'] == 1 + 4 + 3 and s['imune'] == ['encanto', 'medo']
