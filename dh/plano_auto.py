"""Plano do dia automático (para builds de referência em lote, ex.: RPGBot).

Regra explícita, para ficar auditável: entre todas as atribuições de linhas aos combates do dia que fecham o
livro-caixa (sem gastar o que não tem), escolhe a de **maior rendimento do dia** (D5, 23/11): soma de peso do combate ×
valor da linha, com o valor da linha = níveis eq. dos eixos × `plano.auto.peso_eixo`. O rendimento só existe depois de
calcular as linhas, então o motor reescolhe o plano (`valores=`); sem valores (no `dh expandir`) vale a regra antiga,
que serve de rascunho: a que **gasta mais recurso no dia** e, entre essas, a que põe **o gasto mais pesado nas
prioritárias** (gasto × peso do combate); com valores, o gasto vira desempate.
Gasto de uma linha: `"gasta"` declarado na linha (recomendado: {"espacos": {"3": 1}, "ki": 2}) ou inferido das
magias dos eixos. Desempates, nesta ordem:
  1. linhas marcadas `"plano": "prioritaria"` nos combates prioritários e `"plano": "comum"` nos comuns;
  2. menos sobra no fim do dia;
  3. linhas mais completas (mais eixos declarados);
  4. menos trocas de linha (dia mais simples).
Linhas com `"plano": false` (ou `"aneis": false`) ficam de fora (ex.: "shield-total", conferência).
Valor do gasto: espaço de magia = seu nível; outro recurso = 1 por uso (ou `recursos.outros.<r>.valor`).
O plano gerado leva `"auto": true` e uma descrição dizendo isso; um plano escrito à mão nunca é sobrescrito.
"""
import copy
from itertools import product

from . import planos
from .controle.campo import MAGIAS

LIMITE = 60000   # combinações avaliadas no máximo (10 linhas × 4 combates = 10 000)


def _candidatas(b):
    return [l for l in b['linhas'] if l.get('plano', True) is not False and l.get('aneis', True) is not False]


def _valor(b, ge, go):
    outros = b.get('recursos', {}).get('outros', {})
    return sum(int(k) * v for k, v in ge.items()) + sum(v * outros.get(k, {}).get('valor', 1) for k, v in go.items())


def valores_linhas(res_linhas, nivel=None):
    """Valor de cada linha para o rendimento (D5): soma, por eixo, do nível eq. (nota do plano) ÷ nível típico daquele
    eixo no nível da build (P2.15: plano.auto.tipico; sem nível ou sem típico, divide por 1) × peso por eixo."""
    import json
    from .premissas import P
    w = P('plano.auto.peso_eixo'); r = json.loads(json.dumps(res_linhas))
    tip = P('plano.auto.tipico') if nivel else {}

    def t(e):
        d = tip.get(e) or {}
        if not d: return 1.0
        L = min(d, key=lambda k: abs(int(k) - nivel))
        return max(0.5, d[L])
    out = {}
    for lid, x in r.items():
        v = 0.0
        for eixo, sub in planos.EIXOS:
            sub_n = 'campo_pico' if sub == 'campo' else sub
            n = planos._nota(x.get(eixo), sub_n)
            v += w.get(sub or eixo, 1) * (n or 0.0) / t(sub or eixo)
        out[lid] = v
    return out


def _k(b, seq):
    """D9: linhas (magias) por luta = espaços do dia × (1 − utilidade) / combates, entre 1 e os rounds da luta."""
    from .premissas import P
    if b.get('magias_por_luta'): return int(b['magias_por_luta'])
    rec = b.get('recursos', {}); n = len(seq)
    vezes = 1 + (sum(1 for x in seq if x == planos.SR) if rec.get('espacos_volta') == 'curto' else 0)
    esp = sum(rec.get('espacos', {}).values()) * vezes
    for v in rec.get('outros', {}).values():   # M7: pontos conversíveis em espaços (~1 espaço a cada 3 pontos)
        if v.get('converte_em_espacos'): esp += v.get('qtd', 0) / 3
    k = round(esp * (1 - P('planos.magias_por_luta')['utilidade']) / max(1, n))
    return int(max(1, min(P('base.rounds_por_luta'), k)))


def _extras(b, tag, seq, combo, valores, cands):
    """D9: guloso sobre o melhor plano de uma linha por luta: acrescenta, enquanto couber no livro-caixa e no k da
    luta, a linha extra de maior ganho (peso da luta × (valor da extra − valor da principal)); concentração: uma por luta."""
    from . import orcamento
    k = _k(b, planos._seq(tag)); bid = planos.base_id(b)
    if k <= 1: return None
    import json
    import re

    def pecas(l):   # o que a linha põe na luta além da principal (ataques, fontes, áreas, invocações)
        d = l.get('dano') if isinstance(l.get('dano'), dict) else {}
        # ataque sem o "n": o mesmo truque/arma com menos rounds (porque a linha lançou magia) não é peça nova
        s = {'atq:' + json.dumps({k: v for k, v in x.items() if k != 'n'}, sort_keys=True) for x in d.get('ataques', [])}
        s |= {'sup:' + f.get('nome', '') for f in (l.get('suporte') or {}).get('fontes', []) if isinstance(l.get('suporte'), dict)}
        s |= {'ctl:' + f.get('nome', '') for f in l.get('controle', {}).get('fontes', [])}
        s |= {'area:' + (x.get('nome', '') if isinstance(x, dict) else str(x)) for x in l.get('area', []) or []}
        s |= {'inv:' + i.get('nome', '') for i in l.get('invocacoes', []) or []}
        return s
    lin = {l['id']: l for l in cands}; p0 = pecas(lin[bid]) if bid in lin else set()
    tok = lambda i: set(re.split(r'[+\-]', i)) - {'principal', ''}   # peças do nome (bless+arma, guardioes-arma)
    pc = {i: (pecas(l) - p0) | {'id:' + t for t in tok(i)} for i, l in lin.items()}
    conc = {l['id']: {t for t, _ in orcamento._conc_com_topos(l, MAGIAS)} for l in cands}
    from pathlib import Path
    _mj = json.loads((Path(__file__).parent / 'controle' / 'magias.json').read_text(encoding='utf-8'))
    nomes_c = tuple(n.lower() for n in _mj.get('_concentracao_nomes', {}).get('nomes', []))
    ehc = lambda nome: nome.lower().startswith(nomes_c)
    for l in cands:   # concentração declarada ou reconhecida pelo nome (área, dano, suporte, invocação)
        d = l.get('dano') if isinstance(l.get('dano'), dict) else {}
        nomes = [x.get('nome', '') for x in (l.get('area') or []) if isinstance(x, dict)]
        nomes += [f.get('nome', '') for f in (l.get('suporte') or {}).get('fontes', []) if isinstance(l.get('suporte'), dict)]
        nomes += [i.get('nome', '') for i in l.get('invocacoes', []) or []]
        nomes += [x.get('nome', '') for x in d.get('ataques', []) if x.get('nome')]
        for n in nomes:
            if ehc(n): conc[l['id']].add('nome:' + re.sub(r'\s*\(.*', '', n).lower())
    ents = [{'linha': i, 'extras': []} for i in combo]; pesos = [p for _, p in seq]
    v0 = valores.get(bid, 0.0); sobra = None
    while True:
        melhor = None
        for f, e in enumerate(ents):
            if 1 + len(e['extras']) >= k: continue
            usadas = {e['linha'], *e['extras']}; cs = set().union(*(conc.get(x, set()) for x in usadas))
            for l in cands:
                j = l['id']
                if j in usadas or j == bid: continue
                if conc.get(j) and (cs or len(conc[j]) > 1): continue      # uma concentração por luta
                if any(pc.get(j, set()) & pc.get(x, set()) for x in usadas): continue   # nada repetido na luta
                ganho = pesos[f] * (valores.get(j, 0.0) - v0)
                if ganho <= 1e-9 or (melhor and ganho <= melhor[0]): continue
                e['extras'].append(j)
                b['planos'] = {tag: {'combates': [dict(x) for x in ents]}}
                erros, _, sb = planos.livro_caixa(b, tag, MAGIAS)
                e['extras'].pop()
                if not erros: melhor = (ganho, f, j, sb)
        if not melhor: break
        _, f, j, sobra = melhor; ents[f]['extras'].append(j)
    if sobra is None: return None
    return [e['linha'] if not e['extras'] else dict(e) for e in ents], sobra


def gerar(b, tag='padrao', valores=None):
    """Devolve o dict do plano (ou None se nenhuma combinação fecha o livro-caixa). valores = {linha: valor} (D5)."""
    from .build import resolver
    b = resolver(copy.deepcopy(b)); seq = [x for x in planos._seq(tag) if x != planos.SR]
    cands = _candidatas(b)
    if not cands: return None
    gastos = {l['id']: planos._gasto(l, b['corpo'], MAGIAS, {'linha': l['id']}) for l in cands}
    marca = {l['id']: l.get('plano') for l in cands}
    eixos = {l['id']: [e for e in ('dano', 'defesa', 'saves', 'controle', 'area', 'suporte') if e in l] for l in cands}
    ids = [l['id'] for l in cands]
    if len(ids) ** len(seq) > LIMITE:
        crit = (lambda i: -valores.get(i, 0.0)) if valores else (lambda i: -_valor(b, *gastos[i]))
        ids = sorted(ids, key=crit)[:int(LIMITE ** (1 / len(seq)))]
    melhor = None
    if True:
        for combo in product(ids, repeat=len(seq)):
            b['planos'] = {tag: {'combates': list(combo)}}
            erros, combates, sobra = planos.livro_caixa(b, tag, MAGIAS)
            if erros: continue
            gasto = sum(p * _valor(b, *gastos[i]) for (_, p), i in zip(seq, combo))
            pref = sum(1 for (cat, _), i in zip(seq, combo)
                       if (marca[i] == 'prioritaria' and cat in ('p', 'mod', 'boss')) or (marca[i] == 'comum' and cat == 'np'))
            resto = sum(int(k) * v for k, v in sobra.get('espacos', {}).items()) + sum(v for k, v in sobra.items() if k != 'espacos')
            total = sum(_valor(b, *gastos[i]) for i in combo)
            completas = sum(len(eixos[i]) for i in combo)
            chave = (round(total, 6), round(gasto, 6), pref, -resto, completas, -len(set(combo)))
            if valores:
                rend = sum(p * valores.get(i, 0.0) for (_, p), i in zip(seq, combo))
                chave = (round(rend, 4),) + chave
            if melhor is None or chave > melhor[0]: melhor = (chave, combo, sobra)
    if melhor is None: return None
    _, combo, sobra = melhor
    ents = list(combo)
    if valores:
        ents, sobra = _extras(b, tag, seq, list(combo), valores, cands) or (ents, sobra)
    nomes = lambda cat: sorted({i for (c, _), i in zip(seq, combo) if c == cat})
    partes = [f"{planos.CATEGORIAS[c]}: {', '.join(nomes(c))}" for c in dict.fromkeys(c for c, _ in seq)]
    sb = ', '.join([f"{v:g}×{k}º" for k, v in sobra.get('espacos', {}).items()] + [f"{v:g} {k}" for k, v in sobra.items() if k != 'espacos'])
    regra = ("maior rendimento do dia que cabe no orçamento; gasto desempata" if valores
             else "maior gasto ponderado que cabe no dia")
    desc = (f"Plano automático ({regra}; prioritário pesa 2). "
            f"{'; '.join(partes)}. Sobra: {sb or 'nada'}.")
    nx = sum(len(e.get('extras', [])) for e in ents if isinstance(e, dict))
    if nx: desc += f" + {nx} magia(s) extra(s) nas lutas (D9, k = {_k(b, seq)} por luta)."
    return {'auto': True, 'descricao': desc[:600], 'combates': ents}


def aplicar(b, tags=('padrao', 'combate_unico')):
    """Preenche os planos marcados "auto" (ou ausentes, se a build pedir "planos_auto": true). Devolve as tags geradas."""
    feitos = []
    pl = b.setdefault('planos', {})
    for tag in tags:
        atual = pl.get(tag)
        quer = atual == 'auto' or (isinstance(atual, dict) and atual.get('auto')) or (atual is None and b.get('planos_auto'))
        if not quer: continue
        p = gerar(b, tag)
        if p: pl[tag] = p; feitos.append(tag)
        else: pl.pop(tag, None)
    if not pl: b.pop('planos')
    return feitos
