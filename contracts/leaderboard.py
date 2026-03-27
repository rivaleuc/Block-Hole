# GenLayer Intelligent Contract — Block and Hole Weekly Challenge
# Deploy on GenLayer Studio or testnet-asimov:
#   genlayer deploy contracts/leaderboard.py
#
# Optimistic Democracy is used to validate player scores (anti-cheat).
# Five AI validators reach consensus on whether each score is plausible.

from genlayer import *
import re


class WeeklyBlockChallenge(IContract):
    scores: TreeMap[str, u256]   # "week:player" -> move_count
    times: TreeMap[str, u256]    # "week:player" -> time_seconds

    def __init__(self) -> None:
        self.scores = TreeMap()
        self.times = TreeMap()

    @view
    def get_current_week(self) -> int:
        """Fetch current week number (weeks since 2024-01-01) via GenLayer web access."""
        result = get_webpage("https://worldtimeapi.org/api/timezone/UTC", mode="text")
        match = re.search(r'"unixtime":\s*(\d+)', result)
        if match:
            unix = int(match.group(1))
            epoch = 1704067200  # 2024-01-01 00:00:00 UTC
            return max(0, (unix - epoch) // 604800)
        return 0

    @view
    def get_challenge_level(self, week: int) -> int:
        """Deterministic level selection for a given week (cycles 1–10)."""
        return (week % 10) + 1

    @write
    def submit_score(self, player: str, week: int, moves: int, time_sec: int) -> None:
        """Submit weekly challenge score.

        Rules:
        - One submission per wallet per week
        - Score validated by Optimistic Democracy (5 AI validators reach consensus)
        - Lower move count = better rank; time is tiebreaker
        """
        key = f"{week}:{player}"

        if key in self.scores:
            raise Exception("Already submitted score this week")

        level = self.get_challenge_level(week)

        # Optimistic Democracy: AI validators decide if score is a plausible human play
        is_valid = eq_principle(
            f"A player claims to have completed level {level} of Block and Hole "
            f"(a 3D rolling block puzzle game) in {moves} moves and {time_sec} seconds. "
            f"Block and Hole is a puzzle where you roll a rectangular block to reach a goal tile. "
            f"Is this a plausible human score? "
            f"Rules for rejection: fewer than 3 moves is physically impossible; "
            f"under 5 seconds is too fast for any human; "
            f"over 10000 moves or over 7200 seconds (2 hours) suggests a bot or exploit. "
            f"Otherwise accept it. Answer yes if it seems legitimate, no if it should be rejected.",
            comparative=False
        )

        if not is_valid:
            raise Exception("Score rejected by consensus: suspected invalid or cheated input")

        self.scores[key] = u256(moves)
        self.times[key] = u256(time_sec)

    @view
    def has_played_this_week(self, player: str, week: int) -> bool:
        """Check if a player already submitted a score for the given week."""
        return f"{week}:{player}" in self.scores

    @view
    def get_weekly_leaderboard(self, week: int) -> list:
        """Return top 10 players for the week, sorted by fewest moves then fastest time."""
        prefix = f"{week}:"
        entries = []
        for k, v in self.scores.items():
            if k.startswith(prefix):
                player = k[len(prefix):]
                moves = int(v)
                time_val = int(self.times.get(k, u256(0)))
                short = player[:6] + "..." + player[-4:] if len(player) > 10 else player
                entries.append({"player": short, "moves": moves, "time": time_val})
        entries.sort(key=lambda x: (x["moves"], x["time"]))
        return entries[:10]

    @view
    def get_player_score(self, player: str, week: int) -> dict:
        """Get a player's score for a given week."""
        key = f"{week}:{player}"
        if key not in self.scores:
            return {"played": False}
        return {
            "played": True,
            "moves": int(self.scores[key]),
            "time": int(self.times.get(key, u256(0)))
        }
