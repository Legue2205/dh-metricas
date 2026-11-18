"""Gabarito de calibração: compara o que os motores dizem com o que uma fonte de referência espera.

Um gabarito = um arquivo `calibracao/<nome>.json`:

{
  "nome": "Party DragonHeist, nível 7",
  "fonte": "percepção da mesa (2 anos de jogo)",       // ou "rpgbot", "d4", "treant"
  "visao": "padrao",          // padrao | combate_unico | dia_longo | externo | interno   (padrão: padrao)
  "tolerancia": 0.5,          // diferença de nível abaixo da qual uma inversão é "empate técnico" (padrão 0,5)
  "eixos": {
    "dano": {"ordem": ["tinbin-7", ["john-7", "kael-7"], "amadeus-7"]},   // do mais forte ao mais fraco; sublista = empate
    "area": {"faixa": {"amadeus-7": ["B-", "A"], "marcus-7": ["D", "C+"]}},  // letra mínima e máxima aceitas
    "suporte": {"ordem": [...], "faixa": {...}}                           // os dois juntos também valem
  },
  "notas": {"dano": "texto livre: por que a mesa acha isso"}
}

Eixos: dano, deff, defm, controle, corpo, area, suporte (os do painel).
Visão: as abas de plano usam a média do dia daquele plano (sem plano → linha principal, marcado com ~);
externo/interno usam os anéis (máximo/mínimo entre as linhas-opção).

Saída: por eixo, pares concordantes × invertidos (tau de Kendall), as inversões com os números e as faixas violadas.
"""
import json
from itertools import combinations
from pathlib import Path

from . import base

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / 'calibracao'
EIXOS = ('dano', 'deff', 'defm', 'controle', 'corpo', 'area', 'suporte')
NOME = dict(dano='Dano', deff='Def. Física', defm='Def. Mágica', controle='Controle', corpo='Corpo', area='Área', suporte='Suporte')
POS = {r: i for i, r in enumerate(base.ORDEM)}


def valores(dados, visao='padrao'):
    """{build_id: ({eixo: n}, marca)} a partir de site.dados(). marca '~' = sem o plano pedido (linha principal)."""
    out = {}
    if visao in ('externo', 'interno'):
        for bid, b in dados['builds'].items():
            an = b.get('aneis')
            if an: out[bid] = ({k: v['n'] for k, v in an[visao].items()}, '')
        return out
    princ = {e['b']: e for e in dados['entradas']['legado'] if e['tipo'] == 'principal'}
    plano = {e['b']: e for e in dados['entradas'].get(visao, [])}
    for bid in dados['builds']:
        e, m = (plano[bid], '') if bid in plano else (princ.get(bid), '~')
        if e: out[bid] = ({k: v['n'] for k, v in e['eixos'].items()}, m)
    return out


def _niveis(ordem):
    """['a', ['b','c'], 'd'] -> {'a': 0, 'b': 1, 'c': 1, 'd': 2} (posição esperada; menor = mais forte)."""
    pos = {}
    for i, x in enumerate(ordem):
        for bid in (x if isinstance(x, list) else [x]): pos[bid] = i
    return pos


def avaliar_eixo(eixo, regra, vals, tol=0.5):
    """vals = {build: ({eixo: n}, marca)}. Devolve dict com tau, contagens, inversões, faixas e ausentes."""
    n = lambda b: vals[b][0].get(eixo, 0.0) if b in vals else None
    r = dict(eixo=eixo, concordantes=0, invertidos=0, empates_tecnicos=0, inversoes=[], faixas=[], ausentes=[])
    if 'ordem' in regra:
        pos = _niveis(regra['ordem'])
        r['ausentes'] += [b for b in pos if b not in vals]
        ids = [b for b in pos if b in vals]
        for a, b in combinations(ids, 2):
            if pos[a] == pos[b]: continue
            forte, fraco = (a, b) if pos[a] < pos[b] else (b, a)
            d = n(forte) - n(fraco)
            if d > 0: r['concordantes'] += 1
            elif -d < tol: r['empates_tecnicos'] += 1
            else:
                r['invertidos'] += 1
                r['inversoes'].append(dict(esperado_maior=forte, esperado_menor=fraco, valores=(n(forte), n(fraco))))
        tot = r['concordantes'] + r['invertidos']
        r['tau'] = round((r['concordantes'] - r['invertidos']) / tot, 2) if tot else None
        r['inversoes'].sort(key=lambda x: x['valores'][0] - x['valores'][1])
    for bid, (lo, hi) in regra.get('faixa', {}).items():
        if bid not in vals: r['ausentes'].append(bid); continue
        x = n(bid); L = base.letra(x)
        if not POS[lo] <= POS[L] <= POS[hi]: r['faixas'].append(dict(build=bid, valor=x, letra=L, esperado=(lo, hi)))
    return r


def avaliar(gab, dados):
    vals = valores(dados, gab.get('visao', 'padrao'))
    tol = gab.get('tolerancia', 0.5)
    eixos = {k: avaliar_eixo(k, regra, vals, tol) for k, regra in gab.get('eixos', {}).items() if k in EIXOS}
    taus = [e['tau'] for e in eixos.values() if e.get('tau') is not None]
    return dict(nome=gab.get('nome', ''), fonte=gab.get('fonte', ''), visao=gab.get('visao', 'padrao'),
                sem_plano=sorted(b for b, (_, m) in vals.items() if m), eixos=eixos,
                tau_medio=round(sum(taus) / len(taus), 2) if taus else None)


def carregar(alvos=None):
    arqs = [Path(a) for a in alvos] if alvos else sorted(PASTA.glob('*.json'))
    return [(p, json.loads(p.read_text(encoding='utf-8'))) for p in arqs]


def _f(x): return '–' if x is None else f'{x:.1f}'.replace('.', ',')


def imprimir(r):
    print(f"\n=== {r['nome']} · fonte: {r['fonte']} · visão: {r['visao']} · tau médio {r['tau_medio']}")
    if r['sem_plano']: print('  (~ sem plano nesta visão, usa a linha principal: ' + ', '.join(r['sem_plano']) + ')')
    for k, e in r['eixos'].items():
        tau = '' if e.get('tau') is None else f"tau {e['tau']:+.2f} · {e['concordantes']} ok · {e['invertidos']} invertidos · {e['empates_tecnicos']} empates técnicos"
        print(f"  {NOME[k]:12s} {tau}")
        for i in e['inversoes']:
            a, b = i['valores']
            print(f"      ✗ {i['esperado_maior']} ({_f(a)}) deveria passar {i['esperado_menor']} ({_f(b)})")
        for x in e['faixas']:
            print(f"      ✗ {x['build']}: {x['letra']} {_f(x['valor'])}, esperado {x['esperado'][0]}–{x['esperado'][1]}")
        if e['ausentes']: print('      ? sem resultado: ' + ', '.join(e['ausentes']))


def registrar(rotulo, rodadas, arq=None):
    """Grava uma linha por gabarito em calibracao/historico.jsonl: tau por eixo + as premissas vigentes (o "checkpoint")."""
    import datetime
    from . import premissas
    arq = Path(arq or PASTA / 'historico.jsonl')
    pr = {k: v['valor'] for k, v in premissas._dados().items() if not k.startswith('_')}
    with arq.open('a', encoding='utf-8') as f:
        for r in rodadas:
            f.write(json.dumps(dict(rotulo=rotulo, data=datetime.date.today().isoformat(), gabarito=r['nome'], visao=r['visao'],
                                    tau_medio=r['tau_medio'], tau={k: e.get('tau') for k, e in r['eixos'].items()},
                                    invertidos={k: e['invertidos'] for k, e in r['eixos'].items()}, premissas=pr),
                               ensure_ascii=False) + '\n')
    return arq
