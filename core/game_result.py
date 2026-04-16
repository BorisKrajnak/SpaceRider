from dataclasses import dataclass

@dataclass
class GameResult:
    next_state: str
    score: int = 0
    time: int = 0
    is_best: bool = False
    game_name: str = ""