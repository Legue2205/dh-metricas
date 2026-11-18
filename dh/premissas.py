"""Premissas nomeadas (a "bíblia de hipóteses"): os pesos do nosso modelo, versionados como os de um modelo de IA.

premissas/premissas.json = {nome: {valor, eixo, descricao, desde, historico: [...]}}.
- Motores: P('controle.peso_no_controle.sentinela') — lido na hora do cálculo e registrado como "usado".
- Builds: qualquer valor do JSON pode ser {"$p": "nome"} (resolvido ao carregar a build, também registrado).
- O motor guarda em resultados/<id>.json as premissas usadas e seus valores; se um valor mudar, o cache cai
  só para quem usou aquela premissa (dh completo recalcula sozinho).
- HIPOTESES.md é gerado daqui (dh premissas --md): nunca editar à mão.
"""
import datetime
import json
from pathlib import Path

ARQ = Path(__file__).resolve().parents[1] / 'premissas' / 'premissas.json'
_DADOS = None
_USADAS = {}


def _dados():
    global _DADOS
    if _DADOS is None: _DADOS = json.loads(ARQ.read_text(encoding='utf-8'))
    return _DADOS


def recarregar():
    global _DADOS
    _DADOS = None


def P(nome, padrao=None):
    d = _dados().get(nome)
    if d is None:
        if padrao is None: raise KeyError(f'premissa desconhecida: {nome} (cadastre em premissas/premissas.json)')
        return padrao
    _USADAS[nome] = d['valor']
    return d['valor']


def inicio(): _USADAS.clear()
def usadas(): return dict(sorted(_USADAS.items()))


def atuais(nomes):
    d = _dados(); return {n: (d[n]['valor'] if n in d else None) for n in nomes}


def resolver(x):
    """Troca {"$p": nome} pelo valor (recursivo)."""
    if isinstance(x, dict):
        if set(x) == {'$p'}: return P(x['$p'])
        return {k: resolver(v) for k, v in x.items()}
    if isinstance(x, list): return [resolver(v) for v in x]
    return x


def definir(nome, valor, motivo=''):
    d = _dados()
    if nome not in d: raise KeyError(f'premissa desconhecida: {nome}')
    hoje = datetime.date.today().isoformat(); p = d[nome]
    p.setdefault('historico', []).append(dict(de=p['valor'], para=valor, data=hoje, motivo=motivo))
    p['valor'] = valor; p['desde'] = hoje
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def markdown(uso=None):
    """HIPOTESES.md: uma seção por eixo, tabela de premissas e histórico. uso = {nome: [builds]}."""
    d = {k: v for k, v in _dados().items() if not k.startswith('_')}
    out = ['# Bíblia de hipóteses (gerada de premissas/premissas.json — não editar à mão)', '',
           'Cada premissa é um "peso" do modelo. Mudar: `python -m dh premissa <nome> <valor> --motivo "..."`; '
           'depois `python -m dh completo \'builds/*.json\'` recalcula só quem usa.', '']
    for eixo in sorted({v.get('eixo', '-') for v in d.values()}):
        out += [f'## {eixo}', '', '| Premissa | Valor | Desde | Builds que usam | O que é |', '|---|---|---|---|---|']
        for n, v in sorted(d.items()):
            if v.get('eixo', '-') != eixo: continue
            u = len((uso or {}).get(n, [])); mig = '' if v.get('migrada', True) else ' *(ainda no código)*'
            out.append(f"| `{n}` | {v['valor']} | {v.get('desde', '')} | {u} | {v.get('descricao', '')}{mig} |")
        hist = [(n, h) for n, v in sorted(d.items()) if v.get('eixo', '-') == eixo for h in v.get('historico', [])]
        if hist:
            out += ['', '<details><summary>Histórico</summary>', '']
            out += [f"- `{n}`: " + ', '.join(f'{k} {x}' for k, x in h.items()) for n, h in hist]
            out += ['', '</details>']
        out.append('')
    return '\n'.join(out)
