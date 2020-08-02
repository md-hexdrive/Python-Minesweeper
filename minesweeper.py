import numpy as np
import tkinter as tk
from tkinter import font
import random

CLEAR_SPACE = 0
MINE = 9

"""
Customized button subclass that serves as a point on the game board

"""
class MineButton(tk.Button):
    def __init__(self, root, posx, posy, board):
        super(MineButton, self, ).__init__(root, command = self.click, width=4, height=2,
                                           font=font.Font(family="Helvetica", size=12, weight="bold"),
                                           fg="red")
        self.root = root
        self.posx = posx
        self.posy = posy
        self.board = board
        self.revealed = False
        self.flagged = False
        self.bind('<Button-3>', self.flag)
    
    """
    click() what happens when this button is clicked
    """
    def click(self):
    def flag(self, event):
        print("flagging")
        if not self.revealed:
            if self.flagged:
                self.flagged = False
                self.config(state=tk.NORMAL, #image = self.root.flagImage,
                            disabledforeground="#345678", text="")
            else:
                self.flagged = True
                self.config(state=tk.DISABLED, #image = self.root.flagImage,
                                disabledforeground="#345678", text="F")
        
        if not self.revealed and self.root.game.game_running:
            self.revealed = True
            contents = self.root.game.board[self.posx, self.posy]
#             if contents == 0:
#                 contents = self.root.game.num_of_adjacent_mines((self.posx, self.posy))
#                 print("Number of adjacent mines:", contents)
#                 if contents == 0:
#                     buttonsToCheck = self.root.buttonArray[max(0, self.posx-1) : min(self.posx+2, self.root.game.board_width)][max(0, self.posy-1) : min(self.posy+2, self.root.game.board_height)]
#                     for i in range(len(buttonsToCheck)):
#                         for j in range(len(buttonsToCheck)):
#                             if not buttonsToCheck[i][j].revealed:
#                                 buttonsToCheck[i][j].click()
            if contents == MINE:
                self.root.game.mine_found((self.posx, self.posy))
                if self.root.game.game_running:
                    self.config(state=tk.DISABLED, fg="#345678", bg='navyblue', text="M")
                else:
                    self.config(state=tk.DISABLED, fg="#345678", bg='darkred', text="M")
                    self.root.blow_everything_up()
            else:
                self.config(state=tk.DISABLED, fg="#345678", bg='gray64', text=str(contents))
                if contents == CLEAR_SPACE:
                    self.root.reveal_spaces(self.root.game.pool_fill((self.posx, self.posy)))
            
            
        print("Button: ", self.posx, self.posy, " was pressed")

"""
The game's GUI class
"""
class MineSweeperGUI(tk.Label):
    def __init__(self, root, board_size = (7,7) , mine_count=10):
        super(MineSweeperGUI, self).__init__(root)
        self.board_size = board_size
        self.mine_count = mine_count
        self.game = Minesweeper(board_size, mine_count)
        
        self.buttonArray = []
        for i in range(self.game.board_width):
            self.buttonArray.append([])
            for j in range(self.game.board_height):
                newButton = MineButton(self, i, j, self.game.board)
                self.buttonArray[i].append(newButton)
                newButton.grid(column = i, row = j)
        self.pack()
        root.mainloop()
    
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
            self.buttonArray[pos[0]][pos[1]].click()
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
        
        if self.board[pos] != 0:
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
                if self.is_inside_board(pos) and not pos in spaces_to_reveal:
                    if not self.is_a_mine(pos):
                        spaces_to_reveal.append(pos)
                        if self.is_empty_space(pos):
                            empty_spaces.append(pos)
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
    def place_mines(self):
        
        for i in range(self.mine_count+1):
            x_cords = random.choice(range(self.board_width))
            y_cords = random.choice(range(self.board_height))
            
            self.mine_positions.append((x_cords, y_cords)) 
        
        for pos in self.mine_positions:
            self.board[pos] = MINE


if __name__ == '__main__':
    game = Minesweeper((7, 7), 10)
    print(game.board)
    gui_game = MineSweeperGUI(root=tk.Tk())
    