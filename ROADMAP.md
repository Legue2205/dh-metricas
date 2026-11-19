# ROADMAP e decisões — dh-metricas

> Para retomar em outra sessão: "vamos retomar o dh-metricas". Conecte o repo `Legue2205/dh-metricas`,
> leia este arquivo, o `CLAUDE.md` e o `README.md`. Tudo o que foi decidido está aqui; não dependa do chat.
> Atualize este arquivo ao fim de cada sessão (seção "Estado" e "Próximo passo").

## Objetivo

Adicionar uma build deve ser só: **discutir a build → gerar `builds/<id>.json` → commit**. O resto (validar,
rodar motores, guardar resultados, atualizar o painel) é automático, sem o Claude rodar código nem colar valores.

## Decisões tomadas

| # | Decisão | Data |
|---|---|---|
| 1 | Um repo único com todos os motores; números só vêm de `python -m dh` | 08/11 |
| 2 | Uma build = um JSON em `builds/`; nada de nome de personagem em `dh/` (motor agnóstico) | 08/11 |
| 3 | Moeda comum = nível equivalente + letra (F…S), por eixo. Eixos do card antigo (COND, FÔLEGO, MOB, alcance) retirados | 08/11 |
| 4 | Controle declarativo (`fontes`, `plano`) com biblioteca única `magias.json` | 08/11 |
| 5 | Uma linha = uma hipótese: reação e espaços de magia não contam duas vezes (`orcamento.py`). Reação duplicada = erro; espaços estourados = aviso "eixos não somam" | 10/11 |
| 6 | Shield/Uncanny Dodge são recursos finitos com decisão informada (vê o ataque/dano, pesa o resto do round). Counterspell conta em controle e em saves, não em blindagem | 10/11 |
| 7 | Padrão: 4 lutas por dia (2 prioritárias que gastam o dobro de uma comum), 2 por descanso curto, 4 rounds por luta | 10/11 |
| 7b | (substituída pelo plano do dia, abaixo) ~~Tags de orçamento automáticas por linha~~ (menor em que a linha cabe): `comum` (1/6 dos espaços do dia) < `prioritaria` (1/3) < `combate_unico` (dia inteiro) < `hypercharged_1.5` < `hypercharged_2.0` … (degraus de 0,5 dia). Substitui o aviso "eixos não somam" | 10/11 |
| 8 | **Armazenamento = o próprio Git** (`builds/` entrada, `resultados/` saída). Sem banco de dados por enquanto | 10/11 (confirmada) |
| 9 | **Automação = GitHub Actions**: a cada push roda testes + `dh completo` e commita `resultados/` e `PAINEL.md` | 10/11 (confirmada) |
| 10 | **Front-end = site estático** gerado dos `resultados/*.json` (Cloudflare Pages ou GitHub Pages). Sem back-end: os motores são Python/numpy com Monte Carlo, ruins para funções serverless da Vercel/Cloudflare | 10/11 (confirmada) |
| 11 | Google Sheets vira opcional (espelho/exportação), não fonte da verdade | 10/11 (confirmada) |

Itens 8–11 confirmados pelo usuário em 10/11. **Repo público → site no GitHub Pages.**

### Por que não app com back-end + banco agora
- Os dados são poucos arquivos JSON versionados: o Git já dá histórico, diff e backup.
- O cálculo leva ~1 min e precisa de numpy: cabe num job de CI gratuito, não numa função serverless.
- Site estático não tem servidor para manter nem custo.
- Se um dia for preciso editar builds por formulário: o formulário gera o JSON e abre um commit pela API do
  GitHub (ou os motores rodam no navegador com Pyodide). Só então pensar em banco (ex.: Cloudflare D1).

## Estado (10/11/2026)

Pronto e testado (37 testes): dano, defesa (com reações), saves (Resiliência/Vontade), controle (campo +
atenção + absoluto), área, suporte, orçamento de recursos, CLI (`validar`, `rapido`, `completo`, `linhas`,
`painel`), caches de régua. 16 builds migradas. Paridade com as planilhas descrita no README.

## Próximos passos (em ordem)

### Fase 1 — motor geral completo e flexível
1. ~~Invocações~~ **feito em 10/11**: `invocacoes` na linha alimenta controle de corpo, atenção e dano calculado. Texto original: Invocações/summons como cidadãos de primeira classe. Hoje os esqueletos do Amadeus aparecem em três
   lugares soltos (dano `medido`, fonte `esqueletos` do controle, `atencao.esqueletos`). Criar no JSON
   `"invocacoes": [{"nome", "quantidade", "pv", "ca", "ataque": {...}}]` na linha (hipótese de quantos tem) e
   fazer dano, controle de corpo e atenção lerem dali.
2. **Ação, ação bônus e concentração no orçamento** (hoje só reação e espaços).
3. **Dano calculado para todas as builds** (trocar `medido` por `ataques`); rotações com recursos.
4. **Ganchos para mecânicas exóticas**: `golpes_extras_a_0pv` (o "barrado" do Ravin) já existe na defesa;
   seguir o mesmo padrão (campo genérico no JSON) para o que aparecer.
5. ~~Avisos de espaços~~ → resolvido com as tags (7b).
6. Pendências de dados: saves de Jamal e Virgil (Caleb e Lucius já entraram); planos e suporte do Marcus; arquétipos e monstros.

### Fase 2 — automação (sem Claude no meio)
7. ~~Workflow do GitHub Actions~~: roda com sucesso a cada push (conferido em 10/11).
8. `dh site`: gera `site/index.html` estático (painel, página por build, comparação) a partir de `resultados/`.
9. Publicar no GitHub Pages (repo público), pelo próprio workflow.
10. Opcional: `dh exportar-sheets` no CI para manter as planilhas como espelho.

### Fase 3 — aplicação
11. Formulário no site para criar/editar build (gera JSON + commit pela API do GitHub).
12. Só se precisar: back-end/banco.


## Plano de orçamento do dia (decidido em 10/11)

Pedido do usuário: a decisão de como gastar os recursos é qualitativa e deve ser tomada **na discussão da
build**, escrita no JSON, e não por fração automática nem por agente no workflow.

1. **Tag = premissa diária**, poucas: `padrao` (4 combates: NP1, P1, descanso curto, NP2, P2),
   `combate_unico` (1 combate, todos os recursos) e `dia_longo` (a definir).
2. **Plano do dia no JSON**: para cada tag, a sequência de combates; cada combate diz, round a round, o que o
   personagem faz e com qual recurso ("R1 Faerie Fire 1º; R2–R4 espada"; "bárbaro: Fúria só nos prioritários").
   Também a postura (linha de frente ou não), que muda o controle de corpo/atenção daquele combate.
3. **Livro-caixa automático**: o validador desconta cada gasto do dia (espaços, pacto e ki voltam no descanso
   curto, Fúria por descanso longo, etc.). Gastar o que não tem = **erro**. O que sobra aparece como
   "sobra para utilidade". Gastar 100% é permitido (sem coeficiente de folga), mas fica visível que não há sobra.
4. **Cada combate é avaliado em todos os eixos**, com os motores atuais, a partir do que foi gasto nele.
5. **Resultado da tag padrão**: média do dia (ponderada, mais peso nos prioritários) **e** separados:
   média dos prioritários e média dos não prioritários, para ver os "picos" (ex.: Marcus com mais dano no NP e
   mais controle no P).
6. As tags automáticas `comum/prioritaria/hypercharged` saem; a comparação entre builds é sempre na mesma tag.

Etapas: (a) formato do plano + livro-caixa + agregação, reaproveitando os eixos por combate como hoje;
(b) modelo de ação round a round unificado, em que uma ação alimenta dano, controle, área e suporte ao mesmo tempo.

Decisões do usuário (10/11):
- Média do dia: **prioritário pesa 2, não prioritário pesa 1**.
- `dia_longo`: **8 combates, 2 descansos curtos** (entre o 3º e o 4º e entre o 6º e o 7º).
- Estourar o orçamento é **erro**, exceto em linhas com a tag explícita **`hypercharged`** (hipótese de acesso a
  mais recursos), que declaram quanto a mais têm.
- `dia_longo`, pesos: **1 1 2 · SR · 1 2 2 · SR · 2 4** (1 = não prioritário, 2 = moderado, 4 = boss fight).
- **Etapa (a) implementada em 10/11** (`dh/planos.py`, herança de linhas com `herda`, livro-caixa, média do dia
  e por categoria, `dh painel [tag]`). Kael e Tin Bin já têm plano (trivial). Falta a etapa (b).

## Modelo de anéis (decidido em 13/11) — substitui o plano do dia como fonte da nota

Motivo: a pré-seleção rígida de magias tirava do conjurador a escolha situacional (Lightning Bolt contra horda
alinhada, Hypnotic Pattern contra brutos de Sabedoria baixa, Web/Haste contra boss com resistência lendária).
A força de um conjurador é a caixa de ferramentas, não um dia fixo.

1. **Uma build = um conjunto de opções; cada opção é uma linha.** Magias (Ravin: sem espaço, Hypnotic Pattern,
   Haste em si, Haste no aliado, Lightning Bolt) e posturas (Caleb: agressiva, defensiva, utilitária) são a mesma
   coisa. Só entram linhas do jogo real da build (decididas na discussão), para o mínimo não despencar à toa. A
   estratégia da build (Sorlock de Hex, caster de controle/suporte, híbrido) aparece na escolha das linhas.
2. **Anel externo = máximo de cada eixo entre as linhas; anel interno = mínimo.** O externo não é alcançável
   inteiro ao mesmo tempo ("pico: um eixo por vez"); a distância entre anéis = dependência de recurso/flexibilidade
   (caster: interno baixo, externo alto; marcial: anéis quase iguais).
3. **Anel intermediário = linha "equilibrada"** = o plano de orçamento do dia (mantido): uso razoável/realista
   dos recursos definido na discussão. **É o ranking padrão da build**; mínimo e máximo são o contexto (teste de
   estresse e potencial). Desenhado como pontos com traçado suave entre os dois anéis. Confirmado em 13/11.
4. **Marca de custo por linha:** `gratuita` (postura, escolhida turno a turno, mistura cai entre os anéis) ou
   `gasta_recurso` (espaços etc.). Recursos dedicados (Second Wind) entram direto no eixo deles, em todas as linhas.
5. **Fôlego** (eixo de volta, generalizado): quantas lutas por dia a build sustenta nas linhas que gastam recurso.
   Um número da build inteira (o tanque é um só). O livro-caixa de `planos.py` passa a servir para isso e para um
   "dia de exemplo"/modus operandi; deixa de gerar a nota dos eixos.
6. **"Uma linha = uma hipótese" vale na escala da luta** (ação, concentração, reação), não mais do dia.
7. **Consistência dos eixos:** hoje área e controle medem pico por luta, mas suporte divide `usos_dia` pelas lutas
   (média). Suporte passa a medir o valor na luta em que é usado.
8. **Site:** radar com os dois anéis + intermediário; cada linha aparece por cima ao passar o dedo (para ver quais
   eixos trocam com quais).

## Fluxo rápido por build (13/11)

Pedido: adicionar uma build deve custar pouco esforço; o cerne é discutir a estratégia.
1. **Contexto:** party já está em `builds/*.json` (não precisa de .md). Build nova: um `.md` curto na pasta do
   Drive "Builds RPG/Biblioteca de builds .md" (~5 KB, barato de ler), gerado por `prompts/prompt-build.md`.
2. **Resumo de 4 linhas** (ideia, o que faz, recursos, estratégia proposta) — lido do JSON/.md.
3. **Discussão só da estratégia:** linhas-opção (máximos de cada eixo), mínimo realista, linha equilibrada.
4. Claude gera o JSON, roda `dh validar`/`rapido`, commita; o CI faz o resto.
Facilitadores planejados:
- `prompt-build.md`: trocar "Modos de jogo" + "Plano do dia" por "Linhas-opção (gratuita/gasta recurso)" +
  "Linha equilibrada", para a IA externa já trazer um rascunho da estratégia e a discussão virar revisão.
- `dh resumo <id>`: imprime o card de 4 linhas + recursos + opções candidatas a partir do JSON (sem LLM).

## Perguntas em aberto para o usuário
- Incluir ação/concentração no orçamento agora?

## Feito em 10/11 (noite)
- **Site estático** (`dh site` → `docs/index.html`), regenerado pelo workflow. Falta só ligar o GitHub Pages
  (Settings → Pages → Deploy from a branch → `main` / `/docs`): ação do usuário.
- **Orçamento:** ação bônus (declarada) e concentração (uma por linha; detecta magias de concentração do controle).
  Conflitos reais encontrados e resolvidos dividindo linhas: John (Hunter's Mark × Ensnaring Strike) e
  Solaris (Hex × Wall of Force).
- **Dano calculado** (em vez de `medido`) para John, Tin Bin, Abdul, Marcus e Amadeus (este com os esqueletos
  vindo de `invocacoes`); os valores antigos ficam em `conferencia` e são testados. Recursos "no acerto" por
  luta (smites) agora usam E[min(usos, acertos)]. Tin Bin subiu de 9,8 (B+) para 10,0 (A-) por 0,3 de DPR.

## Feito em 11/11
- **Front-end novo** (`dh/site.html`): abas por premissa + Legado, busca, filtros numéricos, ordenação, tema
  escuro/claro, ranks coloridos, radar de 6 atributos, cards por atributo com valores intermediários, comparação 1×1.
- **Decisão:** eixos do painel = Dano, Defesa Física (2/3 Defesa + 1/3 Resiliência), Defesa Mágica (2/3 Vontade +
  1/3 Resiliência), Controle, Área, Suporte. Sem saves cadastrados: Def. Física = Defesa, Def. Mágica sem nota.
- Motor: `controle.corpo` (T/S/P + perfil), `dano.nivel_bruta/precisa`, campo `descricao` nas builds (tamanho máximo).
  Descrições escritas para a party (7 builds); **NPCs ainda sem `descricao`**.

## Próximo passo
1. ~~**Modelo de anéis**~~ **feito em 15/11**: `dh/aneis.py` (mín/máx por eixo entre as linhas, equilibrado = plano
   `padrao`; eixo ativo ausente = 0, passivo ausente = ignorado; `"aneis": false` exclui linha antiga; `custo`
   declarado ou inferido). Site: faixa mín–máx, equilibrado pontilhado, botões para sobrepor cada linha, zoom
   automático da escala. CLI imprime `ANÉIS`. Falta: linhas-opção revisadas de cada build (linhas parciais antigas,
   como `so-sobreviver` do Kael sem `dano`, puxam o mínimo de dano para 0).
2. Suporte: trocar a diluição por dia pelo valor na luta em que é usado.
3. Motor de fôlego (a partir do livro-caixa de `planos.py`).
4. **Com o usuário:** linhas-opção + linha equilibrada de cada build (pedido típico: "vamos criar o plano do
   Marcus"), começando por Marcus, Amadeus, Abdul; posturas do Caleb. Antes: `dh resumo` e o prompt novo.
5. Gancho genérico de "bônus que escala durante a luta" (combo do Kael, carga do Ravin); ataques dos NPCs.
6. `dh linhas`/exportação para o Sheets com os eixos novos (opcional: o site já substitui).

## Feito em 15/11
- **Marcus: plano do dia padrão no motor** (linha equilibrada = anel intermediário): linhas `comum-escudo`,
  `comum-marcial`, `prioritaria`, `prioritaria-polymorph` e `planos.padrao`/`combate_unico`. Livro-caixa fecha
  com sobra de 1×3º (Healing Word); Inspiração entra como recurso `inspiracao` (4, volta no descanso curto).
  Homebrew da mesa: espadada de ação bônus depois de feitiço de 1º (adiantamento do Battle Magic).
- Motor: `"topos": [...]` numa fonte de controle (só vale nessas topologias) e no checador de concentração
  (concentrações em topologias disjuntas não conflitam). Testes novos.
- Pendente do Marcus: arcos mínimo e máximo (linhas-opção); suposição de que FF lançado de 2º ainda conta como
  "feitiço de 1º" para a espadada (confirmar com o usuário).

## Motor tático (15/11, noite)
`dh/tatico.py` + `python -m dh tatico builds/<id>.json [--w 1]`: programação dinâmica turno a turno para quem alterna
esconderijo e linha de frente (bloco `"tatico"` na build: ataques melee/arremesso/distância, deslocamento, sneak).
Estado: distância ao alvo, esconderijo, escondido, distância alvo→esconderijo (por topologia), aliado colado, round 1
com Assassinate. Ações: Melee/Thrower Lurker, Melee/Thrower Dasher, Frontline (Steady Aim / Hide e entra), Ranged
Lurker, Sniper, Reposicionar, Aproximar. Objetivo: dano − w × dano recebido. Políticas: ótima, só sombras, só frontline.
Primeiro uso: Tin Bin (Nick 2024 homebrew: 2 golpes na ação).
Premissas a confirmar com o usuário: exposição (escondido 5%, longe 15%, colado 30% do dano inimigo da régua, ×0,85
por Uncanny Dodge), distâncias iniciais e entre alvos por topologia, PV do alvo 60, aliado colado 20% no R1 e 70% depois.
Feito (15/11, 22h): PV perdido na luta entra no estado; custo convexo pelo orçamento ((pv + recuperação)/lutas):
w dentro (razão de piscinas), w × 3 acima, queda = 60. Três composições fixas (`terceiro_melee`, `segundo_frontliner`,
`sem_tanque`) definem a exposição. Decisão do usuário: o motor mostra um cardápio (política × composição) e o jogador
escolhe; não otimizar para cada party possível.
Próximo: (1) "deixa na mão": quanto dano o esconder-se empurra para a party (usar o motor de atenção/corpo, T/S/P);
(2) ligar as políticas às linhas da build para entrar nos anéis; (3) Action Surge depois (decisão do usuário).

## Corpo separado do Controle (15/11, 23h) — decisão do usuário
- **Controle** = só turnos negados (`nivel_campo`). **Corpo** = 7º eixo (`nivel_atencao`) + perfil T/S/P estampado ao
  lado do nome, junto com a **posição** na party de referência (Tanque, 2º marcial, Atirador/backliner, Conjurador).
  Motores intactos (0 diferença nos números); muda o que planos, anéis e site mostram. Versão 0.5.0.
- Atenção: `front` aceita fração e `oculto` (fração dos turnos inimigos em que não pode ser alvo).
- Linha com `"tatico": {"politica", "composicao"}`: o motor tático gera o dano (9 CAs) e a ficha de atenção
  (colado → front, escondido → oculto, composição → posição: 3º melee = atirador, 2º frontliner = striker, sem tanque = tank).
- Tin Bin: linhas transicao-3o-melee (equilibrada), transicao-2o-frontliner, sombras, frontline; Action Surge fora.
- Em aberto: parties de 5–6 (3º melee como posição própria); a exposição do motor tático vem de presets por composição,
  não do motor de atenção (possível iteração: calibrar os presets pela atenção); nome melhor para "controle de corpo".

## 16/11 (madrugada) — régua de dia, planos da party
- **Controle na régua de dia** (aprovado): todo número de Controle mostrado = `controle.total.nivel_dia(pico)`, o nível L
  cujo conjurador de referência, gastando um espaço de controle por luta (maiores nas prioritárias, pesos 2-2-1-1),
  rende esse pico médio. Plano: converte a média dos picos do dia. O pico por luta segue no card (régua antiga).
- PV real no painel (`corpo.pv_real`): Ravin 31, Kael 59, Amadeus 44 (motores: 48,5 = 44 + metade do Líder Inspirador).
- Abdul: todos os espaços em smite (1/2.../3/2 por luta), Lay on Hands 35 no livro-caixa; linhas herdam a principal.
- Amadeus: 7 esqueletos (4º no início + 3º de taxa no meio do dia), Haste + Fireball, Greater Invisibility (4º do Arcane
  Recovery), 2 Webs, Mage Armor + 3 Shields. Conflito avisado: 4 Shields não cabem com Mage Armor.
- Ravin: 4×3º, 2 por prioritária (Haste + LB; Counterspell + HP), Bladesong 3/dia (uma comum sem, com Mage Armor; CA sem
  Bladesong suposta 15,85), barrado 2/dia. Dano ainda medido da planilha; Counterspell e Vortex Warp fora das contas.
- Pendente: suporte do Marcus (Healing Word "levantar", resgate de save para Inspiração/Countercharm, Song of Rest);
  motor de vida do Kael (adiado); John (fica na comparação) precisa de plano; dano do Ravin por motor (precisa da ficha).
- **Controle sem fontes de corpo** (16/11, 3h): `ameaca`, `sentinela`, `parada_oa` e `esqueletos` desviam ataques para um
  corpo que aguenta — isso é o eixo Corpo (atenção). Antes entravam também no Controle (contagem dupla). Novo
  `nivel_controle` (campo sem essas fontes) alimenta o eixo Controle; `nivel_campo` antigo fica no card. Abdul:
  Conquering Presence só nas prioritárias (Channel Divinity 1/descanso curto). Controle do dia: Abdul 4,9 → 2,5,
  Amadeus 2,9 → 2,3, Kael 4,2 → 3,9, Tin Bin e Lucius → 0. A revisar: hipóteses do Stunning Strike do Kael.
- **Suporte: 3 modelos novos** (16/11, tarde): `dado_multiuso` (Bardic Inspiration: mistura de usos — dano certo, virar
  erro em acerto, +CA, save de meio dano, save crítico, Counterspell; o jogador gasta perto do limite: chance ×2),
  `resgate_condicao` (Countercharm 2024: p_evento × reroll com vantagem × 1,5 turno do aliado), `levantar` (Healing Word num
  caído: PV + 1 turno do aliado). Song of Rest = `cura` 14 PV/dia. Marcus: suporte do dia C 4,9 → B 7,2. Iniciativa fora.
- 16/11 (tarde): Lucius → NPC. Ravin: CA 19,85 com Bladesong (14 + 5 + 0,85 da carga da espada), 21,85 com Haste, 14,85 sem. (Correção: o 20,85
  antigo era Bladesong 20 + carga, não Shield diluído — não havia contagem dupla.) John: plano com comum (Steady Aim),
  prioritária de dano (Hunter's Mark, 1 troca) e de controle (3 Ensnaring Strikes), Cure Wounds 2×2º, Pass without Trace.
  Suporte: modelo `desvantagem_contra` (Greater Invisibility defensivo: 40% dos acertos contra o aliado da frente).

## Plano de calibração (decidido em 16/11, noite)
Biblioteca .md completa da party no Drive ("Biblioteca de builds .md": abdul, amadeus, john, kael, marcus, ravin,
tinbin; o doc mestre de 01/11 vira histórico). Atributos confirmados em 16/11 (Tin Bin rolado, a confirmar).
**MVP em 3 passos:**
1. **Consistência de cada régua:** dentro de um eixo, quem faz mais tem nota maior (o usuário acha que já está).
2. **Calibração grossa entre réguas com a party de referência** (2 anos de jogo com essas builds): comparar os
   números com a percepção da mesa eixo a eixo, investigar o que falta (ex.: suporte do Marcus baixo → faltavam os
   Healing Words) e acertar o viés entre eixos (ex.: suporte 7 não pode ser mais fácil que controle 7 ou dano 7).
3. **Ajustes finais e generalização:** réguas agnósticas, valendo para builds novas. Fim do MVP.
**Pós-MVP — fine tuning com fontes externas** (cada build com a tag da fonte):
- RPGBot (~50 builds de várias classes, com os rankings dele): fonte principal de comparação.
- 2ª opinião: D4 / D&D Deep Dive — builds desequilibradas, burst; esperar pico num eixo e o resto baixo.
- 3ª opinião: Treant Monk — valoriza defesa, sustentação, agir no 1º turno e controle; builds sem build-up.
**Motores pendentes:** Ravin (carga da espada: quando gastar, manter fora de fase para +1 CA no turno inimigo,
Booming Blade para recarregar quando o 1º golpe erra, quando entrar no barrado e se gasta carga); Kael (vida:
custos em PV, cura por acerto conforme CA e vantagem, limiar, Blood Dice no meio x depois da luta, moeda).

## 18/11 — radar mais limpo + diagnóstico de área + o que falta para o fine tuning
- **Radar:** nova ordem dos eixos (horário a partir do topo): Dano · Def. Física · Def. Mágica · Área · Controle ·
  Suporte · Corpo. Físico em cima, arcano embaixo, Def. Mágica de transição; eixos que andam juntos ficam vizinhos
  (menos "estrelas"). Faixa mín–máx sem os dois contornos tracejados. Linhas-opção: até 4, cada uma com cor própria
  e legenda, desenhadas **por cima** da principal (que recua para um contorno fraco). Linhas NP/P/boss escondidas
  atrás do botão "separar por tipo de combate".
- **Área Marcus (2,8) × Amadeus (2,7) no dia padrão:** por luta a Fireball vale 8,1 (B+) e o Shatter nv3 4,2 (C) —
  a Fireball pega 4 alvos e o Shatter 2. A diferença é só frequência: Amadeus solta 1 Fireball no dia (1 prioritária,
  peso 2 de 6 → 8,1 × 2/6), Marcus solta Shatter nas 2 prioritárias (4,2 × 4/6). No anel externo Amadeus segue 8,1 × 4,5.
  Em aberto: média do dia é média de *níveis* com zeros; avaliar converter pela régua de dia como no Controle.
- **Gaps antes do fine tuning com o RPGBot** (ver "Plano de calibração"):
  1. **Plano automático/heurístico** para builds externas (o plano hoje é escrito na discussão; 50 builds não dá).
     Proposta: `dh plano-auto` gera linhas-opção padrão a partir de recursos + magias (maior espaço por eixo, sem
     recurso, equilibrada pelos pesos 2-2-1-1) e marca a build como `plano: auto`.
  2. **Importador**: prompt/rotina RPGBot → `.md` → JSON num nível fixo (5, 8, 11), com `fonte: rpgbot` e o link.
  3. **Gabarito de calibração** (`calibracao/esperado.json`): o que a fonte diz de cada build por eixo (alto/médio/
     baixo, ou ordem entre builds), e `dh calibrar` que mede concordância (correlação de postos, violações listadas).
     Sem isso o fine tuning vira impressão visual.
  4. **Cobertura de mecânicas**: aviso por build de features ignoradas pelos motores (Rage, Sneak Attack, Divine Smite,
     Wild Shape, Spiritual Weapon…), para separar "métrica errada" de "mecânica não modelada".
  5. **Dano calculado para todas** (sem `medido`) e rotações com recursos — builds externas não têm planilha.
  6. Site: filtro por `fonte` e grupo "Referência externa" separado da party.
  7. MVP passos 1–3 ainda abertos (consistência por régua, calibração com a party, generalização).

## 18/11 (tarde) — gabarito pronto; pipeline do RPGBot decidido
- Usuário: Amadeus usa mesmo ~1 Fireball por dia → área do dia padrão está certa, sem mudança.
- **Gabarito** (`dh/calibrar.py`, `python -m dh calibrar [arquivos]`, testes em `tests/test_calibrar.py`):
  `calibracao/<nome>.json` com, por eixo, `ordem` (do mais forte ao mais fraco, sublista = empate) e/ou `faixa`
  (letra mín–máx por build); `visao` = padrao | combate_unico | dia_longo | externo | interno. Saída: tau de Kendall
  por eixo, inversões com os números, faixas violadas; diferenças < `tolerancia` (0,5 nível) = empate técnico.
  `calibracao/party-dh-7.json` criado vazio: **falta o usuário ditar a ordem da mesa por eixo**.
- **Fatias de nível do RPGBot:** 3, 5, 7, 9, 11 (13 opcional; tirar o 3 se pesar).
- **Pipeline decidido (a implementar):**
  1. `.md` por build no Drive, **compacto e com a progressão inteira** (um só .md cobre 3–11: atributos, feats, magias
     e features novas por fatia, rotação, o que o guia diz do orçamento). Texto do guia fica no Drive, não no repo
     público; o JSON leva só mecânica, descrição parafraseada e o link.
  2. **Progressão:** `builds/rpgbot/<id>.prog.json` = base + patches por nível (deep-merge); `dh expandir` gera
     `<id>-<nv>.json`. Hipóteses (linhas) se reaproveitam; cada nível só soma o que muda.
  3. **`dh plano-auto`:** monta o plano `padrao` a partir das linhas-opção e dos recursos (maiores gastos nas
     prioritárias, livro-caixa fechando), grava `"auto": true` e um texto explicando as escolhas. Guia do RPGBot
     com orçamento → usa o do guia.
  4. **Lote:** 5–10 builds por prompt: ler os .md → escrever os .prog.json → `dh expandir` → `dh validar` → commit;
     o CI calcula. Meta: o Claude só lê e escreve JSON, sem rodar motor na conversa.
- **Capacidade:** hoje ~17 KB de resultado por build-nível; 250 build-níveis ≈ 5 MB no Git (folgado; limites do GitHub
  são 100 MB por arquivo e ~1 GB recomendado por repo). CPU ~10–15 s por build-nível → ~1 h no CI se recalcular
  tudo (Actions grátis em repo público, limite 6 h por job); o cache recalcula só o que mudou. Gargalo real: o site
  embute tudo num HTML só → separar em índice leve + um JSON por build carregado sob demanda. Planilha não é necessária.
- **Dano:** o motor existe (`ataques`/`por_turno`/`por_luta`, fórmula fechada). `medido` (vindo da planilha) sobra em
  Ravin (3 linhas), Kael e uma linha de John, Tin Bin e Amadeus, mais NPCs. Builds do RPGBot entram 100% calculadas;
  faltam ganchos genéricos: ataque poderoso (GWM/Sharpshooter −5/+10 decidido por CA), Sneak Attack 1×/turno com
  chance de vantagem, Rage, ataque bônus (PAM/CBE), escala de truque por nível.
- **Ordem até o fim do MVP:** (a) usuário dita a ordem da mesa → `dh calibrar` → investigar inversões;
  (b) tirar `medido` do Ravin e do Kael (motores da carga e da vida) e ganchos de dano acima;
  (c) suporte no valor da luta; (d) generalização. Depois: expandir, plano-auto, site leve, lote piloto de 3 builds.

## 18/11 (noite) — gabarito da mesa, calibração, generalização para o lote
- **Gabarito da mesa** em `calibracao/party-dh-7.json` (ordens por eixo + notas do usuário; Def. Mágica sem opinião).
  Primeira rodada (tau médio 0,66 → 0,8 após o Kael): Dano 1,00 · Suporte 1,00 · Corpo 1,00 · Controle 0,89 ·
  Def. Física 0,62 · Área 0,00.
- **Kael:** linha `sem-stunning` (como a mesa joga hoje) vira o plano padrão; Stunning Strike fica como linha-opção
  (anel externo). Controle do dia 3,9 → 0. O vendaval (redução de velocidade) não é modelado.
- **Inversões que sobram** (para investigar; Ravin e Kael ficam para os motores próprios):
  1. Def. Física: Ravin 12,1 > Abdul 9,2 e Tin Bin 6,2 < Kael 7,6. Causas: "barrado" (3 golpes a 0 PV) dá ao Ravin
     durabilidade 10,6 com 31 PV; Def. Física = 2/3 Defesa + 1/3 Resiliência e a Resiliência do Ravin é S (16,4);
     PV efetivo do Kael (79) inclui autocura. Questão geral: o peso da Resiliência na Def. Física.
  2. Área: Ravin 5,6 > Amadeus 2,7 no dia — Thunderclap com espadada em toda luta comum (cleave_save 1–3 alvos × 4
     rounds) rende 4,1, igual a um Shatter nv3. **Perguntar:** o Ravin solta Thunderclap todo round nas comuns?
  3. Controle: John 0,8 parece baixo (mesa: parecido com o Abdul, 2,5); Amadeus 2,3 < Ravin 2,8 (dentro do ruído).
  4. Pedido em aberto do usuário: o AO do Sentinel que zera a velocidade conta como controle (negação de movimento),
     além do corpo? Hoje `parada_oa`/`sentinela` só entram no Corpo (decisão de 16/11). Decidir antes do lote.
- **Generalização feita:**
  - `dh/progressao.py` + `dh expandir`: `progressoes/<id>.json` (base + patches cumulativos por nível; linhas por id;
    `null` apaga; `_remover`) → `builds/<id>-<nv>.json`. Modelo: `progressoes/exemplo-guerreiro.json` (pulado por padrão).
  - `dh/plano_auto.py` + `dh plano-auto`: plano `padrao`/`combate_unico` automático (maior gasto do dia que cabe no
    livro-caixa, o pesado nas prioritárias; desempates por marca `"plano": "prioritaria"|"comum"`, sobra, linhas
    completas, simplicidade) com descrição explicando. Linha pode declarar `"gasta"` (por luta).
  - Dano: `com_save` (alvo único com save: Toll the Dead, Sacred Flame…), save do alvo por CA a partir das medianas do MM.
    Já existiam: `poder` (GWM/SS por CA), `por_turno` (Sneak Attack), `por_luta` (smites), vantagem, Elven Accuracy.
  - `prompts/prompt-rpgbot.md`: .md compacto com progressão 3–11 e linhas-opção com gasto por luta.
  - CI: `dh expandir` antes de validar; `progressoes/**` dispara o workflow. CLAUDE.md: fluxo do lote.
- **Antes do lote piloto (3 builds):** (a) decidir o item 4 acima; (b) site leve (índice + JSON por build sob demanda)
  quando passar de ~40 builds; (c) gabarito do RPGBot (`calibracao/rpgbot.json`) escrito a partir da análise de meta
  que o usuário vai colar; (d) faixas de dano nos patches de truque (escala por nível) conferidas no piloto.

## 18/11 (noite 2) — premissas como pesos do modelo; regra do lote congelado
**Decisões do usuário:**
- Suporte medido na luta em que é usado (como área e controle). Feito: `usos_dia` em combate conta inteiro na luta
  da linha; `"quando": "entre_lutas"` mantém a diluição (Song of Rest, Inspiring Leader, cura fora de combate). Aviso do
  validador se o plano usar a fonte em mais lutas do que ela tem. Dados: Song of Rest (Marcus), Lay on Hands nos
  aliados (Abdul), Inspiring Leader e Cure Wounds (Amadeus) = entre lutas; a Máscara (Crusader's Mantle, 1/dia) do
  Amadeus ficou só na linha haste-fireball.
- Sentinel/parada por AO: taunt e diluição ficam no Corpo; a negação de movimento entra no Controle com **peso 0,5**.
- **Regra de ouro do lote: a régua não muda no meio de uma passada.** Nenhuma premissa muda enquanto um lote de
  builds de referência está sendo importado; mudanças só entre passadas, registradas e com recálculo de tudo.
- **Fine tuning como treino:** passada 1 (todas as builds com as premissas congeladas) → comparar com RPGBot (o que ele
  diz de cada build + meta, num .md à parte) → achar padrões de erro → mudar premissas (com motivo) → recalcular →
  medir de novo. Cada passada fica registrada.

**Infraestrutura feita:**
- `premissas/premissas.json` + `dh/premissas.py`: premissa nomeada (valor, eixo, descrição, histórico). Motor lê com
  `P(nome)`; build usa `{"$p": "nome"}` em qualquer valor. `resultados/<id>.json` guarda as premissas usadas; mudou o
  valor → só essas builds perdem o cache e `dh completo` recalcula (código, não tokens).
- `dh premissa <nome> <valor> --motivo "…"` (grava histórico, lista afetadas, reescreve `HIPOTESES.md`);
  `dh premissas [--md]` lista com quantas builds usam. `HIPOTESES.md` = a bíblia, gerada.
- `dh calibrar --registrar "<rótulo>"` grava a rodada em `calibracao/historico.jsonl` (tau por eixo + snapshot das
  premissas) — o log de treino.
- `dh comparar [eixos] [--visao] [--grupo]`: builds × níveis por eixo (curva da progressão), texto ou `--json`.
- VERSAO 0.8.0 (suporte e controle mudaram de semântica): tudo recalculado.

**Próximo (migração das premissas):** a maioria das hipóteses ainda é constante no código (`suporte.H`,
`campo.H`, `area` alvos/rounds, `tatico` exposições, pesos 2-1 dos planos, perfis/topologias). Migrar por eixo para
`premissas.json` com `P()`, começando pelas que o fine tuning mais deve mexer: alvos por forma de área e fração do
round 2+; `campo.H` (taunt, disengage); `suporte.H` (ACERTO, ATIVO, EF_CURA, ESCOLHA); pesos do dia; exposição do
tático. Critério de pronto do MVP: nenhuma hipótese qualitativa fora de `premissas.json`.

## 18/11 (noite 3) — migração das premissas
- Sentinel e parada por AO: **0,25** no Controle (decisão do usuário; vale para todo personagem com Sentinel).
  Abdul: controle 4,1 → 2,9 (empata com o Marcus). Rodada "0b" gravada no histórico de calibração (tau médio 0,73).
- **Migradas para `premissas/premissas.json` (58 premissas):** mundo de referência (rounds por luta, perfis de
  inimigos, topologias, peso dos saves fortes/fracos, chefe, mistura de encontros), composição das notas
  (peso da Resiliência na Def. Física/Mágica), crítico inimigo, controle (campo, atenção, padrões, peso do corpo no
  controle), área (fator do round 2+, alvos de referência, horda, cenários), suporte (16 + mix + padrões),
  dias de aventura, tático (padrão e composições).
- **Refatoração neutra verificada:** com o Sentinel em 0,5, as 119 notas do painel saíram idênticas antes e depois;
  teste `test_migracao_reproduz_constantes_antigas` guarda isso.
- Registro por eixo: cada resultado guarda as premissas dos prefixos que seus eixos leem (determinístico); caches de
  régua (controle, área, saves) incluem o hash das premissas que os afetam.
- `HIPOTESES.md` agora lista também o que **não** é premissa (tabelas do MM/DMG, réguas, parâmetros de simulação) e
  as **pendentes**: repertório de magias inimigas dos saves (a maior), modelo da horda/chefe na defesa, funções de área
  com nome de personagem (remover), `tatico.padrao.rounds` duplicado.
- Critério de pronto do MVP: zerar a lista de pendentes; depois, lote piloto de 3 builds.

## 18/11 (noite 4) — pendências da Bíblia zeradas
- **Saves:** o repertório já existia no motor (24 magias mentais, 25 físicas, 2+2 truques, com efeito e peso); o que
  faltava era tirá-lo do código. Agora são premissas `saves.repertorio_mental/fisico`, `saves.truques_*`,
  `saves.peso.*` (Slow, Vicious Mockery) e `saves.conjurador_inimigo.mod_por_nivel`.
- **Defesa:** horda (dano por golpe 4 + CR/2, 3–10 atacantes, acerto 3 + CR/3) e chefe (2/3/4 ataques até CR 4/16/30,
  +3 de acerto, arma mágica a partir do CR 10) viraram premissas `defesa.horda.*` / `defesa.chefe.*`.
- **Área:** removidas as funções legadas com nome de personagem (carga, Wall of Fire, Horde Breaker, Thunderclap);
  as builds usam só os tipos genéricos. Chave de topologia `alc_miau` → `alc_corpo_a_corpo_atras`.
- **Tático:** rounds vêm de `base.rounds_por_luta`.
- Refatoração neutra de novo: 119 notas idênticas; caches antigos apagados. **72 premissas; lista de pendentes vazia.**
- **Critério de pronto do MVP atingido** no que depende de código. Próximo: lote piloto de 3 builds do RPGBot
  (precisa dos .md gerados com `prompts/prompt-rpgbot.md`).

## 18/11 (noite 5) — ingestão do RPGBot decidida
- **Formato:** página bruta colada no Drive (sem IA intermediária) é a fonte da verdade; o Claude lê uma vez e gera a
  ficha compacta + `progressoes/<id>.json`. Motivo: no nosso desenho a build é lida só uma vez (as passadas de fine
  tuning recalculam em código, sem tokens), então pagar a fidelidade uma vez compensa; e números calculados por outra
  IA são o ponto mais frágil. `prompts/prompt-rpgbot.md` vira o formato da ficha que o Claude escreve.
- **Ordem:** (0) contexto: Fundamental Math of Character Optimization, guia de DPR, guia geral de meta (com o FAQ) →
  comparar nossas réguas (DPR, CA, PV, CD) com os alvos dele e montar o esqueleto de `calibracao/rpgbot.json`;
  (1) guias de subclasses por classe (as notas por subclasse = gabarito); (2) piloto: 3 builds de guias de subclasse
  (marcial, half-caster, full caster); (3) lotes de ~5. Guias de magias/Wild Shape/invocação só quando uma build precisar.
- Cuidado: o RPGBot tem versões 2014 e 2024 das páginas; usar só 2014.

## 19/11 — protocolo da passada 1 (cega)
- Decisão do usuário: **não ajustar nada ao RPGBot antes de medir.** Passada 1 = importar as builds dele com as
  premissas atuais congeladas, gerar nossas notas, e só então comparar com o que ele diz. Divergências sistemáticas →
  padrões de erro nossos *ou* a "opinião" dele (o que ele valoriza: controle, defesa…). RPGBot não é fonte da verdade.
- **Cegueira:** as páginas de `02-subclasses` (notas dele por subclasse) são guardadas mas **não lidas** até a nossa
  passada da classe terminar. Na ingestão das builds, extrair só mecânica e plano; opiniões do guia ficam no bruto.
- Notas do RPGBot: 4 níveis por cor (vermelho = muito situacional, laranja = situacional, verde = bom, azul =
  excelente), o mesmo sistema para features e subclasses. Cores somem no texto puro; colar a página de subclasses com
  formatação (Ctrl+V) para tentar preservá-las; senão, inferir a nota pela justificativa (marcar como inferida).
- Gabarito `calibracao/rpgbot.json` sai das notas de subclasse destiladas (nota + resumo da justificativa).
- **Ordem: uma classe inteira por vez.** Piloto: Fighter (motor marcial mais maduro, subclasses mecanicamente
  diferentes). Depois Wizard (testa área, controle e Def. Mágica).

## 19/11 — passada 1, lote 1 (Fighter: Champion, Battle Master, Eldritch Knight, Arcane Archer, Cavalier)
- 5 progressões (`progressoes/rpgbot-fighter-*.json`) → 25 fatias (3/5/7/9/11), plano automático em todas.
- Convenções escritas em `calibracao/convencoes-passada1.md` (ler antes do lote 2).
- Novo: `"dpr": "auto"` na atenção (DPR da própria linha na CA da premissa `controle.atencao.ca_dpr_auto` = 16).
- Lote 2: Samurai, Echo Knight, Psi Warrior, Rune Knight, Purple Dragon Knight. Depois: `subclasses-fighter`
  (notas, ler só então) → `calibracao/rpgbot-fighter.json` → `dh calibrar`.

## 19/11 — passada 1, lote 2 (Fighter: Samurai, Echo Knight, Psi Warrior, Rune Knight, Purple Dragon Knight)
- 5 progressões → 25 fatias; com o lote 1, o Fighter inteiro do RPGBot está no repo (10 subclasses, 50 fatias).
- Casos novos registrados em `calibracao/convencoes-passada1.md` (multiclasse por nível de personagem, recursos de
  ativação por luta em linhas próprias, Sentinel, Reckless, agarrão). Nenhuma premissa mudou.
- Próximo: depois do CI, ler `02-subclasses/subclasses-fighter` (notas do RPGBot) → `calibracao/rpgbot-fighter.json`
  → `dh calibrar` / `dh comparar`. Spell list do Eldritch Knight ainda não colada (não faz falta para a passada 1).

## 19/11 — passada 1 do Fighter: primeira comparação com o RPGBot
- Gabarito `calibracao/rpgbot-fighter.json`: notas por subclasse INFERIDAS do texto (a página não traz as cores em
  texto); falta o usuário conferir contra as cores.
- tau (nota RPGBot × média de dano, Def. Física, Def. Mágica e Controle) = 0,32 no nível 7 e 0,34 no 11: concordância
  fraca, mas positiva. Extremos batem (Champion/PDK embaixo; Echo/Cavalier/Rune em cima).
- Padrões de erro candidatos (decidir antes da passada 2, sem mexer no meio):
  1. Controle cego para efeitos marciais (manobras, Unwavering Mark, runas, flechas, Telekinetic Thrust): 7 de 10
     subclasses com controle 0. Maior fonte de divergência (Battle Master, Cavalier).
  2. Sentinel sozinho vale quase nada no controle (Echo 0,4 até o Ancestral; Cavalier 0 até o Hold the Line).
  3. Eldritch Knight: guia diz "muito durável", nós o pomos no meio da Def. Física e no fim da Def. Mágica.
  4. Arcane Archer acima do esperado: Curving Shot foi modelado funcionando, mas RAW exige flecha mágica.
  5. Samurai lidera a média no 11 por Def. Mágica (4 saves proficientes); o guia não destaca isso.

## 19/11 — passada 2 do Fighter
- Usuário conferiu as cores: só o Samurai muda (azul). Gabarito marcado como conferido.
- Decisões: (1) tipo genérico `condicao_no_acerto` + 8 efeitos `cond_*` na biblioteca, aplicados a Battle Master
  (Menacing), Cavalier (Unwavering Mark como marca), Arcane Archer (Shadow Arrow), Rune Knight (Fire e Stone Rune),
  Psi Warrior (Telekinetic Thrust), PDK (Form of Dread + linha "medo" com Dragon Fear); (2) Curving Shot vira Área.
- Padrões 2 (Sentinel fraco), 3 (EK durável) e 5 (Samurai Def. Mágica) seguem abertos.
- Resultado da passada 2 (CI 19/11): tau (nota RPGBot × média de dano, Def. F, Def. M, controle) 0,32 → 0,42 no
  nível 7 e 0,34 → 0,51 no 11. Controle agora: Cavalier 4,9/6,2, Rune Knight 6,4/6,6, PDK 2,3/2,8, BM 2,2.
- Site: caixa "Mostrar RPGBot" (desligada por padrão) e seletor de nível da fatia; o nome de cada entrada leva "nv N".

## 19/11 — Ancestral × Unwavering Mark; Wizard preparado
- Usuário: Ancestral Protectors é mais forte (aliados ganham resistência ao dano do marcado). `ancestral_protectors`
  ganha `"resistencia"` (padrão true); sem ela (Unwavering Mark do Cavalier) vale a premissa
  `controle.marca.fator_sem_resistencia` = 0,5. Muda só o controle do Cavalier (cai).
- Docs criados no Drive para o Wizard (classe, subclasses, 13 builds: Abjuration, Bladesinging, Chronurgy,
  Conjuration, Divination, Enchantment, Evocation, Graviturgy, Illusion, Necromancy, Order of Scribes, Transmutation,
  War Magic) e para as listas de magias (`04-magias/magias-wizard`, `magias-eldritch-knight`).
- Próximo: ingestão do Wizard inteiro numa passada (premissas congeladas), depois gabarito e comparação.

## 19/11 — passada 1 do Wizard (13 subclasses, 65 fatias)
- Gerador único para conjuradores (convenções em `calibracao/convencoes-passada1.md`, seção Conjuradores).
- Biblioteca: +5 efeitos (phantasmal_force, earthen_grasp, phantasmal_killer, cond_hipnotizado, cond_estase).
- Próximo: CI → ler `subclasses-wizard` (notas) → `calibracao/rpgbot-wizard.json` → comparação.

## 19/11 — Wizard: primeira comparação (passada 1)
- Gabarito `calibracao/rpgbot-wizard.json` (notas inferidas; usuário confere as cores).
- tau (nota × média de dano, Def. F, Def. M, controle, área): −0,14 no 7 e 0,12 no 11. Sem concordância.
- Padrões candidatos:
  1. Medimos a BUILD; o RPGBot nota a SUBCLASSE. No Wizard o grosso do poder é da lista de magias comum, e as
     escolhas do guia (dip de Artificer, Polymorph, Fireball) pesam mais que a subclasse (Transmutation, vermelho, no meio).
  2. Recursos de manipulação de dados fora do modelo (Portent, Chronal Shift, Silvery Barbs, iniciativa): Divination
     (azul) cai para o fim.
  3. Área depende do plano automático: o Evoker fica com área 0 no 11 porque o plano preferiu as linhas de controle.
     Comparar área pelo anel externo (melhor linha), não pelo plano?
  4. Dano de magias de nível (Fireball, Chain Lightning) só entra na Área; o dano de alvo único dos magos é só truque.
- Correções no caminho: divisão por zero com invocação de PV 0; Def. Mágica ausente (linha principal sem `saves`).

## 19/11 (madrugada) — passada 2: área v2, forçar falha, builds puras
- Gabarito do Wizard conferido: Scribes verde, Bladesinging laranja; o resto como inferido.
- Área v2 (`dh/horda.py`): combate contra horda com a party de referência, até 50% da vida, 5 rounds no máximo.
  Premissas `area.horda2.*`. Muda a Área de TODAS as builds (party incluída) e agora marciais também têm Área.
- Plano: Área = pico da build. `forcar_falha` (Portent, Chronal Shift). Builds `-puro` (5).

## 19/11 noite — tarefa 1
- **Site dividido.** `docs/index.html` = modelo + índice da tabela (id, nome, grupo, nível, build, rótulo, abas, PV,
  CA, DPR em CA 15, notas dos eixos, perfil de corpo); `docs/dados/<id>.json` = o resto (linhas, anéis, descrição;
  fonte, plano e médias por categoria de cada entrada). O front-end busca o JSON com `fetch` ao abrir o detalhe ou
  escolher "Comparar com…" (cache em memória, "carregando…", URL com `?v=<versão>` para não misturar versões).
  Tabela: 150 linhas por vez + "mostrar mais".
  - Tamanhos: index.html **2.440.894 → 424.102 bytes** (gzip 226 KB → 45 KB); `docs/dados/` 157 arquivos,
    1.821.530 bytes no total (maior: marcus-7, 64 KB).
  - Teste no Chromium (Playwright): zero erros de JS; abas, busca, filtros, ordenação, "Mostrar RPGBot", seletor
    de nível, detalhe, linhas-opção, categorias, comparação e tema funcionam. O HTML do detalhe e da comparação
    (18 casos em 3 abas) saiu **idêntico** ao do site antigo. `tests/test_site_navegador.py` roda onde houver
    Playwright (no CI é pulado).
- **`dh completo` em paralelo.** Várias builds → `ProcessPoolExecutor` (os.cpu_count() processos, spawn), réguas
  preaquecidas no processo principal (`motor.preaquecer`), uma linha por build no terminal. Caches de `cache/` e
  `resultados/` gravados de forma atômica (`dh/arquivos.py`) e mesclados com o que outro processo gravou.
  - Determinismo: 3 builds (Cavalier 7, Evocation 9, Amadeus 7) em série, em ordem invertida, isoladas e em
    paralelo → JSON idênticos (sem `segundos`). No CI, o recálculo forçado das 157 builds em paralelo mudou só o
    campo `segundos` em relação ao recálculo em série anterior.
  - Como o próprio arquivo entra no hash dos caches, area/horda/saves ganharam caches novos (mesmos números).
- **CI:** recálculo completo **~32 min (32m26s, em série) → 12m12s** no total (completo: 702 s com 4 processos).
  Push sem build nova: ~20 s. Novo disparo manual com `forcar` (Actions → metricas → Run workflow) para recalcular tudo.
- Teste `test_aneis_minimo_equilibrado_maximo` falhava desde o recálculo da Área v2 (o Marcus passou a ter área em
  toda linha); a asserção foi atualizada, sem mudar números.

## 19/11 noite — passada 3
- **O que mudou** (convenções em `calibracao/convencoes-passada1.md`, seção Passada 3):
  - (a) Marcas no Corpo: `ancestral_protectors` em `TIPOS_CORPO`; nova premissa
    `controle.peso_no_controle.ancestral_protectors` = 0,25 (igual à do Sentinel). Na atenção, a marca reduz o dano do
    marcado contra os OUTROS membros (`atencao.vida(..., marca=(k, vetor))`); quem marca não ganha nada para si. O
    "total" usa a marca do mesmo jeito (sem contá-la também como campo). Teste em `tests/test_passada3.py`.
  - (b) Frontliner único: `ref('tank'|'striker'|'frontliner')` = CA marcial+1 (máx. 21), PV 11+(L−1)·8, soft 0,15,
    DPR 0,85·ref (premissas `controle.referencia.frontliner.*`). Party = 2 frontliners + atirador + conjurador;
    `A.posicao(papel)` dá a vaga (tank/striker → frontliner). `build.py` aceita `frontliner`; o motor tático
    (`segundo_frontliner`, `sem_tanque`) cai numa vaga de frontliner; site mostra "Frontliner". O hash da régua de
    controle inclui `controle.referencia`. A paridade do controle com as planilhas virou retrato do motor novo
    (valores da planilha ficam no comentário de `tests/test_paridade.py`).
  - (c) `area.horda2.rounds_max` 5 → 3.
  - (d) Área dos magos com upcast (`ferramentas/geradores/wiz.py`, `area_pico`): 2 maiores magias de área nos 2 maiores
    espaços, escaladas; uma magia só = 2 vezes; truque 0,5. **Bug achado e corrigido no gerador:** os patches de nível
    eram mesclados recursivamente e o `gasta` herdava espaços de níveis anteriores (73 linhas de controle, combo e
    invocação gastavam espaços a mais, ex.: controle do Abjuration 11 gastava 2º+5º). Agora o patch anula o que sumiu.
- Recálculo: push com `[skip ci]` + disparo manual forçado (`gh workflow run` falha: GraphQL bloqueado na sessão; o
  disparo foi feito pela API REST `POST .../actions/workflows/metricas.yml/dispatches` com `inputs[forcar]=true`).
  CI 17m03s, verde.
- **Tau** (`python calibracao/comparar_rpgbot.py`: tau-b entre a nota do RPGBot e a média de dano, Def. F, Def. M,
  controle e área, plano padrão; níveis 7 / 11). Antes = os mesmos dados antes da passada 3 medidos pelo mesmo script
  (os valores anotados antes eram Fighter 0,41/0,63 e Wizard 0,18/0,22):

  | Classe | Versão | Antes (7 / 11) | Depois (7 / 11) |
  |---|---|---|---|
  | Fighter | originais | 0,46 / 0,62 | 0,40 / 0,62 |
  | Fighter | puras | 0,38 / 0,67 | 0,38 / 0,67 |
  | Wizard | originais | 0,18 / 0,21 | 0,03 / −0,03 |
  | Wizard | puras | −0,03 / 0,21 | −0,03 / −0,03 |

- **Corpo dos frontliners do Fighter** (linha principal: nível do Corpo e perfil; antes → depois):

  | Subclasse | nv 7 | nv 11 |
  |---|---|---|
  | Cavalier | 0,1 Taunt → **2,35 Guardião** | 3,73 Tank → **4,99 Tank** |
  | Echo Knight (puro) | 1,40 Tank → 1,93 Tank | 1,28 Taunt → 1,68 Tank |
  | Echo Knight | 0,33 Taunt → 0,99 Taunt | 0,0 Alvo Frágil → 0,0 (a marca está na linha `furia`; no plano: 0,0 → 1,9) |
  | Battle Master | 0,75 Resistente → 0,93 | 1,45 → 1,47 Resistente |
  | Rune Knight | 0,75 → 0,77 Taunt | 0,95 → 0,99 Taunt |
  | Samurai | 0,50 → 0,54 Redirecionador | 0,88 → 0,91 Redirecionador |
  | Purple Dragon Knight | 0,45 → 0,49 Redirecionador | 0,85 → 0,88 Redirecionador |
  | Psi Warrior | 0,0 Neutro | 0,50 → 0,36 Neutro |
  | Champion | 0,28 Redirecionador → 0,0 Neutro | 0,87 Redirecionador → 0,0 Neutro |
  | Eldritch Knight | 0,30 Redirecionador → 0,0 Neutro | 0,0 Redirecionador → 0,0 Vulnerável |

  Quem era `tank` ficou contra uma referência mais fraca (CA −1, PV −4 no 7) e sobe; quem era `striker` (Champion, EK)
  ficou contra uma mais forte e cai para 0. Controle do Cavalier (plano padrão): 3,0 → 1,9 (nv 7) e 4,9 → 2,5 (nv 11);
  a marca saiu do Controle (fica 0,25) e foi para o Corpo.
- Outros efeitos: Área dos magos com área sobe muito (nv 7: ~8 → ~11; nv 11: ~8,4 → 16–20, Evocation e Necromancy no
  teto 20); magos sem linha de área (Chronurgy, Enchantment, Illusion) caem (teto de 3 rounds pune quem só tem truque).
  A correção do `gasta` mudou planos automáticos (ex.: Conjuration 11 dano 7,2 → 0,9 e controle 2,7 → 7,0; Evocation
  11 controle 7,7 → 4,8 porque o plano passou a escolher `area`; Bladesinging 7 controle 3,3 → 0).
- **3 maiores padrões de divergência que restam:**
  1. **Área domina o Wizard e é da lista de magias, não da subclasse.** Com upcast + teto 3, todo mago com Fireball
     fica com Área 10–11 no 7 e 16–20 no 11; Transmutation (vermelho) fica no meio e Divination/Chronurgy (azuis) caem
     por não terem linha de área. É o que derrubou o tau do Wizard. Candidatos: medir a subclasse pelo diferencial
     sobre um "mago base" comum, ou dar linha de área a todos os magos que têm Fireball na lista.
  2. **Manipulação de dados ainda subvalorizada** (Portent, Chronal Shift, Silvery Barbs, iniciativa): Divination
     (azul) segue no fim (média 4,1 / 5,7), Chronurgy só se segura pelo controle.
  3. **Fighter: Eldritch Knight (azul) no fim e Rune Knight (verde) no topo do nv 7.** EK: Corpo 0, controle 0,
     Def. M baixa (War Magic, Shield extra e Indomitable fora do modelo); Rune Knight: Def. F 8,5/12,7 e controle 6,4
     inflam a média. Champion e PDK (laranjas) seguem embaixo, o que bate.
- Nota de medição: a Área dos marciais anda em degraus (4,6–4,8 ↔ 8,1–8,4) por diferenças de 0,3–0,5 round, porque a
  régua da horda não é monotônica no nível (rounds do conjurador de referência: 2,24 no 7, 3,39 no 8, 2,45 no 9).
  Ex.: Champion 11 8,1 → 4,8 e Echo Knight 7 8,1 → 4,8 com o teto 3. Vale suavizar a régua antes da passada 4.

## 19/11 noite — tarefa 3
- **Invalidação por eixo** (`dh/impressoes.py`, `dh/eixos.py`, `dh/motor.py`; README "Cache por eixo"). Cada linha de
  `resultados/<id>.json` ganha `impressoes[linha][eixo]` = hash de (arquivos-fonte do eixo, levantados pelos imports
  + `magias.json` + `eixos.py`) + (premissas sob os prefixos do eixo) + (parte da linha que o eixo lê, com o modo onde
  importa). Ao recalcular, os eixos com a mesma impressão são copiados do resultado antigo; orçamento, planos e anéis
  são sempre refeitos. Sem mudança nenhuma = build inteira em cache. `VERSAO` e `--forcar` continuam forçando tudo.
  - O cálculo de cada eixo saiu de `motor.py` para `dh/eixos.py` (sem mudar número): `motor.py` (cache) fica fora das
    impressões, então mexer na orquestração não recalcula nada. 4 builds (Kael 7, Tin Bin 7 com motor tático,
    Evocation 11, Marcus 7) recalculadas com `--forcar` em modo completo: JSON idêntico ao do CI (sem `segundos`).
  - Migração: resultado antigo sem `impressoes` que ainda vale pela regra antiga (build, VERSAO, premissas, modo) é
    carimbado com as impressões atuais sem recalcular (uma vez; o 1º CI regrava os 157 resultados só com esse campo).
  - Só `segundos` mudou → o arquivo não é regravado (menos commits de ruído do CI).
  - `tests/test_impressoes.py` (13 testes, ~35 s): sem mudança nada recalcula; "mexer" em `horda.py` (hash fingido)
    recalcula só a Área e o resultado é idêntico ao recálculo do zero (Kael, Tin Bin, Amadeus); `dano.py` → dano + área;
    `controle/campo.py` → só controle; `tatico.py` → tático + dano + área + controle só nas linhas táticas; build com
    defesa mexida → só a defesa das linhas afetadas; VERSAO → tudo; migração; `segundos`. Conferido à parte em modo
    completo: Kael 7, Evocation 11 e Marcus 7 com `horda.py` "mexido" recalculam só a Área e batem com o CI
    (Marcus 7: 32 s → 6,5 s).
- **Publicação do site pelo GitHub Actions Pages** (`.github/workflows/metricas.yml`): o job `rodar` gera o site e
  sobe `docs/` com `actions/upload-pages-artifact@v3`; o job `publicar` (`actions/deploy-pages@v4`, permissões
  `pages: write` e `id-token: write`, ambiente `github-pages`) está com `continue-on-error: true`. A troca da fonte do
  Pages pela API (`gh api -X PUT/POST repos/Legue2205/dh-metricas/pages -f build_type=workflow`) foi recusada pelo
  proxy da sessão (403, também no GET), então **docs/ continua sendo commitado na main** até o usuário trocar.
  - **O deploy pelo Actions já funciona** com a fonte atual: no 1º CI o job `publicar` deu "Reported success" e o
    ambiente `github-pages` apontou para https://legue2205.github.io/dh-metricas/. Mas o Pages continua em modo
    branch (o `pages-build-deployment` ainda roda a cada push na main), então hoje os dois publicam o mesmo `docs/`.
- **Bug achado pelo reaproveitamento e corrigido (`dh/planos.py`)**: um eixo recém-calculado chega aos planos como
  `numpy.float64` e um reaproveitado chega como `float` (lido do JSON), e os dois arredondam empates de jeitos
  diferentes (`round(np.float64(0.45), 1)` = 0,4; `round(0.45, 1)` = 0,5). O CI com só a Área recalculada mudou 150
  resultados: as linhas ficaram idênticas, mas algumas médias de plano mudaram. Agora `planos.agregar` lê os eixos
  como no JSON gravado, e o plano não depende mais de o eixo ter vindo do cache (teste
  `test_planos_nao_dependem_de_numpy`). Efeito em relação ao estado de antes da tarefa (linhas idênticas): **±0,1 em
  11 médias de plano de 10 builds**, todas da passada RPGBot: Arcane Archer 3 (corpo np 0,0→0,1), Battle Master 3
  (corpo np 0,4→0,5), Cavalier 5 (corpo 1,2→1,1 no padrão e no combate único), PDK 9 (corpo 1,0→1,1), Enchantment 3
  (controle 0,2→0,1), Illusion 3 (controle np 1,2→1,1), Necromancy 3 e Scribes 3 (controle 2,2→2,1), Scribes 7
  (corpo np 2,0→1,9), Transmutation 11 (controle np 0,9→0,8). Nenhuma letra muda (conferido em todas as tags e
  eixos dos planos).
- **Tempo do CI** (antes: ~20 s num push sem build nova; recálculo completo 12–17 min):
  - push sem mudança de número (1º push, só carimbou as impressões): **1m48s** no total (`rodar` 1m31s, dos quais
    pytest 73 s e `dh completo` 0 s com as 157 builds em cache; `publicar` 10 s). O pytest subiu de 12 s para ~50–75 s
    no CI por causa de `tests/test_impressoes.py` (recalcula 3 builds do zero).
  - mudança só em `dh/horda.py` (só a Área): **2m26s** no total (`dh completo` 58 s: régua da horda refeita + Área
    das 157 builds, o resto copiado), contra 12–17 min antes.
  - mudança só em `dh/planos.py` (planos refeitos, todos os eixos copiados): **1m18s** no total (`dh completo` 1 s).
- **resultados/**: continua na main (é o cache). O que deixou de ir para o commit: arquivo em que só `segundos` mudou
  (ex.: `--forcar` sem mudança de número) não é regravado. As impressões somam 0,1–3,5 KB por resultado (93 KB nos 157)
  (uma linha por eixo); no commit de uma mudança de motor, o diff de cada arquivo é a impressão do eixo + `segundos`.

## 19/11 noite — pendências (tarefa 3)
- **Trocar a fonte do Pages (depende do usuário; a API foi recusada pelo proxy desta sessão):**
  1. GitHub → repositório `Legue2205/dh-metricas` → **Settings** → **Pages** (menu da esquerda, em "Code and
     automation").
  2. Em **Build and deployment** → **Source**, trocar "Deploy from a branch" por **GitHub Actions**. Não precisa
     escolher modelo de workflow (o `metricas.yml` já tem o deploy).
  3. Disparar o workflow uma vez (Actions → metricas → Run workflow, ou um push em `dh/`/`builds/`) e conferir que
     o job `publicar` passou e o site abre.
  4. Depois disso, no `.github/workflows/metricas.yml`, na linha `git add builds resultados cache PAINEL.md docs`,
     **tirar o ` docs`** (e o comentário acima dela); opcionalmente trocar `continue-on-error: true` do job `publicar`
     por nada (para o erro de deploy aparecer). E parar de versionar o site: `git rm -r --cached docs` + `docs/` no
     `.gitignore`, num commit só. (O histórico antigo de docs/ continua no repositório; limpar exigiria reescrever
     o histórico, o que não foi feito.)
- O pytest do CI ficou ~40–60 s mais lento (`tests/test_impressoes.py`). Se incomodar: rodar esses testes só quando
  `dh/` mudar, ou marcá-los como lentos.
- Mexer em `motor.py`/`impressoes.py`/`premissas.py`/`arquivos.py` não invalida nada: se uma mudança nesses arquivos
  mudar número, subir `VERSAO`.
- Avisos do Actions: `actions/checkout@v4`, `setup-python@v5`, `upload-pages-artifact@v3` e `deploy-pages@v4` usam
  Node 20 (obsoleto, forçado para Node 24). Funciona; atualizar as versões quando saírem as novas.
