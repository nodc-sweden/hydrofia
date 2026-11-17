import pathlib
import subprocess
import tomllib
from pathlib import Path

PROJECT_ROOT = pathlib.Path(__file__).parent
ENTRY_POINT_DIR = PROJECT_ROOT / "entrypoints"
DIST_DIR = PROJECT_ROOT / "dist"
OUTPUT_DIR = PROJECT_ROOT / "bin"


def main():
    version = get_package_version()
    for entry_point in (
        "ph_calculation_hydrofia.py",
        "ph_calculation_hydrofia_underway.py",
    ):
        entry_point_path = ENTRY_POINT_DIR / entry_point
        build_exe(entry_point_path, version)


def get_package_version() -> str:
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    with pyproject_path.open("rb") as fid:
        config = tomllib.load(fid)
    return config["project"]["version"]


def build_exe(entry_point_path: Path, version: str):
    # PyInstaller appends .exe on Windows
    exe_name = f"{entry_point_path.stem}_v{version}"
    print("-" * 80)
    print(f"Entrypoint: {entry_point_path.relative_to(PROJECT_ROOT)}")
    print(f"Artefact:   {exe_name}.exe")
    print("-" * 80)

    # flet pack wraps PyInstaller and bundles the flet desktop client.
    # --debug-console keeps the console window with log output, as before.
    subprocess.run(
        [
            "flet",
            "pack",
            str(entry_point_path),
            "--name",
            exe_name,
            "--debug-console",
            "true",
            "--yes",
        ],
        check=True,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for file in DIST_DIR.iterdir():
        file.move(OUTPUT_DIR / file.name)

    DIST_DIR.rmdir()


if __name__ == "__main__":
    main()
