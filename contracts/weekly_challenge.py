# v0.3.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json


class WeeklyBlockChallenge(gl.Contract):
    scores: TreeMap[str, str]       # key="week:player"      value="moves,time_sec,xp,grade,verdict"
    rooms: TreeMap[str, str]        # key="room_id"           value="host,level,week"
    room_scores: TreeMap[str, str]  # key="room_id:player"    value="moves,time_sec,xp,grade,verdict"

    def __init__(self) -> None:
        self.scores = TreeMap()
        self.rooms = TreeMap()
        self.room_scores = TreeMap()

    # ── helpers ────────────────────────────────────────────────────────────────

    def _grade(self, moves: int, time_sec: int) -> str:
        if moves <= 20 and time_sec <= 60:
            return "S"
        if moves <= 35 and time_sec <= 120:
            return "A"
        if moves <= 60 and time_sec <= 240:
            return "B"
        return "C"

    def _validate(self, level: int, moves: int, time_sec: int) -> None:
        prompt = (
            f"A player completed level {level} of Block and Hole puzzle game "
            f"in {moves} moves and {time_sec} seconds. "
            f"Block and Hole is a 3D rolling block puzzle where you roll a block into a hole. "
            f"Is this a plausible human score? "
            f"Reject if: fewer than 3 moves, under 5 seconds, over 10000 moves, or over 7200 seconds. "
            f"Respond ONLY with JSON in this exact format: {{\"is_valid\": bool}} "
            f"Nothing else. No extra text."
        )
        def check():
            r = gl.nondet.exec_prompt(prompt)
            return r.replace("```json", "").replace("```", "").strip()
        result = gl.eq_principle.prompt_comparative(check, "The value of is_valid has to match")
        parsed = json.loads(result)
        if not parsed.get("is_valid", False):
            raise Exception("Score rejected by AI validators: suspected cheating")

    # ── weekly challenge ────────────────────────────────────────────────────────

    @gl.public.view
    def get_challenge_level(self, week: int) -> int:
        return (week % 10) + 1

    @gl.public.write
    def submit_score(self, player: str, week: int, moves: int, time_sec: int) -> None:
        key = f"{week}:{player}"
        if key in self.scores:
            raise Exception("Already submitted this week")
        level = (week % 10) + 1
        self._validate(level, moves, time_sec)
        grade = self._grade(moves, time_sec)
        xp_map = {"S": 950, "A": 750, "B": 450, "C": 150}
        verdicts = {"S": "Incredible efficiency!", "A": "Smart and precise!", "B": "Good effort!", "C": "Keep practicing!"}
        self.scores[key] = f"{moves},{time_sec},{xp_map[grade]},{grade},{verdicts[grade]}"

    @gl.public.view
    def has_played_this_week(self, player: str, week: int) -> bool:
        return f"{week}:{player}" in self.scores

    @gl.public.view
    def get_weekly_leaderboard(self, week: int) -> list:
        prefix = f"{week}:"
        entries = []
        for k, v in self.scores.items():
            if k.startswith(prefix):
                addr = k[len(prefix):]
                parts = v.split(",")
                short = addr[:6] + "..." + addr[-4:] if len(addr) > 10 else addr
                entries.append({
                    "player": short,
                    "moves": int(parts[0]) if parts else 0,
                    "time": int(parts[1]) if len(parts) > 1 else 0,
                    "xp": int(parts[2]) if len(parts) > 2 else 0,
                    "grade": parts[3] if len(parts) > 3 else "C",
                })
        entries.sort(key=lambda x: -x["xp"])
        return entries[:10]

    @gl.public.view
    def get_player_score(self, player: str, week: int) -> dict:
        key = f"{week}:{player}"
        if key not in self.scores:
            return {"played": False}
        parts = self.scores[key].split(",")
        return {
            "played": True,
            "moves": int(parts[0]) if parts else 0,
            "time": int(parts[1]) if len(parts) > 1 else 0,
            "xp": int(parts[2]) if len(parts) > 2 else 0,
            "grade": parts[3] if len(parts) > 3 else "C",
            "verdict": ",".join(parts[4:]) if len(parts) > 4 else "Level completed!",
        }

    # ── rooms ───────────────────────────────────────────────────────────────────

    @gl.public.write
    def submit_room_score(self, room_id: str, player: str, week: int, moves: int, time_sec: int) -> None:
        if room_id not in self.rooms:
            level = (week % 10) + 1
            self.rooms[room_id] = f"{player},{level},{week}"
        key = f"{room_id}:{player}"
        if key in self.room_scores:
            raise Exception("Already submitted for this room")
        parts = self.rooms[room_id].split(",")
        level = int(parts[1]) if len(parts) > 1 else 1
        self._validate(level, moves, time_sec)
        grade = self._grade(moves, time_sec)
        xp_map = {"S": 950, "A": 750, "B": 450, "C": 150}
        verdicts = {"S": "Incredible efficiency!", "A": "Smart and precise!", "B": "Good effort!", "C": "Keep practicing!"}
        self.room_scores[key] = f"{moves},{time_sec},{xp_map[grade]},{grade},{verdicts[grade]}"

    @gl.public.view
    def get_room_leaderboard(self, room_id: str) -> list:
        prefix = f"{room_id}:"
        entries = []
        for k, v in self.room_scores.items():
            if k.startswith(prefix):
                addr = k[len(prefix):]
                parts = v.split(",")
                short = addr[:6] + "..." + addr[-4:] if len(addr) > 10 else addr
                entries.append({
                    "player": short,
                    "moves": int(parts[0]) if parts else 0,
                    "time": int(parts[1]) if len(parts) > 1 else 0,
                    "xp": int(parts[2]) if len(parts) > 2 else 0,
                    "grade": parts[3] if len(parts) > 3 else "C",
                })
        entries.sort(key=lambda x: -x["xp"])
        return entries[:20]

    @gl.public.view
    def has_played_in_room(self, room_id: str, player: str) -> bool:
        return f"{room_id}:{player}" in self.room_scores

    @gl.public.view
    def get_room_info(self, room_id: str) -> dict:
        if room_id not in self.rooms:
            return {"exists": False}
        parts = self.rooms[room_id].split(",")
        return {
            "exists": True,
            "host": parts[0] if parts else "",
            "level": int(parts[1]) if len(parts) > 1 else 1,
            "week": int(parts[2]) if len(parts) > 2 else 0,
        }
