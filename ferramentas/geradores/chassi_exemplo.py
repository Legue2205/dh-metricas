"""MODELO das builds de chassi (22/11): Fighter Champion, striker de espadão, sem feat e com GWM.
Rodar da raiz: python ferramentas/geradores/chassi_exemplo.py && python -m dh expandir
As sessões do mini-mutirão copiam este formato em ferramentas/geradores/chassi_<classe>.py.
"""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402

ORDEM = ('for', 'con', 'des', 'sab', 'car', 'int')   # Str principal, Con secundário
AS = {"qtd": 1, "volta": "curto"}


def fatia(L, feat=None):
    s = C.atributos('fighter', L, ORDEM, feat=feat); m = C.mods(s); p = C.pb(L)
    n = 2 if L < 11 else 3
    crit = 19                                             # Improved Critical (3)
    gwm = {"poder": [-5, 10]} if feat == 'Great Weapon Master' else {}
    atk = {"n": n, "bonus": m['for'] + p, "dano": f"2d6+{m['for']}+1.33", "crit_em": crit, **gwm}   # GWF ≈ +1,33 no 2d6
    ca = 18                                               # placas (sem escudo: espadão)
    ctl = {"atencao": C.atencao('striker'), "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}
    surge = dict(atk, n=round(n / 4, 4))                  # Action Surge: 1 round de 4
    linhas = [
        {"id": "principal", "hipotese": "espadão com GWF todo round", "dano": {"ataques": [atk]}, "defesa": {},
         "controle": ctl, "saves": {}},
        {"id": "surge", "herda": "principal", "plano": "prioritaria", "hipotese": "Action Surge num round",
         "dano": {"ataques": [atk, surge]}, "gasta": {"action_surge": 1}},
    ]
    corpo = {"ca": ca, "pv": C.hp(10, L, m['con']), "saves": {"sv": C.sv(L, m, ('for', 'con')), "ataques": n}}
    return {"corpo": corpo, "recursos": {"espacos": {}, "outros": {"action_surge": AS}}, "linhas": linhas,
            "_texto": f"atributos {s}"}


for feat in (None, 'Great Weapon Master'):
    C.escrever('fighter', 'champion', 'striker', {L: fatia(L, feat) for L in C.NIV},
               build=f"Fighter (Champion), striker de espadão, placas, GWF" + (f"; {feat} no 4" if feat else "; sem feat"),
               desc={"resumo": "Chassi do Champion: o Fighter base de espadão com Improved Critical.",
                     "nao_modelado": "Remarkable Athlete; Second Wind; Indomitable."},
               feat=feat, url="https://rpgbot.net/dnd5/characters/classes/fighter/subclasses/champion/")
