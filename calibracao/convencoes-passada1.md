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
