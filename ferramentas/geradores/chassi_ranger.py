"""Chassi do Ranger (mini-mutirão 22/11): 8 conclaves do gabarito, sem feat e com o feat da subclasse.
Rodar da raiz: python ferramentas/geradores/chassi_ranger.py && python -m dh expandir
Features das subclasses = ran.py (passada 1). Régua comum: Extra Attack, linha sem magia + linha Hunter's Mark
(+1d6 por acerto, 0,5 espaço de 1º por luta), espaços de magia do Ranger, saves For/Des.
Posição: atiradores = arco longo, Archery, couro batido, Des>Con>Sab, feat Sharpshooter (as progressões rpgbot-ranger-*
são um chassi genérico com Sharpshooter, não builds do RPGBot: feat natural). Pets de perto:
  Drakewarden = striker de glaive (GWF, meia-armadura), For>Des>Con>Sab; feats GWM ou Polearm Master (só a reação:
    a ação bônus é do drake).
  Beast Master = defensor com espada longa + escudo (Dueling, meia-armadura), For>Des>Con>Sab; feat Sentinel
    (segura a linha com a fera; a ação bônus é da fera, então PAM/GWM perdem metade do valor).
"""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402
from marcial import A  # noqa: E402

SL = {7: {"1": 4, "2": 3}, 11: {"1": 4, "2": 3, "3": 3}}
HM = {"espacos": {"1": 0.5}}
ORD_ARCO = ('des', 'con', 'sab', 'for', 'int', 'car')
ORD_PERTO = ('for', 'des', 'con', 'sab', 'car', 'int')
REAC = [{"uso": "ataque de oportunidade", "fracao": 0.5, "eixos": ["dano", "controle"]}]
URL = "https://rpgbot.net/dnd5/characters/classes/ranger/subclasses/"

# sub: (nome, posição, perto?, feats)
SUBS = {
    'hunter': ('Hunter', 'atirador', False, ('Sharpshooter',)),
    'gloom-stalker': ('Gloom Stalker', 'atirador', False, ('Sharpshooter',)),
    'horizon-walker': ('Horizon Walker', 'atirador', False, ('Sharpshooter',)),
    'monster-slayer': ('Monster Slayer', 'atirador', False, ('Sharpshooter',)),
    'fey-wanderer': ('Fey Wanderer', 'atirador', False, ('Sharpshooter',)),
    'swarmkeeper': ('Swarmkeeper', 'atirador', False, ('Sharpshooter',)),
    'drakewarden': ('Drakewarden', 'striker', True, ('Great Weapon Master', 'Polearm Master')),
    'beast-master': ('Beast Master (Primal Companion)', 'defensor', True, ('Sentinel',)),
}


def fatia(L, sub, feat=None):
    nome, pos, perto, _ = SUBS[sub]
    ordem = ORD_PERTO if perto else ORD_ARCO
    s = C.atributos('ranger', L, ordem, feat=feat); m = C.mods(s); P = C.pb(L)
    n = 2; bm = P + m['sab']                                   # ataque de magia (pets)
    poder = {"poder": [-5, 10]} if feat in ('Sharpshooter', 'Great Weapon Master') else {}
    if sub == 'drakewarden':
        st = m['for']; b = P + st; arma = ('1d10', f"{st}+0.8")   # glaive, GWF ≈ +0,8 no d10
        ca = 15 + min(2, m['des']); equip = "glaive, Great Weapon Fighting, meia-armadura"
    elif sub == 'beast-master':
        st = m['for']; b = P + st; arma = ('1d8', f"{st}+2")      # espada longa, Dueling
        ca = 15 + min(2, m['des']) + 2; equip = "espada longa + escudo, Dueling, meia-armadura"
    else:
        st = m['des']; b = P + st + 2; arma = ('1d8', f"{st}")    # arco longo, Archery
        ca = 12 + st; equip = "arco longo, Archery, couro batido"

    def atk(nn, marca, extra='', **k):
        return A(nn, b, arma[0], arma[1], ('+1d6' if marca else '') + extra, **poder, **k)

    pt, extra_at, txt = [], [], ''
    saves = C.sv(L, m, ('for', 'des'))
    if sub == 'hunter':
        pt = [{"dano": "1d8", "nota": "Colossus Slayer (alvo já ferido, 1×/turno)"}]
        txt = "Colossus Slayer (3); Multiattack Defense/Escape the Horde (7) e Volley (11) não modelados."
    elif sub == 'gloom-stalker':
        extra_at = [lambda mc: atk(0.25, mc, '+1d8', nota="Dread Ambusher: ataque extra +1d8 no 1º round")]
        if L >= 7: saves['sab'] = m['sab'] + P                                   # Iron Mind
        if L >= 11: extra_at.append(lambda mc: atk(0.5, mc, nota="Stalker's Flurry: ataque extra após errar (≈0,5/turno)"))
        txt = "Dread Ambusher (3); Iron Mind (7); Stalker's Flurry (11); Umbral Sight não modelado."
    elif sub == 'horizon-walker':
        pt = [{"dano": "1d8" if L < 11 else "2d8", "nota": "Planar Warrior (ação bônus, 1 acerto/turno, força)"}]
        if L >= 11: extra_at = [lambda mc: atk(1, mc, nota="Distant Strike: 3º ataque contra outra criatura")]
        txt = "Planar Warrior (3; 2d8 no 11); Distant Strike (11) com o 3º ataque sempre; Ethereal Step (7) e o teleporte não modelados."
    elif sub == 'monster-slayer':
        pt = [{"dano": "1d6", "nota": "Slayer's Prey (1×/turno no alvo marcado)"}]
        txt = "Slayer's Prey (3); Supernatural Defense (7) e Magic-User's Nemesis (11) não modelados."
    elif sub == 'fey-wanderer':
        pt = [{"dano": "1d4" if L < 11 else "1d6", "nota": "Dreadful Strikes (psíquico, 1×/turno)"}]
        txt = "Dreadful Strikes (3; 1d6 no 11); Otherworldly Glamour, Beguiling Twist (7) e Fey Reinforcements (11) não modelados."
    elif sub == 'swarmkeeper':
        pt = [{"dano": "1d6" if L < 11 else "1d8", "nota": "Gathered Swarm (1×/turno)"}]
        txt = "Gathered Swarm (3; 1d8 no 11); empurrão do enxame, Writhing Tide (7) e Mighty Swarm (11) não modelados."
    elif sub == 'drakewarden':
        extra_at = [lambda mc: A(0.75, bm, '1d6', P, "+1d6", nota="Drake: mordida (ação bônus; round 1 vai na Hunter's Mark)")]
        txt = "Drake Companion (3); Bond of Fang and Scale (7: +1d6 na mordida, montaria não modelada); Drake's Breath e drake maior (11) não modelados."
    elif sub == 'beast-master':
        nb = 0.75 if L < 11 else 1.5
        extra_at = [lambda mc: A(nb, bm, '1d8', 2 + P, nota="Primal Companion (Beast of the Land; ação bônus; 2 ataques no 11)")]
        txt = "Primal Companion (Beast of the Land); Exceptional Training (7) e Bestial Fury (11). Charge, Share Spells e o corpo da fera na defesa não modelados."

    reac, fontes, aten = None, [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}], {}
    if feat == 'Polearm Master':
        extra_at.append(lambda mc: atk(0.5, mc, nota="ataque de oportunidade do Polearm Master (reação em 50% dos rounds)"))
        reac = REAC; txt += " Polearm Master: só a reação (a ação bônus é do drake)."
    if feat == 'Sentinel':
        extra_at.append(lambda mc: atk(0.5, mc, nota="ataque de oportunidade (Sentinel), reação em 50% dos rounds"))
        reac = [dict(REAC[0], uso="ataque de oportunidade (Sentinel)")]
        fontes = [{"tipo": "sentinela", "nome": "Corpo (Sentinel)", "bonus": b}] + fontes
        aten = {"hard": {"sentinela": b}}
        txt += " Sentinel: OA em 50% dos rounds + sentinela no controle."
    if feat == 'Sharpshooter':
        txt += " Sharpshooter: −5/+10 escolhido pelo motor; ignorar cobertura e alcance não modelados."

    def dano(mc):
        x = {"ataques": [atk(n, mc)] + [f(mc) for f in extra_at]}
        if pt: x["por_turno"] = pt
        return x
    ctl = {"atencao": C.atencao(pos, **aten), "fontes": fontes}
    arm = equip.split(',')[0]
    cd = 8 + P + m['sab']
    # M2 (23/11): pet como corpo (o ataque dele já está no dano); Primal Companion CA 13+PB, Drake CA 14+PB, PV 5+5×nível
    pet = ([{"nome": "Primal Companion (Beast of the Land)", "quantidade": 1, "pv": 5 + 5 * L, "ca": 13 + P}] if sub == 'beast-master'
           else [{"nome": "Drake Companion", "quantidade": 1, "pv": 5 + 5 * L, "ca": 14 + P}] if sub == 'drakewarden' else [])
    l1 = {"id": "principal", "hipotese": f"{arm} sem magia", "dano": dano(False), "defesa": {}, "controle": ctl, "saves": {}}
    dm = dict(dano(True), concentracao="hunters_mark")                      # M2: a Marca é concentração
    l2 = {"id": "marca", "hipotese": "Hunter's Mark (1 hora: 0,5 espaço de 1º por luta)", "dano": dm, "defesa": {},
          "controle": ctl, "saves": {}, "gasta": HM}
    # M2: Favored Foe (Tasha's): 1d4 (1d6 do 6) uma vez por turno no alvo marcado; concentração; PB usos/descanso longo
    ff = dano(False); ff["por_turno"] = ff.get("por_turno", []) + [{"dano": "1d4" if L < 6 else "1d6", "nota": "Favored Foe (1×/turno)"}]
    ff["concentracao"] = "favored_foe"
    l3 = {"id": "inimigo-favorito", "hipotese": "Favored Foe (sem espaço: PB usos por descanso longo, 1 por luta)",
          "dano": ff, "defesa": {}, "controle": ctl, "saves": {}, "gasta": {"favored_foe": 1}}
    # M2: Ensnaring Strike (1º, concentração): contido no acerto, save de For
    l4 = {"id": "enredar", "hipotese": "Ensnaring Strike no 1º acerto (1 espaço de 1º), depois ataques normais",
          "dano": dano(False), "defesa": {}, "saves": {}, "gasta": {"espacos": {"1": 1}},
          "controle": dict(ctl, fontes=[{"tipo": "condicao_no_acerto", "nome": "Ensnaring Strike", "efeito": "ensnaring_strike",
                                          "cd": cd, "bonus": [b] * n, "usos": 1}] + ctl["fontes"])}
    linhas = [l1, l2, l3, l4]
    if L >= 9:   # M2: Conjure Animals (3º, concentração): 8 lobos (CR 1/4), Pack Tactics ≈ vantagem em 80% dos ataques
        l5 = {"id": "conjurar-animais", "hipotese": "Conjure Animals (8 lobos; 1 espaço de 3º), ataques normais",
              "dano": dano(False), "defesa": {}, "controle": ctl, "saves": {}, "gasta": {"espacos": {"3": 1}},
              "invocacoes": [{"nome": "Conjure Animals (8 lobos)", "quantidade": 8, "pv": 11, "ca": 13,
                              "ataque": {"n": 1, "bonus": 4, "dano": "2d4+2", "vantagem": 0.8}}]}
        linhas.append(l5)
    # M6 (23/11): terreno: Spike Growth (2º, concentração) do 5; Plant Growth (3º, sem concentração) do 9
    if L >= 5:
        linhas.append({"id": "terreno-espinhos", "hipotese": "Spike Growth (1 espaço de 2º), ataques normais", "dano": dano(False),
                       "defesa": {}, "saves": {}, "gasta": {"espacos": {"2": 1}},
                       "controle": dict(ctl, fontes=[{"tipo": "area", "nome": "Spike Growth", "magia": "spike_growth", "cd": cd}] + ctl["fontes"])})
    if L >= 9:
        linhas.append({"id": "terreno-plantas", "hipotese": "Plant Growth (1 espaço de 3º, sem concentração), ataques normais",
                       "dano": dano(False), "defesa": {}, "saves": {}, "gasta": {"espacos": {"3": 1}},
                       "controle": dict(ctl, fontes=[{"tipo": "area", "nome": "Plant Growth", "magia": "plant_growth", "cd": cd}] + ctl["fontes"])})
    for l in linhas:
        if reac: l['reacao'] = reac
        if pet: l['invocacoes'] = pet + l.get('invocacoes', [])
    corpo = {"ca": ca, "pv": C.hp(10, L, m['con']), "saves": {"sv": saves, "ataques": n}}
    return {"corpo": corpo, "recursos": {"espacos": dict(SL[L]), "outros": {"favored_foe": {"qtd": P, "volta": "longo"}}}, "linhas": linhas,
            "_texto": f"atributos {s}. {txt}", "_equip": equip}


NM = ("Troca de alvo da Hunter's Mark (ação bônus); magias utilitárias (Pass without Trace etc.); dano do Spike Growth; "
      "Natural Explorer; vantagem de criaturas Grandes contra o Ensnaring Strike; ")   # M2 (23/11): o resto entrou
for sub, (nome, pos, perto, feats) in SUBS.items():
    for feat in (None,) + feats:
        fat = {L: fatia(L, sub, feat) for L in C.NIV}
        equip = fat[7].pop('_equip'); fat[11].pop('_equip')
        ft = f"; {feat} no 4" if feat else "; sem feat"
        if sub == 'drakewarden' and feat:
            ft += " (natural de quem luta de perto com arma de haste; a ação bônus fica com o drake)"
        if sub == 'beast-master' and feat:
            ft += " (natural do defensor de escudo; a ação bônus fica com a fera)"
        C.escrever('ranger', sub, pos, fat, build=f"Ranger ({nome}), {pos}: {equip}{ft}",
                   desc={"resumo": f"Chassi do {nome}: Ranger {pos} com Hunter's Mark e a feature de dano da subclasse.",
                         "estrategia": "Ataca todo round; Hunter's Mark nas lutas que o plano escolher.",
                         "nao_modelado": NM + fat[11]['_texto'].split('. ', 1)[1]},
                   feat=feat, url=URL)
