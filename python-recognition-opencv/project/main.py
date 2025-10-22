
import os
import cv2
import sys
import numpy as np
import kivy
import time
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.splitter import Splitter
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.graphics.texture import Texture

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

cascade_path = resource_path(os.path.join("lib", "haarcascade_frontalface_default.xml"))
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    raise Exception(f"Erro ao carregar o classificador! Caminho verificado: {cascade_path}")


face_classifier = cv2.CascadeClassifier(cascade_path)


if face_classifier.empty():
    raise Exception(f"Erro ao carregar o classificador! Caminho verificado: {cascade_path}")


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
        color=Theme.BUTTON_TEXT_COLOR
    )
    btn.bind(on_press=callback)
    return btn


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(styled_label("Login", Theme.FONT_SIZE_TITLE, Theme.PRIMARY_COLOR))

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cpf_logado = None
        self.current_path = None
        self.file_editor = None
        self.editor_text = None

        # Layout principal (horizontal)
        self.main_layout = BoxLayout(orientation="horizontal", spacing=10, padding=10)
        self.add_widget(self.main_layout)

        # Painel esquerdo — navegação
        self.sidebar = BoxLayout(orientation="vertical", size_hint_x=0.3, spacing=10)

        self.path_label = styled_label("📁 Caminho atual:", 18)
        self.sidebar.add_widget(self.path_label)

        self.btn_new_folder = styled_button("➕ Nova Pasta", self.create_folder)
        self.btn_new_file = styled_button("📝 Novo Arquivo TXT", self.create_file)
        self.btn_back = styled_button("⬅️ Voltar", lambda *_: setattr(self.manager, 'current', 'home'))

        self.sidebar.add_widget(self.btn_new_folder)
        self.sidebar.add_widget(self.btn_new_file)
        self.sidebar.add_widget(self.btn_back)

        self.main_layout.add_widget(self.sidebar)

        # Painel direito — conteúdo da pasta
        self.files_area = BoxLayout(orientation="vertical", spacing=10)
        self.scroll_view = ScrollView()
        self.files_grid = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        self.files_grid.bind(minimum_height=self.files_grid.setter('height'))

        self.scroll_view.add_widget(self.files_grid)
        self.files_area.add_widget(self.scroll_view)
        self.main_layout.add_widget(self.files_area)

    def on_pre_enter(self, *args):
        """Carrega o diretório do usuário ao entrar"""
        base_dir = os.path.join("pasta_usuarios", self.cpf_logado)
        os.makedirs(base_dir, exist_ok=True)
        self.current_path = base_dir
        self.show_directory(self.current_path)

    def restore_files_view(self):
        """Restaura a view padrão de listagem (scroll + grid) no painel direito."""
        self.files_area.clear_widgets()
        if self.scroll_view.parent is None:
            self.files_area.add_widget(self.scroll_view)

    def show_directory(self, path):
        """Atualiza a visualização da pasta"""
        if self.scroll_view.parent is None:
            self.restore_files_view()

        self.files_grid.clear_widgets()
        self.path_label.text = f"📁 {os.path.relpath(path, 'pasta_usuarios')}"

        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            items = []

        for item in items:
            full_path = os.path.join(path, item)
            icon = "📁" if os.path.isdir(full_path) else "📄"
            btn = styled_button(f"{icon}\n{item}", lambda *_: None)
            btn.size_hint_y = None
            btn.height = 100

            # Clique esquerdo → abre
            btn.bind(on_release=lambda _, p=full_path: self.item_action(p))

            # Clique direito → menu
            btn.bind(on_touch_down=lambda instance, touch, p=full_path: self.on_right_click(instance, touch, p))
            self.files_grid.add_widget(btn)

    def on_right_click(self, instance, touch, path):
        """Cria menu de contexto (deletar/renomear) ao clicar com botão direito."""
        if touch.button == 'right' and instance.collide_point(*touch.pos):
            Clock.schedule_once(lambda dt: self.show_context_menu(touch.pos, path), 0.05)

    def show_context_menu(self, pos, path):
        """Mostra popup com opções: deletar e renomear."""
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup = Popup(title='Opções', size_hint=(None, None), size=(220, 180), auto_dismiss=True)

        btn_rename = styled_button("✏️ Renomear", lambda *_: (popup.dismiss(), self.rename_item(path)))
        btn_delete = styled_button("🗑️ Deletar", lambda *_: (popup.dismiss(), self.delete_item(path)))

        layout.add_widget(btn_rename)
        layout.add_widget(btn_delete)

        popup.add_widget(layout)
        popup.open()

        popup.pos = (pos[0] - 100, pos[1] - 60)

    def rename_item(self, path):
        """Renomeia arquivo/pasta"""
        old_name = os.path.basename(path)
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        text_input = TextInput(text=old_name, multiline=False, size_hint_y=None, height=40)
        layout.add_widget(Label(text="Digite o novo nome:"))
        layout.add_widget(text_input)

        btns = BoxLayout(size_hint_y=None, height=50, spacing=10, padding=10)
        btn_cancel = styled_button("❌ Cancelar", lambda *_: popup.dismiss())
        btn_confirm = styled_button("✅ Confirmar", lambda *_: self.confirm_rename(path, text_input.text, popup))
        btns.add_widget(btn_cancel)
        btns.add_widget(btn_confirm)

        layout.add_widget(btns)

        popup = Popup(title="Renomear", content=layout, size_hint=(None, None), size=(350, 200))
        popup.open()

    def confirm_rename(self, old_path, new_name, popup):
    

        base_dir = os.path.dirname(old_path)
        new_path = os.path.join(base_dir, new_name)

        try:
            os.rename(old_path, new_path)
        except Exception as e:
            print("Erro ao renomear:", e)
        else:
        # Se a pasta renomeada era a atual, atualizar current_path
            if self.current_path == old_path:
                self.current_path = new_path

        popup.dismiss()
        self.show_directory(self.current_path)


    def delete_item(self, path):
        """Deleta arquivo ou pasta (com confirmação se for pasta)."""
        if os.path.isdir(path):
            layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
            layout.add_widget(Label(text=f"Tem certeza que deseja apagar a pasta:\n[b]{os.path.basename(path)}[/b]?", markup=True))

            btns = BoxLayout(size_hint_y=None, height=50, spacing=10, padding=10)
            btn_cancel = styled_button("❌ Cancelar", lambda *_: popup.dismiss())
            btn_confirm = styled_button("✅ Confirmar", lambda *_: self.confirm_delete_folder(path, popup))

            btns.add_widget(btn_cancel)
            btns.add_widget(btn_confirm)
            layout.add_widget(btns)

            popup = Popup(title="Confirmação", content=layout, size_hint=(None, None), size=(400, 200))
            popup.open()
        else:
            os.remove(path)
            self.show_directory(self.current_path)

    def confirm_delete_folder(self, path, popup):
        """Confirma exclusão de pasta e recarrega diretório."""
        import shutil
        shutil.rmtree(path, ignore_errors=True)
        popup.dismiss()
        self.show_directory(self.current_path)

    def item_action(self, path):
        """Abre pasta ou arquivo conforme o tipo"""
        if os.path.isdir(path):
            self.enter_folder(path)
        else:
            self.open_file(path)

    def enter_folder(self, path):
        """Entra na pasta"""
        self.current_path = path
        self.show_directory(path)

    def create_folder(self, instance):
        """Cria nova pasta"""
        folder_name = f"NovaPasta_{len(os.listdir(self.current_path))}"
        new_path = os.path.join(self.current_path, folder_name)
        os.makedirs(new_path, exist_ok=True)
        self.show_directory(self.current_path)

    def create_file(self, instance):
        """Cria novo arquivo"""
        file_name = f"NovoArquivo_{len(os.listdir(self.current_path))}.txt"
        new_file = os.path.join(self.current_path, file_name)
        with open(new_file, "w", encoding="utf-8") as f:
            f.write("")
        self.show_directory(self.current_path)

    def open_file(self, file_path):
        """Abre o editor de texto no painel direito"""
        self.files_area.clear_widgets()
        self.file_editor = file_path

        title = styled_label(f"✏️ Editando: {os.path.basename(file_path)}", 18)
        self.files_area.add_widget(title)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.editor_text = TextInput(
            text=content,
            multiline=True,
            size_hint_y=0.85,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=16,
        )
        self.files_area.add_widget(self.editor_text)

        btns = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btns.add_widget(styled_button("💾 Salvar", self.save_file))
        btns.add_widget(styled_button("↩️ Voltar", lambda *_: (self.restore_files_view(), self.show_directory(self.current_path))))
        self.files_area.add_widget(btns)

    def save_file(self, instance):
        """Salva o arquivo editado"""
        with open(self.file_editor, "w", encoding="utf-8") as f:
            f.write(self.editor_text.text)
        self.show_directory(self.current_path)

class CreateAccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation="horizontal", padding=20, spacing=10)

        # Lado esquerdo (formulário)
        form_layout = GridLayout(cols=1, spacing=10, size_hint=(0.5, 1))
        form_layout.add_widget(styled_label("Criar Conta", Theme.FONT_SIZE_TITLE))

        self.nome_input = styled_input("Nome")
        form_layout.add_widget(self.nome_input)

        self.cpf_input = styled_input("CPF")
        form_layout.add_widget(self.cpf_input)

        self.cargo_input = styled_input("Cargo")
        form_layout.add_widget(self.cargo_input)

        self.email_input = styled_input("Email")
        form_layout.add_widget(self.email_input)

        self.senha_input = styled_input("Senha", password=True)
        form_layout.add_widget(self.senha_input)

        self.progress_label = styled_label("Aguardando captura...")
        form_layout.add_widget(self.progress_label)

        capturar_btn = styled_button("Iniciar Captura de Rosto", self.start_capture)
        form_layout.add_widget(capturar_btn)

        salvar_btn = styled_button("Salvar Cadastro", self.save_account)
        form_layout.add_widget(salvar_btn)

        voltar_btn = styled_button("Voltar", lambda *_: setattr(self.manager, 'current', 'login'))
        form_layout.add_widget(voltar_btn)

        main_layout.add_widget(form_layout)

        
        self.camera_widget = Image(size_hint=(0.5, 1))
        main_layout.add_widget(self.camera_widget)

        self.add_widget(main_layout)

        
        self.capture = None
        self.frames_captured = 0
        self.capturing = False

    def face_extractor(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return None
        for (x, y, w, h) in faces:
            return img[y:y+h, x:x+w]

    def start_capture(self, instance):
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

    def stop_capture(self):
        self.capturing = False
        if self.capture:
            self.capture.release()
            self.capture = None
        Clock.unschedule(self.update_camera)

    def save_account(self, instance):
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

        # Layout principal
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.layout.add_widget(styled_label("Reconhecimento Facial", Theme.FONT_SIZE_TITLE))

        self.status_label = styled_label("Posicione seu rosto na câmera...")
        self.layout.add_widget(self.status_label)

        self.camera_widget = Image(size_hint=(1, 1))
        self.layout.add_widget(self.camera_widget)

        # Botões inferiores
        self.buttons_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.voltar_btn = styled_button("Voltar", lambda *_: setattr(self.manager, 'current', 'login'))
        self.buttons_box.add_widget(self.voltar_btn)
        self.layout.add_widget(self.buttons_box)

        self.add_widget(self.layout)

        # Controle de captura
        self.model = None
        self.capture = None
        self.event = None

    def show_support_button(self):
        """Exibe botão de suporte se ainda não estiver visível"""
        if not any(btn.text.startswith("Dificuldades") for btn in self.buttons_box.children):
            suporte_btn = styled_button(
                "Dificuldades no login? Suporte",
                lambda *_: setattr(self.manager, 'current', 'support')
            )
            suporte_btn.size_hint_x = 0.8
            self.buttons_box.add_widget(suporte_btn)

    def show_register_face_button(self):
        """Exibe botão para ir à tela de cadastro"""
        if not any(btn.text.startswith("Cadastrar rosto") for btn in self.buttons_box.children):
            cadastrar_btn = styled_button(
                "Cadastrar rosto agora",
                lambda *_: setattr(self.manager, 'current', 'create_account')
            )
            self.buttons_box.add_widget(cadastrar_btn)

    def on_enter(self, *args):
        cpf = self.cpf_logado
        if not cpf:
            self.status_label.text = "Erro: Nenhum CPF em uso."
            self.show_support_button()
            return

        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            self.status_label.text = "Erro: não foi possível acessar a câmera"
            self.show_support_button()
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
            self.show_register_face_button()
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
            self.show_support_button()
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
                    time.sleep(2)
                    self.manager.current = "home"
                else:
                    self.status_label.text = f"Face não reconhecida ({confidence}%)"
                    self.show_support_button()


class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=30, spacing=20)

        layout.add_widget(styled_label("Suporte Técnico", Theme.FONT_SIZE_TITLE))
        layout.add_widget(styled_label("Se estiver enfrentando dificuldades no login, entre em contato:"))
        layout.add_widget(styled_label("+55 61 991876314", Theme.FONT_SIZE_LABEL, [0, 0.7, 0, 1]))

        voltar_btn = styled_button("Voltar", lambda *_: setattr(self.manager, 'current', 'recognition'))
        layout.add_widget(voltar_btn)

        self.add_widget(layout)

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
        sm.add_widget(SupportScreen(name="support"))
        sm.add_widget(ResetRequestScreen(name="reset_request"))
        sm.add_widget(FileManagerScreen(name="file_manager"))  # ✅ nova tela
        return sm

if __name__ == "__main__":
    MyApp().run()
