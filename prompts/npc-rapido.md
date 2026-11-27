# Testar um NPC (ou qualquer build nova) — fluxo curto, 27/11

1. **Ficha → JSON.** Descreva o NPC (classe/nível ou bloco de monstro adaptado, atributos, ataques, magias, features).
   O Claude escreve `progressoes/npc-<slug>.json` no formato de `progressoes/exemplo-guerreiro.json`, com
   `"grupo": "NPC"`, e `"planos": {"padrao": "auto", "combate_unico": "auto"}`. Mecânica que faltar vai para
   `descricao.nao_modelado` (e, se pesar, vira tipo genérico em `dh/`).
2. `python -m dh expandir && python -m dh validar builds/npc-<slug>-*.json`
3. `python -m dh completo builds/npc-<slug>-*.json` (rápido: segundos por build)
4. `python -m dh valor builds/npc-<slug>-*.json` → valor do dia em dano equivalente, parcelas (dano, suporte,
   controle, área), a luta única, o **percentil entre os chassis do mesmo nível** e os 3 chassis de valor parecido.
5. Eixos um a um: `python -m dh linhas builds/npc-<slug>-<nv>.json` ou o site (`python -m dh site`).

Limites da v0 do valor (P3): é a moeda do plano automático (`dh/moeda.py`) somada no dia; a defesa passiva só entra
pelas vidas do controle/atenção; o corpo de invocação está sem teto (DIAGNOSTICO-RAIOX.md #2). Comparar NPC com NPC
do mesmo nível é mais seguro que ler o número absoluto.
