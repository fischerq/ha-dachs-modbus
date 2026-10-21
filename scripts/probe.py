#!/usr/bin/env python3
"""Read-only probe of a Dachs GLT Modbus interface.

    python3 scripts/probe.py 192.168.25.205 [--port 502]

Prints the raw input registers 8000..8056 next to the decoded values, so the
register map in custom_components/dachs_modbus/api.py can be checked against
the unit's display (power, temperatures, operating hours). Never writes.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

from pymodbus.client import ModbusTcpClient  # noqa: E402

from dachs_modbus.api import (
    READ_COUNT,
    READ_START,
    REGISTER_MAP,
    decode_registers,
)  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("host")
    parser.add_argument("--port", type=int, default=502)
    args = parser.parse_args()

    client = ModbusTcpClient(args.host, port=args.port)
    try:
        result = client.read_input_registers(address=READ_START, count=READ_COUNT)
        if result.isError():
            print(f"read failed: {result}", file=sys.stderr)
            return 1
        regs = result.registers
    finally:
        client.close()

    data = decode_registers(regs)
    print(f"{'reg':>5}  {'raw':>6}  key = decoded")
    for key, off, kind, _scale in REGISTER_MAP:
        print(f"{READ_START + off:>5}  {regs[off]:>6}  {key} = {data[key]!r}  ({kind})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
