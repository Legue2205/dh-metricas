"""Orquestra os eixos para uma build e guarda o resultado em resultados/<id>.json."""
import json
import time
from pathlib import Path

from . import VERSAO, area, base, horda, planos, saves
from . import eixos as E
from . import impressoes as I
from .build import carregar, impressao
from .controle import campo, total
from .eixos import MODOS  # noqa: F401  (compatibilidade)

RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / 'resultados'


def avaliar_linha(b, linha, modo='rapido', regua=None, eixos=None, velho=None, imps=None, imps_velhas=None, feitos=None):
    """Resultado de uma linha. Com velho (resultado antigo da linha) e as impressões nova e antiga de cada eixo, reaproveita
    os eixos cuja impressão não mudou; o orçamento (barato) é sempre refeito. feitos: lista que recebe os eixos calculados."""
    pres = E.presentes(linha, eixos)
    reusa = {e for e in pres if velho and imps and imps_velhas and e in velho and imps_velhas.get(e) == imps.get(e)}
    calc = [e for e in pres if e not in reusa]
    out = {}; lx = linha
    if 'tatico' in linha:
        cheio = any(e in calc for e in ('tatico',) + I.DO_TATICO)
        lx, resumo = E.expande_tatico(b, linha, leve=not cheio)
        out['tatico'] = resumo if 'tatico' in calc or not velho else velho['tatico']
    for e in E.ORDEM:
        if e == 'tatico': continue
        if e == 'orcamento': out[e] = E.calcular(e, b, lx, modo); continue
        if e in pres: out[e] = velho[e] if e in reusa else E.calcular(e, b, lx, modo, regua)
    if feitos is not None: feitos.extend(calc)
    return out


def _legado_valido(velho, imp, modo):
    """Regra antiga (antes da impressão por eixo): build, versão, premissas e modo iguais."""
    from . import premissas
    pv = velho.get('premissas', {})
    return velho.get('impressao') == imp and premissas.atuais(pv) == pv and (
        velho.get('modo') == modo or (velho.get('modo') == 'completo' and modo == 'rapido'))


def _sem_segundos(r):
    return {k: v for k, v in r.items() if k != 'segundos' and not k.startswith('_')}


def _planos(b, res):
    """Reescolhe os planos automáticos pelo rendimento das linhas e agrega todos os planos (in place em b e res)."""
    from . import plano_auto                      # D5 (23/11): plano auto reescolhido pelo rendimento das linhas
    vals = None
    for tag, pl in list(b.get('planos', {}).items()):
        if isinstance(pl, dict) and pl.get('auto'):
            vals = vals or plano_auto.valores_linhas(res['linhas'], b.get('nivel'))
            novo = plano_auto.gerar(b, tag, vals)
            if novo: b['planos'][tag] = novo
    pp = b.get('planos', {}).get('padrao')
    if isinstance(pp, dict) and pp.get('auto'):
        # Planos de foco automáticos (24/11, Etapa A): o melhor dia DENTRO do orçamento para cada eixo ativo, sem
        # somar eixos descalibrados entre si. Viram o anel externo (aneis.py) e a visão "foco" da calibração.
        for eixo, chave in plano_auto.FOCOS.items():
            if f'foco_{eixo}' in b['planos']: continue
            novo = plano_auto.gerar(b, f'foco_{eixo}', plano_auto.valores_linhas(res['linhas'], b.get('nivel'), so=chave))
            if novo: b['planos'][f'foco_{eixo}'] = dict(novo, descricao=('Foco em ' + eixo + '. ' + novo['descricao'])[:600])
    res['planos'] = planos.agregar(b, res['linhas'], campo.MAGIAS, base.letra)


def avaliar(caminho, modo='rapido', forcar=False, eixos=None, linhas=None):
    """Avalia uma build e grava resultados/<id>.json. Sem forcar, reaproveita do resultado antigo cada eixo cuja impressão
    digital (dh/impressoes.py) não mudou; VERSAO diferente recalcula tudo. eixos/linhas = cálculo parcial, sem cache e sem
    gravar. res['_recalculados'] = {linha: [eixos calculados]} (não é gravado)."""
    from . import premissas
    premissas.inicio()
    b = carregar(caminho); imp = impressao(b)
    arq = RESULTADOS / f"{b['id']}.json"
    parcial = bool(eixos or linhas)
    velho = None
    if arq.exists() and not forcar and not parcial:
        velho = json.loads(arq.read_text(encoding='utf-8'))
        if velho.get('versao') != VERSAO: velho = None
    if velho is not None:
        vm = velho.get('modo')
        if 'impressoes' not in velho:      # resultado de antes da impressão por eixo: vale a regra antiga, uma vez
            if _legado_valido(velho, imp, modo):
                velho['impressoes'] = I.da_build(b, vm, imp)
                from .arquivos import gravar
                gravar(arq, json.dumps(velho, ensure_ascii=False, indent=1))
                velho['_cache'] = True
                return b, velho
            velho = None
        else:
            pv = velho.get('premissas', {})
            for m in ([vm] if vm == 'completo' and modo == 'rapido' else []) + [modo]:
                if (velho.get('impressoes') == I.da_build(b, m, imp) and velho.get('impressao') == imp
                        and premissas.atuais(pv) == pv):
                    pp = b.get('planos', {}).get('padrao')
                    if isinstance(pp, dict) and pp.get('auto') and 'foco_dano' not in velho.get('planos', {}):
                        _planos(b, velho)      # 24/11: resultado de antes dos planos de foco — só refaz os planos
                        from .arquivos import gravar
                        gravar(arq, json.dumps({k: v for k, v in velho.items() if not k.startswith('_')}, ensure_ascii=False, indent=1))
                    velho['_cache'] = True
                    return b, velho
    regua = total.Regua(); t0 = time.time()
    res = dict(id=b['id'], nome=b['nome'], grupo=b['grupo'], nivel=b['nivel'], build=b.get('build', ''),
               impressao=imp, versao=VERSAO, modo=modo, linhas={})
    imps = {} if parcial else I.da_build(b, modo, imp)
    vimps = (velho or {}).get('impressoes', {}); vlinhas = (velho or {}).get('linhas', {}); feitos = {}
    for l in b['linhas']:
        if linhas and l['id'] not in linhas: continue
        pr = l.get('principal', False)
        pr = list(pr) if isinstance(pr, list) else (['dano', 'defesa', 'controle', 'saves', 'area', 'suporte'] if pr else [])
        feitos[l['id']] = []
        res['linhas'][l['id']] = dict(hipotese=l.get('hipotese', ''), principal=pr,
                                      **avaliar_linha(b, l, modo, regua, eixos, vlinhas.get(l['id']), imps.get(l['id']),
                                                      vimps.get(l['id']), feitos[l['id']]))
    if not parcial: _planos(b, res)
    res['segundos'] = round(time.time() - t0, 1)
    eixos_b = {e for l in b['linhas'] for e in ('dano', 'defesa', 'saves', 'controle', 'area', 'suporte', 'tatico') if l.get(e)}
    if any(l.get('dano') for l in b['linhas']): eixos_b.add('area')
    res['premissas'] = {**premissas.relevantes(eixos_b), **premissas.usadas()}
    if not parcial:
        res['impressoes'] = imps
        texto = json.dumps(res, ensure_ascii=False, indent=1)
        antigo = json.loads(arq.read_text(encoding='utf-8')) if arq.exists() else None
        if antigo is None or _sem_segundos(antigo) != _sem_segundos(json.loads(texto)):   # só "segundos" mudou: não regrava
            from .arquivos import gravar
            gravar(arq, texto)
    res['_recalculados'] = feitos
    return b, res


def principal(res, eixo):
    """Resultado do eixo na linha principal (ou na 1ª linha que tiver o eixo)."""
    ls = [l for l in res['linhas'].values() if eixo in l]
    for l in ls:
        if eixo in l['principal']: return l[eixo]
    return None  # sem linha principal nesse eixo (a planilha também deixa em branco)


def nota(x, sub=None):
    """(nível eq, letra) de um resultado de eixo; saves tem dois sub-eixos."""
    if x is None: return None
    if sub: x = x[sub]
    return (x['nivel_eq'], x['rank']) if x.get('nivel_eq') is not None else None


def preaquecer(caminhos, modo='rapido'):
    """Calcula (ou só carrega) no processo principal as réguas em cache/ que as builds vão pedir, antes de distribuir
    as builds entre processos: assim nenhum processo filho calcula régua e todos leem o mesmo arquivo pronto."""
    niveis, eixos = set(), set()
    for c in caminhos:
        try: b = carregar(c)
        except Exception: continue           # o erro aparece quando a build for avaliada
        niveis.add(b['nivel'])
        for l in b['linhas']: eixos |= {e for e in ('dano', 'saves', 'controle', 'area', 'tatico') if l.get(e)}
    if eixos & {'controle', 'tatico'}:
        r = total.Regua()
        for L in sorted(niveis | (set(base.NIVEIS_TESTE) if MODOS[modo]['absoluto'] else set())):
            for tipo in base.PESO_TIPO: r.vetor(tipo, L, 0, 1)
        r.salva()
    if 'area' in eixos:
        for s in area.CENARIOS.values(): area._regua_cache(s, area.N_MODO[modo])
    if eixos & {'dano', 'tatico'}: horda._regua_ref()
    if 'saves' in eixos:
        for rampa in ('res', 'vol'): saves.matriz(rampa)
