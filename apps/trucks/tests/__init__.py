from __future__ import annotations

import os
import unittest


def load_tests(loader: unittest.TestLoader, tests, pattern):
    """
    Descobre testes recursivamente dentro de `trucks/tests/`.

    Mantemos o padrão de nome `*_spec*.py` para refletir a estrutura do projeto.
    """

    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir=start_dir, pattern="*_spec*.py")
    return suite
