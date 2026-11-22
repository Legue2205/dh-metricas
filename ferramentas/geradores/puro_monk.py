"""-puro do Monk (mini-mutirão 22/11): Kensei do RPGBot sem o Fighter 1. Rodar da raiz:
python ferramentas/geradores/puro_monk.py && python -m dh expandir
Mesma build de mon.py (Variant Human com Crossbow Expert, besta de mão, Sharpshooter no 4, Des 18 no 8), mas Monk em todos
os níveis: sem Archery, PV d8, saves For/Des, Evasion/Stillness no 7, Sharpen the Blade no 11."""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import marcial
from marcial import A, M, hp, linha, mod, pb, sv, escrever, NOTA
marcial.CLASSE = 'monk'
NIV = marcial.NIV


def die(L): return 4 if L < 5 else 6 if L < 11 else 8


def kensei(L):
    dx = 16 if L < 9 else 18; cn, ws = 14, 16; d, w, P = mod(dx), mod(ws), pb(L)
    m = M(0, d, 2, -1, w, -1); b = P + d; n = 1 if L < 5 else 2
    ss = dict(sv=sv(L, m, ('for', 'des')))
    if L >= 7: ss.update(evasion=True, stillness=True)
    if L >= 11: ss['imune'] = ['veneno']
    pw = {"poder": [-5, 10]} if L >= 5 else {}
    dado = f'1d{max(6, die(L))}'
    def at(bb=0): return [A(n, b + bb, dado, d + bb, **pw), A(1, b + bb, dado, d + bb, nota="Crossbow Expert (ação bônus)", **pw)]
    ls = [linha('principal', 'besta de mão com Crossbow Expert' + (' e Sharpshooter' if pw else '') + ', sem ki',
                {"ataques": at()}, {}, papel='atirador')]
    if L >= 6:
        ls.append(linha('deft', f'+ Deft Strike (1 ki por acerto: +1d{die(L)}) com o ki da luta ({L // 2} ki)',
                        {"ataques": at(), "por_luta": [{"dano": f"1d{die(L)}", "usos": L // 2, "nota": "Deft Strike"}]}, {},
                        papel='atirador', gasta={"ki": L // 2}))
    if L >= 5:
        ls.append(linha('mira', f'+ Focused Aim com o ki da luta ({L // 2} ki: +2 por ki depois de errar)',
                        {"ataques": at(), "focused_aim": {"ki": L // 2}}, {}, papel='atirador', gasta={"ki": L // 2}))
    if L >= 11:
        ls.append(linha('afiar', 'Sharpen the Blade (3 ki: +3 no acerto e no dano, 1 minuto = 1 luta)',
                        {"ataques": at(3)}, {}, papel='atirador', gasta={"ki": 3}))
    rec = {"espacos": {}, "outros": {"ki": {"qtd": L if L >= 2 else 0, "volta": "curto"}}}
    txt = {3: "Way of the Kensei; besta de mão com Crossbow Expert (Variant Human).", 5: "Extra Attack, Stunning Strike; Sharpshooter (4).",
           7: "One with the Blade (Deft Strike, 6); Evasion, Stillness of Mind.", 9: "Des 18 (8).",
           11: "Sharpen the Blade; Purity of Body; Martial Arts d8."}[L]
    return dict(_texto=txt, corpo=dict(ca=10 + d + w, pv=hp([8] * L, mod(cn)), saves=ss), recursos=rec, linhas=ls)


escrever('rpgbot-monk-kensei-puro', 'kensei', "Kensei Monk puro (extensão da build do RPGBot)",
         'Monk (Kensei) sem multiclasse, Variant Human (Crossbow Expert), besta de mão; Sharpshooter 4, Des 18 8',
         {"resumo": "A build Why don't you just shoot it? sem o Fighter 1: besta de mão com Crossbow Expert e Sharpshooter, sem Archery.",
          "estrategia": "Extensão simples da build do RPGBot sem a multiclasse (níveis adiantados); a build original continua como referência.",
          "nao_modelado": "Agile Parry e Kensei's Shot (competem com o Crossbow Expert pela ação bônus); Deflect Missiles; Stunning Strike (só corpo a corpo)."},
         {L: kensei(L) for L in NIV},
         fonte={"tipo": "rpgbot", "url": "https://rpgbot.net/dnd5/characters/classes/monk/subclasses/kensei/",
                "nota": "Extensão simples sem multiclasse (puro, 22/11). " + NOTA})
