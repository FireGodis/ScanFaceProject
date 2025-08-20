function openFile(file) {
  const viewer = document.getElementById("file-viewer");
  viewer.classList.remove("hidden");

  if (file === "precos") {
    viewer.innerHTML = "<h2>📑 Tabela de preço dos clientes</h2><p>- Cliente A: R$100<br>- Cliente B: R$200<br>- Cliente C: R$300</p>";
  } else if (file === "horarios") {
    viewer.innerHTML = "<h2>🕒 Horários de funcionamento da empresa</h2><p>Seg-Sex: 08h - 18h<br>Sábado: 09h - 13h<br>Domingo: Fechado</p>";
  }
}

function openProtectedFolder() {
  document.getElementById("login-modal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("login-modal").classList.add("hidden");
}

function validateLogin() {
  const cpf = document.getElementById("cpf").value.trim();
  const senha = document.getElementById("senha").value.trim();
  const adminId = document.getElementById("adminId").value.trim();

  if (cpf === "098.876.654.42" && senha === "senhadificil" && adminId === "LHOE1989") {
    alert("Credenciais válidas! Agora prossiga com o reconhecimento facial.");
    window.location.href = "face_detection.html"; // redireciona para a câmera
  } else {
    alert("Dados incorretos. Tente novamente.");
  }
}
