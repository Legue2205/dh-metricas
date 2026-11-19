"""Escrita atômica: arquivo temporário na mesma pasta + os.replace. Vários processos (dh completo em paralelo)
podem gravar o mesmo cache; quem lê vê sempre um arquivo inteiro, o antigo ou o novo, nunca um pedaço."""
import os
import tempfile
from pathlib import Path


def gravar(arq, texto, encoding='utf-8'):
    arq = Path(arq); arq.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=arq.parent, prefix=f'.{arq.name}.', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding=encoding) as f: f.write(texto)
        os.replace(tmp, arq)
    except BaseException:
        try: os.unlink(tmp)
        except OSError: pass
        raise
