"""Cálculo de cada eixo de uma linha. Este arquivo entra na impressão digital de TODOS os eixos (dh/impressoes.py):
mexer aqui recalcula tudo. A orquestração e o cache ficam em dh/motor.py, que não entra em impressão nenhuma."""
from . import area, dano, defesa, horda, orcamento, saves, suporte
from .controle import atencao, campo, efeitos, total

MODOS = {'rapido': dict(N=2000, absoluto=False), 'completo': dict(N=8000, absoluto=True)}
# Ordem das chaves no resultado de uma linha (a mesma de antes da invalidação por eixo, para o diff ficar limpo)
ORDEM = ('tatico', 'dano', 'defesa', 'saves', 'area', 'suporte', 'orcamento', 'controle')
CAROS = ('tatico', 'dano', 'defesa', 'saves', 'area', 'suporte', 'controle')   # os que têm impressão; orçamento é sempre refeito


def corpo_da(b, linha):
    return dict(b['corpo'], **linha.get('corpo', {}))


def presentes(linha, eixos=None):
    """Eixos calculados numa linha (já com a linha crua: "tatico" gera dano e atenção)."""
    tem_dano = 'dano' in linha or 'tatico' in linha
    out = []
    for e in CAROS:
        if e == 'tatico': ok = 'tatico' in linha
        elif e == 'dano': ok = tem_dano
        elif e == 'area': ok = 'area' in linha or tem_dano          # área v2 (19/11): luta contra a horda
        elif e == 'controle': ok = 'controle' in linha or 'tatico' in linha
        else: ok = e in linha
        if ok and (e == 'tatico' or not eixos or e in eixos): out.append(e)
    return out


def expande_tatico(b, linha, leve=False):
    """Linha com "tatico": o motor tático gera o dano (DPR nas 9 CAs) e a ficha de atenção (fração colado/oculto).
    leve=True: mesma forma, sem rodar o motor (DPR e atenção zerados) — basta para o orçamento, que não lê esses números."""
    from . import tatico
    linha = dict(linha)
    if leve: dprs, aten, resumo = [0.0] * len(dano.CAS), {}, None
    else: dprs, aten, resumo = tatico.linha(b['tatico'], linha['tatico'], dano.CAS)
    linha['dano'] = {'medido': dprs, 'fonte': 'motor tático'}
    ctrl = dict(linha.get('controle') or {'fontes': [{'tipo': 'ameaca', 'nome': 'Corpo (ameaça)'}]})
    ctrl['atencao'] = dict(aten, **(ctrl.get('atencao') or {}))
    linha['controle'] = ctrl
    return linha, resumo


def calcular(e, b, linha, modo='rapido', regua=None):
    """Um eixo de uma linha (linha já expandida pelo motor tático, se tiver "tatico")."""
    cfg = MODOS[modo]; corpo = corpo_da(b, linha); inv = linha.get('invocacoes', [])
    if e == 'dano': return dano.avaliar(linha['dano'], b.get('recursos', {}).get('lutas_dia', 4), inv)
    if e == 'defesa': return defesa.avaliar(linha['defesa'], corpo, orcamento.reacao_livre(linha))
    if e == 'saves': return saves.avaliar(linha['saves'], corpo, orcamento.reacao_livre(linha))
    if e == 'area':
        velho = area.avaliar(linha['area'], modo) if linha.get('area') else None
        return dict(horda.avaliar(linha), antigo=velho and {k: velho[k] for k in ('nivel_eq', 'rank')},
                    melhor=(velho or {}).get('melhor') or 'dano de alvo único', areas=(velho or {}).get('areas', []))
    if e == 'suporte': return suporte.avaliar(linha['suporte'], b['nivel'])
    if e == 'orcamento': return orcamento.resumo(linha, b, campo.MAGIAS)
    if e == 'controle':
        campo.configurar(cfg['N'], 11)
        c = linha['controle']
        corpos = [i for i in inv if i.get('corpo', True)]   # invocações que ocupam espaço e atraem ataques
        fontes = c.get('fontes', []) + [dict(tipo='esqueletos', nome=f"Corpo ({i['quantidade']} {i['nome']})",
                                             pv=i['quantidade'] * i['pv'], ca_alvo=i['ca'] + i.get('cobertura', 0)) for i in corpos]
        fn = efeitos.compilar(fontes, corpo, b['nivel'])
        at = dict(c['atencao'])
        if corpos:   # D4 (23/11): o DPR da invocação entra na escolha de alvo do inimigo esperto (ameaça por PV)
            at.update(esqueletos=True, inv_pv=sum(i['quantidade'] * i['pv'] for i in corpos), inv_ca=corpos[0]['ca'],
                      inv_dpr=float(dano.dpr({'ataques': []}, 15, invocacoes=corpos)))
        ficha = atencao.ficha(at, corpo)
        return total.avaliar(fn, ficha, b['nivel'], absoluto=cfg['absoluto'], regua=regua)
    raise KeyError(e)
