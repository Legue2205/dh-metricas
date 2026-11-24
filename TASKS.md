# TASKS — consistência das réguas

Modelo de trabalho (decidido em 22/11/2026):
1. **Varredura descritiva** → lista da passada N (só descreve, não corrige).
2. **Correção task a task**, em ordem de prioridade. Antes de cada task, revalidar contra o último relatório
   (uma correção anterior pode ter resolvido ou mudado o problema). Depois de cada task, rodar o diff contra a baseline
   e anotar o delta na própria task.
3. Problema novo achado no meio → **lista da passada N+1** (não corrigir na hora).
4. Fim da lista → nova varredura descritiva; revisar se as tasks da N+1 ainda fazem sentido; começar a N+1.

Regras:
- **[M] mecânica** (feature faltando, bug, linha mal montada): o Claude corrige sozinho.
  **[J] julgamento** (premissa/hipótese): vai para **Decisões**, para o usuário, em bloco. Premissa não muda no meio da
  passada (régua congelada, regra de 18/11). **[G] gabarito**: talvez a pista esteja errada, e não o motor.
- **Limiar "moderado a grande":** τ por régua < 0,1 numa classe com n ≥ 4 pistas; média de um eixo entre classes fora
  do esperado em > 2 níveis eq. sem justificativa de posição; feat/feature com efeito ≤ 0 quando deveria ser positivo;
  valor no teto (20) ou travado num valor igual para toda uma classe.
- **Ferramentas:** `python calibracao/comparar_chassi.py [--visao padrao|externo] [--classe X]` (τ por régua,
  posição, feats) e `python calibracao/consistencia.py` (originais do RPGBot, entre classes).
  Baseline congelada em `calibracao/baseline/p1-*` (22/11, commit 69c438f + chassis).

## Baseline da passada 1 (22/11)

τ por régua (eixo × pista do gabarito, dentro da classe, média ponderada por n; nv7 / nv11):

| régua | padrão | externo | agrupado (padrão, nv11) |
|---|---|---|---|
| dano | +0,16 / +0,31 | +0,18 / +0,32 | +0,06 |
| def. física | +0,45 / +0,46 | +0,52 / +0,52 | −0,07 |
| controle | +0,49 / +0,25 | +0,47 / +0,34 | +0,44 |
| suporte | +0,31 / +0,33 | +0,33 / +0,39 | +0,23 |
| área | — | — | +0,73 |
| corpo | — | — | +0,39 |

## Passada 1

Ordem: Warlock e Bard primeiro (pedido do usuário); depois por tamanho do erro.

- [x] **P1.1 Warlock — dano** [M] — **feito 22/11:** Hexblade ganhou as linhas `eb` e `eb+hex` (EB com Carisma +
  Hexblade's Curse PB/2 por raio, atenção de atirador): dano no 11 de 5,9 → 9,3 (linha), externo 7,9 → 9,3.
  τ médio warlock nv11 (externo) 0,32 → 0,39; τ dano da classe igual, porque (a) a invocação (Summon Aberration, 9,4) é o
  máximo de dano de todos os patronos no externo (→ P2.1) e (b) a pista "alto" do Fiend é Fireball = área [G] (→ P2.3);
  no padrão nada muda porque o plano auto não olha rendimento (→ D5). Original: — τ dano −0,60 (nv11, padrão). Hexblade (striker, pista "alto") tem o pior dano da
  classe: 2,5 no padrão, 7,9 no externo; a linha corpo a corpo `principal` dá só 4,5 no 11. O plano auto põe `combo`
  (1,8 de dano) nas lutas prioritárias. Fiend (pista "alto") 3,9 < base 5,2. Conferir Hexblade's Curse, arma do pacto,
  Thirsting Blade e se o plano está escolhendo controle onde o dano deveria vencer.
- [x] **P1.2 Warlock — controle** [M] — **revisto 22/11, sem bug:** no padrão os dois valores vêm do plano auto (→ D5);
  no externo nv7 o τ −1,0 é de 3 pistas com valores 6,3–6,9 (ruído). GOO < base no 7 porque o Fiend tem PV temporários
  (Dark One's Blessing) e segura a concentração. Original: — no externo nv7, τ controle −1,0; no padrão nv11 Hexblade/Fiend/Genie = 7,4,
  os outros todos = 2,3 (dois valores para 9 patronos). Great Old One (pista "alto") fica no 2,3.
- [x] **P1.3 Bard — suporte invertido** [M/G] — **feito 22/11:** Cutting Words estava com `lado: "of"`; dado com mix só
  defensivo (ca/save) agora vai para `def` (brd.py e chassi_bard.py; só o Lore muda; total igual). O resto não é bug:
  Unsettling Words do Eloquence está no controle por design (pista de suporte do RPGBot o inclui → [G], P2.4); BI custa
  ação bônus e Cutting Words não (→ D6). Original: — τ −0,89/−0,82: Eloquence e Lore (pista "alto") 7,2/7,0 abaixo de
  Creation e Glamour ("médio") 8,6/8,4. Conferir Unsettling Words, Cutting Words (defensivo), Mantle of Inspiration
  (PV temporários possivelmente inflados), Performance of Creation; e se Eloquence/Lore deviam mesmo ser "alto" em suporte.
- [x] **P1.4 Bard — dano/controle planos** [M] — **revisto 22/11, sem bug:** é a régua comum (Vicious Mockery e a mesma lista
  de controle); as diferenças dos colégios estão em suporte/área ou em `nao_modelado` (Words of Terror, Mantle of Whispers).
  Original: — 8 colégios com dano 0,6 idêntico e controle 3,3 idêntico (exceto
  Eloquence/Swords): a régua comum domina tudo. Conferir se Cutting Words/Unsettling Words entram no controle.
- [x] **P1.5 Wizard — controle e dano** [M] — **feito 22/11 (controle):** bug no motor: o Monte Carlo do controle usava
  um `rng` global e o `forcar_falha` avalia a magia duas vezes, deslocando os sorteios de todas as fontes seguintes; o
  efeito de Portent/Chronal Shift ficava abaixo do ruído (Chronurgy < escola sem feature). Agora cada fonte recomeça da
  mesma semente (números aleatórios comuns, `campo.reiniciar_rng`). τ controle Wizard nv11 (externo) −0,60 → +0,65;
  τ controle global nv11 0,34 → 0,62. Todo o controle desloca um pouco (CI com --forcar). **Dano:** não é bug, é a P2.1
  (a invocação comum é o máximo de todo Wizard; necromancy 14,1 por mortos-vivos) → D7. Original: — τ controle −0,60 e dano −0,60 (nv11, externo). Dano externo do Wizard
  (10,8) passa o do Fighter (9,4): ver qual linha dá esse pico (invocação? área contando em alvo único?).
- [x] **P1.6 Sorcerer — def. física** [G] — **revisto 22/11, sem bug:** a pista "alta" do Divine Soul é a armadura pesada do
  dip de Cleric da build do RPGBot (o chassi não tem dip); Draconic lidera a classe (6,9 × 5,9). Dano baixo nos originais =
  plano auto pondo `combo` em todas as lutas (D5) + metamagia não modelada (→ P2.6). Original: — τ −0,5 nos dois níveis: Draconic (Draconic Resilience) devia liderar.
  Nos originais, dano do Sorcerer 0,8/1,0 (o menor junto do Bard) mesmo com Fire Bolt.
- [x] **P1.7 Cleric — controle e dano** [M] — **revisto 22/11, sem bug de motor:** a régua do Cleric só tem Hold Person e
  Banishment (alvo único); o controle de área do Bard/Wizard/Armorer vem do Hypnotic Pattern. Controle 0,0 nos originais nv7 =
  plano auto sem linha de controle (D5). Dano nv7: depois da D5/D7. Original: — originais nv7: controle 0,0 em todos (checagem "clérigos ≥ fighters" falha);
  chassi externo nv11 controle 3,4 com Hold Person/Banishment, contra Artificer 8,2 só com Web. τ dano nv7 −0,38.
- [x] **P1.8 Controle entre classes** [M] — **revisto 22/11:** Web × Entangle na mesma build: campo 4,9 × 1,8, e a diferença é
  RAW (Web repete o save a cada entrada/início de turno, Entangle só na conjuração; For dos brutos). Hypnotic Pattern do
  Armorer está certo (lista da subclasse no 9). A diferença entre classes vem da lista da régua (→ P2.7). Original: — mesmas magias, valores muito diferentes: Druid 3,6 (Entangle/Hold
  Person/Polymorph) e Cleric 3,4 contra Artificer 8,2, Warlock 9,1, Bard 9,0 (externo nv11). Pode ser o mesmo bug da P1.7.
- [x] **P1.9 Corpo de invocações/torreta** [M/J] — **feito 22/11 (parte M):** o Eldritch Cannon estava grátis em todas as
  linhas; agora custa 0,75 espaço de 1º por luta (1 grátis/descanso longo + 3 espaços) e a `principal` fica sem ele
  (nova `principal+inv`). Corpo do Artillerist nv7 19,7 → 14,8; nv11 continua ~27, porque as linhas de controle/área (que
  já gastam) levam o canhão: o tamanho do corpo de invocação é a D4. Original: — Artificer corpo 28,8 (Artillerist 28,7, o maior de todos, acima do
  Ancestral Guardian 26,8) e Druid 24,3 (Shepherd 24,7). Ver se torreta/invocação está contando como presença do
  personagem, e quanto deveria contar (pode virar decisão).
- [x] **P1.10 Sensibilidade do corpo/defesa a 1 ponto de atributo** [J → D8] — **revisto 22/11:** não é o PV em si, é a
  extrapolação do corpo acima do nível 20 (`nivel_corpo`: "positivo ainda no 20 ⇒ extrapola pela inclinação"). Infiltrator
  (CA 20, 91 PV) tem corpo 31,5; −11 PV → 22,9. Outliers do corpo estão todos nessa faixa (AG 25–27, Artillerist ~27,
  Cavalier 24, War 23,6). Original: — no 11, trocar um ASI por feat derruba o corpo
  em −3 a −7,5 níveis (Armorer Infiltrator + Skill Expert: −7,5; Alchemist + Fey Touched: −5,8). Ver se é o PV/CA
  mesmo ou um degrau da rampa.
- [x] **P1.11 Sobra de recursos dos conjuradores** [J → D9] — **revisto 22/11:** Whispers é intencional (build social do guia,
  só linha `principal`; magias em `nao_modelado` → P2.8). Nos outros, cada linha gasta 1 magia por luta, então sobram os
  espaços de 2º/3º (Life, Moon, Conjuration sobram 2–3 de cada). Original: — originais nv11: Bard Whispers sobra 47 níveis de espaço;
  Cleric 25, Druid 28, Wizard 21 em média. O plano auto gasta pouco e subavalia conjuradores no padrão.
- [x] **P1.12 Área no teto** [J → D3] — **revisto 22/11:** é a escala (teto 20), não bug. Original: — Wizard e Sorcerer médios no 20,0 (teto) no externo nv11; Light e Necromancy no 20
  já nos originais. A régua satura e não separa. Retaguarda 14 × marciais 5–8: conferir se é real.
- [x] **P1.13 Dano no padrão colapsa por troca de linha** [J → D5] — confirmado na P1.1 (plano auto só olha gasto). Original: — estrutural: o plano escolhe linhas de controle/combo nas
  lutas prioritárias, e o dano do dia de quem tem opções cai (Hexblade 2,5 × 7,9 externo). Ligado à Decisão D2.
- [x] **P1.14 τ de dano levemente negativo** [M] — **fechada 23/11: duplicada da P2.12.** — **adiada para a passada 2** (pequena; depende de D5/D7). Original: — Monk (−0,16/0,0), Ranger (−0,19), Rogue (−0,30 externo nv7). Pequenos,
  conferir depois dos maiores.
- [x] **P1.15 Variância zero** [M] — **revisto 22/11:** só 3 pistas de controle no Paladin (Conquest 4,1 < Redemption 4,9:
  a velocidade 0 da Aura of Conquest não está modelada → P2.9) e 1 de suporte no Fighter. Original: — Paladin controle τ 0,0 e Fighter suporte 0,0: provavelmente todos iguais (só uma
  subclasse com valor). Confirmar se é falta de mecânica (Paladin: Conquest/Fear, Ancients/Nature's Wrath).

## Fechamento da passada 1 (22/11, depois do CI com --forcar, commit dafa63e)

τ por régua no externo (nv7 / nv11), baseline → agora: dano 0,18/0,32 → 0,18/0,32; def. física 0,52/0,52 (igual);
**controle 0,47/0,34 → 0,63/0,65**; suporte 0,33/0,39 (igual). Warlock e Sorcerer nv7 no controle: τ −1,0/+0,5 → sem τ
(as subclasses agora empatam; o valor antigo era ruído do sorteio).

Problemas moderados a grandes que restam:
1. **Corpo acima de 20** (D8, agora o maior): 14 chassis > 20 no externo nv11 — Infiltrator 42,6, Moon 31,9, Armorer 32,3,
   Spores 29,3, Artillerist 29,3, Cavalier 26,8; Druid médio 24,3, Artificer 28,8.
2. **Dano escondido pela invocação** (D7): Wizard −0,60, Warlock −0,25 no nv11.
3. **Suporte do Bard invertido** (D6 + pista [G], P2.4): −1,0 / −0,82.
4. **Área no teto** (D3): Sorcerer e Wizard médios em 20,0.
5. **Ranger sem controle nem suporte** (0,0 em todos; Ensnaring Strike, Spike Growth e Conjure Animals fora da régua) → P2.11.
6. **Dano dos marciais no nv7** levemente negativo (Monk −0,16, Ranger −0,19, Rogue −0,30, Fighter 0,07) → P1.14, agora P2.12.
7. Def. física agrupada ≈ 0 entre classes: as pistas são relativas à classe; não é sinal de régua quebrada.
8. Def. mágica não tem nenhuma pista no gabarito: sem teste possível hoje.

Revisão da lista da passada 2: todas seguem valendo. A P2.5 (ruído do Monte Carlo) muda de foco: os números aleatórios
comuns resolveram a comparação entre builds; resta só a dependência do valor absoluto em relação à semente. Entram a
P2.10 (corpo > 20, até a D8), a P2.11 (Ranger) e a P2.12 (ex-P1.14). Ordem sugerida, depois das decisões: D8 → D5 → D7 →
P2.7/P2.8/P2.11 (listas e magias de controle) → P2.6 → o resto.

## Critério de pronto da fase atual (consistência de cada régua) — proposta de 24/11

Ruído do τ de Kendall (erro-padrão sob H0): n = 4 → 0,49; 6 → 0,35; 8 → 0,29; 12 → 0,22; 40 → 0,11; 70 → 0,08. O τ
**por classe** (4–6 subclasses) é quase todo ruído; o τ **global por régua** (n = 19–68) é o número confiável
(erro 0,08–0,17).
1. **Gate da métrica:** τ global por régua (visão misto, dentro da classe) ≥ 0,30 **e** > 2 × erro-padrão, nos níveis 7
   e 11, para dano, def. física, controle e suporte. Área e corpo (poucas pistas): só o agrupado, ≥ 0,30.
2. **O que conta como mudança:** só variação > 1 erro-padrão (~0,1–0,15). Por classe, só é sinal τ < −0,5 com n ≥ 6
   que persiste em duas passadas.
3. **Gate mecânico:** validador sem ERRO; item do `nao_modelado` em ≥ 30 builds modelado ou declarado fora de escopo;
   nenhuma task [M] aberta com efeito esperado ≥ 1 nível num eixo.
4. **Platô:** uma passada inteira sem mover nenhum τ global > 1 erro-padrão encerra a fase; o que sobrar fica rotulado
   ([G] gabarito, [J] decisão, ou "aceita", uma linha cada). Depois: calibração entre réguas.

Situação em 24/11 (p3): def. física 0,44/0,42 ✓; controle 0,38/0,61 ✓; **dano 0,17/0,28 ✗** (abaixo de 0,30);
**suporte 0,37/0,26 ✗** no 11 (0,26 < 2 × 0,17). Faltam só essas duas frentes.

Situação em 24/11 madrugada (p4, CI do commit 7851e81): def. física 0,44/0,42 ✓; controle 0,38/0,61 ✓; suporte
0,37/**0,38** ✓; área agrupada 0,60/0,71 ✓; **dano 0,18/0,28 ✗** (o que era mecânica foi corrigido; o resto depende de
D11/D12 ou é gabarito); **corpo agrupado 0,37/0,18 ✗** no 11 (depende de D13; gate frágil, 13 pistas). Critério 3 ✓
(P3.4). A passada 3 moveu o suporte em > 1 erro-padrão, então ainda não é platô; os bloqueios que sobram são decisões.

## Passada 3 (aberta 24/11) — foco nas duas réguas fora do gate
- [x] **P3.1 Régua de dano** [M] — o pior gate (0,17 no 7). Juntar P2.12 (marciais no 7) e o dano do Cleric no 11
  (0,76 → 0,38); ver o peso das invocações no dano (ligado à P3.3).
  **Feito 24/11 (madrugada).** Varredura de pares discordantes (pista de dano do gabarito × dano do motor, dentro da
  classe; 94 de 268 pares no misto). Quem mais discorda: Swashbuckler 16, Fey Wanderer 9, Samurai 8, Long Death 8,
  Kensei 7, Soulknife 7, Gloom Stalker 6, Arcane Trickster 6. Diagnóstico por grupo:
  - **[M] Swashbuckler sem ação bônus**: o chassi descarta a raça (o Booming Blade do RPGBot é racial) e o Fancy
    Footwork já faz o papel do Disengage, então a ação bônus ficava vazia. Linha nova `duas-armas` (espadas curtas,
    2ª chance de Sneak). Dano 3,9 → 4,9 (nv7), 5,7 → 7,5 (nv11). Rogue nv7 −0,30 → −0,22; global nv7 0,17 → 0,18.
  - **[J] Steady Aim em 100% dos turnos** (todos os atiradores do Rogue): é o que põe os "médio"/"básico" acima do
    Swashbuckler "alto". Experimento numa cópia com 75%: Rogue nv7 −0,22 → −0,11, nv11 igual. → **D11**.
  - **[J] Pico do 1º round**: Gloom Stalker (Dread Ambusher), Assassin, Grave ("alto em pico"). A régua é a média de 4
    rounds; o RPGBot valoriza o alfa. Só 3 pistas: efeito pequeno. → **D12**.
  - **[J/entre réguas] Plano desvia recurso do dano**: Open Hand e Mercy gastam ki em Stunning/Hand of Healing, os
    Rangers usam Spike Growth em 3 de 4 lutas, o Hexblade (k = 1) põe o Summon Aberration nas 4 lutas porque o corpo da
    invocação vale 21 (extrapolado). É a troca entre réguas: a visão externa dá quase o mesmo τ (0,18/0,30), então não é
    o que segura a régua. Fica para a fase 2 (calibração entre réguas); P3.3 continua parada.
  - **[G] Gabarito**: Fey Wanderer (Dreadful Strikes 1d4 contra 1d8 de Colossus Slayer/Planar Warrior: o motor está
    certo no RAW), Kensei e Samurai com arco (alcance não é dano), Order of Scribes (troca de tipo = resistências, não
    modelado), Celestial "fraco" com o mesmo EB do Fiend.
  - Testado e descartado: régua de dano incluindo área (max(dano, área) ou dano + ½ área) não melhora de forma
    consistente (nv7 0,18 → 0,06 ou 0,18; nv11 0,27 → 0,33 ou 0,32).
  **Conclusão:** o que era mecânica na régua de dano foi corrigido; o resto é convenção (D11, D12), troca entre réguas
  ou gabarito. Pelo critério de pronto, o dano fica abaixo do gate com resíduo rotulado, a menos que D11/D12 mudem.
- [x] **P3.2 Régua de suporte no 11** [M] — P2.18 (Cleric sem ordem) e P2.14 (Mantle); Bard no 7 (−0,89) é n = 4: ruído
  até persistir.
  **Feito 24/11.** Causa: a agregação D10 somava os ganhos das magias extras em **níveis**, e a régua de nível não é
  linear (degraus de 1–2 de dano equivalente no começo, ~7 no meio). Quem parte de uma linha base baixa ganha níveis
  baratos: Life (base 2,3) + Bless + Preserve Life dava 13,7, a soma bruta dá 11,9; o Peace, que já tem o Emboldening
  Bond na base, ficava atrás. Agora suporte soma o dano equivalente (`total`) e dano soma o DPR CA a CA, e só no fim
  converte para nível (conferido: `nivel_eq` gravado = régua(total/DPR) nas 2634/5795 linhas). Medido reagregando os
  resultados: suporte nv11 0,26 → **0,38** (Cleric 0,00 → 0,45); dano sem mudança; nada piorou. Teste novo em
  `test_eixos_novos.py`. Área e controle ainda somam níveis (régua própria; efeito esperado pequeno) → resíduo.
  P2.14 (Mantle) e Bard (Glamour acima de Lore/Eloquence, n = 4) ficam como ruído até persistirem.
- [ ] **P3.3 Invocação domina o plano no 7** [J/M] — da varredura da passada M; o usuário não vê problema por ora:
  só investigar se a P3.1 apontar para ela.
- [x] **P3.4 Gate mecânico (critério 3): itens do `nao_modelado` em ≥ 30 builds** — 23 itens (contagem nos níveis 7/11,
  654 builds). Classificação (24/11):
  - **Fora de escopo da fase 1 (valem igual para a classe inteira, não mexem na ordem dentro da classe → fase 2):**
    Faerie Fire (74; todo Bard/Druid/Artificer), Deflect Missiles (56, Monk), Aura of Courage / Find Steed / smite
    guardado para o crítico (54, Paladin), Feral Instinct / Relentless Rage / Fast Movement / Primal Path 14 (Barbarian),
    Slow Fall / Patient Defense / Step of the Wind (Monk), Natural Explorer / troca de alvo da Hunter's Mark / dano do
    Spike Growth (Ranger), Silvery Barbs (Wizard/Bard; = M1b), quebra de concentração (todo Cleric/Wizard), Indomitable.
  - **Fora de escopo do motor (utilidade, fora de luta, mobilidade, iniciativa):** curas fora de luta, magias
    utilitárias, Misty Step, Mass Suggestion, penalidade de deslocamento, Song of Rest fora de luta.
  - **Texto velho (já modelado):** Counterspell (reações M1), Dissonant Whispers (passada M), Sleep onde há a linha.
  - **Específico de subclasse (resíduo pequeno):** Faerie Fire do Light/Twilight Cleric e do Archfey (3 subclasses).
  → Critério 3 atendido com esta classificação. Limpar os textos velhos do `nao_modelado` fica para quando os
  geradores forem rodados de novo.
- [ ] **P3.5 Régua de corpo no 11 (agrupado 0,18 < 0,30)** [J/M] — os "alto" que ficam embaixo são os protetores que
  puxam o dano de um aliado para si: Aura of the Guardian (Redemption), Divine Allegiance (Crown), Protective Bond
  (Peace). Hoje marcam só o próprio corpo (≈ 11), como se a feature não existisse; Ancestral Protectors, Moon e as
  invocações ficam acima. É mecânica nova e de julgamento → **D13**. São só 13 pistas e agrupadas entre classes:
  o gate de corpo é frágil (erro ≈ 0,2).
- Rotular e aceitar: P2.3/P2.4 [G]; Sorcerer def. física (pista do dip) [G]; M1b/M7b/M8b/P2.9 ficam como resíduo
  "aceito" desta fase (efeito esperado < 1 nível).

## Estado geral (23/11 manhã)

Infra sólida (recálculo completo em ~10 min); réguas moderadamente consistentes dentro da classe (τ 0,2–0,5: controle e
def. física ~0,5, dano o mais fraco 0,17–0,32); entre classes ainda não comparável (def. física agrupada ~0; def. mágica
sem pista); ~10 premissas treináveis ainda não treinadas; **1039 das 1056 builds têm `nao_modelado`**. Decisão (usuário,
23/11): antes de mais ajuste por classe, uma **passada de modelagem** dos itens recorrentes, como mecânica genérica;
depois o treino dos parâmetros (treinar agora calibraria em cima de buracos).

## Passada de modelagem (M) — itens recorrentes do `nao_modelado`

Legenda: **[D]** declarar nos geradores (o motor já sabe) · **[N]** mecânica nova (tipo/campo genérico + teste) ·
número = builds com o item no `nao_modelado`. Ordem = impacto (quantas builds × eixos onde hoje há buraco). Mesmo modelo
de trabalho das passadas: revalidar antes de cada item, diff contra a baseline (`p2b-*`) depois, achados novos → lista
seguinte. Itens que mudam premissa vão para Decisões.

- [x] **M1 Reações declaradas** [D] — **feito 23/11 (Counterspell e Absorb Elements):** campo genérico
  `reacoes_magicas` na build → o `resolver` cria `reacao-<magia>` = principal + os campos da reação (tabela
  `_reacoes_magicas` no magias.json); o orçamento cobra o espaço e o plano (D5/D9) decide quando vale. Distribuído por
  `ferramentas/geradores/m1_reacoes.py` (chassis: lista RAW da classe; RPGBot: só se o `nao_modelado` cita) em 97
  progressões; ligado ao `chassi.escrever`. Wizard Evocation 11: def. mental 8,5 → 12,5 com Counterspell; o plano o usa
  como extra nas 4 lutas. Silvery Barbs (defensivo: tipo novo na defesa) → M1b. Original: — Counterspell (86), Absorb Elements (60), Silvery Barbs (60), Shield. O motor de
  saves já trata `absorb`/`contra` e o controle tem Silvery Barbs; falta declarar nas builds, respeitando uma reação por
  round (`reacao` / `dh validar`). Eixos: def. mágica, defesa, controle.
- [ ] **M1b Silvery Barbs** [N] — reação de 1º que força a rerrolagem de um acerto/sucesso inimigo; precisa de um tipo
  de reação na defesa (com custo de espaço no orçamento) e do `forcar_falha` no controle (60 builds).
- [x] **M2 Kit do Ranger** [D/N] — **feito 23/11** (chassi_ranger.py e ran.py): Hunter's Mark com concentração declarada;
  linha Favored Foe (1d4/1d6 por turno, concentração, PB usos/descanso longo); linha Ensnaring Strike (novo
  `ensnaring_strike` no magias.json, `condicao_no_acerto`); linha Conjure Animals no 9+ (8 lobos, Pack Tactics ≈ 80% de
  vantagem; o dano já sai pela sobrevivência da P2.13); pet do Beast Master/Drakewarden como corpo. Ranger 11 (padrão):
  dano 7,2 → 11,2 (Hunter), corpo 11 → 28 (lobos atraem o inimigo esperto); controle do plano segue 0 (Ensnaring rende
  1,5–2,6 e perde para a Marca: honesto para o Ranger 2014); nível 7 sem mudança. Spike Growth → M6. Também: o
  `m1_reacoes.py` ficou idempotente (a 2ª passada apagava as reações das builds do RPGBot). Original: — Hunter's Mark com concentração (74), Favored Foe/Natural Explorer (74), magias além
  da Marca (74), pet como corpo e dano (74; `invocacoes`), Ensnaring Strike e Spike Growth (controle). Ex-P2.11: hoje o
  Ranger tem controle e suporte 0,0 em todas as subclasses.
- [x] **M3 Sobrevivência marcial** [D] — **feito 23/11:** mecânica genérica `patches_linhas` (feature que vale em
  várias linhas; número soma, filtro `quando_gasta`), `defesa.cura_luta` (autocura média por luta, também no PV da
  atenção do corpo) e `rerolagens` fracionário nos saves (determinístico). `m3_sobrevivencia.py` (ligado ao
  chassi/marcial.escrever, 60 progressões): Second Wind 0,5 × (1d10 + nível) por luta; Indomitable 1/2/3 por descanso
  longo ÷ 4 lutas; Relentless Rage ≈ 1,5 golpe extra nas linhas de fúria do 11. Champion 11: defesa 10,3 → 10,7,
  def. mental 2,6 → 3,2, corpo 14,5 → 15,1; Berserker 11: defesa 13,5 → 15,3. Original: — Indomitable (96; `rerolagens` dos saves), Second Wind (80; cura por luta),
  Relentless Rage (50; PV extra). Eixos: defesa, def. mágica, corpo.
- [x] **M4 Kit do Warlock** [D/N] — **feito 23/11** (`wlk.kit_m4`, usado no chassi e nas builds do RPGBot): linhas
  Armor of Agathys (PV temporários 5 × nível do pacto + retaliação 1×/luta, 1,0 na frente / 0,4 atrás; sem
  concentração), Darkness + Devil's Sight (vantagem em 75% dos ataques, desvantagem contra ele; concentração) e Hunger
  of Hadar no 5+ (≈ 6d6 com save em 3 alvos; concentração). Hexblade 11: defesa da linha 8,2 → 14,8 (trevas) / 10,4
  (Agathys). O plano do dia não muda (k = 1 no Warlock e a invocação rende mais); entra pelo anel externo do misto.
  Cegueira/terreno do Hadar e Repelling Blast → M8. Original: — Armor of Agathys (61; PV temporários [D] + dano de retaliação [N]), Hunger of Hadar
  (66; área/controle), Darkness + Devil's Sight (61; [N] vantagem/desvantagem), Repelling Blast e outras invocações (45;
  empurrão no controle [N]).
- [ ] **M4b Corpo agrupado caiu com o M2** [M] — corpo agrupado entre classes 0,27 → 0,18 (nv11) e 0,49 → 0,37 (nv7)
  depois dos lobos do Conjure Animals (Ranger 11 corpo 28). Ver se é o outlier ou a régua.
- [x] **M5 Concentração e linhas sem concentração** [D] — **feito 23/11 (parcial, ver M5b):**
  (1) `orcamento.concentracao_por_nome`: o `dh validar` reconhece pelo nome (lista `_concentracao_nomes`) a concentração
  não declarada em área/suporte/invocação e dá **AVISO** (não erro: podem ser lançadas uma depois da outra; não quebra o
  CI); 6 avisos hoje. (2) `chassi.area_barata`: linha de área sem concentração no nível base (Wizard/Sorcerer: Fireball
  no 3º desde o 5; Druid: Ice Storm no 4º desde o 7). (3) Bug da D9: o mesmo truque com menos rounds (n diferente) era
  tratado como peça repetida e bloqueava qualquer extra. (4) No resultado do dia, cada extra soma só o ganho por eixo
  (dano = chefe, área = horda: o Fireball extra não troca rounds de truque contra o chefe); o ganho total segue decidindo
  a escolha. Wizard Evocation 11 = controle/invocação + Fireball + Counterspell em toda luta (sobram só 2 espaços de 2º);
  dano do dia 7,9 (igual), corpo 15,3 → 18,6; Cleric Life 11 dano 3,2 → 4,4. Original: — ex-P2.17: geradores declaram `concentracao` em área/suporte
  (Spirit Guardians, Wall of Fire, Bless…) e o `dh validar` passa a checar; ex-P2.16: linhas de blaster puro e de
  buff/cura sem concentração para Wizard/Druid/Sorcerer (para a D9 render).
- [x] **M5b Os 6 avisos de concentração** [D] — **feito 23/11:** `wiz.area_sp` marca `concentracao` pelo nome (e a
  marca sobrevive ao upcast); o pico de área não junta duas áreas de concentração; o `combo` só leva áreas sem
  concentração. Sobrou 1 aviso: solaris-9 (party DragonHeist, área "Wall of Fire em linha" junto de outra concentração:
  decisão do usuário). Ligar o erro no validador fica para quando a party estiver limpa. Original: — `combo` do Sorcerer Draconic 11 (Wall of Fire) e Wild Magic 9/11
  (Insect Plague) junto do controle; áreas do Druid Land/Spores 11 (duas áreas de concentração na mesma linha);
  solaris-9 (party: só reportar). Corrigir nos geradores e depois ligar o erro no validador.
- [x] **M6 Magias de controle faltando e listas das réguas** [N] — **feito 23/11 (parcial):** no magias.json, Plant
  Growth (3º, sem save, sem concentração, peso 0,35), Spike Growth (2º, conc., 0,3), Sleet Storm (3º, conc., Des, 0,5,
  repete o save na área), Dissonant Whispers (1º, Sab, um turno, 0,5) e Psychic Lance (4º, Int, um turno, 1). Pesos de
  terreno são chute (a calibrar). Listas: Druid + Sleet Storm e Plant Growth do 5; Ranger + linhas `terreno-espinhos` (5+)
  e `terreno-plantas` (9+). Ranger 7: controle do plano 0 → 3,7 (Spike Growth em 3 lutas, dano 6,1 → 4,8); Druid: linha
  de controle 6,75 no 11, mas o plano prefere Haste/invocação. Sleep fora (precisa de pool de PV). Falta pôr Dissonant
  Whispers nas listas do Bard e Psychic Lance nas de Wizard/Sorcerer (→ M6b). Atenção: magia nova no magias.json **sem**
  `regua` (as marcadas compõem o vetor de referência do controle; marcar muda o nível de todo mundo). Os números de
  Ranger/Druid acima saíram com a régua deslocada; os do CI já vêm certos. Original: — ex-P2.8/P2.7: Sleep, Psychic Lance, Dissonant
  Whispers, Sleet Storm, Plant Growth, Spike Growth, Ensnaring Strike no `magias.json`; depois rever as listas do
  Druid/Cleric (mudança de régua: só entre passadas).
- [x] **M6b Listas: Dissonant Whispers (Bard), Psychic Lance (Wizard/Sorcerer)** [D] — **feito 23/11:** Bard ganha a
  linha `sussurros` (1º, sem concentração: magia extra barata); Psychic Lance no "melhor de" do Wizard/Sorcerer do 7.
  Bard Lore 7: controle do dia 4,7 → 6,0 (sussurros como extra nas 4 lutas).
- [x] **M7 Pontos de feitiçaria** [N] — **feito 23/11 (chassis):** recurso com `"converte_em_espacos": {nível: custo}`
  no livro-caixa (paga com pontos quando falta espaço; "outros" são cobrados antes, para a conversão não usar o que a
  metamagia da luta já gastou; o k da D9 conta ~1 espaço a cada 3 pontos). Chassi do Sorcerer: todos os pontos ficam
  como pontos (Flexible Casting pelo livro-caixa), as linhas continuam desenhadas com os espaços convertíveis, e a linha
  `controle-quickened` (2 pontos: magia como ação bônus + Fire Bolt). Sem premissa de reserva: a divisão entre
  metamagia e espaços é escolha do plano. O plano quase não escolhe o Quickened (ganho = truque cheio num round). Falta:
  `sor.py` (builds RPGBot) na convenção antiga; Twinned (precisa de "dois alvos na mesma concentração"), Heightened,
  Bastion of Law → M7b. Original: — ex-P2.6: metamagia (Quickened, Twinned, Heightened), Bastion of Law; hoje o
  Flexible Casting põe todos os pontos em espaços.
- [ ] **M7b Metamagia restante e sor.py** [N] — Twinned, Heightened, Bastion of Law; levar o livro-caixa de pontos às
  builds do RPGBot de Sorcerer.
- [x] **M8 Efeitos táticos de feats e truques** [N] — **feito 23/11 (parcial):** desvantagem do Vicious Mockery no
  chassi do Bard (`desvantagem_contra`, fração = rounds de truque da linha × 0,5 de falha × 0,5 dos ataques do alvo);
  Flash of Genius no chassi do Artificer 7+ (`bonus_por_uso` +Int, Int/4 usos por luta, reação). Suporte por linha sobe
  (Bard Lore 7 principal 2,5 → 3,7; Alchemist 11 dia 2,5 → 3,6); o dia do Bard Lore 7 cai (4,4 → 3,3) porque o plano
  passou a preferir controle/área + Dissonant Whispers a Greater Invisibility (troca do otimizador, olhar na
  varredura). Booming Blade, Slasher, Telekinetic, Spell-Storing Item e as builds RPGBot de Bard/Artificer → M8b.
  Original: — desvantagem do Vicious Mockery (41), Booming Blade secundário (31),
  Slasher (34), Telekinetic (30), Flash of Genius (40), Spell-Storing Item (40).
- [ ] **M8b Efeitos táticos restantes** [N] — Booming Blade secundário (31), Slasher (34), Telekinetic (30),
  Spell-Storing Item (40); levar VM/Flash of Genius ao brd.py/art.py (builds RPGBot).
- **Fora de escopo, por decisão:** mobilidade (Misty Step 63, Step of the Wind 52, Slow Fall 52, Fast Movement 32;
  eixo retirado em nov/2026) e iniciativa (Feral Instinct 62): só registrados. Ver "Eixos futuros" abaixo.

### Fechamento da passada de modelagem (23/11 tarde, CI 23e2bf7; baseline `calibracao/baseline/p3-*`)

τ por régua (misto; dentro da classe), p2b → agora: dano 0,17/0,31 → 0,17/0,28; def. física 0,47/0,47 → 0,44/0,42;
**controle 0,49/0,53 → 0,38/0,61**; **suporte 0,47 → 0,37 (nv7)**; corpo agrupado 0,49/0,27 → 0,37/0,18; área agrupada
0,59/0,64 → 0,60/0,71. Mais realismo não subiu tudo: o gabarito mede outra coisa em parte dos eixos, e o plano mudou.

Problemas moderados a grandes que restam (lista da próxima passada, ordem sugerida):
1. **Invocação domina o plano no nv7** [J/M] — Wizard, Druid, Warlock e o Aberrant Mind põem a invocação nas 4 lutas;
   o controle do plano zera e o τ de controle do Wizard nv7 cai 0,80 → 0,31 (só Graviturgy/Transmutation/Necromancy
   com controle). A invocação soma dano + corpo (inimigo esperto, D4) + área de uma vez no rendimento; a sobrevivência
   (P2.13) desconta pouco (0,875). Ver se o corpo da invocação deve entrar no rendimento do plano (ou com peso menor).
2. **Suporte do Bard nv7 −0,41 → −0,89** [M/G] — o Vicious Mockery dá o mesmo a todos os colégios e o plano do Lore
   trocou Greater Invisibility por controle + Dissonant Whispers.
3. **Corpo agrupado caindo** (M4b) — lobos do Conjure Animals, pets, invocações.
4. **Dano do Cleric nv11 0,76 → 0,38** [M] — provavelmente as extras da D9 (Spiritual Weapon) trocando a ordem dos
   domínios.
5. **Sorcerer def. física −0,82** [G] — pista do Divine Soul (dip) contra Draconic.
Ganhos: controle nv11 0,53 → 0,61; Paladin controle nv11 0,0 → 0,82; Cleric nv11 τ médio 0,33 → 0,42; Fighter e
Ranger sobem. Resíduos da passada M: M4b, M7b, M8b.

### Eixos futuros (nota do usuário, 23/11) — possíveis adições, futuro distante
Se Monks, Rogues ou conjuradores de controle com Alert aparecerem fracos, uma razão provável está aqui.
- **Iniciativa** (a mais modelável das três): de forma grosseira, a posição no primeiro turno e quantos turnos se nega
  ou quantos inimigos morrem antes de eles agirem. Suporte com iniciativa alta já buffa no turno 1; frontliner com
  iniciativa alta é barreira mais confiável (se todos os inimigos agem antes, quebram a formação). Iniciativa baixa
  custa turno: frontliner gastando Dash, druida tendo de Desengajar de posição ruim.
- **Mobilidade:** não rende todo turno, mas quando é necessária a falta dói muito. A plataforma já capta parte (ficar
  fora do perigo da linha de frente, skirmisher). Falta a liberdade: buscar alvos prioritários, atacar a retaguarda
  inimiga, sair do perigo, reposicionar, achar cobertura. Ex.: Rogue com Mobile como skirmisher. Difícil de modelar
  porque as oportunidades não surgem todo turno.
- **Utilidade:** espaços e recursos fora de combate (~20% já reservados na D9); Rogue é quem mais se beneficia. Não se
  sabe ainda o que o RPGBot diz sobre utilidade.

Depois da passada M: varredura descritiva → **treino dos parâmetros** (α, β, δ, g, típicos, pesos por eixo) contra os
gabaritos, como um treino iterativo.

## Check-up de infraestrutura (23/11, prioridade antes das passadas)

Medido:
- **Onde vai o tempo de uma build** (cProfile, Druid Moon 11, 15 linhas, 64 s com o profiler): 75% na simulação de atenção do
  corpo (`atencao.vida`: 79 mil chamadas por build; `distribui`: 1,4 milhão, com `np.mean` em vetores de 3–5 elementos).
  Quase tudo repetido: a curva da régua (20 simulações por nível × encontro × topografia) e a party de referência são
  as mesmas para toda linha e toda build. Saves: 13% (as linhas de uma build repetem os mesmos saves).
- **Por que todo push recalculava tudo:** a impressão de cada resultado inclui o hash do código do motor; qualquer mudança
  em `dh/` invalida as 1056 builds. O run do push de 22/11 já era um recálculo completo (o `--forcar` foi redundante).
- **CI:** um job só (`dh completo` com um processo por núcleo do runner), ~1h30–2h25 por recálculo completo.
- **Armazenamento:** repo no GitHub 12 MB (compactado); árvore: resultados 30 MB, site (docs) 22 MB, builds 8,7 MB, cache 3 MB.
  Cada recálculo completo recomita resultados + docs (cresce alguns MB de histórico por vez). Não é gargalo hoje: o limite
  prático do GitHub é ~1 GB; Git continua servindo como armazenamento por muitos meses.
- **Site:** `index.html` de 3 MB com o resumo de todas as builds embutido + 1056 JSONs de ~15 KB sob demanda. Pesado no
  celular na primeira carga (~300–400 KB com gzip).

Feito:
- Memo da `vida` (simulação determinística; 88% de acerto) e dos `saves` por entrada; resultados **idênticos** conferidos.
  Tempo por build ~2×: Wizard 14,7 → 7,8 s, Champion 3,5 → 1,8 s, Moon 28 → 16–19 s.
- CI em 4 jobs: `preparar` (expandir, validar, testes) → `calcular` em **8 fatias paralelas** → `juntar` (painel, site,
  commit com `pull --rebase` antes do push) → `publicar`. Esperado: recálculo completo de ~2h para ~10–20 min.

Próximos (não feitos, por ordem de ganho):
- [ ] **I1 Fonte do Pages = GitHub Actions** (Settings → Pages, só o usuário): tira o `docs/` (22 MB) dos commits.
- [ ] **I2 Impressão por módulo**: hoje mudar qualquer arquivo de `dh/` invalida tudo; dá para fazer o hash só dos
  módulos que o eixo usa (o `impressoes.py` já tem `modulos`/`_imports`: conferir por que ainda invalida tudo).
- [ ] **I3 Site:** tirar o resumo embutido do `index.html` (carregar um `resumo.json` à parte) e paginar a tabela.
- [ ] **I4 `distribui` sem NumPy** para vetores pequenos (as simulações restantes, ~10–15%).

## Efeito das decisões (23/11, CI com --forcar, commit b019703)

Baseline da passada 2 congelada em `calibracao/baseline/p2-chassi-{misto,externo,padrao}.json`.

τ por régua (dentro da classe / agrupado entre classes), passada 1 → agora:
| régua | externo nv11 | padrão nv11 | misto nv7 / nv11 (novo) |
|---|---|---|---|
| dano | 0,32 → 0,30 / 0,22 → 0,24 | 0,31 → 0,30 / **0,06 → 0,27** | 0,16 / 0,33 |
| def. física | 0,52 (igual) | 0,46 → 0,47 / −0,07 → −0,06 | 0,47 / 0,47 |
| controle | 0,34 → 0,65 | 0,25 → 0,24 (nv7 **0,49 → 0,23**) | 0,40 / 0,37 |
| suporte | 0,39 (igual) | 0,33 → 0,41 / **0,23 → 0,41** | 0,35 / 0,39 |
| área (agrup.) | 0,73 → 0,64 | 0,73 → 0,64 | 0,59 / 0,64 |
| corpo (agrup.) | 0,25 → 0,37 | 0,39 → 0,27 | 0,49 / 0,27 |

Leitura:
- **D5 deu coerência entre classes no plano:** dano agrupado no padrão 0,06 → 0,27 e suporte 0,23 → 0,41. O preço: o
  controle do plano caiu no nv7 (0,49 → 0,23; agrupado 0,43 → 0,06): com rendimento = soma simples dos níveis, as linhas
  de controle perdem para dano/invocação em várias builds → P2.15.
- **Área sem teto (D3):** Sorcerer e Wizard ~20,7–20,8 no misto (saíram do 20,0 travado); agrupado 0,73 → 0,64.
- **Corpo (D8 + D4):** máximo agora 30,6 (Artillerist), 4 chassis > 25 (antes 14 > 20 no externo, até 42,6). Warlock
  (19,0) e Wizard (18,3) subiram: a invocação perigosa atrai o inimigo esperto e o plano por rendimento a escolhe → P2.13.
- **Bard suporte segue invertido** (−0,82/−0,89): Glamour e Creation lideram; D6 corrigiu só Lore × base → P2.14 + pista [G].
- **Dano por classe ainda < 0,1:** Wizard −0,36, Warlock −0,25, Monk −0,20, Rogue/Ranger (nv7). Wizard/Warlock = invocação
  (P2.13); marciais = P2.12.
- **τ médio por classe** piorou no Sorcerer (nv7 0,16 → −0,46, padrão) e no Rogue (−0,25 → −0,47): olhar na varredura da
  passada 2 (provável efeito da D5 escolhendo linhas diferentes).

## Efeito de D9 + P2.15 + P2.13 (23/11 madrugada, CI em fatias, 10 min)

τ por régua dentro da classe, baseline p2 → agora (misto | padrão):
- **controle** nv7 0,40 → 0,49 | 0,23 → 0,40; nv11 0,37 → 0,53 | 0,24 → **0,51** (a normalização da P2.15 devolveu o
  controle ao plano; agrupado no padrão nv7 0,06 → 0,20).
- **suporte** nv7 0,35 → 0,47 | 0,36 → 0,47; nv11 0,39 → **0,26** | 0,41 → 0,26 (piora: Cleric nv11 vai a 0,0 → P2.18).
- **dano** ≈ igual (0,17/0,31 | 0,20/0,32); def. física igual.
- Bard suporte −0,82 → −0,41; τ médio Bard nv11 0,17 → 0,59/0,68, Paladin nv11 0,31 → 0,65, Cleric nv11 0,0 → 0,32.
- Wizard piora (τ médio nv11 0,0 → −0,21; dano −0,36): segue sendo invocação comum + linhas todas com concentração
  (P2.16) — é a próxima frente do Wizard.

## Passada 2
(problemas novos achados durante a passada 1)

- [ ] **P2.5 Ruído do Monte Carlo** [M] — antes do P1.5 o campo variava ±0,4–0,8 nível só pela ordem das fontes; com os
  números comuns a comparação entre builds fica justa, mas o valor absoluto ainda depende da semente. Medir o ruído
  (sementes 11/12/13 num punhado de builds) e decidir se N=8000 basta.

- [x] **P2.6 Pontos de feitiçaria** [M] — **movida para a passada de modelagem (M7).** — Flexible Casting põe todos os pontos em espaços; metamagia (Quickened/Twinned),
  Bastion of Law (Clockwork) e afins sem mecânica. O dano e a defesa do Sorcerer não têm onde aparecer.
- [x] **P2.7 Listas das réguas de controle** [M/J] — **movida para a passada de modelagem (M6).** — Druid (Entangle, Hold Person, Polymorph) e Cleric (Hold Person,
  Banishment) têm listas fracas perto da do Wizard/Bard; Sleet Storm, Plant Growth e Spike Growth nem existem no
  `magias.json`. Acrescentar as magias é mecânica; mudar a lista da régua comum é decisão de régua (fazer entre passadas).
- [x] **P2.8 Magias de controle faltando no `magias.json`** [M] — **movida para a passada de modelagem (M6).** — Sleep, Psychic Lance, Dissonant Whispers, Sleet Storm,
  Plant Growth, Spike Growth (Whispers, Druid, Bard base).
- [ ] **P2.9 Aura of Conquest: velocidade 0 do amedrontado** [M] — hoje só o dano psíquico entra.
- [x] **P2.10 Corpo > 20 em 14 chassis** [J → D8] — **fechada 23/11:** resolvida pela D8 (máx. 30,6; 4 > 25). — ver o fechamento da passada 1.
- [x] **P2.11 Ranger sem controle nem suporte** [M] — **movida para a passada de modelagem (M2).** — 0,0 em todas as subclasses; Ensnaring Strike, Spike Growth e
  Conjure Animals fora da régua (junto com a P2.7/P2.8).
- [ ] **P2.12 Dano dos marciais no nv7** [M] — ex-P1.14: Monk −0,16, Ranger −0,19, Rogue −0,30, Fighter 0,07.
- [x] **P2.13 Invocação: dano × corpo com o mesmo PV** [M/J] — **feito 23/11:** o dano das invocações é multiplicado
  pela fração da luta em que elas estão vivas (`total.sobrevivencia_inv`: mesma simulação de alvo do corpo, no nível da
  build; resultado em `dano.sobrevivencia_invocacao`). Nível 7: 0,875 (caem no último round), dano −0,4; Necromancy 1,0.
  Original: — com a D4 o inimigo esperto bate na invocação quando a
  ameaça por PV dela é maior (Summon Aberration ≈ 0,4 × conjurador ≈ 0,2), e o corpo sobe (Necromancy 19,8 → 26,4,
  Artillerist 29,3 → 32,4; Moon 31,9 → 27,2). Mas o eixo de dano conta a invocação viva a luta inteira: o PV dela é gasto
  duas vezes. Descontar do dano da invocação a fração da luta em que ela já morreu (a `vida()` da atenção já sabe
  quando o PV dela zera).
- [ ] **P2.14 Mantle of Inspiration e outras fontes de ação bônus** [M] — o fator de ação bônus da D6 só vale no
  `dado_multiuso`; o Mantle (Glamour), que também gasta a ação bônus e um uso de BI, não paga.
- [x] **P2.15 Controle some do plano com a D5** [M/J] — **feito 23/11:** valor da linha = Σ nível ÷ nível típico do eixo
  no nível da build (`plano.auto.tipico` = percentil 75 das linhas que fazem o eixo; `calibracao/tipico_eixos.py
  --gravar`; a mediana caía no Healing Word de toda linha de conjurador). Original: — rendimento = soma simples dos níveis eq.; no nv7 o controle do
  plano cai (τ 0,49 → 0,23, agrupado 0,43 → 0,06). Ver se é a escala do controle (níveis menores que os de dano na mesma
  build) ou peso por eixo (`plano.auto.peso_eixo`); depende da calibração entre réguas.
- [x] **P2.16 Linhas sem concentração nos chassis de conjurador** [M] — **movida para a passada de modelagem (M5).** — para a D9 render, Wizard/Druid/Sorcerer precisam
  de linhas de blaster puro (Fireball, Lightning Bolt) e de buff/cura sem concentração; hoje toda linha deles tem uma.
- [x] **P2.17 Concentração não declarada nas entradas de área/suporte** [M] — **movida para a passada de modelagem (M5).** — Spirit Guardians, Wall of Fire, Bless etc.
  não declaram `concentracao`; o plano reconhece pelo nome, mas o `dh validar` não vê duas concentrações numa linha só.
  Declarar nos geradores e ligar a checagem no validador.
- [ ] **P2.18 Suporte do Cleric no nv11 sem ordem** [M] — depois da D9 o τ de suporte do Cleric no 11 foi a 0,0 (as
  extras `preservar`/`bless` entram em quase todos os domínios e igualam a classe). Ver se a pista ou a régua.
- [x] **P2.1 Invocação domina o dano externo** [J → D7] — **fechada 23/11:** D7 fechada pela D2 + D5; a parte de
  mecânica foi a P2.13; o que sobra no Wizard é a P2.16. — Summon Aberration (9,4 no 11) é o máximo de dano de todos os
  Warlocks no anel externo e iguala a classe; provavelmente o mesmo no Wizard (P1.5) e nos outros conjuradores com summon.
  Conferir o dano da invocação e se ela devia entrar no eixo dano do personagem (ou num eixo/rótulo à parte).
- [x] **P2.2 Linhas grátis empatam no plano auto** [M] — **fechada 23/11:** resolvida pela D5 (rendimento). — sem gasto, `principal` e `eb` empatam e ganha a mais antiga
  (desempate por eixos declarados / menos trocas). Depende da D5.
- [ ] **P2.3 Pista de dano que é área** [G] — Fiend "alto (blaster de fogo, Fireball)": rever pistas de dano que falam de
  magia de área, em todas as classes.
- [ ] **P2.4 Pista de suporte que é controle** [G] — Eloquence "suporte alto" inclui Unsettling Words (no controle por design).

## Decisões (para o usuário)

### Respostas do usuário (23/11) e o que vira tarefa
Ordem de execução: D8 → D3 → D5 → D2 → D4 → D6 → D9 → D1 (D7 fechada pela D2 + D5).
- **D1 → mistura ponderada das rampas** bruta/precisa, peso como premissa treinável. **Feito 23/11:**
  nível = β·bruta + (1 − β)·precisa, β = `dano.peso_rampa_bruta` = 0,5. Champion + GWM: +1,1 → +0,5 nível; Berserker +
  GWM continua ≈ 0 (o +1 de For que o feat custa pesa nas CAs altas tanto quanto o −5/+10 ajuda na CA 16; β maior
  favorece o GWM: o treino decide). Paridade com as planilhas da DragonHeist atualizada (John 9,4 → 9,2, Kael 7,3 →
  7,2, Abdul 5,6 → 5,5, Lucius 20,0 → 18,6, Amadeus 11,8 → 10,7); as planilhas em si não foram reescritas.
- **D2 → mistura plano × externo**: valor = plano + α·(externo − plano), α global = 0,2 (premissa treinável; α por eixo só
  se o treino mostrar padrão por eixo). **Feito 23/11:** anel `misto` (`aneis.alfa_versatilidade`), visão padrão do
  `comparar_chassi` e do `diff_baseline`. Razão: o plano é o que a build faz com o combustível de um dia; o externo conta
  "três Wizards"; a versatilidade vale algo, mas a munição é a mesma; marciais quase não ganham nada com α.
- **D3 → sem teto na área** (consistência interna antes da escala). **Feito 23/11:** acima do 20, nível = 20 +
  ln(fr20/ref20)/ln(g), g = `area.crescimento_por_nivel` = 1,12 (a margem pode ficar plana entre 11 e 20 e a raiz de
  uma reta explodia: combo do Evocation ia a 34,5; agora 22,2; área 21,4; Sorcerer Draconic 21,0).
- **D4 → inimigo esperto**: invocação/torreta entra no corpo, mas o inimigo só bate nela quando eliminá-la rende mais
  (dano evitado por golpe) do que bater no conjurador/tanque. Trabalho em equipe (tanque segurando) fica para a análise
  de party. **Feito 23/11:** na escolha de alvo, a parcela maliciosa pesa a invocação pela ameaça por PV (DPR/PV, com o
  DPR dela na CA 15, campo `inv_dpr`), como os membros; a não maliciosa a trata como mais um corpo na frente
  (`skel_peso` 1,5 → 1,0). Efeito: invocação perigosa sobe, saco de PV inofensivo desce. Falta o custo → P2.13.
- **D5 → rendimento**: o plano auto maximiza o rendimento respeitando o orçamento (gasto ≤ recursos), não o gasto.
  **Feito 23/11:** o motor reescolhe os planos `auto` depois de calcular as linhas (rendimento = Σ peso do combate × valor
  da linha; valor = níveis eq. dos eixos × `plano.auto.peso_eixo`, todos 1); gasto vira desempate. Hexblade: dano do dia
  2,5 → 7,9.
- **D6 → BI cobra a ação bônus**; usos do dado com retorno decrescente na luta (decaimento treinável); Cutting Words é
  opção extra (nunca piora a build); rever se o BI está superestimado. **Feito 23/11:** `dado_multiuso` vale
  (1 − δ^u)/(1 − δ) usos (δ = `suporte.dado_multiuso.decaimento` = 0,75) × 0,85 se for por ação bônus
  (`fator_acao_bonus`); Cutting Words com `acao: reacao`. Suporte nv11 (1ª linha): Lore 4,7 > Valor 4,5 (antes Lore <
  base); Creation 6,1 e Glamour 6,2 seguem no topo (Mote of Potential soma ao BI; Mantle = 3 × 11 PV temp.; a pista
  "médio" deles pode ser [G]). O Mantle também é ação bônus e não paga o fator: → P2.14.
- **D7 → fechada pela D2 + D5** (reabrir se o τ de dano do Wizard seguir negativo depois delas).
- **D8 → sem teto no corpo**, prioridade consistência. **Feito 23/11:** a extrapolação acima do 20 usava só os 2 últimos
  pontos da busca (T oscila com os CRs discretos); agora é a regressão da busca inteira (`controle.corpo.extrap_pontos`
  = 0). Infiltrator 31,5 → 25,7 (pico 42,6 → 29,8); delta do feat −8,6 → −4,1 níveis; AG 25,3 → 25,6.
- **D10 (nova, a confirmar) → extra soma só o ganho por eixo** (M5, 23/11): implementado como acima; alternativa seria
  contar a perda (o Fireball tira rounds de truque também contra o chefe), o que derrubava o dano do Wizard 11 de 7,9
  para 5,0.
- **D9 → premissa de magias por luta por nível** — **Feito 23/11** (proposta aprovada, com um ajuste): até k linhas
  por luta, k = espaços do dia × (1 − 0,2) / combates (`planos.magias_por_luta`, entre 1 e os rounds da luta;
  sobrescrevível com `"magias_por_luta"` na build). **Ajuste:** em vez de "rounds divididos igualmente" (média das
  linhas: nunca supera a melhor linha sozinha, então o plano nunca escolheria duas magias), valor e gasto da luta =
  linha 1 + Σ (extra − principal), o ganho marginal de trocar rounds de truque pela magia extra. Escolha gulosa sobre o
  melhor plano de uma linha; sem repetir peça (ataque, fonte, área, invocação ou parte do nome) e no máximo uma
  concentração por luta (declarada, de controle ou reconhecida pelo nome: `_concentracao_nomes` no magias.json).
  Ex.: Cleric Life 11 = bless+arma + preservar; Paladin Vengeance 11 = haste+smite + voto. Wizard/Druid quase não
  ganham extras: todas as linhas deles têm concentração → P2.16.
- **D9 (texto original) → premissa de magias por luta por nível** (derivada dos espaços, ~20% para utilidade), com ajuste por build
  (blaster gasta mais). Eixo de utilidade: só nota de rodapé por enquanto. **Proposta (a confirmar):** em vez de
  reescrever as linhas, o plano do dia passa a ter até k linhas por luta (linha principal + secundárias, com os rounds
  divididos), k = `orcamento.magias_por_luta[tipo][nível]` = espaços × (1 − 0,2 utilidade) / lutas do dia, e a build
  pode sobrescrever (`"magias_por_luta": 3` num blaster). O rendimento (D5) e o livro-caixa já sabem somar linhas; muda
  o agregador do dia (média ponderada pelos rounds de cada linha).

### Texto original das decisões

- **D1 GWM/Sharpshooter e as rampas** — o nível eq. de dano é o máximo entre a rampa bruta e a precisa. Um feat que troca
  acerto por dano faz a build trocar de perfil e chegar no mesmo nível (Berserker 11: 11,0 com e sem GWM, apesar de +5 de
  DPR na CA 16). (a) manter o máximo; (b) mistura ponderada das rampas, com o peso como premissa treinável.
- **D2 Visão do teste de régua** — testar cada régua no anel externo (potencial do eixo) e o plano do dia à parte, ou no
  padrão (o plano mistura eixos; ver P1.13)?
- **D3 Teto da área** (ver P1.12) — subir o teto, mudar a escala ou aceitar a saturação no 11.
- **D5 Plano automático só olha gasto** — `plano_auto` escolhe a combinação que gasta mais recurso, sem olhar rendimento;
  linhas grátis empatam e linhas de controle/combo (que gastam mais) tomam as lutas prioritárias. Isso derruba o dano do dia
  de quem tem opções (Hexblade 2,5 padrão × 9,3 externo) e torna os eixos do padrão ruidosos. Opções: (a) manter;
  (b) desempatar por rendimento (precisa de um valor da linha = pesos dos eixos, premissa treinável); (c) gasto primeiro,
  rendimento como 2º critério.
- **D6 Custo de ação do Bardic Inspiration** — BI entregue custa ação bônus (compete com Healing Word, Spiritual Weapon…);
  Cutting Words é reação e vê a rolagem. Hoje o motor não cobra nenhum dos dois e o Cutting Words vale menos que o BI
  comum (mix só "ca"). Cobrar a ação bônus do BI? Dar ao Cutting Words um ESCOLHA maior?
- **D7 Anel externo esconde a subclasse** — o externo pega o máximo de cada eixo; quando a linha mais forte é da régua
  comum (Summon Aberration no Wizard/Warlock), toda a classe empata e o τ da régua mede só ruído. Opções: (a) testar as
  réguas por subclasse no anel interno (à vontade) + o externo à parte; (b) marcar linhas de invocação e medir o dano do
  personagem sem elas (invocação como contribuição separada); (c) aceitar.
- **D8 Corpo acima do nível 20** (ver P1.10) — o corpo extrapola pela inclinação final e explode (31,5 num atirador de
  placas). (a) teto em 20 como os outros eixos; (b) compressão acima de 20 (ex.: 20 + log); (c) manter.
- **D9 Uma magia por luta** (ver P1.11) — as linhas de conjurador gastam uma magia (+ Healing Word) por luta; no 11 sobram
  os espaços médios. (a) manter (hipótese conservadora); (b) linhas com 2 magias por luta (controle + área/buff) para os
  conjuradores plenos; (c) uma premissa "magias por luta" por nível.
- **D4 Corpo de invocações** (ver P1.9) — invocação/torreta conta como presença do personagem? Com que peso?

### Decisões abertas pela passada 3 (24/11)
- **D11 Steady Aim: fração dos turnos** — hoje os atiradores do Rogue têm vantagem em 100% dos turnos (não se mexer é
  quase sempre possível de longe). (a) manter 1,0; (b) premissa `rogue.steady_aim.fracao` (ex.: 0,75: um turno por luta
  gasto em reposicionar); (c) tratar como mobilidade (eixo futuro) e aceitar o resíduo. Efeito medido com 0,75: Rogue
  nv7 −0,22 → −0,11.
- **D12 Pico do 1º round na régua de dano** — (a) manter média de 4 rounds; (b) premissa de peso do 1º round (ex.: 1,5:
  quem age primeiro mata antes); (c) deixar para o eixo de iniciativa (futuro). Afeta Gloom Stalker, Assassin, Grave.
- **D13 Redirecionar dano para si** (Aura of the Guardian, Divine Allegiance, Protective Bond; P3.5) — onde conta?
  (a) no corpo: o personagem vira o corpo que absorve uma fração do dano mirado nos aliados (campo genérico
  `atencao.redireciona`: fração por round, limitada pela reação); (b) no suporte defensivo, como dano evitado nos
  aliados (só que o dano não some, muda de alvo); (c) não modelar agora e aceitar o corpo abaixo do gate.

### Respostas do usuário (24/11, 01h) para D11–D13 e o que foi feito
- **D11 → uma chance global de vantagem do atirador (~0,75–0,85), treinável, ajustável por subclasse.** Hide e Steady
  Aim se cobrem (não é produto: as fontes não são independentes); turno 1 costuma ser de posicionamento; Rogue de corpo
  a corpo quase nunca tem Steady Aim. **Feito:** premissa `rogue.vantagem.atirador` = 0,8 (antes 1,0 fixo);
  `rogue.vantagem.ajuste_scout` = +0,1 (Skirmisher anda na reação, fora do turno); Assassin = {"ou": [atirador,
  Assassinate no round 1]}; Sneak = {"ou": [vantagem, aliado adjacente 0,75]}. Mecanismo genérico novo em `dano.prob`:
  número, {"ou": […]} ou {"soma": […]}, com premissas via {"$p"}. Skirmishers (Swashbuckler, Arcane Trickster) sem
  Steady Aim, como antes. Arcane Trickster: a vantagem do Mage Hand (Versatile Trickster) é do nível 13 no 2014, fora
  dos níveis 7/11. Efeito (local): Rogue nv7 −0,22 → +0,17, nv11 +0,07 → +0,33; dano global nv7 0,18 → 0,23, nv11
  0,28 → **0,31**.
- **D13 → puxar dano de um aliado entra no corpo, como um taunt forte (só vale se aguentar).** **Feito:** campo genérico
  `controle.atencao.redireciona` (fração dos turnos inimigos contra os aliados que passa para a build, em
  `atencao.distribui`); premissas `controle.atencao.redireciona.aura` = 0,25 (Aura of the Guardian, Protective Bond) e
  `.adjacente` = 0,15 (Divine Allegiance); aplicado por `patches_linhas` (via `m3_sobrevivencia.py`, que agora mescla
  sub-dicts). Corpo nv11: Redemption 11,0 → 13,0; Crown 11,0 → 11,1; Peace 10,8 → 10,1 (Cleric com menos CA/PV paga o
  dano que puxa: o efeito pedido). Corpo agrupado nv11 0,18 → 0,25, nv7 0,37 → 0,33.
- **D12 → peso extra no 1º round, moderado.** **Feito:** premissa `dano.peso_round1` = 1,25 (rounds pesam [w, 1, 1, 1],
  normalizados: dano constante não muda). Vale para ataques marcados `round1` (Dread Ambusher) e para o dano por luta
  (smites e afins, gastos nos primeiros acertos: 1 uso ×1,18, 2 usos ×1,06, 4+ usos ×1,0). O DPR mostrado continua
  puro (conferência com as planilhas intacta); o nível usa `dpr_regua`. Efeito: depois do CI.
