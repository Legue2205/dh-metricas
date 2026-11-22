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

- [ ] **P1.1 Warlock — dano** [M] — τ dano −0,60 (nv11, padrão). Hexblade (striker, pista "alto") tem o pior dano da
  classe: 2,5 no padrão, 7,9 no externo; a linha corpo a corpo `principal` dá só 4,5 no 11. O plano auto põe `combo`
  (1,8 de dano) nas lutas prioritárias. Fiend (pista "alto") 3,9 < base 5,2. Conferir Hexblade's Curse, arma do pacto,
  Thirsting Blade e se o plano está escolhendo controle onde o dano deveria vencer.
- [ ] **P1.2 Warlock — controle** [M] — no externo nv7, τ controle −1,0; no padrão nv11 Hexblade/Fiend/Genie = 7,4,
  os outros todos = 2,3 (dois valores para 9 patronos). Great Old One (pista "alto") fica no 2,3.
- [ ] **P1.3 Bard — suporte invertido** [M/G] — τ −0,89/−0,82: Eloquence e Lore (pista "alto") 7,2/7,0 abaixo de
  Creation e Glamour ("médio") 8,6/8,4. Conferir Unsettling Words, Cutting Words (defensivo), Mantle of Inspiration
  (PV temporários possivelmente inflados), Performance of Creation; e se Eloquence/Lore deviam mesmo ser "alto" em suporte.
- [ ] **P1.4 Bard — dano/controle planos** [M] — 8 colégios com dano 0,6 idêntico e controle 3,3 idêntico (exceto
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

## Decisões (para o usuário)

- **D1 GWM/Sharpshooter e as rampas** — o nível eq. de dano é o máximo entre a rampa bruta e a precisa. Um feat que troca
  acerto por dano faz a build trocar de perfil e chegar no mesmo nível (Berserker 11: 11,0 com e sem GWM, apesar de +5 de
  DPR na CA 16). (a) manter o máximo; (b) mistura ponderada das rampas, com o peso como premissa treinável.
- **D2 Visão do teste de régua** — testar cada régua no anel externo (potencial do eixo) e o plano do dia à parte, ou no
  padrão (o plano mistura eixos; ver P1.13)?
- **D3 Teto da área** (ver P1.12) — subir o teto, mudar a escala ou aceitar a saturação no 11.
- **D4 Corpo de invocações** (ver P1.9) — invocação/torreta conta como presença do personagem? Com que peso?
