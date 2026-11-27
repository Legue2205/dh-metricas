"""Chassi do Wizard (mini-mutirão de 22/11): uma build por tradição do gabarito (13), fatias 7 e 11, só sem feat.
Rodar da raiz: python ferramentas/geradores/chassi_wizard.py && python -m dh expandir

Mesma régua para todas as tradições:
  - Atributos Int > Con > Des (Bladesinging: Int > Des > Con); saves Int/Sab; d6; Mage Armor (1 espaço de 1º fora do pool)
    + Shield (1 por luta nas linhas que gastam espaço); Arcane Recovery (wiz.espacos).
  - Truque: Toll the Dead (alvo ferido, d12).
  - Lista base: controle Web, Hypnotic Pattern, Banishment (7) + Hold Monster, Wall of Force, Synaptic Static (11);
    controle-barato Web; área Fireball (7) + Cone of Cold (11); invocação Summon Aberration no maior espaço.
  - A tradição troca/acrescenta só o que favorece (magias da escola, features) e a posição.
Features das tradições: as do gerador antigo (wiz_builds.py), sem raça, feats e multiclasse.
"""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402
from wiz import (fatia as wfatia, toll, summon, area_sp, U, WEB, HYP, BAN, HM, WOF, SYN, PF, EBT, HP_, AT, SH, RE)  # noqa: E402,F401
import wiz as W  # noqa: E402

ORDEM = ('int', 'con', 'des', 'sab', 'car', 'for')
ORDEM_BS = ('int', 'des', 'con', 'sab', 'car', 'for')
URL = "https://rpgbot.net/dnd5/characters/classes/wizard/subclasses/{}/"
BASE_NM = ("Portent/Lucky/Silvery Barbs, iniciativa e Counterspell (igual para todos); Absorb Elements; "
           "Ritual Casting e utilidade; quebra de concentração.")
LPSY = lambda cd, usos=1, nome="Psychic Lance": dict(  # noqa: E731
    f={"tipo": "condicao_no_acerto", "nome": nome, "efeito": "psychic_lance", "cd": cd, "no_acerto": False, "usos": usos}, slot=4)


def base(L, ordem=ORDEM):
    s = C.atributos('wizard', L, ordem); m = C.mods(s); p = C.pb(L)
    i = m['int']; cd = 8 + p + i; a = p + i
    ctrl = [WEB(cd), HYP(cd), BAN(cd)] + ([U("Psychic Lance", "psychic_lance", cd, 4)] if L >= 7 else []) + \
        ([HM(cd), WOF(cd), SYN(cd)] if L >= 11 else [])   # M6b (23/11): Psychic Lance
    ctrl += ([W.SLOW(cd), W.FEAR(cd)] if L >= 5 else []) + ([W.CONF(cd)] if L >= 7 else []) + \
        ([W.WOS(cd), W.TK(cd)] if L >= 11 else [])        # 25/11: clássicos que faltavam
    areas = [area_sp("Fireball", 4, "8d6", cd, 3)] + ([area_sp("Cone of Cold", 6, "8d8", cd, 5)] if L >= 11 else [])
    top = 4 if L < 11 else 6
    return dict(s=s, m=m, p=p, i=i, cd=cd, a=a, ctrl=ctrl, barato=WEB(cd), areas=areas,
                inv=dict(i=summon('aberration', top, a), slot=top), top=top,
                cant=lambda n, L=L, cd=cd: toll(L, cd, n), ca=13 + m['des'], pv=C.hp(6, L, m['con']), profs=('int', 'sab'))


def monta(L, b, pos, ff=0, extra=(), **kw):
    f = wfatia(L, L, L, b['m'], b['profs'], b['ca'], b['pv'], b['cant'], b['ctrl'], b['barato'], b['areas'], b['inv'],
               extra=extra, ff=ff, **kw)
    at = C.atencao(pos)
    for l in f['linhas']:
        ctl = l.get('controle') or {}
        if ctl.get('atencao', {}).get('papel') == 'conjurador': ctl['atencao'] = dict(at)
        l.setdefault('hipotese', 'só truques (Toll the Dead)' if l['id'] == 'principal' else l['id'])
    f['corpo']['saves']['ataques'] = 1
    f['_texto'] = f"Wizard {L}; atributos {b['s']}; CD {b['cd']}, ataque +{b['a']}."
    if L >= 5: C.area_barata(f, b['areas'][0])   # M5 (23/11): Fireball no 3º como magia extra
    return f


def sai(sub, pos, F, build, resumo, nm, slug=None):
    C.escrever('wizard', sub, pos, F, build=build,
               desc={"resumo": resumo, "estrategia": "Régua comum do chassi do Wizard (ver gerador) + o que a tradição dá.",
                     "nao_modelado": nm + " " + BASE_NM},
               url=URL.format(slug or sub))


def PROJECTED_WARD(ward):
    """27/11 (pacote C), Abjuration 6: reação que põe o Arcane Ward entre o golpe e um aliado. Em todas as linhas: a parte
    suporte.padroes.ward_projetado_fracao do ward sai do PV do abjurador e vira PV poupado de um aliado (pv_temporario);
    gasta a reação em suporte.padroes.ward_projetado_reacao dos rounds (com reação parcial, tudo cai na mesma proporção)."""
    fr = {"$p": "suporte.padroes.ward_projetado_fracao"}
    return {"origem": "Projected Ward", "fator": fr, "corpo": {"pv": -ward},
            "reacao": {"uso": "Projected Ward", "fracao": {"$p": "suporte.padroes.ward_projetado_reacao"}, "eixos": ["suporte"]},
            "anexar": {"suporte.fontes": [{"nome": "Projected Ward (Arcane Ward num aliado)", "lado": "def", "modelo": "pv_temporario",
                                           "pv": ward, "usos_luta": 1, "fator": fr}]}}


# ---------- Abjuration: Arcane Ward somado ao PV; meia ----------
F = {}
for L in C.NIV:
    b = base(L); ward = 2 * L + b['i']; b['pv'] += ward
    F[L] = monta(L, b, 'meia'); F[L]['_texto'] += f" Arcane Ward {ward} somado ao PV."
    if L >= 6:
        F[L]['patches_linhas'] = [PROJECTED_WARD(ward)]; F[L]['_texto'] += " Projected Ward: parte do ward vai para os aliados."
sai('abjuration', 'meia', F, "Wizard (Abjuration), chassi: Mage Armor + Shield, Arcane Ward; posição meia",
    "Abjurador do chassi: a régua comum com o Arcane Ward como PV extra, um pouco mais perto da frente.",
    "Recarga do Arcane Ward na luta; Improved Abjuration; Spell Resistance (14).")

# ---------- Bladesinging: Bladesong + corpo a corpo; meia ----------
F = {}
for L in C.NIV:
    b = base(L, ORDEM_BS); m = b['m']; p = b['p']; dx = m['des']; ab = dx + p
    song = b['ca'] + b['i']
    bb = f"1d6+{dx}" + ("+1d8" if L < 11 else "+2d8")
    mel = [{"n": 1, "bonus": ab, "dano": bb, "nota": "Booming Blade (espada curta)"},
           {"n": 1, "bonus": ab, "dano": f"1d6+{dx}", "nota": "Extra Attack"},
           {"n": 1, "bonus": ab, "dano": "1d6", "nota": "espada curta na mão inábil (ação bônus)"}]
    # 27/11 (pacote C): o Bladesong vale em todas as linhas (patches_linhas com cobertura PB/dia ÷ lutas), não só nas "canto"
    canto = dict(id="canto", herda="principal", hipotese="corpo a corpo (Booming Blade + Extra Attack), com o Bladesong das outras linhas",
                 dano={"ataques": mel},
                 controle={"atencao": dict(AT(True, 'striker'), dpr="auto"), "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]},
                 defesa=SH, reacao=RE, gasta={"espacos": {"1": 1}}, area=[], invocacoes=[])
    hz = dict(canto, id="canto-haste", hipotese="corpo a corpo + Haste em si mesmo", corpo={"ca": b['ca'] + 2},
              dano={"ataques": mel + [{"n": 0.75, "bonus": ab, "dano": f"1d6+{dx}", "nota": "ataque do Haste"}]},
              gasta={"espacos": {"1": 1, "3": 1}}, plano="prioritaria")
    ex = [canto, hz]
    if L >= 11:
        t = [{"n": 2, "bonus": ab, "dano": f"1d6+{dx}+2d12", "vantagem": 1.0},
             {"n": 1, "bonus": ab, "dano": "1d6+2d12", "vantagem": 1.0, "nota": "mão inábil"}]
        ex.append(dict(canto, id="canto-tenser", hipotese="Tenser's Transformation (1/dia, sem magias)",
                       dano={"ataques": t}, defesa={}, reacao=[], gasta={"espacos": {"6": 1}}, plano="prioritaria"))
    f = monta(L, b, 'meia', extra=ex)
    f['patches_linhas'] = [{"origem": "Bladesong", "cobertura": {"usos": p, "volta": "longo"}, "corpo": {"ca": b['i']}}]
    f['_texto'] += f" Bladesong {p}/dia (CA {song}) em todas as linhas, coberto em min(1, {p}/4) das lutas."
    F[L] = f
sai('bladesinging', 'meia', F, "Wizard (Bladesinging), chassi: Int > Des, duas espadas curtas + Booming Blade, Mage Armor + Shield; meia",
    "Bladesinger do chassi: a régua comum de mago e, nas lutas em que entra no corpo a corpo, Bladesong com Booming Blade, Haste e (11) Tenser's.",
    "Dano secundário do Booming Blade; Song of Defense; Bladesong na concentração e a ação bônus de ligá-lo no 1º round; Shadow Blade.")

# ---------- Chronurgy: Chronal Shift (forcar_falha 0,5) + Momentary Stasis ----------
F = {}
for L in C.NIV:
    b = base(L)
    st = {"id": "estase", "herda": "principal", "hipotese": "Momentary Stasis num alvo (Int/dia ÷ 4 lutas), no lugar de 1 truque",
          "dano": b['cant'](0.75), "controle": {"atencao": C.atencao('retaguarda'), "fontes": [
              {"tipo": "condicao_no_acerto", "nome": "Momentary Stasis", "efeito": "cond_estase", "cd": b['cd'],
               "no_acerto": False, "usos": round(b['i'] / 4, 2)}]}, "area": [], "invocacoes": [], "defesa": {}}
    F[L] = monta(L, b, 'retaguarda', ff=0.5, extra=[st])
sai('chronurgy', 'retaguarda', F, "Wizard (Chronurgy), chassi: Mage Armor + Shield; retaguarda",
    "Cronurgista do chassi: a régua comum com Chronal Shift forçando falha no save do controle e Momentary Stasis.",
    "Temporal Awareness (iniciativa); Chronal Shift em aliados e ataques; Arcane Abeyance.", slug='chronurgy-magic')

# ---------- Conjuration: invocação = Summon Shadowspawn ----------
F = {}
for L in C.NIV:
    b = base(L); b['inv'] = dict(i=summon('shadowspawn', b['top'], b['a']), slot=b['top'])
    F[L] = monta(L, b, 'retaguarda')
sai('conjuration', 'retaguarda', F, "Wizard (Conjuration), chassi: Summon Shadowspawn como invocação; retaguarda",
    "Conjurador do chassi: a régua comum, com Summon Shadowspawn (a invocação que a escola favorece) no maior espaço.",
    "Minor Conjuration; Benign Transposition; Focused Conjuration (concentração não modelada); Durable Summons (14).")

def portent(f, dados):
    """27/11 (pacote C): os dados do Portent do dia (dados ÷ 4 lutas) se dividem sem contar duas vezes. Linha com magia de
    controle: a parte suporte.padroes.portent_fracao_controle força falha no save (forcar_falha_fator) e o resto vai para o
    suporte; linha sem controle: tudo no suporte. Suporte = dado_multiuso com "vira" (o d20 guardado substitui uma rolagem),
    sem ação, mix suporte.padroes.portent_mix (ataque de aliado, ataque inimigo, save de aliado)."""
    fr = {"$p": "suporte.padroes.portent_fracao_controle"}
    for l in f['linhas']:
        fs = (l.get('controle') or {}).get('fontes', [])
        com = [x for x in fs if x.get('forcar_falha')]
        for x in com: x['forcar_falha_fator'] = fr
        fonte = {"nome": "Portent (rolagens de aliados e inimigos)", "lado": "def", "modelo": "dado_multiuso",
                 "vira": {"$p": "suporte.padroes.portent_vira"}, "mix": {"$p": "suporte.padroes.portent_mix"},
                 "acao": "nenhuma", "usos_luta": round(dados / 4, 3)}
        if com: fonte.update(fator=fr, complemento=True)
        sp = l.setdefault('suporte', {}); sp.setdefault('fontes', []).append(fonte)
    return f


# ---------- Divination: Portent (forcar_falha 0,5) ----------
F = {}
for L in C.NIV:
    b = base(L); F[L] = portent(monta(L, b, 'retaguarda', ff=0.5), 2); F[L]['_texto'] += " Portent 2/dia (controle e suporte)."
sai('divination', 'retaguarda', F, "Wizard (Divination), chassi: Mage Armor + Shield; retaguarda",
    "Adivinho do chassi: a régua comum com Portent dividido entre forçar falha no save do controle e as rolagens de aliados e inimigos.",
    "Expert Divination; The Third Eye.")

# ---------- Enchantment: Hold Person, Hypnotic Gaze; Split Enchantment no 10 ----------
F = {}
for L in C.NIV:
    b = base(L); cd = b['cd']
    b['ctrl'] = b['ctrl'] + [HP_(cd), LPSY(cd)]
    if L >= 11:
        b['ctrl'] = [o for o in b['ctrl'] if o['f'].get('nome') not in ('Hold Monster', 'Psychic Lance')] + [
            U("Hold Monster (Split Enchantment)", "hold_monster", cd, 5, alvos=2), LPSY(cd, 2, "Psychic Lance (Split Enchantment: 2 alvos)")]
    olhar = {"id": "olhar", "herda": "principal",
             "hipotese": "Hypnotic Gaze: chega a 5 pés e gasta a ação para manter um alvo incapacitado (sem truques)",
             "dano": {"ataques": []}, "controle": {"atencao": AT(True), "fontes": [
                 {"tipo": "condicao_no_acerto", "nome": "Hypnotic Gaze", "efeito": "cond_hipnotizado", "cd": cd, "no_acerto": False, "usos": 2},
                 {"tipo": "ameaca", "nome": "Corpo (ameaça)"}]},
             "defesa": SH, "reacao": RE, "gasta": {"espacos": {"1": 1}}, "area": [], "invocacoes": []}
    F[L] = monta(L, b, 'retaguarda', extra=[olhar])
    if L >= 11: F[L]['_texto'] += " Split Enchantment: Hold Monster e Psychic Lance em 2 alvos."
sai('enchantment', 'retaguarda', F, "Wizard (Enchantment), chassi: + Hold Person e Psychic Lance; retaguarda",
    "Encantador do chassi: a régua comum + Hold Person, Psychic Lance e o Hypnotic Gaze; no 11, Split Enchantment.",
    "Instinctive Charm; Tasha's Hideous Laughter e Suggestion; Psychic Lance é do Fizban's/Strixhaven (Raulothim's) e entra como magia da escola.")

# ---------- Evocation: Sculpt Spells, Potent Cantrip (6), Empowered Evocation (10), + Chain Lightning ----------
F = {}
for L in C.NIV:
    b = base(L); cd = b['cd']; emp = b['i'] if L >= 11 else 0; e = f"+{emp}" if emp else ""
    b['areas'] = [area_sp("Fireball", 4, "8d6" + e, cd, 3, sel=True)] + (
        [area_sp("Cone of Cold", 6, "8d8" + e, cd, 5, sel=True), area_sp("Chain Lightning", 4, f"10d8{e}", cd, 6, sel=True)] if L >= 11 else [])
    b['cant'] = lambda n, L=L, cd=cd: toll(L, cd, n, True)
    F[L] = monta(L, b, 'retaguarda'); F[L]['_texto'] += " Potent Cantrip." + (" Empowered Evocation (+Int)." if emp else "")
sai('evocation', 'retaguarda', F, "Wizard (Evocation), chassi: Sculpt Spells, Potent Cantrip; retaguarda",
    "Evocador do chassi: a régua comum com áreas seletivas (Sculpt Spells), Potent Cantrip no Toll the Dead, Empowered Evocation e Chain Lightning no 11.",
    "Fogo amigo (Sculpt só entra como área seletiva); Overchannel (14).", slug='evoker')

# ---------- Graviturgy: + Pulse Wave (3) e Gravity Fissure (5) ----------
F = {}
for L in C.NIV:
    b = base(L); cd = b['cd']
    b['areas'] = b['areas'] + [area_sp("Pulse Wave", 3, "6d6", cd, 3)] + ([area_sp("Gravity Fissure", 4, "8d8", cd, 5)] if L >= 11 else [])
    F[L] = monta(L, b, 'retaguarda')
sai('graviturgy', 'retaguarda', F, "Wizard (Graviturgy), chassi: + Pulse Wave e Gravity Fissure; retaguarda",
    "Graviturgo do chassi: a régua comum + as áreas da escola (Pulse Wave, Gravity Fissure).",
    "Adjust Density; Gravity Well e o reposicionamento que prolonga as áreas; Violent Attraction.", slug='graviturgy-magic')

# ---------- Illusion: + Phantasmal Force e Phantasmal Killer ----------
F = {}
for L in C.NIV:
    b = base(L); cd = b['cd']
    b['ctrl'] = b['ctrl'] + [PF(cd), U("Phantasmal Killer", "phantasmal_killer", cd, 4)]
    F[L] = monta(L, b, 'retaguarda')
sai('illusion', 'retaguarda', F, "Wizard (Illusion), chassi: + Phantasmal Force e Phantasmal Killer; retaguarda",
    "Ilusionista do chassi: a régua comum + as ilusões de controle (Phantasmal Force, Phantasmal Killer).",
    "Improved Minor Illusion; Malleable Illusions; Illusory Self (10, reação); dano das ilusões.")

# ---------- Necromancy: Undead Thralls (esqueletos), Summon Undead ----------
F = {}
for L in C.NIV:
    b = base(L); p = b['p']; b['inv'] = dict(i=summon('undead', b['top'], b['a']), slot=b['top'])
    f = monta(L, b, 'retaguarda')
    q = 4 if L < 11 else 6
    esq = {"nome": "esqueletos (Undead Thralls)", "quantidade": q, "pv": 13 + L, "ca": 13, "ataque": {"bonus": 4, "dano": f"1d6+{2 + p}"},
           "nota": "arco curto; +PB de dano e +nível de PV (Undead Thralls)"}
    for l in f['linhas']:
        if l['id'].startswith('canto'): continue
        l['invocacoes'] = [esq] + [x for x in l.get('invocacoes', []) if 'Summon' in x['nome']]
    s = "3" if L < 11 else "4"; f['recursos']['espacos'][s] -= 1
    f['_texto'] += f" {q} esqueletos mantidos (Animate Dead: 1 espaço de {s}º por dia)."
    F[L] = f
sai('necromancy', 'retaguarda', F, "Wizard (Necromancy), chassi: esqueletos com Undead Thralls + Summon Undead; retaguarda",
    "Necromante do chassi: a régua comum + uma tropa de esqueletos mantida com Animate Dead e Summon Undead como invocação.",
    "Grim Harvest; Inured to Undeath; esqueletos sem armadura extra (CA 13 do Monster Manual).")

# ---------- Order of Scribes: só a régua ----------
F = {}
for L in C.NIV:
    F[L] = monta(L, base(L), 'retaguarda')
sai('order-of-scribes', 'retaguarda', F, "Wizard (Order of Scribes), chassi: só a régua comum; retaguarda",
    "Escriba do chassi: a régua comum; as features da ordem (troca de tipo de dano, Manifest Mind) não entram no motor.",
    "Awakened Spellbook (troca de tipo de dano: resistências não modeladas); Manifest Mind; Master Scrivener.", slug='scribes')

# ---------- Transmutation: Transmuter's Stone (Con), Polymorph em si mesmo ----------
F = {}
for L in C.NIV:
    b = base(L); b['profs'] = ('int', 'sab', 'con')
    if L < 11: fo = dict(ca=12, pv=157, at=[{"n": 2, "bonus": 9, "dano": "3d10+6", "nota": "Giant Ape, punho"}], nome="Giant Ape")
    else: fo = dict(ca=13, pv=136, at=[{"n": 1, "bonus": 10, "dano": "4d12+7", "nota": "T-Rex, mordida"},
                                     {"n": 1, "bonus": 10, "dano": "3d8+7", "nota": "T-Rex, cauda"}], nome="Tyrannosaurus Rex")
    poli = {"id": "polimorfo", "herda": "principal", "hipotese": f"Polymorph em si mesmo ({fo['nome']}); PV da forma somados aos do mago",
            "corpo": {"ca": fo['ca'], "pv": b['pv'] + fo['pv']}, "dano": {"ataques": fo['at']},
            "controle": {"atencao": {"papel": "tank", "front": True, "soft": 0.15, "dpr": "auto", "conc": True},
                         "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]},
            "defesa": {}, "reacao": [], "gasta": {"espacos": {"4": 1}}, "area": [], "invocacoes": []}
    F[L] = monta(L, b, 'retaguarda', extra=[poli]); F[L]['_texto'] += " Transmuter's Stone: proficiência em Con."
sai('transmutation', 'retaguarda', F, "Wizard (Transmutation), chassi: Transmuter's Stone (Con), Polymorph em si mesmo; retaguarda",
    "Transmutador do chassi: a régua comum + Polymorph em si mesmo (Giant Ape, T-Rex no 11) e a pedra dando save de Con.",
    "Minor Alchemy; Shapechanger (10); outras opções da pedra.")

# ---------- War Magic: Durable Magic (+2 CA e saves concentrando, 10) ----------
F = {}
for L in C.NIV:
    b = base(L); f = monta(L, b, 'retaguarda')
    if L >= 11:
        sv = {k: v + 2 for k, v in f['corpo']['saves']['sv'].items()}
        for l in f['linhas']:
            if l['id'] in ('controle', 'controle-barato', 'combo', 'invocacao'):
                l['corpo'] = {"ca": b['ca'] + 2, "saves": {"sv": sv, "conjurador": True, "ataques": 1}}
        f['_texto'] += " Durable Magic: +2 CA e saves concentrando."
    F[L] = f
sai('war-magic', 'retaguarda', F, "Wizard (War Magic), chassi: Durable Magic; retaguarda",
    "Mago de guerra do chassi: a régua comum + Durable Magic (+2 CA e saves) nas linhas com concentração.",
    "Arcane Deflection (reação: +2 CA/+4 save); Tactical Wit (iniciativa); Power Surge.")
