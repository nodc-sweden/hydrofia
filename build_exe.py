import pathlib
import subprocess
import tomllib

THIS_DIR = pathlib.Path(__file__).parent


def get_package_version() -> str:
    pyproject_path = THIS_DIR / 'pyproject.toml'
    with open(pyproject_path, 'rb') as fid:
        config = tomllib.load(fid)
    return config['project']['version']


if __name__ == '__main__':
    version = get_package_version()
    main_py_path = THIS_DIR / 'ph_calculation_hydrofia.py'
    exe_file_name = f'ph_calculation_hydrofia_v{version}.exe'
    print(main_py_path)
    print(exe_file_name)
    subprocess.run(f'pyinstaller {main_py_path} --onefile --name {exe_file_name}')