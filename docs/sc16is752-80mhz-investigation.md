# SC16IS752 80 MHz 루프백 조사 정리

## 문서 목적

이 문서는 i.MX8MP 환경에서 커스텀 `sc16is7xx_ext` 드라이버와 SC16IS752를 사용해
80 MHz 외부 클럭 조건으로 동작시킨 뒤, 루프백 시험 중 발생한 RX overrun 및 데이터
유실 현상을 정리한 문서입니다.

정리 기준은 아래 3가지입니다.

1. 사실과 근거 위주로 정리
2. 이미 해본 것과 앞으로 해봐야 할 것 정리
3. 현재 시점의 최종 결론 정리

---

## 1. 사실과 근거

### 1.1 테스트 환경

- 플랫폼: i.MX8MP, Linux 5.10.35 BSP
- 외부 모듈: `sc16is7xx_ext.ko`
- 드라이버 소스: `projects/sc16is7xx/sc16is7xx.c`
- DT compatible: `cantops,sc16is752-ext`
- 테스트 스크립트: `projects/sc16is7xx/serial_loopback_error_rate.py`
- 디바이스: SC16IS752
- 외부 클럭: `XTAL1 = 80 MHz`
- 인터페이스: SPI mode 0
- TTL 시험 조건: RS-232 트랜시버를 제거하고 UART TTL 레벨에서 직접 loopback
- 실회로 정보: 실제 회로에는 UART 측에 `ST3232ECTR` 트랜시버가 존재한다고 사용자 확인

### 1.2 데이터시트 근거

참고 문서: `docs/sc126is752.pdf`

| 항목 | 근거 | 출처 |
|---|---|---|
| FIFO 깊이 | RX/TX FIFO는 64 bytes | p.1: “64 bytes FIFO (transmitter and receiver)”, p.22: “The RHR is actually a 64-byte FIFO.” |
| 최대 UART 속도 | 16× clock mode 기준 최대 5 Mbit/s | p.1 |
| SC16IS752 SPI 한계 | SC16IS752는 최대 4 Mbit/s SPI clock | p.2, §2.3 |
| 외부 클럭 범위 | 외부 clock 입력은 48~80 MHz | p.48, Table 38 |
| baud 공식 | `divisor = XTAL1 / prescaler / (desired baud × 16)` | p.16, §7.8 |
| prescaler 기본값 | reset 후 기본 prescaler는 divide-by-1 | p.16, §7.8 |
| FCR RX trigger | 8 / 16 / 56 / 60 chars | p.23, Table 12 |
| TLR RX trigger | 4~60 chars, 4 단위 조절 가능 | p.29, §8.12 |
| Overrun IRQ 원인 | OE는 receiver line status interrupt 원인 | p.14, Table 6 |
| Overrun 발생 조건 | “If not enabled, overrun errors occur if the transmit data rate exceeds the receive FIFO servicing latency.” | p.8, §7.2 |
| Hardware flow control 효과 | “If both Auto-CTS and Auto-RTS are enabled ... overrun errors are eliminated during hardware flow control.” | p.8, §7.2 |
| CTS/RTS 상태 변화 IRQ | IIR `10 0000` = CTS/RTS change of state | p.14, Table 6 |

### 1.3 80 MHz 기준 정확히 맞는 baud rate

데이터시트 공식 기준:

`baud = XTAL1 / (prescaler × 16 × divisor)`

80 MHz, prescaler=1이면:

`baud = 80,000,000 / (16 × divisor) = 5,000,000 / divisor`

따라서 실무적으로 의미 있는 exact baud는 아래와 같습니다.

| Divisor | Exact baud |
|---|---:|
| 1 | 5,000,000 |
| 2 | 2,500,000 |
| 4 | 1,250,000 |
| 5 | 1,000,000 |
| 8 | 625,000 |
| 10 | 500,000 |
| 20 | 250,000 |

### 1.4 드라이버와 로깅 관련 확인 사항

- 드라이버는 현재 다음 두 종류의 로그를 분리해서 출력합니다.
  - `ttySCx initial-config ...`
  - `ttySCx applied-serial-config requested_baud=... actual_baud=...`
- 최초 `baud=9600`처럼 오해를 부르던 로그는 제거되었습니다.
- 예전 noisy log였던 `Unexpected interrupt: 20`은 modem-status / CTS-RTS 상태 변화 interrupt로 소비하도록 정리되었습니다.
- 테스트 스크립트는 이제 **requested baud**와 **actual baud**를 분리해 보여줍니다.

### 1.5 드라이버의 RTS/CTS 지원 여부

로컬 드라이버는 이미 termios `CRTSCTS`를 지원합니다.

관련 코드:

- `projects/sc16is7xx/sc16is7xx.c:1096-1104`

동작:

- `CRTSCTS`가 켜지면 드라이버가
  - `SC16IS7XX_EFR_AUTOCTS_BIT`
  - `SC16IS7XX_EFR_AUTORTS_BIT`
  를 설정합니다.

즉, 하드웨어 흐름제어 시험을 위해 드라이버를 크게 다시 짤 필요는 없습니다.

### 1.6 현재까지의 측정 결과

#### (1) 초기 해석에서 수정된 내용

처음에는 `4M`, `3M`, `2M` 요청 속도를 각각 독립 시험으로 해석했지만,
actual baud 로그를 넣은 뒤 아래와 같이 수정되었습니다.

- requested `4,000,000` → actual `5,000,000`
- requested `3,000,000` → actual `5,000,000`
- requested `2,000,000` → actual `2,500,000`

즉, 이전 일부 테스트는 요청 속도와 실제 적용 속도가 달랐습니다.

#### (2) exact baud 기준 TTL loopback 결과

최신 exact baud 기준 결과는 아래와 같습니다.

| Requested | Actual | Direction | Error rate |
|---:|---:|---|---:|
| 2,500,000 | 2,500,000 | A->B | 4.3347% |
| 2,500,000 | 2,500,000 | B->A | 6.9513% |
| 1,250,000 | 1,250,000 | A->B | 5.1411% |
| 1,250,000 | 1,250,000 | B->A | 7.5000% |
| 1,000,000 | 1,000,000 | A->B | 0.6944% |
| 1,000,000 | 1,000,000 | B->A | 1.6204% |

핵심 관찰:

- **1,000,000에서도 error가 0이 아님**
- **1,250,000 / 2,500,000에서는 손실이 명확히 큼**

#### (3) 커널 로그 증거

대표 로그:

- `Possible RX FIFO overrun: 64 iir=0x04 lsr=0x63`
- `Possible RX FIFO overrun: 64 iir=0x04 lsr=0x61`
- `Possible RX FIFO overrun: 64 iir=0x0c lsr=0x61`

해석:

- `iir=0x04` = RX data interrupt
- `iir=0x0c` = RX timeout interrupt
- `lsr=0x63`에는 `OE`가 포함되어 실제 overrun error가 발생한 상태
- `lsr=0x61`은 항상 OE는 아니지만 FIFO가 꽉 차는 상황과 함께 반복적으로 나타남

따라서 **실제 RX overrun이 존재한다**는 점은 확실합니다.

---

## 2. 해본 것들과 해봐야 할 것들

### 2.1 이미 해본 것

#### 드라이버 측 변경

1. THRI always-on 동작 제거, on-demand TX interrupt 방식으로 정리
2. FIFO access를 `regmap_noinc_*` 경로로 변경
3. RX trigger를 TLR 기반 `rx_trigger=4`로 낮춤
4. RX FIFO full 로그를 `iir/lsr` 포함하도록 강화
5. baud 로그를 초기 설정 / 이후 변경 로그로 분리
6. 요청 baud와 실제 적용 baud를 함께 표시하도록 개선
7. `Unexpected interrupt: 20` 로그 제거

#### 테스트 스크립트 변경

1. 새 loopback 스크립트 작성: `serial_loopback_error_rate.py`
2. requested / actual baud 표시 추가
3. exact baud 기준 기본값으로 정리
4. `--use-rtscts` 옵션 추가

### 2.2 앞으로 해봐야 할 것

#### 우선순위 1: TTL 레벨 RTS/CTS 시험

이게 지금 가장 중요한 미완 테스트입니다.

권장 TTL 배선:

- `TXA -> RXB`
- `TXB -> RXA`
- `RTSA -> CTSB`
- `RTSB -> CTSA`
- GND 공통

권장 명령:

```bash
./serial_loopback_error_rate.py --use-rtscts --baud-rates 1000000,1250000,2500000 --duration 10
```

왜 중요한가:

- datasheet가 직접 Auto-RTS/CTS로 overrun 제거 가능성을 말함
- 로컬 드라이버가 이미 `CRTSCTS`를 지원함
- 지금 남은 핵심 가설, 즉 “flow control 부재 + servicing latency”를 가장 짧게 검증할 수 있음

#### 우선순위 2: 더 낮은 exact baud 검증

RTS/CTS 시험 후에도 필요하면 아래 속도까지 내려서 안정 구간을 찾는 것이 좋습니다.

```bash
./serial_loopback_error_rate.py --use-rtscts --baud-rates 625000,500000,250000 --duration 10
```

목적:

- 현재 하드웨어/드라이버 조건에서 완전 무결성 구간을 찾기 위함

#### 우선순위 3: 실제 회로 재장착 후 저속 RS-232 검증

이 단계는 **TTL + RTS/CTS 검증 이후**에 하는 것이 맞습니다.

이유:

- 실제 회로에는 `ST3232ECTR`가 존재함
- 따라서 실회로에서는 SC16 자체 외에 트랜시버 제약도 함께 받음
- 고속 검증은 TTL 단계에서 먼저 끝내는 것이 더 논리적임

실회로에서는 다음과 같이 접근하는 것이 좋습니다.

- 저속 RS-232 링크 검증
- 실사용 조건에서 end-to-end 동작 확인

---

## 3. 최종 결론

### 3.1 현재 시점의 가장 유력한 원인

지금까지의 증거를 종합하면, 현재 문제는 아래 순서로 보는 것이 가장 타당합니다.

1. **RX FIFO servicing latency 부족**
2. **TTL loopback 환경에서 hardware flow control이 활성화되지 않은 상태**
3. 그 다음으로 baud 선택과 트랜시버 조건 같은 부가 요소

이 판단은 datasheet의 아래 문장과 직접 연결됩니다.

> “If not enabled, overrun errors occur if the transmit data rate exceeds the receive FIFO servicing latency.”

출처: `docs/sc126is752.pdf`, p.8, §7.2

### 3.2 지금 테스트 결과가 증명하는 것

- 문제는 더 이상 baud 로그 오해만의 문제가 아닙니다.
- 문제는 트랜시버만의 문제도 아닙니다. TTL 레벨에서도 overrun이 납니다.
- 즉, **SC16IS752 + 현재 드라이버 경로 자체가 TTL 테스트 조건에서 이미 overrun에 취약**합니다.

### 3.3 RTS/CTS가 바꿔줄 가능성

TTL 레벨에서 RTS/CTS를 실제로 묶고 `CRTSCTS`를 켜면:

- error rate가 크게 줄 가능성이 높음
- overrun 로그가 크게 줄거나 사라질 가능성이 있음
- 이 경우 문제의 핵심은 “기본 UART 설정”이 아니라 **backpressure / servicing latency**였다는 것이 더 강하게 증명됨

### 3.4 아직 섣불리 내리면 안 되는 결론

현재 단계에서 아래처럼 단정하면 안 됩니다.

- 커스텀 드라이버가 완전히 잘못되었다
- ST3232가 유일 원인이다
- SC16IS752가 2.5M/1.25M 자체를 절대 못한다

지금 확실히 말할 수 있는 건 더 좁습니다.

- **현재 no-flow-control TTL loopback 조건에서는 1M에서도 완전 무결성이 아니다**

### 3.5 현재 가장 방어적인 다음 단계

다음 단계는 아래 순서가 가장 타당합니다.

1. **TTL + RTS/CTS loopback 수행**
2. `--use-rtscts` 사용 전후 비교
3. 그 결과를 보고 추가 드라이버 수정 필요 여부 판단

이 단계가 강하게 정당화되는 이유:

- datasheet가 직접 지지함
- 현재 드라이버가 이미 지원함
- 큰 upstream porting보다 비용이 적고 판단력이 높음

---

## 부록: 실행 명령 예시

### exact baud 현재 기준 시험

```bash
./serial_loopback_error_rate.py --baud-rates 2500000,1250000,1000000 --duration 10
```

### 권장 RTS/CTS TTL 시험

```bash
./serial_loopback_error_rate.py --use-rtscts --baud-rates 1000000,1250000,2500000 --duration 10
```

### 더 낮은 exact baud 안정 구간 확인

```bash
./serial_loopback_error_rate.py --use-rtscts --baud-rates 625000,500000,250000 --duration 10
```
