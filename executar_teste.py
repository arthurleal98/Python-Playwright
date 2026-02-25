import subprocess
from datetime import datetime
import os


subprocess.run(["pytest", f"--html=relatorio.html"])

# 2. Executa o modificador de relatório
print("Executando modificador...")
subprocess.run(["python", "modificador_relatorio.py", "relatorio.html"])

# excluir relatorio.html
#os.remove("relatorio.html")

print("Fluxo concluído!")
