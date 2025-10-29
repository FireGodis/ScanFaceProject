from encryption_utils import encrypt_existing_folder

# Rode apenas uma vez, fora do app
encrypt_existing_folder("cadastros", "senha123")
encrypt_existing_folder("faces", "senha123")

print("Criptografia concluída com sucesso!")