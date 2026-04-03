#!/usr/bin/env python3
"""SC16IS7xx UART loopback error-rate tester.

This script sends framed test traffic from one UART port to another and measures
how many frames are recovered intact. It is designed for ttySC0/ttySC1 TTL
loopback testing on the SC16IS752/762 driver work in this repository.
"""

from __future__ import annotations

import argparse
import struct
import threading
import time
import zlib
from dataclasses import dataclass
from typing import Iterable, List


MAGIC = b"SC16"
HEADER = struct.Struct("<4sII")
DEFAULT_XTAL_HZ = 80_000_000
DEFAULT_BAUD_RATES = [5_000_000, 2_500_000, 1_250_000, 1_000_000]


@dataclass
class FrameAnalysis:
    valid_frames: int
    missing_frames: int
    estimated_gap_frames: int
    corrupt_candidates: int
    leading_noise_bytes: int
    trailing_bytes: int


@dataclass
class TestResult:
    baudrate: int
    actual_baud: int
    direction: str
    tx_port: str
    rx_port: str
    duration_s: float
    sent_frames: int = 0
    sent_bytes: int = 0
    received_bytes: int = 0
    valid_frames: int = 0
    missing_frames: int = 0
    estimated_gap_frames: int = 0
    corrupt_candidates: int = 0
    leading_noise_bytes: int = 0
    trailing_bytes: int = 0
    elapsed_s: float = 0.0
    status: str = "ok"
    error: str = ""

    @property
    def valid_bytes(self) -> int:
        return self.valid_frames * self.frame_size

    @property
    def estimated_error_bytes(self) -> int:
        return max(self.sent_bytes - self.valid_bytes, 0)

    @property
    def frame_error_rate_pct(self) -> float:
        if not self.sent_frames:
            return 0.0
        return (self.missing_frames / self.sent_frames) * 100.0

    @property
    def byte_error_rate_pct(self) -> float:
        if not self.sent_bytes:
            return 0.0
        return (self.estimated_error_bytes / self.sent_bytes) * 100.0

    @property
    def rx_rate_kib_s(self) -> float:
        if self.elapsed_s <= 0:
            return 0.0
        return (self.received_bytes / 1024.0) / self.elapsed_s

    @property
    def tx_rate_kib_s(self) -> float:
        if self.elapsed_s <= 0:
            return 0.0
        return (self.sent_bytes / 1024.0) / self.elapsed_s

    @property
    def baud_error_rate_pct(self) -> float:
        if not self.baudrate:
            return 0.0
        return ((self.actual_baud - self.baudrate) / self.baudrate) * 100.0

    frame_size: int = 0


def parse_baud_rates(text: str) -> List[int]:
    values = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(int(item))
    if not values:
        raise argparse.ArgumentTypeError("at least one baud rate is required")
    return values


def calculate_driver_baud(xtal_hz: int, requested_baud: int) -> tuple[int, int, int]:
    if xtal_hz <= 0:
        raise ValueError("xtal_hz must be positive")
    if requested_baud <= 0:
        raise ValueError("requested_baud must be positive")

    prescaler = 1
    div = xtal_hz // 16 // requested_baud
    if div >= (1 << 16):
        prescaler = 4
        div //= prescaler
    if div < 1:
        raise ValueError(
            f"requested baud {requested_baud} is too high for xtal {xtal_hz}"
        )

    actual_baud = round((xtal_hz / prescaler) / 16 / div)
    return actual_baud, prescaler, div


def build_payload_cache(payload_size: int) -> List[bytes]:
    return [
        bytes(((offset + i) & 0xFF) for i in range(payload_size))
        for offset in range(256)
    ]


def make_frame(seq: int, payload_cache: List[bytes], frame_size: int) -> bytes:
    payload = payload_cache[seq & 0xFF]
    if len(payload) != frame_size - HEADER.size:
        raise ValueError("payload cache size mismatch")
    crc = zlib.crc32(struct.pack("<I", seq) + payload) & 0xFFFFFFFF
    return HEADER.pack(MAGIC, seq, crc) + payload


def analyze_rx_stream(
    raw: bytes, sent_frames: int, frame_size: int, payload_cache: List[bytes]
) -> FrameAnalysis:
    valid_frames = 0
    expected_seq = None
    estimated_gap_frames = 0
    corrupt_candidates = 0
    first_valid_offset = None
    last_consumed_offset = 0
    idx = 0

    while idx + frame_size <= len(raw):
        if raw[idx : idx + 4] != MAGIC:
            idx += 1
            continue

        frame = raw[idx : idx + frame_size]
        _, seq, crc = HEADER.unpack_from(frame)
        payload = frame[HEADER.size :]
        expect_crc = (
            zlib.crc32(struct.pack("<I", seq) + payload_cache[seq & 0xFF]) & 0xFFFFFFFF
        )

        if crc != expect_crc or payload != payload_cache[seq & 0xFF]:
            corrupt_candidates += 1
            idx += 1
            continue

        if first_valid_offset is None:
            first_valid_offset = idx

        if expected_seq is None:
            estimated_gap_frames += seq
        elif seq > expected_seq:
            estimated_gap_frames += seq - expected_seq
        elif seq < expected_seq:
            corrupt_candidates += 1
            idx += 1
            continue

        valid_frames += 1
        expected_seq = seq + 1
        idx += frame_size
        last_consumed_offset = idx

    if expected_seq is None:
        missing_frames = sent_frames
    else:
        missing_frames = max(sent_frames - valid_frames, 0)
        if sent_frames > expected_seq:
            estimated_gap_frames += sent_frames - expected_seq

    leading_noise_bytes = (
        first_valid_offset if first_valid_offset is not None else len(raw)
    )
    trailing_bytes = (
        len(raw) - last_consumed_offset if last_consumed_offset else len(raw)
    )

    return FrameAnalysis(
        valid_frames=valid_frames,
        missing_frames=missing_frames,
        estimated_gap_frames=estimated_gap_frames,
        corrupt_candidates=corrupt_candidates,
        leading_noise_bytes=leading_noise_bytes,
        trailing_bytes=trailing_bytes,
    )


def open_serial(
    port_name: str,
    baudrate: int,
    timeout: float,
    write_timeout: float,
    rtscts: bool = False,
):
    import serial

    return serial.Serial(
        port=port_name,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout,
        write_timeout=write_timeout,
        xonxoff=False,
        rtscts=rtscts,
        dsrdtr=False,
    )


def run_one_direction(
    tx_port_name: str,
    rx_port_name: str,
    baudrate: int,
    actual_baud: int,
    duration_s: float,
    frame_size: int,
    read_size: int,
    frames_per_batch: int,
    read_timeout: float,
    write_timeout: float,
    drain_grace_s: float,
    direction: str,
    rtscts: bool = False,
) -> TestResult:
    payload_cache = build_payload_cache(frame_size - HEADER.size)
    result = TestResult(
        baudrate=baudrate,
        actual_baud=actual_baud,
        direction=direction,
        tx_port=tx_port_name,
        rx_port=rx_port_name,
        duration_s=duration_s,
        frame_size=frame_size,
    )

    try:
        tx_ser = open_serial(
            tx_port_name,
            baudrate,
            timeout=read_timeout,
            write_timeout=write_timeout,
            rtscts=rtscts,
        )
        rx_ser = open_serial(
            rx_port_name,
            baudrate,
            timeout=read_timeout,
            write_timeout=write_timeout,
            rtscts=rtscts,
        )
    except Exception as exc:
        result.status = "open_failed"
        result.error = str(exc)
        return result

    rx_buffer = bytearray()
    stop_event = threading.Event()
    sent_state = {"frames": 0, "bytes": 0}

    def tx_worker() -> None:
        seq = 0
        deadline = time.monotonic() + duration_s
        while time.monotonic() < deadline and not stop_event.is_set():
            batch = []
            batch_frames = 0
            for _ in range(frames_per_batch):
                if time.monotonic() >= deadline or stop_event.is_set():
                    break
                batch.append(make_frame(seq, payload_cache, frame_size))
                seq += 1
                batch_frames += 1
            if not batch:
                break
            blob = b"".join(batch)
            tx_ser.write(blob)
            sent_state["frames"] += batch_frames
            sent_state["bytes"] += len(blob)
        tx_ser.flush()

    def rx_worker() -> None:
        while not stop_event.is_set():
            chunk = rx_ser.read(read_size)
            if chunk:
                rx_buffer.extend(chunk)
        drain_deadline = time.monotonic() + drain_grace_s
        while time.monotonic() < drain_deadline:
            chunk = rx_ser.read(read_size)
            if not chunk:
                continue
            rx_buffer.extend(chunk)

    try:
        tx_ser.reset_input_buffer()
        tx_ser.reset_output_buffer()
        rx_ser.reset_input_buffer()
        rx_ser.reset_output_buffer()

        start = time.monotonic()
        rx_thread = threading.Thread(target=rx_worker, daemon=True)
        tx_thread = threading.Thread(target=tx_worker, daemon=True)
        rx_thread.start()
        tx_thread.start()
        tx_thread.join()
        stop_event.set()
        rx_thread.join()
        result.elapsed_s = time.monotonic() - start
    except KeyboardInterrupt:
        stop_event.set()
        result.status = "interrupted"
        result.error = "interrupted by user"
    except Exception as exc:
        stop_event.set()
        result.status = "runtime_error"
        result.error = str(exc)
    finally:
        tx_ser.close()
        rx_ser.close()

    result.sent_frames = sent_state["frames"]
    result.sent_bytes = sent_state["bytes"]
    result.received_bytes = len(rx_buffer)

    if result.status != "ok":
        return result

    analysis = analyze_rx_stream(
        bytes(rx_buffer), result.sent_frames, frame_size, payload_cache
    )
    result.valid_frames = analysis.valid_frames
    result.missing_frames = analysis.missing_frames
    result.estimated_gap_frames = analysis.estimated_gap_frames
    result.corrupt_candidates = analysis.corrupt_candidates
    result.leading_noise_bytes = analysis.leading_noise_bytes
    result.trailing_bytes = analysis.trailing_bytes
    return result


def format_results(results: Iterable[TestResult]) -> str:
    header = (
        "req_baud act_baud dir        sent_frames  valid_frames  miss_frames  "
        "gap_frames  err%_frame  err%_byte  tx_KiB/s  rx_KiB/s  status"
    )
    lines = [header, "-" * len(header)]
    for item in results:
        lines.append(
            f"{item.baudrate:<8} "
            f"{item.actual_baud:<8} "
            f"{item.direction:<10} "
            f"{item.sent_frames:<12} "
            f"{item.valid_frames:<12} "
            f"{item.missing_frames:<11} "
            f"{item.estimated_gap_frames:<10} "
            f"{item.frame_error_rate_pct:>10.4f} "
            f"{item.byte_error_rate_pct:>10.4f} "
            f"{item.tx_rate_kib_s:>9.1f} "
            f"{item.rx_rate_kib_s:>9.1f} "
            f"{item.status}"
        )
        if item.error:
            lines.append(f"  error: {item.error}")
        if item.status == "ok":
            lines.append(
                f"  bytes: sent={item.sent_bytes} rx_raw={item.received_bytes} valid={item.valid_bytes} "
                f"leading_noise={item.leading_noise_bytes} trailing={item.trailing_bytes} corrupt_candidates={item.corrupt_candidates}"
            )
            if item.actual_baud != item.baudrate:
                lines.append(
                    f"  warning: requested_baud={item.baudrate} actual_baud={item.actual_baud} baud_error={item.baud_error_rate_pct:+.3f}%"
                )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SC16IS7xx ttySC0/ttySC1 loopback error-rate tester",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--port-a", default="/dev/ttySC0", help="first serial port")
    parser.add_argument("--port-b", default="/dev/ttySC1", help="second serial port")
    parser.add_argument(
        "--baud-rates",
        type=parse_baud_rates,
        default=DEFAULT_BAUD_RATES,
        help="comma-separated requested baud rates to test",
    )
    parser.add_argument(
        "--xtal-hz",
        type=int,
        default=DEFAULT_XTAL_HZ,
        help="XTAL1/external clock used by the SC16 baud generator",
    )
    parser.add_argument(
        "--direction",
        choices=["a-to-b", "b-to-a", "both"],
        default="both",
        help="which direction(s) to test",
    )
    parser.add_argument(
        "--duration", type=float, default=3.0, help="seconds to transmit at each baud"
    )
    parser.add_argument(
        "--frame-size", type=int, default=256, help="bytes per framed test packet"
    )
    parser.add_argument(
        "--frames-per-batch", type=int, default=32, help="frames per write() batch"
    )
    parser.add_argument(
        "--read-size", type=int, default=4096, help="bytes per serial read()"
    )
    parser.add_argument(
        "--read-timeout", type=float, default=0.05, help="read timeout in seconds"
    )
    parser.add_argument(
        "--write-timeout", type=float, default=1.0, help="write timeout in seconds"
    )
    parser.add_argument(
        "--drain-grace",
        type=float,
        default=0.35,
        help="extra RX drain time after TX stops",
    )
    parser.add_argument(
        "--use-rtscts",
        action="store_true",
        help="enable hardware RTS/CTS flow control (may help reduce overrun)",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.frame_size <= HEADER.size:
        parser.error(f"--frame-size must be greater than {HEADER.size}")
    if args.frames_per_batch <= 0:
        parser.error("--frames-per-batch must be positive")
    if args.duration <= 0:
        parser.error("--duration must be positive")

    directions = []
    if args.direction in {"a-to-b", "both"}:
        directions.append((args.port_a, args.port_b, "A->B"))
    if args.direction in {"b-to-a", "both"}:
        directions.append((args.port_b, args.port_a, "B->A"))

    all_results: List[TestResult] = []
    for baudrate in args.baud_rates:
        actual_baud, prescaler, divisor = calculate_driver_baud(args.xtal_hz, baudrate)
        print(
            f"\n=== requested baudrate {baudrate} (actual {actual_baud}, prescaler {prescaler}, divisor {divisor}) ===",
            flush=True,
        )
        if actual_baud != baudrate:
            print(
                f"warning: requested baud {baudrate} will be applied as {actual_baud} with xtal {args.xtal_hz}",
                flush=True,
            )
        for tx_port, rx_port, direction in directions:
            print(f"running {direction}: {tx_port} -> {rx_port}", flush=True)
            result = run_one_direction(
                tx_port_name=tx_port,
                rx_port_name=rx_port,
                baudrate=baudrate,
                actual_baud=actual_baud,
                duration_s=args.duration,
                frame_size=args.frame_size,
                read_size=args.read_size,
                frames_per_batch=args.frames_per_batch,
                read_timeout=args.read_timeout,
                write_timeout=args.write_timeout,
                drain_grace_s=args.drain_grace,
                direction=direction,
                rtscts=args.use_rtscts,
            )
            all_results.append(result)

    print()
    print(format_results(all_results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
