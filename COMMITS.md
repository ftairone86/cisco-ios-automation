# Guia de Commits — Cisco IOS Automation

## Padrão adotado

```
<tipo>(<escopo>): <descrição curta>
```

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `refactor` | Refatoração sem mudança de comportamento |
| `docs` | Documentação |
| `chore` | Configuração, dependências, estrutura |
| `style` | Ajustes visuais de interface |

---

## Histórico de commits

```bash
# Inicialização
git commit -m "chore: configuração inicial (.gitignore, requirements)"

# Backend — gerenciador.py (antigo core.py)
git commit -m "feat(gerenciador): conexão SSH com Netmiko e modo simulação"
git commit -m "feat(gerenciador): configurar_vlans() e excluir_vlan()"
git commit -m "feat(gerenciador): backup_config() com timestamp no nome do arquivo"
git commit -m "feat(gerenciador): validar_config() via show vlan brief"
git commit -m "fix(gerenciador): set_base_prompt() após configurar_hostname()"

# Infraestrutura de threads
git commit -m "feat(worker): WorkerRede executa callables em QThread"
git commit -m "feat(sinais): sinais Qt para comunicação cross-thread"
git commit -m "chore(qt_core): importações PySide6 centralizadas"

# Frontend — módulos separados
git commit -m "feat(ui): layouts Qt Designer movidos para ui/"
git commit -m "feat(main): JanelaPrincipal com herança dupla e painel de log"
git commit -m "feat(conexao): AbaConexao — formulário SSH com feedback visual"
git commit -m "feat(vlans): AbaVlans — tabela editável e excluir no switch"
git commit -m "feat(deploy): AbaDeploy — deploy completo e alertas de validação"
git commit -m "fix(conexao): QueuedConnection em todos os sinais cross-thread"

# Correções de interface
git commit -m "fix(vlans): setMinimumWidth(110) no spinVid para exibir VLAN 4094"

# Documentação
git commit -m "docs: README atualizado com nova estrutura modular"
git commit -m "docs: ARQUITETURA.md com diagrama de camadas e fluxo de threads"
git commit -m "docs: COMMITS.md com padrão e histórico atualizado"
```
