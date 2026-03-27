import os
from qt_core import *
from send import FirewallSSHConfig, testar_conectividade_tunel_ipsec

class TunnelTestWorker(QObject):
    """Worker de teste de conectividade do túnel IPSec.

    Ele chama `send.testar_conectividade_tunel_ipsec()` em background.

    `tunnel_status` usa um inteiro para o estado:
    - 1: UP
    - 0: DOWN
    - -1: desconhecido (não deu para inferir)
    """

    tunnel_status = Signal(str, int, str)  # device, state, detail
    log = Signal(str)
    finished = Signal(dict)

    def __init__(
        self,
        *,
        forti_cfg: FirewallSSHConfig | None,
        palo_cfg: FirewallSSHConfig | None,
        simulacao: bool,
        forti_ping_dest: str | None,
        forti_ping_source: str | None,
        palo_ping_dest: str | None,
        palo_ping_source: str | None,
    ):
        super().__init__()
        self.forti_cfg = forti_cfg
        self.palo_cfg = palo_cfg
        self.simulacao = simulacao
        self.forti_ping_dest = forti_ping_dest
        self.forti_ping_source = forti_ping_source
        self.palo_ping_dest = palo_ping_dest
        self.palo_ping_source = palo_ping_source

    def run(self) -> None:
        """Executa o teste (estado das SAs + ping opcional)."""
        self.log.emit("[ipsec] Iniciando teste de conectividade do túnel (best-effort) ...")

        resultados = testar_conectividade_tunel_ipsec(
            forti_cfg=self.forti_cfg,
            palo_cfg=self.palo_cfg,
            simulacao=self.simulacao,
            forti_ping_dest=self.forti_ping_dest,
            forti_ping_source=self.forti_ping_source,
            palo_ping_dest=self.palo_ping_dest,
            palo_ping_source=self.palo_ping_source,
        )

        for device in ("fortigate", "paloalto"):
            info = resultados.get(device)
            if not isinstance(info, dict):
                continue
            up = info.get("tunnel_up")
            if up is True:
                state = 1
                detail = "UP"
            elif up is False:
                state = 0
                detail = "DOWN"
            else:
                state = -1
                detail = "desconhecido"
            self.tunnel_status.emit(device, state, detail)

        self.finished.emit(resultados)