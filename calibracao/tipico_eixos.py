"""P2.15 (23/11): nível típico de cada eixo por nível de build, para o rendimento do plano automático comparar eixos
na mesma escala sem calibrar as réguas entre si. Típico = percentil 75 do nível eq. das linhas que fazem aquele eixo (o que uma linha focada alcança; a mediana caía no Healing Word que toda linha de conjurador carrega)
(nota > 0,5) em todos os resultados daquele nível. Grava a premissa plano.auto.tipico.
Uso (da raiz): python calibracao/tipico_eixos.py [--gravar]"""
import glob, json, os, statistics as st, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dh import planos

RAIZ = os.path.join(os.path.dirname(__file__), '..')
por = {}
for f in glob.glob(os.path.join(RAIZ, 'resultados', '*.json')):
    r = json.load(open(f, encoding='utf-8')); L = r.get('nivel')
    if not L: continue
    for x in r.get('linhas', {}).values():
        for eixo, sub in planos.EIXOS:
            n = planos._nota(x.get(eixo), 'campo_pico' if sub == 'campo' else sub)
            if n and n > 0.5: por.setdefault(sub or eixo, {}).setdefault(L, []).append(n)
tip = {e: {str(L): round(st.quantiles(v, n=4)[2], 2) for L, v in sorted(d.items()) if len(v) >= 5} for e, d in sorted(por.items())}
print(json.dumps(tip, ensure_ascii=False, indent=1))
if '--gravar' in sys.argv:
    p = os.path.join(RAIZ, 'premissas', 'premissas.json'); d = json.load(open(p, encoding='utf-8'))
    ant = d.get('plano.auto.tipico', {}).get('valor')
    d['plano.auto.tipico'] = {"valor": tip, "eixo": "plano", "desde": "2026-11-23",
        "descricao": "P2.15: nível típico de cada eixo por nível de build (percentil 75 das linhas que fazem o eixo, nota > 0,5, em todos os resultados). O rendimento do plano automático usa nível ÷ típico, para nenhum eixo ganhar só por ter uma escala maior. Gerado por calibracao/tipico_eixos.py --gravar.",
        "historico": d.get('plano.auto.tipico', {}).get('historico', []) + [{"data": "2026-11-23", "de": ant and "anterior", "para": "recalculado", "motivo": "P2.15 (usuário, 23/11): normalizar por eixo; recalculado dos resultados."}]}
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2); open(p, 'a').write('\n')
    print('gravado em premissas: plano.auto.tipico')
