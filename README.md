# SC16IS7XX External UART Driver

NXP SC16IS752/762 SPI-to-UART 커널 모듈 드라이버 (외부 빌드용)

## 개요

- **칩셋**: NXP SC16IS752 (Dual UART), SC16IS762
- **인터페이스**: SPI
- **타겟 커널**: Linux 5.10.35 (NXP i.MX8MP BSP)
- **모듈명**: `sc16is7xx_ext.ko`
- **DT compatible**: `cantops,sc16is752-ext`

커널 내장 `sc16is7xx` 드라이버와 독립적으로 동작하는 외부 모듈입니다.
별도의 compatible string(`cantops,sc16is752-ext`)을 사용하여 내장 드라이버와 충돌하지 않습니다.

## 주요 기능

- Dual full-duplex UART (채널 A/B)
- 64 byte TX/RX FIFO
- Baud rate: 최대 921,600 bps (14.7456 MHz 크리스탈 기준)
- 하드웨어/소프트웨어 Flow Control (Auto-RTS/CTS, Xon/Xoff)
- RS-485 지원
- 8개 프로그래머블 GPIO
- Sleep mode 지원

## Baud Rate 설정

`stty`로 설정하면 드라이버가 자동으로 prescaler와 divisor를 계산합니다.

```
divisor = (XTAL_freq / prescaler) / (baud_rate x 16)

prescaler = 1 (MCR[7]=0, 기본값)
prescaler = 4 (MCR[7]=1, divisor >= 65536일 때 자동 전환)
```

### 14.7456 MHz 크리스탈 기준

| Baud Rate | Divisor | 오차 |
|-----------|---------|------|
| 9,600 | 96 | 0% |
| 115,200 | 8 | 0% |
| 460,800 | 2 | 0% |
| 921,600 | 1 | 0% |

## 빌드

### 크로스 컴파일 (iMX8MP)

호스트별 경로는 저장소에 없습니다. 처음 한 번만 `.env`를 만듭니다.

```bash
cp .env.example .env       # 편집기로 열어 경로를 채웁니다
./make-for-imx8
```

`.env`는 `.gitignore` 대상이라 호스트마다 값이 달라도 커밋이 충돌하지 않습니다.
채워야 할 항목의 정본은 `.env.example`입니다.

| 변수 | 무엇인가 | 비울 수 있나 |
|---|---|---|
| `SDK_LOC` | Yocto SDK 설치 위치 | 아니오 |
| `SDK_NAME` | SDK 타깃 이름 (`cortexa53-crypto-poky-linux`) | 아니오 |
| `KERNEL_SRC` | 커널 **소스 트리** (`arch/arm64/configs`가 있는 쪽) | 아니오 |
| `KBUILD_OUTPUT` | 커널 **빌드 디렉터리** (`.config`·`include/config/auto.conf`가 있는 쪽) | 예 — 결합형 트리면 비웁니다 |

`.env`가 없거나 위 셋 중 하나가 비면 빌드 전에 멈추고 무엇을 채워야 하는지 알려줍니다.

우선순위는 **환경변수 > `.env`**입니다. 일회성으로 다른 트리에 빌드하려면 `.env`를
고치지 말고 앞에 붙입니다.

```bash
KERNEL_SRC=/다른/커널/소스 KBUILD_OUTPUT=/다른/커널/빌드 ./make-for-imx8
```

배포판 `linux-headers`처럼 소스와 빌드가 **한 디렉터리에 합쳐진** 트리면
`KBUILD_OUTPUT`을 비웁니다 — 비면 `O=`가 붙지 않습니다.

```bash
make KERNEL_SRC=/usr/src/linux-headers-5.10.0-generic
```

`ARCH=arm64`와 `CROSS_COMPILE=aarch64-poky-linux-`는 타깃 고정값이라 `make-for-imx8`이
직접 넘깁니다.

### Yocto devshell

```bash
bitbake -c devshell linux-imx

# devshell 내에서:
make M=/path/to/this/directory modules
```

### 클린

```bash
./make-for-imx8 clean
```

## 타겟 설치

```bash
scp sc16is7xx_ext.ko root@<target-ip>:/lib/modules/$(uname -r)/extra/
ssh root@<target-ip> 'depmod -a && modprobe sc16is7xx_ext'
```

## Device Tree 예시

```dts
&ecspi1 {
    sc16is752: sc16is752@0 {
        compatible = "cantops,sc16is752-ext";
        reg = <0>;
        spi-max-frequency = <4000000>;
        clocks = <&sc16is752_clk>;
        /* 또는 clock-frequency = <14745600>; */
        interrupt-parent = <&gpio1>;
        interrupts = <10 IRQ_TYPE_EDGE_FALLING>;
    };
};
```

## 파일 구조

| 파일 | 설명 |
|------|------|
| `sc16is7xx.c` | 메인 드라이버 소스 (UART + SPI) |
| `sc16is7xx.h` | 공용 헤더 (최신 커널 분리 구조 참고용) |
| `Makefile` | 커널 모듈 빌드 스크립트 |
| `make-for-imx8` | iMX8MP 크로스 컴파일 스크립트 |

## 라이선스

GPL-2.0+
