from tkinter import *
from threading import Thread
from threading import Condition
import seeker

condition = Condition()


class Game(Thread):
    def __init__(self, arena, movements, player_positions, rounds):
        Thread.__init__(self)
        self.arena = arena
        self.movements = movements
        self.player_positions = player_positions
        self.finished = False
        self.rounds = rounds

    def play(self):
        print("Catching a Moving Prey")
        # CS - Start position
        condition.acquire()
        self.player_positions.append((self.arena.seeker.get_representation(), self.arena.prey))
        condition.notify()
        condition.release()
        # CS

        episode_len = self.arena.rows * self.arena.cols
        episode_num = 300000

        # Initial learning
        self.arena.q_learning(0.6, 0.9, 0.5, episode_len, episode_num)
        self.arena.seeker.reset()


        if self.arena.seeker.caught(self.arena.prey): return
        old_seeker = self.arena.seeker
        episode_num = max(1, int(episode_num/500))

        for r in range(1, self.rounds):
            prey = self.arena.eval_one_step_prey(old_seeker, self.arena.prey)
            print("P " + str(self.arena.prey) + " ~> " + str(prey))
            new_seeker = self.arena.eval_one_step_seeker(old_seeker, self.arena.prey)
            old_seeker = new_seeker
            # CS
            condition.acquire()
            self.player_positions.append((new_seeker.get_representation(), prey))
            condition.notify()
            condition.release()
            # CS

            if new_seeker.caught(prey): break

            if prey != self.arena.prey:
                epsilon = 1 - 0.4*(r/rounds)
                self.arena.prey = prey
                self.arena.q_learning(epsilon, 0.9, 0.5, episode_len, episode_num)
            self.arena.seeker = new_seeker

        self.finished = True

    def catch_prey(self):
        print ("Catching a Stationary Prey")
        episode_len = (self.arena.rows * self.arena.cols)
        episode_num = 30000
        self.arena.q_learning(0.6, 0.9, 0.5, episode_len, episode_num)
        self.arena.seeker.reset()
        self.movements.append(self.arena.eval_control(episode_len))

        for i in range(5):
            start = self.arena.seeker.get_random(self.arena.rows, self.arena.cols, self.arena.is_valid_position)
            if start: self.arena.seeker = start

            condition.acquire()
            self.movements.append(self.arena.eval_control(episode_len))
            condition.notify()
            condition.release()
        print("Finished.")
        self.finished = True

    def run(self):
        #self.play()
        self.catch_prey()

    def is_finished(self):
        return self.finished


class AnimateGameBoard:
    def draw_block(self, cor_x, cor_y, canvas, color):
        canvas.create_rectangle(cor_y*self.pw+1, cor_x*self.pw+1, cor_y*self.pw+self.pw-1, cor_x*self.pw+self.pw-1, outline=color, fill=color)
    
    def draw_prey(self, cor, canvas):
        cor_x = cor[0]
        cor_y = cor[1]
        self.draw_block(cor_x, cor_y, canvas, color="red")

    def draw_seeker_body(self, body, canvas):
        for cor_x, cor_y in body[1]:
            self.draw_block(cor_x, cor_y, canvas, "blue")
        cor_x = body[0][0]
        cor_y = body[0][1]
        self.draw_block(cor_x, cor_y, canvas, "green")

    def erase_seeker_body(self, body, canvas):
        for cor_x, cor_y in body[1]:
            self.draw_block(cor_x, cor_y, canvas, "white")
        cor_x = body[0][0]
        cor_y = body[0][1]
        self.draw_block(cor_x, cor_y, canvas, "white")

    def draw_only_blocks(self, rows, cols, blocks, canvas):
        start_x = 0
        start_y = 0
        for b in blocks: self.draw_block(b[0], b[1], canvas, color="black")

    def __init__(self, arena):
        self.arena = arena
        self.pw = 10

    def show_seeker(self, is_finished, canvas, movements):
        def pred():
            return is_finished() or movements
        while True:
            condition.acquire()
            if not movements:
                print("No movement")
                condition.wait_for(pred)
            if not movements:
                condition.release()
                break

            movement = movements.pop(0)
            condition.release()

            cycle_period = max(1, int(500 / len(movement)))  # time between fresh positions of the ball
            print ("Rendering Movement.")
            for pos in movement:
                # print(pos)
                self.draw_seeker_body(pos, canvas)
                # draw_fill_box(pos[0], pos[1], canvas)
                canvas.update()
                canvas.after(cycle_period)
                self.erase_seeker_body(pos, canvas)
            self.draw_seeker_body(movement[-1], canvas)

    def render_players(self, canvas, old_pos, new_pos):
        if old_pos:
            self.draw_block(old_pos[1][0], old_pos[1][1], canvas, "white")
            self.erase_seeker_body(old_pos[0], canvas)
        self.draw_seeker_body(new_pos[0], canvas)
        self.draw_prey(new_pos[1], canvas)
        canvas.update()

    def show_play(self, is_finished, canvas, player_positions, rounds):
        player_pos = None
        index = 0
        def stop_waiting():
            return is_finished() or len(player_positions) > index

        for i in range (rounds):
            condition.acquire()
            if len(player_positions) <= index:
                condition.wait_for(stop_waiting)

            if is_finished() and len(player_positions) <= index:
                condition.release()
                return

            new_pos = player_positions[index]
            index = index + 1
            condition.release()

            # Draw new
            self.render_players(canvas, player_pos, new_pos)
            canvas.pack()

            player_pos = new_pos

    def show(self, rounds):
        root = Tk()
        root.title("Game of Seeker")
        cw = 800  # canvas width
        ch = 650  # canvas height
        canvas = Canvas(root, width=cw, height=ch, background="white")
        canvas.grid(row=0, column=0)
        # draw_grid(self.game.rows, self.game.cols, self.game.blocks, canvas)
        self.draw_only_blocks(self.arena.rows, self.arena.cols, self.arena.blocks, canvas)
        self.draw_prey(self.arena.prey, canvas)

        print ("Starting Game...")
        movements = []
        player_positions = []

        game = Game(self.arena, movements, player_positions, rounds)
        game.start()
        self.show_seeker(game.is_finished, canvas, movements)
        root.mainloop()
        game.join()


rows = 30
cols = 40
rounds =100#cols*rows
arena = seeker.GameBoard(rows, cols, (4, 4), (int(rows/2), int(cols/2)))
AnimateGameBoard(arena).show(rounds)
