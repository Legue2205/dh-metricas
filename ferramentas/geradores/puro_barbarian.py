"""-puro do Barbarian (mini-mutirão 22/11): Ancestral Guardian do RPGBot sem os níveis de Wizard e Fighter.
Rodar da raiz: python ferramentas/geradores/puro_barbarian.py && python -m dh expandir
Barbarian 11 puro, Shadar-Kai, rapieira + escudo de Destreza (como a build original); Elven Accuracy no 4 (Des 17),
ASI do 8 em Des (19). Sem familiar (Help), Arcane Deflection nem Dueling. Ganha Extra Attack no 5, Spirit Shield no 6,
Brutal Critical no 9 e Spirit Shield 3d6 no 10.
"""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import marcial
from marcial import A, M, mod, pb, sv, furias, hp, linha, ctrl, escrever, NIV  # noqa: E402
marcial.CLASSE = 'barbarian'

DS = {"adv": ["Des"]}
RES = {"resist": True}


def ag(L):
    dx = {3: 16, 5: 17, 7: 17, 9: 19, 11: 19}[L]; d = mod(dx); P = pb(L)
    m = M(1, d, 3, 1, -1, -1); b = P + d; n = 1 if L < 5 else 2; bc = 1 if L >= 9 else 0
    ca = 10 + d + 3 + 2
    ss = dict(sv=sv(L, m), ataques=n, **DS)
    dano = {"ataques": [A(n, b, '1d8', d, bc=bc)]}
    sem = linha('principal', 'sem fúria: rapieira e escudo, sem Reckless Attack (ataque de Destreza)', dano, {}, papel='tank')
    sup = reac = None
    if L >= 6:
        sup = [{"nome": f"Spirit Shield (reação: −{2 if L < 10 else 3}d6 no dano de um aliado)", "lado": "def",
                "modelo": "cura", "usos_luta": 2, "pv": 7 if L < 10 else 10.5}]
        reac = [{"uso": "Spirit Shield", "fracao": 0.5, "eixos": ["suporte"]}]
    fur = linha('furia', 'fúria em toda luta: Ancestral Protectors no 1º alvo atingido (a fúria não soma dano: ataque de Destreza)',
                dano, RES, controle=ctrl('tank', [{"tipo": "ancestral_protectors", "nome": "Ancestral Protectors", "bonus": b}]),
                gasta={"furia": 1}, suporte=sup, reacao=reac)
    rec = {"espacos": {}, "outros": {"furia": {"qtd": furias(L), "volta": "longo"}}}
    txt = {3: "Ancestral Protectors; Unarmored Defense com escudo (18).",
           5: "Elven Accuracy (4, Des 17; sem fonte de vantagem, vale só o +1); Extra Attack.",
           7: "Spirit Shield 2d6 (6); Feral Instinct.", 9: "Des 19 (8); Brutal Critical; fúria +3.",
           11: "Consult the Spirits e Spirit Shield 3d6 (10); Relentless Rage."}[L]
    return dict(_texto=txt, corpo=dict(ca=ca, pv=hp([12] * L, 3), saves=ss), recursos=rec, linhas=[sem, fur])


escrever('rpgbot-barbarian-ancestral-guardian-puro', 'ancestral-guardian',
         'Ancestral Guardian Barbarian puro (extensão da build do RPGBot)',
         'Barbarian (Ancestral Guardian) sem multiclasse, Shadar-Kai, rapieira + escudo de Destreza; Elven Accuracy 4 (Des 17), Des 19 8',
         {"resumo": "A build Furious About Mediocre Strength sem os níveis de Wizard e Fighter: Guardião Ancestral de Destreza com rapieira e escudo.",
          "estrategia": "Extensão simples da build do RPGBot sem a multiclasse (níveis adiantados, atributos e feats remendados); a build original continua como referência.",
          "nao_modelado": "Elven Accuracy sem fonte de vantagem (sem o familiar); Consult the Spirits; teleporte do Shadar-Kai; Booming Blade; Relentless Rage; Feral Instinct."},
         {L: ag(L) for L in NIV},
         fonte={"tipo": "rpgbot", "url": "https://rpgbot.net/dnd5/characters/classes/barbarian/subclasses/ancestral-guardian/",
                "nota": "Extensão simples sem multiclasse; mini-mutirão 22/11."})
