import os
from qt_core import *
from send import FirewallSSHConfig, FortigateSender, PaloAltoSender

class ConnectionWorker(QObject):
    """Worker de teste de conexão.

    Executa em um `QThread` e emite:
    - `status(device, connected, detail)` para atualizar o status na GUI.
    - `log(text)` para registrar eventos em tela.
    - `finished()` para sinalizar término.

    `device` deve ser "fortigate" ou "paloalto".
    """

    status = Signal(str, bool, str)  # device, connected, detail
    log = Signal(str)
    finished = Signal()

    def __init__(self, device: str, cfg: FirewallSSHConfig, *, simulacao: bool):
        super().__init__()
        self.device = device
        self.cfg = cfg
        self.simulacao = simulacao

    def run(self) -> None:
        """Abre e fecha uma conexão SSH apenas para validar credenciais/rede."""
        sender = None
        try:
            if self.device == "fortigate":
                sender = FortigateSender(self.cfg, simulacao=self.simulacao)
            elif self.device == "paloalto":
                sender = PaloAltoSender(self.cfg, simulacao=self.simulacao)
            else:
                raise ValueError(f"Device desconhecido: {self.device}")

            self.log.emit(f"[{self.device}] Testando conexão em {self.cfg.host}:{self.cfg.port} ...")
            prompt = sender.conectar()
            self.status.emit(self.device, True, f"Conectado ({prompt})")
        except Exception as e:
            self.status.emit(self.device, False, f"Falhou: {e}")
        finally:
            try:
                if sender is not None:
                    sender.desconectar()
            except Exception:
                pass
            self.finished.emit()


