"""Rogue (passada 1, mutirão 21/11): as 9 builds do RPGBot (Thief = chassi, sem build dedicada). Rodar da raiz:
python ferramentas/geradores/rog.py && python -m dh expandir progressoes/rpgbot-rogue-*.json
Convenções: seção Rogue do relatório do mutirão (a colar em calibracao/convencoes-passada1.md)."""
import math, sys
sys.path.insert(0, 'ferramentas/geradores')
import marcial
from marcial import *
marcial.CLASSE = 'rogue'

# Gatilho do Sneak Attack (prob por turno, além do acerto):
P_ALIADO = 0.75     # sem fonte própria: aliado adjacente ao alvo (ou alvo distraído) — hipótese da passada 1
P_RAKISH = 0.9      # Rakish Audacity OU aliado adjacente (união das duas condições)
P_PROPRIA = 1.0     # fonte mecânica própria: Steady Aim (vantagem), familiar adjacente


def sa(L): return f"{math.ceil(L / 2)}d6"
def booming(L): return '' if L < 5 else '+1d8' if L < 11 else '+2d8'   # Booming Blade no acerto (o secundário não conta)
def ganho_rr(f): return {4: 0.5, 6: 0.75, 8: 1.0, 10: 1.25, 12: 1.5}[f]


def sneak(L, prob, nota=''):
    return {"dano": sa(L), "prob": prob, "nota": "Sneak Attack" + nota}


def piercer(arma):
    f = int(arma.split('d')[1])
    return [{"dano": str(max(ganho_rr(f), 0.75)), "nota": "Piercer: rerrola 1 dado por turno"},
            {"dano": f"1d{f}", "gatilho": "critico", "nota": "Piercer: dado extra no crítico"}]


def ss_rog(L, m, extra_profs=(), **k):
    d = dict(sv=sv(L, m, ('des', 'int') + tuple(extra_profs)), **k)
    if L >= 7: d['evasion'] = True
    return d


def def_rog(L, **k):
    d = dict(k)
    if L >= 5: d['reacoes'] = [{"tipo": "uncanny_dodge"}] + d.get('reacoes', [])
    return d


def corpo_r(L, dx, cn, ss):
    return dict(ca=12 + mod(dx), pv=hp([8] * L, mod(cn)), saves=ss)


def rec(esp=None, **o): return {"espacos": esp or {}, "outros": o}


def mira(L, b, arma, dm, extra_pt=(), ea=False, nota='Steady Aim (ação bônus, sem mover): vantagem e Sneak garantido'):
    a = A(1, b, arma, dm, vantagem=1.0, nota=nota)
    if ea: a['elven_accuracy'] = True
    return {"ataques": [a], "por_turno": [sneak(L, P_PROPRIA)] + list(extra_pt)}


AB_MIRA = [{"uso": "Steady Aim", "fracao": 1.0, "eixos": ["dano"]}]

# ---------------------------------------------------------------- Arcane Trickster (Small and Tricksy)
def at(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn, it = 14, 16; d, i, P = mod(dx), mod(it), pb(L)
    m = M(-1, d, 2, i, 0, -1); b = P + d; ss = ss_rog(L, m)
    dano = {"ataques": [A(1, b, '1d8', d, booming(L), nota="rapieira com Booming Blade")],
            "por_turno": [sneak(L, P_PROPRIA, " (familiar adjacente ao alvo: cobra-cachecol)")]}
    ls = [linha('principal', 'Booming Blade com rapieira + Sneak (familiar adjacente), Disengage e voo', dano, def_rog(L),
                papel='striker')]
    if L >= 7:
        cd = 8 + P + i
        d2 = {"ataques": [A(0.75, b, '1d8', d, booming(L), nota="round 1 vai para a magia")],
              "por_turno": [dict(sneak(L, P_PROPRIA), prob=0.75)]}
        ls.append(linha('ilusao', 'Phantasmal Force no round 1 (2º círculo) + Booming Blade nos outros', d2, def_rog(L),
                        controle=ctrl('striker', [{"tipo": "alvo_unico", "nome": "Phantasmal Force", "cd": cd, "slots": [2],
                                                   "magias": ["phantasmal_force"], "modo": "melhor"}]),
                        gasta={"espacos": {"2": 1}}))
    esp = {3: {"1": 2}, 5: {"1": 3}, 7: {"1": 4, "2": 2}, 9: {"1": 4, "2": 2}, 11: {"1": 4, "2": 3}}[L]
    txt = {3: "Booming Blade, Silvery Barbs, Silent Image, Find Familiar; Fairy (voo, Faerie Fire 1/dia).",
           5: "Skill Expert (Dex 18, 4); Uncanny Dodge; Booming Blade 1d8.", 7: "Evasion; Phantasmal Force.",
           9: "Dex 20 (8); Magical Ambush.", 11: "Fey Touched (10: Misty Step, Hex); Reliable Talent; Booming Blade 2d8."}[L]
    return dict(_texto=txt, corpo=corpo_r(L, dx, cn, ss), recursos=rec(esp), linhas=ls)


escrever('rpgbot-rogue-arcane-trickster', 'arcane-trickster', 'Arcane Trickster (RPGBot: Small and Tricksy)',
         'Rogue (Arcane Trickster), Fairy, rapieira + Booming Blade, familiar cobra; Skill Expert 4, Dex 20 8, Fey Touched 10',
         {"resumo": "Trapaceiro arcano: Booming Blade com Sneak garantido pelo familiar, voo do Fairy e ilusões de controle.",
          "estrategia": "Voa, desce, Booming Blade com Sneak, Disengage e sobe; Phantasmal Force no alvo grande a partir do 7.",
          "nao_modelado": "Silvery Barbs (reação; conflita com Uncanny Dodge), Faerie Fire do Fairy, Silent Image como caixa de esconder, secundário do Booming Blade, Magical Ambush (precisa estar escondido), voo como defesa, Versatile Trickster (13), Haste (14)."},
         {L: at(L) for L in NIV})

# ---------------------------------------------------------------- Assassin (Killer Rabbit)
def assassin(L):
    dx = {3: 16, 5: 16, 7: 16, 9: 18, 11: 20}[L]; cn = 16; d, P = mod(dx), pb(L)
    m = M(-1, d, 3, -1, -1, 3); b = P + d; ss = ss_rog(L, m)
    p_ini = {3: 0.6, 5: 0.8, 7: 0.8, 9: 0.85, 11: 0.95}[L]   # vence a iniciativa (Harengon + Alert; Reliable Talent no 11)
    v = round(0.25 * p_ini, 3)                                # Assassinate: vantagem no round 1 (1 de 4 rounds)
    prob = round(1 - (1 - P_ALIADO) * (1 - v), 3)
    dano = {"ataques": [A(1, b, '1d6', d, vantagem=v, nota="arco curto; vantagem do Assassinate no round 1")],
            "por_turno": [sneak(L, prob, " (aliado adjacente ou Assassinate no round 1)")]}
    ls = [linha('principal', 'arco curto + Sneak; Assassinate dá vantagem no round 1 quando vence a iniciativa', dano,
                def_rog(L), papel='atirador')]
    txt = {3: "Assassinate (vantagem contra quem não agiu); Harengon (PB na iniciativa).", 5: "Alert (4); Uncanny Dodge.",
           7: "Evasion.", 9: "Dex 18 (8); Infiltration Expertise.", 11: "Dex 20 (10); Reliable Talent (iniciativa mínima 24)."}[L]
    return dict(_texto=txt, corpo=corpo_r(L, dx, cn, ss), recursos=rec(), linhas=ls)


escrever('rpgbot-rogue-assassin', 'assassin', 'Assassin (RPGBot: The Killer Rabbit of Caerbannog)',
         'Rogue (Assassin), Harengon, arco curto; Alert 4, Dex 18 8, Dex 20 10',
         {"resumo": "Assassino de iniciativa: quase sempre age primeiro e abre com Sneak com vantagem; surpresa é bônus.",
          "estrategia": "Arco curto a distância, Sneak nos alvos que os aliados seguram; round 1 com vantagem do Assassinate.",
          "nao_modelado": "Críticos automáticos da surpresa (exigem a party toda furtiva), Rabbit Hop, Death Strike (17), perfil social (Infiltration Expertise, Impostor)."},
         {L: assassin(L) for L in NIV})

# ---------------------------------------------------------------- Inquisitive (PF2 Investigator)
def inquis(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn = 14; d, P = mod(dx), pb(L)
    m = M(-1, d, 2, 1, 2, -1); b = P + d; ss = ss_rog(L, m, adv=['int', 'sab', 'car'])   # Vedalken Dispassion
    pr = piercer('1d6') if L >= 5 else []
    ls = [linha('principal', 'arco curto com Steady Aim (ou Insightful Fighting) + Sneak', mira(L, b, '1d6', d, pr),
                def_rog(L), papel='atirador')]
    ls[0]['acao_bonus'] = AB_MIRA
    txt = {3: "Insightful Fighting e Steady Aim; Vedalken.", 5: "Piercer (Dex 18, 4); Uncanny Dodge.", 7: "Evasion.",
           9: "Dex 20 (8); Steady Eye.", 11: "Observant (10); Reliable Talent."}[L]
    return dict(_texto=txt, corpo=corpo_r(L, dx, cn, ss), recursos=rec(), linhas=ls)


escrever('rpgbot-rogue-inquisitive', 'inquisitive', 'Inquisitive (RPGBot: I Really Wanted to Play the PF2 Investigator)',
         'Rogue (Inquisitive), Vedalken, arco curto + Steady Aim; Piercer 4, Dex 20 8, Observant 10',
         {"resumo": "Investigador: percepção e intuição imbatíveis; em combate é um ladino básico com Steady Aim.",
          "estrategia": "Arco curto, Steady Aim todo turno; Insightful Fighting quando precisa se mover.",
          "nao_modelado": "Eye for Detail; Eye for Weakness (17)."},
         {L: inquis(L) for L in NIV})

# ---------------------------------------------------------------- Mastermind (Criminal Mastermind)
def mastermind(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 19, 11: 20}[L]; cn = 14; d, P = mod(dx), pb(L)
    m = M(-1, d, 2, -1, 1, 2); b = P + d; ss = ss_rog(L, m)
    pr = piercer('1d10') if L >= 9 else []
    atq = 1 if L < 5 else 2 if L < 11 else 3   # ataques do aliado na régua de suporte
    ls = [linha('principal', 'besta pesada com Steady Aim + Sneak', mira(L, b, '1d10', d, pr), def_rog(L), papel='atirador'),
          linha('tatica', 'besta pesada + Sneak (aliado adjacente); Master of Tactics: Help a 30 pés num ataque de aliado',
                {"ataques": [A(1, b, '1d10', d)], "por_turno": [sneak(L, P_ALIADO)] + pr}, def_rog(L), papel='atirador',
                suporte=[{"nome": "Master of Tactics (Help a distância)", "lado": "of", "modelo": "vantagem", "alvos": 1,
                          "fracao": round(1 / (3 * atq), 3), "nota": "1 ataque de 1 aliado por round"}])]
    ls[0]['acao_bonus'] = AB_MIRA
    ls[1]['acao_bonus'] = [{"uso": "Master of Tactics", "fracao": 1.0, "eixos": ["suporte"]}]
    txt = {3: "Master of Tactics; Steady Aim; Hobgoblin (besta pesada).", 5: "Skill Expert (Dex 18, 4); Uncanny Dodge.",
           7: "Evasion.", 9: "Piercer (Dex 19, 8).", 11: "Dex 20 / Car 16 (10); Reliable Talent."}[L]
    return dict(_texto=txt, corpo=corpo_r(L, dx, cn, ss), recursos=rec(), linhas=ls)


escrever('rpgbot-rogue-mastermind', 'mastermind', 'Mastermind (RPGBot: Criminal Mastermind)',
         'Rogue (Mastermind), Hobgoblin (Custom Origin), besta pesada; Skill Expert 4, Piercer 8, Dex 20/Car 16 10',
         {"resumo": "Mentor: face social; em combate troca o Steady Aim por Help a distância para um aliado.",
          "estrategia": "Besta pesada com Steady Aim; Master of Tactics quando um aliado tem um ataque grande.",
          "nao_modelado": "Saving Face do Hobgoblin, Help em teste de empurrão, Insightful Manipulator, Misdirection (13)."},
         {L: mastermind(L) for L in NIV})

# ---------------------------------------------------------------- Phantom (Raven Queen)
def phantom(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 19, 11: 20}[L]; cn = 15; d, P = mod(dx), pb(L)
    m = M(-1, d, 2, 0, 2, 0); b = P + d; ss = ss_rog(L, m)
    wd = math.ceil(math.ceil(L / 2) / 2)
    wails = {"dano": f"{wd}d6", "nota": "Wails from the Grave (2º alvo, necrótico, depois do Sneak)"}
    if L < 9: wails['usos_dia'] = P
    else: wails['usos'] = round(P / 4 + 1, 2)   # PB por dia ÷ 4 lutas + 1 Soul Trinket por luta (reação)
    dano = mira(L, b, '1d4', d, ea=L >= 5, nota='chicote (alcance) com Steady Aim')
    dano['por_luta'] = [wails]
    l = linha('principal', 'chicote com Steady Aim + Sneak; Wails from the Grave num 2º alvo', dano, def_rog(L), papel='striker')
    l['acao_bonus'] = AB_MIRA
    if L >= 9: l['reacao'] = [{"uso": "Tokens of the Departed (pegar Soul Trinket)", "fracao": 0.25, "eixos": ["dano"]}]
    txt = {3: "Wails from the Grave; Steady Aim; elfo da floresta com chicote.", 5: "Elven Accuracy (Dex 18, 4); Uncanny Dodge.",
           7: "Evasion.", 9: "Slasher (Dex 19, 8); Tokens of the Departed.", 11: "Athlete (Dex 20, 10); Reliable Talent."}[L]
    cp = corpo_r(L, dx, cn, ss)
    if L >= 9: cp['saves']['adv'] = ['con']   # Soul Trinket na mão: vantagem em saves de Con
    return dict(_texto=txt, corpo=cp, recursos=rec(), linhas=[l])


escrever('rpgbot-rogue-phantom', 'phantom', "Phantom (RPGBot: Can't defeat Her, so instead I'll have to be Her)",
         'Rogue (Phantom), elfo da floresta, chicote + Steady Aim; Elven Accuracy 4, Slasher 8, Athlete 10',
         {"resumo": "Fantasma: Sneak no alvo e metade dos dados em necrótico num segundo alvo; Soul Trinkets recarregam.",
          "estrategia": "Chicote a 10 pés com Steady Aim; Wails from the Grave quando há dois inimigos perto.",
          "nao_modelado": "Slasher (velocidade), Whispers of the Dead, pergunta ao morto, Ghost Walk (13)."},
         {L: phantom(L) for L in NIV})

# ---------------------------------------------------------------- Scout (Field Scholar)
def scout(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 19, 11: 20}[L]; cn = 15; d, P = mod(dx), pb(L)
    m = M(-1, d, 2, 1, 1, -1); b = P + d; ss = ss_rog(L, m)
    arma = '1d6' if L < 9 else '1d12'
    pr = piercer(arma) if L >= 5 else []
    dano = {"ataques": [A(1, b, arma, d, nota="arco curto" if L < 9 else "mosquete (Gunner)")],
            "por_turno": [sneak(L, P_ALIADO)] + pr}
    ls = [linha('principal', 'arco curto/mosquete + Sneak (sem Steady Aim: o guia não usa opcionais)', dano, def_rog(L),
                papel='atirador')]
    txt = {3: "Skirmisher, Survivalist; Harengon.", 5: "Piercer (Dex 18, 4); Uncanny Dodge.", 7: "Evasion.",
           9: "Gunner (Dex 19, 8): mosquete 1d12; Superior Mobility.", 11: "Skill Expert (Dex 20, 10); Reliable Talent."}[L]
    return dict(_texto=txt, corpo=corpo_r(L, dx, cn, ss), recursos=rec(), linhas=ls)


escrever('rpgbot-rogue-scout', 'scout', 'Scout (RPGBot: Field Scholar)',
         'Rogue (Scout), Harengon, arco curto e depois mosquete; Piercer 4, Gunner 8, Skill Expert 10',
         {"resumo": "Batedor: explorador de perícias que luta de longe e sai do corpo a corpo com a reação.",
          "estrategia": "Atira de longe; Cunning Action para se esconder; Skirmisher para sair do alcance.",
          "nao_modelado": "Hide com Cunning Action (vantagem depende de cobertura), Skirmisher (reação; conflita com Uncanny Dodge), Ambush Master (13), Sudden Strike (17)."},
         {L: scout(L) for L in NIV})

# ---------------------------------------------------------------- Soulknife (Half-Elf Skill Monkey)
def soulknife(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn = 12; d, P = mod(dx), pb(L)
    m = M(-1, d, 1, 3, 2, -1); b = P + d; ss = ss_rog(L, m)
    l1 = linha('principal', 'Psychic Blade arremessada com Steady Aim + Sneak', mira(L, b, '1d6', d, nota='Psychic Blade (60 pés) com Steady Aim'),
               def_rog(L), papel='atirador')
    l1['acao_bonus'] = AB_MIRA
    l2 = linha('duas-laminas', 'duas Psychic Blades (ação bônus) + Sneak (aliado adjacente)',
               {"ataques": [A(1, b, '1d6', d), A(1, b, '1d4', d, nota="2ª lâmina na ação bônus (soma Des)")],
                "por_turno": [sneak(L, P_ALIADO)]}, def_rog(L), papel='atirador')
    l2['acao_bonus'] = [{"uso": "2ª Psychic Blade", "fracao": 1.0, "eixos": ["dano"]}]
    if L >= 9:   # Homing Strikes: dado psiônico no erro, gasto só se acertar; (2×PB + 2 recargas curtas) ÷ 4 lutas
        hs = {"dado": 8 if L < 11 else 10, "usos": round((2 * P + 2) / 4, 2)}
        l1['dano']['dado_no_erro'] = hs; l2['dano']['dado_no_erro'] = hs
    txt = {3: "Psychic Blades, Psionic Power (2×PB dados); Steady Aim; meio-elfo.", 5: "Skill Expert (Dex 18, 4); Uncanny Dodge; dado d8.",
           7: "Evasion.", 9: "Dex 20 (8); Soul Blades (Homing Strikes, Psychic Teleportation).", 11: "Skulker (10); Reliable Talent; dado d10."}[L]
    return dict(_texto=txt, corpo=corpo_r(L, dx, cn, ss), recursos=rec(), linhas=[l1, l2])


escrever('rpgbot-rogue-soulknife', 'soulknife', 'Soulknife (RPGBot: Half-Elf Skill Monkey)',
         'Rogue (Soulknife), meio-elfo, Psychic Blades + Steady Aim; Skill Expert 4, Dex 20 8, Skulker 10',
         {"resumo": "Lâmina psíquica: arremessa lâminas a 60 pés com Sneak; dados psiônicos para perícias e acertos.",
          "estrategia": "Steady Aim com uma lâmina quando falta aliado; duas lâminas quando há aliado no alvo.",
          "nao_modelado": "Psychic Teleportation, Psi-Bolstered Knack, Psychic Veil (13), Rend Mind (17), dano psíquico (resistências)."},
         {L: soulknife(L) for L in NIV})

# ---------------------------------------------------------------- Swashbuckler (Thundering Thrillseeker)
def swash(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn, ch = 16, 16; d, P = mod(dx), pb(L)
    m = M(-1, d, 3, -1, -1, 3); b = P + d; ss = ss_rog(L, m)
    dano = {"ataques": [A(1, b, '1d8', d, booming(L), nota="rapieira com Booming Blade")],
            "por_turno": [sneak(L, P_RAKISH, " (Rakish Audacity ou aliado adjacente)")]}
    sup = None
    if L >= 11:
        sup = [{"nome": "Inspiring Leader", "lado": "def", "modelo": "pv_temporario", "pv": L + mod(ch),
                "quando": "entre_lutas", "usos_descanso_curto": 1}]
    ls = [linha('principal', 'Booming Blade com rapieira + Sneak (Rakish Audacity); Fancy Footwork para sair', dano,
                def_rog(L), papel='striker', suporte=sup)]
    txt = {3: "Fancy Footwork, Rakish Audacity; meio-elfo alto (Booming Blade).", 5: "Skill Expert (Dex 18, 4); Uncanny Dodge.",
           7: "Evasion.", 9: "Dex 20 (8); Panache.", 11: "Inspiring Leader (10); Reliable Talent; Booming Blade 2d8."}[L]
    return dict(_texto=txt, corpo=corpo_r(L, dx, cn, ss), recursos=rec(), linhas=ls)


escrever('rpgbot-rogue-swashbuckler', 'swashbuckler', 'Swashbuckler (RPGBot: Thundering Thrillseeker)',
         'Rogue (Swashbuckler), meio-elfo alto, rapieira + Booming Blade; Skill Expert 4, Dex 20 8, Inspiring Leader 10',
         {"resumo": "Espadachim: Sneak quase garantido no duelo, entra e sai sem ataque de oportunidade.",
          "estrategia": "Booming Blade no alvo isolado e sai com Fancy Footwork; Panache para prender um inimigo em si.",
          "nao_modelado": "Panache (taunt de 1 minuto: sem tipo de taunt por condição no motor), secundário do Booming Blade, Car na iniciativa, Elegant Maneuver (13), Master Duelist (17)."},
         {L: swash(L) for L in NIV})

# ---------------------------------------------------------------- Thief (chassi do Handbook; sem build dedicada)
def thief(L):
    dx = {3: 17, 5: 18, 7: 18, 9: 20, 11: 20}[L]; cn = 14; d, P = mod(dx), pb(L)
    m = M(-1, d, 2, 0, 1, 0); b = P + d; ss = ss_rog(L, m)
    pr = piercer('1d6') if L >= 5 else []
    l1 = linha('principal', 'arco curto com Steady Aim + Sneak', mira(L, b, '1d6', d, pr), def_rog(L), papel='atirador')
    l1['acao_bonus'] = AB_MIRA
    l2 = linha('fast-hands', 'arco curto + Sneak (aliado adjacente); Fast Hands: frasco de ácido na ação bônus',
               {"ataques": [A(1, b, '1d6', d), A(1, d, '2d6', d, nota="ácido (arma improvisada, sem proficiência; soma Des)")],
                "por_turno": [sneak(L, P_ALIADO)] + pr}, def_rog(L), papel='atirador')
    l2['acao_bonus'] = [{"uso": "Fast Hands (Use an Object)", "fracao": 1.0, "eixos": ["dano"]}]
    txt = {3: "Fast Hands, Second-Story Work; Steady Aim.", 5: "Piercer (Dex 18, 4); Uncanny Dodge.", 7: "Evasion.",
           9: "Dex 20 (8); Supreme Sneak.", 11: "ASI/feat livre (10); Reliable Talent."}[L]
    return dict(_texto=txt, corpo=corpo_r(L, dx, cn, ss), recursos=rec(), linhas=[l1, l2])


escrever('rpgbot-rogue-thief', 'thief', 'Thief (chassi do Handbook do RPGBot)',
         'Rogue (Thief), chassi do Handbook (sem build dedicada no RPGBot): arco curto + Steady Aim; Piercer 4, Dex 20 8',
         {"resumo": "Ladrão: o ladino icônico; Fast Hands transforma a ação bônus em itens (ácido, estrepes, kit de cura).",
          "estrategia": "Steady Aim no padrão; frasco de ácido com Fast Hands quando há aliado no alvo.",
          "nao_modelado": "Estrepes/armadilha de caça/esferas (controle por item sem tipo), Healer feat, Second-Story Work, Supreme Sneak, Use Magic Device (13), Thief's Reflexes (17)."},
         {L: thief(L) for L in NIV},
         fonte={"tipo": "rpgbot", "url": "https://rpgbot.net/dnd5/characters/classes/rogue/fast-hands/",
                "nota": NOTA + " Sem build dedicada: chassi do Handbook (como o Berserker)."})
