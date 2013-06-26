# coding=utf-8
import pdb
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from random import randint

CSI="\x1B["
reset=CSI+"m"
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

def winstate(board):
    if '0' not in str(board):
        return 2 # stalemate
    elif assignvalue(board) != 0:
        return 1 # win
    else:
        return 0 # not end state

def findy(board, x):
    y = 5
    while board[x][y] != 0:
        y -= 1
    return y

def minimax(difficulty, boardproxy, depth=0):    
    """
    For every column that isn't filled up, the function will test a board with
    that move having been made.  It takes the value from the assignvalue()
    function (0 or 'inf'), and compares it to the negative value of the same
    function run recursively until either a winning move (or stalemate) is
    found, or the maximum depth is reached.  The higher of the two compared
    values is then compared with the next recursed function upwards, until
    the top of the recursion tree is reached.  Once this occurs, the column
    associated with that optimal move is returned.  If no move is optimal,
    the default '7' value should be returned, which the play() function
    will interpret as choosing a column at random.
    """

#problem seems to be that when redwin value == greenwin value, it cancels out
    p = playerturn(boardproxy)
    maxval = -float('inf')
    best_move = 7 

    for x in range(len(boardproxy)):
        if boardproxy[x][0] != 0:
            continue
        y = findy(boardproxy, x)
        boardproxy[x][y] = p 
        depth += 1

        if depth == difficulty or winstate(boardproxy) != 0:
            maxval = assignvalue(boardproxy)
            boardproxy[x][y] = 0
            depth -= 1
            return (maxval, x) # 7 will turn into randint
        
        prev_max = maxval
        maxval = max(maxval, -1 * minimax(difficulty, boardproxy, depth)[0])
        if maxval > prev_max:
            best_move = x
        
        boardproxy[x][y] = 0
        depth -= 1

    return (maxval, best_move) 

def playerturn(board):
    bsum = 0
    for i in range(0,6):
        bsum += sum(board[i])

    if bsum == 0:
        return 1 # Red = 1
    else:
        return -1 # Green = -1

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

def dispboard(boarddata):
    # Display the board
    cls()
    if playerturn(boarddata) == 1:
        player = CSI+"31m" + "Red" + CSI+"30m" + "'s turn  "
    else:
        player = CSI+"32m" + "Green" + CSI+"30m" + "'s turn"
    oldboard = boarddata
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
    boarddata = oldboard

def boardmessage(p, ai, aicolor):
    if ai and (p == aicolor):
        print "\nComputer's turn; hit any key.\n"
    else:
        print ("Select column:  " + CSI+"34;1m" + "1 2 3 4 5 6 7    Q" +
               CSI+"30;21m" + "uit")
        print "\n"
    
def play(ai, boarddata, difficulty, aicolor):
    p = playerturn(boarddata)
    dispboard(boarddata)
    boardmessage(p, ai, aicolor)
    
    # Stalemate test
    toprow = [(boarddata[x][0]) for x in range(len(boarddata))]
    if 0 not in toprow:
        print "Stalemate!\n"
        print CSI+"0m" # resets color
        exit()
            
    choice = 0
    while choice == 0:
        choice = getch()
        if ai and (p == aicolor):
            choice = (minimax(difficulty, boarddata)[1]) + 1
        else:     
            if choice == 'q' or choice == 'Q':
                print "\n"
                print CSI+"0m" # resets color
                exit()
            try:
                choice = int(choice)
            except ValueError:
                choice = 0
            if choice < 1 or choice > 7 or boarddata[choice-1][0] != 0:
                choice = 0
                
        if choice == 8:
            choice = randint(1,7)
            while boarddata[choice-1][0] != 0:
                choice = randint(1,7)
                
                
    y = findy(boarddata, choice-1)
    boarddata[choice-1][y] = p
    # See if that's a win
    whowon = assignvalue(boarddata) * p
    if whowon == 0:
        play(ai, boarddata, difficulty, aicolor)
    else:
        if whowon > 0:
            whowon = CSI+"31m" + "Red" + CSI+"30m"
        else:
            whowon = CSI+"32m" + "Green" + CSI+"30m"
        dispboard(boarddata)
        print "%s is the winner!\n" % whowon
        print CSI+"0m" # resets color
        exit() 

    
def boardsetup():
    # board is 7x6 matrix
    boarddata = [[0 for x in xrange(6)] for x in xrange(7)]
    return boarddata
    
def intro():
    cls()
    aicolor = 0
    print "** CONNECT FOUR!! **"
    print "\nWhat type of game would you like to play?"
    print "\n" + CSI+"1m" + "1)" + CSI+"21m" + " One player"
    print CSI+"1m" + "2)" + CSI+"21m" + " Two players"
    print "\n\n\n" + CSI+"1m" + "Q)" + CSI+"21m" + " Quit\n\n\n"
    choice = getch()
    if choice == "Q" or choice == "q":
        print "\nGoodbye!"
        print CSI+"0m" # resets color
        exit()
    elif choice == '1':
        ai = True
        cls()
        print "\nSelect a difficulty:"
        print "\n" + CSI+"1m" + "1)" + CSI+"21m" + " Child"
        print CSI+"1m" + "2)" + CSI+"21m" + " Normal"
        print CSI+"1m" + "3)" + CSI+"21m" + " Difficult"
        print "\n\n\n" + CSI+"1m" + "Q)" + CSI+"21m" + " Quit\n\n\n"
        choice = getch()
        if choice == "Q" or choice == "q":
            print "\nGoodbye!"
            print CSI+"0m" # resets color
            exit()
        elif choice == '1':
            difficulty = 1
        elif choice == '2':
            difficulty = 2
        elif choice == '3':
            difficulty = 4
        else:
            intro()
            
        cls()
        print ("\nWould you like to play as " + CSI+"31m" + "R" +
               CSI+"30m" + "ed or " + CSI+"32m" + "G" + CSI+"30m" + "reen?")
        print "\n(Red player goes first.)"
        print "\n\n\n" + CSI+"1m" + "Q)" + CSI+"21m" + " Quit\n\n\n"
        choice = getch()
        if choice == "Q" or choice == "q":
            print "\nGoodbye!"
            print CSI+"0m" # resets color
            exit()
        elif choice == 'g' or choice == 'G':
            aicolor = 1
        elif choice == 'r' or choice == 'R':
            aicolor = -1
        else:
            intro()
    elif choice == '2':
        difficulty = 0
        ai = False
        aicolor = -1
    else:
        intro()
    boarddata = boardsetup()
    play(ai, boarddata, difficulty, aicolor)


cls()
intro()


print CSI+"0m" # resets color
