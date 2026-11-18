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
