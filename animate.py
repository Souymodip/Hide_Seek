from tkinter import *
from threading import Thread
from threading import Condition
import seeker
import exact_learning
import shapes
import math

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

        episode_len = 100#self.arena.rows * self.arena.cols
        episode_num = 5000

        # Initial learning
        old_seeker = self.arena.seeker
        old_prey = shapes.Blob(self.arena.prey)

        seeker_Q = exact_learning.q_learning_seeker(self.arena, self.arena.seeker, self.arena.prey, 0.6,0.9, 0.5, episode_len, episode_num, True)
        prey_Q = exact_learning.q_learning_prey(self.arena, self.arena.seeker, self.arena.prey, 0.6, 0.9, 0.5, episode_len, episode_num, True)
        #self.arena.q_learning(0.6, 0.9, 0.5, episode_len, episode_num)

        episode_num = max(1, int(episode_num/5))
        for r in range(1, self.rounds):
            print("Round " + str(r))

            seeker_move = exact_learning.eval_seeker(self.arena, seeker_Q, old_seeker, old_prey.get_pos(), 4)
            prey_move = exact_learning.eval_prey(self.arena, prey_Q, old_seeker, old_prey.get_pos(), 1)

            for s, p in zip(seeker_move, prey_move):
                condition.acquire()
                self.player_positions.append((s.get_representation(), p.get_pos()))
                condition.notify()
                condition.release()

            if len(seeker_move) > len(prey_move):
                for i in range(len(prey_move), len(seeker_move)):
                    condition.acquire()
                    self.player_positions.append((seeker_move[i].get_representation(), prey_move[-1].get_pos()))
                    condition.notify()
                    condition.release()

            if len(prey_move) > len(seeker_move):
                for i in range(len(seeker_move), len(prey_move)):
                    condition.acquire()
                    self.player_positions.append((seeker_move[-1].get_representation(), prey_move[i].get_pos()))
                    condition.notify()
                    condition.release()

            old_seeker = seeker_move[-1]
            old_prey = prey_move[-1]

            if old_seeker.caught(old_prey.get_pos()):
                print("Caught")
                break

            epsilon = 1 - 0.4*(r/rounds)
            learning = 0.5 + 0.5*math.sqrt(r/rounds)
            seeker_Q = exact_learning.q_learning_seeker(self.arena, old_seeker, old_prey.get_pos(), 0.6, 0.9, learning, episode_len, episode_num, False)
            prey_Q = exact_learning.q_learning_prey(self.arena, old_seeker, old_prey.get_pos(), 0.6, 0.9, learning, episode_len, episode_num, False)
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
        self.play()
        #self.catch_prey()

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
                self.draw_seeker_body(pos[0], canvas)
                self.draw_prey(pos[1], canvas)
                # draw_fill_box(pos[0], pos[1], canvas)
                canvas.update()
                canvas.after(cycle_period)
                self.erase_seeker_body(pos[0], canvas)
                self.draw_block(pos[1][0], pos[1][1], canvas, "white")
            self.draw_seeker_body(movement[-1][0], canvas)
            self.draw_prey(movement[-1][1], canvas)

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
        print("Gui Main loop....")
        while True:
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
        self.show_play(game.is_finished, canvas, player_positions, rounds)
        game.join()
        root.mainloop()


rows = 30
cols = 40
rounds = 100#cols*rows
arena = seeker.GameBoard(rows, cols, (4, 4), (int(rows/2), int(cols/2)))
AnimateGameBoard(arena).show(rounds)
