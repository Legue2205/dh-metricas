"""Ranger (passada 1, mutirão 21/11): 8 subclasses do RPGBot (2014 + Tasha/Xanathar/Fizban).
Rodar da raiz: python ferramentas/geradores/ran.py && python -m dh expandir progressoes/rpgbot-ranger-*.json
Chassi comum (prazo curto: as páginas build-ranger-* não foram lidas uma a uma): arqueiro com arco longo,
Archery (+2), humano variante com Sharpshooter no 1, Des 16 → 18 (4) → 20 (8), Sab 14, Con 14, couro batido.
Hunter's Mark = +1d6 por acerto na string do ataque; dura 1 hora → 0,5 espaço de 1º por luta (convenção de duração).
Convenções: calibracao/convencoes-passada1.md + seção Ranger no relatorio-ranger.md do mutirão."""
import sys
sys.path.insert(0, 'ferramentas/geradores')
import marcial
from marcial import *
marcial.CLASSE = 'ranger'
marcial.NOTA = ("Chassi comum de arqueiro (Handbook do Ranger) com as features da subclasse; mutirão 21/11, passada 1 cega: "
                "só mecânica, premissas congeladas.")

SL = {3: {"1": 3}, 5: {"1": 4, "2": 2}, 7: {"1": 4, "2": 3}, 9: {"1": 4, "2": 3, "3": 2}, 11: {"1": 4, "2": 3, "3": 3}}
HM = {"espacos": {"1": 0.5}}           # Hunter's Mark: 1 hora de concentração cobre ~2 lutas
SS = {"poder": [-5, 10]}               # Sharpshooter


def chassi(L):
    dx = {3: 16, 5: 18, 7: 18, 9: 20, 11: 20}[L]; d, P = mod(dx), pb(L)
    m = M(0, d, 2, 0, 2, 0); b = P + d + 2           # Archery
    n = 1 if L < 5 else 2
    ca = 12 + d                                       # couro batido
    return d, P, m, b, n, ca


def arco(n, b, d, marca, extra='', **k):
    return A(n, b, '1d8', d, ('+1d6' if marca else '') + extra, **SS, **k)


def fazer(L, sub):
    d, P, m, b, n, ca = chassi(L); w = 2; bm = P + w   # ataque de magia (pets)
    ss = dict(sv=sv(L, m, ('for', 'des')))
    pt, pl, extra_at, txt = [], [], [], ''
    papel = 'atirador'
    if sub == 'hunter':
        pt = [{"dano": "1d8", "nota": "Colossus Slayer (alvo já ferido, 1×/turno)"}]
        txt = "Colossus Slayer (3); Multiattack Defense/Escape the Horde (7) e Volley (11) não modelados."
    elif sub == 'gloom-stalker':
        extra_at = [lambda marca: arco(0.25, b, d, marca, '+1d8', nota="Dread Ambusher: ataque extra +1d8 no 1º round")]
        if L >= 7: ss['sv']['sab'] = m['sab'] + P                       # Iron Mind
        if L >= 11:   # Stalker's Flurry: 1×/turno, errou → ataque extra. P(≥1 erro em 2 ataques com SS) ≈ 0,5 (passada 2)
            extra_at.append(lambda marca: arco(0.5, b, d, marca, nota="Stalker's Flurry: ataque extra após errar (≈0,5/turno)"))
        txt = "Dread Ambusher (3); Iron Mind (7: save de Sab); Stalker's Flurry (11: +0,5 ataque/turno); Umbral Sight não modelado."
    elif sub == 'horizon-walker':
        pt = [{"dano": "1d8" if L < 11 else "2d8", "nota": "Planar Warrior (ação bônus, 1 acerto/turno, força)"}]
        if L >= 11: extra_at = [lambda marca: arco(1, b, d, marca, nota="Distant Strike: 3º ataque contra outra criatura")]
        txt = "Planar Warrior (3; 2d8 no 11); Distant Strike (11) com o 3º ataque sempre; Ethereal Step (7) não modelado."
    elif sub == 'monster-slayer':
        pt = [{"dano": "1d6", "nota": "Slayer's Prey (1×/turno no alvo marcado)"}]
        txt = "Slayer's Prey (3); Supernatural Defense (7) e Magic-User's Nemesis (11) não modelados."
    elif sub == 'fey-wanderer':
        pt = [{"dano": "1d4" if L < 11 else "1d6", "nota": "Dreadful Strikes (psíquico, 1×/turno por alvo)"}]
        txt = "Dreadful Strikes (3; 1d6 no 11); Otherworldly Glamour; Beguiling Twist (7) e Fey Reinforcements (11) não modelados."
    elif sub == 'swarmkeeper':
        pt = [{"dano": "1d6" if L < 11 else "1d8", "nota": "Gathered Swarm (1×/turno)"}]
        txt = "Gathered Swarm (3; 1d8 no 11); Writhing Tide (7) e Mighty Swarm (11, derrubar) não modelados."
    elif sub == 'drakewarden':
        extra_at = [lambda marca: A(0.75, bm, '1d6', P, ("+1d6" if L >= 7 else ''),
                                    nota="Drake: mordida (ação bônus do ranger; round 1 vai na Hunter's Mark)")]
        txt = "Drake Companion (3); Bond of Fang and Scale (7: +1d6 na mordida); Drake's Breath e Drake ampliado (11) não modelados."
    elif sub == 'beast-master':
        nb = 0.75 if L < 11 else 1.5
        extra_at = [lambda marca: A(nb, bm, '1d8', 2 + P, nota="Primal Companion (Beast of the Land; ação bônus; 2 ataques no 11)")]
        txt = "Primal Companion (Tasha, Beast of the Land); Bestial Fury (11). Charge, Exceptional Training e Share Spells não modelados."

    def dano(marca):
        x = {"ataques": [arco(n, b, d, marca)] + [f(marca) for f in extra_at]}
        if pt: x["por_turno"] = pt
        return x
    ctl = {"atencao": {"papel": papel, "soft": 0.15, "dpr": "auto"}, "fontes": [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}
    dm = dict(dano(True), concentracao="hunters_mark")                     # M2 (23/11): a Marca é concentração
    ff = dano(False); ff["por_turno"] = ff.get("por_turno", []) + [{"dano": "1d4" if L < 6 else "1d6", "nota": "Favored Foe (1×/turno)"}]
    ff["concentracao"] = "favored_foe"
    cd = 8 + P + 2                                                          # Sab 14
    ls = [linha('principal', 'arco longo com Sharpshooter, sem magia', dano(False), {}, controle=ctl, papel=papel),
          linha('marca', "Hunter's Mark (1 hora: 0,5 espaço de 1º por luta)", dm, {}, controle=ctl, papel=papel, gasta=HM),
          linha('inimigo-favorito', "Favored Foe (sem espaço: PB usos por descanso longo, 1 por luta)", ff, {},
                controle=ctl, papel=papel, gasta={"favored_foe": 1}),
          linha('enredar', "Ensnaring Strike no 1º acerto (1 espaço de 1º), depois ataques normais", dano(False), {},
                controle=dict(ctl, fontes=[{"tipo": "condicao_no_acerto", "nome": "Ensnaring Strike", "efeito": "ensnaring_strike",
                                            "cd": cd, "bonus": [b] * n, "usos": 1}] + ctl["fontes"]),
                papel=papel, gasta={"espacos": {"1": 1}})]
    if L >= 9:
        ls.append(linha('conjurar-animais', "Conjure Animals (8 lobos; 1 espaço de 3º), ataques normais", dano(False), {},
                        controle=ctl, papel=papel, gasta={"espacos": {"3": 1}}))
        ls[-1]['invocacoes'] = [{"nome": "Conjure Animals (8 lobos)", "quantidade": 8, "pv": 11, "ca": 13,
                                 "ataque": {"n": 1, "bonus": 4, "dano": "2d4+2", "vantagem": 0.8}}]
    if L >= 5:   # M6 (23/11): Spike Growth (2º, concentração); Plant Growth (3º, sem concentração) do 9
        ls.append(linha('terreno-espinhos', "Spike Growth (1 espaço de 2º), ataques normais", dano(False), {},
                        controle=dict(ctl, fontes=[{"tipo": "area", "nome": "Spike Growth", "magia": "spike_growth", "cd": cd}] + ctl["fontes"]),
                        papel=papel, gasta={"espacos": {"2": 1}}))
    if L >= 9:
        ls.append(linha('terreno-plantas', "Plant Growth (1 espaço de 3º, sem concentração), ataques normais", dano(False), {},
                        controle=dict(ctl, fontes=[{"tipo": "area", "nome": "Plant Growth", "magia": "plant_growth", "cd": cd}] + ctl["fontes"]),
                        papel=papel, gasta={"espacos": {"3": 1}}))
    pet = ([{"nome": "Primal Companion (Beast of the Land)", "quantidade": 1, "pv": 5 + 5 * L, "ca": 13 + P}] if sub == 'beast-master'
           else [{"nome": "Drake Companion", "quantidade": 1, "pv": 5 + 5 * L, "ca": 14 + P}] if sub == 'drakewarden' else [])
    for l in ls:
        if pet: l['invocacoes'] = pet + l.get('invocacoes', [])
    rec = {"espacos": dict(SL[L]), "outros": {"favored_foe": {"qtd": P, "volta": "longo"}}}
    base_txt = {3: "Arqueiro: Archery, Sharpshooter (1), Des 16.", 5: "Extra Attack; Des 18 (4).", 7: "",
                9: "Des 20 (8); magias de 3º.", 11: ""}[L]
    return dict(_texto=(base_txt + ' ' + txt).strip(), corpo=dict(ca=ca, pv=hp([10] * L, 2), saves=ss), recursos=rec, linhas=ls)


SUBS = {'hunter': 'Hunter', 'gloom-stalker': 'Gloom Stalker', 'horizon-walker': 'Horizon Walker',
        'monster-slayer': 'Monster Slayer', 'fey-wanderer': 'Fey Wanderer', 'swarmkeeper': 'Swarmkeeper',
        'drakewarden': 'Drakewarden', 'beast-master': 'Beast Master (Primal Companion)'}
NM = ("Troca de alvo da Hunter's Mark (ação bônus); magias utilitárias (Pass without Trace etc.); dano do Spike Growth; "
      "Natural Explorer; vantagem de criaturas Grandes contra o Ensnaring Strike; ")   # M2 (23/11): o resto entrou
for slug, nome in SUBS.items():
    fat = {L: fazer(L, slug) for L in NIV}
    escrever('rpgbot-ranger-' + slug, slug, nome + ' Ranger', f'Ranger ({nome}), humano variante arqueiro, arco longo; '
             'Archery, Sharpshooter 1, Des 18 no 4, Des 20 no 8 (chassi comum)',
             {"resumo": f"{nome}: arqueiro com Hunter's Mark e a feature de dano da subclasse.",
              "estrategia": "Atira todo round; Hunter's Mark no 1º round das lutas que o plano escolher.",
              "nao_modelado": NM + fat[11]['_texto']}, fat)
