"""Plano de orçamento do dia: a decisão de como gastar recursos é da build, escrita no JSON.

Tag = premissa diária. Cada combate do plano aponta para uma linha (hipótese) da build:
  "planos": {"padrao": {"combates": ["marcial", "caster", "marcial", {"linha": "caster", "nota": "gasta tudo"}],
                        "hypercharged": 1.5}}        # opcional: hipótese de acesso a mais recursos
O livro-caixa desconta, combate a combate, o que cada linha gasta (espaços de magia de todos os eixos e
"usa" da linha, ex. {"furia": 1}); descanso curto devolve o que tem "volta": "curto". Gastar o que não tem = erro.
O que sobra no fim do dia é a "sobra para utilidade". Resultado por eixo: média do dia ponderada pelo peso do
combate, e a média de cada categoria em separado.
"""
from . import orcamento

SR = 'SR'
TAGS = {  # (categoria, peso) na ordem do dia; SR = descanso curto
    'padrao': [('np', 1), ('p', 2), SR, ('np', 1), ('p', 2)],
    'combate_unico': [('p', 1)],
    'dia_longo': [('np', 1), ('np', 1), ('mod', 2), SR, ('np', 1), ('mod', 2), ('mod', 2), SR, ('mod', 2), ('boss', 4)],
}
CATEGORIAS = {'np': 'não prioritário', 'p': 'prioritário', 'mod': 'moderado', 'boss': 'boss'}
EIXOS = [('dano', None), ('defesa', None), ('saves', 'resiliencia'), ('saves', 'vontade'), ('controle', None),
         ('area', None), ('suporte', None)]


def _entrada(c): return c if isinstance(c, dict) else {'linha': c}


def _gasto(linha, corpo, magias, entrada):
    if 'gasta' in entrada:
        g = dict(entrada['gasta']); esp = {int(k): v for k, v in g.pop('espacos', {}).items()}
        return esp, g
    esp = {}
    for por_eixo in orcamento.espacos_gastos(linha, corpo, magias).values():
        for k, v in por_eixo.items(): esp[int(k)] = esp.get(int(k), 0) + v
    return esp, {k: v for k, v in linha.get('usa', {}).items() if k != 'espacos'}


def livro_caixa(b, tag, magias):
    """(erros, combates, sobra). combates: [{linha, categoria, peso, gasto}]."""
    plano = b['planos'][tag]; rec = b.get('recursos', {}); hyper = plano.get('hypercharged', 1)
    linhas = {l['id']: l for l in b['linhas']}
    cheio_e = {int(k): v * hyper for k, v in rec.get('espacos', {}).items()}
    cheio_o = {k: v['qtd'] * hyper for k, v in rec.get('outros', {}).items()}
    esp, out = dict(cheio_e), dict(cheio_o)
    seq = [x for x in TAGS[tag] if x != SR]; ents = [_entrada(c) for c in plano.get('combates', [])]
    erros = []
    if len(ents) != len(seq):
        return [f'plano {tag}: precisa de {len(seq)} combates, tem {len(ents)}'], [], {}
    combates = []; i = 0
    for passo in TAGS[tag]:
        if passo == SR:
            if rec.get('espacos_volta') == 'curto': esp = dict(cheio_e)
            for k, v in rec.get('outros', {}).items():
                if v.get('volta') == 'curto': out[k] = cheio_o[k]
            continue
        e = ents[i]; i += 1; onde = f'plano {tag}, combate {i} ({e["linha"]})'
        if e['linha'] not in linhas:
            erros.append(f'{onde}: linha inexistente'); continue
        ge, go = _gasto(linhas[e['linha']], b['corpo'], magias, e)
        for nv in sorted(ge, reverse=True):          # gasta o menor espaço disponível de nível >= nv
            falta = ge[nv]
            for k in sorted(esp):
                if k >= nv and falta > 1e-9:
                    u = min(esp[k], falta); esp[k] -= u; falta -= u
            if falta > 1e-9: erros.append(f'{onde}: faltam {falta:g} espaço(s) de nível {nv}+')
        for k, v in go.items():
            if k not in out: erros.append(f'{onde}: recurso "{k}" não declarado em recursos.outros'); continue
            out[k] -= v
            if out[k] < -1e-9: erros.append(f'{onde}: faltam {-out[k]:g} de "{k}"'); out[k] = 0
        combates.append(dict(linha=e['linha'], categoria=passo[0], peso=passo[1], nota=e.get('nota', ''),
                             gasto=dict(espacos={str(k): v for k, v in sorted(ge.items())}, **go)))
    sobra = dict(espacos={str(k): round(v, 2) for k, v in sorted(esp.items()) if v > 1e-9},
                 **{k: round(v, 2) for k, v in out.items() if v > 1e-9})
    return erros, combates, sobra


def checar(b, magias):
    erros = []
    for tag in b.get('planos', {}):
        if tag not in TAGS: erros.append(f'plano "{tag}": tag desconhecida (use {", ".join(TAGS)})'); continue
        erros += livro_caixa(b, tag, magias)[0]
    return erros


def _nota(x, sub):
    if x is None: return None
    if sub: x = x[sub]
    return x.get('nivel_eq')


def agregar(b, res_linhas, magias, letra):
    """Resultado de cada plano: por eixo, média do dia (ponderada) e média por categoria.
    Eixo ausente em todos os combates = sem nota; ausente só em alguns = 0 neles (não fez aquilo naquela luta)."""
    out = {}
    for tag in b.get('planos', {}):
        _, combates, sobra = livro_caixa(b, tag, magias)
        eixos = {}
        for eixo, sub in EIXOS:
            vals = [_nota(res_linhas[c['linha']].get(eixo), sub) for c in combates]
            if all(v is None for v in vals): continue
            vals = [v or 0.0 for v in vals]; pesos = [c['peso'] for c in combates]
            dia = sum(p * v for p, v in zip(pesos, vals)) / sum(pesos)
            cats = {}
            for c, v in zip(combates, vals): cats.setdefault(c['categoria'], []).append(v)
            eixos[sub or eixo] = dict(nivel_eq=round(dia, 1), rank=letra(dia),
                                      por_categoria={k: round(sum(v) / len(v), 1) for k, v in cats.items()})
        out[tag] = dict(hypercharged=b['planos'][tag].get('hypercharged', 1), combates=combates, sobra=sobra, eixos=eixos)
    return out
