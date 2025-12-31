Voice Maze Solver 

An interactive maze game built with Python and Pygame where you control the character using real-time voice commands.

# Features
- **Offline Voice Recognition**: Uses the Vosk engine for low-latency command processing.
- **Procedural Maze Generation**: Every game is a new challenge.
- **Command Queueing**: Chain commands like "up, up, right" and watch the ball follow the path.

# Prerequisites
Before running, you must download a Vosk model.
1. Visit [Vosk Models](https://alphacephei.com/vosk/models).
2. Download a small English model (e.g., `vosk-model-small-en-us-0.15`).
3. Extract it into the project folder and rename the folder to `model`.

# Installation
1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/voice-maze-solver.git](https://github.com/Nishant_MM/voice-maze-solver.git)
   cd voice-maze-solver
2. Install Dependencies:
  pip install -r requirements.txt
