"""Dano: DPR em 9 CAs e nível equivalente pelas rampas da planilha "Ranks de dano".

Dois jeitos de informar o dano de uma linha:
  - "medido": lista com os 9 DPRs já calculados (migração das linhas antigas, que não tinham motor salvo);
  - "ataques"/"por_turno"/"por_luta"/"automatico"/"com_save": o motor calcula em fórmula fechada (valor esperado).
Campos de "ataques": n (fracionário ok), bonus, dano, crit_em, dados_crit, vantagem (0–1 ou prob combinada), round1 (D12), elven_accuracy,
poder [-5, 10] (GWM/Sharpshooter: usa o modo que rende mais em cada CA).
"por_turno": 1× por turno no 1º acerto (Sneak Attack; prob = chance de ter o gatilho). "por_luta": smites (usos ou usos_dia).
"com_save": [{"n", "cd", "save": "Sab", "dano", "meio": false}] — truques/magias de alvo único com save.
"dado_no_erro": {"dado": D, "usos": U} — depois de errar o último ataque do turno sem nenhum acerto antes, soma 1dD ao
acerto; o dado só é gasto se virar acerto (Homing Strikes do Soulknife). U = usos por luta; o acerto convertido traz o
dano da arma e o 1× por turno (Sneak) que ainda não saiu.
"focused_aim": {"ki": K, "max": 3, "por_ponto": 2} — gasta até K pontos por luta transformando erros por pouco em acertos
(Focused Aim do Monk, Tasha's; +2 por ki, até 3): primeiro os erros por 1–2 (1 ki), depois por 3–4 (2), por 5–6 (3).
Fúria, Dueling, Hex etc. entram na string de dano ("1d8+2+1d6"); escala de truque por nível vai no patch da progressão.
O nível equivalente é a mesma conta da coluna U da planilha (porta da fórmula LET/LAMBDA).
"""
import re

from .base import R, letra, p_acerto

CAS = [11, 12, 15, 16, 18, 20, 22, 24, 25]
# (CA, DPR mínimo, nível) — aba Rampas
TRONCO = [(11, 4, 0.5), (12, 8, 1), (15, 12, 3), (15, 15, 4), (15, 20, 5)]
BRUTA = TRONCO + [(16, 22, 6), (16, 26, 7), (16, 31, 8), (16, 37, 10), (16, 45, 11), (16, 60, 13), (16, 80, 16)]
PRECISA = TRONCO + [(18, 19, 6), (18, 22, 7), (20, 23, 8), (20, 28, 10), (22, 29, 11), (24, 31, 13), (25, 40, 16)]


def _degraus(dpr, rampa):
    d = [dpr[CAS.index(ca)] for ca, _, _ in rampa]; t = [x for _, x, _ in rampa]; lv = [x for _, _, x in rampa]
    n = len(t); k = next((i for i in range(n) if d[i] < t[i]), n)
    if k == 0: return 0.5 * d[0] / t[0]
    if k == n: return min(20.0, lv[-1] + (d[-1] - t[-1]) / (t[-1] - t[-2]) * (lv[-1] - lv[-2]))
    a = d[k]; b = t[k - 1] * a / d[k - 1]
    return lv[k - 1] + max(0.0, min(1.0, (a - b) / (t[k] - b))) * (lv[k] - lv[k - 1])


def nivel_equivalente(dpr):
    nb, np_ = _degraus(dpr, BRUTA), _degraus(dpr, PRECISA)
    lb, lp = letra(nb), letra(np_)
    perfil = 'Equilibrado' if lb == lp else ('Bruto' if nb > np_ else 'Preciso')
    from .premissas import P          # D1 (23/11): mistura ponderada das rampas (antes: o máximo)
    beta = P('dano.peso_rampa_bruta')
    return round(beta * nb + (1 - beta) * np_, 1), perfil


def prob(x):
    """Probabilidade de julgamento (D11, 24/11): número, ou combinação de fontes (premissas entram como {"$p": nome},
    resolvidas ao carregar a build): {"ou": [p1, p2, …]} = chance de ao menos uma valer (1 − Π(1 − pᵢ));
    {"soma": [p, ajuste, …]} = soma limitada a [0, 1] (ajuste de subclasse)."""
    if isinstance(x, (int, float)): return x
    if 'ou' in x:
        r = 1.0
        for y in x['ou']: r *= 1 - prob(y)
        return 1 - r
    return max(0.0, min(1.0, sum(prob(y) for y in x.get('soma', []))))


def vantagem(a): return prob(a.get('vantagem', 0.0))


# ---------------- DPR em fórmula fechada ----------------
_DADO = re.compile(r'(\d*)d(\d+)')


def dados(expr):
    """'2d6+1d8+5' -> (média total, média só dos dados). Aceita número puro."""
    expr = str(expr).replace(' ', '')
    tot = dad = 0.0
    for termo in re.findall(r'[+-]?[^+-]+', expr):
        s = -1 if termo.startswith('-') else 1; termo = termo.lstrip('+-')
        m = _DADO.fullmatch(termo)
        if m:
            q = int(m.group(1) or 1); f = int(m.group(2)); v = q * (f + 1) / 2
            tot += s * v; dad += s * v
        else:
            tot += s * float(termo)
    return tot, dad


def _ataque1(a, ca, bonus, fixo):
    avg, dad = dados(a['dano'])
    if 'dados_crit' in a: dad = dados(a['dados_crit'])[1]
    c0 = (21 - a.get('crit_em', 20)) / 20; v = vantagem(a)
    k = 3 if a.get('elven_accuracy') else 2            # dados rolados quando há vantagem
    p0 = p_acerto(bonus, ca)
    p = (1 - v) * p0 + v * (1 - (1 - p0) ** k)
    c = (1 - v) * c0 + v * (1 - (1 - c0) ** k)
    c = min(c, p)
    return p, c, p * (avg + fixo) + c * dad


def _ataque(a, ca):
    """Com "poder": [-5, 10] (GWM/Sharpshooter), usa o modo que rende mais contra aquela CA."""
    op = [_ataque1(a, ca, a['bonus'], 0)]
    if 'poder' in a: op.append(_ataque1(a, ca, a['bonus'] + a['poder'][0], a['poder'][1]))
    return max(op, key=lambda x: x[2])


def _usados(usos, pc, natq):
    """Quantos usos 'no acerto' (smite etc.) saem numa luta de R rounds: E[min(usos, acertos)].
    O recurso é guardado para o próximo acerto, então só se perde se os acertos da luta não bastarem."""
    from math import ceil, comb, floor
    media = R * sum(p for p, _ in pc)
    if media <= 0: return 0.0
    n = max(1, ceil(R * natq), ceil(media)); p = min(1.0, media / n)
    def e(u): return sum(min(u, k) * comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1))
    lo = floor(usos); return e(lo) + (usos - lo) * (e(lo + 1) - e(lo))


def _dado_no_erro(f, ataques, por_turno, ca):
    """Valor esperado por round de somar 1dD a um último ataque errado (sem acerto antes no turno); usos U por luta."""
    D = f['dado']; U = f.get('usos', 0)
    if U <= 0 or not ataques: return 0.0
    a = ataques[-1]; b = a['bonus']; v = vantagem(a); k = 3 if a.get('elven_accuracy') else 2
    pr = {r: (1 - v) / 20 + v * ((r / 20) ** k - ((r - 1) / 20) ** k) for r in range(1, 21)}
    conv = sum(pr[r] * sum(1 for j in range(1, D + 1) if r + b + j >= ca) / D
               for r in range(2, 20) if r + b < ca)        # nat 1 não converte; nat 20 já acerta
    outros = 1.0
    for x in ataques[:-1]: outros *= (1 - _ataque(x, ca)[0]) ** x.get('n', 1)
    if a.get('n', 1) > 1: outros *= (1 - _ataque(a, ca)[0]) ** (a['n'] - 1)
    val = dados(a['dano'])[0] + sum(prob(x.get('prob', 1.0)) * dados(x['dano'])[0] for x in por_turno if x.get('gatilho') != 'critico')
    return min(conv * outros, U / R) * val


def _focused(f, ataques, ca):
    """Valor esperado por round de converter erros por pouco em acertos com um orçamento de K pontos por luta."""
    K = f.get('ki', 0); passo = f.get('por_ponto', 2); mx = f.get('max', 3)
    if K <= 0 or not ataques: return 0.0
    N = sum(a.get('n', 1) for a in ataques)
    hitd = sum(a.get('n', 1) * (dados(a['dano'])[0] + (a['poder'][1] if 'poder' in a and
               _ataque1(a, ca, a['bonus'] + a['poder'][0], a['poder'][1])[2] > _ataque1(a, ca, a['bonus'], 0)[2] else 0))
               for a in ataques) / N
    ganho = 0.0
    for custo in range(1, mx + 1):              # faixa de erro (custo-1)*passo+1 .. custo*passo abaixo da CA
        q = sum(a.get('n', 1) * sum(1 for r in range(2, 20) if ca - custo * passo <= r + a['bonus'] < ca - (custo - 1) * passo)
                for a in ataques) / 20          # erros nessa faixa por round
        conv = min(K / custo, R * q); K -= conv * custo; ganho += conv * hitd
        if K <= 1e-9: break
    return ganho / R


def save_alvo(ca, atributo):
    """Save médio do alvo típico com essa CA (medianas do Monster Manual em base.CRT; acima de CA 19, +1 por ponto)."""
    from .base import CRT, SAVE_TIPO
    w = SAVE_TIPO.get(atributo, 0.5)
    crs = [cr for cr, v in CRT.items() if v[0] == ca]
    extra = 0.0
    if not crs:
        if ca > max(v[0] for v in CRT.values()): crs = [max(CRT)]; extra = ca - CRT[max(CRT)][0]
        else: crs = [min(CRT, key=lambda cr: (abs(CRT[cr][0] - ca), cr))]
    return sum(CRT[cr][2] + w * (CRT[cr][3] - CRT[cr][2]) for cr in crs) / len(crs) + extra


def _com_save(x, ca):
    """Dano de alvo único com save (Toll the Dead, Sacred Flame, Blight…): falha = tudo, sucesso = metade se "meio"."""
    avg = dados(x['dano'])[0]
    falha = max(0.0, min(1.0, (x['cd'] - save_alvo(ca, x.get('save', 'Des')) - 1) / 20))
    v = x.get('vantagem_save', 0.0)                      # desvantagem do alvo no save (ex.: Hex) entra como negativo
    if v: falha = max(0.0, min(1.0, falha + v * falha * (1 - falha)))
    return x.get('n', 1) * avg * (falha + (1 - falha) * (0.5 if x.get('meio') else 0.0))


def _peso_inicio(u):
    """D12 (24/11): rounds pesam [w, 1, 1, …] (w = dano.peso_round1), normalizados para o dano constante não mudar.
    Fator do dano que sai nos primeiros acertos da luta: u usos gastos nos u primeiros rounds (u ≤ 1: só no 1º)."""
    from .premissas import P
    w = P('dano.peso_round1'); k = min(max(u, 1.0), R)
    return R / (w + R - 1) * (w + k - 1) / k


def _peso_round(r):
    """Peso do round r (1..R) para o que sai nos primeiros acertos da luta (u usos nos k = min(max(u, 1), R) primeiros
    rounds, por igual): soma R sobre os rounds, então a média dos rounds é o DPR puro."""
    def pi(u):
        k = min(max(u, 1.0), R)
        return R / k * min(1.0, max(0.0, k - (r - 1)))
    return pi


def dpr(spec, ca, lutas_dia=4, invocacoes=(), regua=False, peso=None):
    """DPR esperado na CA. regua=True: com o peso do 1º round (D12), só para o nível da régua; o DPR mostrado é o puro.
    peso: função u → fator do que sai nos primeiros acertos (perfil por round, Etapa D)."""
    if 'medido' in spec: return spec['medido'][CAS.index(ca)]
    pi = peso or (_peso_inicio if regua else (lambda u: 1.0))
    total = 0.0; nenhum = 1.0; sem_crit = 1.0; pc = []
    for a in spec.get('ataques', []):          # n pode ser fracionário (ex.: Action Surge = 2 ataques ÷ 4 rounds)
        n = a.get('n', 1); p, c, e = _ataque(a, ca)
        total += n * e * (pi(1) if a.get('round1') else 1.0)   # D12: ataque só do 1º round (Dread Ambusher)
        nenhum *= (1 - p) ** n; sem_crit *= (1 - c) ** n; pc.append((n * p, n * c))
    algum = 1 - nenhum
    crit_rel = (sum(c for _, c in pc) / sum(p for p, _ in pc)) if pc and sum(p for p, _ in pc) else 0.0
    for x in spec.get('por_turno', []):        # Sneak Attack e afins: 1× por turno no 1º acerto
        avg, dad = dados(x['dano'])
        if x.get('gatilho') == 'critico':      # ex.: Piercer, dado extra no 1º crítico do turno (não dobra)
            total += prob(x.get('prob', 1.0)) * (1 - sem_crit) * avg; continue
        total += prob(x.get('prob', 1.0)) * algum * (avg + crit_rel * dad)
    for x in spec.get('por_luta', []):         # smites e afins: usos por luta espalhados nos R rounds
        avg, dad = dados(x['dano'])
        usos = x['usos'] if 'usos' in x else x['usos_dia'] / lutas_dia   # recurso diário repartido pelas lutas
        u = _usados(usos, pc, sum(a.get('n', 1) for a in spec.get('ataques', [])))
        total += u / R * (avg + crit_rel * dad) * pi(u)   # D12: gasto nos primeiros acertos
    if 'automatico' in spec: total += dados(spec['automatico'])[0]
    for x in spec.get('com_save', []): total += _com_save(x, ca)
    if 'focused_aim' in spec: total += _focused(spec['focused_aim'], spec.get('ataques', []), ca)
    if 'dado_no_erro' in spec: total += _dado_no_erro(spec['dado_no_erro'], spec.get('ataques', []), spec.get('por_turno', []), ca)
    if invocacoes:
        from .premissas import P
        viva = P('invocacao.fracao_viva')      # 25/11: a criatura morre/some antes do fim da luta às vezes
    for inv in invocacoes:                     # criaturas invocadas atacam por conta própria
        if 'ataque' in inv: total += viva * inv['quantidade'] * inv['ataque'].get('n', 1) * _ataque(inv['ataque'], ca)[2]
    return round(total, 1)


def avaliar(spec, lutas_dia=4, invocacoes=()):
    """invocacoes só somam quando o dano é calculado; em 'medido' já estão dentro do número."""
    bruto = [dpr(spec, ca, lutas_dia, invocacoes) for ca in CAS]
    lista = [dpr(spec, ca, lutas_dia, invocacoes, regua=True) for ca in CAS]   # D12: o nível usa o DPR com peso do 1º round
    nv, perfil = nivel_equivalente(lista)
    out = dict(dpr={f'CA {ca}': v for ca, v in zip(CAS, bruto)}, nivel_eq=nv, rank=letra(nv), perfil=perfil,
               nivel_bruta=round(_degraus(lista, BRUTA), 1), nivel_precisa=round(_degraus(lista, PRECISA), 1),
               medido='medido' in spec)
    if lista != bruto: out['dpr_regua'] = {f'CA {ca}': v for ca, v in zip(CAS, lista)}
    if 'medido' not in spec:   # Etapa D (25/11): dano por round (burst do 1º round × demais), só quando não é constante
        pr = {f'CA {ca}': [dpr(spec, ca, lutas_dia, invocacoes, peso=_peso_round(r)) for r in range(1, R + 1)] for ca in CAS}
        if any(len(set(v)) > 1 for v in pr.values()): out['por_round'] = pr
    return out
