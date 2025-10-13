from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('kivy')

try:
    # Tenta coletar os submódulos de forma isolada
    hiddenimports = collect_submodules('kivy')
except Exception as e:
    import pkgutil
    import kivy
    import os

    kivy_path = os.path.dirname(kivy.__file__)
    hiddenimports = [
        name for _, name, _ in pkgutil.walk_packages([kivy_path], prefix="kivy.")
    ]
