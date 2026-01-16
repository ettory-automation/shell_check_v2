# 🖥️ Shell Audit Orchestrator
> Ferramenta agentless de auditoria e diagnóstico de infraestrutura Linux

- **Desenvolvido por**: Ettory Martins de Souza
- **Versão**: 2.0.0 (Production Ready)

O `Shell Audit Orchestrator` é uma ferramenta de diagnóstico e auditoria desenvolvida em Python, voltada para sistemas GNU/Linux, com foco em distribuições Debian-like e RHEL-like. Seu objetivo é automatizar a coleta de dados do sistema operacional e apresentar outputs formatados e organizados, facilitando:

- Análises de consumo de recursos computacionais
- Verificações de configuração de serviços
- Visualização de logs para auditorias técnicas
- Identificação de gargalos em ambientes produtivos

Com foco na praticidade, o `Shell Audit Orchestrator` pode ser executado em ambientes locais (bare metal, VMs ou containers) ou remotos via SSH.

<img width="617" height="358" alt="Screenshot From 2026-01-16 15-35-23" src="https://github.com/user-attachments/assets/1ad87c51-b9ca-4e3a-9a2a-af4c1dd25cc4" />

### ⚙️ Funcionalidades disponíveis

Até o momento, o Shell Audit Orchestrator oferece as seguintes funcionalidades:

#### 📊 Análise de CPU:

- Verificação detalhada do uso atual da(s) CPU(s)
- Identificação de picos e gargalos de processamento

#### 🧠 Análise de Memória RAM e Swap:

- Exibição do uso total, livre e cache
- Avaliação do uso de swap e memória real disponível

#### 💽 Análise de I/O de disco:

- Identificação de dispositivos com maior tempo de leitura/gravação
- Monitoramento de operações por segundo (IOPS)

#### 🌐 Análise de rede:

- Tráfego de entrada (inbound) e saída (outbound) por interface
- Dados úteis para identificar sobrecarga de banda ou uso anormal

#### 📦 Análise de uso de armazenamento:

- Uso percentual por mountpoint
- Destaca partições próximas da capacidade máxima
- Também utiliza verificação percentual por inodes

#### 🔍 Verificação de atualizações de kernel:

- Checagem da versão atual do kernel
- Notificação sobre versões mais recentes disponíveis
- Compatível com ambientes Debian-like (ex.: Debian, Ubuntu Server) e RHEL-like (ex.: RedHat Enterprise Linux, Oracle Linux, CentOS Linux)

#### 🔐 Ajustes finos para acesso remoto:

- Utilização de hostslists
- Utilização de autenticação via SSH por passwords ou keys

## 📦 Download e Utilização

### 🔁 Clonando com o Git (Recomendado)

Se o servidor possuir `git` instalado, basta executar:

```bash
git clone https://github.com/ettory-automation/shell-audit-orchestrator.git && mv shell-audit-orchestrator shell_check_v2
```

### 📥 Alternativa sem `git` (via `curl` ou `wget`):

Se o `git` não estiver disponível, use `curl` ou `wget` para baixar o projeto em formato `.zip`:

```bash
curl -L -o shell_check_v2.zip https://github.com/ettory-automation/shell-audit-orchestrator/archive/refs/heads/main.zip || \
wget -O shell_check_v2.zip https://github.com/ettory-automation/shell-audit-orchestrator/archive/refs/heads/main.zip 
```

#### 📂 Descompactando:

➤ Com `unzip`:

```bash
unzip shell_check_v2.zip && rm -rf shell_check_v2.zip && mv shell-audit-orchestrator-main shell_check_v2
```

> ⚠️ Nota: Se o servidor não possuir `unzip`, utilize o `Python` nativo para descompactar.

➤ Com `Python` 3.x:

```bash
python3 -m zipfile -e shell_check_v2.zip .
rm -rf shell_check_v2.zip && mv shell-audit-orchestrator-main shell_check_v2
```

➤ Com `Python` 2.x:

```bash
python -c "import zipfile; zipfile.ZipFile('shell_check_v2.zip', 'r').extractall('.')"
rm -rf shell_check_v2.zip && mv shell-audit-orchestrator-main shell_check_v2
```

### ⚡ Execução

➤ Faça o download do Poetry:

```bash
sudo apt install pipx || sudo dnf install pipx
pipx install poetry
```

Observação: Caso já possua o Poetry instalado no sistema, pule esta etapa. Para verificar se já o possui, basta utilizar o comando `poetry --version`.

➤ Entre dentro do diretório raiz do projeto, onde se localiza o arquivo pyproject.toml:

```bash
cd shell_check_v2
```

➤ Instale as dependências no virtual environment:

```bash
poetry install
```

➤ Ative o virtual environment do projeto via Poetry:

```bash
source $(poetry env info -p)/bin/activate
```

➤ Execute o script com o comando abaixo, utilizando o Poetry:

```bash
python -m src.shell_check.main 
```

Nota: Para desativar o virtual environment do Poetry, basta utilizar o comando `deactivate`.

##### Caso surjam dúvidas sobre a utilização do Poetry, a documentação oficial da ferramenta se encontra [aqui](https://python-poetry.org/docs/)

## ⚖️ Licença

Este projeto está licenciado sob a **GNU Affero General Public License v3.0 (AGLPv3)**.

Isso significa que você é livre para utilizar, modificar e distribuir o software, desde que as seguintes condições sejam atendidas:

1. Os créditos ao autor original sejam mantidos.
2. Se houver modificação do software por parte de terceiros, e em conjunto sua distribuição como um serviço (SaaS) em qualquer grau, o código-fonte das modificações aplicadas deverá ser aberto.

Consulte o arquivo `LICENSE` para mais detalhes.

## 📩 Contato

Caso surjam dúvidas, sugestões ou necessidade de suporte especializado para implementação deste software em produção, entre em contato pelo link do [Linkedin](https://linkedin.com/in/ettorymartins)
