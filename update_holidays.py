"""공공데이터포털 '한국천문연구원_특일 정보'에서 공휴일을 받아 holidays.json을 만든다.

GitHub Actions가 매주 실행한다. 인증키는 저장소 Secret(DATA_GO_KR_KEY)에만 있고 데꾸 앱에는 없다.
올해와 내년 것을 받아서, 예전 해의 기록은 그대로 둔 채 합친다.
실패하면(키 오류, 서버 점검 등) 파일을 건드리지 않고 오류로 끝난다.

필요한 것: Python 3 표준 라이브러리만.
"""

import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

API = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
OUTPUT = "holidays.json"


def fetch_month(key: str, year: int, month: int) -> list[dict]:
    query = urllib.parse.urlencode({
        "solYear": year,
        "solMonth": f"{month:02d}",
        "numOfRows": 50,
        "_type": "json",
    })
    # 포털에서 주는 "인코딩된 키"를 그대로 붙인다 (다시 인코딩하면 키가 망가진다)
    url = f"{API}?serviceKey={key}&{query}"
    with urllib.request.urlopen(url, timeout=30) as response:
        text = response.read().decode("utf-8")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # 키가 틀리면 JSON 대신 XML 오류가 온다
        raise RuntimeError(f"{year}-{month:02d}: API가 JSON이 아닌 응답을 보냈어요: {text[:200]}")

    header = data["response"]["header"]
    if header.get("resultCode") != "00":
        raise RuntimeError(f"{year}-{month:02d}: {header}")

    items = data["response"]["body"].get("items") or {}
    item = items.get("item", []) if isinstance(items, dict) else []
    if isinstance(item, dict):  # 하나뿐이면 목록이 아니라 하나로 온다
        item = [item]
    return [i for i in item if i.get("isHoliday") == "Y"]


def main() -> int:
    key = os.environ.get("DATA_GO_KR_KEY", "").strip()
    if not key:
        print("DATA_GO_KR_KEY가 없어요. 저장소 Settings > Secrets에 넣어 주세요.", file=sys.stderr)
        return 1

    today = datetime.date.today()
    years = [today.year, today.year + 1]

    fetched = []
    for year in years:
        for month in range(1, 13):
            for item in fetch_month(key, year, month):
                date = str(item["locdate"])
                fetched.append({
                    "date": f"{date[:4]}-{date[4:6]}-{date[6:]}",
                    "name": item["dateName"].strip(),
                    "comment": item["dateName"].strip(),
                })

    # 이번에 받은 해는 새것으로, 나머지 해(예전 기록)는 그대로.
    # 손으로 넣은 날("manual": true)은 API에 아직 없어도 지우지 않는다
    old = {"days": []}
    if os.path.exists(OUTPUT):
        # utf-8-sig: 윈도우 메모장으로 고쳐서 BOM이 붙어 있어도 읽는다
        with open(OUTPUT, encoding="utf-8-sig") as f:
            old = json.load(f)
    fetched_dates = {d["date"] for d in fetched}
    kept = [
        d for d in old.get("days", [])
        if int(d["date"][:4]) not in years or (d.get("manual") and d["date"] not in fetched_dates)
    ]
    days = sorted(kept + fetched, key=lambda d: (d["date"], d["name"]))

    if days == old.get("days"):
        print("바뀐 게 없어요.")
        return 0

    result = {
        "updated": today.isoformat(),
        "source": "공공데이터포털 한국천문연구원 특일 정보 (getRestDeInfo)",
        "days": days,
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"{len(days)}개 날짜로 갱신했어요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
