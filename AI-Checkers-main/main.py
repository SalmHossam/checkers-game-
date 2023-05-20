import pygame
from tkinter import *
import tkinter.messagebox as messagebox
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo
import time
from copy import deepcopy

WIDTH, HEIGHT = 700, 700
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
pygame.init()

# rbg
pink = (153, 0, 76)
WHITE = (255, 255, 255)
grey = (128, 128, 128)
black = (0, 0, 0)

CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (50, 50))


class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False  # initial there is no king

        self.x = 0
        self.y = 0
        self.calPos()

    def calPos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def makeKing(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, self.color, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))  # put the crown

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calPos()

    def __repr__(self):
        return str(self.color)


class Board:

    def __init__(self):
        self.board = []
        self.pinkLeft = self.whiteLeft = 12  # the number of Piece 12
        self.pinkKings = self.whiteKings = 0
        self.createBoard()

    def drawSquares(self, win):
        win.fill(grey)  # all the board is gray
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):  # divide the board
                pygame.draw.rect(win, pink, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        return self.whiteLeft - self.pinkLeft + (self.whiteKings - self.pinkKings)  # score

    def getAllPieces(self, color):
        pieces = []  # Initial
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:  # if there is a piece in square then
                    pieces.append(piece)  # append in list
        return pieces

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][
            piece.col]  # swap
        piece.move(row, col)  # call the move in piece

        if row == ROWS - 1 or row == 0:  # the last line or first line
            piece.makeKing()  # if Piece in the end of the board
            if piece.color == WHITE:  # if the rows-1
                self.whiteKings += 1
            else:
                self.pinkKings += 1  # if the row ==0

    def getPiece(self, row, col):
        return self.board[row][col]

    def createBoard(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):  # loop in columns
                if col % 2 == ((row + 1) % 2):  # condition inside the columns to put peice 0=no piece 1=piece
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))  # draw the places of pieces
                    elif row > 4:
                        self.board[row].append(Piece(row, col, pink))
                    else:
                        self.board[row].append(0)  # no peice
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.drawSquares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)  # draw the piece it self the circle of piece cll the function draw from piece

    def remove(self, pieces):  # Jump the other piece
        for piece in pieces:  # loop in jumbed piece
            self.board[piece.row][piece.col] = 0  # initial the oice that jumbed
            if piece != 0:  # there is piece
                if piece.color == pink:
                    self.pinkLeft -= 1  # when the coin eat the other coin pinkLeft = the number of pieces
                else:
                    self.whiteLeft -= 1

    def winner(self):
        if self.pinkLeft <= 0:  # the pieces is finished
            return WHITE
        elif self.whiteLeft <= 0:
            return pink

        return None  # the game is continue gaming

    def getValidMoves(self, piece):

        moves = {}  # dictenary the  move (the move will do) : skipped (how much make kill the piece)
        if piece.king or piece.color == pink:
            # stop = max(piece.row-3, -1)
            moves.update(self._traverseLeft(piece.row, piece.col, -1, piece, []))  # valid move to left of pink
            moves.update(self._traverseRight(piece.row, piece.col, -1, piece, []))  # valid move to right of pink
        if piece.king or piece.color == WHITE:
            # stop = min(piece.row+3, ROWS)
            moves.update(self._traverseLeft(piece.row, piece.col, 1, piece, []))  # valid move to left of white
            moves.update(self._traverseRight(piece.row, piece.col, 1, piece, []))  # valid move to right of white

        return moves

    def _traverseLeft(self, row, column, step, piece, skipped=[]):
        moves = {}
        last = []

        next_row, next_col = (row + step, column - 1)  # step = 1 or -1 if 1 then move up in -1 then move down
        if 0 <= next_row < ROWS and next_col >= 0:
            step1 = self.board[next_row][next_col]
            if step1 == 0:  # it not valid
                if not skipped:
                    moves[((piece.row, piece.col),
                           (next_row, next_col))] = skipped  # we can't do anything with it so it uninvalid so skipped
            elif step1.color != piece.color:
                next_row, next_col = (next_row + step, next_col - 1)
                if 0 <= next_row < ROWS and next_col >= 0:
                    skipped.append(step1)
                    step2 = self.board[next_row][next_col]
                    if step2 == 0:
                        moves[((piece.row, piece.col), (next_row, next_col))] = skipped
                        if len(skipped) < 2:
                            moves.update(self._traverseLeft(next_row, next_col, step, piece, list(skipped)))
                            moves.update(self._traverseRight(next_row, next_col, step, piece, list(skipped)))

        return moves

    def _traverseRight(self, row, column, step, piece, skipped=[]):
        moves = {}
        last = []

        next_row, next_col = (row + step, column + 1)
        if 0 <= next_row < ROWS and next_col < COLS:

            step1 = self.board[next_row][next_col]
            if step1 == 0:
                if not skipped:
                    moves[((piece.row, piece.col), (next_row, next_col))] = skipped
            elif step1.color != piece.color:
                next_row, next_col = (next_row + step, next_col + 1)
                if 0 <= next_row < ROWS and next_col < COLS:
                    skipped.append(step1)
                    step2 = self.board[next_row][next_col]
                    if step2 == 0:
                        moves[((piece.row, piece.col), (next_row, next_col))] = skipped
                        if len(skipped) < 2:
                            moves.update(self._traverseLeft(next_row, next_col, step, piece, list(skipped)))
                            moves.update(self._traverseRight(next_row, next_col, step, piece, list(skipped)))
        return moves


class Game:

    def __init__(self, win):
        self._init()
        self.win = win  # object from window if we play in more than one window and use it functions

    def update(self):
        self.board.draw(self.win)
        pygame.display.update()  # draw every step and play make it

    def _init(self):
        self.selected = None  # If clicked the piece
        self.board = Board()
        self.turn = pink  # the turn of next game
        self.validMoves = {}

    def winner(self):
        return self.board.winner()

    def _move(self, row, col):  # is the row and col is valid to go with it
        piece = self.board.getPiece(row, col)  # the piece that i clicked with it
        if self.selected and piece == 0 and (row, col) in self.validMoves:
            self.board.move(self.selected, row, col)  # make the piece move the selected square witt go with it
            skipped = self.validMoves[
                (row, col)]  # the piece thai i move it to will put it in skipped to make it not valid
            if skipped:
                self.board.remove(skipped)  # the red circle is remove it
            self.changeTurn()
        else:
            return False
        return True

    def changeTurn(self):
        self.validMoves = {}  # after game the valid move is zero beacuse it not turned
        if self.turn == pink:
            self.turn = WHITE
        else:
            self.turn = pink

    def getBoard(self):
        return self.board

    def aiMove(self, board):
        self.board = board
        self.changeTurn()  # change tutrn autamitly without clicked


pink = (153, 0, 76)
WHITE = (255, 255, 255)


def minimax(position, depth, maxPlayer):  # max player =true of false true when turn to max otherwise false
    if position.winner():
        if position.winner() == WHITE:
            return (100, position)  # infinity is the maximum evaluation output
        return (-100, position)
    if depth == 0:
        return (position.evaluate(), position)  # the end of depth (tree) so it is the game end
    if maxPlayer:
        v = float('-inf')  # the min value can compare
        max_position = position  # the current position on the board.
        for a in getAllMoves(position,
                             WHITE).items():  # returns a list of all possible moves and their resulting positions in the form of tuples
            board = simulateMove(a, position)
            e, new_position = minimax(board, depth - 1, False)  # evaluate the minimax
            if max(v, e) == e:  # the variabl take place -inf
                v = e
                max_position = board
        return (v, max_position)

    else:
        v = float('inf')
        min_position = position
        for a in getAllMoves(position, pink).items():
            board = simulateMove(a, position)
            e, new_position = minimax(board, depth - 1, True)
            if min(v, e) == e:
                v = e
                min_position = board
        return (v, min_position)


def alphaBeta(position, depth, alpha, beta, maxPlayer):
    if position.winner():
        if position.winner() == pink:
            return (18, position)  # infinity is the maximum evaluation output
        return (-18, position)
    if depth == 0:
        return (position.evaluate(), position)  # the end of depth (tree) so it is the game end
    if maxPlayer:
        v = float('-inf')  # the min value can compare
        max_position = position  # the current position on the board.
        for a in getAllMoves(position, WHITE).items():  # returns a list of all possible moves and their resulting positions in the form of tuples
            board = simulateMove(a, position)
            e, new_position = alphaBeta(board, depth - 1, alpha, beta, False)  # evaluate the minimax
            v = max(v, e)
            alpha = max(alpha, e)
            if alpha >= beta:
                break
            max_position = board
        return (v, max_position)

    else:
        v = float('inf')
        min_position = position
        for a in getAllMoves(position, pink).items():
            board = simulateMove(a, position)
            e, new_position = alphaBeta(board, depth - 1, alpha, beta, True)
            v = min(v, e)
            beta = min(beta, e)
            if alpha >= beta:
                break
            min_position = board
        return (v, min_position)


def simulateMove(action, board):  # make the move
    new_board = deepcopy(board)  # copu board
    move, skipped = action
    piece = new_board.board[move[0][0]][move[0][1]]  # piece in current board
    new_board.move(piece, move[1][0], move[1][1])  # move the piece to the new action
    new_board.remove(skipped)  # if kill the pieces

    return new_board


def getAllMoves(board, color):
    moves = {}
    for p in board.getAllPieces(color):
        moves.update(board.getValidMoves(p))
    return moves


FPS = 60  # number of frames per second
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # the window of game
pygame.display.set_caption('Checkers Game')  # name window

# Easy Version
WHITE_DEPTH_1 = 3
pink_DEPTH_1 = 1
# Medium Version
WHITE_DEPTH_2 = 4
pink_DEPTH_2 = 2
# Hard Version
WHITE_DEPTH_3 = 6
pink_DEPTH_3 = 4


def getRowColFromMouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def main():
    run = True
    clock = pygame.time.Clock()  # object of clock
    game = Game(WIN)  # send window to game
    messagebox.showinfo("Game Checkers", "Start")
    name = askstring('Level of game', 'Choose your level')
    showinfo('Start', 'start, {}'.format(name))
    algo = askstring('Algorithm of game', 'Choose Algorithm')
    showinfo('Start', 'start, {}'.format(algo))
    while run:
        clock.tick(FPS)

        if name == "Easy":
            if algo == "alphaBeta":
                if game.turn == WHITE:
                    value, new_board = alphaBeta(game.getBoard(), WHITE_DEPTH_1, float('-inf'), float('inf'), True)
                    game.aiMove(new_board)
                else:
                    value, new_board = alphaBeta(game.getBoard(), pink_DEPTH_1, float('-inf'), float('inf'), False)
                    game.aiMove(new_board)
            elif algo == "MinMax":
                if game.turn == WHITE:
                    value, new_board = minimax(game.getBoard(), WHITE_DEPTH_1, True)
                    game.aiMove(new_board)
                else:
                    value, new_board = minimax(game.getBoard(), pink_DEPTH_1, False)
                    game.aiMove(new_board)

        elif name == "Medium":
            if algo == "alphaBeta":
                if game.turn == WHITE:
                    value, new_board = alphaBeta(game.getBoard(), WHITE_DEPTH_2, float('-inf'), float('inf'), True)
                    game.aiMove(new_board)
                else:
                    value, new_board = alphaBeta(game.getBoard(), pink_DEPTH_2, float('-inf'), float('inf'), False)
                    game.aiMove(new_board)
            elif algo == "MinMax":
                if game.turn == WHITE:
                    value, new_board = minimax(game.getBoard(), WHITE_DEPTH_2, True)
                    game.aiMove(new_board)
                else:
                    value, new_board = minimax(game.getBoard(), pink_DEPTH_2, False)
                    game.aiMove(new_board)

        elif name == "Hard":
            if algo == "alphaBeta":
                if game.turn == WHITE:
                    value, new_board = alphaBeta(game.getBoard(), WHITE_DEPTH_3, float('-inf'), float('inf'), True)
                    game.aiMove(new_board)
                else:
                    value, new_board = alphaBeta(game.getBoard(), pink_DEPTH_3, float('-inf'), float('inf'), False)
                    game.aiMove(new_board)
            elif algo == "MinMax":
                if game.turn == WHITE:
                    value, new_board = minimax(game.getBoard(), WHITE_DEPTH_3, True)
                    game.aiMove(new_board)
                else:
                    value, new_board = minimax(game.getBoard(), pink_DEPTH_3, False)
                    game.aiMove(new_board)

        else:
            messagebox.showinfo("Game Checkers", "Undefined Answer")

        if game.winner() is not None:  # check if there is winner or not
            print(game.winner())  # the color that win
            run = False  # close the game
        for event in pygame.event.get():  # any click do in window from user
            if event.type == pygame.QUIT:  # exit game
                run = False

        game.update()
    if name=="Easy" and algo=="alphaBeta":
        messagebox.showinfo("Game Over", "Winner is Purple pieces")
    else:
        messagebox.showinfo("Game Over", "Winner is White pieces, ate all the Purple pieces!")
    pygame.quit()


main()
