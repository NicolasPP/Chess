import functools
import tkinter as tk
from ttkbootstrap import ttk

window = tk.Tk()
frame_container = ttk.Frame(window)

canvas_container = tk.Canvas(frame_container, height=100)
frame2 = ttk.Frame(canvas_container)
my_scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas_container.yview)
# will be visible if the frame2 is to to big for the canvas
canvas_container.create_window((0, 0), window=frame2, anchor='nw')


def func(name):
    print(name)


my_list = ['item1', 'item2', 'item3']

for item in my_list:
    button = ttk.Button(frame2, text=item, command=functools.partial(func, item))
    button.pack()

# update frame2 height so it's no longer 0 ( height is 0 when it has just been created )
frame2.update()
canvas_container.configure(yscrollcommand=my_scrollbar.set, scrollregion="0 0 0 %s" % frame2.winfo_height())
# the scrollregion must be the size of the frame inside it,
# in this case "x=0 y=0 width=0 height=frame2 height"
# width 0 because we only scroll vertically so don't mind about the width.

canvas_container.pack(side=tk.LEFT)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

frame_container.pack()
window.mainloop()
