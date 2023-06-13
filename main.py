from copy import deepcopy
import random
import time
import turtle
NEG_INFINITY = -1000
POS_INFINITY = 1000
explored_nodes = 0
n = 0
m = 0

class OthelloUI:
    def __init__(self, board_size=6, square_size=60):
        self.board_size = board_size
        self.square_size = square_size
        self.screen = turtle.Screen()
        self.screen.setup(self.board_size * self.square_size + 50, self.board_size * self.square_size + 50)
        self.screen.bgcolor('white')
        self.screen.title('Othello')
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        turtle.tracer(0, 0)
        

    def draw_board(self, board):
        self.pen.penup()
        x, y = -self.board_size / 2 * self.square_size, self.board_size / 2 * self.square_size
        for i in range(self.board_size):
            self.pen.penup()
            for j in range(self.board_size):
                self.pen.goto(x + j * self.square_size, y - i * self.square_size)
                self.pen.pendown()
                self.pen.fillcolor('green')
                self.pen.begin_fill()
                self.pen.setheading(0)
                for _ in range(4):
                    self.pen.forward(self.square_size)
                    self.pen.right(90)
                self.pen.penup()
                self.pen.end_fill()
                self.pen.goto(x + j * self.square_size + self.square_size / 2,
                              y - i * self.square_size - self.square_size + 5)
                if board[i][j] == 1:
                    self.pen.fillcolor('white')
                    self.pen.begin_fill()
                    self.pen.circle(self.square_size / 2 - 5)
                    self.pen.end_fill()
                elif board[i][j] == -1:
                    self.pen.fillcolor('black')
                    self.pen.begin_fill()
                    self.pen.circle(self.square_size / 2 - 5)
                    self.pen.end_fill()

        turtle.update()


class Othello:
    def __init__(self, ui, minimax_depth=1, prune=True):
        self.size = 6
        self.ui = OthelloUI(self.size) if ui else None
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.board[int(self.size / 2) - 1][int(self.size / 2) - 1] = self.board[int(self.size / 2)][
            int(self.size / 2)] = 1
        self.board[int(self.size / 2) - 1][int(self.size / 2)] = self.board[int(self.size / 2)][
            int(self.size / 2) - 1] = -1
        self.current_turn = random.choice([1, -1])
        self.changedPieces = {}
        self.minimax_depth = minimax_depth
        self.prune = prune
        self.best_move = {}

    def set_board(self, new_board):
        self.board = new_board

    def get_winner(self):
        white_count = sum([row.count(1) for row in self.board])
        black_count = sum([row.count(-1) for row in self.board])
        if white_count > black_count:
            return 1
        elif white_count < black_count:
            return -1
        else:
            return 0
    
    def calc_prioritiy(self,key):
        i, j = key
        for x in [0, 5]:
            for y in [0, 5]:
                if (i,j) == (x,y):
                    return 1
            for y in [1,2,3,4]:
                if (i,j) == (x,y) or (i,j) == (y,x):
                    return 2
        return 3

    def get_valid_moves(self, player):
        moves = set()
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            x, y = i, j
                            captured = []
                            while 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][
                                    y + dj] == -player:
                                captured.append((x + di, y + dj))
                                x += di
                                y += dj
                            if 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][
                                    y + dj] == player and len(captured) > 0:
                                moves.add((i, j))
        return list(moves)

    def make_move(self, player, move):
        i, j = move
        changed = [move]
        self.board[i][j] = player
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                x, y = i, j
                captured = []
                while 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][y + dj] == -player:
                    captured.append((x + di, y + dj))
                    x += di
                    y += dj
                if 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][y + dj] == player:
                    for (cx, cy) in captured:
                        self.board[cx][cy] = player
                        changed.append((cx, cy))
        return changed

    def get_cpu_move(self):
        moves = self.get_valid_moves(-1)
        if len(moves) == 0:
            return None
        return random.choice(moves)

    def evaluate(self):
        white_count, black_count = 0, 0
        for i in range(0,6):
            for j in range(0,6):
                if self.board[i][j] == 1:
                    white_count += 1
                    if i == 0 or i == 5:
                        white_count += 1
                    if j == 0 or j == 5:
                        white_count += 1
                elif self.board[i][j] == -1:
                    black_count += 1
                    if i == 0 or i == 5:
                        black_count += 1
                    if j == 0 or j == 5:
                        black_count += 1
        return white_count - black_count

    def retrackBoard(self, depth):
        x,y = self.changedPieces[depth].pop(0)
        self.board[x][y] = 0
        for x,y in self.changedPieces[depth]:
            self.board[x][y] = -self.board[x][y]

    def max_val(self, depth, alpha, beta):
        global explored_nodes, n
        if depth < 0:
           return self.evaluate()
        moves = self.get_valid_moves(1)
        if moves == []:
            return self.evaluate()
        max_till_now = alpha
        for move in moves:
            self.changedPieces[depth] = self.make_move(1, move)
            explored_nodes += 1
            val = self.min_val(depth - 1, alpha, beta) 
            if val > max_till_now:
                max_till_now = val
                self.best_move[depth] = move
            if self.prune and max_till_now >= beta:
                n += 1
                self.retrackBoard(depth)
                return max_till_now
            alpha = max(max_till_now, alpha)
            self.retrackBoard(depth)
    
        return max_till_now

    def min_val(self, depth, alpha, beta):
        global explored_nodes, m
        if depth < 0:
            return self.evaluate()
        moves = self.get_valid_moves(-1)
        if moves == []:
            return self.evaluate()
        min_till_now = beta
        for move in moves:
            self.changedPieces[depth] = self.make_move(-1, move)
            explored_nodes += 1
            val = self.max_val(depth - 1, alpha, beta)
            if val < min_till_now:
                min_till_now = val
                self.best_move[depth] = move
            if self.prune and min_till_now <= alpha:
                m += 1
                self.retrackBoard(depth)
                return min_till_now
            beta = min(min_till_now, beta)
            self.retrackBoard(depth)
        return min_till_now

    def get_human_move(self):
        moves = self.get_valid_moves(1)
        if len(moves) == 0:
            return None
        self.max_val(depth = self.minimax_depth, alpha = NEG_INFINITY, beta = POS_INFINITY)
        return self.best_move[self.minimax_depth]

    def terminal_test(self):
        return len(self.get_valid_moves(1)) == 0 and len(self.get_valid_moves(-1)) == 0

    def play(self):
        winner = None
        while not self.terminal_test() :
            if self.ui:
                self.ui.draw_board(self.board)
            if self.current_turn == 1:
                move = self.get_human_move()
                if move:
                    self.make_move(self.current_turn, move)
            else:
                move = self.get_cpu_move()
                if move:
                    self.make_move(self.current_turn, move)
            self.current_turn = -self.current_turn
            if self.ui:
                self.ui.draw_board(self.board)
                time.sleep(0.1)
        winner = self.get_winner()
        return winner

RANGE = 10
depth = 5
alpha_beta_prune = 0
test = []
start_time = time.time()
for i in range(RANGE):
    otl = Othello(0, depth, alpha_beta_prune)
    winner = otl.play()
    print(i, ":" ,winner)
    test.append(winner)

human_win = test.count(1)
cpu_win = test.count(-1)
equal = test.count(0)
print("depth: ", depth)
print("human: ",human_win/RANGE)
print("cpu: ",cpu_win/RANGE)
print("mean explored nodes: ", explored_nodes/RANGE)
print("--- %s seconds ---" % (time.time() - start_time))
print(n/RANGE)
print(m/RANGE)


