"""Divine Soul Sorcerer PURO (22/11): a build do RPGBot (5e Mystic Theurge) sem o nível de Cleric (Order).
Rodar da raiz: python ferramentas/geradores/puro_sorcerer.py
Remendos: Sorcerer = nível de personagem; sem armadura pesada (Mage Armor, que gasta 1 espaço de 1º); saves de
Sorcerer (Con/Car); Des e Sab trocadas (Des 14, Sab 8) porque sem armadura pesada a Des vira CA; ASIs no 4/8
(Telekinetic 4 → Car 18; Car +2 8 → 20); Fireball a partir do 5 (antes vinha 1 nível depois).
"""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import wiz as W  # noqa: E402
from wiz import fatia, escrever, hpcalc, M, FB, U, prof  # noqa: E402
from chassi_sorcerer import esp_sor, fb, BLESS  # noqa: E402

W.espacos = esp_sor
W.FONTE = lambda slug: {"tipo": "rpgbot", "url": f"https://rpgbot.net/dnd5/characters/classes/sorcerer/subclasses/{slug}/",
                        "nota": "Extensão simples sem multiclasse (22/11); premissas congeladas."}
POLY = lambda cd: U("Polymorph", "polymorph", cd, 4)

F = {}
for L, c in ((3, 3), (5, 4), (7, 4), (9, 5), (11, 5)):
    cd = 8 + prof(L) + c; a = prof(L) + c; m = M(-1, 2, 3, 0, -1, c)
    f = fatia(L, L, L if L >= 2 else 0, m, ('con', 'car'), 13 + 2, hpcalc([6] * L, 3),
              lambda n, L=L, a=a: fb(L, a, n), [POLY(cd)] if L >= 9 else [], None, [FB(cd)] if L >= 5 else [])
    f['linhas'].append(dict(id="bless", herda="principal", hipotese="Bless nos aliados", dano=fb(L, a, 0.75),
                            suporte={"fontes": [BLESS]}, gasta={"espacos": {"1": 1}}))
    f['_texto'] = f"Sorcerer {L}; Mage Armor (CA 15)" + ("; Telekinetic (4), Car 18" if L >= 5 else "") + ("; Car 20 (8)" if L >= 9 else "") + "."
    F[L] = f
escrever('rpgbot-sorcerer-divine-soul-puro', 'divine-soul', 'Divine Soul Sorcerer puro (extensão da build do RPGBot)',
 "Sorcerer (Divine Soul) sem multiclasse, Shifter, Mage Armor, Telekinetic 4, Car +2 8; Car 17 → 18 (4) → 20 (8)",
 {"resumo": "A build 5e Mystic Theurge sem o dip de Order Cleric: sem armadura pesada nem Voice of Authority, em troca de um nível de Sorcerer a mais (espaços e pontos).",
  "estrategia": "Extensão simples da build do RPGBot sem a multiclasse (níveis adiantados, atributos e feats remendados); a build original continua como referência. Bless no 1º round; Fireball em grupos; Polymorph.",
  "nao_modelado": "Silvery Barbs; Twinned (Haste, Polymorph, Death Ward) e demais metamagias; Favored by the Gods; Healing Word; Shield of Faith; Guiding Bolt; Bestow Curse; Mass Cure Wounds; Telekinetic (empurrão de ação bônus)."}, F)
