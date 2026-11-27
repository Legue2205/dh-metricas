# Diagnóstico do raio-x das builds do RPGBot (27/11)

Base: painel "Raio-x das builds do RPGBot" (`ferramentas/raiox_rpgbot.py`, resultados do CI de 27/11), 110 builds
de exemplo fora do holdout × níveis 3–11, mais o chassi e as medições oficiais (`comparar_chassi.py --sem-holdout`,
`meta_consenso.py`, `comparar_dpr.py`). Holdout e party não foram olhados.

## 1. As 36 quedas de nível (um eixo cai > 1 nível equivalente de um nível para o seguinte)

Para cada caso: o plano padrão mudou? A melhor linha daquele eixo caiu?

| | casos | o que é |
|---|---|---|
| **Troca de plano, melhor linha não caiu** | 29 | o eixo cai porque o plano trocou um eixo por outro (soma zero entre eixos) |
| **Troca de plano e a melhor linha caiu** | 6 | regressão real da mecânica no nível novo |
| **Mesmo plano, eixo caiu** | 1 | regressão dentro do plano |

### 1a. Troca de plano (29) — o padrão é o "pêndulo" invocação ↔ controle
- **Warlocks, 7→9 (4 casos, todos −3,5 no controle):** Fathomless, Fiend, Genie, Undead passam de `controle` ×4 para
  `invocacao` ×4. A melhor linha de controle sobe (8,4–9,0 → 9,9–11,6). O corpo do plano vai a 18,9.
- **Warlocks, 9→11 (3 casos, −3,0):** Archfey, Celestial, Undying: `controle` ×4 → `invocacao` ×3 + `arcano+hex`.
- **Wizards 5→7 (Abjuration ·p, Scribes, Necromancy, Abjuration):** `combo`/`controle` → `invocacao` ×4.
- **Wizards 7→9 (Abjuration ·p, Scribes, Necromancy no dano; Evocation no controle):** volta de `invocacao` para
  `controle-barato`/`combo`. **O mesmo Wizard vai e volta entre invocação e controle a cada dois níveis.**
- **Wizards/Druids/Warlocks 9→11 no corpo (Conjuration, Land, Fiend, Fathomless, Undead):** saem da invocação em
  1–2 lutas para `haste`, `arcano`, `controle`.
- **Conjuration 3→5:** `controle` → `invocacao` ×4.
- **Bards:** Valor 9→11 (`controle` → `invisibilidade` ×4, −4,3); Lore 7→9 (→ `invisibilidade` ×4, −2,1).
- **Monks 7→9:** Open Hand, Sun Soul: `atordoar` sai do plano para `rajada-mira`/`raios-rajada` (dano).
- **Paladins:** Vengeance 7→9 no dano (`voto+smite` → `bless+smite`, −1,4); Redemption 7→9 no suporte (`bless` →
  `padrao-hipnotico+smite`, −1,6).

**Leitura:** o plano escolhe a linha de maior dano equivalente para **cada luta**, mas as 4 lutas do dia são
iguais: quando invocação e controle estão perto, o dia inteiro troca de uma vez ("tudo ou nada"). Os eixos do plano
(visão misto) herdam a troca. Isso não é erro de mecânica, mas torna o ranking por eixo frágil (G5) e esconde que a
build sabe fazer as duas coisas.

### 1b. A melhor linha caiu (6) — regressão real
- **Stunning Strike cai do 7 para o 9:** Astral Self 1,1 → 0,3, Drunken Master 1,0 → 0,5, Four Elements 1,0 → 0,5
  (Open Hand 1,3 → 0,8 dentro da troca). Hipóteses: os inimigos de CR 9 sobem o save de CON mais rápido que a CD do
  Monk; resistência lendária no chefe; imunidade a atordoamento nos encontros novos; ki por luta.
- **Conquest 9→11:** controle 3,3 → 2,2 e corpo 12,7 → 11,0 na linha `conquista+smite`. Hipótese: imunidade a medo
  nos inimigos de CR 11, ou a aura de 10 pés perdendo alvos.
- **Eloquence 7→9:** melhor linha de controle 14,1 → 13,2 (pequena).
### 1c. Mesmo plano (1)
- **Arcane Archer 7→9:** controle cai com o mesmo plano (`principal` + `surge`) e a melhor linha sobe — os Arcane Shots
  não escalam (2 por descanso) enquanto a régua sobe.

## 2. Outras divergências do raio-x

1. **Corpo de invocação sem teto.** Creation 30,2 (nv9) e 38,3 (nv11); Wizards/Druids de invocação 18–26; o
   Hexblade chega ao topo do corpo porque o plano dele é `invocacao` ×4. Um nível equivalente acima de 20 é fora da
   escala da própria régua. Isso alimenta o pêndulo (o corpo das invocações entra na moeda pelo controle).
2. **Dano dentro da classe (G1, 0,36 / 0,38):** Cleric 0,0 / 0,0, Monk 0,13 / 0,08, Warlock 0,40 / −0,12, Wizard
   0,27 / 0,27, Ranger 0,15 (nv7). A conta do DPR está certa (G1b, 23 casos), então o problema é o que entra nela.
3. **Mecânicas de subclasse que faltam (aparecem como empate ou zero):**
   - Hunter no 11: todas as linhas com a mesma área (4,6) — **Multiattack (Volley/Whirlwind Attack) não existe**;
   - Bladesinging no 11: defesa física 5,1 — o plano não usa a linha com Bladesong (defesa amarrada a uma linha);
   - Wizards com suporte 0 (16/16 sem fonte): Projected Ward (Abjuration), Portent em aliado (Divination);
   - Order's Wrath (Cleric Order, 8), Protective Field (Psi Warrior), Hand of Healing (Mercy, 0,3).
4. **Suporte ausente em classes inteiras:** sem fonte de suporte no nv7 — Ranger 8/8, Warlock 8/9, Fighter 10/12,
   Monk 9/11, Barbarian 6/10, Wizard 16/16. Parte é real (marciais), parte é mecânica que falta (item 3).
5. **Defesa mental imatura:** os Druids todos no topo, os Paladins quase ausentes (a Aura of Protection deveria pôr
   os Paladins no topo).
6. **G3 (meta faz sentido): passa 2 de 12.** O topo de cada eixo está bom (nenhum "fraco" no top-10); o fundo falha,
   muito por empates (todos os Wizards com suporte 0, todos os Bards juntos no dano e na defesa).
7. **Chassi × build de exemplo:** a build do RPGBot tem mais corpo (+1,3 / +1,5) e defesa (+0,7 / +0,6) e menos
   controle e área (−0,6 a −1,2) que o nosso chassi: o chassi escolhe magias/feats mais "conjurador controlador".
8. **Nota geral do RPGBot × média dos eixos:** τ 0,20 / 0,17 (agrupado). A área anticorrelaciona (−0,13): o RPGBot
   valoriza menos blaster do que a média dos eixos.

## 3. Ranking (impacto nos gates e na pergunta do Kael)

| # | Problema | Gates | Tipo |
|---|---|---|---|
| 1 | **Plano tudo-ou-nada e o pêndulo invocação ↔ controle** (29 quedas) | G5, G1, G3, G4 | estrutural (plano) |
| 2 | **Corpo de invocação sem teto** (Creation 38, invocações 18–26, Hexblade no topo) | G2 corpo, G3, e alimenta o #1 | valoração |
| 3 | **Dano dentro da classe** (Cleric, Monk, Warlock, Wizard) | G1 dano (0,36 → 0,50) | diagnóstico por classe |
| 4 | **Mecânicas de subclasse faltando no 11** (Hunter Multiattack, Bladesong fora do plano, Projected Ward, Portent, Order's Wrath, Protective Field, Hand of Healing) | G1 suporte, G3, G7 | mecânica genérica |
| 5 | **Regressões reais** (Stunning Strike 7→9, Conquest 9→11, Arcane Archer) | G1 controle, G5 | mecânica/encontro |
| 6 | **Defesa mental imatura** (Paladins ausentes) | G2 defm, G3 | régua |
| 7 | **Empates no fundo** (G3, G7: ≤ 10% de empates) | G3, G7 | resolução da escala |
| 8 | **Chassi mais controlador que a build real** | G1, G4 | escolha do chassi |
| 9 | **Valor total (P3) inexistente** — a moeda DE já existe por linha (`dh/moeda.py`), mas não há o total do dia nem defesa/saves nela | G4, G6, Kael | plataforma |

## 4. Sprint paralela (27/11 noite → 29/11)
Cada pacote roda numa sessão própria, num worktree e num branch `sprint/<pacote>`; cada um registra o que fez em
`sprint/<pacote>.md` (achado, mudança genérica, teste, medição antes/depois dos gates afetados). O Claude principal
junta os branches, mede tudo de uma vez e só então manda para a main.
- **A — plano e corpo (#1 + #2).** Diagnosticar a margem das trocas; propor (sem mudar premissa) um plano que não seja
  tudo-ou-nada e um teto/saturação para o corpo de invocação; medir G5 e o corpo.
- **B — dano dentro da classe (#3 + #8).** Cleric, Monk, Warlock, Wizard: discordâncias par a par, causa, correção
  genérica.
- **C — mecânicas faltando (#4).** Tipos genéricos com teste: ataque em área do Hunter, buff defensivo que vale fora
  da própria linha (Bladesong), proteção de aliado por reação (Projected Ward, Protective Field), Portent, Order's
  Wrath, Hand of Healing.
- **D — regressões e defesa mental (#5 + #6).** Stunning Strike 7→9, Conquest 9→11, Arcane Archer; Aura of Protection
  na defesa mental.
- **Principal — P3 e NPC (#9).** Valor total do dia em DE (plano + defesa/saves convertidos), `dh valor` e o fluxo de
  teste de NPC novo.

Regras para todos: não mudar gabarito, gate nem premissa (propor e deixar para o usuário); nada de holdout nem party;
`python -m pytest -q` antes de cada commit; medir com builds recalculadas localmente (`dh completo` nas afetadas).
