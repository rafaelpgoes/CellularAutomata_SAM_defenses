# 🛡️ A2/AD Simulation: Autômato Celular de Defesa Aérea

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![NumPy](https://img.shields.io/badge/NumPy-Vectorized-013243)
![Pygame](https://img.shields.io/badge/Pygame-Simulation-vk)
![Status](https://img.shields.io/badge/Status-Completed-success)

> Um simulador de **Saturação de Defesa e Negação de Área (A2/AD)** baseado em Autômatos Celulares de fluxo, desenvolvido para análise de eficácia de sistemas antiaéreos contra enxames heterogêneos.

---

## 📖 Sobre o Projeto

Este projeto é uma modelagem computacional que simula o conflito dinâmico entre um sistema de defesa aérea integrado (IADS) e uma força atacante composta por Drones, Caças e Aeronaves Furtivas (Stealth).

Diferente de modelos estáticos, esta simulação utiliza **lógica vetorial (NumPy)** para processar o fluxo de milhares de agentes simultaneamente, incorporando mecânicas complexas como:
* **SEAD (Suppression of Enemy Air Defenses):** Capacidade do inimigo destruir baterias SAM enquanto elas recarregam.
* **Guerra Eletrônica:** Uso de *Chaff* e interferência gerada por aeronaves abatidas.
* **Fadiga de Sistema:** Análise do ponto de ruptura onde a defesa colapsa devido à saturação.

---

## 🚀 Funcionalidades Principais

* **⚡ Processamento Vetorial:** Alta performance usando operações de matriz do NumPy em vez de loops tradicionais.
* **🧠 Comportamentos Emergentes:** O sistema demonstra falhas em cascata, criação de corredores aéreos e saturação temporal sem serem explicitamente programados.
* **✈️ Inimigos Heterogêneos:**
    * **Drones:** Lentos, numerosos (Enxame).
    * **Caças:** Rápidos (Velocidade supersônica/Pulo de células).
    * **Stealth:** Baixa probabilidade de detecção por radar.
* **📊 Análise de Dados:** Geração automática de gráficos (Matplotlib) ao final da simulação para avaliar Vazamento (*Breakthrough*) vs. Interceptação.

---

## 🎨 Legenda Visual (Estados)

A simulação roda em tempo real via **Pygame**. Entenda o que cada cor representa:

| Cor | Representação | Descrição |
| :--- | :--- | :--- |
| 🟩 **Verde** | **SAM Pronta** | Bateria antiaérea ativa, pronta para disparar. |
| 🟨 **Amarelo** | **SAM em Recarga** | Bateria vulnerável. **Pode ser destruída** se um inimigo passar por cima (SEAD). |
| 🟥 **Vermelho** | **Drone** | Unidade de ataque padrão. Baixa resistência. |
| 🟦 **Ciano** | **Caça** | Unidade rápida. Move-se 2 células por turno. |
| ⬛ **Cinza Escuro** | **Stealth** | Unidade furtiva. Tem chance de passar despercebida pela defesa. |
| ⬜ **Cinza Claro** | **Interferência** | Destroços/Chaff. Bloqueia a visão das SAMs vizinhas (Jamming). |

---

## 🔧 Instalação e Execução

### Pré-requisitos
Certifique-se de ter o Python 3 instalado. As dependências são mínimas:

```bash
pip install pygame numpy matplotlib
```

## 🔧 Como Rodar

Clone o repositório e execute o script principal:

```bash
python simulation_advanced.py
```

### Durante a simulação: Pressione R para reiniciar o cenário.
### Para ver os gráficos: Feche a janela da simulação (o gráfico será gerado automaticamente).

## 🔧 Tecnologias Utilizadas

*  **Python 3:** Linguagem base.
*  **NumPy:** Lógica de Autômatos Celulares, array shifting e máscaras booleanas.
* **Pygame:** Renderização gráfica em tempo real.
* **Matplotlib:** Plotagem de dados estatísticos acumulados.
