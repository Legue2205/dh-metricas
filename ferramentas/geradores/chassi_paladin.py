"""Chassi do Paladin (mini-mutirão de 22/11): os 8 juramentos do gabarito, sem feat e com o feat da subclasse.
Rodar da raiz: python ferramentas/geradores/chassi_paladin.py && python -m dh expandir
Régua comum (convenções do Paladin): smites de cada círculo, Bless, Lay on Hands, Aura of Protection, ataque de
oportunidade 0,5, Channel 1/descanso curto. Features das subclasses = as funções/números de pal.py.
Posições: striker = espadão + GWF + placas (18); defensor = espada longa + escudo + Dueling + placas (20);
atirador = arco longo + couro batido (Defense; Archery só pelo Fighting Initiate)."""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402
import pal  # noqa: E402
from marcial import A, ctrl  # noqa: E402

STR = ('for', 'car', 'con', 'sab', 'des', 'int')
DEX = ('des', 'car', 'con', 'sab', 'for', 'int')
PAPEL = {'striker': 'striker', 'defensor': 'tank', 'atirador': 'atirador'}

# sub: posição, arma ('espadao'|'longa'|'arco'), feats (1º não racial da build do RPGBot; 2º só onde indicado)
SUBS = {
    'vengeance':  ('striker', 'espadao', ['Polearm Master']),
    'devotion':   ('striker', 'espadao', ['Metamagic Adept', 'Great Weapon Master']),
    'conquest':   ('defensor', 'longa', ['Shield Master']),
    'ancients':   ('atirador', 'arco', ['Fighting Initiate']),
    'crown':      ('defensor', 'longa', ['Resilient']),
    'glory':      ('striker', 'espadao', ['Resilient']),
    'redemption': ('defensor', 'longa', ['Telekinetic']),
    'watchers':   ('striker', 'espadao', ['Skill Expert']),
}
MEIO = {'Resilient': 'con', 'Telekinetic': 'car', 'Skill Expert': 'for', 'Metamagic Adept': None}


def fatia(sub, L, feat=None):
    pos, arma, _ = SUBS[sub]
    ordem = DEX if arma == 'arco' else STR
    s = C.atributos('paladin', L, ordem, feat=feat, meio_feat=MEIO.get(feat)); m = C.mods(s)
    P = C.pb(L); cha = m['car']; con = m['con']; cd = 8 + P + cha; n = 2
    ex = '+1d8' if L >= 11 else ''
    pam = feat == 'Polearm Master'; gwm = {"poder": [-5, 10]} if feat == 'Great Weapon Master' else {}
    if arma == 'arco':
        at = m['des']; b = P + at + (2 if feat == 'Fighting Initiate' else 0)
        ca = 12 + min(at, 5) + 1                                  # couro batido + Defense
    else:
        at = m['for']; b = P + at
        ca = 20 if arma == 'longa' else 18

    def atk(bonus=0, frac=1.0, vant=0.0, de='', ba=1.0, extra_n=0.0):
        if arma == 'arco':
            return {"ataques": [A(n * frac + extra_n, b + bonus, '1d8', at, de, vantagem=vant, nota="arco longo")]}
        if arma == 'longa':
            a = [A(n * frac + extra_n, b + bonus, '1d8', at + 2, ex + de, vantagem=vant, nota="espada longa (Dueling)")]
            oa = A(0.5, b, '1d8', at + 2, ex, nota="ataque de oportunidade (reação em 50%)")
        elif pam:
            a = [A(n * frac + extra_n, b + bonus, '1d10', at, '+0.8' + ex + de, vantagem=vant, nota="glaive (GWF)"),
                 A(ba, b + bonus, '1d4', at, '+0.5' + ex + de, vantagem=vant, nota="cabo (Polearm Master, ação bônus)")]
            oa = A(0.5, b, '1d10', at, '+0.8' + ex, nota="ataque de oportunidade (Polearm Master, reação em 50%)")
        else:
            a = [A(n * frac + extra_n, b + bonus, '2d6', at, '+1.33' + ex + de, vantagem=vant, nota="espadão (GWF)", **gwm)]
            oa = A(0.5, b, '2d6', at, '+1.33' + ex, nota="ataque de oportunidade (reação em 50%)", **gwm)
        return {"ataques": a + [oa]}

    ext = []; area = None
    hold = lambda: dict(id='controle', hip='Hold Person no round 1 (ação), ataques nos rounds 2–4', dano=atk(frac=0.75),
                        gasta={"espacos": {"2": 1}},
                        controle=ctrl('tank', [{"tipo": "alvo_unico", "nome": "Hold Person", "cd": cd, "slots": [2],
                                                "magias": ["hold_person"], "modo": "melhor"}]))
    haste = lambda: dict(id='haste', hip='Haste em si (3º) no round 1 (ação): +1 ataque e +2 de CA nos rounds 2–4',
                         dano=atk(frac=0.75, extra_n=0.75), defesa={"ca": ca + 2}, gasta={"espacos": {"3": 1}})
    if sub == 'vengeance':
        ext += [dict(id='voto', hip='Vow of Enmity (ação bônus no round 1): vantagem contra o alvo a luta toda',
                     dano=atk(vant=1.0, ba=0.75), gasta={"canal": 1}),
                dict(id='marca', hip="Hunter's Mark (1 hora: 0,5 espaço de 1º por luta; ação bônus no round 1)",
                     dano=atk(de='+1d6', ba=0.75), gasta={"espacos": {"1": 0.5}}), hold()]
        if L >= 9: ext.append(haste())
    elif sub == 'devotion':
        ext.append(dict(id='arma-sagrada', hip='Sacred Weapon (ação no round 1: +Car no acerto a luta toda)',
                        dano=atk(bonus=max(cha, 1), frac=0.75), gasta={"canal": 1}))
    elif sub == 'conquest':
        aoc = [{"n": 0.75, "cd": cd, "save": "Sab", "dano": str(L // 2), "meio": False, "nota": "Aura of Conquest no amedrontado"}]
        com = lambda dn: dict(dn, com_save=dn.get('com_save', []) + aoc)
        ext += [dict(id='conquista', hip='Conquering Presence no round 1 (ação), ataques nos rounds 2–4',
                     dano=com(atk(frac=0.75)), gasta={"canal": 1},
                     controle=ctrl('tank', [{"tipo": "area", "nome": "Conquering Presence", "magia": "conquering_presence",
                                             "cd": cd, "so_corpo_a_corpo": True}])),
                dict(id='agathys', hip='Armor of Agathys (1º) antes da luta: 5 PV temporários', dano=atk(),
                     defesa={"pvt_luta": 5}, gasta={"espacos": {"1": 1}}),
                dict(id='arma-espiritual', hip='Spiritual Weapon (2º; ação bônus, rounds 2–4)',
                     dano={"ataques": atk()['ataques'] + [A(0.75, P + cha, '1d8', cha, nota="Spiritual Weapon")]},
                     gasta={"espacos": {"2": 1}})]
        if L >= 9:
            ext.append(dict(id='medo', hip='Fear (3º) no round 1 (ação), ataques nos rounds 2–4', dano=com(atk(frac=0.75)),
                            gasta={"espacos": {"3": 1}},
                            controle=ctrl('tank', [{"tipo": "area", "nome": "Fear", "magia": "fear", "cd": cd}])))
    elif sub == 'ancients':
        ext.append(dict(id='enredar', hip='Ensnaring Strike (ação bônus) no 1º acerto: impedido até escapar',
                        dano=atk(), gasta={"espacos": {"1": 1}},
                        controle=ctrl('atirador', [{"tipo": "alvo_unico", "nome": "Ensnaring Strike", "cd": cd, "slots": [1],
                                                    "magias": ["ensnaring_strike"], "modo": "melhor"}])))
    elif sub == 'crown' and L >= 9:
        g = atk(frac=0.75)
        g['com_save'] = [{"n": 0.75, "cd": cd, "save": "Sab", "dano": "3d8", "meio": True, "nota": "Spirit Guardians no alvo"}]
        ext.append(dict(id='guardioes', hip='Spirit Guardians (3º) no round 1, ataques nos rounds 2–4', dano=g,
                        gasta={"espacos": {"3": 1}},
                        area=[{"nome": "Spirit Guardians (3º)", "tipo": "aura", "alvos": 3, "dano": "3d8", "cd": cd, "metade": True}]))
    elif sub == 'glory':
        ext.append(dict(id='inspirador', hip='Inspiring Smite: 1 Divine Smite de 1º e 2d8 + nível de PV temporários para um aliado',
                        dano=dict(atk(), por_luta=[{"usos": 1, "dano": "2d8", "nota": "Divine Smite (1º)"}]),
                        gasta={"canal": 1, "espacos": {"1": 1}},
                        suporte=[{"nome": "Inspiring Smite (PV temporários)", "lado": "def", "modelo": "pv_temporario",
                                  "usos_luta": 1, "alvos": 1, "pv": 9 + L}]))
        if L >= 9: ext.append(haste())
    elif sub == 'redemption':
        ext.append(hold())
        if L >= 9:
            ext.append(dict(id='padrao-hipnotico', hip='Hypnotic Pattern (3º) no round 1 (ação), ataques nos rounds 2–4',
                            dano=atk(frac=0.75), gasta={"espacos": {"3": 1}},
                            controle=ctrl('tank', [{"tipo": "area", "nome": "Hypnotic Pattern", "magia": "hypnotic_pattern", "cd": cd}])))
    profs = ('sab', 'car') + (('con',) if feat == 'Resilient' else ())
    nat = n + (1 if pam else 0)
    corpo = dict(ca=ca, pv=C.hp(10, L, con), saves=pal.saves_pal(L, m, L, cha, profs, sub=sub, ataques=nat))
    fat = pal.montar(L, L, atk, corpo, pal.esp_pal(L), cha, papel=PAPEL[pos], smite=arma != 'arco', extras=ext,
                     outros=pal.canal(L, P), area=area)
    att = C.atencao(pos)
    for l in fat['linhas']:
        front = l['id'].startswith('guardioes')
        l['controle']['atencao'] = dict(att, front=True) if front else dict(att)
    fat['_texto'] = f"atributos {s}; CA {ca}"
    return fat


ARMA_TXT = {'espadao': 'espadão, GWF, placas', 'longa': 'espada longa + escudo, Dueling, placas',
            'arco': 'arco longo, Defense, couro batido'}
NM = {
    'vengeance': "Relentless Avenger, Abjure Enemy, Misty Step.",
    'devotion': "Purity of Spirit, Turn the Unholy, Protection from Evil, Sanctuary.",
    'conquest': "Guided Strike, Bestow Curse, Scornful Rebuke; retorno do Armor of Agathys.",
    'ancients': "Nature's Wrath, Turn the Faithless, Moonbeam, Misty Step; "
                "Improved Divine Smite sem uso à distância; Harness Divine Power (opcional) não usado na régua.",
    'crown': "Divine Allegiance, Champion Challenge, Turn the Tide, Compelled Duel, Warding Bond, Command.",
    'glory': "Peerless Athlete (agarrar/empurrar), Aura of Alacrity, Protection from Energy.",
    'redemption': "Aura of the Guardian, Rebuke the Violent, Emissary of Peace, Sleep, Calm Emotions, Counterspell.",
    'watchers': "Watcher's Will (vantagem em saves mentais), Aura of the Sentinel (iniciativa), Abjure the Extraplanar, "
                "Moonbeam, Counterspell.",
}
NM_FEAT = {
    'Polearm Master': "", 'Great Weapon Master': "", 'Fighting Initiate': " Fighting Initiate = estilo Archery (+2 no acerto).",
    'Metamagic Adept': " Metamagic Adept: sem uso modelado sem truques/magias de Sorcerer (diferença ~zero de propósito).",
    'Shield Master': " Shield Master (derrubar com o escudo; escudo no save de Des): não modelado, diferença zero de propósito.",
    'Resilient': " Resilient (Con): +1 Con e proficiência em saves de Con.",
    'Telekinetic': " Telekinetic: +1 Car; empurrão na ação bônus não modelado.",
    'Skill Expert': " Skill Expert: só o +1 de For conta.",
}
COMUM = " Comum: Find Steed, curas fora de luta, smite guardado para o crítico, upcast de Bless."

if __name__ == '__main__':
    for sub, (pos, arma, feats) in SUBS.items():
        for feat in [None] + feats:
            C.escrever('paladin', sub, pos, {L: fatia(sub, L, feat) for L in C.NIV},
                       build=f"Paladin (Oath of {sub.title()}), {pos}: {ARMA_TXT[arma]}" + (f"; {feat} no 4" if feat else "; sem feat"),
                       desc={"resumo": f"Chassi do Oath of {sub.title()}: régua comum do Paladin + features do juramento "
                                       f"({pos}). Feat da subclasse = 1º feat não racial da build do RPGBot.",
                             "nao_modelado": NM[sub] + (NM_FEAT.get(feat, '') if feat else '') + COMUM},
                       feat=feat, url=f"https://rpgbot.net/dnd5/characters/classes/paladin/subclasses/oath-of-{'the-' if sub in ('ancients', 'crown', 'watchers') else ''}{sub}/")
