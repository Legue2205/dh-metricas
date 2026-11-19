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
