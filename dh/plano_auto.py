"""Plano do dia automático (para builds de referência em lote, ex.: RPGBot).

Regra explícita, para ficar auditável: entre todas as atribuições de linhas aos combates do dia que fecham o
livro-caixa (sem gastar o que não tem), escolhe a que **gasta mais recurso no dia** (build otimizada não deixa
recurso parado) e, entre essas, a que põe **o gasto mais pesado nas prioritárias** (gasto × peso do combate).
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


def gerar(b, tag='padrao'):
    """Devolve o dict do plano (ou None se nenhuma combinação fecha o livro-caixa)."""
    from .build import resolver
    b = resolver(copy.deepcopy(b)); seq = [x for x in planos._seq(tag) if x != planos.SR]
    cands = _candidatas(b)
    if not cands: return None
    gastos = {l['id']: planos._gasto(l, b['corpo'], MAGIAS, {'linha': l['id']}) for l in cands}
    marca = {l['id']: l.get('plano') for l in cands}
    eixos = {l['id']: [e for e in ('dano', 'defesa', 'saves', 'controle', 'area', 'suporte') if e in l] for l in cands}
    ids = [l['id'] for l in cands]
    if len(ids) ** len(seq) > LIMITE: ids = sorted(ids, key=lambda i: -_valor(b, *gastos[i]))[:int(LIMITE ** (1 / len(seq)))]
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
            if melhor is None or chave > melhor[0]: melhor = (chave, combo, sobra)
    if melhor is None: return None
    _, combo, sobra = melhor
    nomes = lambda cat: sorted({i for (c, _), i in zip(seq, combo) if c == cat})
    partes = [f"{planos.CATEGORIAS[c]}: {', '.join(nomes(c))}" for c in dict.fromkeys(c for c, _ in seq)]
    sb = ', '.join([f"{v:g}×{k}º" for k, v in sobra.get('espacos', {}).items()] + [f"{v:g} {k}" for k, v in sobra.items() if k != 'espacos'])
    desc = (f"Plano automático (maior gasto ponderado que cabe no dia; prioritário pesa 2). "
            f"{'; '.join(partes)}. Sobra: {sb or 'nada'}.")
    return {'auto': True, 'descricao': desc[:500], 'combates': list(combo)}


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
