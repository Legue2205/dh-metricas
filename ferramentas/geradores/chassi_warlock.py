"""CHASSI do Warlock (mini-mutirão de 22/11/2026): um chassi-warlock-<patrono> por subclasse do gabarito, fatias 7 e 11,
só a variante sem feat (Warlock é tratado como conjurador: quebra de concentração não modelada).
Rodar da raiz: python ferramentas/geradores/chassi_warlock.py && python -m dh expandir

Mesma régua para todos (convenções "Warlock" e "Chassi" em calibracao/convencoes-passada1.md):
  - atributos Car > Con > Des > Sab > Int > For (compra padrão +2/+1; ASIs no Carisma, depois Con);
  - Eldritch Blast + Agonizing Blast, Hex (0,5 espaço/luta), espaços de pacto (voltam no descanso curto),
    Mystic Arcanum (Mass Suggestion) no 11;
  - Pact of the Tome para todos (Book of Shadows sem mecânica no motor), exceto Hexblade = Pact of the Blade;
  - invocações base: Agonizing Blast, Armor of Shadows (CA 13+Des), Repelling Blast, Devil's Sight (+ uma no 9);
    Hexblade: Thirsting Blade (5) no lugar de Armor of Shadows (já usa armadura média + escudo);
  - lista base: Hold Person, Hypnotic Pattern, Banishment, Hold Monster, Synaptic Static, Shatter, Summon
    Shadowspawn/Aberration. A subclasse soma só o que a lista expandida/features dela dão (mesmas funções de wlk.py).
Posição: Hexblade = striker (espada longa do pacto + escudo, meia-armadura); os outros = retaguarda.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chassi as C  # noqa: E402
import wlk as W  # noqa: E402  (aplica os espaços de pacto em wiz.fatia)
from wiz import fatia, AT, U, PF  # noqa: E402

ORDEM = ('car', 'con', 'des', 'sab', 'int', 'for')
URL = "https://rpgbot.net/dnd5/characters/classes/warlock/subclasses/"
# Extras de controle da lista expandida (além do que wlk.sub_cfg já dá ao Great Old One).
CTRL_EXTRA = {'archfey': [(3, PF)], 'undead': [(3, PF)]}


def fatia_ch(L, sub):
    s = C.atributos('warlock', L, ORDEM); m = C.mods(s); c = m['car']
    cd = W.dc(L, c); a = W.at(L, c); pl = str(W.PACTO[L][1])
    pos = 'striker' if sub == 'hexblade' else 'retaguarda'
    ca = 15 + min(m['des'], 2) + 2 if sub == 'hexblade' else 13 + m['des']    # meia-armadura + escudo / Armor of Shadows
    o = W.sub_cfg(sub, L, c, cd, a)
    if sub in CTRL_EXTRA: o['ctrl'] = W.ctrl_pad(L, cd, CTRL_EXTRA[sub])
    cant = o.get('cant') or (lambda n: W.eb(L, a, c, n))
    cant_hex = o.get('cant_hex', lambda n: W.eb(L, a, c, n, True))
    f = fatia(L, L, 0, m, ('sab', 'car'), ca, C.hp(8, L, m['con']), cant, o.get('ctrl', W.ctrl_pad(L, cd)), None,
              o.get('areas', [W.SHAT(cd)]), o.get('inv', W.inv_pad(L, a)), o.get('extra', []), shield=False,
              mage_armor=False, papel=o.get('papel', 'conjurador'), front=o.get('front', False),
              ctl_extra=o.get('ctl_extra', ()))
    f['linhas'].insert(1, dict(id="hex", herda="principal", hipotese="Hex (1 hora: 0,5 espaço por luta) no ataque principal",
                               dano=cant_hex(1.0), gasta={"espacos": {pl: 0.5}}))
    if L >= 11:   # Mystic Arcanum (6º, 1/descanso longo) = Mass Suggestion
        mf = U("Mass Suggestion (Mystic Arcanum)", "mass_suggestion", cd, 6, area=True)['f']
        f['linhas'].append(dict(id="arcano", herda="principal", hipotese="Mystic Arcanum: Mass Suggestion no pico",
                                dano=cant(0.75), controle={"atencao": AT(), "fontes": [mf]}, gasta={"arcano": 1}))
        o.setdefault('outros', {})['arcano'] = {"qtd": 1, "volta": "longo"}
    n0 = f['linhas'][0]['dano']['ataques'][0]['n']
    for l in list(f['linhas']):   # Hex junto das linhas sem concentração
        if l['id'] in ('area', 'arcano'):
            fr = l['dano']['ataques'][0]['n'] / n0; g = json.loads(json.dumps(l.get('gasta', {})))
            g.setdefault('espacos', {}); g['espacos']['9'] = 0.5   # marcador; W.ajusta junta no nível do pacto
            f['linhas'].append(dict(l, id=l['id'] + '+hex', hipotese=l.get('hipotese', l['id']) + ' + Hex',
                                    dano=cant_hex(fr), gasta=g))
    for kk, v in o.get('corpo', {}).items(): f['corpo'][kk] = v
    if o.get('outros'): f['recursos']['outros'] = o['outros']
    for l in f['linhas']:
        for kk, v in o.get('todas', {}).items():
            if not l.get(kk): l[kk] = json.loads(json.dumps(v))
        l.setdefault('hipotese', l['id'])
        if l.get('controle', {}).get('atencao'):    # posição do chassi (só muda a atenção)
            l['controle']['atencao'] = C.atencao(pos)
        if l['id'] == 'principal': l.pop('herda', None)
    f = W.ajusta(f, L)
    f['linhas'][0]['hipotese'] = 'só o ataque à vontade (anel interno)'
    f['_texto'] = f"Warlock {L}; atributos {s}; pacto {W.PACTO[L][0]}×{W.PACTO[L][1]}º; CA {ca}." + o.get('txt', '')
    return pos, f


NM_BASE = ("Pact of the Tome (Book of Shadows: truques extras); Repelling Blast, Devil's Sight e a invocação do 9; "
           "Hunger of Hadar; Armor of Agathys; Counterspell; Misty Step; Darkness+Devil's Sight")
NM_BLADE = ("Pact of the Blade (troca de arma); Agonizing Blast/EB como alternativa à distância; Devil's Sight; "
            "Counterspell; Misty Step")
SUBS = {
    'archfey': ("Archfey", "Fey Presence, Misty Escape, Beguiling Defenses; Faerie Fire/Sleep/Dominate Person da lista"),
    'celestial': ("Celestial", "Radiant Soul (EB é de força), Celestial Resilience; Guiding Bolt/Flaming Sphere/Flame Strike"),
    'fathomless': ("Fathomless", "Gift of the Sea, Oceanic Soul, Fathomless Plunge; Guardian Coil como reduz_dano 4,5"),
    'fiend': ("Fiend", "Dark One's Own Luck, Fiendish Resilience; Wall of Fire"),
    'genie': ("Genie (Efreeti)", "Bottled Respite, Elemental Gift (voo); listas Dao/Djinni/Marid"),
    'great-old-one': ("Great Old One", "Awakened Mind, Thought Shield; Entropic Ward como desvantagem 1/descanso curto "
                                       "(a vantagem seguinte não modelada)"),
    'hexblade': ("Hexblade", "Hex Warrior (já no Carisma na arma), Accursed Specter, Armor of Hexes; crítico em 19 do "
                             "Curse; Shield/Wrathful Smite da lista"),
    'undead': ("Undead", "Form of Dread (medo no acerto), Grave Touched, Necrotic Husk; Cloudkill"),
    'undying': ("Undying", "Among the Dead, Defy Death, Undying Nature (o patrono não muda números no motor)"),
}

if __name__ == '__main__':
    for sub, (nome, nm) in SUBS.items():
        fat = {}
        for L in C.NIV:
            pos, fat[L] = fatia_ch(L, sub)
        if sub == 'hexblade':
            b = ("Warlock (Hexblade), striker: Pact of the Blade, espada longa + escudo, meia-armadura; Car>Con>Des; "
                 "Thirsting Blade no 5; sem feat")
            res = "Chassi do Hexblade: espada do pacto com Carisma, Hexblade's Curse e Hex no alvo principal, na linha de frente."
        else:
            b = (f"Warlock ({nome}), retaguarda: Pact of the Tome, Eldritch Blast + Agonizing Blast, Armor of Shadows; "
                 "Car>Con>Des; sem feat")
            res = f"Chassi do {nome}: Eldritch Blast com Agonizing Blast e Hex, espaços de pacto; muda só o que o patrono dá."
        desc = {"resumo": res,
                "estrategia": "Hex no início do dia (cobre ~2 lutas); controle (Hold Person, Hypnotic Pattern, Banishment, "
                              "Hold Monster, Synaptic Static), área ou invocação no espaço de pacto; Mass Suggestion no 11.",
                "nao_modelado": nm + "; " + (NM_BLADE if sub == 'hexblade' else NM_BASE)}
        C.escrever('warlock', sub, pos, fat, build=b, desc=desc, url=URL)
