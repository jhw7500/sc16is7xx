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

```bash
./make-for-imx8
```

빌드 환경 변수는 `make-for-imx8` 스크립트에 정의되어 있습니다.
`KERNEL_SRC`, `KBUILD_OUTPUT`, `ARCH`, `CROSS_COMPILE`을 환경에 맞게 수정하세요.

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
| `setup_for_pim` | PIM 빌드 환경 설정 스크립트 |

## 라이선스

GPL-2.0+
