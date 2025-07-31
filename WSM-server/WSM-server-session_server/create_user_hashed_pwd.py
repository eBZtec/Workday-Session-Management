import time
import sys
from passlib.context import CryptContext
from src.connections.database import DatabaseManager
from src.models.models import User
from getpass import getpass

dm = DatabaseManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Simples animação de loading com WSM
def wsm_loading(duration=3):
    frames = ["[W]   ", " [S]  ", "  [M] ", "   [W]", "  [S] ", " [M] ", " [W] ", " [S] ", " [M] "]
    end_time = time.time() + duration
    while time.time() < end_time:
        for frame in frames:
            sys.stdout.write(f"\rWSM Loading {frame}")
            sys.stdout.flush()
            time.sleep(0.2)
    sys.stdout.write("\r")  # Limpa linha

if __name__ == "__main__":
    _username = input("Enter new username: ")
    _password = getpass("Enter unhashed password: ")
    _hashed_password = hash_password(_password)
    print(f"Senha hasheada:\n{_hashed_password}")

    user = User(username=_username, hashed_password=_hashed_password)

    print("Adicionando usuário ao banco de dados...")
    wsm_loading()

    try:
        dm.add_entry(user)
        print("✅ Usuário adicionado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao adicionar usuário: {e}")
