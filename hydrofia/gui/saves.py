import yaml
import pathlib
import sys

if getattr(sys, 'frozen', False):
    ROOT_DIR = pathlib.Path(sys.executable).parent
else:
    ROOT_DIR = pathlib.Path(__file__).parent


SAVES_PATH = pathlib.Path(ROOT_DIR, 'saves.yaml')
controls = {}
loaded_data = dict()


def _load():
    if not SAVES_PATH.exists():
        return {}
    with open(SAVES_PATH) as fid:
        return yaml.safe_load(fid)


def _save(data):
    with open(SAVES_PATH, 'w') as fid:
        yaml.safe_dump(data, fid)


def add_control(name, cont):
    controls[name] = cont


def _get_name_from_control(cont):
    return str(cont).split('=')[0].split('.')[1]


def save():
    data = {}
    print()
    for name, cont in controls.items():
        data[name] = cont.value
        print(f'SAVE: {name=}, {cont.value=}')
    _save(data)


def load(obj):
    data = _load()
    for name, cont in controls.items():
        value = data.get(name)
        print(f'LOAD: {name=}, {value=}')
        if value is None:
            continue
        attr = getattr(obj, name)
        attr.value = value
        attr.update()

