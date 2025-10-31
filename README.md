

# 🧠 **ScanFaceProject**

## 🎯 **Descrição**
O **ScanFaceProject** é um sistema desenvolvido em **Python**, utilizando **OpenCV** e **Kivy**, que realiza o **reconhecimento facial** de forma simples, leve e com interface gráfica interativa.  

Criado por **Luiz Henrique**, **Gustavo Sabino** e **Eduardo Marinho**, o projeto une visão computacional e design moderno para demonstrar como a tecnologia pode identificar rostos em tempo real.

---

## 🧩 **Tecnologias Utilizadas**

- 🐍 **Python 3.10+**
- 🧠 **OpenCV** — Detecção facial com `haarcascade_frontalface_default.xml`
- 🎨 **Kivy** — Criação da interface gráfica
- ⚙️ **NumPy** — Manipulação de dados de imagem
- 💡 **Virtualenv** — Isolamento de dependências

---

## ⚙️ **Como Executar o Projeto**

### 📁 **1️⃣ Clone o repositório**
```bash
git clone https://github.com/seuusuario/ScanFaceProject.git
cd ScanFaceProject/python-recognition-opencv/project
````

---

## 🧱 **2️⃣ Crie e ative o ambiente virtual**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)](https://opencv.org/)
[![Kivy](https://img.shields.io/badge/Kivy-GUI%20Framework-orange?logo=kivy)](https://kivy.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)
[![Status](https://img.shields.io/badge/Build-Stable-success)]()
[![Contributors](https://img.shields.io/badge/Contributors-3-blueviolet)]()

---

### 🪟 **No Windows (PowerShell):**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 🐧 **No Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 📦 **3️⃣ Instale as dependências**

```bash
pip install -r requirements.txt
```

> Caso o arquivo `requirements.txt` não exista, instale manualmente:

```bash
pip install kivy opencv-python numpy
```

---

## 🧾 **4️⃣ Verifique o classificador**

Certifique-se de que o arquivo **`haarcascade_frontalface_default.xml`** está localizado em:

```
python-recognition-opencv/project/lib/haarcascade_frontalface_default.xml
```

---

## ▶️ **5️⃣ Execute o projeto**

```bash
python main.py
```

> O sistema abrirá uma janela gráfica do **Kivy** e iniciará a **detecção facial** com sua câmera.

---

## 🧰 **Compilando para .EXE (opcional)**

Caso queira gerar um executável:

```bash
python -m PyInstaller main.py ^
    --onefile ^
    --noconsole ^
    --add-data ".venv\Lib\site-packages\kivy\data;kivy_install\data" ^
    --add-data ".venv\Lib\site-packages\cv2\data;cv2\data" ^
    --add-data "..\..\faces;faces" ^
    --add-data "..\..\cadastros;cadastros" ^
    --add-data "..\..\pasta_usuarios;pasta_usuarios" ^
    --add-data "..\..\lib;lib" ^
    --hidden-import=kivy.weakmethod ^
    --hidden-import=numpy ^
    --hidden-import=cv2 ^
    --additional-hooks-dir=hooks
```

> O executável final estará em:
> 🗂️ `dist/main.exe`

## **🧰 Arquivo .EXE compilado**
>Se encontra na aba "Releases" no canto direito

---

## 🧑‍💻 **Autores**

| Nome                                   | Função                     |
| -------------------------------------- | -------------------------- |
| **Luiz Henrique de Oliveira Eufrásio** | 🧠 Programação e Interface |
| **Gustavo Sabino**                     | ⚙️ Telas  |
| **Eduardo Marinho**                    | 🔗 Documentação |

---

## 💖 **Apoie nosso trabalho**

Se o projeto te ajudou, **deixe uma ⭐ no repositório!**
Isso incentiva a continuação do desenvolvimento e **novas funcionalidades** ✨

---

> 🧩 *“Transformando visão em reconhecimento — um frame por vez.”*




