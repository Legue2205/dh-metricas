"""Dano: DPR em 9 CAs e nível equivalente pelas rampas da planilha "Ranks de dano".

Dois jeitos de informar o dano de uma linha:
  - "medido": lista com os 9 DPRs já calculados (migração das linhas antigas, que não tinham motor salvo);
  - "ataques"/"por_turno"/"por_luta"/"automatico": o motor calcula em fórmula fechada (valor esperado).
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
    return round(max(nb, np_), 1), perfil


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
    c0 = (21 - a.get('crit_em', 20)) / 20; v = a.get('vantagem', 0.0)
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


def dpr(spec, ca, lutas_dia=4, invocacoes=()):
    if 'medido' in spec: return spec['medido'][CAS.index(ca)]
    total = 0.0; nenhum = 1.0; pc = []
    for a in spec.get('ataques', []):          # n pode ser fracionário (ex.: Action Surge = 2 ataques ÷ 4 rounds)
        n = a.get('n', 1); p, c, e = _ataque(a, ca)
        total += n * e; nenhum *= (1 - p) ** n; pc.append((n * p, n * c))
    algum = 1 - nenhum
    crit_rel = (sum(c for _, c in pc) / sum(p for p, _ in pc)) if pc and sum(p for p, _ in pc) else 0.0
    for x in spec.get('por_turno', []):        # Sneak Attack e afins: 1× por turno no 1º acerto
        avg, dad = dados(x['dano'])
        total += x.get('prob', 1.0) * algum * (avg + crit_rel * dad)
    for x in spec.get('por_luta', []):         # smites e afins: usos por luta espalhados nos R rounds
        avg, dad = dados(x['dano'])
        usos = x['usos'] if 'usos' in x else x['usos_dia'] / lutas_dia   # recurso diário repartido pelas lutas
        total += _usados(usos, pc, sum(a.get('n', 1) for a in spec.get('ataques', []))) / R * (avg + crit_rel * dad)
    if 'automatico' in spec: total += dados(spec['automatico'])[0]
    for inv in invocacoes:                     # criaturas invocadas atacam por conta própria
        if 'ataque' in inv: total += inv['quantidade'] * inv['ataque'].get('n', 1) * _ataque(inv['ataque'], ca)[2]
    return round(total, 1)


def avaliar(spec, lutas_dia=4, invocacoes=()):
    """invocacoes só somam quando o dano é calculado; em 'medido' já estão dentro do número."""
    lista = [dpr(spec, ca, lutas_dia, invocacoes) for ca in CAS]
    nv, perfil = nivel_equivalente(lista)
    return dict(dpr={f'CA {ca}': v for ca, v in zip(CAS, lista)}, nivel_eq=nv, rank=letra(nv), perfil=perfil)
