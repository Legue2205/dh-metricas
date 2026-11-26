import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'calibracao'))
from comparar_dpr import classe, medir  # noqa: E402


def test_classe():
    assert classe(28.6, 28.65) == 'igual' and classe(27.0, 28.65) == 'pequena' and classe(25.0, 28.65) == 'grande'


def test_baseline_warlock_do_rpgbot_bate():
    """O baseline do Fundamental Math (EB + Hex + Agonizing) é a conta mais simples do RPGBot: tem de bater."""
    assert all(x['classe'] == 'igual' for x in medir() if x['id'].startswith('fm-warlock'))
