from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> int:
    print(">>>", " ".join(cmd))
    p = subprocess.run(cmd, check=False)
    if check and p.returncode != 0:
        raise SystemExit(p.returncode)
    return p.returncode


def has_cmd(cmd: list[str]) -> bool:
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def pip_install(pkg: str) -> None:
    run([sys.executable, "-m", "pip", "install", "-U", pkg], check=True)


def ensure_pip_packages() -> None:
    # ensure pip itself is reasonable
    run([sys.executable, "-m", "pip", "install", "-U", "pip"], check=False)

    needed = [
        ("pre-commit", ["pre-commit", "--version"]),
        ("nbstripout", ["python", "-c", "import nbstripout"]),  # import check
        ("nbautoexport", ["nbautoexport", "--help"]),
    ]

    for pkg, probe in needed:
        ok = has_cmd(probe) if probe[0] != "python" else has_cmd([sys.executable, "-c", probe[2]])
        if ok:
            print(f">>> {pkg} already available")
        else:
            print(f">>> Installing {pkg}")
            pip_install(pkg)


def ensure_git_repo() -> None:
    if not has_cmd(["git", "--version"]):
        raise SystemExit("ERROR: git is not installed or not in PATH.")

    # init if not a repo
    if has_cmd(["git", "rev-parse", "--is-inside-work-tree"]):
        print(">>> git already initialized")
    else:
        run(["git", "init"], check=True)


def write_precommit_config() -> None:
    cfg = Path(".pre-commit-config.yaml")
    if cfg.exists():
        print(">>> .pre-commit-config.yaml already exists")
        return

    cfg.write_text(
        "\n".join(
            [
                "repos:",
                "  - repo: https://github.com/kynan/nbstripout",
                "    rev: 0.6.1",
                "    hooks:",
                "      - id: nbstripout",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(">>> wrote .pre-commit-config.yaml")


def install_hooks_and_configure() -> None:
    # pre-commit install
    if has_cmd(["pre-commit", "--version"]):
        run(["pre-commit", "install"], check=False)
    else:
        print(">>> pre-commit still not available, skipping install")

    # nbautoexport configure
    if has_cmd(["nbautoexport", "--help"]):
        run(["nbautoexport", "configure", "-f", "script", "notebooks"], check=False)
    else:
        print(">>> nbautoexport still not available, skipping configure")


def main() -> None:
    ensure_pip_packages()
    ensure_git_repo()
    write_precommit_config()
    install_hooks_and_configure()
    print(">>> git_tools done")


if __name__ == "__main__":
    main()
