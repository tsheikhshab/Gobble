"""
Demo script showing Gobble's educational features.
Run this to see how the game teaches AlphaGo concepts progressively.
"""

from gobble import Game, GameConfig, LearningLevel, PlayerProfile, Concept


def demonstrate_learning_progression():
    """Show how the game adapts to different learning levels."""
    print("🎓 GOBBLE EDUCATIONAL DEMO")
    print("=" * 50)
    print("This demo shows how Gobble teaches AlphaGo concepts at each level.\n")
    for level in LearningLevel:
        print(f"\n{'='*50}")
        print(f"📚 {level.name} LEVEL (Level {level.value})")
        print(f"{'='*50}\n")
        player = PlayerProfile(level=level)
        game = Game(player)
        GameConfig.SHOW_INFLUENCE = (level.value >= 3)
        print("Making a few moves to demonstrate feedback style...\n")
        valid, feedback = game.apply_move(2, 2, GameConfig.SYMBOLS['black'])
        print(f"You play (3,3): {feedback}")
        print("\nAI thinking process:")
        simulations = GameConfig.MCTS_SIMULATIONS[level]
        print(f"  Using {simulations} simulations")
        if level == LearningLevel.DISCOVERY:
            print("  AI: 'Looking for a good spot...'")
        elif level == LearningLevel.GUIDED:
            print("  AI: 'I should place near your bubble to limit your growth'")
        elif level == LearningLevel.STRATEGIC:
            print("  AI: Analyzing top 3 moves:")
            print("     1. (2,3): 62% win rate - extends territory")
            print("     2. (3,2): 58% win rate - blocks expansion")
            print("     3. (4,4): 51% win rate - claims corner")
        elif level == LearningLevel.ANALYTICAL:
            print("  Detailed MCTS Analysis:")
            print("     Position | Visits | Win% | UCB Score | Reasoning")
            print("     (2,3)   |   234  | 62%  |   1.84    | extends territory + pressure")
            print("     (3,2)   |   198  | 58%  |   1.79    | blocks expansion")
            print("     (4,4)   |   156  | 51%  |   1.71    | claims corner territory")
        else:
            print("  [Minimal feedback - you should know why these moves matter]")
        if GameConfig.SHOW_INFLUENCE:
            print("\n  Influence indicators: ◦ = white influence, • = black influence")
        print("\nConcepts taught at this level: ", end="")
        if level == LearningLevel.DISCOVERY:
            print("connections, captures, basic liberties")
        elif level == LearningLevel.GUIDED:
            print("territory, group strength, breathing spaces")
        elif level == LearningLevel.STRATEGIC:
            print("influence, reading ahead, position evaluation")
        elif level == LearningLevel.ANALYTICAL:
            print("UCB formula, statistical analysis, tree search")
        else:
            print("full strategic mastery")


def demonstrate_concept_teaching():
    """Show how specific concepts are introduced."""
    print("\n\n🎯 CONCEPT TEACHING DEMO")
    print("=" * 50)
    print("Gobble introduces concepts gradually through gameplay:\n")
    concepts = [
        (Concept.CONNECTION, "When bubbles connect, they share breathing spaces"),
        (Concept.CAPTURE, "Remove all breathing spaces to capture enemy bubbles"),
        (Concept.LIBERTY, "Empty spaces next to groups that let them 'breathe'"),
        (Concept.TERRITORY, "Empty areas you control for points"),
        (Concept.INFLUENCE, "How stones project power over empty areas"),
        (Concept.READING_AHEAD, "Imagining future positions like AlphaGo"),
        (Concept.SACRIFICE, "Giving up stones for strategic advantage"),
        (Concept.LIFE_AND_DEATH, "Determining which groups can survive")
    ]
    for i, (concept, description) in enumerate(concepts, 1):
        print(f"{i}. {concept.upper()}")
        print(f"   📖 {description}")
        print(f"   🎓 Typically learned in: Level {min(i//2 + 1, 5)}\n")


def demonstrate_alphago_thinking():
    """Show how MCTS works in simple terms."""
    print("\n🧠 HOW ALPHAGO THINKS (SIMPLIFIED)")
    print("=" * 50)
    print("Monte Carlo Tree Search in action:\n")
    print("1️⃣  CURRENT POSITION")
    print("    · · · · ·")
    print("    · · ○ · ·")
    print("    · · ● · ·")
    print("    · · · · ·")
    print("    · · · · ·\n")
    print("2️⃣  CONSIDER POSSIBLE MOVES")
    print("    The AI identifies all legal moves (marked with ?):")
    print("    ? ? ? ? ?")
    print("    ? ? ○ ? ?")
    print("    ? ? ● ? ?")
    print("    ? ? ? ? ?")
    print("    ? ? ? ? ?\n")
    print("3️⃣  SIMULATE MANY GAMES")
    print("    For each '?' position, play out random games:")
    print("    - Position (2,4): Played 156 times → Won 98 (63%)")
    print("    - Position (4,3): Played 143 times → Won 79 (55%)")
    print("    - Position (3,2): Played 137 times → Won 71 (52%)")
    print("    ...\n")
    print("4️⃣  CHOOSE STATISTICALLY BEST MOVE")
    print("    AI picks (2,4) - highest win rate after many simulations!")
    print("    This is how AlphaGo beat world champions - not by")
    print("    calculating everything, but by smart statistical sampling!\n")


def main():
    """Run all demonstrations."""
    demonstrate_learning_progression()
    demonstrate_concept_teaching()
    demonstrate_alphago_thinking()
    print("\n" + "="*50)
    print("🎮 Ready to start learning? Run 'python gobble.py' to begin!")
    print("="*50)


if __name__ == "__main__":
    main()
