"""Linha de comando.

  python -m dh validar builds/*.json
  python -m dh rapido  builds/kael-7.json            # N=2000, sem absoluto: segundos
  python -m dh completo builds/kael-7.json           # N=8000 + controle absoluto (10 níveis)
  python -m dh linhas  builds/kael-7.json            # linhas para colar (TSV); com --json: células por planilha
  python -m dh painel [padrao|combate_unico|dia_longo] # resumo de todos os resultados, pelo plano do dia
  python -m dh site                                  # gera docs/index.html (site estático) a partir de resultados/
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
        print(f"  [{lid}{marca}] {l['hipotese'][:90]}")
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
            print(f"    Recursos     reação livre {_fmt(float(o['reacao_livre']), 2)}" + (f" · espaços: {esp}" if esp else ''))
        if 'controle' in l:
            c = l['controle']
            ab = f"  absoluto {_fmt(c['nivel_absoluto'])} ({c['rank_absoluto']})" if 'nivel_absoluto' in c else ''
            print(f"    Controle {c['rank']:>2}  nível eq {_fmt(c['nivel_eq'])}  campo {_fmt(c['nivel_campo'])} · "
                  f"atenção {_fmt(c['nivel_atencao'])} · vidas {c['vidas_total']:+.2f}{ab}")
            print('             por encontro: ' + ' · '.join(f"{t.split(' ')[0]} {_fmt(v)}" for t, v in c['por_tipo'].items()))


def _aneis(b, res):
    from . import aneis
    a = aneis.calcular(b, res)
    if not a: return
    eq = a['equilibrado'] or {}
    nomes = dict(dano='dano', deff='def. física', defm='def. mágica', controle='controle', corpo='corpo', area='área', suporte='suporte')
    print('  ANÉIS (interno · equilibrado · externo): ' + ' | '.join(
        f"{nomes[k]} {_fmt(a['interno'][k]['n'])} · {_fmt(eq[k]['n']) if k in eq else '–'} · {_fmt(a['externo'][k]['n'])}"
        for k in a['externo']))


def _planos(res):
    for tag, p in res.get('planos', {}).items():
        hy = f" · hypercharged ×{p['hypercharged']:g}" if p['hypercharged'] != 1 else ''
        print(f"  PLANO {tag}{hy}: " + ' → '.join(f"{c['linha']}({c['categoria']})" for c in p['combates']))
        sb = p['sobra']; esp = ', '.join(f"{v:g}×{k}º" for k, v in sb.get('espacos', {}).items())
        resto = ', '.join(f"{v:g} {k}" for k, v in sb.items() if k != 'espacos')
        print('    sobra para utilidade: ' + (', '.join(x for x in (esp, resto) if x) or 'nada'))
        for e, v in p['eixos'].items():
            print(f"    {e:12s} dia {v['rank']:>2} {_fmt(float(v['nivel_eq']))}   " +
                  ' · '.join(f"{k} {_fmt(float(x))}" for k, x in v['por_categoria'].items()))


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


def _carrega_modulos():
    """Inicializador dos processos filhos: importa tudo antes da 1ª build, para que nenhuma build pague (nem registre
    como usadas) as premissas lidas na importação de um módulo carregado tarde."""
    import os
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ.setdefault(v, '1')
    from . import area, horda, planos, saves, tatico  # noqa: F401
    from .controle import total  # noqa: F401


def _um(f, modo, forcar, eixo, linha):
    try:
        b, res = motor.avaliar(f, modo, forcar, eixo, linha)
    except ErroBuild as e:
        return f, None, str(e)
    return f, dict(id=res['id'], segundos=res.get('segundos'), cache=res.get('_cache', False)), None


def _em_paralelo(arquivos, modo, a):
    """Várias builds: um processo por núcleo (os.cpu_count()). As réguas são preaquecidas aqui antes; cada build
    grava o próprio resultados/<id>.json. Saída: uma linha por build, na ordem em que terminam."""
    import os
    import time
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from multiprocessing import get_context
    t0 = time.time(); motor.preaquecer(arquivos, modo)
    n = min(os.cpu_count() or 1, len(arquivos)); erro = 0
    print(f'{len(arquivos)} builds em {n} processo(s) ({modo}); réguas prontas em {time.time() - t0:.0f} s', flush=True)
    with ProcessPoolExecutor(n, mp_context=get_context('spawn'), initializer=_carrega_modulos) as ex:
        fut = [ex.submit(_um, f, modo, a.forcar, a.eixo, a.linha) for f in arquivos]
        for i, ft in enumerate(as_completed(fut), 1):
            f, r, e = ft.result()
            if e: erro = 1; print(f'[{i}/{len(arquivos)}] ERRO {e}', file=sys.stderr, flush=True); continue
            print(f"[{i}/{len(arquivos)}] {r['id']:40s} " + ('em cache' if r['cache'] else f"{r['segundos']:.1f} s"), flush=True)
    print(f'pronto em {time.time() - t0:.0f} s')
    return erro


def main(argv=None):
    ap = argparse.ArgumentParser(prog='dh', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('comando', choices=['validar', 'rapido', 'completo', 'linhas', 'painel', 'regua', 'site', 'tatico', 'calibrar', 'expandir', 'plano-auto', 'premissas', 'premissa', 'comparar'])
    ap.add_argument('alvos', nargs='*')
    ap.add_argument('--forcar', action='store_true')
    ap.add_argument('--eixo', action='append')
    ap.add_argument('--linha', action='append')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--md', action='store_true', help='premissas: escreve HIPOTESES.md')
    ap.add_argument('--motivo', default='', help='premissa: por que o valor mudou (vai para o histórico)')
    ap.add_argument('--registrar', metavar='ROTULO', help='calibrar: grava a rodada em calibracao/historico.jsonl')
    ap.add_argument('--visao', default='padrao', help='comparar: padrao | combate_unico | dia_longo | externo | interno | misto (D2: plano + α·(externo − plano))')
    ap.add_argument('--grupo', action='append', help='comparar: só estes grupos')
    ap.add_argument('--w', type=float, action='append', help='tatico: razão de piscinas, valor de 1 PV dentro do orçamento (padrão 1)')
    ap.add_argument('--comp', action='append', help='tatico: composição (padrão: as três)')
    a = ap.parse_args(argv)
    arquivos = [f for p in a.alvos for f in sorted(glob.glob(p))] if a.comando not in ('regua', 'painel', 'site', 'calibrar', 'expandir', 'premissas', 'premissa', 'comparar') else []

    if a.comando == 'validar':
        ok = True
        for f in arquivos:
            b = json.load(open(f, encoding='utf-8')); erros = validar(b); av = [] if erros else avisos(b)
            print(('ERRO  ' if erros else 'AVISO ' if av else 'OK    ') + f); ok &= not erros
            for e in erros: print('      -', e)
            for e in av: print('      ~', e)
        return 0 if ok else 1

    if a.comando == 'tatico':
        from . import tatico
        for f in arquivos:
            b = json.load(open(f, encoding='utf-8'))
            if 'tatico' not in b: print(f'{f}: sem bloco "tatico"'); continue
            for comp in a.comp or list(tatico.COMPOSICOES):
              for w in a.w or [1.0]:
                r = tatico.avaliar(b['tatico'], w=w, composicao=comp)
                if a.json: print(json.dumps({'w': w, 'composicao': comp, **r}, ensure_ascii=False)); continue
                print(f"\n{b['nome']} — {comp} ({tatico.COMPOSICOES[comp]['nota']}) · w = {w:g} · "
                      f"orçamento {_fmt(tatico.Modelo(b['tatico']).orcamento())} PV por luta")
                for pol, res in r.items():
                    m = res['media']
                    print(f"  {pol:9s} média: DPR {_fmt(m['dpr'])} · recebido/luta {_fmt(m['recebido_luta'])} · escondido no fim do turno "
                          f"{_fmt(m['escondido_fim_turno'])}% · lutas acima do orçamento {_fmt(m['lutas_acima_do_orcamento'])}%")
                    if pol != 'otima': continue
                    for t, v in res.items():
                        if t == 'media': continue
                        print(f"    {t}: DPR {_fmt(v['dpr'])} · recebido {_fmt(v['recebido_luta'])} · escondido {_fmt(v['escondido_fim_turno'])}%")
                        print('      R1:   ' + ' · '.join(f"{k} {_fmt(x)}%" for k, x in v['acoes_r1'].items() if x >= 1))
                        print('      R2-4: ' + ' · '.join(f"{k} {_fmt(x)}%" for k, x in v['acoes_r2_4'].items() if x >= 1))
        return 0

    if a.comando == 'expandir':
        from .progressao import expandir
        esc = expandir(a.alvos or None)
        print(f'{len(esc)} fatia(s) escrita(s)' + ''.join(f'\n  {p.name}' for p in esc)); return 0

    if a.comando == 'plano-auto':
        from .plano_auto import aplicar
        for f in arquivos:
            b = json.load(open(f, encoding='utf-8')); feitos = aplicar(b)
            if feitos: open(f, 'w', encoding='utf-8').write(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
            print(f, '→', ', '.join(f"{t}: {' / '.join(b['planos'][t]['combates'])}" for t in feitos) or 'nada a gerar (planos escritos à mão ou sem "auto")')
        return 0

    if a.comando == 'calibrar':
        from . import calibrar
        from .site import dados
        d = dados(); rods = []
        for p, g in calibrar.carregar(a.alvos):
            r = calibrar.avaliar(g, d); rods.append(r)
            print(json.dumps(r, ensure_ascii=False)) if a.json else calibrar.imprimir(r)
        if a.registrar: print('rodada gravada em', calibrar.registrar(a.registrar, rods))
        return 0

    if a.comando in ('premissas', 'premissa'):
        from . import premissas
        if a.comando == 'premissa':
            if len(a.alvos) != 2: print('uso: dh premissa <nome> <valor> --motivo "..."'); return 1
            v = json.loads(a.alvos[1]); premissas.definir(a.alvos[0], v, a.motivo)
            print(f'{a.alvos[0]} = {v}. Builds afetadas (recalcule com dh completo):')
        import pathlib
        uso = {}
        for f in sorted(pathlib.Path(motor.RESULTADOS).glob('*.json')):
            for n in json.loads(f.read_text(encoding='utf-8')).get('premissas', {}): uso.setdefault(n, []).append(f.stem)
        if a.comando == 'premissa': print('  ' + ', '.join(uso.get(a.alvos[0], [])) or '  (nenhuma ainda registrada)'); premissas.recarregar()
        if a.md or a.comando == 'premissa':
            (pathlib.Path(motor.RAIZ) / 'HIPOTESES.md').write_text(premissas.markdown(uso), encoding='utf-8'); print('HIPOTESES.md atualizado')
        if a.comando == 'premissas' and not a.md:
            for n, v in premissas._dados().items():
                if not n.startswith('_'): print(f"{n:45s} {str(v['valor']):>6s}  {len(uso.get(n, [])):3d} builds  {v.get('descricao', '')[:70]}")
        return 0

    if a.comando == 'comparar':
        from . import comparar
        from .site import dados
        print(comparar.tabela(dados(), a.alvos or None, a.visao, a.grupo, a.json)); return 0

    if a.comando == 'site':
        from .site import gerar
        print('site gerado em', gerar()); return 0

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
        tag = (a.alvos or ['padrao'])[0]
        print(f"Plano do dia: {tag}. Builds marcadas com ~ ainda não têm esse plano (mostra a linha principal).")
        print(f"{'ID':21s} {'nv':>3s}  " + '  '.join(f'{c[0]:>8s}' for c in cols))
        for f in sorted(pathlib.Path(motor.RESULTADOS).glob('*.json')):
            r = json.loads(f.read_text(encoding='utf-8')); p = r.get('planos', {}).get(tag)
            cel = []
            for _, eixo, sb in cols:
                if p: x = p['eixos'].get(sb or eixo); n = (x['nivel_eq'], x['rank']) if x else None
                else: n = motor.nota(motor.principal(r, eixo), sb)
                cel.append(f"{_fmt(float(n[0]))} {n[1]}" if n else '-')
            print(f"{('' if p else '~') + r['id']:21s} {r['nivel']:>3d}  " + '  '.join(f'{x:>8s}' for x in cel))
        return 0

    modo = 'completo' if a.comando == 'completo' else 'rapido'
    if a.comando in ('rapido', 'completo') and not a.json and len(arquivos) > 1:
        return _em_paralelo(arquivos, modo, a)
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
        else: _resumo(res); _planos(res); _aneis(b, res)
    return 0


if __name__ == '__main__':
    sys.exit(main())
