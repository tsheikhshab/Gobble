# Gobble - Learn to Think Like AlphaGo! 🫧

Gobble is an educational Go game that teaches you to think like AlphaGo through progressive learning stages. Using playful bubble metaphors and Vygotsky's Zone of Proximal Development (ZPD), it adapts to your skill level while always using AlphaGo's core Monte Carlo Tree Search algorithm underneath.

## 🎓 Educational Philosophy

### Vygotsky's Zone of Proximal Development
The game adapts to keep you in your optimal learning zone:
- **Too Easy**: You get bored and don't learn
- **Too Hard**: You get frustrated and give up  
- **Just Right (ZPD)**: Challenging but achievable with the right guidance

### Learning to Think Like AlphaGo
At every level, the AI uses the same Monte Carlo Tree Search algorithm that powered AlphaGo to defeat world champions. The difference is in how it's presented:
- **Beginners**: Simple explanations with bubble metaphors
- **Advanced**: Full statistical analysis and strategic concepts

## 🌟 Progressive Learning Levels

### Level 1: DISCOVERY 🔍
- **Focus**: Learn basic rules through play
- **AI**: Uses 100 simulations, gives simple feedback
- **Concepts**: Connections, captures, liberties
- **Language**: "Your bubbles joined together!" 🤝

### Level 2: GUIDED 🗺️
- **Focus**: AI explains its thinking in simple terms
- **AI**: Uses 300 simulations, shares basic reasoning
- **Concepts**: Territory, breathing spaces, groups
- **Language**: "I chose this because it connects friendly bubbles"

### Level 3: STRATEGIC 📊
- **Focus**: Learn to read ahead like AlphaGo
- **AI**: Uses 500 simulations, shows top 3 moves considered
- **Concepts**: Influence, reading ahead, position evaluation
- **New Feature**: Influence indicators on empty spaces

### Level 4: ANALYTICAL 📈
- **Focus**: Understand AlphaGo's decision-making process
- **AI**: Uses 1000 simulations, detailed move analysis
- **Concepts**: UCB formula, win rates, statistical thinking
- **Language**: Full technical explanations available

### Level 5: MASTER 🏆
- **Focus**: Minimal guidance, maximum challenge
- **AI**: Uses 2000 simulations for strongest play
- **You're ready to**: Think strategically like AlphaGo!

## 🎮 How to Play

### Installation
```bash
git clone https://github.com/yourusername/gobble.git
cd gobble
python gobble.py
python gobble_gui.py  # optional graphical version
Running `gobble_gui.py` opens a simple Tkinter window so you can play by clicking on the board instead of using the console.
```

### Basic Commands
- **`row col`** - Place a bubble (e.g., "3 3" for center)
- **`p`** - Pass your turn
- **`h`** - Show help menu
- **`i`** - Toggle influence display
- **`c`** - Show concepts you've learned
- **`s`** - Save your progress
- **`q`** - Quit and save

### Visual Guide
```
  1 2 3 4 5
1 · · · · ·    · = Empty space
2 · · ○ · ·    ○ = White bubble (AI)
3 · · ● · ·    ● = Black bubble (You)
4 · · · · ·    ◦ = White influence
5 · · · · ·    • = Black influence
```

## 🧠 Core Concepts Explained

### Thinking Like AlphaGo
AlphaGo doesn't calculate every possible move. Instead, it:
1. **Explores** promising moves by simulation
2. **Learns** which positions lead to victory
3. **Balances** trying new things vs. exploiting known good moves

### The Bubble Metaphor
- **Bubbles** = Go stones (made friendly and intuitive)
- **Breathing spaces** = Liberties (empty adjacent spaces)
- **Popping** = Capturing (when bubbles lose all air)
- **Joining** = Connecting groups (stronger together!)

### Key Strategic Concepts

1. **Connection**: Bubbles joined together share breathing spaces
2. **Territory**: Empty areas you control
3. **Influence**: How your bubbles affect nearby empty spaces  
4. **Reading Ahead**: Imagining future positions before playing
5. **Statistical Thinking**: Choosing moves based on win probability

## 📊 How the AI Works

### Monte Carlo Tree Search (MCTS)
The same algorithm that powers AlphaGo, scaled for education:

```
For each possible move:
  1. SELECTION: Navigate to promising positions
  2. EXPANSION: Try new moves
  3. SIMULATION: Play random games to see outcomes
  4. BACKPROPAGATION: Learn from results
  
Choose the move with the best statistics!
```

### Adaptive AI Strength
- **Discovery**: 100 simulations (quick, makes mistakes)
- **Guided**: 300 simulations (balanced play)
- **Strategic**: 500 simulations (thoughtful moves)
- **Analytical**: 1000 simulations (strong player)
- **Master**: 2000 simulations (very challenging)

## 🎯 Learning Progression

### What You'll Learn
1. **Basic Rules** → Through discovery and play
2. **Pattern Recognition** → Seeing good shapes
3. **Strategic Thinking** → Planning ahead
4. **Statistical Reasoning** → Probability-based decisions
5. **Positional Judgment** → Evaluating whole board

### Advancement Criteria
The game tracks your progress and advances you when ready:
- Concepts learned and applied
- Games played at current level
- Win rate and improvement
- Understanding demonstrated

## 💡 Tips for Learning

1. **Don't rush levels** - Master each concept before advancing
2. **Watch the AI's explanations** - They reveal AlphaGo's thinking
3. **Experiment freely** - The AI will explain why moves work or don't
4. **Use influence display** - See how stones project power
5. **Review AI's top moves** - Understand why it chose what it did

## 🔬 Technical Details

### Requirements
- Python 3.6+
- No external dependencies
- Works on all platforms

### Architecture
- **Game Engine**: Handles rules and state
- **MCTS AI**: Full implementation of Monte Carlo Tree Search
- **Educational Layer**: Adaptive feedback and progression
- **Visual System**: Clear display with influence indicators

### Performance
- Fast simulations on 5×5 board
- Real-time feedback
- Efficient tree search
- Minimal memory usage

## 🌈 Why Gobble?

Traditional Go tutorials can be overwhelming. Gobble makes learning natural by:
- **Starting simple**: Bubbles are friendlier than stones
- **Building gradually**: Each level adds complexity
- **Explaining clearly**: AI shares its thought process
- **Adapting dynamically**: Stays in your learning zone
- **Using proven methods**: Real AlphaGo algorithm throughout

## 🚀 Future Enhancements

- [ ] Larger boards (7×7, 9×9) for advanced players
- [ ] Puzzle mode with specific scenarios
- [ ] Multiplayer with skill matching
- [ ] Visual tutorials and animations
- [ ] Deep learning position evaluation
- [ ] Tournament mode with rankings

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional teaching moments
- Better metaphors for complex concepts
- Performance optimizations
- Visual enhancements
- More detailed progress tracking

## 📜 License

MIT License - Free for educational use

## 🙏 Acknowledgments

- DeepMind's AlphaGo team for revolutionizing Go AI
- Lev Vygotsky for ZPD learning theory
- The Go community for preserving this beautiful game
- Everyone learning to think strategically through games

---

*"In the beginner's mind there are many possibilities, but in the expert's mind there are few."* - Shunryu Suzuki

Start your journey from Discovery to Mastery. Learn to think like AlphaGo, one bubble at a time! 🫧
