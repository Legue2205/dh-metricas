# Sprint D — regressões de nível (#5) e defesa mental (#6) — 27/11

Branch `sprint/d-regressoes-defm`. Medido com `dh completo` local em 109 builds afetadas (chassi dos Paladins, chassi
de nível 11 com efeito de um turno no acerto, RPGBot Monk 9, Arcane Archer 9, Paladins do RPGBot 7 e 11). O resto foi
conferido: recalcular uma build não afetada dá os mesmos números do CI (só os hashes mudam).

## #5 Regressões

### Causa comum: Legendary Resistance do chefe sozinho a partir do nível 9
`base.chefe.lr_cr` = 10 e `lr_n` = 1: o encontro "Chefe sozinho" (peso 0,30) tem CR 8 no nível 7 e CR 10 no 9, e só aí
ganha 1 LR. A CD e o save não explicam a queda: Stunning Strike CD 14 contra CON +7,9 (nv7) e CD 15 contra +9,0 (nv9)
dão a mesma chance de falha (~0,25). Os outros encontros ficam iguais nos dois níveis (Minions, Party de elite, Horda,
Dupla); só o chefe vai a ~0.

| caso | o que cai | causa | veredito |
|---|---|---|---|
| Stunning Strike 7→9 (Astral Self, Drunken Master, Four Elements, Open Hand) | negação no Chefe sozinho 0,13–0,19 → ~0 | 2 tentativas por luta contra 1 LR | **regra certa** (o chefe gasta a LR no atordoamento) + **defeito pequeno** (abaixo) |
| Arcane Archer 7→9 | campo do plano 1,7 → 0,3 | Shadow Arrow 1×/luta: a LR come a única tentativa contra o chefe; a régua de dia (`nivel_dia`) amplia a diferença | **regra certa** |
| Conquest 9→11 (`conquista+smite`) | controle 3,3 → 2,2, corpo 12,2 → 11,0 | a build do RPGBot é Paladin 8 / Warlock 2→3: do 9 ao 11 a linha não muda (mesma CD 16, mesmo DPR, CA 20, +7 PV), enquanto os inimigos sobem (chefe CR 12, horda CR 3) e a party de referência passa a CA 19 no 11; o T da atenção cai 0,185 → 0,087. O chefe já estava em 0 no 9 (LR) | **regra certa** (build parada no multiclasse) |

**Defeito corrigido (genérico):** `condicao_no_acerto` com término `um_turno` subtraía a LR do número *esperado* de
falhas: `max(0, E[X] − lr)`. Com 2 tentativas e 1 LR, E[X] = 0,5 → 0, embora a 2ª falha passe em 6% das lutas.
Agora é `E[X] − E[min(X, lr)]`, exato por programação dinâmica (`_lr_gastas` em `dh/controle/efeitos.py`). Sem LR o
valor é idêntico ao anterior. Teste: `tests/test_condicao_no_acerto.py::test_um_turno_lr_exata_nao_zera`.
Efeito: Chefe sozinho do Stunning Strike 0 → 0,013–0,019; Open Hand nv9 `atordoar` 0,80 → 1,42 (a Open Hand
Technique também era zerada); Astral Self/Drunken Master/Four Elements ficam iguais no arredondamento (0,32 / 0,46).

**Não mudei (para o usuário decidir):**
- *Valor de queimar uma LR.* O motor dá zero ao Stunning Strike que só gasta a LR; na mesa isso é o papel clássico do
  Monk (a próxima magia da party pega). Seria uma premissa nova de valor para a party (ex.: fração do valor de um
  controle de referência por LR gasta) — `seq1` já conta as LR gastas (`q`), mas ninguém usa.
- *Ki por luta fixo nas linhas.* As linhas `atordoar` do gerador do Monk usam 2 tentativas em todos os níveis (4 ki),
  com 9 ki por descanso curto no nível 9. Uma linha "atordoar o chefe" com mais tentativas recuperaria parte do valor.
  É dado de linha (gerador do Monk, que o pacote B também mexe), não defeito do motor.
- O degrau `lr_cr` = 10 é uma premissa (cria o penhasco 7→9 para todo efeito de poucos usos).

## #6 Defesa mental

**Como é calculada:** `defm = 2/3 · Vontade + 1/3 · Resiliência` (`base.defesa_magica`), cada uma o nível equivalente
de `dh/saves.py` (conjurador inimigo de nível L, 4 rounds, repertório `saves.repertorio_mental`), lido dos `sv` do
corpo + campos da linha (imune, adv, res, rerolagens, stillness…). A Aura of Protection **já estava** no próprio save
(`saves_pal` soma o CAR em todos), e as proficiências também.

**O que faltava (Paladin):** Aura of Devotion (Devotion 7: imune a encanto), Aura of Courage (todo Paladin 10: imune a
medo) e Aura of Warding (Ancients 7: resistência a dano de magia). Já estavam: Mindless Rage, Fanatical Focus
(rerolagem), Iron Mind, Elegant Courtier, Indomitable (0,25 por luta via `patches_linhas`), Stillness of Mind, Purity
of Body. Diamond Soul é do 14 (fora).

**Mudanças:**
- `dh/saves.py`: listas `imune`/`res`/`adv` do corpo agora **somam** às da linha (antes a linha substituía: uma fúria
  com imune a encanto/medo apagaria uma imunidade do corpo). Nenhuma build atual tinha o conflito. Teste em
  `tests/test_saves_auras.py`.
- Geradores `pal.py` / `chassi_paladin.py` / `puro_paladin.py`: `auras_saves(pal, sub)` põe as três auras no corpo
  (pelo nível de PALADINO: o Conquest do RPGBot, Pal 8, não ganha a Aura of Courage). `nao_modelado` atualizado.
  Regeneradas as progressões `chassi-paladin-*` e `rpgbot-paladin-*` (só entram os campos novos), `dh expandir` e
  `calibracao/pacotes.py` (só os pacotes de Paladin mudam, e só no saves).

**Efeito (defm, visão misto, chassi sem feat):** Devotion 7,3 → 11,5 (nv7) e 11,2 → 16,2 (nv11); Ancients 7,7 → 9,7 e
11,9 → 14,6; demais Paladins 7,3 = (nv7) e 11,2 → 11,4 (nv11). Druids 7,4 / 12,3 (iguais).
G3 defm: topo nv7 1/10 → 2/10 forte, nv11 2/10 → 3/10; fundo 2/10 nos dois (não passa; defm não está no gate).
- topo nv7: paladin-devotion, paladin-ancients, monk-astral-self, druid-moon, barbarian-berserker, druid-dreams,
  druid-land, druid-shepherd, druid-spores, druid-stars
- topo nv11: paladin-devotion, paladin-ancients, 7 Druids, paladin-conquest
- fundo (os dois níveis): ranger-beast-master, ranger-drakewarden e os Bards.

**Por que os outros Paladins seguem atrás dos Druids (estrutural — levar ao usuário):**
1. O repertório mental é ~60% Sab (15 de 24 magias com save), 5 Int e só 3 Car: o +7/+10 de CAR do Paladin quase não conta.
2. O chassi do Paladin tem CAR 15 no 7 (aura +2) e Sab 12: Sab +6 contra +7 do Druid. Com Sab + aura o Paladin
   empata com o Druid no 7 (7,37 × 7,38) e perde no 11 (Sab +8 × +9). A régua de saves sobe Sab em degraus (prof. e
   itens a cada 4 níveis), e 1 ponto de Sab vale ~2 níveis.
3. O inimigo só lança magias; efeitos de monstro (Frightful Presence, olhar encantador, Mind Blast) não entram, e são
   eles que dão valor à Aura of Courage. Mudar o repertório é mudar premissa existente: não fiz.

**Lacunas que ficaram (não Paladin, de propósito, para não cruzar com o pacote C):** Beguiling Defenses (Archfey 10,
imune a encanto), Nature's Ward (Land 10, imune a veneno), Beguiling Twist (Fey Wanderer 7, vantagem contra
encanto/medo: o motor só tem `adv_encanto`), Watcher's Will (Channel Divinity, divide o recurso com outra linha),
Portent no próprio save (o dado já é gasto no controle via `forcar_falha`).

## Gates (comparar_chassi --sem-holdout), antes → depois
Nenhum τ cai mais que 0,01: dano 0,36/0,38 =; controle pista 0,66/0,61 =, agrupado nv11 0,34 → 0,33; suporte
0,38/0,37 =; área e corpo agrupados =; deff pista 0,60/0,58 =, agrupado −0,12 → −0,08 (nv7) e −0,13 → −0,12 (nv11).
G3 só muda no defm (acima).
