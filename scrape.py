import json, os
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

SETS = [f"OP{n:02d}" for n in range(1, 16)]  # [김윤서] 먼저 테스트용으로 OP15만 해보자
KST = timezone(timedelta(hours=9))
os.makedirs("data", exist_ok=True)

JS = """els => els.map(e => ({
  name: e.querySelector('.archetype-tile-name')?.textContent.trim(),
  decks: e.querySelector('.archetype-tile-count')?.textContent.trim(),
  share: e.querySelector('.archetype-tile-share')?.textContent.trim()
}))"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    for s in SETS:
        try:
            page.goto(f"https://deckbuilder.egmanevents.com/optcg/meta?set={s}",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector(".archetype-tile", timeout=20000)
            page.wait_for_timeout(1500)
            tiles = page.eval_on_selector_all(".archetype-tile", JS)
        except Exception as e:
            print(f"{s}: 실패 ({e})")
            continue
        if not tiles:
            continue
        with open(f"data/{s}.json", "w", encoding="utf-8") as f:
            json.dump({"set": s,
                       "updated": datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
                       "decks": tiles}, f, ensure_ascii=False, indent=1)
        print(f"{s}: {len(tiles)}개 저장")
    browser.close()
