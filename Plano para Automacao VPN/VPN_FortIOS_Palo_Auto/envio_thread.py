import os
from qt_core import *
from send import FirewallSSHConfig, FortigateSender, PaloAltoSender, extrair_blocos_forti_palo

class SendWorker(QObject):
    """Worker de envio.

    Também roda em um `QThread`. Ele:
    1) Separa o texto em blocos Forti/Palo via `extrair_blocos_forti_palo()`.
    2) Para cada firewall que tiver credenciais, conecta e envia o bloco.

    Observação importante:
    - O envio aqui é feito *por firewall* (com try/except separados) para que
      uma falha em um não impeça o outro.
    """

    status = Signal(str, bool, str)  # device, ok, detail
    log = Signal(str)
    finished = Signal(dict)  # resultados

    def __init__(
        self,
        conteudo_combinado: str,
        forti_cfg: FirewallSSHConfig | None,
        palo_cfg: FirewallSSHConfig | None,
        *,
        commit_palo: bool,
        simulacao: bool,
    ):
        super().__init__()
        self.conteudo_combinado = conteudo_combinado
        self.forti_cfg = forti_cfg
        self.palo_cfg = palo_cfg
        self.commit_palo = commit_palo
        self.simulacao = simulacao

    def run(self) -> None:
        """Executa o envio e retorna um dict com as saídas/erros."""
        resultados: dict[str, str] = {}
        forti_script, palo_script = extrair_blocos_forti_palo(self.conteudo_combinado)

        if self.forti_cfg and forti_script.strip():
            self.log.emit(f"[fortigate] Enviando comandos para {self.forti_cfg.host}:{self.forti_cfg.port} ...")
            forti = None
            try:
                forti = FortigateSender(self.forti_cfg, simulacao=self.simulacao)
                prompt = forti.conectar()
                out = forti.enviar_script(forti_script)
                resultados["fortigate"] = out
                self.status.emit("fortigate", True, f"Enviado ({prompt})")
            except Exception as e:
                resultados["fortigate_error"] = str(e)
                self.status.emit("fortigate", False, f"Falhou: {e}")
            finally:
                try:
                    if forti is not None:
                        forti.desconectar()
                except Exception:
                    pass
        elif self.forti_cfg and not forti_script.strip():
            resultados["fortigate_info"] = "Bloco Fortigate vazio."

        if self.palo_cfg and palo_script.strip():
            self.log.emit(f"[paloalto] Enviando comandos para {self.palo_cfg.host}:{self.palo_cfg.port} ...")
            palo = None
            try:
                palo = PaloAltoSender(self.palo_cfg, simulacao=self.simulacao)
                prompt = palo.conectar()
                out = palo.enviar_script(palo_script, commit=self.commit_palo)
                resultados["paloalto"] = out
                self.status.emit("paloalto", True, f"Enviado ({prompt})")
            except Exception as e:
                resultados["paloalto_error"] = str(e)
                self.status.emit("paloalto", False, f"Falhou: {e}")
            finally:
                try:
                    if palo is not None:
                        palo.desconectar()
                except Exception:
                    pass
        elif self.palo_cfg and not palo_script.strip():
            resultados["paloalto_info"] = "Bloco Palo Alto vazio."

        if not resultados:
            resultados["info"] = "Nada para enviar (blocos vazios ou credenciais não informadas)."

        self.finished.emit(resultados)