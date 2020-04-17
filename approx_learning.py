import random
import seeker
import Draw


def x(state, r, c):
    return [1, state[0]/r, state[1]/c, state[0]*state[1]/(r*c)]


def cross(v1, v2):
    c = []
    for i in range(max(len(v1), len(v2))):
        c.append(v1[i]*v2[i])
    return c


def dot(v1, v2):
    c = 0
    for i in range(max(len(v1), len(v2))):
        c = c + (v1[i] * v2[i])
    return c


def add(v1, v2):
    c = []
    for i in range(max(len(v1), len(v2))):
        c.append(v1[i] + v2[i])
    return c


def times(c, v1):
    r = []
    for i in range(len(v1)):
        r.append(c * v1[i])
    return r


def q(state, w, r, c):
    return dot(x(state, r, c), w)


def e_greedy(ar, epsilon, seeker, w, r, c):
    seekers = seeker.moves(ar.is_valid_position)
    if not seekers:
        return None
    if random.uniform(0,1) < epsilon:
        maximum = max([q(s.get_pos(), w, r, c) for s in seekers])
        seekers = [s for s in seekers if q(s.get_pos(), w, r, c) == maximum]
    return random.choice(seekers) if seekers else None


def greedy(ar, seeker, w, r, c):
    seekers = seeker.moves(ar.is_valid_position)
    if not seekers: return None
    maximum = max([q(s.get_pos(), w, r, c) for s in seekers])
    seekers = [s for s in seekers if q(s.get_pos(), w, r, c) == maximum]
    return random.choice(seekers) if seekers else None


def linear(ar, epsilon, gamma, alpha, episode_len, episode_num):
    scale = ar.rows*ar.cols

    print("\t Starting Linear approximation of Q function")
    w = [0]*4
    dead = 0
    for i in range(episode_num):
        rand_seeker = ar.seeker.get_random(ar.rows, ar.cols, ar.is_valid_position)
        if rand_seeker: ar.seeker = rand_seeker
        next_seeker = None
        for j in range(episode_len):
            error = 0
            s = x(ar.seeker.get_pos(), ar.rows, ar.cols)
            if ar.seeker.caught(ar.prey):
                error = 10 - q(ar.seeker.get_pos(), w, ar.rows, ar.cols)
            else:
                next_seeker = e_greedy(ar, epsilon, ar.seeker, w, ar.rows, ar.cols)
                if next_seeker:
                    error = -1 * q(ar.seeker.get_pos(), w, ar.rows, ar.cols) + gamma* q(next_seeker.get_pos(), w, ar.rows, ar.cols)

            w = add(w, times(alpha * error, s))
            #print("State :=" + str(ar.seeker.get_pos()) + ", x(s) := " + str(s) + ", Error :=" + str(error) + ", w := " + str(w))
            if ar.seeker.caught(ar.prey): break
            if next_seeker:  ar.seeker = next_seeker
        if i%100 == 0:
         print(str(i) + ". Random Start State :=" + str(rand_seeker.get_pos()) +  ", w := " + str(w))

    return w


def eval(ar, w, start_seeker, episode_len):
    episode = []
    curr = start_seeker
    for i in range(episode_len):
        episode.append(curr.get_representation())
        if not curr.caught(ar.prey):
            curr = greedy(ar, curr, w, ar.rows, ar.cols)
            if not curr: break
    return episode


rows = 30
cols = 40
rounds =10#cols*rows
episode_len=100
episode_num= 10000
arena = seeker.GameBoard(rows, cols, (4, 4), (int(rows/2), int(cols/2)))
w = linear(arena, 0.6, 0.9, 0.5, episode_len, episode_num)
arena.seeker.reset()

print (cross([1,2], [3, 4]))

movement = eval(arena, w, arena.seeker, episode_len*10)
ani = Draw.AnimateGameBoard(arena)

print(movement)
ani.show(movement)


