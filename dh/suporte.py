"""Suporte: dano equivalente por round (ofensivo = dano acrescentado aos aliados; defensivo = PV poupados).

Fórmula fechada, conforme a especificação de 10/11/2026 (planilha "Ranks de suporte"). Não conta o que o
controle já mede (turnos negados, ataques desviados). A build lista fontes; cada fonte usa um modelo.
"""
from .base import R, letra

from .premissas import grupo as _grupo, valor as _p
H_ANTIGO = dict(ACERTO=0.65, ATIVO=0.875, ALIADOS=3, EF_CURA=0.9, EF_PVT=0.75, F_SAVE=0.25, F_AURA=0.67, CUSTO_SAVE=1,
         LUTAS_SR=2, LUTAS_DIA=4,
         # 16/11 — dados de vários usos (Bardic Inspiration e afins), resgates e levantar caídos:
         ESCOLHA=2.0,            # o jogador gasta o dado quando a rolagem parece perto: chance de virar ×2 frente a uma rolagem qualquer
         ACERTOS_INIM_ROUND=4,   # o dano inimigo do round chega em ~4 acertos (dano de um acerto inimigo = inim / 4)
         TURNOS_CONDICAO=1.5,    # save crítico falho (Hold Person, Hypnotic Pattern, medo): turnos do aliado perdidos
         TURNOS_LEVANTAR=1.0,    # levantar um caído devolve ~1 turno do aliado além dos PV
         P_ACERTO_INIM=0.6,      # chance de um ataque inimigo acertar o aliado
         PARCELA_FRENTE=0.35)    # parcela do dano inimigo que vai para um aliado da linha de frente
H = _grupo('suporte.h')   # premissas suporte.h.* (H_ANTIGO acima só como referência)
MIX_PADRAO = _p('suporte.mix_dado_multiuso')
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
    """Usos NA LUTA desta linha (18/11: suporte medido na luta em que é usado, como área e controle).
    - "usos_luta": direto.
    - "quando": "entre_lutas" (Song of Rest, PV temporário de descanso, cura depois da luta): o recurso não é gasto
      numa luta específica, então se espalha: usos_dia ÷ lutas do dia, usos_descanso_curto ÷ lutas por descanso.
    - em combate com "usos_descanso_curto": ÷ lutas por descanso (cada luta do descanso usa a sua parte).
    - em combate com "usos_dia": todos nesta luta (no máximo um por round). O plano do dia não pode pôr essa fonte
      em mais lutas do que ela tem usos (aviso do validador)."""
    from .premissas import P
    if 'usos_luta' in f: return f['usos_luta']
    if f.get('quando') == 'entre_lutas':
        if 'usos_dia' in f: return f['usos_dia'] / P('suporte.lutas_dia')
        if 'usos_descanso_curto' in f: return f['usos_descanso_curto'] / P('suporte.lutas_por_descanso_curto')
    if 'usos_descanso_curto' in f: return f['usos_descanso_curto'] / P('suporte.lutas_por_descanso_curto')
    if 'usos_dia' in f: return min(f['usos_dia'], R)
    return 1


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
    if m == 'dado_multiuso':
        # Dado gasto a critério do jogador (Bardic Inspiration): mistura de usos; cada uso em dano equivalente.
        d = f['dado_medio']; vira = min(1.0, 0.05 * d * H['ESCOLHA'])
        golpe_inim = inim / H['ACERTOS_INIM_ROUND']; critico = H['TURNOS_CONDICAO'] * dpr
        v = dict(dano=d, acerto=vira * dpa, ca=vira * golpe_inim, save_dano=vira * golpe_inim,
                 save_critico=vira * critico, counterspell=vira * critico)
        mix = f.get('mix', MIX_PADRAO)
        if abs(sum(mix.values()) - 1) > 0.01: raise ValueError('dado_multiuso: "mix" precisa somar 1')
        return u / R * sum(p * v[k] for k, p in mix.items())
    if m == 'resgate_condicao':
        # Reação que refaz um save falho contra uma condição (Countercharm 2024: medo/encantamento, com vantagem).
        p_ok = 1 - (1 - f.get('p_save', _p('suporte.padroes.resgate_p_save'))) ** (2 if f.get('vantagem', True) else 1)
        return f.get('p_evento', _p('suporte.padroes.resgate_p_evento')) * p_ok * H['TURNOS_CONDICAO'] * dpr / R
    if m == 'desvantagem_contra':
        # Ataques contra o aliado com desvantagem (Greater Invisibility, Blur...): PV que ele deixa de perder.
        p = f.get('p_acerto', H['P_ACERTO_INIM']); corte = 1 - p * p / p    # acerto com desvantagem = p²
        return al * f.get('fracao', 1) * inim * f.get('parcela', H['PARCELA_FRENTE']) * corte
    if m == 'levantar':
        # Cura num aliado caído: os PV + o turno que ele recupera.
        return u * (f['pv'] * H['EF_CURA'] + H['TURNOS_LEVANTAR'] * dpr) / R
    if m == 'cura_na_luta':
        # 19/11: cura que levanta um caído durante a luta. Usos limitados pelos caídos esperados (P_CAIDO) e pelo acesso:
        # distância + ação bônus (Healing Word) = 1; toque e/ou ação custam ACESSO_TOQUE / ACESSO_ACAO.
        usos = min(f.get('usos_luta', 1), H['P_CAIDO'])
        fa = (H['ACESSO_TOQUE'] if f.get('alcance', 'distancia') == 'toque' else 1) * (H['ACESSO_ACAO'] if f.get('acao', 'bonus') == 'acao' else 1)
        return usos * fa * (f['pv'] * H['EF_CURA'] + H['TURNOS_LEVANTAR'] * dpr) / R
    if m == 'fixo': return f['valor']                      # valor por round medido fora (documente em "nota")
    raise ValueError(f'suporte: modelo desconhecido "{m}"')


MODELOS = ('vantagem', 'bonus_continuo', 'bonus_por_uso', 'ataque_extra', 'dano_por_acerto', 'cura', 'pv_temporario',
           'aura_saves', 'valor_por_luta', 'fixo', 'dado_multiuso', 'resgate_condicao', 'levantar', 'cura_na_luta',
           'desvantagem_contra')


def avaliar(spec, nivel):
    """spec: {"fontes": [{"nome", "lado": "of"|"def", "modelo", ...}]}."""
    fs = [dict(nome=f.get('nome', f['modelo']), lado=f['lado'], valor=round(valor(f, nivel), 2)) for f in spec.get('fontes', [])]
    g = sum(f['valor'] for f in fs if f['lado'] == 'of'); h = sum(f['valor'] for f in fs if f['lado'] == 'def')
    no, nd, nt = _nivel(g, REGUAS[0]), _nivel(h, REGUAS[1]), _nivel(g + h, REGUAS[2])
    perfil = '-' if g + h == 0 else 'Amplificador' if no - nd >= 1.5 else 'Protetor' if nd - no >= 1.5 else 'Equilibrado'
    return dict(ofensivo=round(g, 2), defensivo=round(h, 2), total=round(g + h, 2), nivel_ofensivo=no, nivel_defensivo=nd,
                nivel_eq=nt, rank=letra(nt), perfil=perfil,
                fonte_principal=max(fs, key=lambda f: f['valor'])['nome'] if fs else '-', fontes=fs)
