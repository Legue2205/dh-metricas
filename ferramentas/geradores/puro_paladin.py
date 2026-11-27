"""-puro do Paladin (mini-mutirão 22/11): builds do RPGBot sem a multiclasse, fatias 3/5/7/9/11, grupo RPGBot.
Rodar da raiz: python ferramentas/geradores/puro_paladin.py && python -m dh expandir
  - rpgbot-paladin-conquest-puro: a build de Conquest sem os 2 níveis de Warlock (Paladin 9 e 11 no lugar de 8/W1, 8/W2).
  - rpgbot-paladin-devotion-puro: a build Curseedge sem os 2 níveis de Sorcerer (Paladin = nível de personagem).
Números das features = pal.py (passada 1)."""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import marcial  # noqa: E402
from marcial import A, M, ctrl, hp, pb, escrever, NIV  # noqa: E402
import pal  # noqa: E402

marcial.CLASSE = 'paladin'
PURO = "Extensão simples da build do RPGBot sem a multiclasse (níveis adiantados, atributos e feats remendados); a build original continua como referência."
FONTE = lambda slug: {"tipo": "rpgbot", "url": f"https://rpgbot.net/dnd5/characters/classes/paladin/subclasses/{slug}/",
                      "nota": "Extensão simples sem multiclasse; mini-mutirão 22/11."}


def conquest(L):
    P = pb(L); s = 3 if L < 5 else 4; cha = 3 if L < 9 else 4; con = 2
    m = M(s, 0, con, -1, -1, cha); b = P + s; n = 1 if L < 5 else 2; ex = '+1d8' if L >= 11 else ''
    ca = 18 if L < 7 else 20; cd = 8 + P + cha

    def atk(bonus=0, frac=1.0, vant=0.0, de=''):
        return {"ataques": [A(n * frac, b + bonus, '1d8', s + 2, ex + de, vantagem=vant, nota="espada longa (Dueling)"),
                            A(0.5, b, '1d8', s + 2, ex, nota="ataque de oportunidade (reação em 50%)")]}
    aoc = [{"n": 0.75, "cd": cd, "save": "Sab", "dano": str(L // 2), "meio": False,
            "nota": "Aura of Conquest no amedrontado"}] if L >= 7 else []
    def com(dn): return dict(dn, com_save=dn.get('com_save', []) + aoc) if aoc else dn
    ext = [dict(id='conquista', hip='Conquering Presence no round 1 (ação), ataques nos rounds 2–4',
                dano=com(atk(frac=0.75)), gasta={"canal": 1},
                controle=ctrl('tank', [{"tipo": "area", "nome": "Conquering Presence", "magia": "conquering_presence",
                                        "cd": cd, "so_corpo_a_corpo": True}])),
           dict(id='agathys', hip='Armor of Agathys (1º) antes da luta: 5 PV temporários', dano=atk(),
                defesa={"pvt_luta": 5}, gasta={"espacos": {"1": 1}})]
    if L >= 5:
        ext.append(dict(id='arma-espiritual', hip='Spiritual Weapon (2º; ação bônus, rounds 2–4)',
                        dano={"ataques": atk()['ataques'] + [A(0.75, P + cha, '1d8', cha, nota="Spiritual Weapon")]},
                        gasta={"espacos": {"2": 1}}))
    if L >= 9:
        ext.append(dict(id='medo', hip='Fear (3º) no round 1 (ação), ataques nos rounds 2–4', dano=com(atk(frac=0.75)),
                        gasta={"espacos": {"3": 1}},
                        controle=ctrl('tank', [{"tipo": "area", "nome": "Fear", "magia": "fear", "cd": cd}])))
    fat = pal.montar(L, L, atk, dict(ca=ca, pv=hp([10] * L, con), saves=pal.saves_pal(L, m, L, cha, sub='conquest', ataques=n)),
                     pal.esp_pal(L), cha, extras=ext, outros=pal.canal(L, P))
    fat['_texto'] = {3: "Variant Human (Shield Master); espada longa + escudo, Dueling; cota de malha + escudo (18).",
                     5: "For 18 (4); Extra Attack; Spiritual Weapon/Hold Person.", 7: "Placas (20); Aura of Conquest.",
                     9: "Car 18 (8); magias de 3º (Fear) no lugar de Warlock 1.",
                     11: "Improved Divine Smite no lugar de Warlock 2."}[L]
    return fat


def devotion(L):
    P = pb(L); s = 2; cha = 3; con = 3; m = M(s, -1, con, -1, -1, cha); b = P + s
    n = 2 if L >= 5 else 1; ex = '+1d8' if L >= 11 else ''
    ca = 16 if L < 7 else 18
    pw = {"poder": [-5, 10]} if L >= 9 else {}

    def atk(bonus=0, frac=1.0, vant=0.0, de=''):
        return {"ataques": [A(n * frac, b + bonus, '2d6', s, ex + de, vantagem=vant, nota="espadão", **pw),
                            A(0.5, b, '2d6', s, ex, nota="ataque de oportunidade (reação em 50%)", **pw)]}
    ext = [dict(id='arma-sagrada', hip='Sacred Weapon (ação no round 1: +Car no acerto a luta toda)',
                dano=atk(bonus=cha, frac=0.75), gasta={"canal": 1})]
    fat = pal.montar(L, L, atk, dict(ca=ca, pv=hp([10] * L, con), saves=pal.saves_pal(L, m, L, cha, sub='devotion', ataques=n)),
                     pal.esp_pal(L), cha, extras=ext, outros=pal.canal(L, P))
    fat['_texto'] = {3: "Paladin 3: Sacred Weapon; espadão, Blessed Warrior; cota de malha (16).",
                     5: "Metamagic Adept (4; sem truque de Sorcerer: sem uso modelado); Extra Attack.",
                     7: "Placas (18); Aura of Protection.", 9: "Great Weapon Master (8); Aura of Devotion; magias de 3º.",
                     11: "Improved Divine Smite."}[L]
    return fat


COMUM = " Comum: Find Steed, curas fora de luta, smite guardado para o crítico."
B = [
    ('rpgbot-paladin-conquest-puro', 'oath-of-conquest', 'Oath of Conquest Paladin puro (extensão da build do RPGBot)',
     'Paladin (Conquest) sem multiclasse, Variant Human, Shield Master 1, For 18 4, Car 18 8; espada longa + escudo, Dueling', conquest,
     {"resumo": "A build de Conquest sem o dip de Warlock: Conquering Presence, Aura of Conquest, Fear no 9 e Improved Divine Smite no 11.",
      "estrategia": PURO,
      "nao_modelado": "Shield Master (derrubar), Guided Strike, Bestow Curse, retorno do Armor of Agathys, Scornful Rebuke." + COMUM}),
    ('rpgbot-paladin-devotion-puro', 'oath-of-devotion', 'Oath of Devotion Paladin puro (extensão da build do RPGBot)',
     'Paladin (Devotion) sem multiclasse, Astral Elf, Metamagic Adept 4, GWM 8; espadão, Blessed Warrior', devotion,
     {"resumo": "A build Curseedge sem o dip de Sorcerer: Sacred Weapon, espadão e GWM no 8; sem Booming Blade nem Shield.",
      "estrategia": PURO,
      "nao_modelado": "Metamagic Adept (sem magia de Sorcerer para acelerar), Blessed Warrior (truques), "
                      "Astral Elf (Astral Trance etc.)." + COMUM}),
]

if __name__ == '__main__':
    for id_, slug, nome, build, fn, desc in B:
        escrever(id_, slug, nome, build, desc, {L: fn(L) for L in NIV}, fonte=FONTE(slug))
