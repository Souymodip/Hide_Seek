import random
import Draw
import itertools


class Grid:
    def probabilistic_blocks(self):
        b = set()
        for y in range(self.rows):
            for x in range(self.cols):
                if (y, x) == self.finish or (y,x) == self.start: continue
                count = 1.2
                total = 0
                for i in range(3):
                    for j in range(3):
                        shift_y = y + (i - 1)
                        shift_x = x + (j - 1)
                        if 0 <= shift_x < self.cols and 0 <= shift_y < self.rows:
                            count = count + 1 if (shift_y, shift_x) in b else count
                            total = total + 1
                p = random.uniform(0, total)
                if p <= count: b.add((y, x))
        return b

    def __init__(self, rows, cols, start, finish):
        self.rows = rows
        self.cols = cols
        self.start = start
        self.finish = finish
        self.current = start
        #self.arena = [[0]*cols for i in range(rows)]
        self.blocks = self.probabilistic_blocks()

    def get_actions(self, y, x):
        pw = []
        manhattan = True
        moves = [(0,1), (2,1), (1,0), (1,2)]
        if not manhattan: moves = moves + [(0,0), (0, 2), (2,0), (2,2)]
        for i,j in moves:
            shift_y = y + (i-1)
            shift_x = x + (j-1)
            if 0 <= shift_x < self.cols and 0 <= shift_y < self.rows and not (shift_x == x and shift_y == y):
                if (shift_y, shift_x) not in self.blocks:
                    pw.append((shift_y, shift_x))
        return pw

    def get_next(self):
        return self.get_actions(self.current[0], self.current[1])

    def e_greedy(self, e, Q, cor):
        choices = self.get_actions(cor[0], cor[1])
        if random.uniform(0, 1) < e and choices:
            maximum = (Q[(cor, choices[0])], choices[0])
            for c in choices:
                maximum = (Q[(cor,c)], c) if Q[(cor, c)] > maximum[0] else maximum
            return maximum[1]
        else:
            return random.choice(choices) if choices else cor

    def q_learning(self, epsilon, gamma, alpha, episode_len, episode_num):
        Q = dict()
        for p in itertools.product(range(self.rows), range(self.cols)):
            choices = self.get_actions(p[0], p[1])
            if p == self.finish:
                for c in choices: Q[(p, c)] = 0
            else:
                for c in choices:
                    Q[(p, c)] = 1 if c == self.finish else -1
        positive_reward = 0
        for i in range(episode_num):
            if i%10000 == 0:
                print(str(i)+" ... Positive Reward count : " + str(positive_reward))
                positive_reward = 0
            # For each episode
            self.current = (int(random.uniform(0, self.rows-1)), int(random.uniform(0, self.cols-1)))
            #episode = []
            R = 0
            for j in range(episode_len):
                #pisode.append(self.current)
                if self.current == self.finish: break
                curr = self.current
                #choices_curr = self.get_next()
                c = self.e_greedy(epsilon, Q, curr)
                reward = 100 if c == self.finish else 0
                next_moves = self.get_actions(c[0], c[1])
                next_move_estimate = [Q[(c, n_c)] for n_c in next_moves]
                if (curr, c) not in Q or not next_move_estimate:
                    Q[(curr, c)] = 0
                else:
                    Q[(curr, c)] = Q[(curr, c)] + alpha *(reward + gamma * max(next_move_estimate) - Q[(curr, c)])
                self.current = c
                R = R + reward
            if R != 0:
                positive_reward = positive_reward + 1
        return Q

    def eval_control(self, Q, episode_len):
        episode = []
        self.current = self.start
        for i in range(episode_len):
            episode.append(self.current)
            if self.current == self.finish: break
            choices = self.get_next()
            if choices:
                max_choice = (Q[(self.current, choices[0])], choices[0])
                for c in choices:
                    max_choice = (Q[(self.current, c)], c) if Q[(self.current, c)] > max_choice[0] else max_choice
                self.current = max_choice[1]
            else: break
        return episode


def test():
    rows = 16
    cols = 19
    g = Grid(rows, cols, (0, 0), (rows-1, cols-1))
    episode_len = (g.rows * g.cols)
    episode_num = 100000
    Q = g.q_learning(0.6, 0.1, 0.5, episode_len, episode_num)
    pos_list = g.eval_control(Q, episode_len)
    print(pos_list)
    if pos_list[-1] != g.finish:
        pos_list = [pos_list[0], pos_list[-1]]
    ani = Draw.Animate(g)
    ani.show(pos_list)


test()
