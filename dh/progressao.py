"""Progressão: uma build em várias fatias de nível a partir de um arquivo só.

`progressoes/<id>.json`:
{
  "id": "rpgbot-devotion-paladin", "nome": "Paladino da Devoção (RPGBot)", "grupo": "RPGBot",
  "fonte": {"tipo": "rpgbot", "url": "https://…", "nota": "…"},
  "base":   { …campos de uma build (corpo, recursos, linhas, planos, descricao…), sem id/nivel… },
  "niveis": { "3": {patch}, "5": {patch}, "7": {patch} … }
}

Os patches são **cumulativos**: o nível 7 = base + patch 3 + patch 5 + patch 7 (só se escreve o que muda).
Regras do merge:
  - dicionário: merge recursivo; `null` apaga a chave;
  - lista comum: substitui inteira;
  - `linhas`: merge por `id` (id existente → merge recursivo; id novo → entra no fim; `{"id": x, "_remover": true}` tira);
  - `"planos": {"padrao": "auto", "combate_unico": "auto"}` (ou `"planos_auto": true`) gera o plano de cada fatia
    com `dh/plano_auto.py`; um plano escrito à mão no patch vale só a partir daquele nível;
  - `"_texto"` num patch de nível vai para `descricao.progressao` (o que muda naquele nível, curto).
Sem argumentos, `dh expandir` pula `progressoes/exemplo-*.json` (modelos).
Saída: `builds/<id>-<nível>.json`, com `"gerado_de"` apontando para o arquivo de progressão (não editar à mão).
"""
import copy
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / 'progressoes'
BUILDS = RAIZ / 'builds'


def mesclar(a, b, chave=None):
    """Merge de b sobre a (sem alterar os dois)."""
    if chave == 'linhas' and isinstance(a, list) and isinstance(b, list):
        out = [copy.deepcopy(x) for x in a]; pos = {x.get('id'): i for i, x in enumerate(out)}
        for x in b:
            i = pos.get(x.get('id'))
            if x.get('_remover'):
                if i is not None: out[i] = None
            elif i is None: out.append(copy.deepcopy(x)); pos[x.get('id')] = len(out) - 1
            else: out[i] = mesclar(out[i], x)
        return [x for x in out if x is not None]
    if isinstance(a, dict) and isinstance(b, dict):
        out = copy.deepcopy(a)
        for k, v in b.items():
            if v is None: out.pop(k, None)
            elif k in out: out[k] = mesclar(out[k], v, k)
            else: out[k] = copy.deepcopy(v)
        return out
    return copy.deepcopy(b)


# Rótulos de comparação (22/11, builds de chassi): passam da progressão para cada fatia; os motores não os leem.
ROTULOS = ('classe', 'subclasse', 'posicao', 'feat', 'variante')


def fatias(prog):
    """{nível: build completa} para cada nível declarado em "niveis"."""
    atual = copy.deepcopy(prog['base']); out = {}
    for nv in sorted(prog['niveis'], key=int):
        patch = dict(prog['niveis'][nv]); txt = patch.pop('_texto', None)
        atual = mesclar(atual, patch)
        b = copy.deepcopy(atual)
        b.update(id=f"{prog['id']}-{int(nv)}", nome=prog['nome'], grupo=prog.get('grupo', 'Referência'), nivel=int(nv))
        for k in ('fonte',) + ROTULOS:
            if k in prog: b[k] = prog[k]
        if txt: b.setdefault('descricao', {})['progressao'] = txt
        from .plano_auto import aplicar
        aplicar(b)
        out[int(nv)] = b
    return out


def expandir(arquivos=None, destino=BUILDS):
    """Escreve as fatias. Devolve a lista de arquivos escritos."""
    arqs = [Path(a) for a in arquivos] if arquivos else sorted(x for x in PASTA.glob('*.json') if not x.name.startswith('exemplo'))
    escritos = []
    for p in arqs:
        prog = json.loads(p.read_text(encoding='utf-8'))
        for nv, b in fatias(prog).items():
            b = {'gerado_de': str(p.relative_to(RAIZ)) if p.is_relative_to(RAIZ) else p.name, **b}
            alvo = Path(destino) / f"{b['id']}.json"
            novo = json.dumps(b, ensure_ascii=False, indent=1) + '\n'
            if not alvo.exists() or alvo.read_text(encoding='utf-8') != novo:
                alvo.write_text(novo, encoding='utf-8'); escritos.append(alvo)
    return escritos
