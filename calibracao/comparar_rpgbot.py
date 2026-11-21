"""Concordância entre a nota do RPGBot por subclasse e as nossas notas (passada 3, 19/11).

Para cada classe com gabarito (calibracao/rpgbot-<classe>.json), pega as builds 'rpgbot-<classe>-<sub>' (originais) e
'rpgbot-<classe>-<sub>-puro' (puras: a pura no lugar da original quando existe; senão a original) e calcula o tau de
Kendall (tau-b, com empates) entre a nota do RPGBot (1–4) e a MÉDIA dos níveis de Dano, Def. Física (deff),
Def. Mágica (defm), Controle e Área, nos níveis 7 e 11. Eixo ausente conta 0.

Com --com-suporte-corpo a média inclui também Suporte e Corpo (padrão 3 da comparação do Cleric no ROADMAP);
sem a opção o resultado é o de sempre (Fighter/Wizard inalterados).

Uso (da raiz do repo): python calibracao/comparar_rpgbot.py [--json] [--visao padrao] [--com-suporte-corpo]
Os números vêm de `python -m dh comparar --grupo RPGBot --json` (visão do plano padrão).
"""
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CLASSES = ('fighter', 'wizard', 'cleric', 'barbarian', 'monk',
           'paladin', 'rogue', 'bard', 'druid', 'warlock', 'sorcerer', 'ranger', 'artificer')
EIXOS = ('dano', 'deff', 'defm', 'controle', 'area')
EIXOS_SC = EIXOS + ('suporte', 'corpo')
NIVEIS = (7, 11)


def tau_b(x, y):
    """Tau-b de Kendall (empates corrigidos)."""
    c = d = tx = ty = 0
    for i, j in combinations(range(len(x)), 2):
        a, b = x[i] - x[j], y[i] - y[j]
        if a == 0 and b == 0: continue
        if a == 0: tx += 1
        elif b == 0: ty += 1
        elif a * b > 0: c += 1
        else: d += 1
    den = ((c + d + tx) * (c + d + ty)) ** 0.5
    return (c - d) / den if den else float('nan')


def dados(visao='padrao'):
    cmd = [sys.executable, '-m', 'dh', 'comparar', '--grupo', 'RPGBot', '--json', '--visao', visao]
    return json.loads(subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, check=True).stdout)


def media(d, bid, nv, eixos=EIXOS):
    return sum((d.get(e, {}).get(bid, {}).get(str(nv)) or 0.0) for e in eixos) / len(eixos)


def comparar(d, eixos=EIXOS):
    out = {}
    for cl in CLASSES:
        gab = json.loads((RAIZ / 'calibracao' / f'rpgbot-{cl}.json').read_text(encoding='utf-8'))['subclasses']
        res = {}
        for versao in ('originais', 'puras'):
            res[versao] = {}
            for nv in NIVEIS:
                linhas = []
                for sub, g in gab.items():
                    bid = f'rpgbot-{cl}-{sub}'
                    if versao == 'puras' and str(nv) in d['dano'].get(bid + '-puro', {}): bid += '-puro'
                    if str(nv) not in d['dano'].get(bid, {}): continue
                    linhas.append((sub, g['nota'], round(media(d, bid, nv, eixos), 2), bid))
                t = tau_b([x[1] for x in linhas], [x[2] for x in linhas])
                res[versao][nv] = dict(tau=round(t, 2), n=len(linhas),
                                       ordem=sorted(([s, nota, m] for s, nota, m, _ in linhas), key=lambda r: -r[2]))
        out[cl] = res
    return out


def main():
    visao = sys.argv[sys.argv.index('--visao') + 1] if '--visao' in sys.argv else 'padrao'
    eixos = EIXOS_SC if '--com-suporte-corpo' in sys.argv else EIXOS
    r = comparar(dados(visao), eixos)
    if '--json' in sys.argv: print(json.dumps(r, ensure_ascii=False, indent=1)); return
    for cl, res in r.items():
        print(f'\n== {cl.title()} (média de {", ".join(eixos)}; visão {visao})')
        for versao, por_nv in res.items():
            print(f'  {versao:9s} ' + '  '.join(f"nv{nv}: tau {x['tau']:+.2f} (n={x['n']})" for nv, x in por_nv.items()))
        for nv in NIVEIS:
            print(f'  nv{nv} (originais): ' + ', '.join(f"{s} {nota}/{m:.1f}".replace('.', ',') for s, nota, m in res['originais'][nv]['ordem']))


if __name__ == '__main__':
    main()
