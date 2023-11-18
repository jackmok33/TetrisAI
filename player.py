from board import Direction, Rotation, Action
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError
    
class ForthPlayer(Player):
    def __init__(self):
        pass

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)

    #Measures to calculate score
    def bumpiness(self, cloned_board):
        bumpiness = 0
        for x in range(cloned_board.width):
            current_height = 0
            next_height = 0

            for y in range(cloned_board.height):
                if (x, y) in cloned_board.cells:
                    current_height = max(current_height, cloned_board.height - y)
                if(x+1, y) in cloned_board.cells:
                    next_height = max(next_height, cloned_board.height - y)

            height_diff = abs(current_height - next_height)
            bumpiness += height_diff
        
        return bumpiness
    
    def aggregate_height(self, cloned_board):
        aggregate_height = 0

        for x in range(cloned_board.width):
            height = 0

            for y in range(cloned_board.height):
                if(x, y) not in cloned_board.cells and (x, y + 1) in cloned_board.cells:
                    height = cloned_board.height - y
                    aggregate_height += height
                    break
        
        return aggregate_height
    
    def holes(self, cloned_board):
        holes = 0
        for x in range(cloned_board.width):
            for y in range(cloned_board.height):
                if(x, y) in cloned_board.cells and (x, y+1) not in cloned_board.cells:
                    for height in range(cloned_board.height - y):
                        if (x, y+ height) not in cloned_board.cells:
                            holes += 1
                    break
        return holes
    
    def max_height(self, cloned_board):
        maxheight = 0
        for x in range(cloned_board.width):
            height = 0
            for y in range(cloned_board.height):
                if(x, y) in cloned_board.cells:
                    height = max(height, cloned_board.height - y)
                    if height > maxheight:
                        maxheight = height

        if maxheight > 15:
            return maxheight
        return 0


    
    def empty_col(self, cloned_board):
        empty_col = 0
        for x in range(cloned_board.width):
            empty = True
            if(x, cloned_board.height-1) in cloned_board.cells:
                empty = False
            if empty == True:
                empty_col += 1

        return empty_col
    
    def completed_lines(self, cloned_board, board):
        old_aggregate_height = self.aggregate_height(board)
        new_aggregate_height = self.aggregate_height(cloned_board)
        height_difference = old_aggregate_height - new_aggregate_height

        aggregate = self.aggregate_height(cloned_board)
        max = self.max_height(cloned_board)

        if aggregate < 130 or max < 10:
            if height_difference > 25:
                completed_lines = 2000

            elif height_difference > 15:
                completed_lines = 30

            elif height_difference > 5:
                completed_lines = -2

            elif height_difference > 0:
                completed_lines = -4

            else:
                completed_lines = 0

        elif aggregate < 160 or max < 15:
            if height_difference > 25:
                completed_lines = 2000

            elif height_difference > 15:
                completed_lines = 30

            elif height_difference > 5:
                completed_lines = -0.5

            elif height_difference > 0:
                completed_lines = -1

            else:
                completed_lines = 0

        else:
            if height_difference > 25:
                completed_lines = 200

            elif height_difference > 15:
                completed_lines = 20

            elif height_difference > 5:
                completed_lines = 2

            elif height_difference > 0:
                completed_lines = 1

            else:
                completed_lines = 0

        return completed_lines
    
    #not working
    #score closer to bottom left will get higher score
    def build_landscape(self,cloned_board, board):
        new_num_blocks = 0
        old_num_blocks = 0
        for x in range(cloned_board.width//3):
            for y in range(cloned_board.height):
                if(x, y) in cloned_board.cells:
                    new_num_blocks += 1
                if (x, y) in board.cells:
                    old_num_blocks += 1
        if new_num_blocks > old_num_blocks:
            return 1
        return 0
                
    def calculate_score(self, cloned_board, board):
        bumpiness = self.bumpiness(cloned_board)
        aggregate_height = self.aggregate_height(cloned_board)
        holes = self.holes(cloned_board)
        max_height = self.max_height(cloned_board)
        empty_col = self.empty_col(cloned_board)
        completed_lines = self.completed_lines(cloned_board, board)
        build_landscape = self.build_landscape(cloned_board, board)

        a = - 0.35
        c = -2.6
        e = 0.5

        score = bumpiness * a  + holes * c  + completed_lines * e

        return score

    def move_to_target(self, cloned_board ,target_position, moves):
        has_landed = False

        while has_landed == False and target_position < cloned_board.falling.left:
            has_landed = cloned_board.move(Direction.Left)
            moves.append(Direction.Left)
            if has_landed == True:
                return has_landed

        while has_landed == False and target_position > cloned_board.falling.left:
            has_landed = cloned_board.move(Direction.Right)
            moves.append(Direction.Right)
            if has_landed == True:
                return has_landed
        
        return has_landed

    def rotate_to_target(self, cloned_board, target_rotation, moves):
        has_landed = False
        rotation = 0

        while has_landed == False and rotation < target_rotation:
            has_landed = cloned_board.rotate(Rotation.Clockwise)
            moves.append(Rotation.Clockwise)
            if has_landed == True:
                return has_landed
            rotation += 1
        return has_landed
    
    def next_move(self, board):
        for target_rotation in range(4):
            sandbox = board.next.clone()
            has_landed = self.rotate_to_target(sandbox, target_rotation)
            if has_landed == True:
                continue
            for target_position in range(board.width):

                cloned_next = sandbox.clone()
                has_landed = self.move_to_target(cloned_next, target_position)
                
                if has_landed == False:
                    cloned_next.move(Direction.Drop)
                else:
                    continue
                
                score = self.calculate_score(cloned_next, board)
                if score > best_score:
                    best_score = score
        return best_score

    
    def simulate_moves(self, board):
        best_score = -10000
        moves = []
        best_moves = []

        for target_rotation in range(4):
            sandbox = board.clone()
            has_landed = self.rotate_to_target(sandbox, target_rotation, moves)
            if has_landed == True:
                continue
            for target_position in range(board.width):
                inner_move = [*moves]

                cloned_board = sandbox.clone()
                has_landed = self.move_to_target(cloned_board, target_position, inner_move)
                
                if has_landed == False:
                    cloned_board.move(Direction.Drop)
                    inner_move.append(Direction.Drop)

                    
                else:
                    continue
                
                score = self.calculate_score(cloned_board, board)

                if score > best_score:
                    best_score = score
                    best_moves = inner_move.copy()
                inner_move.clear()
            moves.clear()

        return best_moves
    
    def max_height_x_position(self, board):
        maxheight = 0
        x_target = 0
        for x in range(board.width):
            height = 0
            for y in range(board.height):
                if(x, y) in board.cells:
                    height = max(height, board.height - y)
                    if height > maxheight:
                        maxheight = height
                        x_target = x
        return x_target
    
    def move_to_bomb(self, cloned_board ,target_position):
        has_landed = False
        moves = []
        while has_landed == False and target_position < cloned_board.falling.left:
            has_landed = cloned_board.move(Direction.Left)
            moves.append(Direction.Left)
            if has_landed == True:
                moves.pop()
                moves.append(Action.Bomb)

        while has_landed == False and target_position > cloned_board.falling.left:
            has_landed = cloned_board.move(Direction.Right)
            moves.append(Direction.Right)
            if has_landed == True:
                moves.pop()
                moves.append(Action.Bomb)
        if has_landed == False:
            moves.append(Action.Bomb)
        return moves
    
    def choose_action(self, board):
        time.sleep(0.)
        
        return self.simulate_moves(board)
        
SelectedPlayer = ForthPlayer