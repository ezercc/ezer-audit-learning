"""命令行入口：运行一次样例，或启动本机审阅接口。"""

from __future__ import annotations

import argparse
import json

from ezer_audit_review.pipeline import run_chain
from ezer_audit_review.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(description="Ezer audit review build")
    parser.add_argument("command", nargs="?", choices=("run", "serve"), default="run")
    parser.add_argument("--code", default="000000.SZ")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--period", default="FY")
    parser.add_argument("--lang", default="zh-CN")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "serve":
        httpd = serve(port=args.port)
        print(f"review server on http://127.0.0.1:{httpd.server_address[1]}")
        httpd.serve_forever()
        return
    result = run_chain(
        {"code": args.code, "year": args.year, "period": args.period, "lang": args.lang}
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
