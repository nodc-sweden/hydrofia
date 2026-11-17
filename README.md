# hydrofia

## Installera uv
Projektet hanteras med `uv` som behöver installeras separat.

### Direktinstallation
Följ den officiella [installationsguiden](https://docs.astral.sh/uv/getting-started/installation/) för att installera
`uv` på standardsätt med ett enda kommando. Med denna installation kan `uv` sedan uppdatera sig självt.

## Installation med pip
Det går också att installera genom en befintlig Python-installation:
```bash
pip install uv
```

Denna installation kan inte uppdatera sig själv utan måste även fortsättningsvis uppdateras med hjälp av `pip`.

## Bygg exe-filer
Bygg exe-filer med följande kommando:
```bash
uv run build_exe.py
```

Filerna hamnar i mappen `dist/`.