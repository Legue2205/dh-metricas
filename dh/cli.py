"""Linha de comando.

  python -m dh validar builds/*.json
  python -m dh rapido  builds/kael-7.json            # N=2000, sem absoluto: segundos
  python -m dh completo builds/kael-7.json           # N=8000 + controle absoluto (10 níveis)
  python -m dh linhas  builds/kael-7.json            # linhas para colar (TSV); com --json: células por planilha
  python -m dh painel                                # resumo de todos os resultados salvos
  python -m dh regua 7 9 10                          # pré-calcula a régua de controle desses níveis
Opções: --forcar (ignora o cache de resultados), --eixo dano|defesa|controle, --linha <id>, --json
"""
import argparse
import glob
import json
import sys

from . import motor
from .base import NIVEIS_TESTE, PESO_TIPO, TIPOS
from .build import ErroBuild, avisos, carregar, validar


def _fmt(x, c=1):
    return '-' if x is None else (f'{x:.{c}f}'.replace('.', ',') if isinstance(x, float) else str(x))


def _resumo(res):
    print(f"\n{res['nome']} ({res['id']}, nível {res['nivel']}) — modo {res['modo']}"
          f"{' (cache)' if res.get('_cache') else ''}, {res.get('segundos', 0)} s")
    for lid, l in res['linhas'].items():
        marca = '' if not l['principal'] else (' *' if len(l['principal']) == 3 else ' *' + '/'.join(l['principal']))
        print(f"  [{lid}{marca}] ({l.get('orcamento', {}).get('tag', '-')}) {l['hipotese'][:80]}")
        if 'dano' in l:
            d = l['dano']; dp = d['dpr']
            print(f"    Dano     {d['rank']:>2}  nível eq {_fmt(d['nivel_eq'])}  ({d['perfil']})  "
                  f"DPR CA15 {_fmt(dp['CA 15'])} · CA16 {_fmt(dp['CA 16'])} · CA20 {_fmt(dp['CA 20'])}")
        if 'defesa' in l:
            d = l['defesa']
            print(f"    Defesa   {d['rank']:>2}  nível eq {_fmt(d['nivel_eq'])}  ({d['perfil']})  "
                  f"blindagem CR {_fmt(d['blindagem'], 2)} · durabilidade CR {_fmt(d['durabilidade'], 2)}")
        if 'saves' in l:
            v = l['saves']
            print(f"    Saves        Resiliência {v['resiliencia']['rank']} ({_fmt(v['resiliencia']['nivel_eq'])}) · "
                  f"Vontade {v['vontade']['rank']} ({_fmt(v['vontade']['nivel_eq'])})")
        if 'area' in l and l['area']['nivel_eq'] is not None:
            a_ = l['area']
            print(f"    Área     {a_['rank']:>2}  nível eq {_fmt(a_['nivel_eq'])}  ({a_['melhor']})")
        if 'suporte' in l:
            u = l['suporte']
            print(f"    Suporte  {u['rank']:>2}  nível eq {_fmt(u['nivel_eq'])}  ({u['perfil']}; of {_fmt(u['ofensivo'])} · def {_fmt(u['defensivo'])})")
        o = l.get('orcamento', {})
        if o.get('reacao') or o.get('espacos_por_eixo'):
            esp = '; '.join(f"{e}: " + ', '.join(f"{v:g}×{k}º" for k, v in sorted(g.items())) for e, g in o['espacos_por_eixo'].items())
            print(f"    Recursos     tag {o['tag']} · reação livre {_fmt(float(o['reacao_livre']), 2)}" + (f" · espaços: {esp}" if esp else ''))
        if 'controle' in l:
            c = l['controle']
            ab = f"  absoluto {_fmt(c['nivel_absoluto'])} ({c['rank_absoluto']})" if 'nivel_absoluto' in c else ''
            print(f"    Controle {c['rank']:>2}  nível eq {_fmt(c['nivel_eq'])}  campo {_fmt(c['nivel_campo'])} · "
                  f"atenção {_fmt(c['nivel_atencao'])} · vidas {c['vidas_total']:+.2f}{ab}")
            print('             por encontro: ' + ' · '.join(f"{t.split(' ')[0]} {_fmt(v)}" for t, v in c['por_tipo'].items()))


def _linhas(b, res):
    """Valores (sem as colunas de fórmula) no layout de cada planilha de rank."""
    nome, grupo, bld = b['nome'], b['grupo'], b.get('build', '')
    blocos = {'Ranks de dano › Personagens (A:M, depois S:T)': [],
              'Ranks de defesa › Personagens (A:H, depois O:P)': [],
              'Ranks de controle › Controle total (A:J, M, O, Q:S, V:W)': []}
    for lid, l in res['linhas'].items():
        sim = lambda eixo: 'Sim' if eixo in l['principal'] else 'Não'
        rotulo = nome if lid == 'principal' else f"{nome} ({lid.replace('-', ' ')})"
        if 'dano' in l:
            blocos['Ranks de dano › Personagens (A:M, depois S:T)'].append(
                [nome, grupo, bld, l['hipotese'], *[_fmt(v) for v in l['dano']['dpr'].values()], '|', sim('dano'), b['id']])
        if 'defesa' in l:
            d = l['defesa']
            blocos['Ranks de defesa › Personagens (A:H, depois O:P)'].append(
                [nome, grupo, bld, l['hipotese'], _fmt(d['pv_efetivo']), _fmt(d['ca']), _fmt(d['blindagem'], 2),
                 _fmt(d['durabilidade'], 2), '|', sim('defesa'), b['id']])
        if 'controle' in l:
            c = l['controle']
            blocos['Ranks de controle › Controle total (A:J, M, O, Q:S, V:W)'].append(
                [rotulo, grupo, sim('controle'), str(b['nivel']), *[_fmt(c['por_tipo'][t], 2) for t in PESO_TIPO], '|',
                 _fmt(c['nivel_campo'], 2), '|', _fmt(c['nivel_atencao'], 2), '|', _fmt(c['vidas_total'], 3),
                 _fmt(c['vidas_campo'], 3), _fmt(c['vidas_atencao'], 3), '|', b['id'],
                 _fmt(c.get('nivel_absoluto'), 2)])
    for titulo, rows in blocos.items():
        if rows:
            print(f'\n# {titulo}   ("|" marca colunas de fórmula a pular)')
            for r in rows: print('\t'.join(r))


def main(argv=None):
    ap = argparse.ArgumentParser(prog='dh', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('comando', choices=['validar', 'rapido', 'completo', 'linhas', 'painel', 'regua'])
    ap.add_argument('alvos', nargs='*')
    ap.add_argument('--forcar', action='store_true')
    ap.add_argument('--eixo', action='append')
    ap.add_argument('--linha', action='append')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    arquivos = [f for p in a.alvos for f in sorted(glob.glob(p))] if a.comando not in ('regua', 'painel') else []

    if a.comando == 'validar':
        ok = True
        for f in arquivos:
            b = json.load(open(f, encoding='utf-8')); erros = validar(b); av = [] if erros else avisos(b)
            print(('ERRO  ' if erros else 'AVISO ' if av else 'OK    ') + f); ok &= not erros
            for e in erros: print('      -', e)
            for e in av: print('      ~', e)
        return 0 if ok else 1

    if a.comando == 'regua':
        from .controle.total import Regua
        r = Regua()
        for L in (int(x) for x in (a.alvos or NIVEIS_TESTE)):
            for t, _, _ in TIPOS: r.vetor(t, L, 0, 1)
            r.salva(); print(f'régua do nível {L} pronta ({r.arq.name})')
        return 0

    if a.comando == 'painel':
        import pathlib
        cols = [('Dano', 'dano', None), ('Defesa', 'defesa', None), ('Resil.', 'saves', 'resiliencia'),
                ('Vontade', 'saves', 'vontade'), ('Controle', 'controle', None), ('Área', 'area', None), ('Suporte', 'suporte', None)]
        print(f"{'ID':20s} {'nv':>3s}  " + '  '.join(f'{c[0]:>8s}' for c in cols))
        for f in sorted(pathlib.Path(motor.RESULTADOS).glob('*.json')):
            r = json.loads(f.read_text(encoding='utf-8'))
            cel = []
            for _, eixo, sub in cols:
                n = motor.nota(motor.principal(r, eixo), sub); cel.append(f"{_fmt(float(n[0]))} {n[1]}" if n else '-')
            print(f"{r['id']:20s} {r['nivel']:>3d}  " + '  '.join(f'{x:>8s}' for x in cel))
        return 0

    modo = 'completo' if a.comando == 'completo' else 'rapido'
    for f in arquivos:
        try:
            b, res = motor.avaliar(f, modo, a.forcar, a.eixo, a.linha)
        except ErroBuild as e:
            print(e, file=sys.stderr); return 1
        if a.comando == 'linhas' and a.json:
            from .planilhas import itens
            print(json.dumps(itens(b, res), ensure_ascii=False))
        elif a.json: print(json.dumps(res, ensure_ascii=False, indent=1))
        elif a.comando == 'linhas': _linhas(b, res)
        else: _resumo(res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
