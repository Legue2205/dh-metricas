"""Chassi do Rogue (mini-mutirão 22/11): as 9 subclasses do gabarito, sem feat e com 2 feats no 4
(o 1º feat NÃO racial da build do RPGBot + o feat de posição: Mobile p/ skirmisher, Sharpshooter p/ atirador).
Rodar da raiz: python ferramentas/geradores/chassi_rogue.py && python -m dh expandir
Features das subclasses reaproveitadas de rog.py; raça, multiclasse, feats e atributos do RPGBot descartados.
Régua comum: Sneak Attack com os gatilhos das convenções do Rogue (aliado 0,75; Rakish 0,9; fonte própria 1,0);
couro batido (12 + Des); Uncanny Dodge (5+), Evasion (7+). Atirador = besta leve (1d8, simples) + Steady Aim;
skirmisher = rapieira + Cunning Action (Disengage), sem Steady Aim (Steady Aim prende no lugar)."""
import math
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402
import marcial as Mc  # noqa: E402

P_ALIADO, P_RAKISH, P_PROPRIA = 0.75, 0.9, 1.0
URL = "https://rpgbot.net/dnd5/characters/classes/rogue/subclasses/"
MEIO = {'Skill Expert': 'des', 'Piercer': 'des', 'Slasher': 'des'}   # meio-feats: +1 Des
ORD_PAD = ('des', 'con', 'sab', 'int', 'car', 'for')
AB_MIRA = [{"uso": "Steady Aim", "fracao": 1.0, "eixos": ["dano"]}]


def sa(L): return f"{math.ceil(L / 2)}d6"
def sneak(L, prob, nota=''): return {"dano": sa(L), "prob": prob, "nota": "Sneak Attack" + nota}
def booming(L): return '' if L < 5 else '+1d8' if L < 11 else '+2d8'


def piercer(f):
    ganho = {4: 0.5, 6: 0.75, 8: 1.0, 10: 1.25}[f]
    return [{"dano": str(max(ganho, 0.75)), "nota": "Piercer: rerrola 1 dado por turno"},
            {"dano": f"1d{f}", "gatilho": "critico", "nota": "Piercer: dado extra no crítico"}]


def ctl(pos, extra=()):
    return {"atencao": C.atencao(pos), "fontes": list(extra) + [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}


def defesa(L): return {"reacoes": [{"tipo": "uncanny_dodge"}]} if L >= 5 else {}


def base(L, ordem, feat):
    s = C.atributos('rogue', L, ordem, feat=feat, meio_feat=MEIO.get(feat)); m = C.mods(s); p = C.pb(L)
    ss = dict(sv=C.sv(L, m, ('des', 'int')))
    if L >= 7: ss['evasion'] = True
    corpo = {"ca": 12 + m['des'], "pv": C.hp(8, L, m['con']), "saves": ss}
    return s, m, p, corpo


def ln(id_, hip, dano, L, pos, **k):
    l = Mc.linha(id_, hip, dano, defesa(L), controle=ctl(pos, k.pop('fontes', ())), **k)
    return l


def atq(b, arma, d, feat, extra='', **k):
    a = Mc.A(1, b, arma, d, extra, **k)
    if feat == 'Sharpshooter': a['poder'] = [-5, 10]
    return a


def pierce(feat, f): return piercer(f) if feat == 'Piercer' else []


def mira_linha(L, b, d, feat, hip='besta leve com Steady Aim + Sneak', arma='1d8', f=8, nota='besta leve (Steady Aim)',
               pos='atirador'):
    dano = {"ataques": [atq(b, arma, d, feat, vantagem=1.0, nota=nota)],
            "por_turno": [sneak(L, P_PROPRIA, " (Steady Aim)")] + pierce(feat, f)}
    l = ln('principal', hip, dano, L, pos); l['acao_bonus'] = AB_MIRA
    return l


def rec(esp=None): return {"espacos": esp or {}, "outros": {}}


def fat(s, corpo, linhas, txt, esp=None):
    return {"corpo": corpo, "recursos": rec(esp), "linhas": linhas, "_texto": f"{txt} atributos {s}"}


# ------------------------------------------------------------------ subclasses
def arcane_trickster(L, feat):   # skirmisher: rapieira + Booming Blade, familiar dá o Sneak (fonte própria)
    s, m, p, corpo = base(L, ('des', 'int', 'con', 'sab', 'car', 'for'), feat); d, b = m['des'], p + m['des']
    dano = {"ataques": [atq(b, '1d8', d, feat, booming(L), nota="rapieira com Booming Blade")],
            "por_turno": [sneak(L, P_PROPRIA, " (familiar adjacente ao alvo)")] + pierce(feat, 8)}
    ls = [ln('principal', 'Booming Blade com rapieira + Sneak (familiar adjacente), Disengage', dano, L, 'skirmisher')]
    cd = 8 + p + m['int']
    d2 = {"ataques": [atq(b, '1d8', d, feat, booming(L), nota="round 1 vai para a magia")],
          "por_turno": [sneak(L, 0.75, " (3 de 4 rounds)")] + pierce(feat, 8)}
    d2['ataques'][0]['n'] = 0.75
    ls.append(ln('ilusao', 'Phantasmal Force no round 1 (2º círculo) + Booming Blade nos outros', d2, L, 'skirmisher',
                 fontes=[{"tipo": "alvo_unico", "nome": "Phantasmal Force", "cd": cd, "slots": [2],
                          "magias": ["phantasmal_force"], "modo": "melhor"}], gasta={"espacos": {"2": 1}}))
    esp = {7: {"1": 4, "2": 2}, 11: {"1": 4, "2": 3}}[L]
    return fat(s, corpo, ls, "Booming Blade, Find Familiar, Phantasmal Force; Uncanny Dodge, Evasion.", esp)


def assassin(L, feat):   # atirador; Assassinate se sobrepõe ao Steady Aim
    s, m, p, corpo = base(L, ORD_PAD, feat); d, b = m['des'], p + m['des']
    p_ini = 0.8 if feat == 'Alert' else 0.6
    v = round(0.25 * p_ini, 3); prob = round(1 - (1 - P_ALIADO) * (1 - v), 3)
    l2 = ln('assassinate', 'besta leve sem Steady Aim (ação bônus livre); Sneak por aliado ou Assassinate no round 1',
            {"ataques": [atq(b, '1d8', d, feat, vantagem=v, nota="vantagem do Assassinate no round 1")],
             "por_turno": [sneak(L, prob, " (aliado adjacente ou Assassinate)")] + pierce(feat, 8)}, L, 'atirador')
    return fat(s, corpo, [mira_linha(L, b, d, feat), l2], f"Assassinate (iniciativa vencida {p_ini}).")


def inquisitive(L, feat):
    s, m, p, corpo = base(L, ORD_PAD, feat); d, b = m['des'], p + m['des']
    return fat(s, corpo, [mira_linha(L, b, d, feat, 'besta leve com Steady Aim (ou Insightful Fighting) + Sneak')],
               "Insightful Fighting (redundante com Steady Aim).")


def mastermind(L, feat):
    s, m, p, corpo = base(L, ('des', 'con', 'car', 'sab', 'int', 'for'), feat); d, b = m['des'], p + m['des']
    n_al = 2 if L < 11 else 3
    l2 = ln('tatica', 'besta leve + Sneak (aliado adjacente); Master of Tactics: Help a 30 pés num ataque de aliado',
            {"ataques": [atq(b, '1d8', d, feat)], "por_turno": [sneak(L, P_ALIADO)] + pierce(feat, 8)}, L, 'atirador',
            suporte=[{"nome": "Master of Tactics (Help a distância)", "lado": "of", "modelo": "vantagem", "alvos": 1,
                      "fracao": round(1 / (3 * n_al), 3), "nota": "1 ataque de 1 aliado por round"}])
    l2['acao_bonus'] = [{"uso": "Master of Tactics", "fracao": 1.0, "eixos": ["suporte"]}]
    return fat(s, corpo, [mira_linha(L, b, d, feat), l2], "Master of Tactics.")


def phantom(L, feat):
    s, m, p, corpo = base(L, ORD_PAD, feat); d, b = m['des'], p + m['des']
    wd = math.ceil(math.ceil(L / 2) / 2)
    w = {"dano": f"{wd}d6", "nota": "Wails from the Grave (2º alvo, necrótico)"}
    if L < 9: w['usos_dia'] = p
    else: w['usos'] = round(p / 4 + 1, 2)
    l = mira_linha(L, b, d, feat, 'besta leve com Steady Aim + Sneak; Wails from the Grave num 2º alvo')
    l['dano']['por_luta'] = [w]
    if L >= 9:
        l['reacao'] = [{"uso": "Tokens of the Departed (pegar Soul Trinket)", "fracao": 0.25, "eixos": ["dano"]}]
        corpo['saves']['adv'] = ['con']
    return fat(s, corpo, [l], "Wails from the Grave; Tokens of the Departed (9).")


def scout(L, feat):
    s, m, p, corpo = base(L, ORD_PAD, feat); d, b = m['des'], p + m['des']
    return fat(s, corpo, [mira_linha(L, b, d, feat)], "Skirmisher, Survivalist; Superior Mobility (9).")


def soulknife(L, feat):
    s, m, p, corpo = base(L, ('des', 'con', 'int', 'sab', 'car', 'for'), feat); d, b = m['des'], p + m['des']
    l1 = mira_linha(L, b, d, feat, 'Psychic Blade arremessada com Steady Aim + Sneak', arma='1d6', f=6,
                    nota='Psychic Blade (60 pés) com Steady Aim')
    l1['dano']['por_turno'] = [sneak(L, P_PROPRIA, " (Steady Aim)")]   # dano psíquico: Piercer não vale
    l2 = ln('duas-laminas', 'duas Psychic Blades (ação bônus) + Sneak (aliado adjacente)',
            {"ataques": [atq(b, '1d6', d, feat), atq(b, '1d4', d, feat, nota="2ª lâmina na ação bônus")],
             "por_turno": [sneak(L, P_ALIADO)]}, L, 'atirador')
    l2['acao_bonus'] = [{"uso": "2ª Psychic Blade", "fracao": 1.0, "eixos": ["dano"]}]
    if L >= 9:
        hs = {"dado": 8 if L < 11 else 10, "usos": round((2 * p + 2) / 4, 2)}
        l1['dano']['dado_no_erro'] = hs; l2['dano']['dado_no_erro'] = dict(hs)
    return fat(s, corpo, [l1, l2], "Psychic Blades; Homing Strikes (9).")


def swashbuckler(L, feat):
    s, m, p, corpo = base(L, ('des', 'con', 'car', 'sab', 'int', 'for'), feat); d, b = m['des'], p + m['des']
    dano = {"ataques": [atq(b, '1d8', d, feat, nota="rapieira")],
            "por_turno": [sneak(L, P_RAKISH, " (Rakish Audacity ou aliado adjacente)")] + pierce(feat, 8)}
    return fat(s, corpo, [ln('principal', 'rapieira + Sneak (Rakish Audacity); Fancy Footwork para sair', dano, L,
                             'skirmisher')], "Fancy Footwork, Rakish Audacity; Panache (9).")


def thief(L, feat):
    s, m, p, corpo = base(L, ORD_PAD, feat); d, b = m['des'], p + m['des']
    l2 = ln('fast-hands', 'besta leve + Sneak (aliado adjacente); Fast Hands: frasco de ácido na ação bônus',
            {"ataques": [atq(b, '1d8', d, feat), Mc.A(1, d, '2d6', d, nota="ácido (improvisada, sem proficiência)")],
             "por_turno": [sneak(L, P_ALIADO)] + pierce(feat, 8)}, L, 'atirador')
    l2['acao_bonus'] = [{"uso": "Fast Hands (Use an Object)", "fracao": 1.0, "eixos": ["dano"]}]
    return fat(s, corpo, [mira_linha(L, b, d, feat), l2], "Fast Hands, Second-Story Work; Supreme Sneak (9).")


# sub: (função, posição, feat do RPGBot, origem, arma/armadura, resumo, nao_modelado)
SUBS = {
    'arcane-trickster': (arcane_trickster, 'skirmisher', 'Skill Expert', 'RPGBot (Small and Tricksy): Skill Expert no 4',
                         'rapieira + Booming Blade, couro batido',
                         'Trapaceiro arcano: Booming Blade com Sneak garantido pelo familiar; Phantasmal Force de controle.',
                         'Mage Hand Legerdemain, Silvery Barbs/Shield (reação; conflita com Uncanny Dodge), secundário do Booming Blade, Magical Ambush (9, precisa estar escondido).'),
    'assassin': (assassin, 'atirador', 'Alert', 'RPGBot (Killer Rabbit): Alert no 4', 'besta leve, couro batido',
                 'Assassino: Assassinate dá vantagem no round 1, mas se sobrepõe ao Steady Aim da régua comum.',
                 'Críticos automáticos da surpresa, Infiltration Expertise (9), Impostor (13).'),
    'inquisitive': (inquisitive, 'atirador', 'Piercer', 'RPGBot (PF2 Investigator): Piercer no 4', 'besta leve, couro batido',
                    'Investigador: percepção e intuição; em combate é o ladino básico de Steady Aim.',
                    'Ear for Deceit, Eye for Detail, Insightful Fighting (redundante com Steady Aim), Steady Eye (9).'),
    'mastermind': (mastermind, 'atirador', 'Skill Expert', 'RPGBot (Criminal Mastermind): Skill Expert no 4',
                   'besta leve, couro batido', 'Mentor: troca o Steady Aim por Help a distância para um aliado.',
                   'Insightful Manipulator (9), Misdirection (13), perfil social.'),
    'phantom': (phantom, 'atirador', 'Slasher', 'RPGBot (Raven Queen): Slasher no 8 (Elven Accuracy é racial), trazido ao 4',
                'besta leve, couro batido', 'Fantasma: Sneak no alvo e metade dos dados num 2º alvo; Soul Trinkets recarregam.',
                'Slasher (besta perfura: só o +1 Des vale), Whispers of the Dead, Ghost Walk (13).'),
    'scout': (scout, 'atirador', 'Piercer', 'RPGBot (Field Scholar): Piercer no 4', 'besta leve, couro batido',
              'Batedor: luta de longe e sai do corpo a corpo com a reação (Skirmisher).',
              'Skirmisher (reação; conflita com Uncanny Dodge), Survivalist, Superior Mobility (9), Ambush Master (13).'),
    'soulknife': (soulknife, 'atirador', 'Skill Expert', 'RPGBot (Half-Elf Skill Monkey): Skill Expert no 4',
                  'Psychic Blades arremessadas, couro batido', 'Lâmina psíquica: lâminas a 60 pés com Sneak; dados psiônicos.',
                  'Psi-Bolstered Knack, Psychic Whispers, Psychic Teleportation (9), dano psíquico (resistências).'),
    'swashbuckler': (swashbuckler, 'skirmisher', 'Skill Expert', 'RPGBot (Thundering Thrillseeker): Skill Expert no 4',
                     'rapieira, couro batido (sem Booming Blade: truque é racial no RPGBot)',
                     'Espadachim: Sneak quase garantido no duelo, entra e sai sem ataque de oportunidade.',
                     'Panache (9; taunt sem tipo no motor), Car na iniciativa, Elegant Maneuver (13).'),
    'thief': (thief, 'atirador', 'Piercer', 'RPGBot (chassi do Handbook do Fast Hands): Piercer no 4', 'besta leve, couro batido',
              'Ladrão: Fast Hands transforma a ação bônus em itens (ácido).',
              'Estrepes/armadilhas por item, Second-Story Work, Supreme Sneak (9), Use Magic Device (13).'),
}
FEAT_POS = {'skirmisher': 'Mobile', 'atirador': 'Sharpshooter'}

if __name__ == '__main__':
    for sub, (fn, pos, f_rpg, origem, equip, resumo, nm) in SUBS.items():
        for feat in (None, f_rpg, FEAT_POS[pos]):
            nm_f = nm + (' Mobile (sem mecânica de movimento no motor: diferença zero de propósito).' if feat == 'Mobile' else '')
            if feat in ('Skill Expert',): nm_f += ' Skill Expert: só o +1 Des e a expertise (perícias não modeladas).'
            if feat == 'Alert': nm_f += ' Alert: só a iniciativa do Assassinate (+5 na iniciativa no resto não conta).'
            orig = {None: 'sem feat', f_rpg: f'{feat} no 4 — {origem}',
                    FEAT_POS[pos]: f'{feat} no 4 — feat de posição ({pos})'}[feat]
            C.escrever('rogue', sub, pos, {L: fn(L, feat) for L in C.NIV},
                       build=f"Rogue ({sub.replace('-', ' ').title()}), {pos}, {equip}; {orig}",
                       desc={"resumo": "Chassi: " + resumo, "nao_modelado": nm_f.strip()},
                       feat=feat, url=URL + sub + '/')
