# dekku-data

데꾸 앱이 받아 가는 데이터 파일 저장소예요.

- `holidays.json`: 임시공휴일·선거일처럼 미리 계산할 수 없는 빨간날 목록
  - 데꾸는 하루 한 번 이 파일을 받아서, 직접 계산한 공휴일에 없는 날만 더해요.
  - 몇 KB짜리 파일이라 용량 걱정은 없어요.
- `update_holidays.py`: 공공데이터포털 특일 정보 API로 `holidays.json`을 새로 만드는 스크립트
- `.github/workflows/update-holidays.yml`: 위 스크립트를 매주 월요일에 자동으로 실행

인증키는 이 저장소의 Secret에만 있어요. 데꾸 앱 안에는 들어가지 않아요.

## 처음 한 번 설정하기

1. **API 신청**: [공공데이터포털](https://www.data.go.kr)에서 "한국천문연구원_특일 정보"를 활용신청해요. 개발계정은 보통 바로 승인돼요.
2. **인증키 복사**: 마이페이지 → 활용신청 현황에서 **일반 인증키 (Encoding)**를 복사해요.
3. **저장소 만들기**: GitHub에 `dekku-data`라는 **공개(Public)** 저장소를 만들고, 이 폴더의 파일을 올려요.
   - 공개 저장소여야 데꾸가 로그인 없이 `holidays.json`을 받을 수 있어요.
   - 인증키는 Secret에 들어가서 공개되지 않아요.
4. **Secret 넣기**: 저장소 Settings → Secrets and variables → Actions → New repository secret
   - Name: `DATA_GO_KR_KEY`
   - Secret: 2번에서 복사한 키
5. **처음 실행**: Actions 탭 → "공휴일 목록 갱신" → Run workflow. 초록색 체크가 뜨면 성공이에요.
6. **데꾸에 주소 넣기**: `Dekku/HolidayFeed.cs`의 `Url`에서 `OWNER`를 내 GitHub 계정 이름으로 바꿔요.

## 급하게 임시공휴일이 생겼을 때

API에 반영되기 전이라도 `holidays.json`의 `days`에 한 줄을 직접 넣고 올리면, 하루 안에 모든 데꾸 사용자에게 반영돼요.
`"manual": true`를 꼭 붙여 주세요. 그래야 다음 자동 갱신 때 API에 아직 없어도 지워지지 않아요. API에 같은 날이 들어오면 자동으로 API 것으로 바뀌어요.

```json
{ "date": "2027-01-04", "name": "임시공휴일", "comment": "신정 연휴 임시공휴일", "manual": true }
```
