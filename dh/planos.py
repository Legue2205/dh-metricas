"""Plano de orçamento do dia: a decisão de como gastar recursos é da build, escrita no JSON.

Tag = premissa diária. Cada combate do plano aponta para uma linha (hipótese) da build, e pode levar linhas extras
(D9, 23/11: {"linha": "controle", "extras": ["area"]} = mais de uma magia na luta; valor e gasto das extras entram
pelo ganho marginal sobre a linha principal):
  "planos": {"padrao": {"combates": ["marcial", "caster", "marcial", {"linha": "caster", "nota": "gasta tudo"}],
                        "hypercharged": 1.5}}        # opcional: hipótese de acesso a mais recursos
O livro-caixa desconta, combate a combate, o que cada linha gasta (espaços de magia de todos os eixos e
"usa" da linha, ex. {"furia": 1}); descanso curto devolve o que tem "volta": "curto". Gastar o que não tem = erro.
O que sobra no fim do dia é a "sobra para utilidade". Resultado por eixo: média do dia ponderada pelo peso do
combate, e a média de cada categoria em separado.
"""
from . import orcamento

SR = 'SR'
TAGS_ANTIGO = {  # (categoria, peso) na ordem do dia; SR = descanso curto
    'padrao': [('np', 1), ('p', 2), SR, ('np', 1), ('p', 2)],
    'combate_unico': [('p', 1)],
    'dia_longo': [('np', 1), ('np', 1), ('mod', 2), SR, ('np', 1), ('mod', 2), ('mod', 2), SR, ('mod', 2), ('boss', 4)],
}
from .premissas import valor as _p
TAGS = {k: [x if x == SR else tuple(x) for x in v] for k, v in _p('planos.dias').items()}   # premissa planos.dias
CATEGORIAS = {'np': 'não prioritário', 'p': 'prioritário', 'mod': 'moderado', 'boss': 'boss'}
EIXOS = [('dano', None), ('defesa', None), ('saves', 'resiliencia'), ('saves', 'vontade'), ('controle', 'campo'), ('controle', 'corpo'),
         ('area', None), ('suporte', None)]


def _entrada(c): return c if isinstance(c, dict) else {'linha': c}


def base_id(b):
    """Linha à vontade da build (D9: referência do ganho marginal das linhas extras de uma luta)."""
    for l in b['linhas']:
        if l.get('principal'): return l['id']
    return b['linhas'][0]['id']


def _marginal(gj, gb):
    """Gasto marginal de uma linha extra sobre a principal (D9): o que a principal já gasta não se repete."""
    return {k: max(0.0, v - gb.get(k, 0)) for k, v in gj.items() if v - gb.get(k, 0) > 1e-9}


def _gasto(linha, corpo, magias, entrada):
    if 'gasta' in entrada or 'gasta' in linha:      # no combate do plano > na linha (gasto declarado da hipótese)
        g = dict(entrada.get('gasta', linha.get('gasta'))); esp = {int(k): v for k, v in g.pop('espacos', {}).items()}
        return esp, g
    esp = {}
    for por_eixo in orcamento.espacos_gastos(linha, corpo, magias).values():
        for k, v in por_eixo.items(): esp[int(k)] = esp.get(int(k), 0) + v
    return esp, {k: v for k, v in linha.get('usa', {}).items() if k != 'espacos'}


def _seq(tag):
    """Estrutura do dia do plano. "foco_<eixo>": o dia padrão com um único foco (anéis externo e interno)."""
    if tag in TAGS: return TAGS[tag]
    return TAGS['padrao'] if tag.startswith('foco_') else None


def livro_caixa(b, tag, magias):
    """(erros, combates, sobra). combates: [{linha, categoria, peso, gasto}]."""
    plano = b['planos'][tag]; rec = b.get('recursos', {}); hyper = plano.get('hypercharged', 1)
    linhas = {l['id']: l for l in b['linhas']}
    cheio_e = {int(k): v * hyper for k, v in rec.get('espacos', {}).items()}
    cheio_o = {k: v['qtd'] * hyper for k, v in rec.get('outros', {}).items()}
    esp, out = dict(cheio_e), dict(cheio_o)
    seq = [x for x in _seq(tag) if x != SR]; ents = [_entrada(c) for c in plano.get('combates', [])]
    erros = []
    if len(ents) != len(seq):
        return [f'plano {tag}: precisa de {len(seq)} combates, tem {len(ents)}'], [], {}
    combates = []; i = 0
    for passo in _seq(tag):
        if passo == SR:
            if rec.get('espacos_volta') == 'curto': esp = dict(cheio_e)
            for k, v in rec.get('outros', {}).items():
                if v.get('volta') == 'curto': out[k] = cheio_o[k]
            continue
        e = ents[i]; i += 1; onde = f'plano {tag}, combate {i} ({e["linha"]})'
        if e['linha'] not in linhas:
            erros.append(f'{onde}: linha inexistente'); continue
        ge, go = _gasto(linhas[e['linha']], b['corpo'], magias, e)
        extras = [x for x in e.get('extras', []) if x in linhas]   # D9: linhas extras da luta, pelo gasto marginal
        if extras:
            gbe, gbo = _gasto(linhas[base_id(b)], b['corpo'], magias, {'linha': base_id(b)})
            ge, go = dict(ge), dict(go)
            for x in extras:
                xe, xo = _gasto(linhas[x], b['corpo'], magias, {'linha': x})
                for k, v in _marginal(xe, gbe).items(): ge[k] = ge.get(k, 0) + v
                for k, v in _marginal(xo, gbo).items(): go[k] = go.get(k, 0) + v
        for k, v in go.items():                      # M7 (23/11): outros antes dos espaços (a conversão não usa
            if k not in out: erros.append(f'{onde}: recurso "{k}" não declarado em recursos.outros'); continue
            out[k] -= v                              # os pontos que a metamagia da mesma luta já gastou)
            if out[k] < -1e-9: erros.append(f'{onde}: faltam {-out[k]:g} de "{k}"'); out[k] = 0
        for nv in sorted(ge, reverse=True):          # gasta o menor espaço disponível de nível >= nv
            falta = ge[nv]
            for k in sorted(esp):
                if k >= nv and falta > 1e-9:
                    u = min(esp[k], falta); esp[k] -= u; falta -= u
            for rk, rv in rec.get('outros', {}).items():   # M7: Flexible Casting e afins ("converte_em_espacos")
                custo = (rv.get('converte_em_espacos') or {}).get(str(nv))
                if falta > 1e-9 and custo and out.get(rk, 0) >= custo - 1e-9:
                    u = min(falta, out[rk] / custo); out[rk] -= u * custo; falta -= u
            if falta > 1e-9: erros.append(f'{onde}: faltam {falta:g} espaço(s) de nível {nv}+')
        c = dict(linha=e['linha'], categoria=passo[0], peso=passo[1], nota=e.get('nota', ''),
                 gasto=dict(espacos={str(k): round(v, 3) for k, v in sorted(ge.items())}, **go))
        if extras: c['extras'] = extras
        combates.append(c)
    sobra = dict(espacos={str(k): round(v, 2) for k, v in sorted(esp.items()) if v > 1e-9},
                 **{k: round(v, 2) for k, v in out.items() if v > 1e-9})
    return erros, combates, sobra


def checar(b, magias):
    erros = []
    for tag in b.get('planos', {}):
        if _seq(tag) is None: erros.append(f'plano "{tag}": tag desconhecida (use {", ".join(TAGS)})'); continue
        erros += livro_caixa(b, tag, magias)[0]
    return erros


SUB_CONTROLE = {'campo': 'nivel_campo', 'corpo': 'nivel_corpo'}   # Controle (turnos negados) e Corpo (quem leva o dano)


def _nota(x, sub):
    if x is None: return None
    if sub == 'campo':      # Controle na régua de dia (16/11): o conjurador de referência também tem orçamento
        from .controle.total import nivel_dia
        return nivel_dia(x.get('nivel_controle', x.get('nivel_campo')))
    if sub == 'campo_pico': return x.get('nivel_controle', x.get('nivel_campo'))
    if sub == 'corpo': return x.get('nivel_corpo', x.get('nivel_atencao'))   # 19/11: nível de neutralidade
    if sub in SUB_CONTROLE: return x.get(SUB_CONTROLE[sub])
    if sub: x = x[sub]
    return x.get('nivel_eq')


def agregar(b, res_linhas, magias, letra):
    """Resultado de cada plano: por eixo, média do dia (ponderada) e média por categoria.
    Eixo ausente em todos os combates = sem nota; ausente só em alguns = 0 neles (não fez aquilo naquela luta).
    Os eixos entram como no JSON gravado (float do Python): um eixo recém-calculado vem com numpy.float64, que
    arredonda empates de outro jeito (round(np.float64(0.45), 1) = 0.4; round(0.45, 1) = 0.5). Assim o plano não
    depende de o eixo ter sido recalculado ou reaproveitado do cache (19/11, tarefa 3)."""
    import json
    res_linhas = json.loads(json.dumps(res_linhas))
    out = {}
    for tag in b.get('planos', {}):
        _, combates, sobra = livro_caixa(b, tag, magias)
        eixos = {}
        bid = base_id(b)

        def luta(c, eixo, sb):   # D9: linha 1 + Σ max(0, extra − principal) por eixo
            # M5 (23/11): só o ganho. Os eixos medem cenários diferentes (dano: alvo único/chefe; área: horda): o
            # Fireball extra não troca rounds de truque contra o chefe. O ganho total segue decidindo a escolha.
            v = _nota(res_linhas[c['linha']].get(eixo), sb)
            if not c.get('extras'): return v
            if eixo == 'suporte':   # P3.2 (24/11): soma na unidade bruta (dano equivalente) e converte no fim: a régua
                from . import suporte as S   # de nível não é linear, e somar níveis favorece quem parte de baixo
                tb = lambda i: (res_linhas[i].get('suporte') or {}).get('total')
                if tb(c['linha']) is not None:
                    t0 = tb(bid) or 0.0
                    raw = tb(c['linha']) + sum(max(0.0, (tb(x) or 0.0) - t0) for x in c['extras'])
                    return S._nivel(raw, S.REGUAS[2])
            if eixo == 'dano':      # idem no DPR, CA a CA (smite extra em cima de Bless soma DPR, não níveis)
                from . import dano as D
                dp = lambda i: (res_linhas[i].get('dano') or {}).get('dpr')
                if dp(c['linha']):
                    z = {k: 0.0 for k in dp(c['linha'])}; d0 = dp(bid) or z
                    lst = [dp(c['linha'])[f'CA {ca}'] + sum(max(0.0, (dp(x) or z)[f'CA {ca}'] - d0.get(f'CA {ca}', 0.0))
                                                         for x in c['extras']) for ca in D.CAS]
                    return D.nivel_equivalente(lst)[0]
            v0 = _nota(res_linhas[bid].get(eixo), sb) or 0.0
            tot = (v or 0.0) + sum(max(0.0, (_nota(res_linhas[x].get(eixo), sb) or 0.0) - v0) for x in c['extras'])
            return max(0.0, tot) if (v is not None or tot) else None
        for eixo, sub in EIXOS:
            vals = [luta(c, eixo, sub) for c in combates]
            if all(v is None for v in vals): continue
            vals = [v or 0.0 for v in vals]; pesos = [c['peso'] for c in combates]
            dia = sum(p * v for p, v in zip(pesos, vals)) / sum(pesos)
            if eixo == 'area':   # 19/11: área vale o pico (melhor linha da build), não a média do dia
                dia = max((_nota(r.get('area'), None) or 0.0) for r in res_linhas.values())
            if sub == 'campo':   # régua de dia: média dos picos do dia contra o dia do conjurador de referência
                from .controle.total import nivel_dia
                picos = [luta(c, eixo, 'campo_pico') or 0.0 for c in combates]
                dia = nivel_dia(sum(p * v for p, v in zip(pesos, picos)) / sum(pesos))
            cats = {}
            for c, v in zip(combates, vals): cats.setdefault(c['categoria'], []).append(v)
            eixos[sub or eixo] = dict(nivel_eq=round(dia, 1), rank=letra(dia),
                                      por_categoria={k: round(sum(v) / len(v), 1) for k, v in cats.items()})
        out[tag] = dict(hypercharged=b['planos'][tag].get('hypercharged', 1), combates=combates, sobra=sobra, eixos=eixos)
    return out
