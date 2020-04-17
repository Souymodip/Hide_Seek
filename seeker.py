import random
import Draw
import shapes


def get_manhattan_moves(y, x):
    moves = [(0, 1), (2, 1), (1, 0), (1, 2)]
    pw = []
    for i, j in moves:
        shift_y = y + (i - 1)
        shift_x = x + (j - 1)
        pw.append((shift_y, shift_x))
    return pw


def get_neighbourhood(cor):
    y = cor[0]
    x = cor[1]
    moves = [(0, 1), (2, 1), (1, 0), (0,0), (1, 2), (0, 2), (2, 0), (2, 2)]
    pw = []
    for i, j in moves:
        shift_y = y + (i - 1)
        shift_x = x + (j - 1)
        pw.append((shift_y, shift_x))
    return pw


class GameBoard:
    def probabilistic_blocks(self, forbidden):
        b = set()
        #return b
        for y in range(self.rows):
            for x in range(self.cols):
                if (y, x) in forbidden : continue
                count = 0.5
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

    def __init__(self, rows, cols, start, prey):
        self.rows = rows
        self.cols = cols
        self.start = start
        self.prey = prey
        self.seeker = shapes.Snake(start, 5)
        #self.seeker = shapes.Blob(start)
        forbidden = {prey}
        forbidden.add(start)
        for i in range(5):
            new_set = set()
            for coor in forbidden:
                new_set = new_set.union(get_neighbourhood(coor))
            forbidden = forbidden.union(new_set)

        self.blocks = self.probabilistic_blocks(forbidden)
        self.Q = dict() # State Value Estimate
        self.explored = 1
        self.non_zero = 0

    def is_valid_position(self, positions):
        for y, x in positions:
            if not ((0 <= y < self.rows) and (0 <= x < self.cols) and ((y,x) not in self.blocks)):
                return False
        return True

    def estimate(self, seeker):
        h = seeker.get_hash()
        if h not in self.Q:
            self.Q[h] = 100 if seeker.caught(self.prey) else 0
            self.explored = self.explored + 1
        return self.Q[h]

    def reward(self, seeker):
        return 100 if seeker.caught(self.prey) else 0

    def greedy_move_seeker(self, seekers):
        maximum = seekers[0], self.estimate(seekers[0])
        for seeker in seekers:
            if self.estimate(seeker) > maximum[1]: maximum = seeker, self.estimate(seeker)
        maximals = [seeker for seeker in seekers if self.estimate(seeker) == maximum[1]]
        return random.choice(maximals)

    def q_learning(self, epsilon, gamma, alpha, episode_len, episode_num):
        print("\tStarting q-Learning ... episode length :={}, number of episodes:={}".format(episode_len, episode_num))
        for i in range(episode_num):
            # Wondering Start
            rand_seeker = self.seeker.get_random(self.rows, self.cols, self.is_valid_position)
            if rand_seeker: self.seeker = rand_seeker
            self.seeker.reset()

            for j in range(episode_len):
                h = self.seeker.get_hash()

                if self.seeker.caught(self.prey):
                    if h not in self.Q:
                        self.Q[h] = self.reward(self.seeker)
                    break

                # Get legal next moves
                next_seekers = self.seeker.moves(self.is_valid_position)
                if not next_seekers:
                    #print ("No Legal Next Move from :" +str(self.seeker.get_body()))
                    #for s in sm : print ("\t\t" + str(s))
                    break

                # Q-Learning BootStrapping
                max_estimates = max([self.estimate(seeker) for seeker in next_seekers])
                old_val = 0
                if h in self.Q:
                    old_val = self.Q[h]
                    self.Q[h] = old_val + alpha *(self.reward(self.seeker) + gamma * max_estimates - old_val)
                else:
                    self.Q[h] = alpha * (self.reward(self.seeker) + gamma * max_estimates)
                    self.explored = self.explored + 1
                if old_val == 0 and self.Q[h] != 0: self.non_zero = self.non_zero + 1

                # Take epsilon-greedy Step
                self.seeker = self.greedy_move_seeker(next_seekers) if random.uniform(0, 1) < epsilon else random.choice(next_seekers)

            if i % 10000 == 0 and i != 0:
                p = self.non_zero/self.explored*100
                print("\t{} ... Health : {}/{} := {:.2f}%".format(i, self.non_zero, self.explored, p))
                if p > 98.0: break

        p = (float(self.non_zero) / float(self.explored)) * 100
        print("\tFinally ... Health : {:d}/{:d} := {:.2f}%".format(self.non_zero, self.explored, p))

    def eval_control(self, episode_len):
        print("\tEvaluating Optimal Strategy...")
        episode = []
        for i in range(episode_len):
            episode.append(self.seeker.get_representation())
            if self.seeker.caught(self.prey): break
            choices = self.seeker.moves(self.is_valid_position)
            if choices:
                self.seeker = self.greedy_move_seeker(choices)
            else:
                break
        return episode

    def eval_one_step_seeker(self, seeker, prey):
        if seeker.caught(prey):
            return seeker
        else:
            choices = self.seeker.moves(self.is_valid_position)
            return self.greedy_move_seeker(choices) if choices else seeker

    def greedy_move_prey(self, preys):
        def estimate_prey(preys):
            sums = [0]*len(preys)
            count = [0]*len(preys)
            for k in self.Q:
                for i in range(len(preys)):
                    if str(preys[i]) in k:
                        sums[i] = (sums[i]*count[i] + -1*self.Q[k])/(count[i]+1)
                        count[i] = count[i] + 1
            return sums
        est = estimate_prey(preys)
        #print("\t\t prey moves :="+str(list(zip(est, preys))))
        maximum = max(est)
        maximals = []
        for i in range(len(preys)):
            if est[i] == maximum:
                maximals.append(preys[i])

        return random.choice(maximals)

    def eval_one_step_prey(self, seeker, prey):
        if seeker.caught(prey):
            return prey
        else:
            choices = [m for m in get_neighbourhood(prey) if self.is_valid_position([m])] + [prey]
            return self.greedy_move_prey(choices) if choices else prey


def test():
    rows = 60
    cols = 80
    g = GameBoard(rows, cols, (4, 4), (rows-1, cols-1))
    episode_len = (g.rows * g.cols)
    episode_num = 50000
    g.q_learning(0.6, 0.9, 0.5, episode_len, episode_num)
    g.seeker.reset()
    pos_list = g.eval_control(episode_len)

    ani = Draw.AnimateGameBoard(g)
    ani.show(pos_list)
    for i in range (5):
        seeker = g.seeker.get_random(g.rows, g.cols, g.is_valid_position)
        if seeker: g.seeker = seeker
        pos_list = g.eval_control(episode_len)
        ani.show(pos_list)


if __name__ =="__main__":
    test()
