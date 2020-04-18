from tkinter import *
from PIL import Image
from PIL import ImageTk

pixel_width = 10


def draw_running_man(cor_x, cor_y, photo, canvas):
    canvas.create_image(cor_y*pixel_width+1+18, cor_x*pixel_width+1+18, image=photo)


def draw_fill_box(cor_x, cor_y, canvas):
    canvas.create_rectangle(cor_y*pixel_width+1, cor_x*pixel_width+1, cor_y*pixel_width+pixel_width-1, cor_x*pixel_width+pixel_width-1, outline="blue", fill="blue")


def draw_blocks(cor_x, cor_y, canvas):
    canvas.create_rectangle(cor_y*pixel_width+1, cor_x*pixel_width+1, cor_y*pixel_width+pixel_width-1, cor_x*pixel_width+pixel_width-1, outline="black", fill="black")


def erase_fill_box(cor_x, cor_y, canvas):
    canvas.create_rectangle(cor_y*pixel_width+1, cor_x*pixel_width+1, cor_y*pixel_width+pixel_width-1, cor_x*pixel_width+pixel_width-1, outline="white", fill="white")


def draw_grid(rows, cols, blocks, canvas):
    start_x = 0
    start_y = 0
    for i in range(rows+1):
        canvas.create_line(start_x, start_y+i*pixel_width, start_x + cols*pixel_width, start_y + i*pixel_width)
    for i in range(cols+1):
        canvas.create_line(start_x + i*pixel_width, start_y, start_x + i*pixel_width, start_y + rows*pixel_width)
    for b in blocks:
        draw_blocks(b[0], b[1], canvas)


def draw_only_blocks(rows, cols, blocks, canvas):
    start_x = 0
    start_y = 0
    for b in blocks: draw_blocks(b[0], b[1], canvas)


class Animate:
    def __init__(self, grid):
        self.rows = grid.rows
        self.cols = grid.cols
        self.blocks = grid.blocks
        self.target = grid.finish

    def show(self, pos_list):
        root = Tk()
        root.title("Time Delayed")
        cw = 800  # canvas width
        ch = 650  # canvas height
        canvas = Canvas(root, width=cw, height=ch, background="white")
        canvas.grid(row=0, column=0)
        draw_grid(self.rows, self.cols, self.blocks, canvas)
        house = ImageTk.PhotoImage(Image.open("./house37.jpeg"))
        canvas.create_image(self.target[1] * pixel_width + 1 + 18, self.target[0] * pixel_width + 1 + 18, image=house)
        #draw_fill_box(self.target[0], self.target[1], canvas)
        #photo = PhotoImage(file="./run_right_37.png")
        photo = ImageTk.PhotoImage(Image.open("run_right_37.png"))
        #draw_running_man(2,2, photo, canvas)

        cycle_period = 500  # time between fresh positions of the ball
        for pos in pos_list:
            #print(pos)
            draw_running_man(pos[0], pos[1], photo, canvas)
            #draw_fill_box(pos[0], pos[1], canvas)
            canvas.update()
            canvas.after(cycle_period)
            erase_fill_box(pos[0], pos[1], canvas)
        if pos_list[-1] == self.target:
            chill = ImageTk.PhotoImage(Image.open("./chill37.jpeg"))
            canvas.create_image(self.target[1] * pixel_width + 1 + 18, self.target[0] * pixel_width + 1 + 18, image=chill)
        else:
            draw_fill_box(pos_list[-1][0], pos_list[-1][1], canvas)
        root.mainloop()


def draw_prey(cor_x, cor_y, canvas):
    canvas.create_rectangle(cor_y*pixel_width+1, cor_x*pixel_width+1, cor_y*pixel_width+pixel_width-1, cor_x*pixel_width+pixel_width-1, outline="red", fill="red")
    
    
def draw_seeker_body(body, canvas):
    for cor_x, cor_y in body[1]:
        canvas.create_rectangle(cor_y * pixel_width + 1, cor_x * pixel_width + 1, cor_y * pixel_width + pixel_width - 1,
                                cor_x * pixel_width + pixel_width - 1, outline="blue", fill="blue")
    cor_x = body[0][0]
    cor_y = body[0][1]
    canvas.create_rectangle(cor_y * pixel_width + 1, cor_x * pixel_width + 1, cor_y * pixel_width + pixel_width - 1,
                            cor_x * pixel_width + pixel_width - 1, outline="green", fill="green")


def erase_seeker_body(body, canvas):
    for cor in body[1]:
        cor_y = cor[0]
        cor_x = cor[1]
        canvas.create_rectangle(cor_x * pixel_width + 1, cor_y * pixel_width + 1, cor_x * pixel_width + pixel_width - 1,
                                cor_y * pixel_width + pixel_width - 1, outline="white",
                                fill="white")
    cor_x = body[0][0]
    cor_y = body[0][1]
    canvas.create_rectangle(cor_y * pixel_width + 1, cor_x * pixel_width + 1, cor_y * pixel_width + pixel_width - 1,
                            cor_x * pixel_width + pixel_width - 1, outline="white", fill="white")


def erase_prey(pos, canvas):
    cor_x = pos[0]
    cor_y = pos[1]
    canvas.create_rectangle(cor_y * pixel_width + 1, cor_x * pixel_width + 1, cor_y * pixel_width + pixel_width - 1,
                            cor_x * pixel_width + pixel_width - 1, outline="white", fill="white")


class AnimateGameBoard:
    def __init__(self, game):
        self.game = game

    def show(self, pos_list):
        root = Tk()
        root.title("Game of Seeker")
        cw = 800  # canvas width
        ch = 650  # canvas height
        canvas = Canvas(root, width=cw, height=ch, background="white")
        canvas.grid(row=0, column=0)
        #draw_grid(self.game.rows, self.game.cols, self.game.blocks, canvas)
        draw_only_blocks(self.game.rows, self.game.cols, self.game.blocks, canvas)

        cycle_period = max(1, int(500/len(pos_list)) ) # time between fresh positions of the ball
        for pos in pos_list:
            # print(pos)
            draw_seeker_body(pos[0], canvas)
            draw_prey(pos[1][0], pos[1][1], canvas)
            # draw_fill_box(pos[0], pos[1], canvas)
            canvas.update()
            canvas.after(cycle_period)
            erase_seeker_body(pos[0], canvas)
            erase_prey(pos[1], canvas)
        draw_seeker_body(pos_list[-1][0], canvas)
        draw_prey(pos_list[-1][1][0], pos_list[-1][1][1], canvas)

        #draw_fill_box(pos_list[-1][0], pos_list[-1][1], canvas)
        root.mainloop()

    def show_exact(self, pos_list):
        root = Tk()
        root.title("Game of Seeker")
        cw = 800  # canvas width
        ch = 650  # canvas height
        canvas = Canvas(root, width=cw, height=ch, background="white")
        canvas.grid(row=0, column=0)
        #draw_grid(self.game.rows, self.game.cols, self.game.blocks, canvas)
        draw_only_blocks(self.game.rows, self.game.cols, self.game.blocks, canvas)

        cycle_period = max(1, int(500/len(pos_list)) ) # time between fresh positions of the ball
        for s, p in zip(pos_list[0], pos_list[1]):
            # print(pos)
            s_rep = s.get_representation()
            p_rep = p.get_pos()
            draw_seeker_body(s_rep, canvas)
            draw_prey(p_rep[0], p_rep[1], canvas)
            # draw_fill_box(pos[0], pos[1], canvas)
            canvas.update()
            canvas.after(cycle_period)
            erase_seeker_body(s_rep, canvas)
            erase_prey(p_rep, canvas)
        s_rep = pos_list[0][-1].get_representation()
        p_rep = pos_list[1][-1].get_pos()
        draw_seeker_body(s_rep, canvas)
        draw_prey(p_rep[0], p_rep[1], canvas)

        #draw_fill_box(pos_list[-1][0], pos_list[-1][1], canvas)
        root.mainloop()
