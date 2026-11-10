"""Orçamento de recursos por hipótese (linha): nenhum recurso pode ser contado duas vezes.

Uma linha = uma hipótese de luta. Regras checadas:
  REAÇÃO (1 por round). A linha declara como a gasta:
      "reacao": [{"uso": "2º Sneak (ataque de reação)", "fracao": 1.0, "eixos": ["dano"]}]
    fracao = parte dos rounds em que a reação vai para esse uso; um mesmo uso pode render em mais de um eixo
    (o ataque de oportunidade do Sentinel dá dano E controle). A soma não passa de 1. O que sobrar
    (reacao_livre) é o que as reações de defesa (Shield, Uncanny Dodge, Absorb Elements, Counterspell) podem usar.
    Fontes de controle que dependem de reação (sentinela, parada_oa, counterspell) exigem um uso declarado
    com "controle" em eixos.
  ESPAÇOS DE MAGIA. Se a build declara "recursos": {"espacos": {"1": 4, "2": 3, ...}, "lutas_dia": 4},
    soma-se o que cada eixo da linha gasta numa luta e compara-se com o que cabe nela:
      "cenario": "dia_padrao" (padrão)  -> espaços do dia ÷ lutas_dia
      "cenario": "luta_prioritaria"     -> todos os espaços do dia nesta luta
    Um gasto pode usar espaço maior que o necessário. Eixos sem leitura automática declaram
    "usa": {"espacos": {"3": 1}} dentro do eixo.
"""
FONTES_REACAO = ('sentinela', 'parada_oa', 'counterspell')


def reacao_livre(linha):
    return max(0.0, 1.0 - sum(u.get('fracao', 1.0) for u in linha.get('reacao', [])))


def _espacos_fonte(f, magias):
    t = f['tipo']
    if t == 'melhor_de':
        ops = [_espacos_fonte(o, magias) for o in f['opcoes']]
        return max(ops, key=lambda g: sum(int(k) * v for k, v in g.items())) if ops else {}
    g = {}
    def soma(nv, q=1):
        if nv and nv > 0: g[str(nv)] = g.get(str(nv), 0) + q
    if t == 'alvo_unico':
        for s in f['slots']: soma(s)
    elif t in ('area', 'alvo_unico_direto'):
        soma(f.get('slot', magias[f['magia']]['nivel']))
    elif t == 'plano':
        for a in f['acoes']: soma(a.get('slot', magias[a['magia']]['nivel']))
    elif t == 'counterspell':
        soma(f.get('slot', 3), f.get('usos_luta', 1))
    for k, v in f.get('usa', {}).get('espacos', {}).items(): soma(int(k), v)
    return g


def espacos_gastos(linha, corpo, magias):
    """{nível: quantidade} gasto numa luta, por eixo."""
    out = {}
    def junta(eixo, g):
        if g: out[eixo] = {k: out.get(eixo, {}).get(k, 0) + v for k, v in g.items()} | {k: v for k, v in out.get(eixo, {}).items() if k not in g}
    for eixo in ('dano', 'defesa', 'controle', 'saves', 'area', 'suporte'):
        e = linha.get(eixo)
        if isinstance(e, dict): junta(eixo, dict(e.get('usa', {}).get('espacos', {})))
    for f in linha.get('controle', {}).get('fontes', []): junta('controle', _espacos_fonte(f, magias))
    livre = reacao_livre(linha) > 0
    for r in linha.get('defesa', {}).get('reacoes', []) if livre else []:
        if r['tipo'] == 'shield': junta('defesa', {str(r.get('slot', 1)): r.get('usos_luta', 1)})
    if 'saves' in linha and livre:
        sv = dict(corpo.get('saves', {})); sv.update(linha['saves'])
        g = {}
        if sv.get('absorb'): g['1'] = sv['absorb']
        if sv.get('contra'): g[str(sv.get('contra_nivel', 3))] = g.get(str(sv.get('contra_nivel', 3)), 0) + sv['contra']
        junta('saves', g)
    for a in linha.get('area', []) if isinstance(linha.get('area'), list) else []:
        for u in a.get('usos', []):
            if 'slot' in u: junta('area', {str(u['slot']): 1})
    return out


def checar(b, magias):
    """(erros, avisos). Erro: reação contada duas vezes. Aviso: os eixos da linha, somados, gastam mais espaços
    do que cabem na luta: cada eixo vale sozinho, mas a linha não pode somar os eixos."""
    erros = []; avisos = []; rec = b.get('recursos', {}); esp = {int(k): v for k, v in rec.get('espacos', {}).items()}
    lutas = rec.get('lutas_dia', 4)
    for l in b['linhas']:
        nome = f"linha {l.get('id')}"
        usos = l.get('reacao', [])
        if sum(u.get('fracao', 1.0) for u in usos) > 1 + 1e-9:
            erros.append(f'{nome}: a reação está contada mais de uma vez (soma das frações > 1)')
        for u in usos:
            if not u.get('eixos'): erros.append(f'{nome}: uso de reação "{u.get("uso")}" sem "eixos"')
        def tem(eixo): return any(eixo in u.get('eixos', []) for u in usos)
        def fontes(fs):
            for f in fs:
                yield f
                yield from fontes(f.get('opcoes', []))
        for f in fontes(l.get('controle', {}).get('fontes', [])):
            if f['tipo'] in FONTES_REACAO and not tem('controle'):
                erros.append(f'{nome}: a fonte de controle "{f.get("nome", f["tipo"])}" usa a reação; '
                             f'declare-a em "reacao" com "controle" em eixos')
        hard = l.get('controle', {}).get('atencao', {}).get('hard')
        if hard and not tem('controle'):
            erros.append(f'{nome}: controle.atencao.hard (parar inimigos com a reação) exige um uso de reação com "controle"')
        if esp:
            gasto = {}
            for g in espacos_gastos(l, b['corpo'], magias).values():
                for k, v in g.items(): gasto[int(k)] = gasto.get(int(k), 0) + v
            fator = 1.0 if l.get('cenario', 'dia_padrao') == 'luta_prioritaria' else 1.0 / lutas
            for nv in sorted(gasto, reverse=True):   # gasto de nível >= nv tem que caber nos espaços >= nv
                precisa = sum(v for k, v in gasto.items() if k >= nv); tem_ = sum(v for k, v in esp.items() if k >= nv) * fator
                if precisa > tem_ + 1e-9:
                    avisos.append(f'{nome}: gasta {precisa:g} espaço(s) de nível {nv}+ numa luta, mas cabem {tem_:g} '
                                 f'({l.get("cenario", "dia_padrao")}); mude o cenário, corte um gasto ou divida em linhas')
                    break
    return erros, avisos


def resumo(linha, corpo, magias, soma_eixos=True):
    return dict(cenario=linha.get('cenario', 'dia_padrao'), reacao=linha.get('reacao', []), soma_eixos=soma_eixos,
                reacao_livre=round(reacao_livre(linha), 2), espacos_por_eixo=espacos_gastos(linha, corpo, magias))
