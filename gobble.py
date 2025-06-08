import random
import json
import time
import math
from typing import Set, Tuple, List, Optional, Dict
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum

class LearningLevel(Enum):
    """Learning stages based on Vygotsky's ZPD"""
    DISCOVERY = 1
    GUIDED = 2
    STRATEGIC = 3
    ANALYTICAL = 4
    MASTER = 5

@dataclass
class PlayerProfile:
    """Track player progress for adaptive learning"""
    level: LearningLevel = LearningLevel.DISCOVERY
    games_played: int = 0
    wins: int = 0
    concepts_learned: Set[str] = None

    def __post_init__(self):
        if self.concepts_learned is None:
            self.concepts_learned = set()

class GameConfig:
    """Configuration for the Gobbles game."""
    BOARD_SIZE = 5
    SYMBOLS = {'empty': '+', 'black': '●', 'white': '○'}
    LEARNING_MODE = True
    SHOW_INFLUENCE = False
    MCTS_SIMULATIONS = {
        LearningLevel.DISCOVERY: 100,
        LearningLevel.GUIDED: 300,
        LearningLevel.STRATEGIC: 500,
        LearningLevel.ANALYTICAL: 1000,
        LearningLevel.MASTER: 2000
    }
    MCTS_EXPLORATION = 1.414

neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class Concept:
    CONNECTION = "connection"
    CAPTURE = "capture"
    LIBERTY = "liberty"
    TERRITORY = "territory"
    INFLUENCE = "influence"
    READING_AHEAD = "reading_ahead"
    SACRIFICE = "sacrifice"
    LIFE_AND_DEATH = "life_and_death"

class MCTSNode:
    """Node in the Monte Carlo Tree Search."""
    def __init__(self, game_state: 'Game', parent: Optional['MCTSNode'] = None,
                 move: Optional[Tuple[int, int, str]] = None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.children: List['MCTSNode'] = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = self._get_possible_moves()

    def _get_possible_moves(self) -> List[Tuple[int, int, str]]:
        moves = []
        color = GameConfig.SYMBOLS['white'] if self._get_current_player() == 'W' else GameConfig.SYMBOLS['black']
        for r in range(GameConfig.BOARD_SIZE):
            for c in range(GameConfig.BOARD_SIZE):
                if self.game_state.board[r][c] == GameConfig.SYMBOLS['empty']:
                    test_game = deepcopy(self.game_state)
                    valid, _ = test_game.apply_move(r, c, color)
                    if valid:
                        moves.append((r, c, color))
        moves.append((-1, -1, color))
        return moves

    def _get_current_player(self) -> str:
        if not self.game_state.move_history:
            return 'B'
        last_color = self.game_state.move_history[-1]['move'][2]
        return 'W' if last_color == GameConfig.SYMBOLS['black'] else 'B'

    def select_child(self) -> 'MCTSNode':
        c = GameConfig.MCTS_EXPLORATION
        def ucb1(child):
            if child.visits == 0:
                return float('inf')
            exploitation = child.wins / child.visits
            exploration = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploitation + exploration
        return max(self.children, key=ucb1)

    def expand(self) -> 'MCTSNode':
        move = self.untried_moves.pop(random.randrange(len(self.untried_moves)))
        new_game = deepcopy(self.game_state)
        if move[0] == -1:
            new_game.pass_turn()
        else:
            new_game.apply_move(move[0], move[1], move[2])
        child = MCTSNode(new_game, self, move)
        self.children.append(child)
        return child

    def simulate(self) -> float:
        sim_game = deepcopy(self.game_state)
        current_player = self._get_current_player()
        consecutive_passes = 0
        moves_played = 0
        max_moves = GameConfig.BOARD_SIZE * GameConfig.BOARD_SIZE * 2
        while consecutive_passes < 2 and moves_played < max_moves:
            color = GameConfig.SYMBOLS['white'] if current_player == 'W' else GameConfig.SYMBOLS['black']
            valid_moves = []
            for r in range(GameConfig.BOARD_SIZE):
                for c in range(GameConfig.BOARD_SIZE):
                    if sim_game.board[r][c] == GameConfig.SYMBOLS['empty']:
                        test_game = deepcopy(sim_game)
                        valid, _ = test_game.apply_move(r, c, color)
                        if valid:
                            valid_moves.append((r, c))
            if valid_moves and random.random() > 0.1:
                r, c = random.choice(valid_moves)
                sim_game.apply_move(r, c, color)
                consecutive_passes = 0
            else:
                consecutive_passes += 1
            current_player = 'W' if current_player == 'B' else 'B'
            moves_played += 1
        return sim_game.evaluate_winner(GameConfig.SYMBOLS['white'])

    def backpropagate(self, result: float):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(1.0 - result)

    def best_move(self) -> Tuple[int, int]:
        if not self.children:
            return -1, -1
        best_child = max(self.children, key=lambda c: c.visits)
        return best_child.move[0], best_child.move[1]

    def get_move_analysis(self) -> List[Dict]:
        if not self.children:
            return []
        analysis = []
        sorted_children = sorted(self.children, key=lambda c: c.visits, reverse=True)[:5]
        for child in sorted_children:
            if child.visits > 0:
                win_rate = child.wins / child.visits
                move_r, move_c = child.move[0], child.move[1]
                move_info = {
                    'position': (move_r, move_c),
                    'visits': child.visits,
                    'win_rate': win_rate,
                    'reasoning': self._analyze_move_reason(child)
                }
                analysis.append(move_info)
        return analysis

    def _analyze_move_reason(self, child: 'MCTSNode') -> str:
        win_rate = child.wins / child.visits if child.visits > 0 else 0
        move_r, move_c = child.move[0], child.move[1]
        if move_r == -1:
            return "Passing - no urgent moves needed"
        game = child.game_state
        reasons = []
        if any('captured' in m for m in game.move_history[-1:]):
            reasons.append("captures enemy bubbles")
        color = child.move[2]
        connected = 0
        for dr, dc in neighbors:
            nr, nc = move_r + dr, move_c + dc
            if 0 <= nr < GameConfig.BOARD_SIZE and 0 <= nc < GameConfig.BOARD_SIZE:
                if game.board[nr][nc] == color:
                    connected += 1
        if connected >= 2:
            reasons.append("connects friendly bubbles")
        elif connected == 1:
            reasons.append("extends a group")
        empty_neighbors = sum(1 for dr, dc in neighbors
                              for nr, nc in [(move_r + dr, move_c + dc)]
                              if 0 <= nr < GameConfig.BOARD_SIZE and 0 <= nc < GameConfig.BOARD_SIZE
                              and game.board[nr][nc] == GameConfig.SYMBOLS['empty'])
        if empty_neighbors >= 3:
            reasons.append("claims open territory")
        if win_rate > 0.6:
            reasons.append("statistically strong")
        elif win_rate < 0.4:
            reasons.append("risky move")
        return " + ".join(reasons) if reasons else "solid position"

class Game:
    """Main game class with educational features."""
    def __init__(self, player_profile: PlayerProfile = None):
        self.board = [[GameConfig.SYMBOLS['empty'] for _ in range(GameConfig.BOARD_SIZE)]
                      for _ in range(GameConfig.BOARD_SIZE)]
        self.move_history: List[Dict] = []
        self.ko_point: Optional[Tuple[int, int]] = None
        self.passes = 0
        self.player = player_profile or PlayerProfile()
        self.last_ai_analysis = None

    def display(self, show_coordinates: bool = True):
        if show_coordinates:
            print("\n  " + " ".join(str(i+1) for i in range(GameConfig.BOARD_SIZE)))
        for i, row in enumerate(self.board):
            if show_coordinates:
                print(str(i+1) + " ", end="")
            for j, cell in enumerate(row):
                if GameConfig.SHOW_INFLUENCE and cell == GameConfig.SYMBOLS['empty']:
                    influence = self._calculate_influence(i, j)
                    if influence > 0.3:
                        print("◦", end=" ")
                    elif influence < -0.3:
                        print("•", end=" ")
                    else:
                        print(cell, end=" ")
                else:
                    print(cell, end=" ")
            print()
        print()

    def _calculate_influence(self, r: int, c: int) -> float:
        if self.board[r][c] != GameConfig.SYMBOLS['empty']:
            return 0.0
        influence = 0.0
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                nr, nc = r + dr, c + dc
                if 0 <= nr < GameConfig.BOARD_SIZE and 0 <= nc < GameConfig.BOARD_SIZE:
                    distance = max(abs(dr), abs(dc))
                    if self.board[nr][nc] == GameConfig.SYMBOLS['white']:
                        influence += 1.0 / (distance + 1)
                    elif self.board[nr][nc] == GameConfig.SYMBOLS['black']:
                        influence -= 1.0 / (distance + 1)
        return influence

    def get_group(self, r: int, c: int) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        color = self.board[r][c]
        if color == GameConfig.SYMBOLS['empty']:
            return set(), set()
        visited = set()
        liberties = set()
        stack = [(r, c)]
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GameConfig.BOARD_SIZE and 0 <= ny < GameConfig.BOARD_SIZE:
                    if self.board[nx][ny] == GameConfig.SYMBOLS['empty']:
                        liberties.add((nx, ny))
                    elif self.board[nx][ny] == color:
                        stack.append((nx, ny))
        return visited, liberties

    def apply_move(self, r: int, c: int, color: str) -> Tuple[bool, str]:
        if not (0 <= r < GameConfig.BOARD_SIZE and 0 <= c < GameConfig.BOARD_SIZE):
            return False, "Move out of bounds."
        if self.board[r][c] != GameConfig.SYMBOLS['empty']:
            return False, "Spot not empty."
        if GameConfig.LEARNING_MODE and self.ko_point == (r, c):
            return False, "Ko rule: Cannot immediately recapture."
        board_backup = [row[:] for row in self.board]
        opponent = GameConfig.SYMBOLS['white'] if color == GameConfig.SYMBOLS['black'] else GameConfig.SYMBOLS['black']
        self.board[r][c] = color
        captured = []
        for dx, dy in neighbors:
            nx, ny = r + dx, c + dy
            if 0 <= nx < GameConfig.BOARD_SIZE and 0 <= ny < GameConfig.BOARD_SIZE and self.board[nx][ny] == opponent:
                group, libs = self.get_group(nx, ny)
                if not libs:
                    captured.extend(group)
        for x, y in captured:
            self.board[x][y] = GameConfig.SYMBOLS['empty']
        group, libs = self.get_group(r, c)
        if not libs:
            self.board = board_backup
            return False, "Move is suicidal."
        if len(captured) == 1 and len(group) == 1:
            self.ko_point = captured[0]
        else:
            self.ko_point = None
        self.move_history.append({'board': board_backup, 'move': (r, c, color), 'captured': captured, 'ko_point': self.ko_point})
        self.passes = 0
        feedback = self._generate_educational_feedback(r, c, captured, color)
        return True, feedback

    def _generate_educational_feedback(self, r: int, c: int, captured: List[Tuple[int, int]], color: str) -> str:
        level = self.player.level
        if captured:
            self.player.concepts_learned.add(Concept.CAPTURE)
            base = f"captured {len(captured)} bubble(s)"
            if level == LearningLevel.DISCOVERY:
                return f"Pop! You {base}! 🎯"
            elif level == LearningLevel.GUIDED:
                return f"Great capture! You {base} by taking away all their breathing spaces."
            else:
                return f"Captured {len(captured)} stone{'s' if len(captured) > 1 else ''}. Territory gained: ~{len(captured)} points."
        connected_groups = 0
        for dx, dy in neighbors:
            nx, ny = r + dx, c + dy
            if 0 <= nx < GameConfig.BOARD_SIZE and 0 <= ny < GameConfig.BOARD_SIZE:
                if self.board[nx][ny] == color:
                    connected_groups += 1
        if connected_groups >= 2:
            self.player.concepts_learned.add(Concept.CONNECTION)
            if level == LearningLevel.DISCOVERY:
                return "Nice! Your bubbles joined together to form a stronger group! 🤝"
            elif level == LearningLevel.GUIDED:
                return "Good connection! Larger groups are harder to capture - they share breathing spaces."
            else:
                return "Strong connection. Group efficiency increased."
        if connected_groups == 1:
            if level == LearningLevel.DISCOVERY:
                return "Your bubble found a friend! They're stronger together. 👯"
            else:
                return "Extending group - maintaining connectivity."
        empty_neighbors = sum(1 for dx, dy in neighbors
                              if 0 <= r + dx < GameConfig.BOARD_SIZE and 0 <= c + dy < GameConfig.BOARD_SIZE
                              and self.board[r + dx][c + dy] == GameConfig.SYMBOLS['empty'])
        if empty_neighbors >= 3:
            self.player.concepts_learned.add(Concept.TERRITORY)
            if level == LearningLevel.DISCOVERY:
                return "Good move! Your bubble claims some open space. 🏞️"
            elif level == LearningLevel.GUIDED:
                return "Nice territory move! You're influencing empty areas around your bubble."
            else:
                return f"Claiming territory. Influence radius: {empty_neighbors} points."
        if level == LearningLevel.DISCOVERY:
            return "Bubble placed! Watch out for your breathing spaces. 🫧"
        else:
            return "Solid move."

    def pass_turn(self) -> bool:
        self.passes += 1
        self.ko_point = None
        if self.player.level.value <= LearningLevel.GUIDED.value and self.passes == 1:
            print("💡 Tip: When both players pass, the game ends and we count territory!")
        return self.passes >= 2

    def ai_move(self) -> bool:
        level = self.player.level
        simulations = GameConfig.MCTS_SIMULATIONS[level]
        print(f"\n🤖 AI is thinking", end="")
        if level >= LearningLevel.GUIDED:
            print(f" (using {simulations} simulations like AlphaGo)", end="")
        print("...", end="", flush=True)
        root = MCTSNode(deepcopy(self))
        start_time = time.time()
        for i in range(simulations):
            node = root
            while node.untried_moves == [] and node.children != []:
                node = node.select_child()
            if node.untried_moves:
                node = node.expand()
            result = node.simulate()
            node.backpropagate(result)
            if (i + 1) % max(1, simulations // 10) == 0:
                print(".", end="", flush=True)
        elapsed = time.time() - start_time
        print(f" Done! ({round(elapsed,1)}s)\n")
        self.last_ai_analysis = root.get_move_analysis()
        best_r, best_c = root.best_move()
        if best_r == -1:
            print("AI passes.")
            self.pass_turn()
            return False
        color = GameConfig.SYMBOLS['white']
        self.apply_move(best_r, best_c, color)
        self._explain_ai_move(best_r, best_c, level)
        return True

    def _explain_ai_move(self, r: int, c: int, level: LearningLevel):
        print(f"AI placed a bubble at ({r+1}, {c+1})")
        if level == LearningLevel.DISCOVERY:
            if self.last_ai_analysis and self.last_ai_analysis[0]['win_rate'] > 0.6:
                print("💭 AI: 'This looks like a good spot!'")
        elif level == LearningLevel.GUIDED:
            if self.last_ai_analysis:
                best = self.last_ai_analysis[0]
                print(f"💭 AI: 'I chose this because it {best['reasoning']}'")
                print(f"    (I tested this move {best['visits']} times!)")
        elif level == LearningLevel.STRATEGIC:
            print("\n📊 AI considered these moves:")
            for i, move in enumerate(self.last_ai_analysis[:3]):
                if move['position'][0] >= 0:
                    print(f"   {i+1}. ({move['position'][0]+1},{move['position'][1]+1}): "
                          f"{move['win_rate']:.1%} win rate - {move['reasoning']}")
            if Concept.READING_AHEAD not in self.player.concepts_learned:
                print("\n💡 Learning moment: Like AlphaGo, I'm not just looking at this move -")
                print("   I'm imagining many possible future games from each position!")
                self.player.concepts_learned.add(Concept.READING_AHEAD)
        elif level >= LearningLevel.ANALYTICAL:
            print("\n📈 Detailed AI Analysis:")
            for move in self.last_ai_analysis[:5]:
                if move['position'][0] >= 0:
                    pos_str = f"({move['position'][0]+1},{move['position'][1]+1})"
                else:
                    pos_str = "Pass"
                print(f"   {pos_str}: {move['visits']:4d} visits, "
                      f"{move['win_rate']:5.1%} win rate - {move['reasoning']}")
            if "UCB" not in self.player.concepts_learned:
                print("\n🎓 Advanced concept: I balance exploring new moves with exploiting good ones")
                print("   using the UCB1 formula: win_rate + C×√(ln(parent_visits)/visits)")
                self.player.concepts_learned.add("UCB")

    def evaluate_winner(self, perspective_color: str) -> float:
        black_territory = 0
        white_territory = 0
        for r in range(GameConfig.BOARD_SIZE):
            for c in range(GameConfig.BOARD_SIZE):
                if self.board[r][c] == GameConfig.SYMBOLS['black']:
                    black_territory += 1
                elif self.board[r][c] == GameConfig.SYMBOLS['white']:
                    white_territory += 1
                else:
                    influence = self._calculate_influence(r, c)
                    if influence < -0.5:
                        black_territory += 0.7
                    elif influence > 0.5:
                        white_territory += 0.7
        total = black_territory + white_territory
        if total == 0:
            return 0.5
        if perspective_color == GameConfig.SYMBOLS['white']:
            return white_territory / total
        else:
            return black_territory / total

    def evaluate_position(self, color: str) -> float:
        score = 0.0
        for r in range(GameConfig.BOARD_SIZE):
            for c in range(GameConfig.BOARD_SIZE):
                if self.board[r][c] == color:
                    _, libs = self.get_group(r, c)
                    score += 1 + len(libs) * 0.1
        return score

    def undo_last_move(self) -> bool:
        if not self.move_history:
            return False
        last = self.move_history.pop()
        self.board = [row[:] for row in last['board']]
        self.ko_point = last['ko_point']
        return True

    def check_learning_progress(self):
        games_at_level = self.player.games_played % 5
        win_rate = self.player.wins / max(1, self.player.games_played)
        should_advance = False
        if self.player.level == LearningLevel.DISCOVERY:
            required = {Concept.CONNECTION, Concept.CAPTURE, Concept.LIBERTY}
            if required.issubset(self.player.concepts_learned) and games_at_level >= 3:
                should_advance = True
        elif self.player.level == LearningLevel.GUIDED:
            if Concept.TERRITORY in self.player.concepts_learned and games_at_level >= 3:
                should_advance = True
        elif self.player.level == LearningLevel.STRATEGIC:
            if Concept.READING_AHEAD in self.player.concepts_learned and win_rate > 0.3:
                should_advance = True
        elif self.player.level == LearningLevel.ANALYTICAL:
            if win_rate > 0.4 and games_at_level >= 5:
                should_advance = True
        if should_advance and self.player.level.value < LearningLevel.MASTER.value:
            self.player.level = LearningLevel(self.player.level.value + 1)
            print(f"\n🎉 Congratulations! You've advanced to {self.player.level.name} level!")
            print(f"   New concepts will be introduced as you play.\n")
            if self.player.level >= LearningLevel.STRATEGIC:
                GameConfig.SHOW_INFLUENCE = True
                print("   💡 Influence indicators now visible on empty spaces!\n")

    def save_progress(self, filename: str = "gobble_progress.json"):
        data = {
            'board': self.board,
            'move_history': self.move_history,
            'player': {
                'level': self.player.level.value,
                'games_played': self.player.games_played,
                'wins': self.player.wins,
                'concepts_learned': list(self.player.concepts_learned)
            }
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Progress saved to {filename}")

    def load_progress(self, filename: str = "gobble_progress.json") -> bool:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.board = data['board']
            self.move_history = data['move_history']
            self.player.level = LearningLevel(data['player']['level'])
            self.player.games_played = data['player']['games_played']
            self.player.wins = data['player']['wins']
            self.player.concepts_learned = set(data['player']['concepts_learned'])
            print(f"Progress loaded! You're at {self.player.level.name} level.")
            return True
        except Exception:
            return False

    def main_loop(self):
        print("🫧 Welcome to Gobbles - Learn to Think Like AlphaGo! 🫧")
        print("=" * 50)
        if not self.load_progress():
            print("\n🌟 Starting your journey to Go mastery!")
            print("   I'll teach you to think like AlphaGo, step by step.")
            print("   Let's begin with the basics...\n")
            print("📚 Level 1: DISCOVERY")
            print("   - Place bubbles (stones) on the board")
            print("   - Bubbles need breathing space (liberties) to survive")
            print("   - Capture enemy bubbles by removing all their air")
            print("   - Connect your bubbles to make them stronger\n")
        print("Commands: 'row col' to play, 'p' to pass, 'h' for help, 'q' to quit\n")
        while True:
            self.display(show_coordinates=True)
            print(f"Level: {self.player.level.name} | "
                  f"Games: {self.player.games_played} | "
                  f"Concepts learned: {len(self.player.concepts_learned)}")
            move = input("\nYour move: ").strip().lower()
            if move == 'q':
                self.save_progress()
                print("\n👋 Thanks for learning with Gobbles! See you next time!")
                break
            elif move == 'h':
                print("\n📖 Help:")
                print("  'row col' - Place a bubble (e.g., '3 3' for center)")
                print("  'p' - Pass your turn")
                print("  'i' - Toggle influence display")
                print("  'c' - Show concepts learned")
                print("  's' - Save progress")
                print("  'q' - Quit and save\n")
                continue
            elif move == 'p':
                if self.pass_turn():
                    print("\n🏁 Game Over! Both players passed.")
                    winner = "You" if self.evaluate_winner(GameConfig.SYMBOLS['black']) > 0.5 else "AI"
                    print(f"   {winner} controlled more territory!")
                    if winner == "You":
                        self.player.wins += 1
                    self.player.games_played += 1
                    self.check_learning_progress()
                    self.__init__(self.player)
                    continue
                else:
                    print("You passed your turn.")
            elif move == 'i':
                GameConfig.SHOW_INFLUENCE = not GameConfig.SHOW_INFLUENCE
                print(f"Influence display: {'ON' if GameConfig.SHOW_INFLUENCE else 'OFF'}")
                continue
            elif move == 'c':
                print(f"\n🎓 Concepts learned: {', '.join(sorted(self.player.concepts_learned))}")
                continue
            elif move == 's':
                self.save_progress()
                continue
            else:
                try:
                    parts = move.split()
                    r, c = map(int, parts)
                    r -= 1
                    c -= 1
                except Exception:
                    print("❌ Invalid input. Use 'row col' format (e.g., '3 3')")
                    continue
                valid, msg = self.apply_move(r, c, GameConfig.SYMBOLS['black'])
                if not valid:
                    print(f"❌ {msg}")
                    continue
                print(f"✅ {msg}")
                if self.passes >= 2:
                    print("\n🏁 Game Over!")
                    continue
                self.ai_move()
                if self.player.level >= LearningLevel.GUIDED and random.random() < 0.3:
                    if Concept.LIBERTY not in self.player.concepts_learned:
                        print("\n💡 Tip: Count the empty spaces next to your groups - those are liberties!")
                        print("   Groups with more liberties are safer from capture.")
                        self.player.concepts_learned.add(Concept.LIBERTY)
                    elif Concept.INFLUENCE not in self.player.concepts_learned and self.player.level >= LearningLevel.STRATEGIC:
                        print("\n💡 Tip: Empty spaces near your stones are under your 'influence'.")
                        print("   Controlling influence means controlling future territory!")
                        self.player.concepts_learned.add(Concept.INFLUENCE)

if __name__ == "__main__":
    Game().main_loop()
