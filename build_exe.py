import pathlib
import subprocess
import tomllib

THIS_DIR = pathlib.Path(__file__).parent


def get_package_version() -> str:
    pyproject_path = THIS_DIR / "pyproject.toml"
    with pyproject_path.open("rb") as fid:
        config = tomllib.load(fid)
    return config["project"]["version"]


if __name__ == "__main__":
    version = get_package_version()
    main_py_path = THIS_DIR / "ph_calculation_hydrofia.py"
    # PyInstaller appends .exe on Windows
    exe_name = f"ph_calculation_hydrofia_v{version}"
    print(main_py_path)
    print(exe_name)
    # flet pack wraps PyInstaller and bundles the flet desktop client.
    # --debug-console keeps the console window with log output, as before.
    subprocess.run(
        [
            "flet",
            "pack",
            str(main_py_path),
            "--name",
            exe_name,
            "--debug-console",
            "true",
            "--yes",
        ],
        check=True,
    )
