"""Passada 3 (19/11): marcas no Corpo e frontliner de referência único."""
import numpy as np

from dh.base import encontro
from dh.controle import atencao as A, campo as C, efeitos, total
from dh.premissas import P


def test_party_de_referencia_dois_frontliners():
    L = 7
    party = A.party_com(dict(papel='atirador', ca=17, pv=50, front=False, dpr=20), L)
    assert [p['papel'] for p in party] == ['frontliner', 'frontliner', 'atirador', 'conjurador']
    fr = A.ref('tank', L)
    assert fr == A.ref('striker', L) == A.ref('frontliner', L)
    assert fr['ca'] == min(21, A.ca_marcial(L) + 1) and fr['pv'] == 11 + (L - 1) * 8
    assert abs(fr['dpr'] - 0.85 * A.dpr_ref(L)) < 1e-9
    for papel in ('tank', 'striker', 'frontliner'):
        px = A.party_com(dict(papel=papel, ca=18, pv=60, front=True, dpr=20), L)
        assert px[0]['pv'] == 60 and px[1]['nome'] == 'Frontliner de referência'


def test_marca_no_corpo():
    assert 'ancestral_protectors' in efeitos.TIPOS_CORPO
    assert P('controle.peso_no_controle.ancestral_protectors') == P('controle.peso_no_controle.sentinela')
    corpo = dict(ca=18, pv=60)
    ficha = A.ficha(dict(papel='tank', dpr=20, soft=0.15), corpo)
    sem = efeitos.compilar([{'tipo': 'ameaca'}], corpo, 7)
    com = efeitos.compilar([{'tipo': 'ameaca'}, {'tipo': 'ancestral_protectors', 'nome': 'Marca', 'bonus': 8,
                                                  'resistencia': False}], corpo, 7)
    assert com.marca == {'Marca'} and com.peso_ctrl['Marca'] == 0.25
    C.configurar(1000, 11)
    reg = total.Regua()
    g0, _ = total.avaliar_nivel(sem, ficha, 7, reg)
    g1, _ = total.avaliar_nivel(com, ficha, 7, reg)
    assert g1['vidas_atencao'] > g0['vidas_atencao'] + 0.01     # a marca protege os aliados (Corpo)
    assert g1['vidas_party'] > g0['vidas_party']
    assert abs(g1['vidas_proprio'] - g0['vidas_proprio']) < 1e-9  # quem marca não ganha nada para si


def test_marca_reduz_so_os_outros():
    E = encontro('Dupla', 7)
    party = A.party_com(dict(papel='tank', ca=18, pv=60, front=True, dpr=20), 7)
    _, f0 = A.vida(E, party, 1, detalhe=True)
    _, f1 = A.vida(E, party, 1, detalhe=True, marca=(0, np.full(len(E), 0.3)))
    assert f1[0] == f0[0] and all(b < a for a, b in zip(f0[1:], f1[1:]) if a > 0)
