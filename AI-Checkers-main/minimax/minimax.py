from copy import deepcopy
from typing import NewType
from numpy import inf
import random
import pygame
from checkers.game import Game

from tkinter import font

import pygame
import tkinter.messagebox as messagebox
from copy import deepcopy

WIDTH, HEIGHT = 700, 700
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

#rbg
pink = (255, 102, 178)
WHITE = (255, 255, 255)
grey = (128, 128, 128)
red = (153, 0, 0)
darkpink = (153,0,76)
black = (0, 0, 0)

CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (44, 25))

class Piece:
    PADDING = 15
    OUTLINE = 2

    def _init_(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False #initial there is no king
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
        pygame.draw.circle(win, darkpink, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2)) #put the crown

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calPos()

   # def _repr_(self):
    #    return str(self.color)


class Board:

    def _init_(self):
        self.board = []
        self.pinkLeft = self.whiteLeft = 12 # the number of Piece 12
        self.pinkKings = self.whiteKings = 0
        self.createBoard()

    def drawSquares(self, win):
        win.fill(grey) #all the board is gray
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2): #divide the board
                pygame.draw.rect(win, darkpink, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        return self.whiteLeft - self.pinkLeft + (self.whiteKings - self.pinkKings) #score
    def getAllPieces(self, color):
        pieces = [] #Initial
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color: #if there is a piece in square then
                    pieces.append(piece) #append in list
        return pieces

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col] #swap
        piece.move(row, col) #call the move in piece

        if row == ROWS - 1 or row == 0: #the last line or first line
            piece.makeKing() #if Piece in the end of the board
            if piece.color == WHITE: #if the rows-1
                self.whiteKings += 1
            else:
                self.pinkKings += 1 #if the row ==0

    def getPiece(self, row, col):
        return self.board[row][col]

    def createBoard(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS): #loop in columns
                if col % 2 == ((row + 1) % 2): #condition inside the columns to put peice 0=no piece 1=piece
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE)) #draw the places of pieces
                    elif row > 4:
                        self.board[row].append(Piece(row, col,pink))
                    else:
                        self.board[row].append(0) #no peice
                else:
                    self.board[row].append(0)  # no piece

    def draw(self, win):
        self.drawSquares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win) #draw the piece it self the circle of piece cll the function draw from piece

    def remove(self, pieces): #Jump the other piece
        for piece in pieces: #loop in jumbed piece
            self.board[piece.row][piece.col] = 0  #initial the oice that jumbed
            if piece != 0: #there is piece
                if piece.color == pink:
                    self.pinkLeft -= 1 # when the coin eat the other coin pinkLeft = the number of pieces
                else:
                    self.whiteLeft -= 1

    def winner(self):
        if self.pinkLeft <= 0: #the pieces is finished
            return WHITE
        elif self.whiteLeft <= 0:
            return pink

        return None  #the game is continue gaming

    def getValidMoves(self, piece):

        moves = {} #dictenary the  move (the move will do) : skipped (how much make kill the piece)
        if piece.king or piece.color == pink:
            moves.update(self._traverseLeft(piece.row, piece.col, -1, piece, [])) #valid move to left
            moves.update(self._traverseRight(piece.row, piece.col, -1, piece, [])) #valid move to right
        if piece.king or piece.color == WHITE:
            moves.update(self._traverseLeft(piece.row, piece.col, 1, piece, []))
            moves.update(self._traverseRight(piece.row, piece.col, 1, piece, []))

        return moves

    def _traverseLeft(self, row, column, step, piece, skipped=[]):
        moves = {}
        #last = []

        next_row, next_col = (row + step, column - 1) #step = 1 or -1 if 1 then move up in -1 then move down
        if 0 <= next_row < ROWS and next_col >= 0:
            step1 = self.board[next_row][next_col]
            if step1 == 0: # it not valid
                if not skipped:
                    moves[((piece.row, piece.col), (next_row, next_col))] = skipped #we can't do anything with it so it uninvalid so skipped
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

    def _init_(self, win):
        self._init()
        self.win = win #object from window if we play in more than one window and use it functions

    def update(self):
        self.board.draw(self.win) #draw every step and play make it
        pygame.display.update()

    def _init(self):
        self.selected = None #If clicked the piece
        self.board = Board()
        self.turn = pink #the turn of next game
        self.validMoves = {}

    def winner(self):
        return self.board.winner()

    def _move(self, row, col): #is the row and col is valid to go with it
        piece = self.board.getPiece(row, col) #the piece that i clicked with it
        if self.selected and piece == 0 and (row, col) in self.validMoves:
            self.board.move(self.selected, row, col) #make the piece move the selected square witt go with it
            skipped = self.validMoves[(row, col)] #the piece thai i move it to will put it in skipped to make it not valid
            if skipped:
                self.board.remove(skipped) #the red circle is remove it
            self.changeTurn()
        else:
            return False
        return True

    def changeTurn(self):
        self.validMoves = {} #after game the valid move is zero beacuse it not turned
        if self.turn == pink:
            self.turn = WHITE
        else:
            self.turn = pink

    def getBoard(self):
        return self.board

    def aiMove(self, board):
        self.board = board
        self.changeTurn() #change tutrn autamitly without clicked



def minimax(position, depth, maxPlayer): #max player =true of false true when turn to max otherwise false
    if position.winner():
        if position.winner() == WHITE:
            return (float('inf'), position)  # infinity is the maximum evaluation output
        return (float('-inf'), position)
    if depth == 0:
        return (position.evaluate(), position) #the end of depth (tree) so it is the game end
    if maxPlayer:
        v = float('-inf') #the min value can compare
        max_position = position # the current position on the board.
        for a in getAllMoves(position, WHITE).items(): # returns a list of all possible moves and their resulting positions in the form of tuples
            board = simulateMove(a, position)
            e, new_position = minimax(board, depth - 1, False) #evaluate the minimax
            if max(v, e) == e: #the variabl take place -inf
                v = e
                max_position = board
        return (v, max_position)

    else:
        v = float('inf')
        min_position = position
        for a in getAllMoves(position,pink).items():
            board = simulateMove(a, position)
            e, new_position = minimax(board, depth - 1, True)
            if min(v, e) == e:
                v = e
                min_position = board
        return (v, min_position)


def simulateMove(action, board): #make the move
    new_board = deepcopy(board) #copu board
    move, skipped = action
    piece = new_board.board[move[0][0]][move[0][1]] #piece in current board
    new_board.move(piece, move[1][0], move[1][1]) #move the piece to the new action
    new_board.remove(skipped) #if kill the pieces

    return new_board


def getAllMoves(board, color):
    moves = {}
    for p in board.getAllPieces(color):
        moves.update(board.getValidMoves(p))
    return moves


FPS = 60 #number of frames per second

WHITE_DEPTH = 2
pink_DEPTH = 1

WIN = pygame.display.set_mode((WIDTH, HEIGHT)) #the window of game
pygame.display.set_caption('Checkers') #name window

if _name_ == '_main_':
    run = True
    clock = pygame.time.Clock() #object of clock
    game = Game(WIN) #send window to game
    game.update()

    while run:
        clock.tick(FPS)

        if game.turn == WHITE:
            value, newBoard = minimax(game.getBoard(), WHITE_DEPTH, True)
            game.aiMove(newBoard)

        else:
            value, newBoard = minimax(game.getBoard(), pink_DEPTH, False)
            game.aiMove(newBoard)

        if game.winner() != None: #check if there is winner or not
            print(game.winner()) #the color that win
            run = False #close the game

        for event in pygame.event.get(): #any click do in window from user
            if event.type == pygame.QUIT: #exit game
                run = False


        game.update()


    pygame.quit()