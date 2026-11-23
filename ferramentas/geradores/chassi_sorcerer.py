"""Chassi do Sorcerer (mini-mutirão 22/11/2026). Rodar da raiz: python ferramentas/geradores/chassi_sorcerer.py
Conjurador pleno: só a variante SEM feat. Todas as origens na retaguarda.
Régua comum: Car > Con > Des; Fire Bolt; Mage Armor (salvo Draconic Resilience) e Shield; Flexible Casting pela
convenção atual (TODOS os pontos viram espaços, guloso até o 5º — pendência conhecida, não mudada aqui).
Lista base (magias conhecidas): 7 = Shield, Mage Armor, Web, Hold Person, Hypnotic Pattern, Fireball, Polymorph;
11 = + Hold Monster, Synaptic Static, Cone of Cold. A origem só acrescenta as magias/feat. que ela dá.
"""
import json
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402
import wiz as W  # noqa: E402
from wiz import fatia, U, HYP, WEB, HP_, HM, SYN, WOF, EBT, FB, area_sp, summon, SH, RE  # noqa: E402

CUSTO = {1: 2, 2: 3, 3: 5, 4: 6, 5: 7}


def esp_sor(cl, sp, mage_armor=True):
    """Igual a sor.esp_sor (convenção da passada 1): todos os pontos viram espaços, guloso até o 5º."""
    e = dict(W.SL[cl]); top = min(5, max(int(k) for k in e)); r = sp
    while r >= 2:
        s = max(x for x in range(1, top + 1) if CUSTO[x] <= r)
        e[str(s)] = e.get(str(s), 0) + 1; r -= CUSTO[s]
    if mage_armor: e["1"] -= 1
    return e


W.espacos = esp_sor
ORDEM = ('car', 'con', 'des', 'sab', 'int', 'for')
BLESS = {"nome": "Bless", "lado": "of", "modelo": "bonus_continuo", "alvos": 3, "bonus": 2.5, "concentracao": "bless"}
POLY = lambda cd: U("Polymorph", "polymorph", cd, 4)
BLIND = lambda cd: U("Blindness/Deafness", "blindness", cd, 2)
CONE = lambda cd: area_sp("Cone of Cold", 6, "8d8", cd, 5)          # cone de 60 pés = 6 alvos (DMG)
BASE_NM = ("Metamagia além do Quickened (Twinned, Heightened…; M7: pontos convertidos em espaços pelo livro-caixa); "
           "Counterspell; Haste; magias conhecidas além da lista base.")


def fb(L, a, n, extra=0):
    return {"ataques": [{"n": n, "bonus": a, "dano": f"{W.k(L)}d10" + (f"+{extra}" if extra else ""),
                         "nota": "Fire Bolt" + (" + Elemental Affinity" if extra else "")}]}


def construct(lv, a):   # Summon Construct (Tasha): CA 13+nível, PV 40+15/nível acima do 4º, pancada 1d8+4+nível
    return {"nome": f"Summon Construct ({lv}º)", "quantidade": 1, "pv": 40 + 15 * (lv - 4), "ca": 13 + lv,
            "ataque": {"n": lv // 2, "bonus": a, "dano": f"1d8+{4 + lv}"}}


def montar(sub, L):
    s = C.atributos('sorcerer', L, ORDEM); m = C.mods(s); p = C.pb(L); c = m['car']
    cd = 8 + p + c; a = p + c
    drac = sub == 'draconic'
    ea = c if drac and L >= 6 else 0                                  # Elemental Affinity (fogo)
    ca = 13 + m['des']                                                # Mage Armor ou Draconic Resilience
    pv = C.hp(6, L, m['con']) + (L if drac else 0)
    ctrl = [WEB(cd), HP_(cd), HYP(cd), POLY(cd)] + ([U("Psychic Lance", "psychic_lance", cd, 4)] if L >= 7 else []) + \
        ([HM(cd), SYN(cd)] if L >= 11 else [])   # M6b (23/11): Psychic Lance
    ar = [FB(cd, ea)] + ([CONE(cd)] if L >= 11 else [])
    inv = None; extra = []; top = 4 if L < 11 else 6
    if sub == 'aberrant-mind':
        ctrl.append(EBT(cd)); inv = dict(i=summon('aberration', top, a), slot=top)
    if sub == 'clockwork-soul':
        inv = dict(i=construct(top, a), slot=top)
        if L >= 9: ctrl.append(WOF(cd))
    if sub == 'lunar':
        ctrl.append(BLIND(cd))
    cant = (lambda n: fb(L, a, n, ea))
    # M7 (23/11): os pontos ficam como pontos; o livro-caixa os converte em espaços quando faltar (Flexible Casting)
    # e a metamagia (Quickened) gasta 2. A divisão entre as duas é escolha do plano, não premissa.
    reserva = L if L >= 2 else 0
    f = fatia(L, L, L, m, ('con', 'car'), ca, pv, cant, ctrl, WEB(cd), ar, inv, mage_armor=not drac)   # linhas: com conversão
    f['recursos']['espacos'] = esp_sor(L, 0, mage_armor=not drac)   # recursos: só os espaços de verdade (o resto é ponto)
    if reserva >= 2:
        f['recursos'].setdefault('outros', {})['pontos'] = {"qtd": reserva, "volta": "longo",
                                                           "converte_em_espacos": {str(k): v for k, v in CUSTO.items()}}
        lc = next((l for l in f['linhas'] if l['id'] == 'controle'), None)
        if lc and L >= 3:   # Quickened Spell: a magia de controle sai como ação bônus e o truque segue cheio no round
            q = json.loads(json.dumps(lc)); g = dict(q.get('gasta', {})); g['pontos'] = 2
            q.update(id='controle-quickened', dano=cant(1.0), gasta=g,
                     hipotese="controle com Quickened Spell (2 pontos): magia como ação bônus + Fire Bolt no round")
            q.pop('principal', None); f['linhas'].append(q)
    if sub == 'divine-soul':
        f['linhas'].append(dict(id="bless", herda="principal", hipotese="Bless nos aliados (lista do Cleric)",
                                dano=cant(0.75), suporte={"fontes": [BLESS]}, gasta={"espacos": {"1": 2}},
                                defesa=SH, reacao=RE))
    if sub == 'shadow':
        cao = {"nome": "Hound of Ill Omen", "quantidade": 1, "pv": 37 + L // 2, "ca": 14,
               "ataque": {"n": 1, "bonus": 5, "dano": "2d6+3"}}
        f['linhas'].append(dict(id="cao", herda="principal", hipotese="Hound of Ill Omen (3 pontos ≈ 1 espaço de 2º; ação bônus)",
                                dano=cant(1.0), invocacoes=[cao], gasta={"espacos": {"2": 1, "1": 1}},
                                defesa=SH, reacao=RE))
    ate = C.atencao('retaguarda')
    for l in f['linhas']:
        if 'controle' in l: l['controle']['atencao'] = dict(ate)
        l.setdefault('hipotese', {'principal': 'só Fire Bolt'}.get(l['id'], l['id']))
    f['_texto'] = f"Sorcerer {L}; atributos {s}; CA {ca}" + ("; Elemental Affinity (+Car no fogo)" if ea else "") + "."
    nc = [x for x in ar if x['usos'][0]['slot'] >= 3 and not x.get('concentracao')]
    if L >= 5 and nc: C.area_barata(f, nc[0])   # M5 (23/11): área sem concentração no nível base como magia extra
    return f


SUBS = {
    'aberrant-mind': ("Psionic Spells: Evard's Black Tentacles e Summon Aberration (no maior espaço) além da lista base.",
                      "Psionic Sorcery; Psychic Defenses; Arms/Hunger of Hadar, Dissonant Whispers, Detect Thoughts, Sending, Telekinesis; Mind Sliver (régua: Fire Bolt)."),
    'clockwork-soul': ("Clockwork Magic: Summon Construct (no maior espaço) e Wall of Force (9) além da lista base.",
                       "Restore Balance; Bastion of Law; Trance of Order; Aid, Protection from Evil and Good, Lesser/Greater Restoration, Dispel Magic, Protection from Energy, Freedom of Movement, Alarm."),
    'divine-soul': ("Divine Magic: lista do Cleric; usa Bless como linha de suporte (1 magia conhecida da lista base).",
                    "Favored by the Gods (+2d4 num ataque/save falho); magia de afinidade; Empowered Healing; Healing Word/Cure Wounds; demais magias de Cleric."),
    'draconic': ("Draconic Resilience (CA 13+Des sem Mage Armor, +1 PV/nível) e Elemental Affinity de fogo (+Car no Fire Bolt e no Fireball a partir do 6).",
                 "Resistência a fogo de Elemental Affinity; Dragon Ancestor (idioma, perícias)."),
    'wild-magic': ("Sem mecânica modelável: chassi = Sorcerer base.",
                   "Wild Magic Surge; Tides of Chaos; Bend Luck; Controlled Chaos."),
    'lunar': ("Lunar Embodiment: Blindness/Deafness como opção de controle (Shield já está na base; Hold Monster do 9 já está na base no 11).",
              "Moon Fire (régua: Fire Bolt); Lunar Boons e Waxing and Waning (desconto de metamagia/fase); Ray of Sickness, Color Spray, Alter Self, Vampiric Touch, Phantom Steed, Confusion, Death Ward, Hallucinatory Terrain, Mislead, Rary's Telepathic Bond (fora da biblioteca ou sem efeito no motor)."),
    'shadow': ("Hound of Ill Omen (6) como invocação de uma luta por 3 pontos (≈ 1 espaço de 2º).",
               "Desvantagem nos saves do alvo do cão; Eyes of the Dark (Darkness por pontos); Strength of the Grave (cair a 1 PV); Superior Darkvision."),
    'storm': ("Sem mecânica modelável com tipos existentes: chassi = Sorcerer base (a lista base não tem magia de raio/trovão).",
              "Tempestuous Magic (voo de 10 pés); Heart of the Storm (dano em área de metade do nível ao lançar raio/trovão; resistência); Storm Guide."),
}

if __name__ == '__main__':
    for sub, (res, nm) in SUBS.items():
        url = f"https://rpgbot.net/dnd5/characters/classes/sorcerer/subclasses/{sub}/"
        C.escrever('sorcerer', sub, 'retaguarda', {L: montar(sub, L) for L in C.NIV},
                   build=f"Sorcerer ({sub}), retaguarda, Car > Con > Des, Fire Bolt, " +
                         ("Draconic Resilience" if sub == 'draconic' else "Mage Armor") + ", Shield; sem feat",
                   desc={"resumo": f"Chassi do Sorcerer {sub}: {res}",
                         "estrategia": "Fire Bolt nos rounds livres; Web/Hold Person/Hypnotic Pattern/Polymorph; Fireball em grupos; o plano automático escolhe.",
                         "nao_modelado": nm + " " + BASE_NM},
                   url=url)
