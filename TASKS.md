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
- [ ] **P1.14 τ de dano levemente negativo** [M] — **adiada para a passada 2** (pequena; depende de D5/D7). Original: — Monk (−0,16/0,0), Ranger (−0,19), Rogue (−0,30 externo nv7). Pequenos,
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

## Passada 2
(problemas novos achados durante a passada 1)

- [ ] **P2.5 Ruído do Monte Carlo** [M] — antes do P1.5 o campo variava ±0,4–0,8 nível só pela ordem das fontes; com os
  números comuns a comparação entre builds fica justa, mas o valor absoluto ainda depende da semente. Medir o ruído
  (sementes 11/12/13 num punhado de builds) e decidir se N=8000 basta.

- [ ] **P2.6 Pontos de feitiçaria** [M] — Flexible Casting põe todos os pontos em espaços; metamagia (Quickened/Twinned),
  Bastion of Law (Clockwork) e afins sem mecânica. O dano e a defesa do Sorcerer não têm onde aparecer.
- [ ] **P2.7 Listas das réguas de controle** [M/J] — Druid (Entangle, Hold Person, Polymorph) e Cleric (Hold Person,
  Banishment) têm listas fracas perto da do Wizard/Bard; Sleet Storm, Plant Growth e Spike Growth nem existem no
  `magias.json`. Acrescentar as magias é mecânica; mudar a lista da régua comum é decisão de régua (fazer entre passadas).
- [ ] **P2.8 Magias de controle faltando no `magias.json`** [M] — Sleep, Psychic Lance, Dissonant Whispers, Sleet Storm,
  Plant Growth, Spike Growth (Whispers, Druid, Bard base).
- [ ] **P2.9 Aura of Conquest: velocidade 0 do amedrontado** [M] — hoje só o dano psíquico entra.
- [ ] **P2.10 Corpo > 20 em 14 chassis** [J → D8] — ver o fechamento da passada 1.
- [ ] **P2.11 Ranger sem controle nem suporte** [M] — 0,0 em todas as subclasses; Ensnaring Strike, Spike Growth e
  Conjure Animals fora da régua (junto com a P2.7/P2.8).
- [ ] **P2.12 Dano dos marciais no nv7** [M] — ex-P1.14: Monk −0,16, Ranger −0,19, Rogue −0,30, Fighter 0,07.
- [ ] **P2.13 Invocação: dano × corpo com o mesmo PV** [M/J] — com a D4 o inimigo esperto bate na invocação quando a
  ameaça por PV dela é maior (Summon Aberration ≈ 0,4 × conjurador ≈ 0,2), e o corpo sobe (Necromancy 19,8 → 26,4,
  Artillerist 29,3 → 32,4; Moon 31,9 → 27,2). Mas o eixo de dano conta a invocação viva a luta inteira: o PV dela é gasto
  duas vezes. Descontar do dano da invocação a fração da luta em que ela já morreu (a `vida()` da atenção já sabe
  quando o PV dela zera).
- [ ] **P2.14 Mantle of Inspiration e outras fontes de ação bônus** [M] — o fator de ação bônus da D6 só vale no
  `dado_multiuso`; o Mantle (Glamour), que também gasta a ação bônus e um uso de BI, não paga.
- [ ] **P2.1 Invocação domina o dano externo** [J → D7] — Summon Aberration (9,4 no 11) é o máximo de dano de todos os
  Warlocks no anel externo e iguala a classe; provavelmente o mesmo no Wizard (P1.5) e nos outros conjuradores com summon.
  Conferir o dano da invocação e se ela devia entrar no eixo dano do personagem (ou num eixo/rótulo à parte).
- [ ] **P2.2 Linhas grátis empatam no plano auto** [M] — sem gasto, `principal` e `eb` empatam e ganha a mais antiga
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
- **D9 → premissa de magias por luta por nível** (derivada dos espaços, ~20% para utilidade), com ajuste por build
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
