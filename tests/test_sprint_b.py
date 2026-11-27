"""Sprint B (27/11): quem conta como linha de concentração no ajuste genérico (dh/concentracao.py) e as escolhas do
chassi que o diagnóstico do dano dentro da classe apontou (Path to the Grave em 2 espaços, Kensei corpo a corpo,
Haste/Tenser's do Bladesinger declarados como concentração)."""
import json
from pathlib import Path

from dh import concentracao as K
from dh.controle import campo

RAIZ = Path(__file__).resolve().parents[1]
POSTURA = {"atencao": {"papel": "conjurador", "front": False, "conc": True}, "fontes": [{"tipo": "ameaca", "nome": "Corpo"}]}
PRINC = {"id": "principal", "principal": True, "controle": json.loads(json.dumps(POSTURA)),
         "dano": {"ataques": [{"n": 2, "bonus": 7, "dano": "1d10+4", "nota": "Eldritch Blast"}]}}


def tem(l, principal=PRINC): return K._tem_conc(l, campo.MAGIAS, principal)


def test_postura_da_principal_nao_vira_concentracao():
    # Inflict Wounds / Fireball numa build de conjurador: o atencao.conc só repete a postura da principal
    l = {"id": "punho", "controle": json.loads(json.dumps(POSTURA)),
         "dano": {"ataques": [{"n": 0.25, "bonus": 7, "dano": "8d10", "nota": "Inflict Wounds (4º)"}]}}
    assert not tem(l)
    assert tem(l, principal={"id": "principal", "principal": True})       # declarado só na linha: vale


def test_concentracao_pelo_nome_raw():
    sg = {"id": "guardioes", "area": [{"nome": "Spirit Guardians (4º)", "tipo": "aura", "alvos": 3, "dano": "4d8", "cd": 15}]}
    inv = {"id": "invocacao", "invocacoes": [{"nome": "Summon Aberration (4º)", "quantidade": 1, "pv": 40, "ca": 15}]}
    hx = {"id": "area+hex", "dano": {"ataques": [{"n": 1, "bonus": 7, "dano": "1d10+4+1d6", "nota": "Eldritch Blast + Agonizing Blast + Hex"}]}}
    curse = {"id": "eb", "dano": {"ataques": [{"n": 2, "bonus": 7, "dano": "1d10+5", "nota": "Eldritch Blast + Hexblade's Curse"}]}}
    forma = {"id": "polimorfo", "hipotese": "Polymorph em si mesmo (Giant Ape)"}
    assert tem(sg) and tem(inv) and tem(hx) and tem(forma)
    assert not tem(curse)                                                   # "Hex" não pega "Hexblade's Curse"


def test_ajuste_usa_a_regra_nova():
    b = {"posicao": "striker", "corpo": {"saves": {"sv": {"con": 2}}},
         "linhas": [{"id": "principal", "principal": True},
                    {"id": "guardioes", "area": [{"nome": "Spirit Guardians", "tipo": "aura", "alvos": 3, "dano": "3d8", "cd": 15}]}]}
    L = {"principal": {"dano": {"nivel_eq": 2.0}}, "guardioes": {"dano": {"nivel_eq": 6.0}}}
    Lc, inf = K.ajustar(b, L)
    assert 'guardioes' in inf and 2.0 < Lc['guardioes']['dano']['nivel_eq'] < 6.0


def _linhas(arq, nv):
    return {l['id']: l for l in json.loads((RAIZ / 'builds' / f'{arq}-{nv}.json').read_text(encoding='utf-8'))['linhas']}


def test_chassi_grave_kensei_bladesinger():
    for nv in (7, 11):
        g = _linhas('chassi-cleric-grave', nv)
        top = max(int(s) for s in g['punho']['gasta']['espacos'])
        assert max(int(s) for s in g['punho-barato']['gasta']['espacos']) < top
        k = _linhas('chassi-monk-kensei', nv)
        assert {'cac', 'cac-rajada', 'cac-deft'} <= set(k)
        w = _linhas('chassi-wizard-bladesinging', nv)
        assert w['canto-haste']['dano'].get('concentracao') == 'haste'
    assert _linhas('chassi-wizard-bladesinging', 11)['canto-tenser']['dano'].get('concentracao') == 'tensers_transformation'
