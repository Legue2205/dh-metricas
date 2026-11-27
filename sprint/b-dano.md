# Sprint B — dano dentro da classe (#3) e chassi × build de exemplo (#8) — 27/11

Medição: `python calibracao/comparar_chassi.py --sem-holdout --json` (visão misto, dano com pacote_vh), antes = resultados
do main (8054825), depois = builds afetadas recalculadas localmente (`dh expandir` + `dh completo`; nas outras 950
builds chassi/pacote/rpgbot fora do holdout só os planos mudam, as linhas vieram do cache). Gabarito, gates e premissas
não foram mudados. Holdout e party não foram olhados.

## Resultado

| G1 dano (τ pista, dentro da classe) | nv7 | nv11 |
|---|---|---|
| antes | 0,36 | 0,38 |
| depois | **0,43** | **0,39** |

| classe | nv7 antes → depois | nv11 antes → depois |
|---|---|---|
| Cleric | 0,00 → **0,67** | 0,00 → **0,67** |
| Monk | 0,13 → **0,47** | 0,08 → 0,08 |
| Warlock | 0,40 → **0,00** | −0,12 → **−0,36** |
| Wizard | 0,27 → 0,27 | 0,14 → 0,14 |
| Paladin | 1,00 → 1,00 | 1,00 → 0,55 (empate de valor no plano, ver abaixo) |
| Barbarian, Druid, Fighter, Ranger | iguais | iguais |

Outros gates (τ pista / agrupado), antes → depois: deff 0,60/0,58 iguais; controle 0,66/0,61 iguais; suporte
0,38 → 0,38 (nv7), 0,37 → 0,33 (nv11, n≈20: dentro de 1 EP); área agrupada 0,52 → 0,58 (nv7), 0,58 igual (nv11); corpo
agrupado 0,19 → 0,10 (nv7, n = 12: dentro de 1 EP; Peace e Moon caíram por troca de plano), 0,21 igual (nv11). G1b
(comparar_dpr): passa, igual (18/4/1 de 23). G3: nenhum eixo que passava deixou de passar; o topo-10 de área caiu de
9 para 7 "fortes" nos dois níveis (os Spirit Guardians dos domínios de frente agora pagam a concentração) — área não
passava antes.

## Correções (genéricas, com teste em `tests/test_sprint_b.py`)

1. **Concentração genérica errava nos dois sentidos** (`dh/concentracao.py`, `_tem_conc`). Achado no par Grave < War/Forge.
   - O `controle.atencao.conc` da posição (meia/retaguarda do chassi: "conjurador que costuma concentrar", insumo da
     atenção) era lido como "esta linha concentra". 383 linhas sem concentração perdiam o ganho: Inflict Wounds do
     Grave, arma do Death, Fireball/Mystic Arcanum dos Warlocks, Wild Shape/formas dos Druids, Psychic Blades dos Bards.
   - E 271 linhas com concentração RAW sem o campo `"concentracao"` passavam sem ajuste: Spirit Guardians (190, todos
     os domínios de frente e o Crown), Conjure Animals / Summon Beast (Rangers, Druids), Summon do Hexblade, Wall of
     Fire, Insect Plague; e o Hex dos Warlocks (154 linhas, o nome só estava na nota do dano).
   - Regra nova: concentra se declarou (`orcamento.concentracoes`), se o nome RAW está na lista `_concentracao_nomes`
     do magias.json (área, suporte, invocação — `concentracao_por_nome` — e agora também nome/nota das entradas de
     dano, peça a peça e com fim de palavra: "Hex" não pega "Hexblade's Curse"), se é forma de Polymorph/Shapechange/
     Animal Shapes, ou se a LINHA declara `atencao.conc` diferente da principal. Nenhuma premissa nova.
2. **Bladesinger: Haste e Tenser's Transformation declarados como concentração** (`chassi_wizard.py`, campo
   `dano.concentracao`). Sem isso, a correção 1 tirava o ajuste delas (a nota "ataque do Haste" não é nome de magia).
3. **Grave: Path to the Grave com o 2º espaço** (`chassi_cleric.py`, linha `punho-barato`). O Channel Divinity é 2 por
   descanso curto e o Path vale com Inflict Wounds de qualquer nível; o chassi só tinha o maior espaço (1 pico por dia,
   como antes da `area-barata` do M5). O plano padrão agora usa o Path numa luta e o foco de dano em três.
4. **Kensei: arma kensei corpo a corpo** (`chassi_monk.py`, linhas `cac`, `cac-*`, `cac-deft`, `cac-afiar` no 11). RAW o
   Kensei escolhe uma arma kensei corpo a corpo e uma à distância; o chassi só tinha o arco, então nenhum Flurry. O
   plano escolhe: no 7 o foco de dano vai para o corpo a corpo (5,7), no 11 o padrão fica no arco com Sharpen the Blade
   (7,2; o plano paga a distância em corpo/defesa).

## Pares discordantes e causa (visão misto)

### Cleric (pistas: só Grave "alto em pico"; os outros 4 "médio")
| par (nível) | causa | status |
|---|---|---|
| grave < war, grave < forge (7 e 11) | (a) concentração: War/Forge (striker/defensor) com Spirit Guardians sem ajuste; Grave (meia) com o Inflict Wounds ajustado como se concentrasse; (b) o Path só no maior espaço, o plano nunca usava | **corrigido** (1 e 3): Grave 1º nos dois níveis |

### Monk (pistas: Mercy alto, Kensei médio-alto, Long Death baixo, o resto médio)
| par | causa | status |
|---|---|---|
| kensei < open-hand, sun-soul, drunken, long-death (7 e 11) | chassi só com o arco (sem Flurry) | **corrigido no 7** (empata com a régua, 5,0); **no 11 segue** (7,4 < 7,9): o plano padrão prefere o arco + Sharpen pela defesa; o foco de dano no corpo a corpo dá 8,1 |
| astral-self < long-death (7) | RAW: os braços astrais batem com o dado de Martial Arts (1d6 no 7) em vez da lança 1d8, e o 1º round invoca os braços; o Astral Self põe Sab antes de Des | discordância a discutir |
| empates (sun-soul, open-hand, drunken, long-death = régua) | nenhuma dessas tradições muda o dano de alvo único no 7/11; o "baixo" do Long Death e o "médio" das outras não têm mecânica de dano que os separe | discordância a discutir ("por nada consigo separar Long Death de Open Hand no dano") |

### Warlock (pistas: Hexblade, Genie, Fiend alto; Fathomless médio; Celestial fraco)
| par | causa | status |
|---|---|---|
| fiend < fathomless (7, 11), fiend < celestial (11) | o "alto" do Fiend é Fireball = eixo de área (Fiend é 10,2–10,8 em área, topo da classe). No dano de alvo único o Fiend é o Warlock base; Fathomless tem o tentáculo (1d8/2d8 por round na ação bônus) | discordância a discutir (definição do eixo) |
| genie < fathomless (11) | RAW: tentáculo 2d8 todo round > Genie's Wrath +PB 1×/turno | discordância a discutir |
| hexblade < fathomless (7, 11), hexblade < celestial (11) | (a) até o 11 a espada com Thirsting Blade não passa do Eldritch Blast (Lifedrinker é do 12; crítico em 19 não modelado); a vantagem própria do Hexblade é só o Curse, modelado como +PB/2 por acerto (média de 1 uso por descanso curto); (b) **piorou com a correção 1**: o Summon e o Hex do Hexblade (striker, grupo "front", 1,5 acertos/round) agora pagam concentração, e o plano padrão troca para `controle` ×4 (nv7: dano 2,3) — é o pêndulo do pacote A, não erro de dano | discordância a discutir + depende do pacote A |
| celestial = fiend (7, empate) | os dois são o Warlock base no dano; o "fraco" do Celestial é dano radiante/fogo que não casa com o EB, sem efeito no motor | coerente |

### Wizard (pistas: Evocation alto, Scribes médio-alto, o resto médio)
| par | causa | status |
|---|---|---|
| scribes < bladesinging, conjuration (7, 11), scribes < necromancy (11) | Order of Scribes no chassi = a régua pura: a troca de tipo de dano (Awakened Spellbook) só vale contra resistência/imunidade, que o motor não modela. Diferenças de 0,1 | discordância a discutir ("por nada consigo pôr Scribes acima da média sem resistências") |
| (Evocation em 1º, mas só 1,8 contra 1,4) | o "alto" do Evocation é Fireball esculpido (área: 10,7 / 21,4); no 7 nada da escola mexe no alvo único além do Potent Cantrip. E todo Wizard tem o plano padrão em `controle`, então o dano do dia é o truque | coerente na ordem; ver #8 |

### Fora das quatro classes (não mexi)
Ranger nv7 (Gloom Stalker / Fey Wanderer < Hunter/Swarmkeeper/Monster Slayer, Dread Ambusher só no 1º round); Druid
Moon < Spores (as formas pararam de pagar concentração, mas o plano não as usa); Paladin nv11 Conquest < Crown: o
Crown trocou `bless+smite` por `guardioes+smite` porque os dois valem 123,2 × 123,5 no plano (empate de moeda) —
troca de plano por diferença de 0,3%, tema do pacote A.

## #8 — chassi × build de exemplo do RPGBot (misto, depois das correções)
- **Wizard:** o chassi faz `controle` em todas as lutas (controle 4,7–9,4 no 7; 8,7–14,3 no 11); as builds do RPGBot de
  Abjuration, Conjuration, Necromancy, Scribes e Transmutation fazem `invocacao`/`polimorfo` (dano +1,9 a +2,4, corpo
  +5 a +12, controle −2 a −5). Causa: a lista base do chassi tem TODA magia clássica de controle (Web, Hypnotic Pattern,
  Banishment, Psychic Lance, Slow, Fear, Confusion; Hold Monster, Wall of Force, Synaptic Static, Wall of Stone,
  Telekinesis no 11) num `melhor_de`; a build do RPGBot só tem as que o guia escolheu. Com o melhor controle de cada
  encontro, o plano sempre prefere controle e o dano de todos os Wizards vira o truque — o que **comprime o dano dentro
  da classe** (1,4–1,8 no 7) e esconde as invocações da escola.
- **Warlock (11):** o chassi faz `controle` + `arcano`; as builds do RPGBot fazem `invocacao` (dano +1,1 a +1,5, controle
  −4 a −5) pelo mesmo motivo (lista de controle mais longa no chassi). No 7 os dois fazem `controle` ×4.
- **Cleric:** quase igual no dano; o RPGBot põe Spirit Guardians numa luta, o chassi às vezes põe `controle` (Arcana,
  Grave, Knowledge, Trickery no 7). Corpo da build do RPGBot maior nos domínios de frente (raça/feat/armadura).
- **Monk:** Kensei do RPGBot +2,6 / +2,9 no dano (feat e raça); Shadow usa Darkness (Eldritch Adept); Sun Soul do RPGBot
  fica nos raios (menos dano que a lança do chassi).
- Leitura: não achei escolha do chassi injustificável pela regra que eu pudesse mudar sem decidir com o usuário (a régua
  comum é de propósito). Proposta: rodar uma variante do chassi dos plenos com a lista de controle "do guia" (as 3–4
  magias de controle que o RPGBot recomenda para a classe) para medir quanto do G1/G4 vem da lista longa.

## Discordâncias para o usuário (com hipótese)
1. **Fiend "alto" = área.** O RPGBot dá dano alto ao Fiend pelo Fireball; no nosso eixo de dano (alvo único/chefe) o
   Fiend é o Warlock base. Ler a pista do Fiend como área? (o mesmo vale para o "alto" do Evocation).
2. **Hexblade no 7/11.** Por nada consigo deixar o Hexblade forte no dano antes do Lifedrinker (12): espada = EB, e o
   Curse é +PB/2 por acerto. Proposta de premissa (não mudei): o Curse no eixo de dano (cenário de chefe) valer +PB
   inteiro, já que o alvo amaldiçoado é o chefe; e "eb+trevas" (Darkness + Devil's Sight no EB) como linha do Hexblade.
3. **Scribes "médio-alto"** só com resistências modeladas.
4. **Monk:** Long Death "baixo" × Open Hand/Drunken/Sun Soul "médio" sem mecânica de dano que os separe; Astral Self
   abaixo da régua pelo dado dos braços (RAW).
5. **Visão misto nos conjuradores:** com α = 0,2 o dano de Cleric/Warlock/Wizard é ~o plano padrão, que para conjurador
   quase sempre é controle; o τ dessas classes (n = 5 cada, um par muda 0,2–0,4) passa a medir a troca de plano mais que
   o dano da subclasse. A visão foco/externo não ajuda (0,27 / 0,38 antes). Depende do pacote A (plano não tudo-ou-nada).

## Arquivos
`dh/concentracao.py`; `ferramentas/geradores/chassi_{cleric,monk,wizard}.py`; `progressoes/` e `builds/` de
chassi-cleric-grave, chassi-monk-kensei (3 variantes), chassi-wizard-bladesinging; `tests/test_sprint_b.py`.
Para medir depois do merge: `dh completo` em todas as builds (a impressão dos planos muda com `concentracao.py`; as
linhas vêm do cache — ~9 min com 8 processos) e nas 5 progressões acima (linhas novas, ~2 min).
