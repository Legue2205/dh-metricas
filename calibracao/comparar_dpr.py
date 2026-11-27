"""G1b (sprint 26/11): DPR do motor × DPR calculado pelo RPGBot (calibracao/dpr-rpgbot.json).

Uso (da raiz): python calibracao/comparar_dpr.py [--json]
Classifica cada caso: 'igual' (≤ 0,05 de diferença absoluta — arredondamento), 'pequena' (≤ 10%: investigar a causa),
'grande' (> 10%: investigar de verdade). O motor é chamado sem arredondar (dano._dpr_bruto quando existir)."""
import json
import os
import sys

RAIZ = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, RAIZ)


def classe(motor, ref):
    d = motor - ref
    if abs(d) <= 0.05 + 1e-9: return 'igual'   # o motor arredonda a 0,1
    return 'pequena' if abs(d) <= 0.10 * ref else 'grande'


def medir():
    from dh import dano
    casos = json.load(open(os.path.join(RAIZ, 'calibracao', 'dpr-rpgbot.json'), encoding='utf-8'))['casos']
    out = []
    for c in casos:
        m = dano.dpr(c['spec'], c['ca'], c.get('lutas_dia', 4))
        out.append(dict(id=c['id'], nivel=c['nivel'], ca=c['ca'], motor=m, rpgbot=c['dpr_rpgbot'],
                        dif=round(m - c['dpr_rpgbot'], 2), pct=round(100 * (m - c['dpr_rpgbot']) / c['dpr_rpgbot'], 1),
                        classe=classe(m, c['dpr_rpgbot']), explicacao=c.get('explicacao')))
    return out


def main():
    r = medir()
    if '--json' in sys.argv: print(json.dumps(r, ensure_ascii=False, indent=1)); return
    for x in r:
        print(f"{x['id']:22s} nv{x['nivel']:<2d} CA {x['ca']}  motor {x['motor']:6.2f}  RPGBot {x['rpgbot']:6.2f}  "
              f"{x['dif']:+6.2f} ({x['pct']:+5.1f}%)  {x['classe']}")
        if x['explicacao']: print(f"{'':24s}↳ explicada: {x['explicacao']}")
    print(f"G1b: {'PASSA' if all(x['classe'] != 'grande' or x['explicacao'] for x in r) else 'não passa'} "
          f"({sum(x['classe'] == 'igual' for x in r)} iguais, {sum(x['classe'] == 'pequena' for x in r)} pequenas, "
          f"{sum(x['classe'] == 'grande' for x in r)} grandes de {len(r)})")


if __name__ == '__main__':
    main()
