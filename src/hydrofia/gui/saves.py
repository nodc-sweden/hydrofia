import pathlib
import sys

import yaml

if getattr(sys, "frozen", False):
    ROOT_DIR = pathlib.Path(sys.executable).parent
else:
    ROOT_DIR = pathlib.Path(__file__).parent


SAVES_PATH = pathlib.Path(ROOT_DIR, "saves.yaml")
# A file of its own, since each save replaces the whole file
UNDERWAY_SAVES_PATH = pathlib.Path(ROOT_DIR, "underway_saves.yaml")
controls = {}
loaded_data = {}


def load_values(path: pathlib.Path) -> dict:
    """The values saved in the file, or an empty dict if there are none."""
    if not path.exists():
        return {}
    with path.open() as fid:
        return yaml.safe_load(fid) or {}


def save_values(path: pathlib.Path, data: dict) -> None:
    with path.open("w") as fid:
        yaml.safe_dump(data, fid)


def _load():
    return load_values(SAVES_PATH)


def _save(data):
    save_values(SAVES_PATH, data)


def add_control(name, cont):
    controls[name] = cont


def _get_name_from_control(cont):
    return str(cont).split("=")[0].split(".")[1]


def save():
    data = {}
    print()
    for name, cont in controls.items():
        data[name] = cont.value
    _save(data)


def load(obj):
    data = _load()
    for name in controls:
        value = data.get(name)
        if value is None:
            continue
        attr = getattr(obj, name)
        attr.value = value
        attr.update()
