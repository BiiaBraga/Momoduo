# 🐱 Momoduo 🎵

<p align="center">
  <img src="momoduo.png" alt="Screenshot do jogo Momoduo" width="600"/>
</p>

**Momoduo** é um jogo de plataforma **cooperativo para 2 jogadores**, desenvolvido com a engine retrô **Pyxel**.  
Inspirado na dinâmica caótica e divertida de **PICO PARK**, o jogo desafia a coordenação da dupla em níveis que exigem **sincronia perfeita**.

Para tornar a experiência ainda mais imersiva, a trilha sonora conta com uma versão **8-bit de _"Faded In My Last Song"_ do grupo de K-pop NCT**, trazendo uma atmosfera única para as partidas.

---

## 📥 Guia de Instalação (2026)

### 1️⃣ Instalação do Python

O jogo requer o **Python** instalado.

1. Acesse o site oficial: https://www.python.org  
2. Baixe a versão mais recente para o seu sistema operacional  
3. ⚠️ **Importante (Windows):** durante a instalação, marque a opção  
   **“Add Python to PATH”**

---

### 2️⃣ Instalação da Engine Pyxel

Com o Python instalado, abra o terminal (ou CMD) e execute:

```bash
pip install -U pyxel
```

---

### 3️⃣ Clonando ou Baixando o Jogo

Baixe ou clone este repositório e extraia os arquivos em uma pasta de sua preferência.

Certifique-se de que **todos os arquivos estejam na mesma pasta**, especialmente:

- `main.py`
- `servidor.py`
- `Intro.pyxres`
- `levels_hello_stop.pyxres`
- `levels.pyxres`
- `player.pyxres`
- `Change_character`
- `creditos.pyxres`

⚠️ O jogo não funcionará corretamente se os arquivos estiverem separados em pastas diferentes ou fora do diretório principal.

---

### 🌐 4️⃣ Configuração de Rede (Multiplayer Local)

O **Momoduo** é jogado em **rede local (LAN)**.  
Ambos os jogadores precisam estar conectados **ao mesmo Wi-Fi ou rede cabeada**.

---

### 🖥️ 5️⃣ Iniciar o Servidor (Host)

Um dos jogadores será o **Host** do jogo.

1. Abra o terminal na pasta do jogo  
2. Descubra seu **IP local**:

**Windows**
```bash
ipconfig
```

> Procure por **Endereço IPv4** (exemplo: `192.168.0.10`)

**Linux / Mac**
```bash
hostname -I
```

3. Execute o servidor:
```bash
python servidor.py
```

4. Informe:
   - O **IP local**
   - Uma **porta** (exemplo: `5000`)

---

### 🎮 6️⃣ Iniciar o Jogo

Agora, **ambos os jogadores** (inclusive o Host) devem:

1. Abrir um novo terminal na pasta do jogo  
2. Executar o comando:
```bash
pyxel run main.py
```

3. Quando solicitado pelo jogo, digite:
   - **IP do servidor**
   - **Porta configurada**

---

### 🕹️ 7️⃣ Mecânicas e Controles

#### 🤝 Cooperação Total
Assim como em **PICO PARK**, o progresso no jogo depende totalmente da cooperação entre os dois jogadores.  
Os puzzles exigem **sincronia, comunicação e trabalho em equipe**.

---

#### 🎵 Trilha Sonora
O jogo conta com uma versão **8-bit de _"Faded In My Last Song"_ do grupo NCT**, trazendo ritmo e identidade à experiência.

---

#### 🎮 Controles

| Ação | Tecla |
|------|------|
| Movimentação | Setas ou **W / A / S / D** |
| Pular | **Espaço** |

---

### 🛠️ 8️⃣ Tecnologias Utilizadas

- **Python**
- **Pyxel Engine**
- **Multiplayer em rede local (LAN / sockets)**

---

### 🎨 9️⃣ Estilo Visual

- Pixel Art retrô  
- Interface simples e minimalista  
- Personagens carismáticos e animações leves  

---

### 🧠 🔟 Objetivo do Projeto

Este projeto foi desenvolvido com foco em:

- jogos cooperativos  
- aplicação de conceitos de programação em Python  
- comunicação em rede utilizando multiplayer local  
- criação de puzzles baseados em colaboração entre jogadores  

---

### 🛠️ 1️⃣1️⃣ Créditos e Inspirações

- 🎮 **Game Design:** Inspirado em *PICO PARK*  
- 🎵 **Música:** *Faded In My Last Song* — **NCT** (arranjo 8-bit)  
- 🧰 **Engine:** **Pyxel Engine** — Takashi Kitao  

---

💜 Projeto desenvolvido para aprendizado, diversão e caos cooperativo.

✨Feito por Beatriz Braga Silva
