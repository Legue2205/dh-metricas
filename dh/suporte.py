"""Suporte: dano equivalente por round (ofensivo = dano acrescentado aos aliados; defensivo = PV poupados).

Fórmula fechada, conforme a especificação de 10/11/2026 (planilha "Ranks de suporte"). Não conta o que o
controle já mede (turnos negados, ataques desviados). A build lista fontes; cada fonte usa um modelo.
"""
from .base import R, letra

H = dict(ACERTO=0.65, ATIVO=0.875, ALIADOS=3, EF_CURA=0.9, EF_PVT=0.75, F_SAVE=0.25, F_AURA=0.67, CUSTO_SAVE=1,
         LUTAS_SR=2, LUTAS_DIA=4)
H['VANT'] = (1 - (1 - H['ACERTO']) ** 2) / H['ACERTO'] - 1
# nível: (DPR do aliado, ataques, dano do inimigo por round, maior espaço, mod)
REGUA = {1: (8, 1, 14.5, 1, 3), 2: (10, 1, 20, 1, 3), 3: (12, 1, 25.5, 2, 3), 4: (15, 1, 31.5, 2, 4),
         5: (20, 2, 49, 3, 4), 6: (22, 2, 49, 3, 4), 7: (26, 2, 54.5, 4, 4), 8: (31, 2, 60.5, 4, 5),
         9: (34, 2, 66.5, 5, 5), 10: (37, 2, 72.5, 5, 5), 11: (45, 3, 78, 6, 5), 12: (52.5, 3, 89.5, 6, 5),
         13: (60, 3, 95.5, 7, 5), 14: (66.7, 3, 101.5, 7, 5), 15: (73.3, 3, 101.5, 8, 5), 16: (80, 3, 107, 8, 5),
         17: (86.7, 3, 118.5, 9, 5), 18: (93.3, 3, 126, 9, 5), 19: (100, 3, 126, 9, 5), 20: (106.7, 4, 136.5, 9, 5)}


def _regua(k):
    dpr, atq, inim, E, M = REGUA[k]; al = H['ALIADOS']
    cura = max(E * 2.5 + M, al * ((E - 2) * 2.5 + M) if E >= 3 else 0, al * ((E - 2) * 4.5 + M) if E >= 5 else 0,
               70 + 10 * (E - 6) if E >= 6 else 0)
    of = al * dpr * (2.5 * 0.05 / H['ACERTO']) * H['ATIVO']; de = cura * H['EF_CURA'] / R
    return of, de, of + de


REGUAS = [[_regua(k)[i] for k in range(1, 21)] for i in range(3)]  # of, def, tot


def _nivel(x, r):
    k = sum(1 for v in r if v <= x)
    if x <= 0: return 0.0
    if k == 0: return round(x / r[0], 1)
    if k >= 20: return 20.0
    return round(k + (x - r[k - 1]) / (r[k] - r[k - 1]), 1)


def _usos(f):
    """Usos por luta: direto, ou a partir de usos por dia / por descanso curto."""
    if 'usos_dia' in f: return f['usos_dia'] / H['LUTAS_DIA']
    if 'usos_descanso_curto' in f: return f['usos_descanso_curto'] / H['LUTAS_SR']
    return f.get('usos_luta', 1)


def valor(f, nivel):
    dpr, atq, inim, _, _ = REGUA[nivel]; dpa = dpr / (atq * H['ACERTO']); m = f['modelo']
    al = f.get('alvos', 1); u = _usos(f)
    if m == 'vantagem': return al * dpr * H['VANT'] * f['fracao']
    if m == 'bonus_continuo': return al * dpr * (f['bonus'] * 0.05 / H['ACERTO']) * H['ATIVO']
    if m == 'bonus_por_uso': return u / R * f['bonus'] * 0.05 * dpa
    if m == 'ataque_extra': return al * dpr / atq * H['ATIVO']
    if m == 'dano_por_acerto': return u * al * atq * H['ACERTO'] * f['dano_extra'] * H['ATIVO']
    if m == 'cura': return u * f['pv'] * H['EF_CURA'] / R
    if m == 'pv_temporario': return u * al * f['pv'] * H['EF_PVT'] / R
    if m == 'aura_saves': return inim * H['F_SAVE'] * H['F_AURA'] * f['bonus'] * 0.05 * H['CUSTO_SAVE']
    if m == 'valor_por_luta': return u * f['valor'] / R
    if m == 'fixo': return f['valor']                      # valor por round medido fora (documente em "nota")
    raise ValueError(f'suporte: modelo desconhecido "{m}"')


MODELOS = ('vantagem', 'bonus_continuo', 'bonus_por_uso', 'ataque_extra', 'dano_por_acerto', 'cura', 'pv_temporario',
           'aura_saves', 'valor_por_luta', 'fixo')


def avaliar(spec, nivel):
    """spec: {"fontes": [{"nome", "lado": "of"|"def", "modelo", ...}]}."""
    fs = [dict(nome=f.get('nome', f['modelo']), lado=f['lado'], valor=round(valor(f, nivel), 2)) for f in spec.get('fontes', [])]
    g = sum(f['valor'] for f in fs if f['lado'] == 'of'); h = sum(f['valor'] for f in fs if f['lado'] == 'def')
    no, nd, nt = _nivel(g, REGUAS[0]), _nivel(h, REGUAS[1]), _nivel(g + h, REGUAS[2])
    perfil = '-' if g + h == 0 else 'Amplificador' if no - nd >= 1.5 else 'Protetor' if nd - no >= 1.5 else 'Equilibrado'
    return dict(ofensivo=round(g, 2), defensivo=round(h, 2), total=round(g + h, 2), nivel_ofensivo=no, nivel_defensivo=nd,
                nivel_eq=nt, rank=letra(nt), perfil=perfil,
                fonte_principal=max(fs, key=lambda f: f['valor'])['nome'] if fs else '-', fontes=fs)
