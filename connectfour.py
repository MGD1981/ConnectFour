# coding=utf-8
import copy
import pdb
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from random import randint

CSI="\x1B["
# sample: print CSI+"31;40m" + "Colored Text" + CSI + "0m"

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()

def cls():
    print CSI+"30;47m" + CSI+"2J" # clears screen

# I think that this is subtly wrong - a board w/ 4 in a row placed as the 
# last move, then it'll return a stalemate rather than a win 
def winstate(board):
    if '0' not in str(board):
        return 2 # stalemate
    elif assignvalue(board) != 0:
        return 1 # win
    else:
        return 0 # not end state

# I think that this is buggy - if the whole column is full, 
# then y could wind up at -1, at which point it'll throw an 
# exception (I had this happen while plaing, and think this is the cause ...) -LEL
def findy(board, x):
    y = 5
    while board[x][y] != 0:
        y -= 1
        if y < 0:
            return None
    return y

def minimax(difficulty, board, depth=0):    
    """
    For every column that isn't filled up, the function will test a board with
    that move having been made.  It takes the value from the assignvalue()
    function (0 or 'inf'), and compares it to the negative value of the same
    function run recursively until either a winning move (or stalemate) is
    found, or the maximum depth is reached.  The higher of the two compared
    values is then compared with the next recursed function upwards, until
    the top of the recursion tree is reached.  Once this occurs, the column
    associated with that optimal move is returned.  If no move is optimal,
    a random legal move is returned. 
    """
 
    p = board.playerturn()
    maxval = -float('inf')
    best_move = None

    for x in range(len(board.boarddata)):
        if board.boarddata[x][0] != 0:
            continue
        y = findy(board.boarddata, x)
        if y == None:
            continue
        board.boarddata[x][y] = p 

        if depth == difficulty or winstate(board.boarddata) != 0:
            maxval = assignvalue(board.boarddata)
            board.boarddata[x][y] = 0
            depth -= 1
            return (maxval, x) 
        
        prev_max = maxval
        maxval = max(maxval, -1 * minimax(difficulty, board, depth+1)[0])
        if maxval > prev_max:
            best_move = x
        
        # This undoes the search, so we don't need to worry about deep copies
        board.boarddata[x][y] = 0

    if best_move is None:
        best_move = board.random_move()

    return (maxval, best_move) 


def assignvalue(boardproxy): # Returns float('inf') for win, 0 otherwise.
    assignedval = 0
    xp = 0; yp = 0
    # Horizontal score
    while yp < 6:
        t = boardproxy[xp][yp]
        if boardproxy[xp][yp] == 0:
            xp += 1
        elif boardproxy[xp+1][yp] != t:
            xp += 1
        elif boardproxy[xp+2][yp] != t:
            xp += 1
        elif boardproxy[xp+3][yp] != t:
            xp += 1
        else:
            assignedval = float('inf')
            xp += 1   
        if xp > 3:
            xp = 0; yp += 1
    xp = 0; yp = 0
    # Vertical score
    while yp < 3:
        t = boardproxy[xp][yp]
        if boardproxy[xp][yp] == 0:
            xp += 1
        elif boardproxy[xp][yp+1] != t:
            xp += 1
        elif boardproxy[xp][yp+2] != t:
            xp += 1
        elif boardproxy[xp][yp+3] != t:
            xp += 1
        else:
            assignedval = float('inf')
            xp += 1
        if xp > 6:
            xp = 0; yp += 1
    xp = 0; yp = 0
    # Diagonal-right score
    while yp < 3:
        t = boardproxy[xp][yp]
        if boardproxy[xp][yp] == 0:
            xp += 1
        elif boardproxy[xp+1][yp+1] != t:
            xp += 1
        elif boardproxy[xp+2][yp+2] != t:
            xp += 1
        elif boardproxy[xp+3][yp+3] != t:
            xp += 1
        else:
            assignedval = float('inf')
            xp += 1
        if xp > 3:
            xp = 0; yp += 1
    xp = 3; yp = 0
    # Diagonal-left score
    while yp < 3:
        t = boardproxy[xp][yp]
        if boardproxy[xp][yp] == 0:
            xp += 1
        elif boardproxy[xp-1][yp+1] != t:
            xp += 1
        elif boardproxy[xp-2][yp+2] != t:
            xp += 1
        elif boardproxy[xp-3][yp+3] != t:
            xp += 1
        else:
            assignedval = float('inf')
            xp += 1
        if xp > 6:
            xp = 3; yp += 1
    return assignedval


def chips(tile):
    if tile == 1:
        return (CSI + "31m" + "○" + CSI+"30m")
    elif tile == -1:
        return (CSI + "32m" + "○" + CSI+"30m")
    else:
        return ' '

def dispboard(board):
    boarddata = board.boarddata
    # Display the board
    cls()
    if board.playerturn() == 1:
        player = CSI+"31m" + "Red" + CSI+"30m" + "'s turn  "
    else:
        player = CSI+"32m" + "Green" + CSI+"30m" + "'s turn"
    print player + "   ┌─┬─┬─┬─┬─┬─┬─┐"
    for y in range(6):
        print"               │%s│%s│%s│%s│%s│%s│%s│" % (
                chips(boarddata[0][y]), chips(boarddata[1][y]),
                chips(boarddata[2][y]), chips(boarddata[3][y]),
                chips(boarddata[4][y]), chips(boarddata[5][y]),
                chips(boarddata[6][y]))
        if y != 5:
            print"               ├─┼─┼─┼─┼─┼─┼─┤"
        else:
            print"               └─┴─┴─┴─┴─┴─┴─┘"

def boardmessage(p, ai, aicolor):
    if ai and (p == aicolor):
        print "\nComputer's turn; hit any key.\n"
    else:
        print ("Select column:  " + CSI+"34;1m" + "1 2 3 4 5 6 7    Q" +
               CSI+"30;21m" + "uit")
        print "\n"

class c4board():
    def __init__(self):
        self.boarddata = [[0 for x in xrange(6)] for x in xrange(7)]
    def set_data(self, data):
        self.boarddata = data
    def is_stalemate(self):
        """ Checks for stalemate by seeing if any legal moves exist"""
        toprow = [(self.boarddata[x][0]) for x in range(len(self.boarddata))]
        if 0 not in toprow:
            return True
        else:
            return False 
    def playerturn(self):
        bsum = 0
        for i in range(0,len(self.boarddata)):
            bsum += sum(self.boarddata[i])
        if bsum == 0:
            return 1 # Red = 1
        elif bsum == 1:
            return -1 # Green = -1
        else:
            raise Exception("Illegal bsum for board: ", repr(self.boarddata))
    def random_move(self):
        if self.is_stalemate():
            raise Exception("requested move when board is full!")
        else:
            choice = randint(1,7)
            while myboard.boarddata[choice-1][0] != 0:
                choice = randint(1,7)
        return choice
        
        
def _handle_stalemate():
    print "Stalemate!\n"
    print CSI+"0m" # resets color
    exit()

def _handle_winner(id):
    if id > 0:
        whowon = CSI+"31m" + "Red" + CSI+"30m"
    else:
        whowon = CSI+"32m" + "Green" + CSI+"30m"
    dispboard(myboard)
    print "%s is the winner!\n" % whowon
    print CSI+"0m" # resets color
    exit() 


def _getHumanMove():
    choice = 0
    while choice == 0:
        choice = getch()
        if choice == 'q' or choice == 'Q':
            _goodbye()
        try:
            choice = int(choice)
        except ValueError:
            choice = 0
        if choice < 1 or choice > 7 or myboard.boarddata[choice-1][0] != 0:
            choice = 0
    return choice

    
def play(ai, myboard, difficulty, aicolor):

    p = myboard.playerturn()
    dispboard(myboard)
    boardmessage(p, ai, aicolor)
    
    # Stalemate test
    if myboard.is_stalemate():
        _handle_stalemate()

    if ai and (p == aicolor):
        # I left this here s.t. human still has to press "enter" for computer to move
        choice = getch()
        choice = (minimax(difficulty, myboard)[1]) + 1
    else:
        choice = _getHumanMove()

    # TODO: I think that we want to check for valid move here?
    y = findy(myboard.boarddata, choice-1)
    myboard.boarddata[choice-1][y] = p

    # See if that's a win
    whowon = assignvalue(myboard.boarddata) * p

    if whowon == 0:
        play(ai, myboard, difficulty, aicolor)
    else:
        _handle_winner(whowon)


def _gameSelectUI():
    cls()
    print "** CONNECT FOUR!! **"
    print "\nWhat type of game would you like to play?"
    print "\n" + CSI+"1m" + "1)" + CSI+"21m" + " One player"
    print CSI+"1m" + "2)" + CSI+"21m" + " Two players"
    print "\n\n\n" + CSI+"1m" + "Q)" + CSI+"21m" + " Quit\n\n\n"
    choice = getch()

    if choice == "Q" or choice == "q":
        _goodbye()
    elif choice == '1':
        ai = True
        return ai    
    elif choice == '2':
        ai = False
        return ai    
    else:
        _gameSelectUI()


def _difficultySelectUI():
    cls()
    print "\nSelect a difficulty:"
    print "\n" + CSI+"1m" + "1)" + CSI+"21m" + " Child"
    print CSI+"1m" + "2)" + CSI+"21m" + " Normal"
    print CSI+"1m" + "3)" + CSI+"21m" + " Difficult"
    print "\n\n\n" + CSI+"1m" + "Q)" + CSI+"21m" + " Quit\n\n\n"
    choice = getch()
    if choice == "Q" or choice == "q":
        _goodbye()
    elif choice == '1':
        difficulty = 1
        return difficulty
    elif choice == '2':
        difficulty = 2
        return difficulty
    elif choice == '3':
        difficulty = 4
        return difficulty
    else:
        _difficultySelectUI()


def _colorSelectUI():
    cls()
    print ("\nWould you like to play as " + CSI+"31m" + "R" +
           CSI+"30m" + "ed or " + CSI+"32m" + "G" + CSI+"30m" + "reen?")
    print "\n(Red player goes first.)"
    print "\n\n\n" + CSI+"1m" + "Q)" + CSI+"21m" + " Quit\n\n\n"
    choice = getch()
    if choice == "Q" or choice == "q":
        _goodbye()
    elif choice == 'g' or choice == 'G':
        aicolor = 1
        return aicolor
    elif choice == 'r' or choice == 'R':
        aicolor = -1
        return aicolor
    else:
        _colorSelectUI()


def _goodbye():
        print "\nGoodbye!"
        print CSI+"0m" # resets color
        exit()
    
def intro():
    """ This function handles all of the game setup. Returns:
    * ai: True/False, whether ai is enabled
    * difficulty: {1, 2, 4} - difficulty level of AI. 0 if AI not enabled
    * aicolor: -1 (green), 1 (red) - color AI will play. -1 if AI not enabled"""
    useai = _gameSelectUI()
    if useai: 
        difficulty = _difficultySelectUI()
        aicolor = _colorSelectUI()
    else:
        difficulty = 0
        aicolor = -1
    return (useai, difficulty, aicolor)


if __name__=="__main__":

    useai, difficulty, aicolor = intro()
    myboard = c4board()    
    play(useai, myboard, difficulty, aicolor)
    
    # TODO: I don't think that the program ever reaches this point ... ?
    print CSI+"0m" # resets color
