"""Site no navegador (Playwright + Chromium): só roda onde o Playwright estiver instalado (não no CI)."""
import subprocess
import sys
import time

import pytest

pw = pytest.importorskip('playwright.sync_api')


def test_site_no_navegador(tmp_path):
    from dh import site
    site.gerar(tmp_path / 'index.html')
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8799'], cwd=tmp_path,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    erros = []
    try:
        time.sleep(0.8)
        with pw.sync_playwright() as p:
            br = p.chromium.launch(); pg = br.new_page()
            pg.on('pageerror', lambda e: erros.append(str(e)))
            pg.on('console', lambda m: m.type == 'error' and erros.append(m.text))
            pg.goto('http://localhost:8799/index.html'); pg.wait_for_selector('#corpo tr[data-id]')
            n = lambda: pg.locator('#corpo tr[data-id]').count()
            pg.click('[data-aba=padrao]'); sem = n()
            pg.check('#rpg'); com = n()
            assert com > sem
            nv = pg.eval_on_selector_all('#nvsel option', 'os=>os.map(o=>o.value)')[2]
            pg.select_option('#nvsel', nv)
            assert set(pg.eval_on_selector_all('#corpo tr td:nth-child(2)', 'ts=>ts.map(t=>t.textContent)')) == {nv}
            pg.select_option('#nvsel', '')
            pg.click('[data-aba=legado]'); pg.uncheck('#sop')
            assert n() == 150 and pg.is_visible('#mais')
            pg.click('#mais'); assert n() > 150
            pg.click('#corpo tr[data-id]:first-child'); pg.wait_for_selector('#det .cards', timeout=10000)
            assert pg.locator('#det .res .r').count() == 7 and pg.locator('#det svg.radar').count() == 1
            op = pg.eval_on_selector_all('#cmp option', 'os=>os.map(o=>o.value)')[3]
            pg.select_option('#cmp', op); pg.wait_for_selector('#det table.cmp', timeout=10000)
            assert pg.locator('#det table.cmp tbody tr').count() > 5
            br.close()
    finally:
        srv.terminate()
    assert not erros, erros
