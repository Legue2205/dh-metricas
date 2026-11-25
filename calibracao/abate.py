"""Etapa D, protótipo (24/11): valor de abate — matar um inimigo nega os turnos futuros dele — sob três modos de focus fire.

Pergunta do usuário: o ranking de dano se inverte conforme a "malícia" da party? Este script NÃO mexe no motor: lê os
resultados de dano e simula, por Monte Carlo, a party de referência (a build + 3 aliados de referência com o DPR de
referência do nível) contra os encontros do motor de controle (base.encontro: Minions + minibosses, Party de elite,
Horda + chefe, Horda, Dupla, Chefe sozinho; pesos base.encontros).

Modos de focus fire (alavanca; vira premissa se o modelo for adotado):
  perfeito  — a party inteira bate no inimigo vivo de maior ameaça (dano por round ÷ PV) até ele cair
  uniforme  — cada ataque vai para um inimigo vivo sorteado a cada ataque (dano espalhado)
  aleatorio — cada atacante sorteia um alvo vivo e bate nele até cair, aí sorteia outro
Métrica por luta: dano inimigo NEGADO = Σ inimigos (dano por round × acerto 0,6 × rounds que ele deixou de agir), em
R rounds (base.rounds_por_luta). Valor de abate da build = negado(party com a build) − negado(party com um aliado de
referência no lugar dela). Granularidade: cada ataque acerta com 0,65 e, se acerta, causa DPR ÷ (n × 0,65) — muitos
ataques pequenos desperdiçam menos dano no overkill.
25/11: usa o dano POR ROUND do motor (dano.por_round: burst do 1º round, usos por luta no início) e a ÁREA nas lutas
com 4+ minions (linha mais usada no foco_area; fração do PV de cada minion por round = 1 ÷ rounds da régua de área no
nível da build; rounds com área = usos da linha, ou todos se ela não gasta). Sem controle; linha de dano = a mais
frequente no plano foco_dano. Modo padrão sugerido: aleatorio (MODO_PADRAO).

Uso (da raiz): python calibracao/abate.py [--nivel 7] [--n 400] [--top 15] [--csv f.csv]
"""
import collections
import csv
import glob
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from dh import base  # noqa: E402
from dh.build import carregar  # noqa: E402
from dh.controle import atencao  # noqa: E402
from dh.premissas import P  # noqa: E402

MODOS = ('perfeito', 'uniforme', 'aleatorio')
MODO_PADRAO = 'aleatorio'     # sugestão (25/11): cada um escolhe um alvo e segura até cair — o meio-termo realista
ACERTO, ACERTO_INIM, ALIADOS, ATQ_ALIADO = 0.65, 0.6, 3, 2
R_LUTA = int(P('base.rounds_por_luta'))


def _dpr_ca(dpr, ca):
    cas = sorted((int(k.split()[1]), v) for k, v in dpr.items())
    xs, ys = zip(*cas)
    return float(np.interp(ca, xs, ys))


def _mais_usada(res, tag):
    pl = res['planos'].get(tag) or res['planos']['padrao']
    return collections.Counter(c.get('linha') for c in pl.get('combates', [])).most_common(1)[0][0]


def atacante_build(b, res):
    """dict(dpr por CA, dano por round por CA (ou None), nº de ataques por round, área) da linha mais usada no plano
    foco_dano; área = (fração do PV de cada minion por round, rounds com área por luta) da linha mais usada no foco_area."""
    lid = _mais_usada(res, 'foco_dano')
    linhas = {l['id']: l for l in b['linhas']}
    l = linhas.get(lid) or b['linhas'][0]
    atq = (l.get('dano') or {}).get('ataques') or (linhas.get(l.get('herda'), {}).get('dano') or {}).get('ataques') or []
    n = max(1.0, sum(float(a.get('n', 1)) for a in atq if not a.get('round1')))
    d = res['linhas'][lid]['dano']
    aoe = None
    la = _mais_usada(res, 'foco_area'); xa = res['linhas'].get(la, {}).get('area') or {}
    rr = (xa.get('rounds') or {}).get(str(b['nivel']))
    if rr and rr > 0:
        usos = xa.get('usos') or 0
        aoe = (min(1.0, 1.0 / rr), R_LUTA if not usos else min(R_LUTA, math.ceil(usos)))
    return dict(dpr=d['dpr'], por_round=d.get('por_round'), n=n, aoe=aoe, linha=lid, linha_area=la)


def luta(atacantes, inimigos, modo, R, rng, N):
    """Dano inimigo negado médio. atacantes: [dict(dpr, por_round, n, aoe)], inimigos: [dict(hp, ca, dn, papel)].
    Numa luta com 4+ minions, a build com área usa a área no round em que ela rende mais que o alvo único (nos rounds
    que o orçamento de área da luta permite): cada minion vivo perde fração × PV cheio."""
    tot = 0.0
    dano_inim = np.array([c['dn'] * ACERTO_INIM for c in inimigos])
    minion = np.array([c.get('papel') == 'Minion' for c in inimigos]); hp_cheio = np.array([float(c['hp']) for c in inimigos])
    horda = minion.sum() >= 4
    for _ in range(N):
        hp = hp_cheio.copy(); vivo_ate = np.full(len(inimigos), R, float)
        alvo_fixo = [None] * len(atacantes); aoe_usada = [0] * len(atacantes)
        for r in range(R):
            for i, at in enumerate(atacantes):
                dpr, n = (dict((k, v[r]) for k, v in at['por_round'].items()) if at.get('por_round') else at['dpr']), at['n']
                if horda and at.get('aoe') and aoe_usada[i] < at['aoe'][1]:
                    vm = np.flatnonzero((hp > 0) & minion)
                    ganho_aoe = float(np.minimum(hp[vm], at['aoe'][0] * hp_cheio[vm]).sum())
                    if ganho_aoe > _dpr_ca(dpr, inimigos[vm[0]]['ca'] if len(vm) else 15):
                        hp[vm] -= at['aoe'][0] * hp_cheio[vm]; aoe_usada[i] += 1
                        for j in vm:
                            if hp[j] <= 0 and vivo_ate[j] == R: vivo_ate[j] = r + 1
                        continue
                k = int(math.floor(n)) + (rng.random() < n - math.floor(n))
                for _a in range(k):
                    vivos = np.flatnonzero(hp > 0)
                    if not len(vivos): break
                    if modo == 'perfeito':
                        j = vivos[np.argmax(dano_inim[vivos] / hp[vivos])]
                    elif modo == 'uniforme':
                        j = rng.choice(vivos)
                    else:
                        if alvo_fixo[i] is None or hp[alvo_fixo[i]] <= 0: alvo_fixo[i] = rng.choice(vivos)
                        j = alvo_fixo[i]
                    if rng.random() < ACERTO:
                        hp[j] -= _dpr_ca(dpr, inimigos[j]['ca']) / (n * ACERTO)
                        if hp[j] <= 0 and vivo_ate[j] == R: vivo_ate[j] = r + 1   # cai no round r (a party age antes)
        tot += float(np.sum(dano_inim * (R - vivo_ate)))
    return tot / N


def main():
    a = sys.argv
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    N = int(a[a.index('--n') + 1]) if '--n' in a else 300
    top = int(a[a.index('--top') + 1]) if '--top' in a else 12
    R = int(P('base.rounds_por_luta'))
    rows = []
    for nv in nvs:
        ref = dict(dpr={f'CA {c}': atencao.dpr_ref(nv) for c in (10, 30)}, por_round=None, n=ATQ_ALIADO, aoe=None)
        enc = {t: base.encontro(t, nv) for t in base.PESO_TIPO}
        rng = np.random.default_rng(7)
        base_val = {(t, m): luta([ref] * (ALIADOS + 1), enc[t], m, R, rng, N) for t in enc for m in MODOS}
        arqs = sorted(glob.glob(f'builds/chassi-*-{nv}.json')) + sorted(glob.glob(f'builds/pacote-*-vh-{nv}.json'))
        for f in arqs:
            bj = json.load(open(f, encoding='utf-8'))
            if bj['id'].startswith('chassi') and bj.get('variante') != 'sem-feat': continue
            rp = os.path.join('resultados', os.path.basename(f))
            if not os.path.exists(rp): continue
            res = json.load(open(rp, encoding='utf-8'))
            at = atacante_build(carregar(f), res)
            row = dict(nivel=nv, build=bj['id'].rsplit('-', 1)[0], classe=bj['classe'], subclasse=bj['subclasse'],
                       linha=at['linha'], linha_area=at['linha_area'], n_ataques=round(at['n'], 2),
                       dpr16=round(_dpr_ca(at['dpr'], 16), 1),
                       burst=round(at['por_round']['CA 16'][0] / max(0.1, _dpr_ca(at['dpr'], 16)), 2) if at['por_round'] else 1.0,
                       area_frac=at['aoe'][0] if at['aoe'] else 0)
            for m in MODOS:
                v = 0.0
                for t, inim in enc.items():
                    x = luta([at] + [ref] * ALIADOS, inim, m, R, rng, N) - base_val[(t, m)]
                    row[f'{m}:{t}'] = round(x, 1); v += base.PESO_TIPO[t] * x
                row[m] = round(v, 1)
            rows.append(row)
        sel = [r for r in rows if r['nivel'] == nv]
        print(f'\n== nv{nv}: valor de abate (dano inimigo negado por luta, ponderado pelos tipos; build − aliado de referência)')
        for m in MODOS:
            s = sorted(sel, key=lambda r: -r[m])
            print(f'  {m:9s} top:', ', '.join(f"{r['build'].replace('chassi-', '').replace('pacote-', 'P:')} {r[m]:.0f}" for r in s[:top]))
        # concordância entre modos (τ de Kendall entre rankings)
        from comparar_rpgbot import tau_b
        for m1, m2 in (('perfeito', 'uniforme'), ('perfeito', 'aleatorio'), ('uniforme', 'aleatorio')):
            print(f'  τ({m1}, {m2}) = {tau_b([r[m1] for r in sel], [r[m2] for r in sel]):+.2f}')
        # quem mais sobe/desce entre perfeito e uniforme (posição no ranking)
        pos = {m: {r['build']: i for i, r in enumerate(sorted(sel, key=lambda r: -r[m]))} for m in MODOS}
        d = sorted(sel, key=lambda r: pos['perfeito'][r['build']] - pos['uniforme'][r['build']])
        print('  sobem com focus fire perfeito:', ', '.join(f"{r['build'][7:]} ({pos['uniforme'][r['build']] + 1}→{pos['perfeito'][r['build']] + 1}, {r['n_ataques']} atq)" for r in d[:6]))
        print('  sobem sem focus fire (uniforme):', ', '.join(f"{r['build'][7:]} ({pos['perfeito'][r['build']] + 1}→{pos['uniforme'][r['build']] + 1}, {r['n_ataques']} atq)" for r in d[-6:][::-1]))
    if '--csv' in a:
        with open(a[a.index('--csv') + 1], 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == '__main__':
    main()
