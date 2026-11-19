"""Cleric (passada 1 cega, 19/11): Death, Grave, Life, Light, Nature + Peace sobre um clérigo base.
Convenções em calibracao/convencoes-passada1.md, seção "Clérigos". Rodar da raiz do repo; depois `python -m dh expandir`."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
import wiz
from wiz import SL, prof, k, merge, U, area_sp, area_pico, AT, hpcalc, M, escrever, controle_fonte

URL = {'death': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/death/',
       'grave': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/grave/',
       'life': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/life-domain/',
       'light': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/light-domain/',
       'nature': 'https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/nature/',
       'peace': 'https://rpgbot.net/ban-5es-peace-domain/'}
NOTA = "Build exemplo do guia de subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."
wiz.FONTE = lambda slug: {"tipo": "rpgbot", "url": URL[slug],
                          "nota": NOTA if slug != 'peace' else "Sem build no RPGBot (o guia recomenda banir o domínio): "
                          "clérigo base comum + recursos do Peace Domain. Passada 1 cega."}
FATIAS = (3, 5, 7, 9, 11)


# ---------- peças ----------
def toll(L, cd, n, extra=''): return {"com_save": [{"n": n, "cd": cd, "save": "Sab", "dano": f"{k(L)}d12{extra}", "meio": False, "nota": "Toll the Dead (alvo ferido)"}]}
def sacred(L, cd, n, extra=''): return {"com_save": [{"n": n, "cd": cd, "save": "Des", "dano": f"{k(L)}d8{extra}", "meio": False, "nota": "Sacred Flame"}]}
def wor(L, cd, extra=''):
    """Word of Radiance: todos a 5 pés (convenção do Thunderclap), ação livre na horda."""
    return {"nome": "Word of Radiance", "tipo": "cleave_save", "dano": f"{k(L)}d6{extra}", "cd": cd, "save": "Con", "alvos": [1, 2, 3]}
def sw(atk, wis, n, slot=2): return {"ataques": [{"n": n, "bonus": atk, "dano": f"{1 + (slot - 2) // 2}d8+{wis}", "nota": f"Spiritual Weapon ({slot}º)"}]}
def sg_dano(cd, s, n): return {"com_save": [{"n": n, "cd": cd, "save": "Sab", "dano": f"{s}d8", "meio": True, "nota": f"Spirit Guardians ({s}º) no alvo"}]}
def sg_area(cd, s): return {"nome": f"Spirit Guardians ({s}º)", "tipo": "aura", "alvos": 3, "dano": f"{s}d8", "cd": cd, "metade": True}
BLESS = {"nome": "Bless", "lado": "of", "modelo": "bonus_continuo", "alvos": 3, "bonus": 2.5, "concentracao": "bless"}
HP = lambda cd: U("Hold Person", "hold_person", cd, 2)
BAN = lambda cd: U("Banishment", "banishment", cd, 4)
BLD = lambda cd: U("Blindness/Deafness", "blindness", cd, 2)


def espacos(L, fora=0, extra=None):
    e = dict(SL[L])
    if fora: e["1"] -= fora                         # Goodberry no fim do dia: espaço de 1º fora do pool (como o Mage Armor)
    for s, q in (extra or {}).items(): e[s] = e.get(s, 0) + q
    return e


def maior(esp): return max(int(s) for s, q in esp.items() if q > 0)


def fatia(L, mods, profs, ca, pv, cant, cd, atk, wis, papel, front, nivel_magia, canal=0, esp=None,
          ctrl=(), areas=(), livres=(), extra_dano=None, sup=(), sw_ok=True, sg_ok=True, extras=(), outros=None):
    """nivel_magia = maior círculo de magia de clérigo conhecido (multiclasse: pelo nível de clérigo)."""
    p = prof(L); sv = {kk: mods[kk] + (p if kk in profs else 0) for kk in mods}
    corpo = dict(ca=ca, pv=pv, saves=dict(sv=sv, conjurador=True))
    esp = esp or espacos(L); top = maior(esp)
    rec = {"espacos": esp, "outros": dict(outros or {})}
    if canal: rec["outros"]["canal"] = {"qtd": canal, "volta": "curto"}
    ed = extra_dano or {}
    def D(*ds): return merge(*ds, ed) if ed else merge(*ds)
    def S(*fs): return {"fontes": list(sup) + list(fs)}
    base_ctl = {"atencao": AT(front, papel), "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}
    L_ = []
    def ln(id_, dn, **kw):
        l = {"id": id_, "dano": dn}; l.update(kw)
        if id_ != 'principal': l.setdefault('herda', 'principal')
        L_.append(l)
    ln("principal", D(cant(1.0)), controle=base_ctl, defesa={}, saves={}, area=list(livres), invocacoes=[], suporte=S())
    ln("bless", D(cant(0.75)), suporte=S(BLESS), gasta={"espacos": {"1": 1}})
    if sw_ok and nivel_magia >= 2:
        ln("arma-espiritual", D(cant(1.0), sw(atk, wis, 1.0)), gasta={"espacos": {"2": 1}})
    if sg_ok and nivel_magia >= 3:
        s = top
        ln("guardioes", D(cant(0.75), sg_dano(cd, s, 0.75)), area=[sg_area(cd, s)] + list(livres), gasta={"espacos": {str(s): 1}})
        if sw_ok:
            g = {str(s): 1}; g["2"] = g.get("2", 0) + 1
            ln("guardioes-arma", D(cant(0.75), sg_dano(cd, s, 0.75), sw(atk, wis, 0.75)), area=[sg_area(cd, s)] + list(livres),
               gasta={"espacos": g})
    if ctrl:
        t = max(o['slot'] for o in ctrl)
        ln("controle", D(cant(0.75)), controle={"atencao": AT(front, papel), "fontes": [controle_fonte(list(ctrl))]},
           gasta={"espacos": {str(t): 1}})
    if areas:
        ap, sp = area_pico(list(areas), esp)
        g = {}
        for x in sp: g[str(x)] = g.get(str(x), 0) + 1
        ln("area", D(cant(0.5 if len(ap) > 1 else 0.75)), area=ap + list(livres), gasta={"espacos": g})
    for x in extras:
        x = dict(x); x.setdefault('herda', 'principal'); L_.append(x)
    return dict(corpo=corpo, recursos=rec, linhas=L_)


def emit(id_, slug, nome, build, desc, F):
    for L in FATIAS:
        for l in F[L]['linhas']:
            if l['id'] != 'principal': l.setdefault('hipotese', l['id'])
    escrever(id_, slug, nome, build, desc, F)


def mods_(f, d, c, i, w, ch): return M(f, d, c, i, w, ch)


# ---------- Death: "Stabby, Murdery Death" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4 if L < 9 else 5; p = prof(L); cd = 8 + p + w; atk = p + w; ab = p + 3
    bb = "1d8+3" + ("" if L < 5 else "+1d8" if L < 11 else "+2d8") + ("+1d8" if L >= 9 else "")
    cant = lambda n, L=L, ab=ab, bb=bb: {"ataques": [{"n": n, "bonus": ab, "dano": bb, "nota": "Booming Blade (rapieira)" + (" + Divine Strike" if L >= 9 else "")}]}
    tod = {"por_luta": [{"usos": 0.5 if L < 6 else 1.0, "dano": str(5 + 2 * L), "nota": "Touch of Death (Channel Divinity ÷ 2 lutas)"}]}
    reaper = {"nome": "Reaper (Toll the Dead em 2 alvos)", "tipo": "cleave_save", "dano": f"{k(L)}d12", "cd": cd, "save": "Sab", "alvos": [1, 2, 2]}
    ctrl = [HP(cd), BLD(cd)] + ([BAN(cd)] if L >= 7 else [])
    f = fatia(L, mods_(-1, 3, 3, -1, w, -1), ('sab', 'car'), 18 if L < 5 else 19, hpcalc([8] * L, 3), cant, cd, atk, w,
              'frontliner', True, (L + 1) // 2, canal=1 if L < 6 else 2, ctrl=ctrl, livres=[reaper, wor(L, cd)], extra_dano=tod)
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}; " + ("escama + escudo" if L < 5 else "meia-armadura + escudo") + "."
    F[L] = f
emit('rpgbot-cleric-death', 'death', 'Death Domain Cleric (RPGBot: Stabby, Murdery Death)',
     "Cleric (Death), Meio-elfo (High Elf, Custom Origin) com Booming Blade; rapieira + escudo, armadura média; Telekinetic 4 (Sab 18), Sab 20 (8)",
     {"resumo": "Clérigo da morte de corpo a corpo: Booming Blade de rapieira com Touch of Death e Divine Strike, Reaper para acertar dois alvos com Toll the Dead.",
      "estrategia": "Corpo a corpo com Booming Blade; Spirit Guardians para grupos e Spiritual Weapon como ação bônus; Hold Person, Blindness e Banishment quando precisa tirar alguém da luta.",
      "nao_modelado": "Dano secundário do Booming Blade; empurrão do Telekinetic para juntar alvos do Reaper; Inflict Wounds e Vampiric Touch com Touch of Death; Animate Dead; Inescapable Destruction; False Life; cura (Healing Word)."}, F)


# ---------- Grave: "One Punch" ----------
F = {}
for L in FATIAS:
    cl = L if L < 7 else L - 1 if L < 9 else L - 2
    w = 3 if L < 5 else 4 if L < 11 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    dados = [8] * cl + [6] * (L - cl)
    cant = lambda n, L=L, cd=cd, w=w: toll(L, cd, n, f"+{w}" if L >= 11 else "")
    esp = espacos(L); s = maior(esp)
    def soco(n, s, atk=atk): return {"ataques": [{"n": n, "bonus": atk, "dano": f"{2 * (s + 2)}d10", "nota": f"Inflict Wounds ({s}º) no alvo vulnerável (Path to the Grave: dados dobrados)"}]}
    extras = [
        dict(id="punho", hipotese="Path to the Grave (ação) e Inflict Wounds no maior espaço no round seguinte",
             dano=merge(cant(0.5), soco(0.25, s)), gasta={"canal": 1, "espacos": {str(s): 1}}),
        dict(id="punho-rapido", hipotese="Path to the Grave + Inflict Wounds acelerado (Quicken Spell) no mesmo round",
             dano=merge(cant(0.75), soco(0.25, s)), gasta={"canal": 1, "metamagia": 1, "espacos": {str(s): 1}}),
    ]
    quick = 1 if L < 9 else 2
    f = fatia(L, mods_(-1, 2, 1, -1, w, 1), ('sab', 'car'), 18 if L < 5 else 19, hpcalc(dados, 1), cant, cd, atk, w,
              'frontliner', True, (cl + 1) // 2, canal=1 if cl < 6 else 2, esp=esp,
              ctrl=[HP(cd)] + ([BAN(cd)] if cl >= 7 else []), extras=extras,
              outros={"metamagia": {"qtd": quick, "volta": "longo"}})
    f['_texto'] = (f"Cleric {cl}" + (f" / Sorcerer {L - cl}" if L > cl else "") + f"; Sab {10 + 2 * w}; Quicken {quick}/dia (Metamagic Adept"
                   + (" + pontos do Sorcerer" if L >= 9 else "") + ").")
    F[L] = f
emit('rpgbot-cleric-grave', 'grave', 'Grave Domain Cleric (RPGBot: One Punch)',
     "Cleric (Grave) / Sorcerer 2 (Divine Soul, personagem 7–8), Custom Lineage (Metamagic Adept: Quicken, Extend); Fey Touched 4; escama → meia-armadura + escudo; Sab 20 (personagem 10)",
     {"resumo": "Clérigo da tumba que torna um alvo vulnerável (Path to the Grave) e o atinge com Inflict Wounds no maior espaço, acelerado com Quicken.",
      "estrategia": "Um 'soco' por luta no alvo mais perigoso; Toll the Dead no resto; Spirit Guardians e Spiritual Weapon como clérigo comum quando o Channel acabou.",
      "nao_modelado": "Hex e True Strike na preparação; Favored by the Gods; conversão de espaços em pontos de feitiçaria (o guia queima espaços para mais Quicken); Absorb Elements no soco; Silvery Barbs; Circle of Mortality e cura; Sentinel at Death's Door; Path to the Grave dado a um aliado."}, F)


# ---------- Life: "Lifeberry the Tank Engine" ----------
F = {}
for L in FATIAS:
    cl = 2 if L == 3 else L - 1 if L < 7 else L - 2
    w = 3 if L < 11 else 4; con = 3 if L < 5 else 4; p = prof(L); cd = 8 + p + w; atk = p + w
    bs = "+1d8" if cl >= 8 else ""
    cant = lambda n, L=L, cd=cd, bs=bs: toll(L, cd, n, bs)
    gb = {"nome": "Goodberry + Disciple of Life (fim do dia)", "lado": "def", "modelo": "cura", "usos_dia": 1, "pv": 40, "quando": "entre_lutas"}
    canal = 1 if cl < 6 else 2
    extras = [dict(id="preservar", hipotese="Preserve Life na luta (Channel Divinity, ação) + truques",
                   dano=cant(0.75), suporte={"fontes": [gb, {"nome": "Preserve Life", "lado": "def", "modelo": "cura", "usos_luta": 1, "pv": 5 * cl}]},
                   gasta={"canal": 1})]
    nm = (cl + 1) // 2
    f = fatia(L, mods_(2, 0, con, -1, w, -1), ('sab', 'car') + (('con',) if L >= 5 else ()), 18 if L < 7 else 20,
              hpcalc([8] * L, con), cant, cd, atk, w, 'frontliner', True, nm, canal=canal, esp=espacos(L, fora=1),
              ctrl=[HP(cd)] + ([BAN(cd)] if cl >= 7 else []), livres=[wor(L, cd)], sup=[gb], extras=extras)
    f['_texto'] = f"Cleric {cl} / Druid {L - cl} (Stars); Con {10 + 2 * con}" + (" (Resilient)" if L >= 5 else "") + ("; placas" if L >= 7 else "; cota de malha + escudo") + "."
    F[L] = f
emit('rpgbot-cleric-life', 'life', 'Life Domain Cleric (RPGBot: Lifeberry the Tank Engine)',
     "Cleric (Life) / Druid 2 (Stars: personagem 2 e 6), Anão da Montanha (Custom Origin); armadura pesada + escudo; Resilient Con (personagem 5), Skill Expert 10",
     {"resumo": "Clérigo da vida de armadura pesada que tanqueia com Spirit Guardians e Spiritual Weapon, cura em massa com Goodberry potencializado pelo Disciple of Life e Preserve Life.",
      "estrategia": "Round 1 Spirit Guardians (no 4º círculo no nível 7), round 2 Spiritual Weapon, depois truques ou Esquivar; Bless nas lutas sem área; cura fora de combate.",
      "nao_modelado": "Starry Form (piso de concentração do Dragão; Archer; Chalice); Healing Word e Disciple of Life na luta; Blessed Healer; Absorb Elements e Faerie Fire do Druid; Beacon of Hope; Death Ward; Heroes' Feast."}, F)


# ---------- Light: "Variant Human Light Domain Cleric" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4 if L < 9 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    pot = f"+{w}" if L >= 9 else ""
    cant = lambda n, L=L, cd=cd, pot=pot: sacred(L, cd, n, pot)
    canal = 1 if L < 6 else 2
    areas = [area_sp("Burning Hands", 2, "3d6", cd, 1)] + ([area_sp("Fireball", 4, "8d6", cd, 3)] if L >= 5 else [])
    rod = {"nome": "Radiance of the Dawn", "tipo": "explosao", "usos": [{"alvos": 6, "seletiva": True, "dano": f"2d10+{L}", "cd": cd, "metade": True}]}
    fs = lambda n, s=2, cd=cd: {"com_save": [{"n": n, "cd": cd, "save": "Des", "dano": f"{s}d6", "meio": True, "nota": "Flaming Sphere (ação bônus)"}]}
    extras = [dict(id="amanhecer", hipotese="Radiance of the Dawn (Channel Divinity) + truques", dano=cant(0.75),
                   area=[rod, wor(L, cd, pot)], gasta={"canal": 1}),
              dict(id="esfera", hipotese="Flaming Sphere (no lugar da Spiritual Weapon: o guia só usa fogo e radiante)",
                   dano=merge(cant(0.75), fs(0.75)), gasta={"espacos": {"2": 1}})]
    f = fatia(L, mods_(-1, 2, 2, 1, w, 0), ('sab', 'car'), 18 if L < 5 else 19, hpcalc([8] * L, 2), cant, cd, atk, w,
              'conjurador', False, (L + 1) // 2, canal=canal, ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []), areas=areas,
              livres=[wor(L, cd, pot)], sw_ok=False, extras=extras)
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}" + ("; Potent Spellcasting" if L >= 9 else "") + "."
    F[L] = f
emit('rpgbot-cleric-light', 'light', 'Light Domain Cleric (RPGBot: Variant Human Light Domain Cleric)',
     "Cleric (Light), Humano Variante (Lucky), só dano de fogo e radiante; escama → meia-armadura + escudo; Sab 18 (4), Sab 20 (8)",
     {"resumo": "Clérigo blaster de fogo e radiante: Sacred Flame e Word of Radiance, Burning Hands, Fireball, Radiance of the Dawn e Spirit Guardians.",
      "estrategia": "Conjurador a distância com armadura média; área no 1º round das lutas com grupos, Spirit Guardians quando entra no meio, Flaming Sphere no lugar da Spiritual Weapon.",
      "nao_modelado": "Warding Flare e Improved Flare (desvantagem num ataque por reação); Wall of Fire; Scorching Ray; Faerie Fire; Lucky; dano de fogo da esfera em quem termina o turno ao lado; cura (Healing Word)."}, F)


# ---------- Nature: "Snake Charmer" ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4; p = prof(L); cd = 8 + p + w; atk = p + w
    bs = "+1d8" if L >= 9 else ""
    cant = lambda n, L=L, cd=cd, bs=bs: toll(L, cd, n, bs)
    hdp_nv = str(math.ceil(p / 2)); hdp_q = 1 if L < 6 else 2
    esp = espacos(L, extra={hdp_nv: hdp_q})                      # Harness Divine Power: Channel → espaço (opcional de classe)
    sup = [{"nome": "Inspiring Leader", "lado": "def", "modelo": "pv_temporario", "usos_descanso_curto": 1, "alvos": 3, "pv": L + 1, "quando": "entre_lutas"}] if L >= 9 else []
    extras = []
    if L >= 9:
        s = maior(esp)
        extras.append(dict(id="praga", hipotese=f"Insect Plague ({s}º) como aura parada a distância + truques",
                           dano=merge(cant(0.75), {"com_save": [{"n": 0.75, "cd": cd, "save": "Con", "dano": f"{4 + s - 5}d10", "meio": True, "nota": "Insect Plague no alvo"}]}),
                           area=[{"nome": f"Insect Plague ({s}º)", "tipo": "aura", "alvos": 4, "dano": f"{4 + s - 5}d10", "cd": cd, "metade": True}, wor(L, cd, bs)],
                           gasta={"espacos": {str(s): 1}}))
    f = fatia(L, mods_(-1, 2, 2, -1, w, 1), ('sab', 'car'), 18 if L < 5 else 19, hpcalc([8] * L, 2), cant, cd, atk, w,
              'conjurador', False, (L + 1) // 2, esp=esp, ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []), livres=[wor(L, cd, bs)],
              sup=sup, extras=extras)
    f['_texto'] = f"Cleric {L}; Sab {17 if L < 5 else 19}; Harness Divine Power {hdp_q}× espaço de {hdp_nv}º" + ("; Blessed Strikes; Inspiring Leader" if L >= 9 else "") + "."
    F[L] = f
emit('rpgbot-cleric-nature', 'nature', 'Nature Domain Cleric (RPGBot: Snake Charmer)',
     "Cleric (Nature), Yuan-ti (MMoM), armadura média + escudo, todas as opcionais de classe; Sab 19 (4), Inspiring Leader 8, Sab 20 (12)",
     {"resumo": "Clérigo da natureza yuan-ti que encanta cobras; na luta é um clérigo de truques e Spirit Guardians, com Channel Divinity convertido em espaços.",
      "estrategia": "Toll the Dead e Word of Radiance; Spirit Guardians e Spiritual Weapon; Insect Plague a partir do 9.",
      "nao_modelado": "Cobras e Animal Friendship; Charm Animals and Plants; Dampen Elements; Spike Growth e Plant Growth; Thorn Whip; resistência a magia e veneno do Yuan-ti; Suggestion racial; cura (Healing Word)."}, F)


# ---------- Peace: clérigo base + Peace Domain ----------
F = {}
for L in FATIAS:
    w = 3 if L < 5 else 4 if L < 9 else 5; p = prof(L); cd = 8 + p + w; atk = p + w
    pot = f"+{w}" if L >= 9 else ""
    cant = lambda n, L=L, cd=cd, pot=pot: toll(L, cd, n, pot)
    al = min(p, 3); frac = min(1.0, p / 4)          # vínculos por dia = PB, um por luta (10 min); aliados no vínculo = PB (até 3)
    bond = [{"nome": "Emboldening Bond (1d4 em 1 ataque por turno)", "lado": "of", "modelo": "bonus_por_uso", "bonus": 2.5,
             "usos_luta": round(4 * al * frac, 2), "nota": f"{al} aliados × 4 rounds × {frac:.2f} das lutas cobertas (PB {p}/dia)"},
            {"nome": "Emboldening Bond (1d4 nos saves)", "lado": "def", "modelo": "aura_saves", "bonus": round(2.5 * frac, 2)}]
    canal = 1 if L < 6 else 2
    extras = [dict(id="balsamo", hipotese="Balm of Peace (Channel Divinity, ação) + truques", dano=cant(0.75),
                   suporte={"fontes": bond + [{"nome": "Balm of Peace (2 aliados)", "lado": "def", "modelo": "cura", "usos_luta": 1, "pv": 2 * (7 + w)}]},
                   gasta={"canal": 1})]
    f = fatia(L, mods_(-1, 2, 2, -1, w, 0), ('sab', 'car'), 18 if L < 5 else 19, hpcalc([8] * L, 2), cant, cd, atk, w,
              'conjurador', False, (L + 1) // 2, canal=canal, ctrl=[HP(cd)] + ([BAN(cd)] if L >= 7 else []),
              livres=[wor(L, cd, pot)], sup=bond, extras=extras)
    f['_texto'] = f"Cleric {L}; Sab {10 + 2 * w}; vínculo em {al} aliados, {p}/dia" + ("; Potent Spellcasting" if L >= 9 else "") + "."
    F[L] = f
emit('rpgbot-cleric-peace', 'peace', 'Peace Domain Cleric (clérigo base; RPGBot recomenda banir)',
     "Cleric (Peace) sobre clérigo base: Humano Variante (War Caster), Des 14, Con 14, Sab 16; escama → meia-armadura + escudo; Sab 18 (4), Sab 20 (8)",
     {"resumo": "Clérigo da paz de retaguarda: Emboldening Bond (1d4 em ataques e saves, sem concentração, empilha com Bless) e Balm of Peace.",
      "estrategia": "Vínculo antes de cada luta; Bless junto do vínculo; Spirit Guardians, Spiritual Weapon e controle como clérigo comum.",
      "nao_modelado": "Protective Bond (teleporte e redistribuição de dano por reação; o principal argumento do RPGBot para banir); Expansive Bond; 1d4 em testes; empilhar com Bardic Inspiration/Guidance; Sanctuary, Aid, Warding Bond; cura (Healing Word)."}, F)
