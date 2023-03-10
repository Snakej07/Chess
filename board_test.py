import pygame
import sys
from Tile import *
from pieces import *
import copy
import time


PIECELIST = ["wk", "wq", "wr", "wb", "wn", "wp", "bk", "bq", "br", "bb", "bn", "bp", 
             "wkh", "wqh", "wrh", "wbh", "wnh", "wph", "bkh", "bqh", "brh", "bbh", "bnh", "bph"]
piecedic = {}
for piece in PIECELIST:
    piecedic[piece] = pygame.image.load("chess_pieces/"+piece+".PNG")
WIDTH = 512
HEIGHT = 512
DIR = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(-1,-1),(1,-1)]
N_DIR = [(-2,-1),(-2,1),(-1,-2),(1,-2),(2,-1),(2,1),(-1,2),(1,2)]
STR_DIR = [(1,0),(-1,0),(0,1),(0,-1)]
DIAG_DIR = [(1,1),(-1,1),(-1,-1),(1,-1)]

#IMPORTANT: calling a piece on the board acts like board[rank][file] or board[y][x]

class Board:
    def __init__(self, screen):
        self.screen = screen
        self.bool = True
        self.color = None
        self.curteam = "w"
        self.moves_dict, self.moves_dictw, self.moves_dictb = {}, {}, {}
        self.board = [[Tile(0,0),Tile(0,0),Tile(0,0),Tile(0,0),Tile(0,0),Tile(0,0),Tile(0,0),Tile(0,0)] for _ in range(8)]
        for rank in range(8):
            for file in range(8):
                self.board[rank][file] = Tile(file, rank)
        self.board[0] = [Tile(0,0,Rook("b")), Tile(1,0,Knight("b")), Tile(2,0,Bishop("b")), Tile(3,0,Queen("b")),
                         Tile(4,0,King("b")), Tile(5,0,Bishop("b")), Tile(6,0,Knight("b")), Tile(7,0,Rook("b"))]
        self.board[1] = [Tile(0,1,Pawn("b")), Tile(1,1,Pawn("b")), Tile(2,1,Pawn("b")), Tile(3,1,Pawn("b")),
                         Tile(4,1,Pawn("b")), Tile(5,1,Pawn("b")), Tile(6,1,Pawn("b")), Tile(7,1,Pawn("b"))]        
        self.board[6] = [Tile(0,6,Pawn("w")), Tile(1,6,Pawn("w")), Tile(2,6,Pawn("w")), Tile(3,6,Pawn("w")),
                         Tile(4,6,Pawn("w")), Tile(5,6,Pawn("w")), Tile(6,6,Pawn("w")), Tile(7,6,Pawn("w"))]       
        self.board[7] = [Tile(0,7,Rook("w")), Tile(1,7,Knight("w")), Tile(2,7,Bishop("w")), Tile(3,7,Queen("w")),
                         Tile(4,7,King("w")), Tile(5,7,Bishop("w")), Tile(6,7,Knight("w")), Tile(7,7,Rook("w"))]
        
    def get_square(self, pos):
        return self.board[pos[1]][pos[0]]
    
    def draw(self):
        for i in range(8):
            for j in range(8):
                if (i+1)%2 == 1 and (8-j)%2 == 1:
                     self.color = (169,108,69)
                elif (i+1)%2 == 0 and (8-j)%2 == 0:
                    self.color = (169,108,69)
                else:
                    self.color = (245,198,156)
                pygame.draw.rect(self.screen, self.color, pygame.Rect((WIDTH//8)*i,(HEIGHT//8)*j,WIDTH//8,HEIGHT//8))

    def makeButton(self, cur, rect):
            if rect.collidepoint(cur):
                pos1 = pygame.mouse.get_pos()[0]//(WIDTH//8)
                pos2 = pygame.mouse.get_pos()[1]//(HEIGHT//8)
                return (pos1,pos2)
    
    def nextturn(self):
        self.curteam = "b" if self.curteam == "w" else "w"

    def kingLoc(self, board):
        wKingLoc, bKingLoc = (int,int), (int,int)
        for rank in board:
            for tile in rank:
                if isinstance(tile.piece, King):
                    if tile.piece.color == "w":
                        wKingLoc = (tile.file,tile.rank)
                    if tile.piece.color == "b":
                        bKingLoc = (tile.file,tile.rank)
        return [wKingLoc, bKingLoc]

    def moveTo(self, piece, pos1, pos2):
        self.board[pos1[1]][pos1[0]] = Tile(pos1[0],pos1[1])
        self.board[pos2[1]][pos2[0]] = Tile(pos2[0],pos2[1],piece)

    def testmove(self, piece, pos1, pos2, board):
        board[pos1[1]][pos1[0]] = Tile(pos1[0],pos1[1])
        board[pos2[1]][pos2[0]] = Tile(pos2[0],pos2[1],piece)
        return board

    def untestmove(self, piece1, piece2, pos1, pos2, board):
        board[pos1[1]][pos1[0]] = Tile(pos1[0],pos1[1],piece1)
        board[pos2[1]][pos2[0]] = Tile(pos2[0],pos2[1],piece2)
        return board

    def callmove(self, piece, endpos, board, bool = True):
        file = endpos[0]
        rank = endpos[1]
        move = Movetypes(piece, rank, file, board, self, bool = bool)
        if isinstance(piece, Pawn):
            return move.p_moves()
        if isinstance(piece, Knight):
            return move.n_moves()
        if isinstance(piece, Bishop):
            return move.b_moves()
        if isinstance(piece, Rook):
            return move.r_moves()
        if isinstance(piece, Queen):
            return move.q_moves()
        if isinstance(piece, King):
            return move.k_moves()
    
    def get_all_moves(self, board, bool = True):
        self.all_moves_white = []
        self.all_moves_black = []
        self.moveList = []
        for i in range(8):
            for j in range(8):
                tile = self.board[j][i]
                if tile.piece != None:
                    self.moveList = self.callmove(tile.piece, (i,j), board)
                    if tile.piece.color == "w" and type(self.moveList) is list:
                        self.all_moves_white += self.moveList
                        self.moves_dict[(i,j)] = self.moveList #creates a list of moves for dictionary key at the piece position

                    elif tile.piece.color == "b" and type(self.moveList) is list:
                        self.all_moves_black += self.moveList
                        self.moves_dict[(i,j)] = self.moveList

        return (self.all_moves_white, self.all_moves_black, self.moves_dict) 

    '''def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.curteam == "w":
            startRank = self.kingLoc(self.board)[0][1]
            startFile = self.kingLoc(self.board)[0][0]
        else:
            startRank = self.kingLoc(self.board)[1][1]
            startFile = self.kingLoc(self.board)[1][0]
        
        for d in DIR:
            possiblePin = ()
            for i in range(1,8):
                iterRank = startRank + d[0] * i
                iterFile = startFile + d[1] * i
                #print(iterFile, iterRank)
                if inrange(iterRank, iterFile):
                    iterTile = self.board[iterRank][iterFile]
                    iterPiece = iterTile.piece
                    if iterPiece != None:
                        if iterTile.has_ally(self.curteam):
                            if possiblePin == ():
                                possiblePin = (iterFile, iterRank, d[0], d[1])
                            elif len(possiblePin) == 1:
                                possiblePin = ()
                                break

                        elif iterPiece.color != self.color:
                            if (isinstance(iterPiece, Rook) and (d in STR_DIR)) or (isinstance(iterPiece, Bishop) and (d in DIAG_DIR)) or \
                                (isinstance(iterPiece, Pawn) and i==1 and ((self.curteam == "b" and (d in DIAG_DIR[2:])) or(self.curteam == "w"  and (d in DIAG_DIR[:2])))) or \
                                (isinstance(iterPiece, Queen)) or (i==1 and isinstance(iterPiece, King)):
                                if possiblePin == (): #there are no possible pins and there is an enemy piece in this line
                                    inCheck = True
                                    checks.append((iterFile, iterRank, d[0], d[1]))
                                    break
                                elif len(possiblePin) == 1: #there is a possible pin and an an enemy piece in this line
                                    pins.append(possiblePin)
                                    break
                            else:
                                break
                else: #out of range
                    break
        for d in N_DIR:
            iterRank = startRank + d[0]
            iterFile = startFile + d[1]
            if inrange(iterRank, iterFile):
                iterTile = self.board[iterRank][iterFile]
                iterPiece = iterTile.piece
                if iterTile.has_enemy(self.curteam) and isinstance(iterPiece, Knight):
                    inCheck = True
                    checks.append((iterFile, iterRank, d[0], d[1]))
        return inCheck, pins, checks

    def inchecktest(self, piece, pos1, pos2):
        #print(pos1, pos2)
        test = False
        testboard = copy.deepcopy(self.board)
        piece2 = testboard[pos2[1]][pos2[0]].piece
        testboard = self.testmove(piece, pos1, pos2, testboard)
        if piece != None:
            moves = self.get_all_moves(testboard, bool = False)[1] if piece.color == "w" else self.get_all_moves(testboard, bool = False)[0]
            for m in moves:
                iterTile = testboard[m[1]][m[0]]
                if isinstance(iterTile.piece, King):
                    test = True
                    break
            
        testboard = self.untestmove(piece, piece2, pos1, pos2, testboard)
        #self.get_all_moves(testboard, bool = False)
        return test

    def incheck(self, piece, endpos):
        test = False
        moves = self.get_all_moves(self.board)[2]
        print(moves)
        moveablepiece = []
        
        for key in moves:
            print(self.board[key[1]][key[0]].piece, (key[0], key[1]))
            if endpos in moves[key]:
                moveablepiece.append(key)
    
        for tile in moveablepiece:
            startpos = (tile[0], tile[1])
            
            moves = self.get_all_moves(self.board, bool = False)[1] if piece.color == "w" else self.get_all_moves(self.board, bool = False)[0]
            
            #print(self.board[tile[1]][tile[0]].piece)
            if self.inchecktest(self.board[tile[1]][tile[0]].piece, startpos, endpos):
                test = True
                break
        return test

    def valid_moves(self):
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        moves = self.get_all_moves(self.board)
        kingLocs = self.kingLoc(self.board)
        legalTiles = []
        if self.curteam == "w":
            kingRank = kingLocs[0][1]
            kingFile = kingLocs[0][0]
        else:
            kingRank = kingLocs[1][1]
            kingFile = kingLocs[1][0]
            #print((kingRank, kingFile))  

        if self.inCheck:
            if len(self.checks) == 1:
                check = self.checks[0]
                checkingRank = check[1]
                checkingFile = check[0]
                pieceChecking = self.board[checkingRank][checkingFile].piece
                legalTiles = []

                if isinstance(pieceChecking, Knight):
                    legalTiles = [(checkingFile, checkingRank)] #must take the knight
                else:
                    for i in range(1, 8):
                        legalTile = (kingFile + check[2] * i, kingRank + check[3] * i)
                        if inrange(legalTile[1], legalTile[0]):
                            if legalTile not in legalTiles:
                                piece = self.board[kingRank][kingFile].piece
                                #print(legalTile)
                                if piece != None:
                                    if not self.incheck(piece, legalTile):
                                        #print("not in check if moved")
                                        legalTiles.append(legalTile)
                            if legalTile[0] == checkingFile and legalTile[1] == checkingRank:
                                break
                
            else:
                kingTile = self.board[kingRank][kingFile]
                legalTiles = self.callmove(kingTile.piece, (kingFile, kingRank), self.board)
                
        else:
            if self.curteam == "w":
                legalTiles = moves[0]
            else:
                legalTiles = moves[1]
            
        return legalTiles'''
        
    




class Movetypes:
    def __init__(self, piece, rank, file, board, boardclass, bool = True):
        self.piece = piece
        self.rank = rank
        self.file = file
        self.pos = (file, rank)
        self.color = piece.color
        self.bool = bool
        self.board = board
        self.boardclass = boardclass
        self.potmoves = []
           
    def p_moves(self):
        firstmove = False
        i = -1 if self.piece.color == "w" else 1
        dir = [(1,1*i),(-1,1*i)]
        if (self.piece.color == "w" and self.rank == 6) or (self.piece.color == "b" and self.rank == 1):
            firstmove = True

        if self.board[self.rank+i][self.file].piece == None:
            move = (self.file, self.rank+i)
            if self.bool == True:
                if not self.incheckmove(move):
                    print(move)
                    self.potmoves.append(move)
            else:
                self.potmoves.append(move)
            
            #look at the king of the person who is moving and go through all of the possible ways it could be attacked
        if firstmove == True and self.board[self.rank+(2*i)][self.file].piece == None:
            move = (self.file, self.rank+(2*i))
            if self.bool == True:
                if not self.incheckmove(move):
                    print(move)
                    self.potmoves.append(move)
            else:
                self.potmoves.append(move)
            
                   
        for d in dir:
            if inrange(self.rank+d[1],self.file+d[0]):
                if self.board[self.rank+d[1]][self.file+d[0]].piece != None:
                    if not self.board[self.rank][self.file].samecolor(self.board[self.rank+d[1]][self.file+d[0]].piece.color):
                        move = (self.file+d[0],self.rank+d[1])
                        if self.bool == True:
                            if not self.incheckmove(move):
                                print(move)
                                self.potmoves.append(move)
                        else:
                            self.potmoves.append(move)
                        
                

        return self.potmoves
    
    def n_moves(self):
        for d in N_DIR:
            x, y = self.file + d[0], self.rank + d[1]
            if inrange(y, x):
                itertile = Tile(x, y, self.board[y][x].piece)
                if itertile.emptytile() or not itertile.has_ally(self.piece.color):
                    if self.bool == True:
                            if not self.incheckmove((x,y)):
                                print((x,y))
                                self.potmoves.append((x,y))
                    else:
                        self.potmoves.append((x,y))
        return self.potmoves
    
    def b_moves(self):
        self.potmoves += self.straight_move(DIAG_DIR)
        return self.potmoves
    
    def r_moves(self):
        self.potmoves += self.straight_move(STR_DIR)
        return self.potmoves
    
    def q_moves(self):
        
        
        self.potmoves += self.straight_move(DIR)
        return self.potmoves
    
    def k_moves(self):
        dir = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(-1,-1),(1,-1)]
        for d in dir:
            rank_dir, file_dir = d
            rank_move = self.rank + rank_dir
            file_move = self.file + file_dir
            if inrange(rank_move, file_move):
                itertile = Tile(rank_move, file_move, self.board[rank_move][file_move].piece)
                if itertile.emptytile() or not itertile.has_ally(self.piece.color):
                    move = (file_move, rank_move)
                    self.callincheck(move)
                        
        
        return self.potmoves

    def straight_move(self, dir):
        smoves = [] #temporary list for straight moves - will make a move class or a total moves list in future
        for d in dir:
            rank_dir, file_dir = d
            rank_move = self.rank + rank_dir
            file_move = self.file + file_dir

            while True:
                if inrange(rank_move, file_move):
                    itertile = Tile(rank_move, file_move, self.board[rank_move][file_move].piece)
                    if itertile.piece == None: #maybe put this in board class so can just call self.board[rank][file].emptytile
                        if self.bool == True:
                            if not self.incheckmove((file_move, rank_move)):
                                print((file_move, rank_move))
                                self.potmoves.append((file_move,rank_move))
                        else:
                            self.potmoves.append((file_move,rank_move))

                    elif not itertile.piece == None:
                        if not itertile.has_ally(self.piece.color):
                            if self.bool == True:
                                if not self.incheckmove((file_move, rank_move)):
                                    print((file_move, rank_move))
                                    self.potmoves.append((file_move,rank_move))
                                    break
                            else:
                                self.potmoves.append((file_move,rank_move))
                                break

                        elif itertile.has_ally(self.piece.color):
                            break
                else:
                    break
                rank_move = rank_move + rank_dir
                file_move = file_move + file_dir
        return smoves

    def incheckmove(self, move): #implement this over each piece
        piece = self.piece #piece that we are checking the result of its potential moves
        pos = self.pos #start position of the piece we are checking
        testboard = copy.deepcopy(self.board)
        testboard = self.testmovepiece(piece, pos, move, testboard)
        for rank in range(8):
            for file in range(8):
                if testboard[rank][file].has_enemy(piece.color): #if square on the board has an enemy
                    enemy_piece = testboard[rank][file].piece #get which piece is on that square
                    enemy_moves = self.boardclass.callmove(enemy_piece, (file, rank), testboard, bool = False) #get the moves of that piece with bool = False, so it doesnt call this function again
                    for m in enemy_moves:
                        if isinstance(testboard[m[1]][m[0]].piece, King):
                            return True
        print("valid move at", move)
        return False

    def testmovepiece(self, piece, pos1, pos2, board):
        board[pos1[1]][pos1[0]] = Tile(pos1[0],pos1[1])
        board[pos2[1]][pos2[0]] = Tile(pos2[0],pos2[1],piece)
        return board

    def callincheck(self, move):
        if self.bool == True:
                if not self.incheckmove(move):
                    print(move)
                    self.potmoves.append(move)
        else:
            self.potmoves.append(move)

                
        




def draw_piece(screen,tile):
    if tile.piece != None:
        image = tile.piece.imagename
        screen.blit(pygame.transform.scale(piecedic[image],(WIDTH//8,HEIGHT//8)), pygame.Rect((WIDTH//8)*tile.file,(HEIGHT//8)*tile.rank,WIDTH//8,HEIGHT//8))

def main():
    pygame.init()
    pygame.display.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    board1 = Board(screen)
    square = pygame.Rect((0,0), (512,512))
    startsq, piece1, piecemoves = None, None, None
    clicks = []
    while True:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    #if board1.curteam == "w":
                        selectedsq = board1.makeButton(event.pos, square)
                        selectedpiece = board1.get_square(selectedsq).piece
                        if selectedpiece != None:
                            if len(clicks) == 0 and selectedpiece.color == board1.curteam:
                                clicks.append(selectedsq)
                                startsq = selectedsq
                                
                            elif len(clicks) == 1 and startsq == selectedsq:
                                selectedpiece.imagename = selectedpiece.imagename[:2]
                                clicks = []
                                startsq = None
                                
                            elif len(clicks) == 1 and selectedpiece.color != board1.curteam:
                                clicks.append(selectedsq)
                                
                            elif len(clicks) == 1 and selectedpiece.color == board1.curteam and piece1 != None:
                                piece1.imagename = piece1.imagename[:2]
                                selectedpiece.imagename = selectedpiece.imagename[:2]
                                clicks = []
                                
                            if len(clicks) == 1 and selectedpiece.color == board1.curteam:
                                piece1 = selectedpiece
                                selectedpiece.imagename = selectedpiece.imagename + "h"
                                piecemoves = board1.callmove(piece1, clicks[0], board1.board)
                                
                        elif selectedpiece == None and len(clicks)==0:
                            clicks = []
                        else:
                            clicks.append(selectedsq)
                            startsq = selectedsq
                        if len(clicks) == 2 and piece1 != None:
                            piece1.imagename = piece1.imagename[:2]
                            moves = board1.get_all_moves(board1.board)[0] if board1.curteam == "w" else board1.get_all_moves(board1.board)[1]
                            if piece1.color == board1.curteam and clicks[1] in piecemoves:
                                
                                board1.moveTo(piece1, clicks[0],clicks[1])
                                board1.nextturn()

                            elif moves == []:
                                print("checkmate") 


                                '''elif legal_moves == []:
                                    print("checkmate")
                                    for _ in range(10):
                                        
                                        time.sleep(0.1)
                                else:
                                    print("not a legal move")'''
                            clicks = []
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pygame.mixer.music.unpause()
                    print("unpaused music")
                if event.key == pygame.K_s:
                    pygame.mixer.music.pause()
                    print("paused music")
                
            
        

            #if board1.curteam == "b": #make AI moves here
            #EX: board1.moveTo(piece, startpos, endpos)
            
        
        pygame.display.set_caption("Chess")
        boardimage = pygame.image.load("WhiteBackground.jpeg")
        screen.blit(boardimage, (0, 0))
        board1.draw()
        for rank in board1.board:
            for p in rank:
                draw_piece(screen,p)
        pygame.display.update()

main()
