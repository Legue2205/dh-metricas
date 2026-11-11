# Regras para o Claude neste repo

Objetivo: adicionar ou mudar uma build gastando poucos tokens e sem divergir dos motores.

- **Nunca reescreva um motor numa conversa.** Os números vêm de `python -m dh …`. Se faltar mecânica,
  adicione um tipo de fonte em `dh/controle/efeitos.py` (ou uma magia em `magias.json`) com um teste em `tests/`.
- **Fonte das builds:** a pasta do Drive "Builds RPG/Biblioteca de builds (md)", um `<id>.md` por build, no formato de
  `prompts/prompt-build.md` (seção 3.3). Leia o .md, não o Google Doc (os Docs têm imagens e são grandes).
  Mapeamento .md → JSON: Ficha → corpo/saves; Recursos do dia → recursos; Ataques → dano; Controle/Área/Suporte →
  eixos; Modos de jogo → linhas; Plano do dia → planos; Resumo e textos → descricao.
- **A ficha é lida uma vez.** Extraia o que importa para `builds/<id>.json` e trabalhe só com o JSON depois.
  Docs de personagem podem ter vários MB: leia só as seções de atributos, ataques, magias e features.
- **Não leia as planilhas para descobrir a estrutura**: o layout está no README e em `dh linhas`.
  Para conferir um valor, use `get_values` numa faixa estreita, nunca `get_spreadsheet` com grid data.
- Fluxo: copiar uma build parecida → `dh validar` → `dh rapido` → `dh completo` → `dh linhas` → colar.
- Rode `python -m pytest -q` antes de commitar qualquer mudança em `dh/`.
- Mudou um valor de premissa (peso de magia, perfil, topologia)? Diga na resposta quais ranks mudam e rode
  `dh completo --forcar` nas builds afetadas.
- **Uma linha = uma hipótese.** Não conte o mesmo recurso em dois eixos: declare `reacao` e `recursos.espacos`
  e respeite o que `dh validar` disser (ERRO de reação bloqueia; AVISO de espaços deve ser relatado ao usuário).
- **Builds agnósticas:** nada de nome de personagem em `dh/`. Mecânica nova entra como tipo/campo genérico no JSON.
- Avise o usuário em uma linha quando um passo for caro (ler fichas grandes, `dh completo` em tudo).
