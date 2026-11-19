# Geradores das progressões do RPGBot

Scripts que escreveram `progressoes/rpgbot-*.json` (rodar da raiz do repo; depois `python -m dh expandir`).
- `fighter_lote2.py`: Samurai, Echo Knight, Psi Warrior, Rune Knight, Purple Dragon Knight (o do lote 1 se perdeu;
  as progressões do lote 1 foram editadas à mão/por `p2.py` depois).
- `p2.py`: passada 2 do Fighter (condição no acerto nas progressões existentes). Já aplicado; não rodar de novo.
- `wiz.py` (biblioteca) + `wiz_builds.py`: as 13 subclasses de Wizard e as 3 puras.
- `puro_fighter.py`: Echo Knight e Purple Dragon Knight puros.
- `cle.py`: Cleric (passada 1): Death, Grave, Life, Light, Nature e Peace (clérigo base). Arcana, Forge, Order,
  Knowledge, Tempest, Trickery, Twilight e War esperam as páginas corretas no Drive.
- `cle2.py`: Cleric lote 2: Arcana, Forge, Knowledge, Order, Tempest, Trickery, Twilight, War (reemite o lote 1, idêntico).
