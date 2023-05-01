import tkinter as tk
from chess_launcher import ChessLauncher
from tkinter import ttk
from config import *

window = tk.Tk()
window.resizable(False, False)
window.title('chess launcher')
window.geometry(WINDOW_SIZE)
chess_launcher: ChessLauncher = ChessLauncher()

single_player_button = ttk.Button(master=window, text='single player', command=chess_launcher.launch_single_player)

single_player_button.pack()

window.mainloop()
