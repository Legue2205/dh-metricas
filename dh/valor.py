"""P3 — valor total da build em dano equivalente (DE) por dia de aventura (sprint DragonHeist, 27/11, versão 0).

Hipótese da v0 (premissas valor.*): o valor de uma build é o que o plano dela rende no dia, luta a luta, na moeda que o
próprio plano já usa para escolher linhas (dh/moeda.py: dano convertido pelo abate + suporte + vidas poupadas pelo
controle e pelo corpo × PV do membro padrão + área nas lutas de horda). A defesa da própria build entra pelas vidas do
controle/atenção (a build no lugar do membro padrão, com a CA e os PV dela); a defesa passiva fora disso ainda não
entra — é a primeira coisa a testar contra o G4.

Saídas:
  dia          Σ (DE da linha da luta × peso da luta) no plano padrão
  luta_unica   DE da melhor luta (plano combate_unico, se houver; senão a melhor linha)
  parcelas     dano / suporte / controle / area somados no dia
  nivel_eq     nível em que o membro padrão da régua rende o mesmo DE por dia (interpolado; só quando a régua existe)
Uso: python -m dh valor builds/<id>.json [--json]   (precisa de resultados/<id>.json: rode dh completo antes)
"""
import json
import os

from . import moeda

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resultado(build_id):
    f = os.path.join(RAIZ, 'resultados', build_id + '.json')
    return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else None


def valor(res):
    """res = resultados/<id>.json já calculado. Devolve o valor total do dia e as parcelas."""
    nv = int(res.get('nivel') or 1)
    linhas = res.get('linhas') or {}
    cache = {}

    def de(lid):
        if lid not in cache:
            x = linhas.get(lid)
            cache[lid] = moeda.de_linha(x, nv) if x else dict(dano=0.0, suporte=0.0, controle=0.0, area=0.0, total=0.0)
        return cache[lid]

    plano = (res.get('planos') or {}).get('padrao') or {}
    combates = plano.get('combates') or [{'linha': next(iter(linhas), None), 'peso': 1}]
    parc = dict(dano=0.0, suporte=0.0, controle=0.0, area=0.0)
    por_luta = []
    for c in combates:
        lid = c.get('linha'); w = float(c.get('peso', 1) or 1)
        v = de(lid) if lid else dict(total=0.0)
        por_luta.append(dict(linha=lid, peso=w, de=round(v['total'], 1)))
        for k in parc: parc[k] += w * v.get(k, 0.0)
    dia = sum(parc.values())
    unico = (res.get('planos') or {}).get('combate_unico') or {}
    cu = [c.get('linha') for c in unico.get('combates') or [] if c.get('linha')]
    luta_unica = max((de(l)['total'] for l in (cu or list(linhas))), default=0.0)
    return dict(id=res.get('id'), nivel=nv, dia=round(dia, 1), luta_unica=round(luta_unica, 1),
                parcelas={k: round(v, 1) for k, v in parc.items()}, por_luta=por_luta)


def valor_id(build_id):
    r = _resultado(build_id)
    return valor(r) if r else None


def texto(v):
    p = v['parcelas']
    lutas = ', '.join(f"{x['linha']} {x['de']:.0f}" for x in v['por_luta'])
    return (f"{v['id']}  nv{v['nivel']}  dia {v['dia']:.0f} DE  (dano {p['dano']:.0f} · suporte {p['suporte']:.0f} · "
            f"controle {p['controle']:.0f} · área {p['area']:.0f})  luta única {v['luta_unica']:.0f}  | {lutas}")


def referencia(nivel, sem_holdout=True):
    """P3 do dia de cada chassi sem feat do nível (a régua de comparação para uma build nova, como um NPC)."""
    import glob
    hold = ('artificer', 'rogue', 'sorcerer')
    out = []
    for f in glob.glob(os.path.join(RAIZ, 'builds', f'chassi-*-{nivel}.json')):
        b = json.load(open(f, encoding='utf-8'))
        if b.get('variante') != 'sem-feat' or (sem_holdout and b.get('classe') in hold): continue
        v = valor_id(b['id'])
        if v: out.append((f"{b.get('classe')}-{b.get('subclasse')}", v['dia']))
    return sorted(out, key=lambda x: x[1])


def situar(v, ref):
    """Percentil do dia da build entre os chassis do mesmo nível e os 3 chassis de valor mais próximo."""
    if not ref: return None
    abaixo = sum(1 for _, d in ref if d < v['dia'])
    viz = sorted(ref, key=lambda x: abs(x[1] - v['dia']))[:3]
    return dict(percentil=round(100 * abaixo / len(ref)), n=len(ref), parecidos=[f'{i} ({d:.0f})' for i, d in viz],
                mediana=ref[len(ref) // 2][1])
