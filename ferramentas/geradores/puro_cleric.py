"""Cleric -puro (mini-mutirão 22/11): Grave, Life, Order e Trickery do RPGBot sem a multiclasse.
Níveis de Cleric = nível de personagem; raça, armadura e feats da build mantidos; o que dependia do dip foi remendado
(ver descricao). Reaproveita as peças de cle.py/cle2.py sem reemitir as builds originais. Rodar da raiz do repo;
depois `python -m dh expandir`."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import wiz
_real = wiz.escrever
wiz.escrever = lambda *a, **k: None          # importar cle/cle2 não reescreve as progressões originais
import cle, cle2
cle.escrever = _real
from cle import FATIAS, fatia, emit, toll, sacred, wor, HP, BAN, espacos, mods_, URL
from cle2 import CMD, POLY
from wiz import prof, hpcalc, AT

wiz.FONTE = lambda slug: {"tipo": "rpgbot", "url": URL[slug], "nota": "Extensão simples sem multiclasse; mini-mutirão 22/11."}
PURO = ("Extensão simples da build do RPGBot sem a multiclasse (níveis de Cleric = nível de personagem, atributos e feats "
        "remendados); a build original continua como referência. ")
CANAL = lambda L: 1 if L < 6 else 2
NM = lambda L: (L + 1) // 2

# ---------- Grave puro (sem Sorcerer 2) ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4 if L < 9 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    cant = lambda n, L=L, cd=cd, w=w: toll(L, cd, n, f"+{w}" if L >= 9 else "")      # Potent Spellcasting (Cleric 8)
    esp = espacos(L); s = max(int(x) for x, q in esp.items() if q > 0)
    def soco(n, s, atk=atk): return {"ataques": [{"n": n, "bonus": atk, "dano": f"{2 * (s + 2)}d10", "nota": f"Inflict Wounds ({s}º) no alvo vulnerável (Path to the Grave: dados dobrados)"}]}
    extras = [dict(id="punho", hipotese="Path to the Grave (ação) e Inflict Wounds no maior espaço no round seguinte",
                   dano=cle.merge(cant(0.5), soco(0.25, s)), gasta={"canal": 1, "espacos": {str(s): 1}}),
              dict(id="punho-rapido", hipotese="Path to the Grave + Inflict Wounds acelerado (Quicken Spell, Metamagic Adept) no mesmo round",
                   dano=cle.merge(cant(0.75), soco(0.25, s)), gasta={"canal": 1, "metamagia": 1, "espacos": {str(s): 1}})]
    f = fatia(L, mods_(-1, 2, 1, -1, w, 1), ('sab', 'car'), 18 if L < 5 else 19, hpcalc([8] * L, 1), cant, cd, atk, w,
              'frontliner', True, NM(L), canal=CANAL(L), esp=esp, ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []), extras=extras,
              outros={"metamagia": {"qtd": 1, "volta": "longo"}},
              reac=("Sentinel at Death's Door", "anula_critico", w / 4) if L >= 6 else None, cura_extra=1.5)
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}" + ("; Potent Spellcasting" if L >= 9 else "") + "; Quicken 1/dia (Metamagic Adept)."
    F[L] = f
emit('rpgbot-cleric-grave-puro', 'grave', 'Grave Domain Cleric puro (extensão da build do RPGBot)',
     "Cleric (Grave) sem multiclasse, Custom Lineage (Metamagic Adept: Quicken, Extend); Fey Touched 4; escama → meia-armadura + escudo; Sab 20 (8)",
     {"resumo": "A build One Punch sem os 2 níveis de Sorcerer: Path to the Grave + Inflict Wounds no maior espaço, com Quicken só pelos 2 pontos do Metamagic Adept.",
      "estrategia": PURO + "Sem o Sorcerer, Quicken fica em 1/dia em todas as fatias (sem os pontos extras do 9+); a ASI do Cleric 8 chega no personagem 8 (Sab 20 no 9); Potent Spellcasting a partir do 9.",
      "nao_modelado": "Conversão de espaços em pontos de feitiçaria (não existe mais); Hex e True Strike; Absorb Elements no soco; Circle of Mortality fora do Healing Word; Sentinel at Death's Door em aliados; Path to the Grave dado a um aliado; Keeper of Souls."}, F)

# ---------- Life puro (sem Druid 2) ----------
F = {}
for L in FATIAS:
    w = 3 if L < 9 else 4; con = 3 if L < 5 else 4; p = prof(L); cd = 8 + p + w; atk = p + w
    bs = "+1d8" if L >= 8 else ""
    cant = lambda n, L=L, cd=cd, bs=bs: toll(L, cd, n, bs)
    extras = [dict(id="preservar", hipotese="Preserve Life na luta (Channel Divinity, ação) + truques", dano=cant(0.75),
                   suporte={"fontes": [{"nome": "Preserve Life", "lado": "def", "modelo": "cura", "usos_luta": 1, "pv": 5 * L}]},
                   gasta={"canal": 1})]
    f = fatia(L, mods_(2, 0, con, -1, w, -1), ('sab', 'car') + (('con',) if L >= 5 else ()), 18 if L < 7 else 20,
              hpcalc([8] * L, con), cant, cd, atk, w, 'frontliner', True, NM(L), canal=CANAL(L), esp=espacos(L),
              ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []), livres=[wor(L, cd)], extras=extras, cura_extra=3)
    f['_texto'] = f"Cleric {L}; Con {10 + 2 * con}" + (" (Resilient, 4)" if L >= 5 else "") + ("; Skill Expert Sab (8); Divine Strike" if L >= 9 else "") + ("; placas" if L >= 7 else "; cota de malha + escudo") + "."
    F[L] = f
emit('rpgbot-cleric-life-puro', 'life', 'Life Domain Cleric puro (extensão da build do RPGBot)',
     "Cleric (Life) sem multiclasse, Anão da Montanha (Custom Origin); armadura pesada + escudo; Resilient Con 4, Skill Expert 8",
     {"resumo": "A build Lifeberry sem os 2 níveis de Druid: tanque de armadura pesada com Spirit Guardians, Spiritual Weapon, Preserve Life e Healing Word reforçado pelo Disciple of Life.",
      "estrategia": PURO + "Sem o Druid não há Goodberry: a cura em massa de fim do dia sai (e o espaço de 1º volta ao pool); Resilient Con no 4 e Skill Expert no 8 (Sab 18 no 9); Divine Strike a partir do 9.",
      "nao_modelado": "Goodberry/Starry Form (perdidos com o Druid, não remendados); Blessed Healer; Beacon of Hope; Death Ward; Mass Healing Word e Mass Cure Wounds; Heroes' Feast."}, F)

# ---------- Order puro (sem Sorcerer 1) ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4 if L < 9 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    bs = "+1d8" if L >= 8 else ""
    cant = lambda n, L=L, cd=cd, bs=bs: toll(L, cd, n, bs)
    voz = lambda usos: {"nome": f"Voice of Authority ({usos} ataque{'s' if usos > 1 else ''} de aliado por reação)", "lado": "of", "modelo": "ataque_extra", "alvos": round(usos / 4, 2)}
    extras = [dict(id="bless", hipotese="Bless + Voice of Authority (1 ataque de aliado)", dano=cant(0.75), suporte={"fontes": [cle.BLESS, voz(1)]}, gasta={"espacos": {"1": 1}}),
              dict(id="voz", hipotese="Healing Word num aliado como ação bônus em 2 rounds (Voice of Authority) + truques",
                   dano=cant(1.0), suporte={"fontes": [voz(2)]}, gasta={"espacos": {"1": 2}})]
    f = fatia(L, mods_(-1, -1, 3, 0, w, 2), ('sab', 'car'), 18 if L < 7 else 20, hpcalc([8] * L, 3), cant, cd, atk, w,
              'conjurador', False, NM(L), canal=CANAL(L), ctrl=[CMD(cd), HP(cd)] + ([BAN(cd)] if L >= 7 else []), extras=extras)
    f['linhas'] = [l for l in f['linhas'] if not (l['id'] in ('bless', 'bless+arma')
                                                     and not any(x['nome'].startswith('Voice') for x in l['suporte']['fontes']))]
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}" + ("; placas" if L >= 7 else "; cota de malha") + " + escudo" + ("; Divine Strike" if L >= 9 else "") + "."
    F[L] = f
emit('rpgbot-cleric-order-puro', 'order', 'Order Domain Cleric puro (extensão da build do RPGBot)',
     "Cleric (Order) sem multiclasse, Shifter; armadura pesada + escudo; Fey Touched 4, Sab 20 (8)",
     {"resumo": "A build de Order sem o nível de Sorcerer: Bless e Healing Word disparam ataques dos aliados (Voice of Authority); Command, Hold Person e Banishment.",
      "estrategia": PURO + "O Sorcerer só dava Silvery Barbs e Favored by the Gods (ambos já fora do modelo) e Bless, que o Cleric tem; Fey Touched no 4 e Sab 20 no 8; Divine Strike a partir do 9.",
      "nao_modelado": "Command em mais alvos (upcast); Silvery Barbs (perdido com o Sorcerer); Embodiment of Law; Order's Demand; Heroism e Shield of Faith."}, F)

# ---------- Trickery puro (sem Rogue) ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4; dx = 3 if L < 9 else 4; p = prof(L); cd = 8 + p + w; atk = p + w; ab = p + dx
    bs = "+1d8" if L >= 8 else ""
    cant = lambda n, L=L, cd=cd, bs=bs: sacred(L, cd, n, bs)
    dup = dict(id="duplicidade", hipotese="Invoke Duplicity (Channel Divinity, concentração): rapieira com vantagem pela ilusão",
               dano={"ataques": [{"n": 1.0, "bonus": ab, "dano": f"1d8+{dx}{bs}", "vantagem": 1.0, "nota": "rapieira" + (" + Divine Strike" if L >= 8 else "")}]},
               controle={"atencao": AT(True, 'striker'), "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}, gasta={"canal": 1})
    f = fatia(L, mods_(-1, dx, 2, -1, w, 1), ('sab', 'car'), 18, hpcalc([8] * L, 2), cant, cd, atk, w,
              'conjurador', False, NM(L), canal=CANAL(L), esp=espacos(L), ctrl=[HP(cd)] + ([POLY(cd)] if L >= 7 else []), extras=[dup])
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}, Des {10 + 2 * dx}; peitoral + escudo" + ("; Divine Strike" if L >= 9 else "") + "."
    F[L] = f
emit('rpgbot-cleric-trickery-puro', 'trickery', 'Trickery Domain Cleric puro (extensão da build do RPGBot)',
     "Cleric (Trickery) sem multiclasse, Meio-elfo; peitoral + escudo; Sab 18 (4), Des 18 (8)",
     {"resumo": "A build Half-Elf Trickery sem os níveis de Rogue: Sacred Flame, Spirit Guardians e Spiritual Weapon; rapieira com vantagem do Invoke Duplicity, agora sem Sneak Attack.",
      "estrategia": PURO + "Sem o Rogue: saves Sab/Car (era Des/Int), sem Sneak Attack, Expertise nem Booming Blade do Arcane Trickster; a linha da duplicidade fica só com vantagem e Divine Strike (Cleric 8); Polymorph no 7.",
      "nao_modelado": "Sneak Attack, Expertise e Booming Blade (perdidos com o Rogue); Blessing of the Trickster; Invoke Duplicity para lançar magias à distância; Cloak of Shadows; Dimension Door; Improved Duplicity (17)."}, F)
