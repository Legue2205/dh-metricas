"""Cleric, lote 2 da passada 1 (19/11): Arcana, Forge, Knowledge, Order, Tempest, Trickery, Twilight, War.
Mesmas convenções do lote 1 (cle.py). Rodar da raiz do repo (reemite o lote 1, idêntico); depois `python -m dh expandir`."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import cle
from cle import (FATIAS, fatia, emit, toll, sacred, wor, sw, sg_dano, sg_area, BLESS, HP, BAN, espacos, maior, mods_, URL)
from wiz import prof, k, merge, U, area_sp, AT, hpcalc

URL.update({
    'arcana': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/arcana-domain/',
    'forge': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/forge/',
    'knowledge': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/knowledge-domain/',
    'order': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/order/',
    'tempest': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/tempest-domain/',
    'trickery': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/trickery-domain/',
    'twilight': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/twilight/',
    'war': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/war-domain/'})
CMD = lambda cd: U("Command", "command", cd, 1)
POLY = lambda cd: U("Polymorph", "polymorph", cd, 4)


def bb(L): return "" if L < 5 else "+1d8" if L < 11 else "+2d8"     # Booming Blade no acerto


# ---------- Arcana: "The Soloist" (Shillelagh + Booming Blade) ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4; p = prof(L); cd = 8 + p + w; atk = p + w
    pot = f"+{w}" if L >= 9 else ""
    dano_bb = f"1d8+{w}{bb(L)}{pot}"
    cant = lambda n, L=L, atk=atk, d=dano_bb: {"ataques": [{"n": n, "bonus": atk, "dano": d, "nota": "Shillelagh + Booming Blade" + (" (Potent Spellcasting)" if L >= 9 else "")}]}
    f = fatia(L, mods_(-1, 2, 2, 0, w, 0), ('sab', 'car'), 18 if L < 5 else 19, hpcalc([8] * L, 2), cant, cd, atk, w,
              'frontliner', True, (L + 1) // 2, canal=1 if L < 6 else 2, ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []),
              livres=[wor(L, cd, pot)])
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}" + (" (Telekinetic)" if L >= 5 else "") + ("; meia-armadura" if L >= 5 else "; escama") + " + escudo."
    F[L] = f
emit('rpgbot-cleric-arcana', 'arcana', 'Arcana Domain Cleric (RPGBot: The Soloist)',
     "Cleric (Arcana), Custom Origin; Magic Initiate (Druid: Shillelagh) 1, Telekinetic 4, War Caster 8; Booming Blade e Mage Hand (Arcane Initiate); armadura média + escudo",
     {"resumo": "Clérigo arcano de linha de frente que bate com Shillelagh e Booming Blade (Sabedoria no acerto e no dano) e cobre todos os papéis com magia.",
      "estrategia": "Corpo a corpo com Shillelagh + Booming Blade; Spirit Guardians e Spiritual Weapon; Hold Person e Banishment para tirar alguém da luta.",
      "nao_modelado": "Dano secundário do Booming Blade; empurrão do Telekinetic e War Caster; Magic Missile; Arcane Abjuration; Spell Breaker; Absorb Elements; Guidance e magias de perícia; Flame Strike e Summon Celestial (9); cura além do Healing Word."}, F)


# ---------- Forge: "Forged in the Heat of Battle" ----------
F = {}
for L in FATIAS:
    s_ = 3 if L < 5 else 4; w = 3; p = prof(L); cd = 8 + p + w; atk = p + w; ab = p + s_ + 1
    ds = "+1d8" if L >= 9 else ""
    cant = lambda n, L=L, ab=ab, s_=s_, ds=ds: {"ataques": [{"n": n, "bonus": ab, "dano": f"1d6+{s_ + 1}{bb(L)}{ds}", "nota": "maça +1 (Blessing of the Forge) + Booming Blade" + (" + Divine Strike" if L >= 9 else "")}]}
    ca = 18 if L < 7 else 21      # cota de malha + escudo; placas no 7 + Soul of the Forge (+1, nível 6)
    f = fatia(L, mods_(s_, -1, 3, -1, w, -1), ('sab', 'car'), ca, hpcalc([8] * L, 3), cant, cd, atk, w,
              'frontliner', True, (L + 1) // 2, canal=1 if L < 6 else 2, ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []),
              livres=[wor(L, cd)])
    f['_texto'] = f"Cleric {L}; For {17 if L < 5 else 18}" + (" (Crusher)" if L >= 5 else "") + f"; CA {ca}" + (" (placas + Soul of the Forge)" if L >= 7 else "") + "."
    F[L] = f
emit('rpgbot-cleric-forge', 'forge', 'Forge Domain Cleric (RPGBot: Forged in the Heat of Battle)',
     "Cleric (Forge), Meio-elfo (High, Custom Origin) com Booming Blade; maça +1 (Blessing of the Forge), armadura pesada + escudo; Crusher 4, War Caster 8, For 20 (12)",
     {"resumo": "Clérigo da forja defensor: maça +1 com Booming Blade, armadura pesada com Soul of the Forge, Spirit Guardians para segurar os inimigos perto.",
      "estrategia": "Corpo a corpo com Booming Blade; Spirit Guardians e Spiritual Weapon; Hold Person e Banishment quando precisa.",
      "nao_modelado": "Dano secundário do Booming Blade; empurrão do Crusher; War Caster (Booming Blade no ataque de oportunidade); resistência a fogo; Searing Smite, Heat Metal, Elemental Weapon, Wall of Fire, Animate Objects; Blessing of the Forge num aliado; cura além do Healing Word."}, F)


# ---------- Knowledge: "Oh nowo" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4 if L < 9 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    pot = f"+{w}" if L >= 9 else ""
    cant = lambda n, L=L, cd=cd, pot=pot: toll(L, cd, n, pot)
    f = fatia(L, mods_(-1, 2, 1, 2, w, -1), ('sab', 'car'), 18 if L < 5 else 19, hpcalc([8] * L, 1), cant, cd, atk, w,
              'conjurador', False, (L + 1) // 2, canal=1 if L < 6 else 2, ctrl=[CMD(cd), HP(cd)] + ([BAN(cd)] if L >= 7 else []))
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}" + ("; Potent Spellcasting" if L >= 9 else "") + "."
    F[L] = f
emit('rpgbot-cleric-knowledge', 'knowledge', 'Knowledge Domain Cleric (RPGBot: Oh nowo)',
     "Cleric (Knowledge), Tabaxi; armadura média + escudo; Telekinetic 4, Sab 20 (8)",
     {"resumo": "Clérigo do conhecimento tabaxi: perícias com Expertise e magias de divinação; na luta, um clérigo de truques, Spirit Guardians e Command.",
      "estrategia": "Toll the Dead e Sacred Flame; Spirit Guardians (Feline Agility para entrar); Command, Hold Person e Banishment.",
      "nao_modelado": "Command em mais alvos (upcast); Expertise e Knowledge of the Ages; Read Thoughts + Suggestion; Confusion; Telekinetic; divinações; Summon Celestial (9); cura além do Healing Word."}, F)


# ---------- Order: Cleric 1 / Sorcerer 1 ----------
F = {}
for L in FATIAS:
    cl = L - 1; w = 3 if L < 5 else 4 if L < 9 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    bs = "+1d8" if cl >= 8 else ""
    cant = lambda n, L=L, cd=cd, bs=bs: toll(L, cd, n, bs)
    voz = lambda usos: {"nome": f"Voice of Authority ({usos} ataque{'s' if usos > 1 else ''} de aliado por reação)", "lado": "of", "modelo": "ataque_extra", "alvos": round(usos / 4, 2)}
    extras = [dict(id="bless", hipotese="Bless + Voice of Authority (1 ataque de aliado)", dano=cant(0.75), suporte={"fontes": [BLESS, voz(1)]}, gasta={"espacos": {"1": 1}}),
              dict(id="voz", hipotese="Healing Word num aliado como ação bônus em 2 rounds (Voice of Authority) + truques",
                   dano=cant(1.0), suporte={"fontes": [voz(2)]}, gasta={"espacos": {"1": 2}})]
    f = fatia(L, mods_(-1, -1, 3, 0, w, 2), ('sab', 'car'), 18 if L < 7 else 20, hpcalc([8] * cl + [6], 3), cant, cd, atk, w,
              'conjurador', False, (cl + 1) // 2, canal=1 if cl < 6 else 2, ctrl=[CMD(cd), HP(cd)] + ([BAN(cd)] if cl >= 7 else []),
              extras=extras)
    f['linhas'] = [l for l in f['linhas'] if not (l['id'] in ('bless', 'bless+arma')                       # troca o Bless genérico pelo com Voice
                                                     and not any(x['nome'].startswith('Voice') for x in l['suporte']['fontes']))]
    f['_texto'] = f"Cleric {cl} / Sorcerer 1 (Divine Soul, personagem 2); Sab {10 + 2 * w}" + ("; placas" if L >= 7 else "; cota de malha") + " + escudo" + ("; Blessed Strikes" if cl >= 8 else "") + "."
    F[L] = f
emit('rpgbot-cleric-order', 'order', 'Order Domain Cleric (RPGBot: I heard a rumor this was originally UA content)',
     "Cleric (Order) / Sorcerer 1 (Divine Soul: Bless, Silvery Barbs), Shifter; armadura pesada + escudo; Fey Touched (personagem 5), Sab 20 (9)",
     {"resumo": "Clérigo da ordem de suporte: cada magia de nível num aliado (Healing Word, Bless) dá a ele um ataque por reação (Voice of Authority).",
      "estrategia": "Bless ou Healing Word para disparar ataques dos aliados, truques na ação; Command, Hold Person e Banishment; Spirit Guardians quando vale.",
      "nao_modelado": "Command em mais alvos (upcast); Silvery Barbs (vantagem + Voice of Authority); Embodiment of Law (encantamento como ação bônus); Order's Demand; Slow; Heroism e Shield of Faith; Favored by the Gods; Inspiring Leader (13)."}, F)


# ---------- Tempest: "Shattering Expectations" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4; p = prof(L); cd = 8 + p + w; atk = p + w
    cant = lambda n, L=L, atk=atk: {"ataques": [{"n": n, "bonus": atk, "dano": f"{k(L)}d8", "nota": "Shocking Grasp (Air Genasi, Sab)"}]}
    wots = {"com_save": [{"n": round(w / 16, 3), "cd": cd, "save": "Des", "dano": "2d8", "meio": True, "nota": "Wrath of the Storm (reação, Sab/dia ÷ 4 lutas ÷ 4 rounds)"}]}
    esp = espacos(L); s = maior(esp)
    shat = area_sp("Shatter", 2, "3d8", cd, 2)
    areas = [shat] + ([area_sp("Destructive Wave", 6, "10d10", cd, 5, sel=True)] if L >= 9 else [])
    if L >= 9:
        ira_a = {"nome": "Destructive Wave + Destructive Wrath (5º)", "tipo": "explosao", "usos": [{"alvos": 6, "seletiva": True, "dano": "50+5d10", "cd": cd, "metade": True}]}; ira_s = 5
    else:
        ira_a = {"nome": f"Shatter + Destructive Wrath ({s}º)", "tipo": "explosao", "usos": [{"alvos": 2, "dano": str(8 * (s + 1)), "cd": cd, "metade": True}]}; ira_s = s
    extras = [dict(id="ira", hipotese="Destructive Wrath (Channel Divinity) maximizando a área do trovão no maior espaço",
                   dano=cant(0.75), area=[ira_a, wor(L, cd)], gasta={"canal": 1, "espacos": {str(ira_s): 1}})]
    f = fatia(L, mods_(2, -1, 3, -1, w, -1), ('sab', 'car'), 18 if L < 7 else 20, hpcalc([8] * L, 3), cant, cd, atk, w,
              'frontliner', True, (L + 1) // 2, canal=1 if L < 6 else 2, esp=esp, ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []),
              areas=areas, livres=[wor(L, cd)], extra_dano=wots, extras=extras)
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}, Con {16 if L < 5 else 17}" + ("; placas" if L >= 7 else "; cota de malha") + " + escudo."
    F[L] = f
emit('rpgbot-cleric-tempest', 'tempest', 'Tempest Domain Cleric (RPGBot: Shattering Expectations)',
     "Cleric (Tempest), Air Genasi (Shocking Grasp por Sab); armadura pesada + escudo; ASI Con/Sab 4, War Caster 8, Sab 20 (12)",
     {"resumo": "Clérigo da tempestade de linha de frente: Shocking Grasp e Wrath of the Storm, e Shatter (Destructive Wave no 9) maximizado com Destructive Wrath.",
      "estrategia": "Spirit Guardians para lutas próximas; Shatter maximizado no maior espaço para grupos; Shocking Grasp no corpo a corpo.",
      "nao_modelado": "Thunderbolt Strike (empurrão e derrubar); vantagem do Shocking Grasp contra armadura de metal e negação de reação; War Caster; Thunderwave, Call Lightning, Sleet Storm, Ice Storm, Insect Plague; Stormborn; cura além do Healing Word."}, F)


# ---------- Trickery: Rogue 1 / Cleric (Half-elf) ----------
F = {}
for L in FATIAS:
    rl = 1 if L < 11 else 3; cl = L - rl; cast = cl + (1 if rl >= 3 else 0)
    w = 3 if cl < 4 else 4; dx = 3 if cl < 8 else 4; p = prof(L); cd = 8 + p + w; atk = p + w; ab = p + dx
    bs = "+1d8" if cl >= 8 else ""
    cant = lambda n, L=L, cd=cd, bs=bs: sacred(L, cd, n, bs)
    sa = f"{(rl + 1) // 2}d6"
    golpe = f"1d8+{dx}" + (bb(L) if rl >= 3 else "") + bs
    dup = dict(id="duplicidade", hipotese="Invoke Duplicity (Channel Divinity, concentração): rapieira com vantagem e Sneak Attack",
               dano={"ataques": [{"n": 1.0, "bonus": ab, "dano": golpe, "vantagem": 1.0, "nota": "rapieira" + (" + Booming Blade" if rl >= 3 else "") + (" + Blessed Strikes" if cl >= 8 else "")}],
                     "por_turno": [{"dano": sa, "nota": "Sneak Attack"}]},
               controle={"atencao": AT(True, 'striker'), "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}, gasta={"canal": 1})
    ctrl = [HP(cd)] + ([POLY(cd)] if cl >= 7 else [])
    f = fatia(L, mods_(-1, dx, 2, -1, w, 1), ('des', 'int'), 18, hpcalc([8] * L, 2), cant, cd, atk, w,
              'conjurador', False, (cl + 1) // 2, canal=1 if cl < 6 else 2, esp=espacos(cast), ctrl=ctrl, extras=[dup])
    f['_texto'] = f"Rogue {rl} / Cleric {cl}; Sab {10 + 2 * w}, Des {10 + 2 * dx}; peitoral + escudo" + ("; Arcane Trickster (Booming Blade)" if rl >= 3 else "") + "."
    F[L] = f
emit('rpgbot-cleric-trickery', 'trickery', 'Trickery Domain Cleric (RPGBot: Half-Elf Trickery Cleric / Rogue)',
     "Rogue 1 / Cleric (Trickery) / Rogue 3 (Arcane Trickster, personagem 10–11), Meio-elfo; peitoral + escudo; Sab 18 (Cleric 4), Des 18 (Cleric 8)",
     {"resumo": "Clérigo trapaceiro com dip de Rogue: perícias e furtividade; na luta, Sacred Flame ou rapieira com vantagem do Invoke Duplicity para o Sneak Attack.",
      "estrategia": "Invoke Duplicity nas lutas corpo a corpo (vantagem e Sneak Attack); fora disso, Sacred Flame, Spirit Guardians e Spiritual Weapon; Polymorph no 9.",
      "nao_modelado": "Pass Without Trace, Blessing of the Trickster e perícias; Mirror Image e Blink; Cloak of Shadows; magias lançadas da ilusão (Word of Radiance); Cunning Action; Silvery Barbs e magias do Arcane Trickster; cura além do Healing Word."}, F)


# ---------- Twilight: "I protect my friends with magic" (Centaur) ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4 if L < 9 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    bs = "+1d8" if L >= 9 else ""
    cant = lambda n, L=L, cd=cd, bs=bs: toll(L, cd, n, bs)
    santo = {"nome": "Twilight Sanctuary (PV temporários todo round)", "lado": "def", "modelo": "pv_temporario", "usos_luta": 4, "alvos": 3, "pv": 3.5 + L}
    esp = espacos(L); s = maior(esp)
    extras = [dict(id="santuario", hipotese="Twilight Sanctuary (Channel Divinity, ação, 1 minuto) + truques", dano=cant(0.75),
                   suporte={"fontes": [santo]}, gasta={"canal": 1})]
    if L >= 5:
        extras.append(dict(id="santuario-guardioes", hipotese="Twilight Sanctuary (round 1) + Spirit Guardians (round 2) + truques",
                           dano=merge(cant(0.5), sg_dano(cd, s, 0.5)), suporte={"fontes": [santo]}, area=[sg_area(cd, s)],
                           gasta={"canal": 1, "espacos": {str(s): 1}}))
    f = fatia(L, mods_(2, -1, 3, -1, w, -1), ('sab', 'car'), 18 if L < 7 else 20, hpcalc([8] * L, 3), cant, cd, atk, w,
              'frontliner', True, (L + 1) // 2, canal=1 if L < 6 else 2, esp=esp, ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []),
              extras=extras)
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}" + ("; placas" if L >= 7 else "; cota de malha") + " + escudo" + ("; Blessed Strikes" if L >= 9 else "") + "."
    F[L] = f
emit('rpgbot-cleric-twilight', 'twilight', 'Twilight Domain Cleric (RPGBot: I protect my friends with magic)',
     "Cleric (Twilight), Centauro; armadura pesada + escudo; Telekinetic 4, Sab 20 (8); um aliado corpo a corpo montado",
     {"resumo": "Clérigo do crepúsculo de linha de frente: Twilight Sanctuary dá PV temporários à party todo round, sem concentração, junto com Spirit Guardians.",
      "estrategia": "Santuário no início das lutas difíceis, Spirit Guardians no round seguinte, truques; Bless e Spiritual Weapon nas outras.",
      "nao_modelado": "Vigilant Blessing (vantagem na iniciativa); Steps of Night (voo); Eyes of Night; Charge do Centauro e o aliado montado; remoção de medo/encantamento do santuário; Faerie Fire, Moonbeam, Greater Invisibility, Circle of Power; Telekinetic; cura além do Healing Word."}, F)


# ---------- War: "Die Kriegerin der Zerstörung" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 9 else 4; con = 3 if L < 5 else 4; p = prof(L); cd = 8 + p + w; atk = p + w
    bs = "+1d8" if L >= 9 else ""
    if L < 5:
        cant = lambda n, L=L, p=p: {"ataques": [{"n": n, "bonus": p + 2, "dano": "1d8+2", "nota": "martelo de guerra"},
                                                {"n": round(n * 3 / 16, 3), "bonus": p + 2, "dano": "1d8+2", "nota": "War Priest (Sab/dia ÷ 4 lutas ÷ 4 rounds)"}]}
    else:
        cant = lambda n, L=L, cd=cd, bs=bs: toll(L, cd, n, bs)
    hdp = {str(math.ceil(p / 2)): 1}                                       # Harness Divine Power (opcional que o guia usa)
    esp = espacos(L, extra=hdp)
    q = 0 if L < 5 else 4 if L < 9 else 6
    if q:
        up = "3" if L < 9 else "4"; esp[up] -= 1                            # Animate Dead: 1 espaço/dia para manter a tropa
    esq = [{"nome": "esqueletos (Animate Dead)", "quantidade": q, "pv": 13, "ca": 13, "ataque": {"bonus": 4, "dano": "1d6+2"}, "nota": "arco curto"}] if q else []
    wgb = [{"nome": "War God's Blessing (+10 num ataque de aliado, reação)", "lado": "of", "modelo": "bonus_por_uso", "bonus": 10, "usos_descanso_curto": 2}] if L >= 6 else []
    extras = []
    if L >= 5:
        manto = {"nome": "Crusader's Mantle (aliados)", "lado": "of", "modelo": "dano_por_acerto", "alvos": 3, "dano_extra": 2.5, "concentracao": "crusaders_mantle"}
        esq_m = [dict(e, ataque=dict(e['ataque'], dano=e['ataque']['dano'] + "+1d4")) for e in esq]
        extras.append(dict(id="manto", hipotese="Crusader's Mantle (aliados e esqueletos) + truques", dano=cant(0.75),
                           suporte={"fontes": wgb + [manto]}, invocacoes=esq_m, gasta={"espacos": {"3": 1}}))
    f = fatia(L, mods_(2, -1, con, -1, w, -1), ('sab', 'car') + (('con',) if L >= 5 else ()), 18 if L < 7 else 20,
              hpcalc([8] * L, con), cant, cd, atk, w, 'frontliner', True, (L + 1) // 2, canal=1 if L < 6 else 2, esp=esp,
              ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []) + ([U("Hold Monster", "hold_monster", cd, 5)] if L >= 9 else []),
              livres=[wor(L, cd, bs)], sup=wgb, extras=extras)
    for l in f['linhas']:
        if esq and l['id'] != 'manto': l['invocacoes'] = esq
    f['_texto'] = (f"Cleric {L}; Sab {10 + 2 * w}, Con {10 + 2 * con}" + (" (Resilient)" if L >= 5 else "") + ("; placas" if L >= 7 else "; cota de malha") + " + escudo"
                   + (f"; {q} esqueletos (1 espaço de {up}º por dia)" if q else "") + "; Harness Divine Power.")
    F[L] = f
emit('rpgbot-cleric-war', 'war', 'War Domain Cleric (RPGBot: Die Kriegerin der Zerstörung)',
     "Cleric (War), Dragonborn Cromático (verde); armadura pesada + escudo; Resilient Con 4, Sab 18 (8), Sab 20 (12); esqueletos de Animate Dead a partir do 5",
     {"resumo": "Clérigo da guerra que larga a arma no 5 e vira oficial: tropa de esqueletos, Crusader's Mantle e War God's Blessing para os aliados.",
      "estrategia": "Martelo e War Priest até o 4; depois Toll the Dead, esqueletos atirando, Crusader's Mantle quando há muitos atacantes, Spirit Guardians quando não.",
      "nao_modelado": "Guided Strike (+10 no próprio acerto); sopro do Dragonborn; Divine Favor, Shield of Faith, Magic Weapon; Death Ward, Stoneskin, Freedom of Movement; Contagion; Avatar of Battle (17); cura além do Healing Word."}, F)
