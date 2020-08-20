import numpy as np
import tkinter as tk
from tkinter import font
import random

import time
CLEAR_SPACE = 0
MINE = 9


"""
Main GUI class

"""
class MineGameGUI(tk.Tk):
    def __init__(self, board_size=(11, 11), n_mines=10):
        super(MineGameGUI, self).__init__()
        self.title("Minesweeper")
        self.menu = tk.Menu(self)
        
        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label="New Game", command=MineGameGUI)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        
        self.menu.add_command(label="Help", command=self.help_window)
        self.config(menu=self.menu)
        
        self.game_gui = MineSweeperGUI(root=self, board_size=board_size, mine_count=n_mines)
        self.game_gui.pack()
    
    def help_window(self):
        help_win = tk.Toplevel()
        help_win.title("About")
        label = tk.Label(help_win, text="""Custom Minesweeper 1.0 \nWritten by: MD-Hexdrive""")
        label.pack(padx=10, pady=10)
        
        button = tk.Button(help_win, text="Ok", width=10, command=help_win.destroy)
        button.pack(padx=10, pady=10)

"""
Customized button subclass that serves as a point on the game board

"""
class MineButton(tk.Button):
    def __init__(self, root, posx, posy, board):
        super(MineButton, self).__init__(root, command = self.click, width=4, height=2,
                                           font=font.Font(family="Helvetica", size=12, weight="bold"),
                                           fg="red")
        self.root = root
        self.posx = posx
        self.posy = posy
        self.board = board
        self.revealed = False
        self.flagged = False
        self.bind('<Button-3>', self.flag)
    
    def flag(self, event):
        
        if not self.revealed and self.root.game.game_running:
            if self.flagged:
                self.flagged = False
                self.config(state=tk.NORMAL, #image = self.root.flagImage,
                            disabledforeground="#345678", text="")
            else:
                self.flagged = True
                self.config(state=tk.DISABLED, #image = self.root.flagImage,
                                disabledforeground="#345678", text="F")
        
    def reveal_contents(self, clicked=False):
        if not self.revealed and self.root.game.game_running:
            self.revealed = True
            contents = self.root.game.board[self.posx, self.posy]

            if contents == MINE:
                self.root.game.mine_found((self.posx, self.posy))
                if self.root.game.game_running:
                    self.config(state=tk.DISABLED, #image = self.root.flagImage,
                                disabledforeground="#345678", bg='navyblue', text="M")
                else:
                    self.config(state=tk.DISABLED, disabledforeground="#345678", bg='darkred', text="M")
                    self.root.blow_everything_up()
            else:
                self.config(state=tk.DISABLED, disabledforeground="#345678", bg='gray64', text=str(contents))
                if contents == CLEAR_SPACE:
                    self.config(state=tk.DISABLED, disabledforeground="#345678", bg='gray64', text="")
                    if clicked:
                        self.root.reveal_spaces(self.root.game.pool_fill((self.posx, self.posy)))
            
            
        print("Board Position: ", self.posx, self.posy, " was accessed")
    """
    click() what happens when this button is clicked
    """
    def click(self):
        self.reveal_contents(clicked=True)

"""
The game's GUI class
"""
class MineSweeperGUI(tk.Label):
    def __init__(self, root, board_size = (7,7) , mine_count=10):
        super(MineSweeperGUI, self).__init__(root)
        self.board_size = board_size
        self.mine_count = mine_count
        self.game = Minesweeper(board_size, mine_count)
        
        self.flagImage = tk.PhotoImage(file = r"C:\Users\Paul\Documents\GitHub\Python-Minesweeper\MinesweeperFlag.png").subsample(2,2)
        
        self.buttonArray = []
        for i in range(self.game.board_width):
            self.buttonArray.append([])
            for j in range(self.game.board_height):
                newButton = MineButton(self, i, j, self.game.board)
                self.buttonArray[i].append(newButton)
                newButton.grid(column = i, row = j)
    
    def blow_everything_up(self): # game over, the user lost
        for i in range(self.game.board_width):
            for j in range(self.game.board_height):
                if not self.buttonArray[i][j].revealed:
                    if self.game.board[i,j] == MINE:
                        self.buttonArray[i][j].config(state=tk.DISABLED, fg="#345678", bg='navyblue', text="M")
                    else:
                        self.buttonArray[i][j].config(state=tk.DISABLED)
        #self.pack_forget()
    def reveal_spaces(self, spaces):
        for pos in spaces:
            self.buttonArray[pos[0]][pos[1]].reveal_contents(clicked=False)
    
"""
The class that handles the game's logic
"""
class Minesweeper:
    """
    Create a new minesweeper game with a specific board size and number of mines
    """
    def __init__(self, board_size, mine_count):
        self.board_width = board_size[0]
        self.board_height = board_size[1]
        self.board = np.zeros((self.board_width, self.board_height), dtype=np.int32)
        self.mine_count = mine_count
        self.mine_positions = []
        self.fill_board()
        self.found_mine = False
        self.game_running = True
    
    """
    Fill the board with with data (place the mines, and put the number of mines adjacent to
    a board position in that position)
    """
    def fill_board(self):
        self.place_mines()
        for i in range(self.board_width):
            for j in range(self.board_height):
                if self.board[i,j] == MINE:
                    continue
                adjacent_mine_count = self.num_of_adjacent_mines((i,j))
                if adjacent_mine_count > 0:
                    self.board[i,j] = adjacent_mine_count
    
    """
    The first time the user clicks on a mine, they are saved, the second time it is game over
    """
    def mine_found(self, pos):
        if self.found_mine:
            self.game_over()
        else:
            self.found_mine = True
    def reveal_space(self, pos):
        if self.board[pos] == MINE:
            self.game_over()
        #if self
    
    def pool_fill(self, pos):
        spaces_to_reveal = []
        empty_spaces = []
        free_space_count = 0
        board_copy = np.copy(self.board)
        if board_copy[pos] != 0:
            return spaces_to_reveal
        
        spaces_to_reveal = [pos]
        empty_spaces = [pos]
        free_space_count = 1
        
        while len(empty_spaces) > 0:
            curr_pos = empty_spaces[0]
            del empty_spaces[0]
            
            x = curr_pos[0]
            y = curr_pos[1]

            up = x, y + 1
            down = x, y - 1
            left = x - 1, y
            right = x + 1, y
            
            up_left = x-1, y+1
            up_right = x+1, y+1
            down_left = x-1, y-1
            down_right = x+1, y-1
            
            next_positions = [up, down, left, right, up_left, up_right, down_left, down_right]
            for pos in next_positions:
                if self.is_inside_board(pos) and not (pos in spaces_to_reveal) and not self.is_a_mine(pos):
                    
                    spaces_to_reveal.append(pos)
                    if self.is_empty_space(pos):
                            empty_spaces.append(pos)
           
                        
        print(board_copy)
        return spaces_to_reveal
    
    # does this space contain a mine?
    def is_a_mine(self, pos):
        if self.board[pos] == MINE:
            return True
        else:
            return False
    
    # is this board position empty space, i.e., no mines inside it or directly adjacent to it?
    def is_empty_space(self, pos): 
        if self.board[pos] == CLEAR_SPACE:
            return True
        else:
            return False
    # is this position/point located inside the board limits?
    def is_inside_board(self, pos):
        if pos[0] in range(0, self.board_width) and pos[1] in range(0, self.board_height):
            return True
        else:
            return False
    #def reveal_surroundings(self, pos):
    
    """
    How many mines are adjacent to this position?
    """
    def num_of_adjacent_mines(self, pos):
        area = self.board[max(pos[0]-1, 0) : min(pos[0]+2, self.board_width),
                          max(pos[1]-1, 0) : min(pos[1]+2, self.board_height)]
        mine_count = np.count_nonzero(area == MINE)
        return mine_count
    
    def game_over(self):
        self.game_running = False
    
    """
    Place mines in random positions around the board
    """
    def place_mines(self):
        
        while len(self.mine_positions) < self.mine_count:
            
            x_cords = random.choice(range(self.board_width))
            y_cords = random.choice(range(self.board_height))
            pos = (x_cords, y_cords)
            if pos in self.mine_positions:
                continue
            self.mine_positions.append((x_cords, y_cords)) 
        
        for pos in self.mine_positions:
            self.board[pos] = MINE


if __name__ == '__main__':
    #game = Minesweeper((11, 11), 10)
    #print(game.board)
    #gui_game = MineSweeperGUI(root=MineGameGUI(), board_size=(11, 11), mine_count=10)
    gui_game = MineGameGUI()
    #print(gui_game.game.board)