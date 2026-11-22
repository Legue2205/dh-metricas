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
- [ ] **P1.5 Wizard — controle e dano** [M] — τ controle −0,60 e dano −0,60 (nv11, externo). Dano externo do Wizard
  (10,8) passa o do Fighter (9,4): ver qual linha dá esse pico (invocação? área contando em alvo único?).
- [ ] **P1.6 Sorcerer — def. física** [M] — τ −0,5 nos dois níveis: Draconic (Draconic Resilience) devia liderar.
  Nos originais, dano do Sorcerer 0,8/1,0 (o menor junto do Bard) mesmo com Fire Bolt.
- [ ] **P1.7 Cleric — controle e dano** [M] — originais nv7: controle 0,0 em todos (checagem "clérigos ≥ fighters" falha);
  chassi externo nv11 controle 3,4 com Hold Person/Banishment, contra Artificer 8,2 só com Web. τ dano nv7 −0,38.
- [ ] **P1.8 Controle entre classes** [M] — mesmas magias, valores muito diferentes: Druid 3,6 (Entangle/Hold
  Person/Polymorph) e Cleric 3,4 contra Artificer 8,2, Warlock 9,1, Bard 9,0 (externo nv11). Pode ser o mesmo bug da P1.7.
- [ ] **P1.9 Corpo de invocações/torreta** [M/J] — Artificer corpo 28,8 (Artillerist 28,7, o maior de todos, acima do
  Ancestral Guardian 26,8) e Druid 24,3 (Shepherd 24,7). Ver se torreta/invocação está contando como presença do
  personagem, e quanto deveria contar (pode virar decisão).
- [ ] **P1.10 Sensibilidade do corpo/defesa a 1 ponto de atributo** [M] — no 11, trocar um ASI por feat derruba o corpo
  em −3 a −7,5 níveis (Armorer Infiltrator + Skill Expert: −7,5; Alchemist + Fey Touched: −5,8). Ver se é o PV/CA
  mesmo ou um degrau da rampa.
- [ ] **P1.11 Sobra de recursos dos conjuradores** [M/J] — originais nv11: Bard Whispers sobra 47 níveis de espaço;
  Cleric 25, Druid 28, Wizard 21 em média. O plano auto gasta pouco e subavalia conjuradores no padrão.
- [ ] **P1.12 Área no teto** [M/J] — Wizard e Sorcerer médios no 20,0 (teto) no externo nv11; Light e Necromancy no 20
  já nos originais. A régua satura e não separa. Retaguarda 14 × marciais 5–8: conferir se é real.
- [ ] **P1.13 Dano no padrão colapsa por troca de linha** [J] — estrutural: o plano escolhe linhas de controle/combo nas
  lutas prioritárias, e o dano do dia de quem tem opções cai (Hexblade 2,5 × 7,9 externo). Ligado à Decisão D2.
- [ ] **P1.14 τ de dano levemente negativo** [M] — Monk (−0,16/0,0), Ranger (−0,19), Rogue (−0,30 externo nv7). Pequenos,
  conferir depois dos maiores.
- [ ] **P1.15 Variância zero** [M] — Paladin controle τ 0,0 e Fighter suporte 0,0: provavelmente todos iguais (só uma
  subclasse com valor). Confirmar se é falta de mecânica (Paladin: Conquest/Fear, Ancients/Nature's Wrath).

## Passada 2
(problemas novos achados durante a passada 1)

- [ ] **P2.1 Invocação domina o dano externo** [M/J] — Summon Aberration (9,4 no 11) é o máximo de dano de todos os
  Warlocks no anel externo e iguala a classe; provavelmente o mesmo no Wizard (P1.5) e nos outros conjuradores com summon.
  Conferir o dano da invocação e se ela devia entrar no eixo dano do personagem (ou num eixo/rótulo à parte).
- [ ] **P2.2 Linhas grátis empatam no plano auto** [M] — sem gasto, `principal` e `eb` empatam e ganha a mais antiga
  (desempate por eixos declarados / menos trocas). Depende da D5.
- [ ] **P2.3 Pista de dano que é área** [G] — Fiend "alto (blaster de fogo, Fireball)": rever pistas de dano que falam de
  magia de área, em todas as classes.
- [ ] **P2.4 Pista de suporte que é controle** [G] — Eloquence "suporte alto" inclui Unsettling Words (no controle por design).

## Decisões (para o usuário)

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
- **D4 Corpo de invocações** (ver P1.9) — invocação/torreta conta como presença do personagem? Com que peso?
