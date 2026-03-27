# Block & Hole GenLayer Mini Game

> A competitive 3D puzzle game powered by **GenLayer's Intelligent Contracts** and **Optimistic Democracy** consensus. Roll the block into the hole but now, AI is the judge.

---

## 🎮 What is Block & Hole?

Block & Hole is a weekly multiplayer puzzle game built on top of [GenLayer](https://genlayer.com). Players roll a 3D block across a floating grid of tiles and guide it into the goal hole. Simple to learn hard to master.

What makes it unique: **your performance is judged by GenLayer's AI validators**, not a deterministic formula. The AI evaluates your efficiency, style, and speed and the entire network reaches consensus on your grade through **Optimistic Democracy**.

---

## ⚡ GenLayer at the Core

This game is not just *using* GenLayer GenLayer **is** the game mechanic.

### Intelligent Contract : `weekly_challenge.py`

The smart contract handles:

- **AI Judged Scoring** : After completing a level your moves and time are sent to the contract. An LLM evaluates your performance and assigns a grade:
  - 🥇 **S Rank** : Exceptional efficiency
  - 🥈 **A Rank** : Smart and precise
  - 🥉 **B Rank** : Good effort
  - **C Rank** : Keep practicing

- **Optimistic Democracy Consensus**  Multiple validator nodes independently run the AI evaluation. They must reach consensus on your grade before your score is accepted on-chain. If validators disagree your score is re-evaluated.

- **Anti Cheat by Design** : The AI detects suspicious scores (too fast, impossible move counts). No score passes without validator consensus.

- **Weekly Leaderboard** : One attempt per wallet per week. Scores are ranked by XP granted by the AI judge.

```python
# The AI prompt used to judge your score
"You are judging a Block & Hole puzzle performance.
 Moves: {moves}, Time: {time_sec}s.
 Grade the player: S, A, B, or C."
```

---

## 🏠 Room System Play With Friends

Beyond the weekly challenge, players can create **private or public rooms** to compete head to head.

### How Rooms Work

1. **Create a Room** : Choose a level (1–6) and room type:
   - 🌍 **Public** : Visible in the open lobby, anyone can join
   - 🔒 **Private** : Share the room code directly with friends

2. **Join a Room** : Browse open public rooms in the lobby or enter a room code

3. **Real-Time Race** : Both players start the same level simultaneously. A WebSocket server syncs the room state in real time.

4. **AI-Judged Results** : When both players finish, GenLayer validators evaluate each performance independently. The room leaderboard shows grades, XP, and the winner.

### Room Architecture

```
Player A ──┐
           ├── WebSocket Server (ws://localhost:3001)
Player B ──┘       │
                   ├── Room state management
                   ├── Real-time sync (join, score, finish)
                   └── Broadcasts game-start to all players

           GenLayer Contract
                   │
                   ├── submit_room_score()  → AI grades each player
                   ├── get_room_leaderboard() → Final standings
                   └── Optimistic Democracy → Consensus on grades
```

---

## 📅 Weekly Challenge

Every week, a new level is selected automatically based on the current week number. Players get **one attempt per week**  make it count.

- ⏱ **5-minute countdown** : the clock is ticking
- 🧠 **AI evaluates** moves, time, and efficiency
- 🏆 **Global leaderboard** : compete against all players worldwide
- 🔁 **Resets weekly** : new level, new chance to climb the ranks

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Game Engine | p5.js (WEBGL 3D) |
| Blockchain | GenLayer (Optimistic Democracy) |
| Smart Contract | Python (GenLayer Intelligent Contract) |
| Real-Time Multiplayer | Node.js + WebSocket (`ws`) |
| Wallet | MetaMask + genlayer-js |
| Frontend | Vanilla HTML/CSS/JS |

---

### Prerequisites
- Node.js
- Python 3
- EVM Wallet

### Key Functions

| Function | Type | Description |
|----------|------|-------------|
| `submit_score(player, week, moves, time)` | Write | Submit weekly score — AI judges and validates |
| `has_played_this_week(player, week)` | View | Check if player already submitted |
| `get_weekly_leaderboard(week)` | View | Get ranked scores for the week |
| `get_player_score(player, week)` | View | Get individual player result |
| `submit_room_score(room_id, player, week, moves, time)` | Write | Submit score for a room match |
| `get_room_leaderboard(room_id)` | View | Get room match results |

---

## 🧠 Why GenLayer?

Traditional games use deterministic formulas for scoring. Block & Hole uses **subjective AI consensus**:

- A player finishing in 30 moves might get S rank for a hard level but C rank for an easy one
- The AI considers *relative* performance, not absolute numbers
- Multiple validators must *agree*  making the system fair, transparent, and cheat resistant

This is what **Optimistic Democracy** enables: subjective, AI powered judgments that the entire network validates.

---

## 🏆 Submission: GenLayer Mini Game Challenge

| Requirement | Implementation |
|-------------|---------------|
| ✅ Multiplayer / Rooms | Public & private rooms with real time WebSocket |
| ✅ 5–15 min sessions | 5 minute countdown per challenge |
| ✅ Replayable weekly | New level every week, one attempt per wallet |
| ✅ Leaderboard + XP | AI assigned XP, on-chain global leaderboard |
| ✅ Intelligent Contract core | AI judges every score  no contract, no rank |
| ✅ Optimistic Democracy | Validators reach consensus on every grade |
| ✅ Subjectivity + AI | Grade depends on level difficulty, not just numbers |

---

*Built by rivale with ❤️ for the GenLayer community where subjectivity meets consensus.*
