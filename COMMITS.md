# Guia de Commits — Gerenciador de VLANs

```bash
# Inicialização
git commit -m "chore: configuração inicial (.gitignore, requirements)"

# Backend
git commit -m "feat(core): conexão SSH com Netmiko e modo simulação"
git commit -m "feat(core): configurar_vlans() e excluir_vlan()"
git commit -m "feat(core): backup_config() com timestamp no nome do arquivo"
git commit -m "feat(core): validar_config() via show vlan brief"
git commit -m "fix(core): set_base_prompt() após configurar_hostname()"


# Frontend
git commit -m "feat(ui): layouts Qt Designer e arquivos pyside6-uic"
git commit -m "feat(app): JanelaPrincipal com herança dupla + painel de log"
git commit -m "feat(app): AbaConexao — formulário SSH com feedback visual"
git commit -m "feat(app): AbaVlans — tabela editável e excluir no switch"
git commit -m "feat(app): AbaDeploy — deploy completo e alertas de validação"
git commit -m "fix(app): QueuedConnection em todos os sinais cross-thread"

# Documentação
git commit -m "docs: README com badges, uso e notas técnicas"
git commit -m "docs: ARCHITECTURE.md com diagrama de camadas"
```

