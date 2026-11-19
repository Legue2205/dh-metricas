from dh import horda


def _l(**k):
    base = {"dano": {"ataques": [{"n": 1, "bonus": 7, "dano": "2d10"}]}}
    base.update(k); return base


FB = {"nome": "Fireball", "usos": [{"alvos": 4, "dano": "8d6", "cd": 15, "slot": 3}]}


def test_area_acelera_e_selecao_ajuda():
    so = horda.avaliar(_l())['rounds'][9]
    fb = horda.avaliar(_l(area=[FB]))['rounds'][9]
    dois = horda.avaliar(_l(area=[{"nome": "2x", "usos": FB['usos'] * 2}]))['rounds'][9]
    sel = horda.avaliar(_l(area=[{"nome": "2x sel", "usos": [dict(FB['usos'][0], seletiva=True)] * 2}]))['rounds'][9]
    assert fb < so and dois < fb and sel <= dois + 0.3


def test_cleave_ajuda_marcial():
    sem = horda.avaliar(_l())['rounds'][9]
    com = horda.avaliar(_l(area=[{"nome": "Horde Breaker", "tipo": "cleave_ataque", "bonus": 7, "dano": "1d8+4", "p": 0.6}]))['rounds'][9]
    assert com < sem
