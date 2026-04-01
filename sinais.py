from qt_core import *

# SINAIS — ponte segura entre QThread e a GUI

class Sinais(QObject):
   
    log       = Signal(str, str)   # (mensagem, nível: info | ok | erro | aviso)
    concluido = Signal(object)     # resultado da operação
    progresso = Signal(int)        # 0-100 para a QProgressBar

# Worker não sabe que existe uma ProgressBar; ele apenas avisa que o progresso mudou. 
# A GUI decide o que fazer com essa informação

# WORKER — executa operação de rede em QThread separada
