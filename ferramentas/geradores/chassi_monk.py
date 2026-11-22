"""Chassi do Monk (mini-mutirão 22/11): as 9 tradições do gabarito, sem feat e com o feat da subclasse (+ Mobile).
Rodar da raiz: python ferramentas/geradores/chassi_monk.py && python -m dh expandir
Régua comum: lança (1d8, duas mãos) + golpe desarmado na ação bônus; linhas principal / meia-rajada (2 ki) / rajada
(4 ki) / atordoar (Flurry em 2 rounds + 2 Stunning Strike, 4 ki) / mira (Flurry em 2 rounds + Focused Aim 2 ki) /
rajada-mira (6 ki). Atributos Des > Sab > Con (Astral Self: Sab > Des > Con). Features das subclasses = mon.py.
Feat da subclasse = 1º feat não racial da build do RPGBot (progressoes/rpgbot-monk-<sub>.json), no nível 4.
"""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import chassi as C  # noqa: E402
from marcial import A, linha  # noqa: E402

ORDEM = ('des', 'sab', 'con', 'for', 'int', 'car')
ORDEM_SAB = ('sab', 'des', 'con', 'for', 'int', 'car')
MEIO = {'Slasher': 'p', 'Piercer': 'p', 'Skill Expert': 'p', 'Gunner': 'p', 'Crusher': 'con'}   # p = atributo principal
URL = "https://rpgbot.net/dnd5/characters/classes/monk/subclasses/"


def die(L): return 4 if L < 5 else 6 if L < 11 else 8
def U(n, b, d, L, **k): return A(n, b, f'1d{die(L)}', d, **k)


def ctrl(pos, extra=()):
    return {"atencao": C.atencao(pos), "fontes": list(extra) + [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}


def stun(L, b, w, golpes, usos=2):
    return {"tipo": "condicao_no_acerto", "nome": "Stunning Strike (ki)", "efeito": "cond_atordoado_um_turno",
            "cd": 8 + C.pb(L) + w, "bonus": [b] * golpes, "usos": usos}


class K:
    """Contexto de uma fatia: atributos, modificadores e bônus."""
    def __init__(s, L, feat, ordem=ORDEM):
        mf = MEIO.get(feat); mf = ordem[0] if mf == 'p' else mf
        s.L, s.feat = L, feat
        s.s = C.atributos('monk', L, ordem, feat=feat, meio_feat=mf); s.m = C.mods(s.s)
        s.d, s.w, s.c, s.P = s.m['des'], s.m['sab'], s.m['con'], C.pb(L)
        s.b = s.P + s.d; s.n = 1 if L < 5 else 2; s.cd = 8 + s.P + s.w

    def corpo(s, **extra):
        ss = dict(sv=C.sv(s.L, s.m, ('for', 'des')))
        if s.L >= 7: ss.update(evasion=True, stillness=True)
        if s.L >= 11: ss['imune'] = ['veneno']
        return dict(ca=10 + s.d + s.w, pv=C.hp(8, s.L, s.c), saves=ss, **extra)

    def rec(s, **o):
        return {"espacos": {}, "outros": dict({"ki": {"qtd": s.L, "volta": "curto"}}, **o)}


def base(k, pos, extra_ctrl=(), defesa=None, sufixo=' (lança)', por_turno=()):
    L, b, d, n = k.L, k.b, k.d, k.n
    def at(x, **e):
        r = {"ataques": [A(n, b, '1d8', d), U(x, b, d, L, nota="ação bônus (Martial Arts / Flurry of Blows)")]}
        if por_turno: r['por_turno'] = list(por_turno)
        r.update(e); return r
    df = defesa or {}
    ls = [linha('principal', 'sem ki: ataque + golpe desarmado na ação bônus' + sufixo, at(1), df, controle=ctrl(pos, extra_ctrl)),
          linha('meia-rajada', 'Flurry of Blows em 2 dos 4 rounds (2 ki)' + sufixo, at(1.5), df, controle=ctrl(pos, extra_ctrl), gasta={"ki": 2}),
          linha('rajada', 'Flurry of Blows todo round (4 ki)' + sufixo, at(2), df, controle=ctrl(pos, extra_ctrl), gasta={"ki": 4})]
    ls.append(linha('atordoar', 'Flurry em 2 rounds + 2 tentativas de Stunning Strike (4 ki)' + sufixo, at(1.5), df,
                    controle=ctrl(pos, [stun(L, b, k.w, n + 2)] + list(extra_ctrl)), gasta={"ki": 4}))
    ls.append(linha('mira', 'Flurry em 2 rounds + Focused Aim com 2 ki (4 ki)' + sufixo, at(1.5, focused_aim={"ki": 2}), df,
                    controle=ctrl(pos, extra_ctrl), gasta={"ki": 4}))
    ls.append(linha('rajada-mira', 'Flurry todo round + Focused Aim com 2 ki (6 ki)' + sufixo, at(2, focused_aim={"ki": 2}), df,
                    controle=ctrl(pos, extra_ctrl), gasta={"ki": 6}))
    return ls


GOLPES = {"principal": 1, "meia-rajada": 1.5, "rajada": 2, "atordoar": 1.5, "mira": 1.5, "rajada-mira": 2}


def crusher(k, ls):
    """Crusher: no crítico com dano de concussão (golpe desarmado), vantagem de todos contra o alvo até o próximo turno."""
    for l in ls:
        g = GOLPES.get(l['id'])
        if g is None: continue
        l['suporte'] = {"fontes": [{"nome": "Crusher (crítico: vantagem de todos contra o alvo)", "lado": "of",
                                    "modelo": "vantagem", "alvos": 3, "fracao": round(1 - 0.95 ** g, 3)}]}


def fim(k, txt, ls, **corpo_extra):
    return dict(_texto=f"{txt} Atributos {k.s}.", corpo=k.corpo(**corpo_extra), recursos=k.rec(), linhas=ls)


# ---------------------------------------------------------------- subclasses
def open_hand(L, feat, pos):
    k = K(L, feat); ls = base(k, pos)
    for l in ls:
        kfl = {"meia-rajada": 4, "rajada": 8, "atordoar": 4, "mira": 4, "rajada-mira": 8}.get(l['id'])
        if kfl: l['controle']['fontes'].insert(0, {"tipo": "condicao_no_acerto", "nome": "Open Hand Technique (derruba no Flurry)",
                                                   "efeito": "cond_derrubado", "cd": k.cd, "bonus": [k.b, k.b], "usos": kfl})
    if feat == 'Crusher': crusher(k, ls)
    return fim(k, "Open Hand Technique; Wholeness of Body (6)" + ("; Tranquility (11)." if L >= 11 else "."), ls)


def drunken(L, feat, pos):
    k = K(L, feat); ls = base(k, pos, sufixo=' (lança; Flurry com Disengage grátis)')
    if feat == 'Crusher': crusher(k, ls)
    return fim(k, "Drunken Technique; Tipsy Sway (6)" + ("; Drunkard's Luck (11)." if L >= 11 else "."), ls)


def mercy(L, feat, pos):
    k = K(L, feat); ls = base(k, pos); b, d, w, n = k.b, k.d, k.w, k.n
    harm = {"dano": f"1d{die(L)}+{w}", "nota": "Hand of Harm (1 ki, 1× por turno num golpe desarmado)"}
    cura = {"nome": "Hand of Healing (troca um golpe do Flurry)", "lado": "def", "modelo": "cura_na_luta", "alcance": "toque",
            "acao": "bonus", "usos_luta": 1, "pv": die(L) / 2 + 0.5 + w}
    if L < 11:
        dano = {"ataques": [A(n, b, '1d8', d), U(1.25, b, d, L, nota="ação bônus (Flurry em 2 rounds, um golpe vira cura)")],
                "por_luta": [dict(harm, usos=2)]}
        usos_p, hip = 2, 'Flurry em 2 rounds + Hand of Harm em 2 acertos + 1 Hand of Healing (4 ki)'
    else:
        dano = {"ataques": [A(n, b, '1d8', d), U(1.75, b, d, L, nota="ação bônus (Flurry todo round, um golpe vira cura)")],
                "por_turno": [harm]}
        usos_p, hip = 4, 'Flurry todo round com Hand of Harm grátis + 1 Hand of Healing (4 ki)'
    fontes = [{"tipo": "condicao_no_acerto", "nome": "Physician's Touch (envenenado, sem save)", "efeito": "cond_envenenado_um_turno",
               "cd": 99, "bonus": [b] * (n + 1), "usos": usos_p}]
    ls.append(linha('mao-da-morte', hip, dano, {}, controle=ctrl(pos, fontes), gasta={"ki": 4}, suporte=[cura]))
    return fim(k, "Hand of Healing/Harm; Physician's Touch (6)" + ("; Flurry of Healing and Harm (11)." if L >= 11 else "."), ls)


def long_death(L, feat, pos):
    k = K(L, feat); d, w = k.d, k.w
    pt = [{"dano": "1", "nota": "Piercer (rerrola um dado de perfurante)"},
          {"dano": "1d8", "gatilho": "critico", "nota": "Piercer (dado extra no crítico)"}] if feat == 'Piercer' else []
    defesa = {"golpes_extras_a_0pv": 1} if L >= 11 else {}
    ls = base(k, pos, defesa=defesa, por_turno=pt)
    ls.append(linha('ceifa', 'Hour of Reaping na ação todo round (amedronta em 30 pés) + golpe desarmado na ação bônus',
                    {"ataques": [U(1, k.b, d, L, nota="ação bônus (Martial Arts)")]}, defesa,
                    controle=ctrl(pos, [{"tipo": "area", "nome": "Hour of Reaping", "magia": "hour_of_reaping",
                                         "cd": k.cd, "so_grupos": True}])))
    # Touch of Death: PV temporários (Sab + nível) ao derrubar alguém a 5 pés; 1 abate por luta (sem o truque do rato)
    return fim(k, "Touch of Death; Hour of Reaping (6)" + ("; Mastery of Death (11)." if L >= 11 else "."), ls,
               pvt_luta=max(1, w + L))


def astral(L, feat, pos):
    k = K(L, feat, ORDEM_SAB); ls = base(k, pos, sufixo=' (lança, sem os braços astrais)')
    w, n, cd = k.w, k.n, k.cd; bw = k.P + w
    extra = {"por_turno": [{"dano": f"1d{die(L)}", "nota": "Empowered Arms (Body of the Astral Self)"}]} if L >= 11 else {}
    k0 = 2 if L >= 11 else 1
    def bra(kba, suf, ki, hip, extra_ctrl=()):
        dano = {"ataques": [U(n, bw, w, L, nota="braços astrais (Sab, alcance 10)"),
                            U(kba, bw, w, L, nota="ação bônus (rounds 2–4: o 1º round invoca os braços)")],
                "com_save": [{"n": 0.25, "cd": cd, "save": "Des", "dano": f"2d{die(L)}", "meio": False,
                              "nota": "invocação dos braços (1× por luta)"}], **extra}
        area = [{"nome": "Arms of the Astral Self (invocação)", "tipo": "explosao",
                 "usos": [{"alvos": 2, "dano": f"2d{die(L)}", "cd": cd, "save": "Des", "metade": False}]}]
        return linha('bracos' + suf, hip, dano, {}, controle=ctrl(pos, extra_ctrl), area=area, gasta={"ki": k0 + ki})
    ls.append(bra(0.75, '', 0, f'Arms of the Astral Self ({k0} ki, 10 minutos = 1 luta): ataques de Sab com alcance'))
    ls.append(bra(1.5, '-rajada', 3, f'braços astrais + Flurry nos rounds 2–4 ({k0 + 3} ki)'))
    ls.append(bra(1.25, '-atordoar', 2, f'braços astrais + Flurry em 1 round + 1 Stunning Strike ({k0 + 2} ki)',
                  [stun(L, bw, w, n + 1, usos=1)]))
    return fim(k, "Arms of the Astral Self; Visage (6)" + ("; Body of the Astral Self (11)." if L >= 11 else "."), ls)


def shadow(L, feat, pos):
    k = K(L, feat); ls = base(k, pos); b, d, n = k.b, k.d, k.n
    if feat == 'Eldritch Adept':   # Darkness (2 ki) + Devil's Sight
        def esc(x, suf, ki, hip):
            at = [A(n, b, '1d8', d, vantagem=1.0), U(x, b, d, L, vantagem=1.0, nota="ação bônus")]
            return linha('escuridao' + suf, hip, {"ataques": at}, {"adv": -1}, controle=ctrl(pos), gasta={"ki": 2 + ki})
        ls.append(esc(1, '', 0, "Darkness (2 ki, 10 minutos = 1 luta) + Devil's Sight: vantagem nos ataques, desvantagem contra ele"))
        ls.append(esc(1.5, '-rajada', 2, 'Darkness + Flurry em 2 rounds (4 ki)'))
    return fim(k, "Shadow Arts; Shadow Step (6)" + ("; Cloak of Shadows (11)." if L >= 11 else "."), ls)


def four(L, feat, pos):
    k = K(L, feat); ls = base(k, pos); b, d, n, cd = k.b, k.d, k.n, k.cd
    def disc(id_, hip, ki, area=None, com_save=None, fontes=()):
        dano = {"ataques": [A(n * 0.75, b, '1d8', d, nota="ação nos rounds 2–4"),
                            U(1, b, d, L, nota="ação bônus (Martial Arts / Ki-Fueled Attack no round da disciplina)")]}
        if com_save: dano['com_save'] = [com_save]
        return linha(id_, hip, dano, {}, controle=ctrl(pos, fontes), area=area, gasta={"ki": ki})
    ls.append(disc('punho', 'Fist of Unbroken Air no 1º round (2 ki): 3d10, empurra e derruba', 2,
                   com_save={"n": 0.25, "cd": cd, "save": "For", "dano": "3d10", "meio": True, "nota": "Fist of Unbroken Air (1× por luta)"},
                   fontes=[{"tipo": "condicao_no_acerto", "nome": "Fist of Unbroken Air (derrubado)", "efeito": "cond_derrubado",
                            "cd": cd, "usos": 1, "no_acerto": False}]))
    if L < 11:
        ls.append(disc('gongo', 'Gong of the Summit (Shatter, 3 ki) no 1º round', 3,
                       area=[{"nome": "Gong of the Summit", "tipo": "explosao",
                              "usos": [{"alvos": 2, "dano": "3d8", "cd": cd, "save": "Con", "metade": True}]}],
                       com_save={"n": 0.25, "cd": cd, "save": "Con", "dano": "3d8", "meio": True, "nota": "Gong of the Summit"}))
    else:
        ls.append(disc('fenix', 'Flames of the Phoenix (Fireball, 4 ki) no 1º round', 4,
                       area=[{"nome": "Flames of the Phoenix", "tipo": "explosao",
                              "usos": [{"alvos": 4, "dano": "8d6", "cd": cd, "save": "Des", "metade": True}]}],
                       com_save={"n": 0.25, "cd": cd, "save": "Des", "dano": "8d6", "meio": True, "nota": "Flames of the Phoenix"}))
    return fim(k, "Fist of Unbroken Air; Gong of the Summit (6)" + ("; Flames of the Phoenix (11, troca o Gong)." if L >= 11 else "."), ls)


def sun(L, feat, pos):
    k = K(L, feat); ls = base(k, pos, sufixo=' (lança, corpo a corpo)'); b, d, n, cd = k.b, k.d, k.n, k.cd
    def raio(x, nm): return A(x, b, f'1d{die(L)}', d, nota=nm)
    ls.append(linha('raios', 'Radiant Sun Bolt na ação (30 pés), sem ki', {"ataques": [raio(n, "Radiant Sun Bolt")]}, {}, controle=ctrl(pos)))
    ls.append(linha('raios-rajada', 'Radiant Sun Bolt + dois raios na ação bônus todo round (4 ki)',
                    {"ataques": [raio(n, "Radiant Sun Bolt"), raio(2, "raios na ação bônus (1 ki)")]}, {}, controle=ctrl(pos), gasta={"ki": 4}))
    ls.append(linha('arco', 'Searing Arc Strike (Burning Hands na ação bônus, 2 ki) no 1º round, raios na ação',
                    {"ataques": [raio(n, "Radiant Sun Bolt"), raio(1, "raios na ação bônus (rounds 2–4)")],
                     "com_save": [{"n": 0.25, "cd": cd, "save": "Des", "dano": "3d6", "meio": True, "nota": "Searing Arc Strike"}]},
                    {}, controle=ctrl(pos), gasta={"ki": 4},
                    area=[{"nome": "Searing Arc Strike", "tipo": "explosao",
                           "usos": [{"alvos": 2, "dano": "3d6", "cd": cd, "save": "Des", "metade": True}]}]))
    if L >= 11:
        ls.append(linha('sunburst', 'Searing Sunburst na ação (grátis, 20 pés de raio, Con anula)',
                        {"ataques": [], "com_save": [{"n": 1, "cd": cd, "save": "Con", "dano": "2d6", "meio": False, "nota": "Searing Sunburst"}]},
                        {}, controle=ctrl(pos),
                        area=[{"nome": "Searing Sunburst (grátis)", "tipo": "cleave_save", "dano": "2d6", "cd": cd, "save": "Con",
                               "alvos": [3, 4, 4], "metade": False}]))
    return fim(k, "Radiant Sun Bolt; Searing Arc Strike (6)" + ("; Searing Sunburst (11)." if L >= 11 else "."), ls)


def kensei(L, feat, pos):
    """Atirador. Sem feat: arco longo (arma kensei) + Kensei's Shot (+1d4 nos acertos à distância, ação bônus).
    Crossbow Expert: besta de mão com o dado de Martial Arts (mín. d6) e o tiro da ação bônus no lugar do Kensei's Shot."""
    k = K(L, feat); b, d, n = k.b, k.d, k.n
    if feat == 'Crossbow Expert':
        dado = f'1d{max(6, die(L))}'
        at = lambda bb=0: [A(n, b + bb, dado, d + bb), A(1, b + bb, dado, d + bb, nota="Crossbow Expert (ação bônus)")]
        arma = 'besta de mão com Crossbow Expert'
    else:
        at = lambda bb=0: [A(n, b + bb, '1d8', d + bb, extra='+1d4', nota="arco longo + Kensei's Shot (ação bônus)")]
        arma = "arco longo com Kensei's Shot"
    deft = {"dano": f"1d{die(L)}", "nota": "Deft Strike (1 ki, 1× por turno)"}
    c = ctrl(pos)
    ls = [linha('principal', f'{arma}, sem ki', {"ataques": at()}, {}, controle=c),
          linha('deft', f'{arma} + Deft Strike em 4 acertos (4 ki)', {"ataques": at(), "por_luta": [dict(deft, usos=4)]}, {},
                controle=c, gasta={"ki": 4}),
          linha('mira', f'{arma} + Focused Aim 2 ki + Deft Strike em 2 acertos (4 ki)',
                {"ataques": at(), "focused_aim": {"ki": 2}, "por_luta": [dict(deft, usos=2)]}, {}, controle=c, gasta={"ki": 4})]
    if L >= 11:
        ls.append(linha('afiar', f'Sharpen the Blade (3 ki: +3 no acerto e no dano, 1 minuto = 1 luta) + {arma}',
                        {"ataques": at(3)}, {}, controle=c, gasta={"ki": 3}))
    return fim(k, "Path of the Kensei, Agile Parry, Kensei's Shot; One with the Blade (6)" +
               ("; Sharpen the Blade (11)." if L >= 11 else "."), ls)


SUBS = {   # sub: (função, posição, feat(s) do RPGBot, resumo, nao_modelado da subclasse)
    'open-hand': (open_hand, 'skirmisher', ['Crusher'], "Mão Aberta: o Flurry derruba; Stunning Strike no resto.",
                  "Empurrão e reação negada da Open Hand Technique; Wholeness of Body; Tranquility; vantagem dos aliados contra o derrubado/atordoado."),
    'drunken-master': (drunken, 'skirmisher', ['Crusher'], "Monge Bêbado: Flurry com Disengage grátis, bate e sai.",
                       "Disengage/deslocamento do Drunken Technique; Redirect Attack (Tipsy Sway); Leap to Your Feet; Drunkard's Luck."),
    'mercy': (mercy, 'skirmisher', ['Slasher'], "Misericórdia: Hand of Harm, veneno sem save e Hand of Healing no Flurry.",
              "Remoção de condições; cura fora de luta; chicote (alcance) trocado pela lança da régua."),
    'long-death': (long_death, 'defensor', ['Piercer'], "Morte Longa: defensor com PV temporários ao derrubar, Hour of Reaping e Mastery of Death.",
                   "Touch of Death além de 1 abate por luta; a mordida do Dhampir da build do RPGBot (racial) fica fora do chassi."),
    'astral-self': (astral, 'skirmisher', ['Skill Expert'], "Eu Astral: braços espectrais que batem com Sabedoria, com alcance.",
                    "Agarrar/empurrar com Sab; Visage; Deflect Energy; duração cobrindo duas lutas."),
    'shadow': (shadow, 'skirmisher', ['Eldritch Adept'], "Sombra: sem Devil's Sight a Darkness cega os dois lados; com Eldritch Adept vira vantagem.",
               "Shadow Step (vantagem no 1º ataque, depende de penumbra); Cloak of Shadows; Pass Without Trace/Silence; custo da Darkness para os aliados."),
    'four-elements': (four, 'skirmisher', [], "Quatro Elementos: disciplinas caras em ki para derrubar e dar dano em área.",
                      "Upcast das disciplinas; empurrão de 20 pés; Ride the Wind; Elemental Attunement."),
    'sun-soul': (sun, 'skirmisher', ['Gunner'], "Alma Solar: raios radiantes a 30 pés, Burning Hands na ação bônus e explosão grátis no 11.",
                 "Mosquete do Gunner (o feat só dá +1 Des aqui); upcast do Searing Sunburst; Sun Shield."),
    'kensei': (kensei, 'atirador', ['Crossbow Expert'], "Kensei atirador: arco longo com Kensei's Shot, Deft Strike e Sharpen the Blade.",
               "Flurry/Stunning Strike (exigem corpo a corpo: as linhas de ki do Kensei são Deft Strike e Focused Aim); Agile Parry; Deflect Missiles."),
}
NM_FEAT = {'Mobile': "Mobile (+10 pés, sem ataque de oportunidade de quem atacou): sem mecânica no motor, diferença zero de propósito.",
           'Slasher': "Slasher (redução de deslocamento, desvantagem no crítico): só o +1 Des entra.",
           'Skill Expert': "Skill Expert (expertise em Atletismo): só o +1 Sab entra.",
           'Gunner': "Gunner: só o +1 Des entra.",
           'Eldritch Adept': "Eldritch Adept exige Spellcasting/Pact Magic (o RPGBot aceita Shadow Arts; ver relatório)."}

if __name__ == '__main__':
    for sub, (fn, pos, feats, resumo, nm) in SUBS.items():
        for feat in [None] + feats + ['Mobile']:
            desc = {"resumo": f"Chassi do Monk {resumo}",
                    "estrategia": "Régua comum do monge (lança + Martial Arts, Flurry, Stunning Strike, Focused Aim) + o que a tradição dá.",
                    "nao_modelado": " ".join(x for x in (nm, NM_FEAT.get(feat, ''), "Deflect Missiles; Slow Fall; Patient Defense/Step of the Wind.") if x)}
            fonte_feat = (" (1º feat não racial da build do RPGBot)" if feat != 'Mobile' else " (variante comum do Monk)") if feat else ''
            C.escrever('monk', sub, pos, {L: fn(L, feat, pos) for L in C.NIV},
                       build=f"Monk ({sub}), {pos}, sem armadura, Des/Sab" + (f"; {feat} no 4{fonte_feat}" if feat else "; sem feat"),
                       desc=desc, feat=feat, url=URL + sub + '/')
