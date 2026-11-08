# Regras para o Claude neste repo

Objetivo: adicionar ou mudar uma build gastando poucos tokens e sem divergir dos motores.

- **Nunca reescreva um motor numa conversa.** Os números vêm de `python -m dh …`. Se faltar mecânica,
  adicione um tipo de fonte em `dh/controle/efeitos.py` (ou uma magia em `magias.json`) com um teste em `tests/`.
- **A ficha é lida uma vez.** Extraia o que importa para `builds/<id>.json` e trabalhe só com o JSON depois.
  Docs de personagem podem ter vários MB: leia só as seções de atributos, ataques, magias e features.
- **Não leia as planilhas para descobrir a estrutura**: o layout está no README e em `dh linhas`.
  Para conferir um valor, use `get_values` numa faixa estreita, nunca `get_spreadsheet` com grid data.
- Fluxo: copiar uma build parecida → `dh validar` → `dh rapido` → `dh completo` → `dh linhas` → colar.
- Rode `python -m pytest -q` antes de commitar qualquer mudança em `dh/`.
- Mudou um valor de premissa (peso de magia, perfil, topologia)? Diga na resposta quais ranks mudam e rode
  `dh completo --forcar` nas builds afetadas.
