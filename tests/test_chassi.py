"""Builds de chassi (22/11): rótulos passam da progressão para as fatias; regra de atributos."""
import sys
sys.path.insert(0, 'ferramentas/geradores')

from dh.progressao import fatias


def test_rotulos_passam_para_as_fatias():
    prog = {"id": "t-chassi", "nome": "t", "grupo": "Chassi", "classe": "fighter", "subclasse": "champion",
            "posicao": "striker", "feat": None, "variante": "sem-feat",
            "base": {"corpo": {"ca": 18, "pv": 60, "saves": {"sv": {}}}, "recursos": {"espacos": {}},
                     "linhas": [{"id": "principal", "principal": True, "dano": {"ataques": [{"n": 2, "bonus": 7, "dano": "2d6+4"}]}}]},
            "niveis": {"7": {}, "11": {}}}
    out = fatias(prog)
    assert set(out) == {7, 11}
    for b in out.values():
        assert (b['classe'], b['subclasse'], b['posicao'], b['variante']) == ('fighter', 'champion', 'striker', 'sem-feat')


def test_atributos_sem_e_com_feat():
    import chassi as C
    o = ('des', 'con', 'sab', 'car', 'int', 'for')
    assert C.atributos('rogue', 3, o)['des'] == 17                       # 15 + 2 de raça
    assert C.atributos('rogue', 7, o)['des'] == 19                       # ASI 4
    assert C.atributos('rogue', 7, o, feat='Sharpshooter')['des'] == 17  # o ASI 4 virou feat
    assert C.atributos('rogue', 11, o) == {'for': 8, 'des': 20, 'con': 18, 'int': 10, 'sab': 13, 'car': 12}   # ASIs 4, 8, 10
    assert C.atributos('wizard', 7, ('int', 'con', 'des', 'sab', 'car', 'for'), feat='x', meio_feat='int')['int'] == 18
