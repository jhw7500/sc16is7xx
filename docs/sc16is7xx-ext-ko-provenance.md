# sc16is7xx_ext.ko 바이너리 provenance

## 문서 목적

이 문서는 아래 PIM 패키지 바이너리가 어느 커밋에서 유래했는지 확인한 결과와
판정 근거를 기록합니다.

`/home/jhw/ai/opencode/projects/pim-package/dist/pim/opt/pim/driver/sc16is7xx_ext.ko`

여기서는 혼동을 피하기 위해 다음 두 대상을 구분합니다.

1. 바이너리가 `pim-package`에 저장된 패키지 커밋
2. 바이너리를 빌드한 `sc16is7xx` 드라이버 소스 계보

---

## 1. 최종 결론

### 1.1 패키지 커밋

대상 바이너리는 `pim-package`의 다음 커밋에 저장된 파일과 정확히 일치합니다.

- 커밋: `e1ade54449a4237b4a7d86883f0924a5cad89867`
- 커밋 축약형: `e1ade54`
- 커밋 일시: `2026-03-31 17:49:16 +0900`
- 커밋 메시지: `fix: WiFi power_save off 안정화 및 sc16is7xx 디버깅 로그 추가`

따라서 **패키지 관점의 provenance는 `e1ade54`로 확정**할 수 있습니다.

### 1.2 드라이버 소스 계보

바이너리의 드라이버 소스 내용은 `sc16is7xx` 저장소의 초기 커밋에서 도입된
버전과 동등합니다.

- 최초 소스 커밋: `9f71cb97ff1c0fe2401a0d1b8b6ababbecac2e19`
- 커밋 축약형: `9f71cb9`
- 커밋 일시: `2026-03-31 17:44:23 +0900`

`9f71cb9` 이후 여러 커밋은 README나 보조 스크립트만 변경했고,
`sc16is7xx.c`는 `a721331` 전까지 변경되지 않았습니다. 바이너리에는 Git 커밋
해시가 내장되어 있지 않으므로 실제 빌드 당시 checkout이 이 동일 소스 구간 중
어느 커밋이었는지는 구별할 수 없습니다.

정리하면 **패키지 커밋은 `e1ade54`, 드라이버 소스 계보는 `9f71cb9` 계열**입니다.

---

## 2. 바이너리 식별값

| 항목 | 값 |
|---|---|
| 파일 크기 | `697,864 bytes` |
| Git blob | `e477b2946a0f6e88c2435521d862c45a0ba8d0c6` |
| SHA-256 | `05462e99a645a5e7386c73906bef24566e4ea80ce296deb339a7d5dc868c0793` |
| ELF Build ID | `40fabc22a7b98661f2a1289078bd4368fe25c4e8` |
| ELF 형식 | `ELF 64-bit LSB relocatable, ARM aarch64` |
| 모듈명 | `sc16is7xx_ext` |
| 드라이버 설명 | `SC16IS7XX ext serial driver v5.10.240` |
| vermagic | `5.10.35-lts-5.10.y+g2fce14defc04 SMP preempt mod_unload modversions aarch64` |

대상 파일에 `git hash-object`를 적용한 결과와 `e1ade54` 트리의 blob ID가
`e477b294...`로 일치합니다. 이 비교는 파일 내용 전체가 동일함을 의미합니다.

---

## 3. 소스 버전 판정 근거

### 3.1 바이너리에 포함되지 않은 후속 기능

대상 바이너리의 `modinfo`에는 다음 모듈 파라미터가 없습니다.

- `diag`
- `diag_period_ms`
- `rx_trigger`

이 기능들과 regmap noinc API 전환은 다음 커밋에서 추가되었습니다.

- `a7213316525f89cb5b574ffed85ce9af7064764f`
- `feat: regmap noinc API 전환, 진단 모듈 파라미터, TX 인터럽트 최적화`

따라서 대상 바이너리는 `a721331` 이후 소스로 빌드된 버전이 아닙니다.

### 3.2 빌드 경로 단서

바이너리의 디버그 정보에는 다음 컴파일 경로가 남아 있습니다.

```text
/home/jhw/ai/opencode/projects/sc16is752/sc16is7xx.c
```

이는 현재 `sc16is7xx`라는 이름으로 관리되는 저장소가 과거
`sc16is752` 작업 디렉터리에서 빌드되었음을 보여주는 단서입니다. 다만 경로
정보만으로 Git checkout 커밋을 직접 확인할 수는 없습니다.

### 3.3 커밋 시각과 변경 범위

| 시각 | 저장소 | 커밋 | 관련 내용 |
|---|---|---|---|
| 2026-03-31 17:44:23 | `sc16is7xx` | `9f71cb9` | 드라이버 소스 최초 등록 |
| 2026-03-31 17:47:07 | `sc16is7xx` | `d95022a` | README 추가, 드라이버 소스 변경 없음 |
| 2026-03-31 17:49:16 | `pim-package` | `e1ade54` | 697,864바이트 바이너리 저장 |
| 2026-04-03 16:31:30 | `sc16is7xx` | `a721331` | 드라이버 소스의 다음 실질 변경 |

패키지에 바이너리가 저장된 시점의 드라이버 소스는 `9f71cb9`에서 도입된
내용과 같았습니다.

---

## 4. 판정 범위와 한계

확정 가능한 내용은 다음과 같습니다.

- 현재 대상 파일은 `pim-package`의 `e1ade54`에 저장된 바이너리와 동일합니다.
- 소스 기능은 `a721331` 이전의 초기 `9f71cb9` 계열입니다.
- 현재 `sc16is7xx` 저장소 HEAD에서 빌드된 로컬 바이너리와는 해시 및 Build ID가
  다릅니다.

확정할 수 없는 내용은 다음과 같습니다.

- 빌드 당시 checkout한 정확한 소스 커밋
- 빌드 시각
- 커밋 이후 수정된 미커밋 소스 사용 여부

이 한계는 바이너리에 Git 커밋 해시나 별도 build provenance 메타데이터가
내장되어 있지 않기 때문입니다.

---

## 부록: 재검증 명령

```bash
TARGET=/home/jhw/ai/opencode/projects/pim-package/dist/pim/opt/pim/driver/sc16is7xx_ext.ko

file "$TARGET"
sha256sum "$TARGET"
modinfo "$TARGET"
readelf -n "$TARGET"
git -C /home/jhw/ai/opencode/projects/pim-package hash-object "$TARGET"
git -C /home/jhw/ai/opencode/projects/pim-package \
  ls-tree e1ade54 dist/pim/opt/pim/driver/sc16is7xx_ext.ko
git -C /home/jhw/ai/opencode/projects/sc16is7xx \
  diff 9f71cb9 fad5bb9 -- sc16is7xx.c Makefile
```
