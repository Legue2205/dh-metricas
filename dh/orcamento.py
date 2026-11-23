"""Orçamento de recursos por hipótese (linha): nenhum recurso pode ser contado duas vezes.

Uma linha = uma hipótese de luta. Regras checadas:
  REAÇÃO (1 por round). A linha declara como a gasta:
      "reacao": [{"uso": "2º Sneak (ataque de reação)", "fracao": 1.0, "eixos": ["dano"]}]
    fracao = parte dos rounds em que a reação vai para esse uso; um mesmo uso pode render em mais de um eixo
    (o ataque de oportunidade do Sentinel dá dano E controle). A soma não passa de 1. O que sobrar
    (reacao_livre) é o que as reações de defesa (Shield, Uncanny Dodge, Absorb Elements, Counterspell) podem usar.
    Fontes de controle que dependem de reação (sentinela, parada_oa, counterspell) exigem um uso declarado
    com "controle" em eixos.
  AÇÃO BÔNUS: mesmo formato da reação ("acao_bonus": [{"uso", "fracao", "eixos"}]); a soma não passa de 1.
  CONCENTRAÇÃO: uma por vez. Fontes de controle com magia de concentração contam uma cada; dano, área e
    suporte declaram "concentracao": "<nome>". Duas distintas na mesma linha = erro.
  ESPAÇOS DE MAGIA e outros recursos: quem decide é o plano do dia da build (ver planos.py). Aqui só se soma
    o que cada linha gasta numa luta: lido das fontes de controle, reações de defesa, saves e áreas ("slot"),
    mais "usa": {"espacos": {"3": 1}} dentro de um eixo e "usa": {"furia": 1} na linha.
"""
import json
import re
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


def _conc_fonte(f, magias):
    ids = set()
    for k in ('magia',):
        if f.get(k): ids.add(f[k])
    ids.update(f.get('magias', []))
    ids.update(a['magia'] for a in f.get('acoes', []))
    if 'solo' in f: ids.add(f['solo']['magia'])
    out = {i for i in ids if magias.get(i, {}).get('conc')}
    for o in f.get('opcoes', []): out |= _conc_fonte(o, magias)
    return out


def _conc_com_topos(linha, magias):
    """[(token, topos)] — topos = conjunto de topologias onde a concentração acontece (None = todas)."""
    out = []
    for f in linha.get('controle', {}).get('fontes', []):
        c = _conc_fonte(f, magias)
        if c: out.append(('|'.join(sorted(c)), frozenset(f['topos']) if 'topos' in f else None))
    extras = []
    d = linha.get('dano')
    if isinstance(d, dict) and d.get('concentracao'): extras.append(d)
    extras += [f for f in (linha.get('suporte') or {}).get('fontes', []) if f.get('concentracao')]
    extras += [a for a in linha.get('area', []) if isinstance(a, dict) and a.get('concentracao')]
    for x in extras:
        n = x['concentracao']
        if not any(n in t.split('|') for t, _ in out):
            out.append((n, frozenset(x['topos']) if 'topos' in x else None))
    return out


def conflitos_concentracao(linha, magias):
    """Pares de concentrações que podem estar ativas na mesma luta (topologias que se cruzam)."""
    cs = _conc_com_topos(linha, magias); out = []
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            a, b = cs[i][1], cs[j][1]
            if a is None or b is None or a & b: out.append((cs[i][0], cs[j][0]))
    return out


def concentracoes(linha, magias):
    """Concentrações distintas que a linha mantém ao mesmo tempo. Cada fonte de controle conta uma (as magias
    dentro dela se revezam); dano, área e suporte declaram "concentracao": "<nome>" (o mesmo nome = a mesma)."""
    toks = []
    for f in linha.get('controle', {}).get('fontes', []):
        c = _conc_fonte(f, magias)
        if c: toks.append('|'.join(sorted(c)))
    nomes = []
    d = linha.get('dano')
    if isinstance(d, dict) and d.get('concentracao'): nomes.append(d['concentracao'])
    nomes += [f['concentracao'] for f in (linha.get('suporte') or {}).get('fontes', []) if f.get('concentracao')]
    nomes += [a['concentracao'] for a in linha.get('area', []) if isinstance(a, dict) and a.get('concentracao')]
    for n in nomes:
        if not any(n in t.split('|') for t in toks): toks.append(n)
    return toks


def _norm(x): return re.sub(r'[^a-z]', '', x.lower())


def concentracao_por_nome(linha, magias):
    """M5 (23/11): magias de concentração RAW (lista _concentracao_nomes do magias.json) em entradas de área, suporte
    e invocação que NÃO declararam "concentracao" nem já aparecem como concentração da linha (nomes normalizados)."""
    nomes = tuple(n.lower() for n in _NOMES_CONC())
    ja = {_norm(p) for t in concentracoes(linha, magias) for p in t.split('|')}
    out = set()
    ents = [x for x in (linha.get('area') or []) if isinstance(x, dict)]
    ents += [f for f in (linha.get('suporte') or {}).get('fontes', [])] if isinstance(linha.get('suporte'), dict) else []
    ents += [i for i in linha.get('invocacoes', []) or []]
    for x in ents:
        n = re.sub(r'\s*\(.*', '', x.get('nome', '')).strip()
        if x.get('concentracao') or not n.lower().startswith(nomes): continue
        if any(_norm(n).startswith(j) or j.startswith(_norm(n)) for j in ja if j): continue
        out.add(n)
    return out


_CACHE_NOMES = None


def _NOMES_CONC():
    global _CACHE_NOMES
    if _CACHE_NOMES is None:
        from pathlib import Path
        _CACHE_NOMES = json.loads((Path(__file__).parent / 'controle' / 'magias.json').read_text(encoding='utf-8')).get(
            '_concentracao_nomes', {}).get('nomes', [])
    return _CACHE_NOMES


def checar(b, magias):
    """(erros, avisos). Erro: reação contada duas vezes. Espaços não geram erro: viram a tag de orçamento."""
    erros = []; avisos = []
    for l in b['linhas']:
        nome = f"linha {l.get('id')}"
        for chave, rot in (('reacao', 'a reação'), ('acao_bonus', 'a ação bônus')):
            us = l.get(chave, [])
            if sum(u.get('fracao', 1.0) for u in us) > 1 + 1e-9:
                erros.append(f'{nome}: {rot} está contada mais de uma vez (soma das frações > 1)')
            for u in us:
                if not u.get('eixos'): erros.append(f'{nome}: uso de {chave} "{u.get("uso")}" sem "eixos"')
        for a, c in conflitos_concentracao(l, magias):
            erros.append(f'{nome}: mais de uma concentração ao mesmo tempo ({a}; {c}); '
                         f'separe em linhas, junte as opções num "melhor_de" ou separe por "topos"')
        nc = concentracao_por_nome(l, magias)   # M5 (23/11): só aviso (podem ser magias lançadas uma depois da outra)
        if nc and len(nc) + len(conflitos_base := concentracoes(l, magias)) > 1:
            avisos.append(f'{nome}: concentração não declarada reconhecida pelo nome ({", ".join(sorted(nc))}) junto de '
                          f'{len(conflitos_base) + len(nc) - 1} outra(s); declare "concentracao" na entrada ou separe em linhas')
        usos = l.get('reacao', [])
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
    return erros, avisos


def resumo(linha, b, magias):
    return dict(reacao=linha.get('reacao', []), acao_bonus=linha.get('acao_bonus', []), concentracao=concentracoes(linha, magias), reacao_livre=round(reacao_livre(linha), 2),
                espacos_por_eixo=espacos_gastos(linha, b['corpo'], magias),
                outros={k: v for k, v in linha.get('usa', {}).items() if k != 'espacos'})
