"""
MOTOR DE ÁREA — DragonHeist (D&D 5e, regras 2014)
Planilha: "00 CLAUDE DPR Dragonheist - Ranks de área — DragonHeist"
Versão consolidada em 10/11/2026 (régua v2 + variações de horda + fichas).

Uso:  python3 motor_area.py            -> imprime fichas, régua, níveis equivalentes e variações
      Precisa só de numpy. Monte Carlo: os números variam ~±0,1 nível entre execuções.

HIPÓTESES (resumo; detalhes nos comentários de cada bloco)
 1. Encontro: horda Difícil do DMG para uma party de 4 em cada nível 1–20, 6 criaturas iguais,
    CR pelo orçamento de XP (multiplicador ×2 para 3–6 criaturas). HP e save médio pelas
    medianas do Monster Manual (ajuste de Tom Dunn; CR < 1 por amostra de stat blocks).
 2. Métrica: fração do HP total da horda removida. Dano acima do HP de cada criatura é perdido.
 3. Alvos por uso: tabela de alvos em área do DMG (esfera raio÷5, cone tamanho÷10,
    cubo lado÷5, linha comprimento÷30). Fireball 4, Shatter 2, Lightning Bolt 4, Wall em linha 2.
    Round 1 vale inteiro; do round 2 em diante 50% sem seleção (aliados no corpo a corpo),
    75% com seleção (Sculpt Spells, Careful Spell). Alvos fracionários são sorteados.
 4. Régua: conjurador pleno de referência em cada nível — dano da diretriz "vários alvos" da
    tabela Spell Damage do DMG no maior espaço, rolado em d6; CD = 8 + prof + atributo
    (+3 até nv 3, +4 do 4 ao 7, +5 do 8 em diante); alvos pela área típica do círculo:
    1º–2º = 2, 3º–4º = 4, 5º+ = 6 (Cone of Cold, Circle of Death, Sunburst).
 5. Luta comum = 1 uso da referência no maior espaço. Luta prioritária = referência gasta os
    3 maiores espaços nos rounds 1 a 3. Entre usos, quem morreu sai da horda.
 6. Nível equivalente: maior nível L em que a área tira ≥ a fração da referência de L,
    interpolado até L+1. Abaixo do nível 1: proporcional (0,5 × fração / referência do nível 1).
 7. Rank: mesma tabela da planilha de defesa (E 0,5 · D 1 · C- 3 · C 4 · C+ 5 · B- 6 · B 7 ·
    B+ 8 · A- 10 · A 11 · A+ 13 · S 16).
 8. Cleave: dano extra em 4 rounds contra a mesma horda, comparado com 1 uso da referência.
 9. Wall of Fire: save ao conjurar + 0,5 exposição extra sem save (metade dos alvos toma um
    tique antes de sair). Em linha pega 2 alvos.
10. Orçamento diário (dia de 4 lutas, 2 descansos curtos): Pyotr 9 espaços de pacto nv 5
    (3 na prioritária, 2 em cada comum). Solaris: Fireball nv 5, 4, 4 na prioritária,
    1 Fireball nv 3 nas comuns.
11. Variações: esparsa = 0,5× alvos; padrão = 1×; agrupada = 1,5× (teto na horda de 6).
    Vale para personagens E para a referência.

PENDENTE / CONFERIR
 - Limiares de XP, XP por CR, multiplicadores e tabela Spell Damage do DMG foram escritos
   de memória: bater com o livro (DMG caps. 3 e 9).
 - Saves fraco/forte por CR são interpolação linear (diferença 3 → 6 do CR 0 ao 30).
 - Sem Magic Resistance, Legendary Resistance nem Evasion na horda.
 - Wall of Fire em anel não modelada.
 - Ponte com a planilha de DPR: letras de área parecem ~1 nível mais exigentes que as de DPR
   (arquétipos de DPR caem, em mediana, +1 nível acima do próprio nível).
"""
import numpy as np

rng = np.random.default_rng(21)
N = 40000                      # combates simulados por ponto

# ---------------------------------------------------------------------------
# 1. Referências do DMG e do Monster Manual
# ---------------------------------------------------------------------------
# CR -> (HP médio, CA, save médio). Fonte: Tom Dunn (CR ≥ 1); amostra do MM (CR < 1).
CR = {0.125: (10, 13, 0), 0.25: (14.5, 13, 0), 0.5: (21.5, 13, 0), 1: (32, 14, 0), 2: (49, 14, 1),
      3: (66, 15, 1), 4: (83, 15, 2), 5: (100, 15, 2), 6: (117, 16, 3)}
# Nível da party -> CR da horda Difícil de 6 criaturas (aba "Encontros por nível").
HORDA = {1: 0.125, 2: 0.25, 3: 0.25, 4: 0.5, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2, 10: 2, 11: 3, 12: 3,
         13: 4, 14: 4, 15: 4, 16: 4, 17: 5, 18: 5, 19: 6, 20: 6}
NH = 6                         # criaturas na horda
# Diretriz "vários alvos" da tabela Spell Damage do DMG (dano médio por círculo).
MULTI = {1: 7, 2: 14, 3: 21, 4: 24.5, 5: 28, 6: 38.5, 7: 42, 8: 45.5, 9: 49}
# Três maiores espaços de um conjurador pleno por nível.
TOP3 = {1: (1, 1, 1), 2: (1, 1, 1), 3: (2, 2, 1), 4: (2, 2, 2), 5: (3, 3, 2), 6: (3, 3, 3),
        7: (4, 3, 3), 8: (4, 4, 3), 9: (5, 4, 4), 10: (5, 5, 4), 11: (6, 5, 5), 12: (6, 5, 5),
        13: (7, 6, 5), 14: (7, 6, 5), 15: (8, 7, 6), 16: (8, 7, 6), 17: (9, 8, 7), 18: (9, 8, 7),
        19: (9, 8, 7), 20: (9, 8, 7)}
RANKS = [("E", 0.5), ("D", 1), ("C-", 3), ("C", 4), ("C+", 5), ("B-", 6), ("B", 7), ("B+", 8),
         ("A-", 10), ("A", 11), ("A+", 13), ("S", 16)]

def alvos_circulo(s): return 2 if s <= 2 else 4 if s <= 4 else 6
def pb(L): return 2 + (L - 1) // 4
def cd(L): return 8 + pb(L) + (3 if L < 4 else 4 if L < 8 else 5)
def rank(neq):
    r = "F"
    for letra, lv in RANKS:
        if neq >= lv: r = letra
    return r

# ---------------------------------------------------------------------------
# 2. Dados
# ---------------------------------------------------------------------------
def roll(n, die): return rng.integers(1, die + 1, (n, N)).sum(0) if n else np.zeros(N, int)
def d6s(media): return roll(int(round(media / 3.5)), 6)
def carga(n):                  # Ravin: a carga da espada dobra o maior dado da magia
    r = rng.integers(1, 7, (n, N)); return r.sum(0) + r.max(0)
def wall_of_fire():            # (5d8 com save ao conjurar, tique extra de 5d8 SEM save em 50% dos alvos)
    return roll(5, 8), np.where(rng.random(N) < 0.5, roll(5, 8), 0)

# ---------------------------------------------------------------------------
# 3. Luta contra a horda
# ---------------------------------------------------------------------------
S = 1.0                        # escala de alvos (variações: 0,5 esparsa / 1 padrão / 1,5 agrupada)

def luta(L, usos):
    """Fração do HP total da horda removida.
    usos: lista de (alvos, seletiva, gerador_de_dano, CD, metade_no_sucesso); um uso por round.
    O gerador devolve o dano (com save) ou uma dupla (dano com save, dano extra sem save)."""
    hp0, ac, sv = CR[HORDA[L]]
    hp = np.full((N, NH), float(hp0)); tot = np.zeros(N)
    for r, (alvos, sel, ger, dc, metade) in enumerate(usos):
        fator = 1.0 if r == 0 else (0.75 if sel else 0.5)
        x = min(alvos * S, NH) * fator
        k = np.floor(x) + (rng.random(N) < x - np.floor(x))      # alvos sorteados
        base = ger()                                             # um rolamento por uso
        base, extra = base if isinstance(base, tuple) else (base, 0)
        vivos = hp > 0; ordem = np.cumsum(vivos, 1) - 1
        for j in range(NH):
            alvo = vivos[:, j] & (ordem[:, j] < k)
            ok = rng.integers(1, 21, N) + sv >= dc
            d = np.where(ok, base // 2 if metade else 0, base) + extra
            real = np.where(alvo, np.minimum(d, hp[:, j]), 0)
            hp[:, j] -= real; tot += real
    return tot.mean() / (NH * hp0)

def ataque(b, ac, dano):       # dano(m): m = 2 no crítico
    a = rng.integers(1, 21, N); crit = a == 20
    hit = crit | ((a != 1) & (a + b >= ac)); m = np.where(crit, 2, 1)
    return np.where(hit, dano(m), 0)

def cleave_horde_breaker(L, p=0.75):
    """John: 2º alvo colado em p dos turnos; arco SS +7, d8+14; 4 rounds."""
    return cleave_ataque(L, 7, '1d8+14', p)

def cleave_thunderclap(L, k=2):
    """Ravin: Thunderclap 2d6 (CD 16, Con, sem metade) em k inimigos colados,
    menos o dado extra do Booming Blade (d8, ataque +9) que ele deixa de usar; 4 rounds."""
    hp, ac, sv = CR[HORDA[L]]; tot = 0.0
    for _ in range(4):
        ok = rng.integers(1, 21, N) + sv >= 16
        tc = np.minimum(np.where(ok, 0, roll(2, 6)), hp).mean() * k
        tot += tc - ataque(9, ac, lambda m: roll(1, 8) * m).mean()
    return tot / (NH * hp)

# ---------------------------------------------------------------------------
# 4. Régua e nível equivalente
# ---------------------------------------------------------------------------
def ref_usos(L, n):
    slots = (max(TOP3[L]),) if n == 1 else TOP3[L][:n]
    return [(alvos_circulo(s), False, (lambda m=MULTI[s]: d6s(m)), cd(L), True) for s in slots]

def regua():
    return ({L: luta(L, ref_usos(L, 1)) for L in range(1, 21)},
            {L: luta(L, ref_usos(L, 3)) for L in range(1, 21)})

def nivel_eq(fr, ref):
    d = [fr[L] - ref[L] for L in range(1, 21)]
    if d[0] < 0: return round(0.5 * fr[1] / ref[1], 2)
    best = max(i for i in range(20) if d[i] >= 0)
    if best == 19: return 20.0
    a, b = d[best], d[best + 1]
    return round(best + 1 + a / (a - b), 2)

# ---------------------------------------------------------------------------
# 5. Camada genérica: a build descreve as áreas no JSON (nada de personagem fixo aqui)
# ---------------------------------------------------------------------------
import re

CENARIOS = {'esparsa': 0.5, 'padrao': 1.0, 'agrupada': 1.5}
N_MODO = {'rapido': 8000, 'completo': 40000}


def rola(expr, m=1):
    """'8d6', '1d8+14': rola N vezes; m multiplica os dados (crítico)."""
    tot = np.zeros(N)
    for sinal, termo in re.findall(r'([+-]?)([^+-]+)', str(expr).replace(' ', '')):
        k = -1 if sinal == '-' else 1
        mm = re.fullmatch(r'(\d*)d(\d+)', termo)
        tot = tot + k * (roll(int(mm.group(1) or 1), int(mm.group(2))) * m if mm else float(termo))
    return tot


def _gerador(u):
    def g():
        if u.get('dobra_maior_dado'):          # ex.: carga que dobra o maior dado da magia
            mm = re.fullmatch(r'(\d+)d(\d+)', u['dano']); r = rng.integers(1, int(mm.group(2)) + 1, (int(mm.group(1)), N))
            base = r.sum(0) + r.max(0)
        else:
            base = rola(u['dano']).astype(int)
        if 'extra_sem_save' in u:              # ex.: Wall of Fire, tique sem save em parte dos alvos
            e = u['extra_sem_save']
            return base, np.where(rng.random(N) < e.get('prob', 1), rola(e['dano']), 0)
        return base
    return g


def cleave_ataque(L, bonus, dano, p):
    """Ataque extra num 2º alvo colado em p dos turnos; 4 rounds."""
    hp, ac, sv = CR[HORDA[L]]; tot = 0.0
    for _ in range(4):
        tot += p * np.minimum(ataque(bonus, ac, lambda m: rola(dano, m)), hp).mean()
    return tot / (NH * hp)


def cleave_save(L, dano, dc, k, metade=False, custo=None):
    """Área pequena todo round em k inimigos colados, menos o que se deixa de fazer (custo: ataque trocado); 4 rounds."""
    hp, ac, sv = CR[HORDA[L]]; tot = 0.0
    for _ in range(4):
        ok = rng.integers(1, 21, N) + sv >= dc; base = rola(dano)
        tot += np.minimum(np.where(ok, base // 2 if metade else 0, base), hp).mean() * k
        if custo: tot -= ataque(custo['bonus'], ac, lambda m: rola(custo['dano'], m)).mean()
    return tot / (NH * hp)


_REGUA = {}


def _regua_cache(s, n):
    """Régua (1 uso, prioritária) por variação de horda e N; guardada em cache/."""
    import hashlib, json
    from pathlib import Path
    global S, N, rng
    chave = f'{s}|{n}'
    if chave in _REGUA: return _REGUA[chave]
    h = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:10]
    arq = Path(__file__).resolve().parents[1] / 'cache' / f'area-{h}.json'
    d = json.loads(arq.read_text()) if arq.exists() else {}
    if chave not in d:
        S, N, rng = s, n, np.random.default_rng(21)
        r1, r3 = regua()
        d[chave] = [[r1[L] for L in range(1, 21)], [r3[L] for L in range(1, 21)]]
        arq.parent.mkdir(exist_ok=True); arq.write_text(json.dumps(d))
    _REGUA[chave] = tuple({L: v[L - 1] for L in range(1, 21)} for v in d[chave])
    return _REGUA[chave]


def _por_cenario(v, i): return v[i] if isinstance(v, list) else v


def avaliar(spec, modo='rapido'):
    """spec: lista de áreas da linha. Cada uma:
      {"nome", "tipo": "explosao" | "prioritaria", "usos": [{"alvos", "seletiva", "dano", "cd", "metade"}...]}
      {"nome", "tipo": "cleave_ataque", "bonus", "dano", "p": [esparsa, padrão, agrupada]}
      {"nome", "tipo": "cleave_save", "dano", "cd", "alvos": [..3..], "metade", "custo_ataque": {"bonus", "dano"}}
    Nível da linha = a melhor área na horda padrão."""
    from .base import letra
    global S, N, rng
    n = N_MODO[modo]; out = []
    for a in spec:
        niveis = {}
        for i, (cen, s) in enumerate(CENARIOS.items()):
            r1, r3 = _regua_cache(s, n)
            S, N, rng = s, n, np.random.default_rng(21)
            t = a.get('tipo', 'explosao')
            if t in ('explosao', 'prioritaria'):
                usos = [(u['alvos'], u.get('seletiva', False), _gerador(u), u['cd'], u.get('metade', True)) for u in a['usos']]
                fr = {L: luta(L, usos) for L in range(1, 21)}
            elif t == 'cleave_ataque':
                fr = {L: cleave_ataque(L, a['bonus'], a['dano'], _por_cenario(a['p'], i)) for L in range(1, 21)}
            elif t == 'cleave_save':
                fr = {L: cleave_save(L, a['dano'], a['cd'], _por_cenario(a['alvos'], i), a.get('metade', False),
                                     a.get('custo_ataque')) for L in range(1, 21)}
            else:
                raise ValueError(f'área de tipo desconhecido: {t}')
            niveis[cen] = float(nivel_eq(fr, r3 if t == 'prioritaria' else r1))
        out.append(dict(nome=a.get('nome', t), tipo=t, nivel_eq=niveis['padrao'], rank=letra(niveis['padrao']), variacoes=niveis))
    if not out: return dict(nivel_eq=None, rank='-', areas=[])
    best = max(out, key=lambda x: x['nivel_eq'])
    return dict(nivel_eq=round(best['nivel_eq'], 1), rank=best['rank'], melhor=best['nome'], areas=out)
