"""Chassi do Cleric (mini-mutirão 22/11): um chassi-cleric-<domínio> por subclasse do gabarito, fatias 7 e 11, só sem feat
(conjurador pleno). Regras em calibracao/convencoes-passada1.md, seção "Chassi"; peças das features vêm de cle.py/cle2.py.
Rodar da raiz: python ferramentas/geradores/chassi_cleric.py && python -m dh expandir

Régua comum a todos os domínios (linhas de cle.fatia): Toll the Dead na linha principal, Bless, Spiritual Weapon,
Spirit Guardians (+ com a arma), controle Hold Person (Banishment no 7+), Healing Word, Channel Divinity 2/descanso curto.
Sem opcionais de classe do Tasha (Harness Divine Power, Blessed Strikes), sem itens mágicos.
O domínio escolhe: posição, armadura (pesada só com proficiência), ordem dos atributos, arma (só quem tem Divine Strike e
fica na frente: domínios de armadura pesada e o Death, de armas marciais) e as magias de domínio que viram linha.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import wiz
wiz.escrever = lambda *a, **k: None          # importar cle/cle2 não reescreve as builds rpgbot-cleric-*
import cle  # noqa: E402
import cle2  # noqa: E402
import chassi as C  # noqa: E402
from cle import fatia, toll, sacred, wor, sw, sg_dano, sg_area, BLESS, HP, BAN, BLD, espacos, maior  # noqa: E402
from wiz import k, merge, U, area_sp  # noqa: E402

PESADA = ('sab', 'for', 'con', 'des', 'car', 'int')      # Sab, depois For (placas sem penalidade, arma de For)
MEDIA = ('sab', 'des', 'con', 'for', 'car', 'int')       # Sab, depois Des (meia-armadura +2)
POTENT = {'arcana', 'grave', 'knowledge', 'light', 'peace'}                   # Potent Spellcasting (8)
URLB = "https://rpgbot.net/dnd5/characters/classes/cleric/subclasses/"

# domínio -> (posição, armadura, arma ou None)   arma = (nome, dado, atributo, bônus mágico)
DOM = {
    'arcana':    ('retaguarda', 'media', None),
    'death':     ('meia', 'media', ('rapieira', '1d8', 'des', 0)),
    'forge':     ('defensor', 'pesada', ('maça +1 (Blessing of the Forge)', '1d6', 'for', 1)),
    'grave':     ('meia', 'media', None),
    'knowledge': ('retaguarda', 'media', None),
    'life':      ('defensor', 'pesada', ('maça', '1d6', 'for', 0)),
    'light':     ('retaguarda', 'media', None),
    'nature':    ('defensor', 'pesada', ('maça', '1d6', 'for', 0)),
    'order':     ('defensor', 'pesada', ('maça', '1d6', 'for', 0)),
    'peace':     ('retaguarda', 'media', None),
    'tempest':   ('defensor', 'pesada', ('martelo de guerra', '1d8', 'for', 0)),
    'trickery':  ('retaguarda', 'media', None),
    'twilight':  ('defensor', 'pesada', ('martelo de guerra', '1d8', 'for', 0)),
    'war':       ('striker', 'pesada', ('martelo de guerra', '1d8', 'for', 0)),
}

NM = {  # nao_modelado por domínio (além do comum)
    'arcana': "Arcane Initiate (2 truques de mago: o chassi usa o mesmo truque de todos); Magic Missile e magias de domínio utilitárias; Arcane Abjuration; Spell Breaker.",
    'death': "Inescapable Destruction; magias de domínio (False Life, Ray of Sickness, Vampiric Touch, Animate Dead, Blight, Cloudkill); Touch of Death só na linha de arma.",
    'forge': "Resistência a fogo; Searing Smite, Heat Metal, Elemental Weapon, Wall of Fire, Animate Objects; Blessing of the Forge na armadura ou num aliado.",
    'grave': "Eyes of the Grave; Path to the Grave dado a um aliado (o chassi usa Inflict Wounds, magia da lista do Cleric preparada por causa do Path); Bane, Vampiric Touch, Blight, Antilife Shell; Sentinel at Death's Door em aliados.",
    'knowledge': "Blessings of Knowledge e Knowledge of the Ages; Read Thoughts + Suggestion; Command (fora das listas de controle, passada 2); Confusion (sem modelo no motor); divinações.",
    'life': "Blessed Healer; Beacon of Hope, Mass Cure Wounds, Guardian of Faith, Death Ward; cura fora de luta.",
    'light': "Improved Flare (Warding Flare em aliados); Faerie Fire, Scorching Ray, Wall of Fire, Flame Strike, Guardian of Faith; fogo da esfera em quem termina o turno ao lado.",
    'nature': "Acolyte of Nature (truque de druida); Charm Animals and Plants; Dampen Elements; Barkskin, Spike Growth, Plant Growth, Wind Wall, Grasping Vine.",
    'order': "Order's Demand; Embodiment of Law; Command e Silvery Barbs com Voice of Authority; Heroism, Zone of Truth, Compulsion, Dominate Person; Mass Healing Word.",
    'peace': "Protective Bond (teleporte e redistribuição de dano); 1d4 em testes; Sanctuary, Aid, Warding Bond, Otiluke's Resilient Sphere.",
    'tempest': "Thunderbolt Strike (empurrão); Stormborn; Fog Cloud, Thunderwave, Call Lightning, Sleet Storm, Ice Storm.",
    'trickery': "Invoke Duplicity (vantagem só em ataque e magias lançadas da ilusão; o chassi usa truque de save e fica atrás); Divine Strike (sem linha de arma: armas simples e Des de retaguarda); Blessing of the Trickster; Cloak of Shadows; Charm Person, Pass without Trace, Mirror Image, Blink, Dimension Door, Polymorph.",
    'twilight': "Vigilant Blessing; Steps of Night (voo); Eyes of Night; remoção de medo/encantamento do santuário; Faerie Fire, Sleep, Moonbeam, Aura of Vitality, Greater Invisibility, Circle of Power.",
    'war': "Guided Strike (+10 no próprio acerto); Divine Favor, Shield of Faith, Magic Weapon, Freedom of Movement, Stoneskin, Flame Strike.",
}
RESUMO = {
    'arcana': "Clérigo base de retaguarda: o Arcana pouco muda na luta (Potent Spellcasting no truque).",
    'death': "Clérigo da morte perto da frente: Reaper (Toll the Dead em dois alvos) e rapieira com Touch of Death e Divine Strike.",
    'forge': "Defensor de placas com Soul of the Forge (+1 CA) e maça +1 do Blessing of the Forge com Divine Strike.",
    'grave': "Clérigo da tumba perto da frente: Path to the Grave + Inflict Wounds no maior espaço; Circle of Mortality no Healing Word.",
    'knowledge': "Clérigo base de retaguarda com Potent Spellcasting; as features do Knowledge são de exploração.",
    'life': "Defensor de placas: Disciple of Life no Healing Word, Preserve Life no Channel, maça com Divine Strike.",
    'light': "Blaster de retaguarda: Burning Hands, Fireball, Flaming Sphere, Radiance of the Dawn, Warding Flare.",
    'nature': "Defensor de placas: clérigo base com maça e Divine Strike; Insect Plague no 9.",
    'order': "Defensor de placas de suporte: Voice of Authority (Bless e Healing Word dão ataque a aliados), Slow, Divine Strike.",
    'peace': "Suporte de retaguarda: Emboldening Bond (1d4 em ataques e saves) e Balm of Peace.",
    'tempest': "Defensor de placas: Wrath of the Storm, Shatter/Destructive Wave maximizados com Destructive Wrath, martelo com Divine Strike.",
    'trickery': "Clérigo base de retaguarda: as features do Trickery não entram no chassi de truque (ver nao_modelado).",
    'twilight': "Defensor de placas: Twilight Sanctuary (PV temporários todo round) com Spirit Guardians, martelo com Divine Strike.",
    'war': "Striker de placas: martelo com War Priest e Divine Strike, Crusader's Mantle e War God's Blessing.",
}


def fat(sub, L):
    pos, arm, arma = DOM[sub]
    ordem = PESADA if arm == 'pesada' else MEDIA
    s = C.atributos('cleric', L, ordem); m = C.mods(s); p = C.pb(L)
    w = m['sab']; cd = 8 + p + w; atk = p + w
    ca = 20 if arm == 'pesada' else 17 + min(2, m['des'])      # placas + escudo / meia-armadura + escudo
    if sub == 'forge': ca += 1                                  # Soul of the Forge (6)
    pot = f"+{w}" if (sub in POTENT and L >= 8) else ""
    cant = lambda n: toll(L, cd, n, pot)
    esp = espacos(L); top = maior(esp)
    ctrl = [HP(cd), BAN(cd)]
    kw = dict(canal=2, esp=esp, ctrl=ctrl)
    extras, livres, sup, areas, ed = [], [], [], [], None
    front_ctl = {"atencao": C.atencao(pos if pos in ('defensor', 'striker') else 'meia', front=True),
                 "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}
    # ---- arma (domínios de Divine Strike que ficam na frente) ----
    if arma:
        nome, dado, at, mg = arma
        ds = "+1d8" if L >= 8 else ""
        golpe = {"n": 1.0, "bonus": p + m[at] + mg, "dano": f"{dado}+{m[at] + mg}{ds}",
                 "nota": nome + (" + Divine Strike" if ds else "")}
        dn = {"ataques": [golpe]}
        if sub == 'war':                                        # War Priest: Sab/dia ÷ 4 lutas ÷ 4 rounds
            dn["ataques"].append(dict(golpe, n=round(w / 16, 3), nota=nome + " (War Priest, ação bônus)"))
        if sub == 'death':                                      # Touch of Death: Channel ÷ 2 lutas (6+: 1 por luta)
            dn["por_luta"] = [{"usos": 1.0, "dano": str(5 + 2 * L), "nota": "Touch of Death (Channel Divinity ÷ 2 lutas)"}]
        extras.append(dict(id="arma", hipotese=f"{nome} todo round" + (" com Divine Strike" if ds else ""), dano=dn,
                           controle=front_ctl))
    # ---- features e magias de domínio ----
    if sub == 'death':
        livres.append({"nome": "Reaper (Toll the Dead em 2 alvos)", "tipo": "cleave_save", "dano": f"{k(L)}d12", "cd": cd, "save": "Sab", "alvos": [1, 2, 2]})
        ctrl.append(BLD(cd))
    elif sub == 'forge':
        pass
    elif sub == 'grave':
        def soco(n, s): return {"ataques": [{"n": n, "bonus": atk, "dano": f"{2 * (s + 2)}d10", "nota": f"Inflict Wounds ({s}º) no alvo vulnerável (Path to the Grave)"}]}
        extras.append(dict(id="punho", hipotese="Path to the Grave (ação) e Inflict Wounds no maior espaço no round seguinte",
                           dano=merge(cant(0.5), soco(0.25, top)), controle=front_ctl, gasta={"canal": 1, "espacos": {str(top): 1}}))
        kw.update(reac=("Sentinel at Death's Door", "anula_critico", w / 4), cura_extra=1.5)
    elif sub == 'life':
        extras.append(dict(id="preservar", hipotese="Preserve Life na luta (Channel Divinity, ação) + truques", dano=cant(0.75),
                           suporte={"fontes": [{"nome": "Preserve Life", "lado": "def", "modelo": "cura", "usos_luta": 1, "pv": 5 * L}]},
                           gasta={"canal": 1}))
        kw.update(cura_extra=3)                                  # Disciple of Life no Healing Word de 1º
    elif sub == 'light':
        areas += [area_sp("Burning Hands", 2, "3d6", cd, 1), area_sp("Fireball", 4, "8d6", cd, 3)]
        rod = {"nome": "Radiance of the Dawn", "tipo": "explosao", "usos": [{"alvos": 6, "seletiva": True, "dano": f"2d10+{L}", "cd": cd, "metade": True}]}
        extras += [dict(id="amanhecer", hipotese="Radiance of the Dawn (Channel Divinity) + truques", dano=cant(0.75), area=[rod], gasta={"canal": 1}),
                   dict(id="esfera", hipotese="Flaming Sphere (ação bônus) + truques",
                        dano=merge(cant(0.75), {"com_save": [{"n": 0.75, "cd": cd, "save": "Des", "dano": "2d6", "meio": True, "nota": "Flaming Sphere (ação bônus)"}]}),
                        gasta={"espacos": {"2": 1}})]
        kw.update(reac=("Warding Flare", "desvantagem", w / 4))
    elif sub == 'nature':
        if L >= 9:
            s = top
            extras.append(dict(id="praga", hipotese=f"Insect Plague ({s}º) como aura parada a distância + truques",
                               dano=merge(cant(0.75), {"com_save": [{"n": 0.75, "cd": cd, "save": "Con", "dano": f"{s - 1}d10", "meio": True, "nota": "Insect Plague no alvo"}]}),
                               area=[{"nome": f"Insect Plague ({s}º)", "tipo": "aura", "alvos": 4, "dano": f"{s - 1}d10", "cd": cd, "metade": True}],
                               gasta={"espacos": {str(s): 1}}))
    elif sub == 'order':
        voz = lambda usos: {"nome": f"Voice of Authority ({usos} ataque{'s' if usos > 1 else ''} de aliado por reação)", "lado": "of", "modelo": "ataque_extra", "alvos": round(usos / 4, 2)}
        extras += [dict(id="bless", hipotese="Bless + Voice of Authority (1 ataque de aliado)", dano=cant(0.75), suporte={"fontes": [BLESS, voz(1)]}, gasta={"espacos": {"1": 1}}),
                   dict(id="voz", hipotese="Healing Word num aliado como ação bônus em 2 rounds (Voice of Authority) + truques",
                        dano=cant(1.0), suporte={"fontes": [voz(2)]}, gasta={"espacos": {"1": 2}})]
        ctrl.append(U("Slow", "slow", cd, 3, area=True))
    elif sub == 'peace':
        al = min(p, 3); fr = min(1.0, p / 4)
        bond = [{"nome": "Emboldening Bond (1d4 em 1 ataque por turno)", "lado": "of", "modelo": "bonus_por_uso", "bonus": 2.5,
                 "usos_luta": round(4 * al * fr, 2), "nota": f"{al} aliados × 4 rounds × {fr:.2f} das lutas cobertas (PB {p}/dia)"},
                {"nome": "Emboldening Bond (1d4 nos saves)", "lado": "def", "modelo": "aura_saves", "bonus": round(2.5 * fr, 2)}]
        sup += bond
        extras.append(dict(id="balsamo", hipotese="Balm of Peace (Channel Divinity, ação) + truques", dano=cant(0.75),
                           suporte={"fontes": bond + [{"nome": "Balm of Peace (2 aliados)", "lado": "def", "modelo": "cura", "usos_luta": 1, "pv": 2 * (7 + w)}]},
                           gasta={"canal": 1}))
    elif sub == 'tempest':
        ed = {"com_save": [{"n": round(w / 16, 3), "cd": cd, "save": "Des", "dano": "2d8", "meio": True, "nota": "Wrath of the Storm (reação, Sab/dia ÷ 4 lutas ÷ 4 rounds)"}]}
        areas += [area_sp("Shatter", 2, "3d8", cd, 2)] + ([area_sp("Destructive Wave", 6, "10d10", cd, 5, sel=True)] if L >= 9 else [])
        if L >= 9:
            ira = {"nome": "Destructive Wave + Destructive Wrath (5º)", "tipo": "explosao", "usos": [{"alvos": 6, "seletiva": True, "dano": "50+5d10", "cd": cd, "metade": True}]}; si = 5
        else:
            ira = {"nome": f"Shatter + Destructive Wrath ({top}º)", "tipo": "explosao", "usos": [{"alvos": 2, "dano": str(8 * (top + 1)), "cd": cd, "metade": True}]}; si = top
        extras.append(dict(id="ira", hipotese="Destructive Wrath (Channel Divinity) maximizando a área do trovão no maior espaço",
                           dano=cant(0.75), area=[ira], gasta={"canal": 1, "espacos": {str(si): 1}}))
    elif sub == 'twilight':
        santo = {"nome": "Twilight Sanctuary (PV temporários todo round)", "lado": "def", "modelo": "pv_temporario", "usos_luta": 4, "alvos": 3, "pv": 3.5 + L}
        extras += [dict(id="santuario", hipotese="Twilight Sanctuary (Channel Divinity, ação, 1 minuto) + truques", dano=cant(0.75),
                        suporte={"fontes": [santo]}, gasta={"canal": 1}),
                   dict(id="santuario-guardioes", hipotese="Twilight Sanctuary (round 1) + Spirit Guardians (round 2) + truques",
                        dano=merge(cant(0.5), sg_dano(cd, top, 0.5)), suporte={"fontes": [santo]}, area=[sg_area(cd, top)],
                        gasta={"canal": 1, "espacos": {str(top): 1}})]
    elif sub == 'war':
        wgb = [{"nome": "War God's Blessing (+10 num ataque de aliado, reação)", "lado": "of", "modelo": "bonus_por_uso", "bonus": 10, "usos_descanso_curto": 2}]
        sup += wgb
        manto = {"nome": "Crusader's Mantle (aliados)", "lado": "of", "modelo": "dano_por_acerto", "alvos": 3, "dano_extra": 2.5, "concentracao": "crusaders_mantle"}
        extras.append(dict(id="manto", hipotese="Crusader's Mantle (aliados) + martelo", dano=extras[0]['dano'], controle=front_ctl,
                           suporte={"fontes": wgb + [manto]}, gasta={"espacos": {"3": 1}}))
        if L >= 9: ctrl.append(U("Hold Monster", "hold_monster", cd, 5))
    f = fatia(L, m, ('sab', 'car'), ca, C.hp(8, L, m['con']), cant, cd, atk, w, 'conjurador', False, (L + 1) // 2,
              areas=areas, livres=livres, extra_dano=ed, sup=sup, extras=extras, **kw)
    if sub == 'order':   # troca o Bless genérico pelo com Voice (como no cle2)
        f['linhas'] = [l for l in f['linhas'] if not (l['id'] in ('bless', 'bless+arma')
                       and not any(x['nome'].startswith('Voice') for x in l['suporte']['fontes']))]
    # posição do chassi: atenção da linha principal; linhas que ficam no corpo a corpo ganham front
    for l in f['linhas']:
        if l['id'] == 'principal':
            l['controle']['atencao'] = C.atencao(pos)
        elif l['id'].startswith('guardioes') and pos not in ('defensor', 'striker'):
            l['controle'] = json.loads(json.dumps(front_ctl))
        elif l['id'] in ('controle', 'controle+arma'):
            l['controle']['atencao'] = C.atencao(pos)
        if l['id'] != 'principal': l.setdefault('hipotese', l['id'])
    f['_texto'] = (f"Cleric {L}; atributos {s}; CA {ca} (" + ("placas" if arm == 'pesada' else "meia-armadura") + " + escudo"
                   + (" + Soul of the Forge" if sub == 'forge' else "") + ")" + ("; Potent Spellcasting" if pot else "") + ".")
    return f


for sub in DOM:
    pos, arm, arma = DOM[sub]
    C.escrever('cleric', sub, pos, {L: fat(sub, L) for L in C.NIV},
               build=f"Cleric ({sub.title()}), {pos}, " + ("placas" if arm == 'pesada' else "meia-armadura") + " + escudo"
                     + (f", {arma[0]}" if arma else "") + "; Toll the Dead; sem feat",
               desc={"resumo": "Chassi do " + sub.title() + ": " + RESUMO[sub],
                     "estrategia": "Régua comum do chassi (Toll the Dead, Bless, Spiritual Weapon, Spirit Guardians, Hold Person/Banishment, Healing Word) + o que o domínio dá; o plano automático escolhe.",
                     "nao_modelado": NM[sub] + " Comum: cura além do Healing Word; utilitárias; quebra de concentração; penalidade de deslocamento ignorada."},
               url=URLB + {'arcana': 'arcana-domain', 'knowledge': 'knowledge-domain', 'life': 'life-domain',
                           'light': 'light-domain', 'tempest': 'tempest-domain', 'trickery': 'trickery-domain',
                           'war': 'war-domain'}.get(sub, sub) + '/')
