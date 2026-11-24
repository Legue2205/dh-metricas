"""Etapa B, simulação (24/11): o plano automático escolhendo pela moeda "dano equivalente" (DE) em vez da soma de níveis.

Não mexe no motor: refaz OFFLINE só o plano padrão de cada build (as linhas vêm de resultados/), com o rendimento de cada
linha em DE por luta, e mede o τ por régua (pista × valor, dentro da classe) contra o plano padrão atual.

Conversão provisória para DE por luta (dano causado = dano evitado, 1:1; tudo temporário, vira premissa moeda.* se adotado):
  dano     = DPR na CA de referência do nível (14 + nível÷4: 15 no 7, 16 no 11) × rounds por luta
  suporte  = suporte.total (já é dano equivalente por round: ofensivo + defensivo) × rounds por luta
  controle = vidas da party poupadas (controle.vidas_total, por luta) × PV do membro padrão da party de referência
  área     = PESO_AREA × fração da horda que a referência tira no nível eq. da linha × PV total da horda do nível da build
             (PESO_AREA = parcela das lutas que são horda; provisório 0,5)
  defesa/saves ficam de fora (passivos: quase não mudam entre linhas).

Uso (da raiz): python calibracao/moeda_de.py [--nivel 7] [--grupo Chassi|Pacote] [--build <id>] [--peso-area 0.5]
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

from dh import area, planos, plano_auto, base  # noqa: E402
from dh.build import carregar  # noqa: E402
from dh.controle import atencao, campo  # noqa: E402
from dh.premissas import P  # noqa: E402

PESO_AREA = 0.5


def ca_ref(nv): return 14 + nv // 4


def _dpr(d, nv):
    dpr = (d or {}).get('dpr') or {}
    if not dpr: return 0.0
    alvo = ca_ref(nv)
    k = min(dpr, key=lambda c: abs(int(c.split()[1]) - alvo))
    return float(dpr[k])


_R1 = None


def _frac_area(L):
    global _R1
    if _R1 is None:
        s = area.CENARIOS['padrao']; _R1, _ = area._regua_cache(s, area.N_MODO['rapido'])
        _R1 = {int(k): float(v) for k, v in _R1.items()}
    if L <= 0: return 0.0
    if L < 1: return L / 0.5 * _R1[1] * 0.5 if L else 0.0
    if L >= 20: return _R1[20]
    lo = int(L); a = L - lo
    return _R1[lo] * (1 - a) + _R1[lo + 1] * a


def de_linha(x, nv, peso_area=PESO_AREA):
    R = P('base.rounds_por_luta')
    pv = atencao.ref_padrao('conjurador', nv)['pv']
    hp0 = area.CR[area.HORDA[nv]][0]
    d = _dpr(x.get('dano'), nv) * R
    s = float((x.get('suporte') or {}).get('total') or 0) * R
    c = float((x.get('controle') or {}).get('vidas_total') or 0) * pv
    a = peso_area * _frac_area(float((x.get('area') or {}).get('nivel_eq') or 0)) * area.NH * hp0
    return dict(total=d + s + c + a, dano=d, suporte=s, controle=c, area=a)


def plano_de(caminho, peso_area=PESO_AREA):
    """(eixos do plano padrão atual, eixos do plano escolhido em DE, combates DE, combates atuais)."""
    b = carregar(caminho)
    res = json.load(open(os.path.join('resultados', os.path.basename(caminho)), encoding='utf-8'))
    pp = b.get('planos', {}).get('padrao')
    if not (isinstance(pp, dict) and pp.get('auto')) or 'padrao' not in res.get('planos', {}): return None
    vals = {lid: de_linha(x, b['nivel'], peso_area)['total'] for lid, x in res['linhas'].items()}
    novo = plano_auto.gerar(b, 'padrao', vals)
    if not novo: return None
    b['planos'] = {'padrao': novo}
    ag = planos.agregar(b, res['linhas'], campo.MAGIAS, base.letra)['padrao']
    e = lambda p: {k: (v or {}).get('nivel_eq') for k, v in p['eixos'].items() if isinstance(v, dict)}
    comb = lambda p: [c if isinstance(c, str) else c.get('linha') for c in p.get('combates', [])]
    return e(res['planos']['padrao']), e(ag), comb(novo), comb(res['planos']['padrao'])


def main():
    a = sys.argv
    pa = float(a[a.index('--peso-area') + 1]) if '--peso-area' in a else PESO_AREA
    if '--build' in a:
        bid = a[a.index('--build') + 1]
        res = json.load(open(f'resultados/{bid}.json', encoding='utf-8')); b = json.load(open(f'builds/{bid}.json'))
        for lid, x in res['linhas'].items():
            d = de_linha(x, b['nivel'], pa)
            print(f"  {lid:24s} DE {d['total']:6.0f}  (dano {d['dano']:5.0f} sup {d['suporte']:5.0f} ctrl {d['controle']:5.0f} área {d['area']:5.0f})")
        r = plano_de(f'builds/{bid}.json', pa)
        if r: print('  plano atual:', r[3], '\n  plano DE:   ', r[2], '\n  eixos atual:', r[0], '\n  eixos DE:   ', r[1])
        return
    from comparar_chassi import pista, PISTA_EIXO
    from teto_subclasse import gabaritos, tau
    nvs = [int(a[a.index('--nivel') + 1])] if '--nivel' in a else [7, 11]
    grupo = (a[a.index('--grupo') + 1] if '--grupo' in a else 'Chassi').lower()
    gabs = gabaritos()
    mapa = {'dano': 'dano', 'controle': 'campo', 'area': 'area', 'suporte': 'suporte'}
    for nv in nvs:
        cands = {'atual': {}, 'de': {}}; mud = 0; tot = 0
        for f in sorted(glob.glob(f'builds/{grupo}-*-{nv}.json')):
            bj = json.load(open(f, encoding='utf-8'))
            if grupo == 'chassi' and bj.get('variante') != 'sem-feat': continue
            r = plano_de(f, pa)
            if not r: continue
            tot += 1; mud += r[2] != r[3]
            for k, ev in (('atual', r[0]), ('de', r[1])):
                for eixo, ch in mapa.items():
                    v = ev.get(ch)
                    if v is not None: cands[k].setdefault(eixo, {})[(bj['classe'], bj['subclasse'])] = {'piso': (v, bj['id'])}
        print(f'\n== nv{nv} ({grupo}): plano mudou em {mud}/{tot} builds')
        for eixo in mapa:
            eg = next(g for g, m in PISTA_EIXO.items() if m == eixo)
            ta = tau(cands['atual'].get(eixo, {}), gabs, eg, 'piso'); td = tau(cands['de'].get(eixo, {}), gabs, eg, 'piso')
            f = lambda t: f"{t['tau']:+.2f} (n={t['n']})" if t['tau'] is not None else '—'
            print(f'  {eixo:9s} atual {f(ta)}  →  DE {f(td)}')


if __name__ == '__main__':
    main()
