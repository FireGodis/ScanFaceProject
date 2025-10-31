
import os
import cv2
import sys
import numpy as np
import kivy
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.config import Config



kivy.require('1.11.1')


Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

if not os.path.exists("faces"):
    os.makedirs("faces")

if not os.path.exists("cadastros"):
    os.makedirs("cadastros")


base_dir = os.path.dirname(os.path.abspath(__file__))
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

cascade_path = resource_path(os.path.join(".\python-recognition-opencv\project\lib", "haarcascade_frontalface_default.xml"))
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    raise Exception(f"Erro ao carregar o classificador! Caminho verificado: {cascade_path}")


face_classifier = cv2.CascadeClassifier(cascade_path)


if face_classifier.empty():
    raise Exception(f"Erro ao carregar o classificador! Caminho verificado: {cascade_path}")



def upload_file(self, instance):
    
    
    layout = BoxLayout(orientation="vertical")
    filechooser = FileChooserListView()
    layout.add_widget(filechooser)
    
    btn_layout = BoxLayout(size_hint_y=None, height=50)
    select_btn = Button(text="Selecionar")
    cancel_btn = Button(text="Cancelar")
    btn_layout.add_widget(select_btn)
    btn_layout.add_widget(cancel_btn)
    layout.add_widget(btn_layout)
    
    popup = Popup(title="Upload de Arquivo", content=layout, size_hint=(0.9, 0.9))

    
    def select_file(instance):
        src = filechooser.selection[0]
        if src:
            dst = os.path.join(self.current_path, os.path.basename(src))
            import shutil
            shutil.copy(src, dst)
            self.show_directory(self.current_path)
            popup.dismiss()
    
    select_btn.bind(on_press=select_file)
    cancel_btn.bind(on_press=lambda *_: popup.dismiss())
    
    popup.open()




class Theme:
    PRIMARY_COLOR = [0.1, 0.6, 0.9, 1]       # Azul
    SECONDARY_COLOR = [0.95, 0.95, 0.95, 1]  # Cinza claro
    BUTTON_COLOR = [0.2, 0.5, 0.8, 1]        # Azul botão
    BUTTON_TEXT_COLOR = [1, 1, 1, 1]         # Branco
    FONT_SIZE_TITLE = 32
    FONT_SIZE_LABEL = 18
    FONT_SIZE_INPUT = 16

def styled_label(text, size=None, color=None):
    return Label(
        text=text,
        font_size=size or Theme.FONT_SIZE_LABEL,
        color=color or Theme.PRIMARY_COLOR
    )

def styled_input(hint, password=False):
    return TextInput(
        hint_text=hint,
        password=password,
        font_size=Theme.FONT_SIZE_INPUT,
        size_hint_y=None,
        height=40,
        background_color=Theme.SECONDARY_COLOR,
        foreground_color=[0,0,0,1],
        padding=[10,10,10,10],
        multiline=False
    )

def styled_button(text, callback):
    btn = Button(
        text=text,
        size_hint_y=None,
        height=50,
        background_color=Theme.BUTTON_COLOR,
        color=Theme.BUTTON_TEXT_COLOR,
        background_normal='',  # remove a imagem de fundo normal
        background_down='',    # remove o efeito de clique
    )
    btn.bind(on_press=callback)
    return btn


class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        layout.add_widget(styled_label(
            "Dificuldades com o login,\nentre em contato no número abaixo para o suporte técnico",
            Theme.FONT_SIZE_LABEL,
            Theme.PRIMARY_COLOR
        ))

        layout.add_widget(styled_label("+55 61991876314", Theme.FONT_SIZE_TITLE, Theme.BUTTON_COLOR))

        voltar_btn = styled_button("Voltar", lambda *_: setattr(self.manager, 'current', 'recognition'))
        layout.add_widget(voltar_btn)

        self.add_widget(layout)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(styled_label("Scan Face Project", Theme.FONT_SIZE_TITLE, Theme.PRIMARY_COLOR))

        self.cpf_input = styled_input("CPF")
        layout.add_widget(self.cpf_input)

        self.senha_input = styled_input("Senha", password=True)
        layout.add_widget(self.senha_input)

        login_btn = styled_button("Login", self.login_action)
        layout.add_widget(login_btn)

        self.status_label = styled_label("")
        layout.add_widget(self.status_label)

        botoes = BoxLayout(size_hint_y=None, height=50, spacing=10)
        criar_btn = styled_button("Criar conta", lambda *_: setattr(self.manager, 'current', 'create_account'))
        esqueceu_btn = styled_button("Esqueceu a senha?", lambda *_: setattr(self.manager, 'current', 'reset_request'))
        botoes.add_widget(criar_btn)
        botoes.add_widget(esqueceu_btn)
        layout.add_widget(botoes)

        

        self.add_widget(layout)

    def login_action(self, instance):
        cpf = self.cpf_input.text.strip()
        senha = self.senha_input.text.strip()
        filepath = os.path.join("cadastros", f"{cpf}.txt")

        if not os.path.exists(filepath):
            self.status_label.text = "CPF não cadastrado."
            return

        with open(filepath, "r", encoding="utf-8") as f:
            dados = f.read().splitlines()
            dados_dict = {line.split(":")[0]: line.split(":")[1] for line in dados if ":" in line}

        if dados_dict.get("Senha") != senha:
            self.status_label.text = "Senha incorreta."
            return

        self.manager.get_screen("recognition").cpf_logado = cpf
        self.manager.current = "recognition"



class FileManagerScreen(Screen):
    def go_to_parent_folder(self, instance):
        if self.current_path:
            base_dir = os.path.join("pasta_usuarios", self.cpf_logado)
            parent = os.path.dirname(self.current_path)

            # Só permite voltar se ainda estivermos dentro da pasta do CPF logado
            if os.path.commonpath([base_dir, parent]) == base_dir:
                self.current_path = parent
                self.show_directory(self.current_path)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.cpf_logado = None
        self.current_path = None
        self.file_editor = None
        self.editor_text = None

        
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(self.layout)

        self.path_label = styled_label("Caminho atual: /")
        self.layout.add_widget(self.path_label)

        
        btn_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_bar.add_widget(styled_button("Nova Pasta", self.create_folder))
        btn_bar.add_widget(styled_button("Novo Arquivo TXT", self.create_file))
        btn_bar.add_widget(styled_button("Voltar", self.go_to_parent_folder))
        btn_bar.add_widget(styled_button("Upload Arquivo", lambda inst: upload_file(self, inst)))
        logout_btn = styled_button("Deslogar", lambda *_: setattr(self.manager, 'current', 'login'))
        logout_btn.size_hint_x = None
        logout_btn.width = 100
        btn_bar.add_widget(logout_btn)
        self.layout.add_widget(btn_bar)

       
        self.files_layout = GridLayout(cols=1, spacing=5)
        self.layout.add_widget(self.files_layout)

    # Criar pasta dentro de uma pasta específica
    def create_folder_in(self, path, parent_popup=None):
        folder_name = f"NovaPasta_{len(os.listdir(path))}"
        new_path = os.path.join(path, folder_name)
        os.makedirs(new_path, exist_ok=True)
        self.show_directory(self.current_path)
        if parent_popup:
            parent_popup.dismiss()

    # Criar arquivo dentro de uma pasta específica
    def create_file_in(self, path, parent_popup=None):
        file_name = f"NovoArquivo_{len(os.listdir(path))}.txt"
        new_file = os.path.join(path, file_name)
        with open(new_file, "w", encoding="utf-8") as f:
            f.write("")  # arquivo vazio
        self.show_directory(self.current_path)
        if parent_popup:
            parent_popup.dismiss()

    def rename_file(self, path, parent_popup=None):
        # Fecha o popup atual, se houver
        if parent_popup:
            parent_popup.dismiss()

        # Layout do Popup
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Label informativa
        layout.add_widget(Label(text=f"Renomear arquivo:\n{os.path.basename(path)}"))

        # Input para o novo nome
        input_name = TextInput(text=os.path.basename(path), multiline=False)
        layout.add_widget(input_name)

        # Botão de confirmar
        def confirm_rename(instance):
            new_name = input_name.text.strip()
            if new_name:
                dir_path = os.path.dirname(path)
                new_path = os.path.join(dir_path, new_name)
                try:
                    os.rename(path, new_path)
                    self.show_directory(dir_path)  # Atualiza lista de arquivos
                    popup.dismiss()
                except Exception as e:
                    print(f"Erro ao renomear: {e}")

        btn_confirm = Button(text="Renomear", size_hint_y=None, height=40)
        btn_confirm.bind(on_release=confirm_rename)
        layout.add_widget(btn_confirm)

        # Criar e abrir Popup
        popup = Popup(title="Renomear Arquivo", content=layout,
                    size_hint=(0.6, 0.4), auto_dismiss=True)
        popup.open()

    def delete_file(self, path, parent_popup=None):
        import os
        try:
            if os.path.isdir(path):
                os.rmdir(path)  # ou shutil.rmtree(path) se quiser apagar pastas com conteúdo
            else:
                os.remove(path)
            self.show_directory(self.current_path)  # atualiza a lista
            if parent_popup:
                parent_popup.dismiss()
        except Exception as e:
            print(f"Erro ao deletar: {e}")

    def file_touch(self, instance, touch, path, is_dir=False):
        if touch.button == 'right' and instance.collide_point(*touch.pos):
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
            from kivy.uix.button import Button

            # Se for pasta, adiciona opções extras
            if is_dir:
                layout.add_widget(Button(text="Nova Pasta", on_press=lambda *_: self.create_folder_in(path, popup)))
                layout.add_widget(Button(text="Criar TXT", on_press=lambda *_: self.create_file_in(path, popup)))

            # Opções comuns a arquivos e pastas
            layout.add_widget(Button(text="Excluir", on_press=lambda *_: self.delete_file(path, popup)))
            layout.add_widget(Button(text="Renomear", on_press=lambda *_: self.rename_file(path, popup)))
            
            popup = Popup(title="Ações", content=layout, size_hint=(0.5, 0.5))
            popup.open()
            return True

    def on_pre_enter(self, *args):
       
        base_dir = os.path.join("pasta_usuarios", self.cpf_logado)
        os.makedirs(base_dir, exist_ok=True)
        self.current_path = base_dir
        self.show_directory(self.current_path)

    def preview_image(self, path):
        if path.lower().endswith(('.png', '.jpg', '.jpeg')):
            from kivy.uix.image import Image
            from kivy.uix.popup import Popup
            img = Image(source=path)
            popup = Popup(title=os.path.basename(path), content=img, size_hint=(0.8, 0.8))
            popup.open()

    def show_directory(self, path):
        """Atualiza a listagem da pasta atual"""
        self.files_layout.clear_widgets()
        self.path_label.text = f"Caminho atual: {os.path.relpath(path, 'pasta_usuarios')}"

        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            btn = styled_button(item, lambda *_: None)  # Callback vazio por enquanto

            # Bind para clique direito
            btn.bind(on_touch_down=lambda inst, touch, p=full_path, d=os.path.isdir(full_path): self.file_touch(inst, touch, p, d))

            # Bind para clique esquerdo (abrir)
            if not os.path.isdir(full_path):
                if full_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    btn.bind(on_press=lambda _, p=full_path: self.preview_image(p))
                else:
                    btn.bind(on_press=lambda _, p=full_path: self.open_file(p))
            else:
                btn.bind(on_press=lambda _, p=full_path: self.enter_folder(p))

            self.files_layout.add_widget(btn)

    def enter_folder(self, path):
        """Entra na pasta"""
        self.current_path = path
        self.show_directory(path)

    def create_folder(self, instance):
        """Cria uma nova pasta dentro da atual"""
        folder_name = f"NovaPasta_{len(os.listdir(self.current_path))}"
        new_path = os.path.join(self.current_path, folder_name)
        os.makedirs(new_path, exist_ok=True)
        self.show_directory(self.current_path)

    def create_file(self, instance):
        """Cria um novo arquivo de texto dentro da atual"""
        file_name = f"NovoArquivo_{len(os.listdir(self.current_path))}.txt"
        new_file = os.path.join(self.current_path, file_name)
        with open(new_file, "w", encoding="utf-8") as f:
            f.write("")  # arquivo vazio
        self.show_directory(self.current_path)

    def open_file(self, file_path):
        """Abre o editor de texto simples"""
        self.layout.clear_widgets()
        self.file_editor = file_path

        self.layout.add_widget(styled_label(f"Editando: {os.path.basename(file_path)}"))

        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.editor_text = TextInput(text=content, multiline=True, size_hint_y=0.8)
        self.layout.add_widget(self.editor_text)

        
        btns = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btns.add_widget(styled_button("Salvar", self.save_file))
        btns.add_widget(styled_button("Voltar", lambda *_: self.refresh_file_manager()))
        self.layout.add_widget(btns)

    def save_file(self, instance):
        """Salva o conteúdo editado"""
        with open(self.file_editor, "w", encoding="utf-8") as f:
            f.write(self.editor_text.text)
        self.refresh_file_manager()

    def refresh_file_manager(self):
        """Recarrega o gerenciador após editar"""
        self.layout.clear_widgets()
        self.__init__()  
        self.cpf_logado = self.manager.get_screen("recognition").cpf_logado
        self.on_pre_enter()


class CreateAccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation="horizontal", padding=20, spacing=10)

        # Lado esquerdo (formulário)
        form_layout = GridLayout(cols=1, spacing=10, size_hint=(0.5, 1))
        form_layout.add_widget(styled_label("Criar Conta", Theme.FONT_SIZE_TITLE))

        # Campos obrigatórios
        self.nome_input = styled_input("Nome *")
        form_layout.add_widget(self.nome_input)

        self.cpf_input = styled_input("CPF *")
        form_layout.add_widget(self.cpf_input)

        self.cargo_input = styled_input("Cargo *")
        form_layout.add_widget(self.cargo_input)

        self.email_input = styled_input("Email *")
        form_layout.add_widget(self.email_input)

        self.senha_input = styled_input("Senha *", password=True)
        form_layout.add_widget(self.senha_input)

        self.progress_label = styled_label("Aguardando captura...")
        form_layout.add_widget(self.progress_label)

        # Botões
        self.capturar_btn = styled_button("Iniciar Captura de Rosto", self.start_capture)
        self.capturar_btn.disabled = True  # começa desativado
        form_layout.add_widget(self.capturar_btn)

        self.salvar_btn = styled_button("Salvar Cadastro", self.save_account)
        self.salvar_btn.disabled = True  # começa desativado
        form_layout.add_widget(self.salvar_btn)

        voltar_btn = styled_button("Voltar", lambda *_: setattr(self.manager, 'current', 'login'))
        form_layout.add_widget(voltar_btn)

        main_layout.add_widget(form_layout)

        # Lado direito (câmera)
        self.camera_widget = Image(size_hint=(0.5, 1))
        main_layout.add_widget(self.camera_widget)

        self.add_widget(main_layout)

        # Inicialização
        self.capture = None
        self.frames_captured = 0
        self.capturing = False

        # Monitorar mudanças no CPF
        self.cpf_input.bind(text=self.on_cpf_text)

    def on_cpf_text(self, instance, value):
        if value.strip():
            self.capturar_btn.disabled = False
        else:
            self.capturar_btn.disabled = True

    # Função para mostrar popup explicativo
    def show_popup(self, message):
        popup = Popup(
            title="Ação Indisponível",
            content=Label(text=message),
            size_hint=(0.6, 0.3),
            auto_dismiss=True
        )
        popup.open()
    def face_extractor(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return None
        for (x, y, w, h) in faces: 
            return img[y:y+h, x:x+w]

    def start_capture(self, instance):
        if self.capturar_btn.disabled:
            self.show_popup("Digite o CPF para habilitar a captura de rosto!")
            return

        # Restante da função normal
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            self.progress_label.text = "Erro: não foi possível acessar a câmera."
            return

        self.frames_captured = 0
        self.capturing = True
        self.progress_label.text = "Analisando Rosto 0/100..."
        Clock.schedule_interval(self.update_camera, 1.0/30.0)

    def update_camera(self, dt):
        if self.capture and self.capturing:
            ret, frame = self.capture.read()
            if not ret:
                self.progress_label.text = "Erro ao capturar frame."
                self.stop_capture()
                return

            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera_widget.texture = texture

            face = self.face_extractor(frame)
            if face is not None:
                self.frames_captured += 1
                face = cv2.resize(face, (200, 200))
                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

                cpf = self.cpf_input.text.strip()
                file_name_path = f"faces/{cpf}({self.frames_captured}).png"
                cv2.imwrite(file_name_path, face)

                if self.frames_captured < 100:
                    self.progress_label.text = f"Analisando Rosto {self.frames_captured}/100..."
                else:
                    self.progress_label.text = "Análise concluída! Fotos salvas."
                    self.stop_capture()
                    self.salvar_btn.disabled = False  # habilita o botão de salvar

    def stop_capture(self):
        self.capturing = False
        if self.capture:
            self.capture.release()
            self.capture = None
        Clock.unschedule(self.update_camera)

    def save_account(self, instance):
        if self.salvar_btn.disabled:
            self.show_popup("Faça a captura da face antes de salvar o cadastro!")
            return

        # Verifica se todos os campos estão preenchidos
        campos = [
            ("Nome", self.nome_input.text),
            ("CPF", self.cpf_input.text),
            ("Cargo", self.cargo_input.text),
            ("Email", self.email_input.text),
            ("Senha", self.senha_input.text)
        ]
        for nome, valor in campos:
            if not valor.strip():
                self.show_popup(f"O campo '{nome}' é obrigatório!")
                return

        cpf = self.cpf_input.text.strip()
        filepath = os.path.join("cadastros", f"{cpf}.txt")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Nome:{self.nome_input.text}\n")
            f.write(f"CPF:{cpf}\n")
            f.write(f"Cargo:{self.cargo_input.text}\n")
            f.write(f"Email:{self.email_input.text}\n")
            f.write(f"Senha:{self.senha_input.text}\n")

        self.progress_label.text = "Cadastro salvo com sucesso!"



class RecognitionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cpf_logado = None

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(styled_label("Reconhecimento Facial", Theme.FONT_SIZE_TITLE))

        self.status_label = styled_label("Posicione seu rosto na câmera...")
        layout.add_widget(self.status_label)

        self.camera_widget = Image(size_hint=(1, 1))
        layout.add_widget(self.camera_widget)

        # Barra inferior com Voltar e Suporte
        bottom_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        voltar_btn = styled_button("Voltar", lambda *_: setattr(self.manager, 'current', 'login'))
        suporte_btn = styled_button("Suporte", lambda *_: setattr(self.manager, 'current', 'suport'))
        bottom_bar.add_widget(voltar_btn)
        bottom_bar.add_widget(suporte_btn)
        layout.add_widget(bottom_bar)

        self.add_widget(layout)

        self.model = None
        self.capture = None
        self.event = None

    def on_enter(self, *args):
        cpf = self.cpf_logado
        if not cpf:
            self.status_label.text = "Erro: Nenhum CPF em uso."
            return

        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            self.status_label.text = "Erro: não foi possível acessar a câmera"
            return

        self.train_model(cpf)
        self.event = Clock.schedule_interval(self.update_camera, 1.0 / 30.0)

    def on_leave(self, *args):
        if self.event:
            Clock.unschedule(self.event)
            self.event = None
        if self.capture:
            self.capture.release()
            self.capture = None

    def train_model(self, cpf):
        data_path = "faces/"
        onlyfiles = [f for f in os.listdir(data_path) if f.startswith(cpf)]

        Training_Data, Labels = [], []
        for i, file in enumerate(onlyfiles):
            image_path = os.path.join(data_path, file)
            images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            Training_Data.append(np.asarray(images, dtype=np.uint8))
            Labels.append(i)

        if len(Labels) == 0:
            self.status_label.text = "Nenhuma face cadastrada para este CPF."
            return

        Labels = np.asarray(Labels, dtype=np.int32)
        self.model = cv2.face.LBPHFaceRecognizer_create()
        self.model.train(np.asarray(Training_Data), np.asarray(Labels))

    def update_camera(self, dt):
        if not self.capture:
            return

        ret, frame = self.capture.read()
        if not ret:
            self.status_label.text = "Erro ao capturar frame"
            return

        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.camera_widget.texture = texture

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (200, 200))

            if self.model is not None:
                result = self.model.predict(roi)
                confidence = int(100 * (1 - (result[1]) / 300))

                if confidence > 75:
                    self.manager.current = "home"
                else:
                    self.status_label.text = f"Face não reconhecida ({confidence}%)"

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.label = styled_label("Login realizado com sucesso!", Theme.FONT_SIZE_TITLE)
        layout.add_widget(self.label)

        abrir_arquivos_btn = styled_button("Abrir Gerenciador de Arquivos", self.abrir_arquivos)
        layout.add_widget(abrir_arquivos_btn)

        logout_btn = styled_button("Deslogar", lambda *_: setattr(self.manager, 'current', 'login'))
        layout.add_widget(logout_btn)

        self.add_widget(layout)

    def abrir_arquivos(self, instance):
        
        cpf = self.manager.get_screen("recognition").cpf_logado
        file_manager_screen = self.manager.get_screen("file_manager")
        file_manager_screen.cpf_logado = cpf
        self.manager.current = "file_manager"


class ResetRequestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(styled_label("Esqueceu a Senha?", Theme.FONT_SIZE_TITLE))

        self.email_input = styled_input("Digite seu Email")
        layout.add_widget(self.email_input)

        enviar_btn = styled_button("Enviar Email de Redefinição", self.enviar_email)
        layout.add_widget(enviar_btn)

        self.confirm_label = styled_label("")
        layout.add_widget(self.confirm_label)

        voltar_btn = styled_button("Voltar", lambda *_: setattr(self.manager, 'current', 'login'))
        layout.add_widget(voltar_btn)

        self.add_widget(layout)

    def enviar_email(self, instance):
        self.confirm_label.text = "Email de redefinição enviado!"

class MyApp(App):
    def build(self):
        self.title = "ScanFace"
        Window.icon = os.path.join(os.path.dirname(__file__), "scanface_ico.ico")
        print(os.path.exists(os.path.join(os.path.dirname(__file__), "scanface_ico.ico")))
        sm = ScreenManager(transition=WipeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(CreateAccountScreen(name="create_account"))
        sm.add_widget(RecognitionScreen(name="recognition"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SupportScreen(name = "suport"))
        sm.add_widget(ResetRequestScreen(name="reset_request"))
        sm.add_widget(FileManagerScreen(name="file_manager"))  # ✅ nova tela
        return sm

if __name__ == "__main__":
    MyApp().run()
