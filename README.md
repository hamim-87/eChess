# ♟️ eChess — Physical Chess Game Powered by AI

**eChess** is a Microprocessor-based CSE316 project where a human can physically play chess against the **Stockfish** chess engine. The system integrates computer vision, a Vision Transformer model, ATmega32, Arduino, and robotic hardware to detect, process, and execute moves on a real chessboard.



## 🖼️ Project Visuals

<table>
  <tr>
    <td><img src="assets/img1.jpg" width="300"/><br/><center>(0, 0)</center></td>
    <td><img src="assets/img2.jpg" width="300"/><br/><center>(0, 1)</center></td>
  </tr>
  <tr>
    <td><img src="assets/img3.jpg" width="300"/><br/><center>(1, 0)</center></td>
    <td><img src="assets/img4.jpg" width="300"/><br/><center>(1, 1)</center></td>
  </tr>
</table>


## 🌐 Frontend & Backend

A **React frontend** and **FastAPI backend** provide the interface between physical events and digital processing.

- `/frontend` — React-based UI to visualize game state and AI response
- `/backend` — FastAPI server handling communication between model, Stockfish, and hardware

---

## 🧠 Human Move Detection

After the human makes a move and presses a physical button:

1. 📸 `vc.py` captures the image from a camera
2. 🔲 The image is cropped into **64 cells (8×8)**
3. 🧠 Each square is classified using a **Vision Transformer (ViT)** model
4. ♟️ Board state change is detected and converted into a **UCI move** format

---

## 📸 Dataset Collection

We created a **custom dataset** using our own chessboard and pieces to train the model.

[⬇️ Download the Dataset](#) *(insert dataset link here)*

---

## 🤖 Vision Transformer Model

- Trained via **Roboflow** on our custom dataset
- Achieved **99.99% accuracy**
- Deployed in the **cloud**, used through a REST **API**

---

## ♟️ Stockfish Integration

- The detected move (e.g., `e2e4`) is sent to the **Stockfish** engine
- Stockfish replies with the best move to play in **UCI format**
- The move is forwarded to the microcontroller for execution

---

## 🔌 Microcontroller Communication

- Laptop sends Stockfish's move via **I2C** to the **Arduino Uno**
- Arduino forwards the command to **ATmega32** using another **I2C** line

---

## 🤖 Physical Move Execution

- **ATmega32**, **stepper motors**, and **electromagnets** work together to:
  - Move the robot arm to the correct square
  - Pick up and place the chess piece

---



