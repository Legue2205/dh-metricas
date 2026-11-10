"""Orquestra os eixos para uma build e guarda o resultado em resultados/<id>.json."""
import json
import time
from pathlib import Path

from . import VERSAO, area, dano, defesa, orcamento, saves, suporte
from .build import carregar, impressao
from .controle import atencao, campo, efeitos, total

RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / 'resultados'
MODOS = {'rapido': dict(N=2000, absoluto=False), 'completo': dict(N=8000, absoluto=True)}


def avaliar_linha(b, linha, modo='rapido', regua=None, eixos=None):
    cfg = MODOS[modo]; corpo = dict(b['corpo'], **linha.get('corpo', {}))
    out = {}; livre = orcamento.reacao_livre(linha)
    lutas = b.get('recursos', {}).get('lutas_dia', 4)
    def quer(e): return e in linha and (not eixos or e in eixos)
    if quer('dano'): out['dano'] = dano.avaliar(linha['dano'], lutas)
    if quer('defesa'): out['defesa'] = defesa.avaliar(linha['defesa'], corpo, livre)
    if quer('saves'): out['saves'] = saves.avaliar(linha['saves'], corpo, livre)
    if quer('area'): out['area'] = area.avaliar(linha['area'], modo)
    if quer('suporte'): out['suporte'] = suporte.avaliar(linha['suporte'], b['nivel'])
    out['orcamento'] = orcamento.resumo(linha, b, campo.MAGIAS)
    if 'controle' in linha and (not eixos or 'controle' in eixos):
        campo.configurar(cfg['N'], 11)
        c = linha['controle']
        fn = efeitos.compilar(c.get('fontes', []), corpo, b['nivel'])
        ficha = atencao.ficha(c['atencao'], corpo)
        out['controle'] = total.avaliar(fn, ficha, b['nivel'], absoluto=cfg['absoluto'], regua=regua)
    return out


def avaliar(caminho, modo='rapido', forcar=False, eixos=None, linhas=None):
    b = carregar(caminho); imp = impressao(b)
    arq = RESULTADOS / f"{b['id']}.json"
    if arq.exists() and not forcar and not eixos and not linhas:
        velho = json.loads(arq.read_text(encoding='utf-8'))
        if velho.get('impressao') == imp and velho.get('versao') == VERSAO and (
                velho.get('modo') == modo or (velho.get('modo') == 'completo' and modo == 'rapido')):
            velho['_cache'] = True
            return b, velho
    regua = total.Regua(); t0 = time.time()
    res = dict(id=b['id'], nome=b['nome'], grupo=b['grupo'], nivel=b['nivel'], build=b.get('build', ''),
               impressao=imp, versao=VERSAO, modo=modo, linhas={})
    for l in b['linhas']:
        if linhas and l['id'] not in linhas: continue
        pr = l.get('principal', False)
        pr = list(pr) if isinstance(pr, list) else (['dano', 'defesa', 'controle', 'saves', 'area', 'suporte'] if pr else [])
        res['linhas'][l['id']] = dict(hipotese=l.get('hipotese', ''), principal=pr,
                                      **avaliar_linha(b, l, modo, regua, eixos))
    res['segundos'] = round(time.time() - t0, 1)
    if not eixos and not linhas:
        RESULTADOS.mkdir(exist_ok=True)
        arq.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
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
