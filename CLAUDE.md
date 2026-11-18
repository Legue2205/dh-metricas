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
- **Hipótese = premissa.** Todo número de julgamento vai para `premissas/premissas.json` (lido com `valor`/`grupo`/`P`),
  nunca constante solta no código. Mudar só com `dh premissa <nome> <valor> --motivo`, **nunca no meio de um lote**.
- **Builds agnósticas:** nada de nome de personagem em `dh/`. Mecânica nova entra como tipo/campo genérico no JSON.
- Avise o usuário em uma linha quando um passo for caro (ler fichas grandes, `dh completo` em tudo).

## Builds de referência em lote (RPGBot, D4, Treant Monk)
- **Fonte da verdade = página bruta** colada pelo usuário no Drive (Google Doc só com texto, `RPGBot/<pasta>/<tipo>-<slug>`,
  cabeçalho com URL, tipo de página, edição 2014 e data; o Claude cria o Doc com o cabeçalho de `prompts/cabecalho-rpgbot.md` e o usuário cola embaixo). Sem IA no meio. Pastas: `00-contexto`, `01-classes`, `02-subclasses`, `03-builds`
  (+ `03-builds/fichas` para as fichas que o Claude escreve), `04-magias`. Caminho: "Builds RPG/Biblioteca de builds .md/RPGBot"
  (ids no Drive: RPGBot `1lKVVcWgGsdgKL3SM4b0zCd1Jk9kvUabo`, 00 `176gRnD8hat1B7iZn-6TFgDO-MUs0I_Fz`,
  01 `1peNspj-DQ2g79p4JK9T1mDOsSVpa6VB9`, 02 `17c93G9-djeUvAlVOirWjksb-pzNi0ApK`, 03 `178DZsrFGY2JOpLLiBxX2Z9x80FXlO_wD`,
  fichas `1DCQHPsJa19HianGOuDongwNKD2Kxb9Ka`, 04 `1unV4p1NYnfpHskfQg82GkVFtwa58ZStx`). Busque com `parentId = '<id>'`.
- **A página bruta é lida uma vez.** Na ingestão o Claude escreve dois derivados: a ficha compacta
  (`03-builds/fichas/<slug>.md`, formato de `prompts/prompt-rpgbot.md`) e `progressoes/<id>.json`. Passadas seguintes
  usam só os derivados; volte ao bruto apenas para conferir algo que a calibração apontar.
- Números (acerto, CD, PV, CA) são calculados pelo Claude a partir das escolhas do guia (atributos, feats, nível),
  não copiados de resumo de outra IA.
- Texto do guia não entra no repo (público): só mecânica, descrição em palavras nossas e o link.
- Escreva `progressoes/<id>.json` (base no menor nível + patches cumulativos só com o que muda; modelo em
  `progressoes/exemplo-guerreiro.json`), com `"planos": {"padrao": "auto", "combate_unico": "auto"}` salvo se o guia
  orientar o orçamento. Cada linha-opção declara `"gasta"` por luta.
- Fluxo do lote: ler os brutos → fichas + `.prog` → `dh expandir` → `dh validar 'builds/*.json'` → commit. Não rode
  `dh completo` na conversa: o CI calcula. Gabarito da fonte em `calibracao/<fonte>.json`; `dh calibrar` depois do CI.
- Lote realista: ~5 páginas brutas por conversa (15–30k tokens cada); avise o usuário se passar disso.
