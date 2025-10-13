from PyInstaller.utils.hooks import collect_all

# Coleta todos os arquivos do OpenCV, incluindo binários e dados
datas, binaries, hiddenimports = collect_all('cv2')

# Assegura que o config.py interno será incluído
