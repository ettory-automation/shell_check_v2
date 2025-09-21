# 🖥️ Shell Check v2

O `Shell Check v2` é uma ferramenta de diagnóstico e auditoria desenvolvida em Python, voltada para sistemas Linux-based. Seu objetivo é automatizar a coleta de dados do sistema operacional e apresentar outputs formatados e organizados, facilitando:

- Análises de consumo de recursos computacionais
- Verificações de configuração de serviços
- Visualização de logs para auditorias técnicas
- Identificação de gargalos em ambientes produtivos

Com foco na praticidade, o `Shell Check v2` pode ser executado em ambientes locais (bare metal, VMs ou containers) ou remotos via SSH.

<img width="664" height="417" alt="image" src="https://github.com/user-attachments/assets/918f119d-f123-4c7f-ae4b-832a329c2b0f" />

### ⚙️ Funcionalidades disponíveis

Até o momento, o Shell Check v2 oferece as seguintes funcionalidades:

#### 📊 Análise de CPU:

- Verificação detalhada do uso atual da(s) CPU(s)
- Identificação de picos e gargalos de processamento

<img width="405" height="920" alt="cpu-consumption-analysis" src="https://github.com/user-attachments/assets/35b9e1fa-60f5-463e-bacc-68a07d7ef961" />

<img width="453" height="289" alt="image" src="https://github.com/user-attachments/assets/8df41dd6-7229-42de-8b44-6505bee37d65" />

#### 🧠 Análise de Memória RAM e Swap:

- Exibição do uso total, livre e cache
- Avaliação do uso de swap e memória real disponível

<img width="610" height="730" alt="image" src="https://github.com/user-attachments/assets/66d53455-7277-4d8c-a76f-76017f5d7c75" />

#### 💽 Análise de I/O de disco:

- Identificação de dispositivos com maior tempo de leitura/gravação
- Monitoramento de operações por segundo (IOPS)

<img width="415" height="476" alt="image" src="https://github.com/user-attachments/assets/8cc27b10-7e06-4e90-957a-002bcc4931b4" />

<img width="394" height="466" alt="image" src="https://github.com/user-attachments/assets/2f538f46-b5d7-49f5-b3ad-74fd8f4a45e8" />

#### 🌐 Análise de rede:

- Tráfego de entrada (inbound) e saída (outbound) por interface
- Dados úteis para identificar sobrecarga de banda ou uso anormal

<img width="572" height="513" alt="image" src="https://github.com/user-attachments/assets/a0799dd6-6d06-4c93-8305-b024bd577b54" />

#### 📦 Análise de uso de armazenamento:

- Uso percentual por mountpoint
- Destaca partições próximas da capacidade máxima
- Também utiliza verificação percentual por inodes

<img width="808" height="534" alt="image" src="https://github.com/user-attachments/assets/cb47a787-bc6f-485a-b43f-8470cff73835" />

#### 🔍 Verificação de atualizações de kernel:

- Checagem da versão atual do kernel
- Notificação sobre versões mais recentes disponíveis
- Compatível com ambientes Debian-like (ex.: Debian, Ubuntu Server) e RHEL-like (ex.: RedHat Enterprise Linux, Oracle Linux, CentOS Linux)

<img width="1890" height="901" alt="image" src="https://github.com/user-attachments/assets/b2ec4927-431e-4810-8817-cd1758fc4266" />


#### 🔐 Ajustes finos para acesso remoto:

- Utilização de hostslists
- Utilização de autenticação via SSH por passwords ou keys

<img width="608" height="405" alt="image" src="https://github.com/user-attachments/assets/0fa13249-378f-49e0-8d22-f304edecb443" />

<img width="580" height="457" alt="image" src="https://github.com/user-attachments/assets/e2e10f33-3f36-42da-a89d-125bbdf99daf" />

<img width="511" height="754" alt="image" src="https://github.com/user-attachments/assets/6d1250fb-5800-43d8-a132-280ec953e9a2" />

## 📦 Download e Utilização

### 🔁 Clonando com o Git (Recomendado)

Se o servidor possuir `git` instalado, basta executar:

```bash
git clone https://github.com/ettory-automation/shell_check_v2.git
```

### 📥 Alternativa sem `git` (via `curl` ou `wget`):

Se o `git` não estiver disponível, use `curl` ou `wget` para baixar o projeto em formato `.zip`:

```bash
curl -L -o shell_check_v2.zip https://github.com/ettory-automation/shell_check_v2/archive/refs/heads/main.zip || \
wget -O shell_check_v2.zip https://github.com/ettory-automation/shell_check_v2/archive/refs/heads/main.zip 
```

#### 📂 Descompactando:

➤ Com `unzip`:

```bash
unzip shell_check_v2.zip && rm -rf shell_check_v2.zip && mv shell_check_v2-main shell_check_v2
```

> ⚠️ Nota: Se o servidor não possuir `unzip`, utilize o `Python` nativo para descompactar.

➤ Com `Python` 3.x:

```bash
python3 -m zipfile -e shell_check_v2.zip .
rm -rf shell_check_v2.zip && mv shell_check_v2-main shell_check_v2
```

➤ Com `Python` 2.x:

```bash
python -c "import zipfile; zipfile.ZipFile('shell_check_v2.zip', 'r').extractall('.')"
rm -rf shell_check_v2.zip && mv shell_check_v2-main shell_check_v2
```

### ⚡ Execução

➤ Faça o download do Poetry:

```bash
sudo apt install pipx || sudo dnf install pipx
pipx install poetry
```

Observação: Caso já possua o Poetry instalado no sistema, pule esta etapa. Para verificar se já o possui, basta utilizar o comando `poetry --version`.

➤ Entre dentro do diretório raiz do projeto e ative o virtual environment do Poetry:

```bash
cd shell_check_v2/src
source $(poetry env info -p)/bin/activate
```

➤ Instale as dependências no virtual environment:

```bash
poetry install
```

➤ Execute o script com o comando abaixo, utilizando o Poetry:

```bash
python -m shell_check.main 
```

Nota: Para desativar o virtual environment do Poetry, basta utilizar o comando `deactivate`.

##### Caso surjam dúvidas sobre a utilização do Poetry, a documentação oficial da ferramenta se encontra [aqui](https://python-poetry.org/docs/)
