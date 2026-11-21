"""Relatório de consistência por eixo ENTRE classes (19/11).

Para cada eixo e nível (7, 11): média, mínimo e máximo por classe (builds de referência originais do RPGBot), mais
checagens óbvias de ordem entre classes/subclasses e a sobra de recurso do plano padrão (valor em níveis de espaço).
Uso: python calibracao/consistencia.py [--md]   (lê resultados/ do último CI)
"""
import glob, json, os, re, sys, statistics as st

RAIZ = os.path.join(os.path.dirname(__file__), '..')
EIXOS = ['dano', 'defesa', 'resiliencia', 'vontade', 'campo', 'corpo', 'area', 'suporte']
NOME = {'defesa': 'Def. física', 'resiliencia': 'Def. mágica (Res)', 'vontade': 'Def. mágica (Von)', 'campo': 'Controle'}
CLASSES = ('fighter', 'wizard', 'cleric', 'barbarian', 'monk')
NIVEIS = (7, 11)


def carregar():
    d = {}
    for f in glob.glob(os.path.join(RAIZ, 'resultados', 'rpgbot-*.json')):
        m = re.match(r'rpgbot-(\w+)-(.+)-(\d+)\.json$', os.path.basename(f))
        if not m or m.group(1) not in CLASSES or m.group(2).endswith('-puro'): continue
        r = json.load(open(f)); p = (r.get('planos') or {}).get('padrao') or {}
        ex = p.get('eixos') or {}
        val = {e: (ex.get(e) or {}).get('nivel_eq') for e in EIXOS}
        sob = p.get('sobra') or {}
        val['_sobra'] = sum(int(k) * v for k, v in (sob.get('espacos') or {}).items()) + sum(v for k, v in sob.items() if k != 'espacos')
        d[(m.group(1), m.group(2), int(m.group(3)))] = val
    return d


def tabela(d, md=False):
    out = []
    for e in EIXOS + ['_sobra']:
        out.append(f"\n## {NOME.get(e, e.strip('_').capitalize())}" if md else f"\n== {NOME.get(e, e)}")
        for L in NIVEIS:
            partes = []
            for c in CLASSES:
                xs = [(s, v[e]) for (cc, s, l), v in d.items() if cc == c and l == L and v.get(e) is not None]
                if not xs: continue
                vs = [x for _, x in xs]; lo = min(xs, key=lambda t: t[1]); hi = max(xs, key=lambda t: t[1])
                partes.append(f"{c} {st.mean(vs):.1f} [{lo[1]:.1f} {lo[0]} … {hi[1]:.1f} {hi[0]}]")
            out.append(f"  nv{L}: " + " | ".join(partes))
    return out


def g(d, c, s, L, e): return (d.get((c, s, L)) or {}).get(e)


def media(d, c, L, e):
    xs = [v[e] for (cc, _, l), v in d.items() if cc == c and l == L and v.get(e) is not None]
    return st.mean(xs) if xs else None


def checagens(d):
    """(descrição, a, b): espera-se a >= b. Lista explícita para ficar auditável."""
    regras = []
    for L in NIVEIS:
        regras += [
            (f"nv{L} Suporte: média dos clérigos ≥ média dos fighters", media(d, 'cleric', L, 'suporte'), media(d, 'fighter', L, 'suporte')),
            (f"nv{L} Suporte: Life ≥ média dos fighters", g(d, 'cleric', 'life', L, 'suporte'), media(d, 'fighter', L, 'suporte')),
            (f"nv{L} Área: Evocation ≥ Light", g(d, 'wizard', 'evocation', L, 'area'), g(d, 'cleric', 'light', L, 'area')),
            (f"nv{L} Área: Light ≥ média dos clérigos", g(d, 'cleric', 'light', L, 'area'), media(d, 'cleric', L, 'area')),
            (f"nv{L} Área: média dos clérigos ≥ média dos fighters", media(d, 'cleric', L, 'area'), media(d, 'fighter', L, 'area')),
            (f"nv{L} Def. física: Forge ≥ média dos wizards", g(d, 'cleric', 'forge', L, 'defesa'), media(d, 'wizard', L, 'defesa')),
            (f"nv{L} Def. física: média dos fighters ≥ média dos wizards", media(d, 'fighter', L, 'defesa'), media(d, 'wizard', L, 'defesa')),
            (f"nv{L} Dano: média dos fighters ≥ média dos clérigos", media(d, 'fighter', L, 'dano'), media(d, 'cleric', L, 'dano')),
            (f"nv{L} Controle: média dos wizards ≥ média dos clérigos", media(d, 'wizard', L, 'campo'), media(d, 'cleric', L, 'campo')),
            (f"nv{L} Controle: média dos clérigos ≥ média dos fighters", media(d, 'cleric', L, 'campo'), media(d, 'fighter', L, 'campo')),
            (f"nv{L} Corpo: média dos fighters ≥ média dos wizards", media(d, 'fighter', L, 'corpo'), media(d, 'wizard', L, 'corpo')),
        ]
    return regras


def main():
    md = '--md' in sys.argv; d = carregar()
    print(f"# Consistência por eixo entre classes ({len(d)} fatias originais)" if md else f"{len(d)} fatias originais")
    print("\n".join(tabela(d, md)))
    print("\n## Checagens" if md else "\n== Checagens (a ≥ b)")
    for desc, a, b in checagens(d):
        if a is None or b is None: print(f"  ?  {desc} (sem dado)"); continue
        print(f"  {'ok' if a >= b - 0.05 else 'XX'}  {desc}: {a:.1f} vs {b:.1f}")


if __name__ == '__main__':
    main()
