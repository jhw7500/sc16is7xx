# sc16is7xx_ext.ko 바이너리 provenance

## 문서 목적

이 문서는 `sc16is7xx_ext.ko`를 사용하는 PIM 패키지별 바이너리가 어느
`sc16is7xx` 소스에서 유래했는지 기록하는 중앙 provenance 문서입니다.

확인 대상은 다음 두 패키지 저장소입니다.

1. `/home/jhw/ai/opencode/projects/pim-package` (GitLab 정식 릴리스)
2. `/home/jhw/ai/opencode/projects/pim-package-jhw` (개인 GitHub workflow)

`pim-package-jhw`에서 `pim-package`로 동기화할 때 `sc16is7xx_ext.ko`는 제외합니다.
따라서 두 패키지의 드라이버 버전은 자동으로 같아지지 않으며, 각 패키지의
provenance를 독립적으로 관리합니다.

패키지 커밋과 드라이버 소스 커밋은 서로 다른 저장소의 SHA입니다. 이 문서는
둘을 명확히 구분하고, 작업자가 현재 `master`를 재빌드해 기존 릴리스
바이너리를 의도치 않게 업그레이드하는 일을 방지합니다.

> **운영 경고:** 두 패키지는 파일명이 같은 `sc16is7xx_ext.ko`를 포함하지만
> 현재 바이너리의 소스 버전이 서로 다릅니다. 빌드 또는 복사 전에 대상 패키지와
> 기록된 source commit을 반드시 확인해야 합니다.

---

## 1. 패키지별 최종 결론

검증일: **2026-08-25**

| 패키지 저장소 | 패키지 커밋 | 드라이버 소스 기준 | 크기 | SHA-256 |
|---|---|---|---:|---|
| `pim-package` | `e1ade54` | `9f71cb9` 계열 | 697,864 | `05462e99...c0793` |
| `pim-package-jhw` | `158fff4` | `1788388` | 550,888 | `1b38dd57...6fe2` |

- `pim-package`는 정식 릴리스이며 source repo `master`는 이 패키지의
  `9f71cb9` 소스 내용과 맞춰 관리합니다.
- `pim-package-jhw`는 개인 GitHub workflow용이며 critical regression 수정
  PR #3가 합쳐진 `1788388` 기준입니다.
- 같은 vermagic을 사용하지만 기능과 수정 수준이 다르므로 서로를 단순 복사해
  덮어쓰면 안 됩니다.

---

## 2. pim-package 바이너리

### 2.1 패키지 커밋

대상 바이너리는 `pim-package`의 다음 커밋에 저장된 파일과 정확히 일치합니다.

- 커밋: `e1ade54449a4237b4a7d86883f0924a5cad89867`
- 커밋 축약형: `e1ade54`
- 커밋 일시: `2026-03-31 17:49:16 +0900`
- 커밋 메시지: `fix: WiFi power_save off 안정화 및 sc16is7xx 디버깅 로그 추가`

따라서 **패키지 관점의 provenance는 `e1ade54`로 확정**할 수 있습니다.

### 2.2 드라이버 소스 계보

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

## 3. pim-package 바이너리 식별값

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

## 4. pim-package 소스 버전 판정 근거

### 4.1 바이너리에 포함되지 않은 후속 기능

대상 바이너리의 `modinfo`에는 다음 모듈 파라미터가 없습니다.

- `diag`
- `diag_period_ms`
- `rx_trigger`

이 기능들과 regmap noinc API 전환은 다음 커밋에서 추가되었습니다.

- `a7213316525f89cb5b574ffed85ce9af7064764f`
- `feat: regmap noinc API 전환, 진단 모듈 파라미터, TX 인터럽트 최적화`

따라서 대상 바이너리는 `a721331` 이후 소스로 빌드된 버전이 아닙니다.

### 4.2 빌드 경로 단서

바이너리의 디버그 정보에는 다음 컴파일 경로가 남아 있습니다.

```text
/home/jhw/ai/opencode/projects/sc16is752/sc16is7xx.c
```

이는 현재 `sc16is7xx`라는 이름으로 관리되는 저장소가 과거
`sc16is752` 작업 디렉터리에서 빌드되었음을 보여주는 단서입니다. 다만 경로
정보만으로 Git checkout 커밋을 직접 확인할 수는 없습니다.

### 4.3 커밋 시각과 변경 범위

| 시각 | 저장소 | 커밋 | 관련 내용 |
|---|---|---|---|
| 2026-03-31 17:44:23 | `sc16is7xx` | `9f71cb9` | 드라이버 소스 최초 등록 |
| 2026-03-31 17:47:07 | `sc16is7xx` | `d95022a` | README 추가, 드라이버 소스 변경 없음 |
| 2026-03-31 17:49:16 | `pim-package` | `e1ade54` | 697,864바이트 바이너리 저장 |
| 2026-04-03 16:31:30 | `sc16is7xx` | `a721331` | 드라이버 소스의 다음 실질 변경 |

패키지에 바이너리가 저장된 시점의 드라이버 소스는 `9f71cb9`에서 도입된
내용과 같았습니다.

---

## 5. pim-package-jhw 바이너리

### 5.1 패키지 및 소스 커밋

`pim-package-jhw`의 현재 바이너리는 다음 패키지 커밋에서 반영되었습니다.

- 패키지 커밋: `158fff47257d0ce875f24f03f13ac2c49c78027d`
- 커밋 일시: `2026-07-24 16:57:04 +0900`
- 커밋 메시지: `chore(pim): sc16is7xx_ext.ko 업데이트 (critical regressions 수정)`
- 기록된 source commit: `1788388e038760c899e78009e6a4b1b0e3bdfc8c`

`1788388`은 PR #3 merge commit입니다. 이 트리의 `sc16is7xx.c`는 PR의 마지막
소스 변경 커밋 `85a3de446edc1b3d4f67ea97364e41e0e727713e`와 동일합니다.

### 5.2 바이너리 식별값

| 항목 | 값 |
|---|---|
| 파일 크기 | `550,888 bytes` |
| Git LFS SHA-256 OID | `1b38dd57647123b62674757e89483182555605c246dc7c321ccd7e932b5b6fe2` |
| ELF Build ID | `9cb171f3153cc8b5b8fec8151f1e6a73fafd1a2b` |
| ELF 형식 | `ELF 64-bit LSB relocatable, ARM aarch64` |
| 모듈명 | `sc16is7xx_ext` |
| 드라이버 설명 | `SC16IS7XX ext serial driver v5.10.240` |
| vermagic | `5.10.35-lts-5.10.y+g2fce14defc04 SMP preempt mod_unload modversions aarch64` |

패키지의 Git LFS pointer OID와 이 저장소의 로컬 빌드 산출물 SHA-256이
`1b38dd57...`로 일치합니다.

### 5.3 포함된 후속 기능과 수정

이 바이너리의 `modinfo`에는 다음 모듈 파라미터가 있습니다.

- `diag`
- `diag_period_ms`
- `rx_trigger`

또한 `a721331`의 regmap noinc 및 TX interrupt 변경과 PR #3의 다음 수정이
포함되어 있습니다.

- port close 경로의 spinlock self-deadlock 수정
- atomic context에서 sleeping regmap API를 호출하던 문제 수정
- FIFO write가 regcache를 오염시키던 문제 수정
- `ier_clear`와 `fifo_write`의 lockdep assertion 추가

---

## 6. 소스 브랜치 정책과 패키지 바이너리 관계

2026-08-25부터 소스 브랜치는 다음 역할로 관리합니다.

| 항목 | 값 |
|---|---|
| `master` 역할 | GitLab 정식 `pim-package` 릴리스 소스 |
| `master` 기준 소스 커밋 | `9f71cb97ff1c0fe2401a0d1b8b6ababbecac2e19` |
| `master:sc16is7xx.c` 기대 blob | `62675b6ee0811dbf6e7bcad0ef95fc534a08a6ae` |
| `fix/sc16is7xx-critical-regressions` 역할 | 개인 GitHub workflow용 최신 수정 소스 |
| 최신 내용의 merge commit | `1788388e038760c899e78009e6a4b1b0e3bdfc8c` |
| 실제 마지막 드라이버 변경 커밋 | `85a3de446edc1b3d4f67ea97364e41e0e727713e` |
| fix 브랜치 `sc16is7xx.c` 기대 blob | `070bb868090420f23bebce8bfc1cd17173d20276` |

`master`는 전체 Git 이력과 문서를 유지하면서 `sc16is7xx.c` 내용만 정식
릴리스 기준으로 복원합니다. 최신 수정 소스와 이 문서는 fix 브랜치에도
보존합니다. 이 구성은 history rewrite 없이 두 사용 목적을 분리합니다.

브랜치 HEAD만 비교해서는 안 됩니다. 문서나 CI만 변경된 커밋일 수 있으므로
항상 `git rev-parse <ref>:sc16is7xx.c`로 드라이버 소스 blob도 함께 기록합니다.

---

## 7. 빌드 및 패키지 반영 게이트

### 7.1 빌드 전

```bash
cd /home/jhw/ai/opencode/projects/sc16is7xx
git status --short
git rev-parse HEAD
git rev-parse HEAD:sc16is7xx.c
```

- working tree가 dirty하면 미커밋 소스를 포함할 수 있으므로 패키지에 반영하지
  않습니다.
- 정식 `pim-package` 빌드는 `master`의 source blob `62675b6e...`를 확인합니다.
- 개인 `pim-package-jhw` 빌드는 기록된 `1788388` 또는
  `fix/sc16is7xx-critical-regressions`의 source blob `070bb868...`을 확인합니다.
- source blob이 다르면 단순 재빌드가 아니라 드라이버 버전 변경으로 취급합니다.

### 7.2 빌드 후

```bash
./make-for-imx8
sha256sum sc16is7xx_ext.ko
modinfo sc16is7xx_ext.ko
readelf -n sc16is7xx_ext.ko
```

SHA-256, ELF Build ID, vermagic, module parameters를 확인합니다. 빌드 경로,
툴체인 또는 커널 빌드 산출물이 다르면 같은 소스에서도 전체 바이너리 해시가
달라질 수 있으므로 source blob과 `modinfo`를 함께 판정 근거로 사용합니다.

### 7.3 패키지 반영 후 기록

패키지 커밋 메시지나 동반 문서에는 최소한 다음 정보를 남깁니다.

```text
sc16is7xx source commit: <full SHA>
sc16is7xx.c blob: <blob SHA>
sc16is7xx_ext.ko sha256: <SHA-256>
ELF Build ID: <Build ID>
vermagic: <vermagic>
board verification: <결과>
```

파일명, 패키지 커밋 SHA 또는 vermagic만으로 소스 버전을 추정하지 않습니다.

---

## 8. 판정 범위와 한계

확정 가능한 내용은 다음과 같습니다.

- `pim-package` 대상 파일은 `e1ade54`에 저장된 바이너리와 동일합니다.
- `pim-package` 바이너리는 `a721331` 이전의 초기 `9f71cb9` 소스 계열입니다.
- `pim-package-jhw` 대상 파일은 `158fff4`의 Git LFS 객체와 동일합니다.
- `pim-package-jhw` 패키지 커밋은 source commit `1788388`을 명시합니다.
- 현재 로컬 빌드 산출물과 `pim-package-jhw` 바이너리의 SHA-256 및 Build ID가
  일치합니다.

확정할 수 없는 내용은 다음과 같습니다.

- `pim-package` 구형 바이너리를 빌드할 때 checkout한 정확한 소스 커밋
- `pim-package` 구형 바이너리의 정확한 빌드 시각
- 바이너리 생성 시점에 미커밋 소스가 있었는지 여부

이 한계는 바이너리에 Git 커밋 해시나 별도 build provenance 메타데이터가
내장되어 있지 않기 때문입니다.

---

## 부록: 재검증 명령

```bash
GITLAB_TARGET=/home/jhw/ai/opencode/projects/pim-package/dist/pim/opt/pim/driver/sc16is7xx_ext.ko
GITHUB_TARGET=/home/jhw/ai/opencode/projects/pim-package-jhw/dist/pim/opt/pim/driver/sc16is7xx_ext.ko

sha256sum "$GITLAB_TARGET" "$GITHUB_TARGET" sc16is7xx_ext.ko
modinfo "$GITLAB_TARGET"
modinfo "$GITHUB_TARGET"
readelf -n "$GITLAB_TARGET"
readelf -n "$GITHUB_TARGET"

git -C /home/jhw/ai/opencode/projects/pim-package \
  hash-object "$GITLAB_TARGET"
git -C /home/jhw/ai/opencode/projects/pim-package \
  ls-tree e1ade54 dist/pim/opt/pim/driver/sc16is7xx_ext.ko

git -C /home/jhw/ai/opencode/projects/pim-package-jhw \
  show 158fff4:dist/pim/opt/pim/driver/sc16is7xx_ext.ko

git rev-parse HEAD
git rev-parse HEAD:sc16is7xx.c
git rev-parse 9f71cb9:sc16is7xx.c
git rev-parse 1788388:sc16is7xx.c
git rev-parse origin/master:sc16is7xx.c
git rev-parse origin/fix/sc16is7xx-critical-regressions:sc16is7xx.c
```
