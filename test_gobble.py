import unittest
from gobble import Game, GameConfig, MCTSNode

class TestGobble(unittest.TestCase):
    """Unit tests for the Gobble game."""
    
    def setUp(self):
        """Set up a fresh game for each test."""
        self.game = Game()
    
    def test_initial_board(self):
        """Test that the board starts empty."""
        for row in self.game.board:
            for cell in row:
                self.assertEqual(cell, GameConfig.SYMBOLS['empty'])
    
    def test_valid_move(self):
        """Test placing a valid move."""
        success, msg = self.game.apply_move(2, 2, GameConfig.SYMBOLS['black'])
        self.assertTrue(success)
        self.assertEqual(self.game.board[2][2], GameConfig.SYMBOLS['black'])
    
    def test_out_of_bounds_move(self):
        """Test that out of bounds moves are rejected."""
        success, msg = self.game.apply_move(-1, 0, GameConfig.SYMBOLS['black'])
        self.assertFalse(success)
        self.assertEqual(msg, "Move out of bounds.")
        
        success, msg = self.game.apply_move(5, 5, GameConfig.SYMBOLS['black'])
        self.assertFalse(success)
        self.assertEqual(msg, "Move out of bounds.")
    
    def test_occupied_spot(self):
        """Test that moves on occupied spots are rejected."""
        self.game.apply_move(2, 2, GameConfig.SYMBOLS['black'])
        success, msg = self.game.apply_move(2, 2, GameConfig.SYMBOLS['white'])
        self.assertFalse(success)
        self.assertEqual(msg, "Spot not empty.")
    
    def test_basic_capture(self):
        """Test capturing a single stone."""
        self.game.apply_move(1, 1, GameConfig.SYMBOLS['black'])
        self.game.apply_move(1, 2, GameConfig.SYMBOLS['white'])
        self.game.apply_move(2, 1, GameConfig.SYMBOLS['white'])
        self.game.apply_move(0, 1, GameConfig.SYMBOLS['white'])
        success, msg = self.game.apply_move(1, 0, GameConfig.SYMBOLS['white'])
        self.assertTrue(success)
        self.assertEqual(self.game.board[1][1], GameConfig.SYMBOLS['empty'])
        self.assertIn("captured 1 bubble(s)", msg)
    
    def test_suicide_rule(self):
        """Test that suicide moves are prevented."""
        positions = [(0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)]
        for r, c in positions:
            self.game.board[r][c] = GameConfig.SYMBOLS['white']
        success, msg = self.game.apply_move(1, 1, GameConfig.SYMBOLS['black'])
        self.assertFalse(success)
        self.assertEqual(msg, "Move is suicidal.")
    
    def test_ko_rule(self):
        """Test that ko rule prevents immediate recapture."""
        self.game.board[0][1] = GameConfig.SYMBOLS['black']
        self.game.board[0][2] = GameConfig.SYMBOLS['white']
        self.game.board[1][0] = GameConfig.SYMBOLS['black']
        self.game.board[1][2] = GameConfig.SYMBOLS['black']
        self.game.board[1][3] = GameConfig.SYMBOLS['white']
        self.game.board[2][1] = GameConfig.SYMBOLS['black']
        self.game.board[2][2] = GameConfig.SYMBOLS['white']
        success, msg = self.game.apply_move(1, 1, GameConfig.SYMBOLS['white'])
        self.assertTrue(success)
        self.assertEqual(self.game.board[1][2], GameConfig.SYMBOLS['empty'])
        success, msg = self.game.apply_move(1, 2, GameConfig.SYMBOLS['black'])
        self.assertFalse(success)
        self.assertEqual(msg, "Ko rule: Cannot immediately recapture.")
    
    def test_group_detection(self):
        """Test that groups are correctly identified."""
        self.game.apply_move(1, 1, GameConfig.SYMBOLS['black'])
        self.game.apply_move(1, 2, GameConfig.SYMBOLS['black'])
        self.game.apply_move(2, 1, GameConfig.SYMBOLS['black'])
        group, liberties = self.game.get_group(1, 1)
        self.assertEqual(len(group), 3)
        self.assertEqual(len(liberties), 7)
    
    def test_pass_ends_game(self):
        """Test that two consecutive passes end the game."""
        self.assertFalse(self.game.pass_turn())
        self.assertTrue(self.game.pass_turn())
    
    def test_undo_move(self):
        """Test undo functionality."""
        self.game.apply_move(2, 2, GameConfig.SYMBOLS['black'])
        self.assertEqual(self.game.board[2][2], GameConfig.SYMBOLS['black'])
        success = self.game.undo_last_move()
        self.assertTrue(success)
        self.assertEqual(self.game.board[2][2], GameConfig.SYMBOLS['empty'])
        success = self.game.undo_last_move()
        self.assertFalse(success)
    
    def test_evaluation_function(self):
        """Test that position evaluation works correctly."""
        self.game.apply_move(2, 2, GameConfig.SYMBOLS['black'])
        self.game.apply_move(1, 1, GameConfig.SYMBOLS['white'])
        black_score = self.game.evaluate_position(GameConfig.SYMBOLS['black'])
        white_score = self.game.evaluate_position(GameConfig.SYMBOLS['white'])
        self.assertGreater(black_score, 0)
        self.assertGreater(white_score, 0)
    
    def test_capture_resets_ko(self):
        """Test that captures of multiple stones reset ko point."""
        self.game.apply_move(1, 1, GameConfig.SYMBOLS['black'])
        self.game.apply_move(1, 2, GameConfig.SYMBOLS['black'])
        self.game.apply_move(0, 1, GameConfig.SYMBOLS['white'])
        self.game.apply_move(0, 2, GameConfig.SYMBOLS['white'])
        self.game.apply_move(2, 1, GameConfig.SYMBOLS['white'])
        self.game.apply_move(2, 2, GameConfig.SYMBOLS['white'])
        self.game.apply_move(1, 3, GameConfig.SYMBOLS['white'])
        self.game.ko_point = (3, 3)
        success, msg = self.game.apply_move(1, 0, GameConfig.SYMBOLS['white'])
        self.assertTrue(success)
        self.assertIsNone(self.game.ko_point)
    
    def test_mcts_node_creation(self):
        """Test MCTS node initialization and move generation."""
        self.game.apply_move(2, 2, GameConfig.SYMBOLS['black'])
        node = MCTSNode(self.game)
        self.assertGreater(len(node.untried_moves), 20)
        pass_moves = [m for m in node.untried_moves if m[0] == -1]
        self.assertEqual(len(pass_moves), 1)
    
    def test_mcts_simulation(self):
        """Test that MCTS simulation completes and returns valid result."""
        node = MCTSNode(self.game)
        result = node.simulate()
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)
    
    def test_mcts_expansion_and_selection(self):
        """Test MCTS tree expansion and UCB selection."""
        root = MCTSNode(self.game)
        child = root.expand()
        self.assertEqual(len(root.children), 1)
        self.assertEqual(child.parent, root)
        child.backpropagate(1.0)
        selected = root.select_child()
        self.assertEqual(selected, child)

if __name__ == '__main__':
    unittest.main()
