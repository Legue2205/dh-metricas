# Convenções da passada 1 (ler ANTES de cada lote; não mudar no meio da passada)

Regra: só entra no cálculo o que tem tipo genérico no motor. O resto vai para `descricao.nao_modelado`, igual para
todas as builds (nem mais duro com build "fraca", nem mais generoso com build "forte").

## Ficha
- PV: d10 → 10 + Con no 1º, 6 + Con por nível (média arredondada para cima); idem por dado da classe.
- Proficiência pela tabela; saves proficientes da classe. Itens mágicos: nenhum (salvo se o guia depender).
- CA pela armadura que o guia diz usar naquele nível (compra de placas quando o guia disser).
- Fatias: 3, 5, 7, 9, 11. Escolhas de nível par (feat/ASI) entram na fatia seguinte.

## Dano
- Action Surge: linha `surge` (1 por descanso curto), ataques extras = ataques de uma ação ÷ 4 rounds; plano automático.
- Recurso por descanso curto em combate: ÷ 2 lutas (ex.: 4 dados de superioridade = 2 por luta).
- Recurso por dia: ÷ 4 lutas.
- Piercer: rerrolagem = ganho esperado de rerrolar o dado se ≤ metade (d6 +0,75, d8 +1, d10 +1,25, d12 +1,5),
  `por_turno`; dado extra no crítico com `"gatilho": "critico"`.
- Great Weapon Fighting: 2d6 → +1,33; 1d12 → +0,83; 1d10 → +0,8 (constante somada ao dano).
- Efeito que depende de o inimigo se mover (Booming Blade secundário): não contado.
- Vantagem só com fonte mecânica própria e frequência sem julgamento (ex.: Curving Shot = vantagem em 1 ataque por
  turno). Vantagem de Inspiração, montaria contra criatura menor, condição causada por save: não contada.
- Elven Accuracy marcado (`elven_accuracy`) mas só vale onde houver vantagem.
- Bônus de manobra/Arcane Shot somado no acerto: `por_luta` com os usos por luta.

## Defesa / saves
- Shield: reação com `usos_luta: 1` e `gasta` 1 espaço de 1º; linha `sem-shield` para o plano automático.
- Indomitable, Second Wind, Absorb Elements: não modelados por enquanto (lista na descrição).

## Controle
- Atenção: `papel` (striker, atirador, tank), `soft` 0,15, `dpr: "auto"`.
- Fontes só com tipo existente: `ameaca` (todo marcial corpo a corpo), `sentinela` (Hold the Line, Sentinel),
  magias de `magias.json`. Manobras, flechas e condições sem tipo: não modeladas.

## Área
- Alvos pela tabela de áreas da DMG (cone/linha/esfera); "todos a 5 pés" = [1, 2, 3] (como o Thunderclap).

## Acrescentado no lote 2 (casos novos; não muda nada do lote 1)
- Multiclasse: as fatias são por **nível de personagem** (Echo Knight F6/Bb1 no 7; PDK F4/Wl1 no 5).
- Recurso que se **ativa por luta** (fúria, Giant's Might, Fighting Spirit, Breath Weapon, Hill Rune): linha própria
  com `gasta`, e o plano automático escolhe as lutas. Recurso gasto **golpe a golpe** (dados psiônicos, Unleash
  Incarnation, Astral Spark): espalhado pelo dia (`usos_dia` ou n fracionário ÷ 4 lutas ÷ 4 rounds).
- Uma ativação de 1 turno (Fighting Spirit) = vantagem 0,25 nos ataques da luta.
- Sentinel / Hold the Line: fonte `sentinela` + ataque de oportunidade n 0,5 no dano + reação 0,5 (dano e controle).
- PV temporários próprios (Fighting Spirit, Form of Dread): não modelados, como o Second Wind.
- Reckless Attack: vantagem 1,0 nos ataques de For e `adv: 1` contra ele (RAW, sem desviar golpes para o eco).
- Fúria: `defesa.resist` e +2 no dano; Hill Rune: `defesa.resist`.
- Hex (1 hora): 1 espaço cobre ~2 lutas → `gasta` 0,5 espaço de 1º por luta.
- Cone: alvos = comprimento ÷ 10, arredondado para cima (15 pés = 2).
- Agarrão: fonte `agarrao` com o bônus de Atletismo; agarrar com a ação custa 1 ataque no 1º round (n − 0,25).

# Passada 2 (19/11, decidida depois da comparação da passada 1 do Fighter)
- **Condição no acerto** (tipo `condicao_no_acerto`): manobras, runas, flechas e empurrões que impõem save e condição
  entram no controle, com os mesmos usos por luta que o recurso já tem (o mesmo uso pode somar dano e controle,
  porque é um só efeito). Efeitos na biblioteca (`magias.json`, prefixo `cond_`): amedrontado 0,4; derrubado 0,25
  (um turno); impedido 0,5; cego (um turno) 0,5; banido (um turno) 1; incapacitado 1.
- Reação sem ataque (Stone Rune): `"no_acerto": false`.
- Marca no acerto com desvantagem contra outros (Unwavering Mark): tipo `ancestral_protectors`.
- **Curving Shot** sai do dano e vai para a Área: `cleave_ataque` com `"p": "erro"` (gatilho = errar ≥ 1 dos
  `n_erro` ataques do turno, contra a CA da horda), como um Horde Breaker.

# Conjuradores (a partir do Wizard, 19/11)
- Linhas padrão: `principal` (só truques), `controle` (melhor_de das magias de controle disponíveis, gasta o maior
  espaço da lista), `controle-barato` (a opção mais barata), `area` (1 magia de área), `combo` (controle + área, truque
  em 2 rounds), `invocacao` (Summon de Tasha no maior espaço; 1 hora = 0,5 espaço por luta). O plano automático escolhe.
- Truque nos rounds livres: 1 (principal), 0,75 (lançou 1 magia), 0,5 (lançou 2). Toll the Dead com d12 (alvo ferido).
- Shield: 1 por luta nas linhas que gastam espaço (gasta 1º). Mage Armor: 1 espaço de 1º por dia fora do pool.
- Arcane Recovery: ceil(nível de Wizard ÷ 2) em espaços, no maior possível (até 5º), somado ao pool do dia.
- Multiclasse conjuradora: espaços pelo nível de conjurador (Artificer 1 conta 1), Arcane Recovery pelo nível de Wizard.
- Magias fora da biblioteca de controle: não modeladas (lista na descrição). Adicionadas antes da passada:
  phantasmal_force 0,75, earthen_grasp 0,5 (escape), phantasmal_killer 0,4, cond_hipnotizado 1 (luta),
  cond_estase 1 (um turno). Psychic Lance via `condicao_no_acerto` (`no_acerto: false`). Slow só em alvo único (não usado).
- Área (DMG): Fireball 4 alvos, Shatter 2, Cone de 30 pés 3, Cone de 60 pés 6, linha de 100 pés 4, Chain Lightning 4.
- Arcane Ward somado ao PV; esqueletos (Undead Thralls) como invocação permanente com upkeep de 1 espaço/dia;
  Polymorph em si mesmo: PV da forma somados, CA da forma, ataques da forma.
- Portent, Lucky, Silvery Barbs, Chronal Shift, iniciativa e Counterspell: não modelados (igual para todos).

# Passada 2 do Wizard / Área v2 (19/11)
- **Área = luta contra uma horda** (`dh/horda.py`): personagem + 2 guerreiros de referência contra 5 criaturas que
  avançam e 3 à distância; termina com 50% da vida da horda; métrica = 1/rounds, nível pela régua (conjurador de
  referência: 1 área no maior espaço, depois truque). Vale para todas as linhas com dano (marciais também; cleaves somam).
  Área com `"seletiva": true` (Sculpt Spells, alvos escolhidos) não perde alvos depois do round 1.
- **Área no plano = pico** (melhor linha da build), não a média do dia.
- **`forcar_falha`** em fonte de controle: Portent e Chronal Shift = 2/dia ÷ 4 lutas = 0,5 por luta.
- **Builds `-puro`**: extensão simples sem multiclasse das builds do RPGBot que usam dip (Abjuration, Chronurgy,
  War Magic, Echo Knight, Purple Dragon Knight). Níveis adiantados; Mage Armor + Shield no lugar de armadura;
  Resilient Con onde o dip dava o save. As originais ficam como estão.

# Passada 3 (19/11 noite, decidida pelo usuário)
- **Marcas no Corpo.** `ancestral_protectors` (Ancestral Protectors; Unwavering Mark com `"resistencia": false`) é fonte
  de corpo: na atenção, reduz o dano do marcado contra os OUTROS membros da party; só a fração
  `controle.peso_no_controle.ancestral_protectors` (0,25, igual à do Sentinel) conta no Controle.
- **Party de referência = 2 frontliners + atirador + conjurador.** Frontliner médio (CA marcial+1 até 21,
  PV 11+(L−1)·8, soft 0,15, DPR 0,85·ref; `controle.referencia.frontliner.*`). `papel` tank, striker ou frontliner
  ocupa uma vaga de frontliner (os JSON não mudam).
- **Área: teto de 3 rounds** na luta contra a horda (`area.horda2.rounds_max`), para medir o pico.
- **Área dos conjuradores com upcast.** Na linha `area` (luta de pico), as DUAS maiores magias de área da build, cada
  uma num dos dois maiores espaços do dia (o maior e o segundo maior, unidades distintas; a magia precisa caber no
  espaço), escolhidas pelo maior dano esperado (alvos × dano médio) e lançadas na ordem do maior para o menor.
  Escala: Fireball +1d6 por círculo acima do 3º; Shatter +1d8 acima do 2º; Cone of Cold +1d8 acima do 5º; Pulse Wave
  +1d6 acima do 3º; Gravity Fissure +1d8 acima do 5º; Chain Lightning +1 alvo acima do 6º; Breath Weapon e magias de
  raça não escalam. Com uma magia de área só, ela é lançada duas vezes (maior e segundo maior espaço). `gasta` = os
  dois espaços (+ Shield). Truque nos rounds livres: 0,5 (lançou 2). `seletiva` (Sculpt Spells) mantida.
  A linha `combo` fica como estava (controle + as áreas no círculo base).
- Gerador (`ferramentas/geradores/wiz.py`): os patches de nível agora são exatos (chave que sumiu = null), então o
  `gasta` de cada linha não herda mais espaços de níveis anteriores.

# Clérigos (passada 1 do Cleric, 19/11)
- Gerador `ferramentas/geradores/cle.py` (usa `wiz.py`). Espaços pelo nível de conjurador (sem Arcane Recovery, sem Shield).
- Linhas padrão: `principal` (truque), `bless` (Bless, suporte `bonus_continuo` 3 aliados +2,5), `arma-espiritual`
  (Spiritual Weapon no 2º, 1 ataque por round), `guardioes` (Spirit Guardians no maior espaço, +1d8 por círculo acima do
  3º), `guardioes-arma` (SG + SW no round 2), `controle` (Hold Person; Banishment a partir do Cleric 7), `area` (regra de
  upcast do Wizard). O plano automático escolhe.
- **Spirit Guardians = `aura`** (tipo novo da Área): a ação do round 1 é o lançamento; do round 2 em diante fere 3 alvos
  (esfera de 15 pés pela DMG) todo round sem gastar a ação. No dano de alvo único: `com_save` n 0,75 (meio).
  Insect Plague também como `aura` (4 alvos).
- Word of Radiance: `cleave_save` [1, 2, 3] (convenção do Thunderclap). Reaper: Toll the Dead em 2 (`cleave_save` [1, 2, 2]).
- Channel Divinity: `outros.canal` (1/descanso curto até o Cleric 5, 2 a partir do 6). Uso que custa a ação (Preserve
  Life, Balm of Peace, Radiance of the Dawn, Path to the Grave) = linha própria com `gasta`; uso que não custa ação
  (Touch of Death) = `por_luta` com qtd ÷ 2 lutas. Harness Divine Power (quando o guia usa opcionais): espaço extra no pool.
- Divine Strike / Blessed Strikes / Potent Spellcasting somados na string de dano do truque (1 ataque por turno).
- Armadura média: escama + escudo (18) até o 4, meia-armadura (19) a partir do 5; pesada: cota de malha (18), placas no 7.
- Cura na luta (Healing Word) não modelada; cura fora de luta só quando o guia a centra (Goodberry do Life, 1 espaço
  de 1º fora do pool). Warding Flare, Dampen Elements, Sentinel at Death's Door, Protective Bond: não modelados.
- Peace (sem build no RPGBot): clérigo base + Emboldening Bond = `bonus_por_uso` (1 ataque por turno de cada aliado
  no vínculo) + `aura_saves`, escalados pela fração de lutas cobertas (PB/dia ÷ 4 lutas).
- Corpo agora é o nível de neutralidade (`nivel_corpo`, ver ROADMAP 19/11).
- Lote 2 (casos novos, sem mudar o lote 1): Voice of Authority = suporte `ataque_extra` com alvos = ataques ÷ 4 rounds;
  Twilight Sanctuary = `pv_temporario` em 3 aliados todo round (usos_luta 4), linha própria e combinável com Spirit
  Guardians (não é concentração); War God's Blessing = `bonus_por_uso` +10 (2/descanso curto); Crusader's Mantle =
  `dano_por_acerto` 1d4 em 3 aliados (+1d4 nos esqueletos); Destructive Wrath = dano máximo constante na área do trovão;
  Wrath of the Storm = `com_save` Sab/dia ÷ 16; Invoke Duplicity = vantagem 1,0 + Sneak Attack na linha própria;
  esqueletos de Animate Dead como os do Necromancer (4 no 5–7 com 1 espaço de 3º/dia, 6 no 9–11 com 1 de 4º).

# Passada 2 do Cleric (19/11, sem supervisão; só correções mecânicas)
- Variante "+arma" de toda linha que gasta só Channel Divinity e da linha `bless`: a mesma hipótese com Spiritual Weapon
  (ação bônus) do round 2 em diante (+1 espaço de 2º). Motivo: o plano automático põe uma linha por luta e deixava
  Channel e espaços parados (Twilight 7: santuário nunca escolhido, 2 Channel e 6 espaços sobrando).
- `recursos.outros.canal.valor` = espaço do Harness Divine Power (ceil(PB/2)) para o plano pesar o Channel como recurso.
- Command fora das listas de controle (o efeito "um turno" ainda não roda como alvo único no motor).

# Barbarian (passada 1, 21/11; gerador `ferramentas/geradores/bar.py`)
- Fatias por nível de personagem (Ancestral Guardian é Bb8/W2/F1 no 11). PV d12: 12 + Con no 1º, 7 + Con por nível.
- Fúrias 2/3/4 (Bb 1–2/3–5/6–11), dano +2 (até o 8) e +3 (9+). Linha `principal` = sem fúria; linhas `furia*` com
  `gasta` furia 1, `defesa.resist` e o bônus na string; o plano automático escolhe as lutas.
- Reckless Attack: vantagem 1,0 nos ataques de For e `adv: 1` contra ele (como no lote 2 do Fighter), em todas as
  linhas das builds que o usam (o Ancestral Guardian de Destreza não usa, e a fúria não soma no ataque de Des).
- Brutal Critical (9) e Savage Attacks: `dados_crit` = todos os dados da string + 1 dado da arma por feature.
- Danger Sense: `adv: ["Des"]` nos saves. Fanatical Focus (Zealot 6) = `rerolagens: 1` só nas linhas de fúria.
  Mindless Rage (Berserker 6) = `imune: [encanto, medo]` nas linhas de fúria.
- Dano automático que não gasta ação (Storm Aura Desert): `automatico` no alvo principal e, na Área, `cleave_ataque`
  com bônus 99 (acerto garantido) por alvo extra (2 alvos a 10 pés).
- Divine Fury = `por_turno` 1d6 + metade do nível. Infectious Fury e Mighty Impel = `com_save` (1 por luta ÷ 4 rounds /
  ação bônus dos rounds 2–4). Mighty Impel também como `condicao_no_acerto` derrubado (`no_acerto: false`, 3 usos).
- Totem do Lobo: suporte `vantagem` 1 aliado, fração 0,5 (julgamento a calibrar). Crusher (Wild Magic, Open Hand):
  `vantagem` 3 aliados com fração = P(≥ 1 crítico no turno). Zealous Presence: 3 aliados × 1/16 (1/dia, 1 round).
- Spirit Shield (Ancestral Guardian 6): suporte `cura` com 2 usos por luta (reação em 50% dos rounds), 2d6 = 7.
- Wild Surge: só o valor esperado das opções de dano 4 (+1d6/8 por acerto) e 8 (1d6 com save na ação bônus, 1/8 dos
  rounds 2–4); Bolstering Magic = linha com +2 no acerto e `gasta` bolstering (PB/dia).
- Polearm Master: ataque do cabo na ação bônus (0,75 nas linhas de fúria: o 1º round vai na fúria) + oportunidade 0,5.
- Berserker (sem build no RPGBot): chassi do Handbook; `frenesi` 1 por descanso longo (RAW) e, na versão
  `-homebrew` (grupo Homebrew, fora do gabarito), 2 por descanso curto (a exaustão sai no descanso curto).
- Não modelados (igual para todos): PV temporários próprios (Reckless Abandon, Touch of Death), Relentless Rage,
  Feral Instinct, agarrar+empurrar (custa ataques), saltos/voo, Form of the Beast mordida/cauda, Guile of the Cloud Giant.

# Monk (passada 1, 21/11; gerador `ferramentas/geradores/mon.py`)
- PV d8 (8 + Con, 5 + Con por nível); CA 10 + Des + Sab; saves For/Des; Evasion e Stillness of Mind a partir do 7;
  Purity of Body (10) = `imune: [veneno]`. Dado de Martial Arts d4/d6/d8 (1–4/5–10/11+), também na arma de monge.
- Ki = nível de monge por descanso curto (`ki`, volta curto). Linhas padrão: `principal` (ataque + 1 golpe desarmado na
  ação bônus), `meia-rajada` (Flurry em 2 rounds, 2 ki), `rajada` (Flurry todo round, 4 ki) e, a partir do 5,
  `atordoar` (Flurry em 2 rounds + 2 tentativas de Stunning Strike, 4 ki). O plano automático reparte o ki do dia.
- Stunning Strike = `condicao_no_acerto` com o efeito novo `cond_atordoado_um_turno` (Con, peso 1, um turno). A vantagem
  dos aliados contra o atordoado não é contada.
- Durações de 10 minutos (Arms of the Astral Self, Darkness) = 1 luta. Invocação dos braços: área `explosao` em 2 alvos.
- Mercy: Hand of Harm `por_luta` (2 usos por luta) e, no 11, `por_turno` (grátis no Flurry); Physician's Touch =
  `cond_envenenado_um_turno` (peso 0,35, sem save: cd 99); Hand of Healing = `cura_na_luta` (toque, ação bônus).
- Long Death: mordida de Con a partir do 5 (sem a vantagem abaixo da metade da vida: condição de julgamento);
  Hour of Reaping = fonte `area` com o efeito novo `hour_of_reaping` (Sab, peso 0,4, 6 alvos), ação todo round;
  Mastery of Death = `golpes_extras_a_0pv: 1`.
- Shadow: Darkness + Devil's Sight = vantagem 1,0 nos ataques e `adv: -1` contra ele (o custo para os aliados não entra).
- Kensei: Fighter 1 (Archery) primeiro, então as fatias são Monk 2/4/6/8/10; Sharpen the Blade fica fora (nível 12).
- Sun Soul: Radiant Sun Bolt como ataque à distância (papel atirador); Searing Sunburst grátis como `cleave_save` livre.
- Ascendant Dragon: os dois sopros (monge, PB/dia; Dragonborn, PB/dia) no lugar de ataques do 1º round, cone de 20 pés = 2
  alvos; Frightful Presence (11) = amedrontado com resave, 4 tentativas por luta (1/descanso longo).

# Mutirão de 21/11 (8 classes; textos das sessões, sem edição)

# Paladin (passada 1, 21/11 mutirão; gerador `ferramentas/geradores/pal.py`)
- PV d10; saves Sab/Car; Aura of Protection (Paladin 6) soma Car nos próprios saves e entra no Suporte como `aura_saves`.
- Espaços pela tabela de conjurador completo com nível ceil(Pal/2) (multiclasse: floor(Pal/2) + nível do outro conjurador);
  espaços de pacto em `outros.pacto` (volta curto).
- Divine Smite: linhas `smite-<círculo>` (2 smites por luta naquele círculo, `por_luta`, 1º 2d8 … 3º 4d8); toda linha de
  subclasse ganha a variante `+smite` (2 smites de 1º) se sobrarem espaços de 1º. Improved Divine Smite = +1d8 na string.
- Linha `bless` em todos os paladinos com espaço (ação no round 1, ataques 0,75). Lay on Hands = `cura_na_luta` (toque, ação,
  pool de 5 × nível ÷ 4 lutas).
- Channel Divinity `outros.canal` 1/descanso curto, `valor` = espaço do Harness Divine Power. Uso de ação no round 1
  (Sacred Weapon, Conquering Presence) = ataques 0,75; de ação bônus (Vow of Enmity) = ataque da ação bônus 0,75.
- Vow of Enmity = vantagem 1,0 na luta. Sacred Weapon = +Car no acerto. Hunter's Mark = +1d6, `gasta` 0,5 espaço de 1º.
- Polearm Master: cabo na ação bônus (1d4) + oportunidade 0,5 (reação, dano e controle). Cimitarra de duas lâminas: ataque
  de 1d4 na ação bônus; GWF em 2d4 = +1,0, em 1d4 = +0,5.
- Form of Dread: `pvt_luta` 1d10 + nível de warlock e `condicao_no_acerto` amedrontado (4 tentativas por luta), PB/dia.
  Aura of Conquest: `com_save` Sab n 0,75 com metade do nível de paladino nas linhas que causam medo.
- Armor of Agathys: `pvt_luta` 5 (1º); dano de retorno não modelado. Inspiring Smite = `pv_temporario` 2d8 + nível em 1 aliado.
- Haste em si: round 1 é a ação; +1 ataque nos rounds 2–4 (0,75) e `defesa.ca` +2.
- Não modelados (igual para todos): smite guardado para o crítico, Aura of Courage, Divine Allegiance, Aura of the Guardian,
  Rebuke the Violent, Champion Challenge/Compelled Duel, Shield Master (derrubar), Watcher's Will, Aura of Warding,
  Find Steed, upcast de Bless/Ensnaring Strike.

# Rogue (passada 1, mutirão 21/11; gerador `ferramentas/geradores/rog.py`)
- Sneak Attack: `por_turno` com `"prob"` = gatilho além do acerto. Sem fonte própria (aliado adjacente ao alvo) 0,75;
  Rakish Audacity 0,9 (união com aliado adjacente); fonte própria 1,0 (Steady Aim; familiar adjacente do AT, como o Help
  do familiar do Ancestral Guardian).
- Steady Aim (Tasha's): vantagem 1,0 e ação bônus declarada (`acao_bonus`); só quando o guia usa os opcionais (o Scout não).
- Hide com Cunning Action: não conta (vantagem depende de cobertura = julgamento).
- Assassinate: vantagem = 0,25 (round 1) × chance de vencer a iniciativa (0,6 no 3; 0,8 com Alert; 0,95 com Reliable
  Talent + Harengon). Críticos da surpresa: não contam.
- Booming Blade: só o dano no acerto (1d8 no 5, 2d8 no 11); o secundário não conta. CA de couro batido 12 + Des.
- Uncanny Dodge (5+) em `defesa.reacoes`; Evasion (7+) nos saves.
- Wails from the Grave: `por_luta` com metade dos dados do Sneak; PB `usos_dia` até o 8; do 9 em diante PB ÷ 4 + 1
  Soul Trinket por luta (reação 0,25). Soul Trinket na mão: vantagem em saves de Con.
- Homing Strikes: `dado_no_erro` com (2×PB + 2) ÷ 4 usos por luta.
- Fast Hands: frasco de ácido na ação bônus (2d6 + Des, arma improvisada sem proficiência); estrepes não contam.
- Master of Tactics: suporte `vantagem` com `fracao` = 1 ÷ (3 × ataques do aliado na régua) (1 ataque de 1 aliado por round).
- Inspiring Leader: `pv_temporario` `entre_lutas` com `usos_descanso_curto` 1 (nível + Car).

# Bard (passada 1, 21/11; gerador `ferramentas/geradores/brd.py`, usa `wiz.py`)
- Espaços de conjurador completo (sem Shield/Mage Armor). Linhas: `principal` (truque: Vicious Mockery kd4 Sab sem meio;
  Valor arco longo, Whispers besta leve, Swords rapieira), `controle` / `controle-barato` / `area` (regras do Wizard),
  `invisibilidade` (Greater Invisibility num aliado: `vantagem` 1 alvo + `desvantagem_contra` 1 alvo, gasta 4º).
- Bardic Inspiration = `dado_multiuso` (d6/d8/d10 em 3/5/10), usos por luta = Car ÷ 4 até o 4 e Car ÷ 2 com Font of
  Inspiration (5). Healing Word como no Cleric (passada 3), exceto Whispers (não tem).
- Dados divididos entre usos: Lore metade como Cutting Words (`mix` {"ca": 1}); Whispers metade em Psychic Blades e Swords
  metade em Blade Flourish (`por_luta`); Eloquence 1 dado por luta em Unsettling Words (CD +dado na linha de controle) e
  Unfailing Inspiration (6) = `volta_se_falhar`; Glamour 1 dado por luta em Mantle of Inspiration (`pv_temporario`
  5/8/11 em 3 aliados).
- Creation: Mote of Potential como riders proporcionais ao mix padrão (ataque → `valor_por_luta` dado × 1,5 alvos; save →
  `pv_temporario` dado + Car); Dancing Item = invocação (CA 16, PV 10 + 5×nível, 1d10 + PB com 0,5 ataque/round pela ação
  bônus), gasta 0,25 espaço de 3º por luta. Glamour: Mantle of Majesty = Command em 4 rounds, `outros.majestade` 1/longo.
- Valor: peitoral + escudo (18), Elven Accuracy no 4, Archery no 8, Holy Weapon (10+) = linha `arma-sagrada`, 0,5 de 5º.
- Não modelados (todos): Silvery Barbs, Counterspell, Sleep, Faerie Fire, Dissonant Whispers, Mass Suggestion, desvantagem
  do Vicious Mockery, Song of Rest, Tales from Beyond (aleatório), Combat Inspiration além do mix padrão.

# Druidas (mutirão 21/11)
- Druida base: Produce Flame (ou o truque da build), controle = Entangle + Hold Person (+ Polymorph quando a build o
  nomeia), Healing Word em todas as linhas (convenção do Cleric). Wild Shape = recurso `forma_selvagem` {qtd 2, volta curto}.
- Usos de Wild Shape como buff (Starry Form, Symbiotic Entity, Wildfire Spirit, forma de combate do Moon) = variante
  "+<nome>" de cada linha, gastando a forma (10 min ou menos = 1 por luta; Wildfire Spirit 1 hora = 0,5). Ataques da
  forma ×0,75 quando a linha lança magia no round 1.
- Moon: PV da forma somados aos do druida, CA e ataques da forma (como Polymorph em si mesmo); efeitos de agarrar/derrubar
  não modelados; Elemental Wild Shape (2 usos) em variantes "+elemental".
- Natural Recovery = Arcane Recovery. Invocações de 1 hora = 0,5 espaço por luta. Mighty Summoner: +2 PV por dado de vida
  (Conjure X), não se aplica aos Summon de Tasha.
- Symbiotic Entity: `pvt_luta` 4 × nível. Halo of Spores: com_save n 0,75 por round (reação). Balm of the Summer Court
  substitui o Healing Word (cura_na_luta, 2 × nível PV, sem espaço). Enhanced Bond em área: +4 fixo (parser).
- Starry Form Archer: ataque extra 1,0/round; Guiding Bolt grátis e Cosmic Omen: PB/4 por luta.

# Warlock (mutirão 21/11)
- Espaços de pacto: `recursos.espacos = {nível do pacto: qtd}`, `espacos_volta: "curto"`; todo `gasta` no nível do pacto
  (magia de círculo menor lançada no espaço do pacto; upcast de área pela regra da magia).
- Eldritch Blast + Agonizing Blast: `ataques` com n = raios (1/2/3 nos níveis 1/5/11), dano 1d10+Car. Armor of Shadows: CA 13+Des.
- Hex: linha `hex` (0,5 espaço/luta) e variantes `+hex` das linhas sem concentração (área, Mass Suggestion).
- Mystic Arcanum: recurso `outros.arcano` (qtd 1, `volta: longo`), linha própria; Mass Suggestion no 11.
- Recurso de subclasse por descanso curto que dura até o alvo cair (Hexblade's Curse): valor médio por golpe = efeito ÷ 2 lutas.
- Recurso PB/dia que dura 1 minuto (Tentacle of the Deeps, Form of Dread): fração por luta = min(1, PB/4).
- Recurso 1/descanso curto em reação (Entropic Ward): `usos_luta` 0,5.

# Sorcerer (passada 1, 21/11; gerador `ferramentas/geradores/sor.py`)
- Espaços = tabela de conjurador pleno (nível de conjurador na multiclasse) + Flexible Casting: TODOS os pontos de feitiçaria
  (= nível de Sorcerer, a partir do 2) viram espaços, gulosamente no maior círculo disponível até o 5º (custo 2/3/5/6/7). Sem Arcane Recovery.
- Metamagia (Twinned, Quickened, Heightened, Extended, Transmuted) não modelada na passada 1; vai para `nao_modelado`.
- Mage Armor: 1 espaço de 1º/dia fora do pool (como Wizard). Draconic Resilience = CA 13+Des e +1 PV/nível de Sorcerer.
- Elemental Affinity: +Car no dano de magias do elemento (truque incluso) a partir do 6. Elemental Adept não modelado.
- Saves de proficiência pela 1ª classe (Divine Soul com Cleric 1: Sab/Car). Armadura da build: média/pesada quando a raça ou o dip dá.
- Linhas: as mesmas dos wizards (principal, controle, controle-barato, area, combo, invocacao) + `bless` quando a build usa Bless
  (fonte de suporte `bonus_continuo` igual à dos clérigos).
- Magias fora de `magias.json` ficam fora (em `nao_modelado`), sem criar magia nova na passada 1.

# Ranger (passada 1, mutirão 21/11; gerador `ferramentas/geradores/ran.py`)
- Hunter's Mark: +1d6 na string de dano de cada ataque; 1 hora → `gasta` 0,5 espaço de 1º por luta. Linha `marca`.
- Dread Ambusher: 0,25 ataque/round com +1d8 (1 ataque extra no 1º de 4 rounds). Stalker's Flurry: +0,5 ataque/turno.
- Riders 1×/turno das subclasses (Colossus Slayer, Planar Warrior, Slayer's Prey, Dreadful Strikes, Gathered Swarm) = `por_turno`.
- Pet (drake, Primal Companion): ataque próprio com bônus de magia, 0,75/round (round 1 da ação bônus vai na Hunter's Mark).
- Distant Strike: 3º ataque sempre (assume ≥ 2 inimigos).

# Artificer (passada 1, mutirão 21/11; gerador `ferramentas/geradores/art.py`)
- Pet/objeto permanente que age na ação bônus (Steel Defender, Eldritch Cannon): `invocacoes` em todas as linhas, com o stat
  block pelo nível; tratado como presente em todas as lutas.
- Reação de outra criatura que protege a build (Deflect Attack): reação com `"propria": true`, 1/round (`usos_luta: 4`).
- "+X dados uma vez por turno se algum ataque acertar" (Lightning Launcher): entrada extra de 1 rolagem por turno com o mesmo bônus.
- Infusões: só as que mudam número fixo (Enhanced Defense/Weapon/Arcane Focus, Repulsion Shield) e só se o guia as põe na própria build.
