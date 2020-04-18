import random
import Draw
import shapes
import time


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
                count = 0.3
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
        for i in range(3):
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

    def reward(self, seeker, prey):
        return 100 if seeker.caught(prey) else 0

    def greedy_move_seeker(self, seekers):
        maximum = seekers[0], self.estimate(seekers[0])
        for seeker in seekers:
            if self.estimate(seeker) > maximum[1]: maximum = seeker, self.estimate(seeker)
        maximals = [seeker for seeker in seekers if self.estimate(seeker) == maximum[1]]
        return random.choice(maximals)

    def new_greedy_move_seeker(self, seekers, visited):
        maximum = seekers[0], self.estimate(seekers[0])
        for seeker in seekers:
            if self.estimate(seeker) > maximum[1]: maximum = seeker, self.estimate(seeker)
        maximals = [seeker for seeker in seekers if self.estimate(seeker) == maximum[1]]
        not_visited = [s for s in maximals if s.get_pos() not in visited]
        return random.choice(not_visited) if not_visited else random.choice(maximals)

    def new_random_move_seeker(self, seekers, visited):
        not_visited = [s for s in seekers if s.get_pos() not in visited]
        return random.choice(not_visited) if not_visited else random.choice(seekers)

    def random_move_seeker(self, seekers):
        return random.choice(seekers)

    def q_learning(self, epsilon, gamma, alpha, episode_len, episode_num):
        print("\tStarting q-Learning ... episode length :={}, number of episodes :={}".format(episode_len, episode_num))
        avg_time = 0
        old_p = 0
        for i in range(episode_num):
            # Wondering Start
            rand_seeker = self.seeker.get_random(self.rows, self.cols, self.is_valid_position)
            if rand_seeker: self.seeker = rand_seeker

            start_time = time.time()
            episode = []
            visited = set()
            for j in range(episode_len):
                h = self.seeker.get_hash()
                episode.append(self.seeker)
                visited.add(self.seeker)
                if self.seeker.caught(self.prey):
                    G = self.reward(self.seeker, self.prey)
                    if h not in self.Q:
                        self.Q[h] = G
                    # Back propagating discounted reward
                    for s in reversed(episode[:-1]):
                        G = gamma * G
                        lhash = s.get_hash()
                        if lhash not in self.Q or self.Q[lhash] == 0 :
                            self.Q[lhash] = G
                            self.non_zero = self.non_zero + 1
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
                    self.Q[h] = old_val + alpha *(self.reward(self.seeker, self.prey) + gamma * max_estimates - old_val)
                else:
                    self.Q[h] = alpha * (self.reward(self.seeker, self.prey) + gamma * max_estimates)
                    self.explored = self.explored + 1
                if old_val == 0 and self.Q[h] != 0: self.non_zero = self.non_zero + 1

                # Take epsilon-greedy Step
                self.seeker = self.new_greedy_move_seeker(next_seekers, visited) \
                    if random.uniform(0, 1) < epsilon else self.new_random_move_seeker(next_seekers, visited)
            avg_time = (avg_time * (i) + (time.time() - start_time))/(i+1)
            if i % 1000 == 0 and i != 0:
                p = self.non_zero/self.explored*100
                print("\t{}. Health : {}/{} := {:.2f}%, Average Time for episode := "
                      "{:.2f}ms".format(i, self.non_zero, self.explored, p, avg_time*1000))
                if p > 0 and p - old_p < 0.1: break
                else: old_p = p

        p = (float(self.non_zero) / float(self.explored)) * 100
        print("\tFinally. Health : {}/{} := {:.2f}%, Average Time for episode :=  "
              "{:.2f}ms".format(self.non_zero, self.explored, p, avg_time*1000))

    def eval_control(self, episode_len):
        print("\tEvaluating Optimal Strategy...")
        episode = []
        visited = set()
        estimate = self.Q[self.seeker.get_hash()] if self.seeker.get_hash() in self.Q else 0
        print("\t Q" + str(self.seeker.get_pos()) +" := " +str(estimate))
        for i in range(episode_len):
            episode.append((self.seeker.get_representation(), self.prey))
            visited.add(self.seeker.get_pos())
            if self.seeker.caught(self.prey): break
            choices = self.seeker.moves(self.is_valid_position)
            if choices:
                self.seeker = self.new_greedy_move_seeker(choices, visited)
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


if __name__ == "__main__":
    rows = 60
    cols = 80
    g = GameBoard(rows, cols, (4, 4), (rows-1, cols-1))
    episode_len = int((g.rows * g.cols)/2)
    episode_num = 50000
    g.q_learning(0.7, 0.9, 0.5, episode_len, episode_num)
    g.seeker.reset()
    pos_list = g.eval_control(episode_len)

    ani = Draw.AnimateGameBoard(g)
    ani.show(pos_list)
    for i in range(5):
        seeker = g.seeker.get_random(g.rows, g.cols, g.is_valid_position)
        if seeker: g.seeker = seeker
        pos_list = g.eval_control(episode_len)
        ani.show(pos_list)

