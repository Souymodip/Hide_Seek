import random
import time
import seeker
import Draw
import shapes


def seeker_reward(s, p):
    return 100 if s.caught(p) else 0


def prey_reward(s, p):
    return 100 if s.caught(p.get_pos()) else 0


def estimate_prey(Q, s, prey):
    caught = s.caught(prey.get_pos())
    if prey.get_hash() not in Q:
        return 100 if caught else 0
    return Q[prey.get_hash()]


def estimate_seeker(Q, s, prey):
    caught = s.caught(prey)
    if s.get_hash() not in Q:
        return 100 if caught else 0
    return Q[s.get_hash()]


def new_greedy_move_seeker(Q, seekers, prey, visited):
    maximum = seekers[0], estimate_seeker(Q, seekers[0], prey)
    for seeker in seekers:
        if estimate_seeker(Q, seeker, prey) > maximum[1]: maximum = seeker, estimate_seeker(Q, seeker, prey)
    maximals = [seeker for seeker in seekers if estimate_seeker(Q, seeker, prey) == maximum[1]]
    not_visited = [s for s in maximals if s.get_pos() not in visited]
    return random.choice(not_visited) if not_visited else random.choice(maximals)


def max_greedy_move_prey(Q, seeker, preys, visited):
    maximum = preys[0], estimate_prey(Q, seeker, preys[0])
    for prey in preys:
        if estimate_prey(Q, seeker, prey) > maximum[1]: maximum = seeker, estimate_prey(Q, seeker, prey)
    maximals = [prey for prey in preys if estimate_prey(Q, seeker, prey) == maximum[1]]
    not_visited = [s for s in maximals if s.get_pos() not in visited]
    return random.choice(not_visited) if not_visited else random.choice(maximals)


def min_greedy_move_prey(Q, seeker, preys, visited):
    minimum = preys[0], estimate_prey(Q, seeker, preys[0])
    for prey in preys:
        if estimate_prey(Q, seeker, prey) < minimum[1]: minimum = seeker, estimate_prey(Q, seeker, prey)
    minimals = [prey for prey in preys if estimate_prey(Q, seeker, prey) == minimum[1]]
    not_visited = [s for s in minimals if s.get_pos() not in visited]
    return random.choice(not_visited) if not_visited else random.choice(minimals)


def new_random_move(moves, visited):
    not_visited = [s for s in moves if s.get_pos() not in visited]
    return random.choice(not_visited) if not_visited else random.choice(moves)


def q_learning_prey(ar, seeker, prey, epsilon, gamma, alpha, episode_len, episode_num, early_exit):
    print("\tStarting Prey's q-Learning ... episode length :={}, number of episodes :={}".format(episode_len, episode_num))
    avg_time = 0
    old_p = 0
    Q = dict()
    non_zero = 0
    explored = 1
    curr_prey = shapes.Blob(prey)

    for i in range(episode_num):
        # Wondering Start
        rand_prey = curr_prey.get_random(ar.rows, ar.cols, ar.is_valid_position)
        if rand_prey: curr_prey = rand_prey

        start_time = time.time()
        episode = []
        visited = set()

        # Simulated Episode Begins
        for j in range(episode_len):
            h = curr_prey.get_hash()
            episode.append(curr_prey)
            visited.add(curr_prey.get_pos())

            if h not in Q:
                Q[h] = 0
                explored = explored + 1
            old_val = Q[h]

            if seeker.caught(curr_prey.get_pos()):
                G = prey_reward(seeker, curr_prey)
                Q[h] = G
                # Back propagating discounted reward
                for p in reversed(episode[:-1]):
                    G = gamma * G
                    lhash = p.get_hash()
                    if lhash not in Q or Q[lhash] == 0:
                        Q[lhash] = G
                        non_zero = non_zero + 1
                #for e in episode:
                #    print(str(e.get_pos()) + " -> " + str(Q[e.get_hash()]))

                break

            # Get legal next moves
            next_preys = curr_prey.moves(ar.is_valid_position)

            if not next_preys: break

            # Q-Learning BootStrapping
            max_est = max([estimate_prey(Q, seeker, p) for p in next_preys])

            Q[h] = old_val + alpha * (prey_reward(seeker, curr_prey) + gamma * max_est - old_val)
            if old_val == 0 and Q[h] != 0: non_zero = non_zero + 1

            # Take epsilon-greedy Step
            curr_prey = max_greedy_move_prey(Q, seeker, next_preys, visited) \
                if random.uniform(0, 1) < epsilon else new_random_move(next_preys, visited)

        avg_time = (avg_time * i + (time.time() - start_time)) / (i + 1)
        # Simulated Episode Ends

        if i % 1000 == 0 and i != 0:
            p = non_zero / explored * 100
            print("\t\t{}. Health : {}/{} := {:.2f}%, Average Time for episode := "
                  "{:.2f}ms".format(i, non_zero, explored, p, avg_time * 1000))
            if early_exit and  p > 60 and p - old_p < 0.5:
                break
            else:
                old_p = p
    p = (float(non_zero / explored)) * 100
    print("\t\tFinally. Health : {}/{} := {:.2f}%, Average Time for episode :=  "
          "{:.2f}ms".format(non_zero, explored, p, avg_time * 1000))
    return Q


def q_learning_seeker(ar, seeker, prey, epsilon, gamma, alpha, episode_len, episode_num, early_exit):
    print("\tStarting Seeker's q-Learning ... episode length :={}, number of episodes :={}".format(episode_len, episode_num))
    avg_time = 0
    old_p = 0
    Q = dict()
    non_zero = 0
    explored = 1
    curr_seeker = seeker

    for i in range(episode_num):
        # Wondering Start
        rand_seeker = seeker.get_random(ar.rows, ar.cols, ar.is_valid_position)
        if rand_seeker: curr_seeker = rand_seeker

        start_time = time.time()
        episode = []
        visited = set()
        # Simulated Episode Begins
        for j in range(episode_len):
            h = curr_seeker.get_hash()
            episode.append(curr_seeker)
            visited.add(curr_seeker)
            if h not in Q:
                Q[h] = 0
                explored = explored + 1
            old_val = Q[h]

            if curr_seeker.caught(prey):
                G = seeker_reward(curr_seeker, prey)
                Q[h] = G

                # Back propagating discounted reward
                for s in reversed(episode[:-1]):
                    G = gamma * G
                    lhash = s.get_hash()
                    if lhash not in Q or Q[lhash] == 0:
                        Q[lhash] = G
                        non_zero = non_zero + 1
                break

            # Get legal next moves
            next_seekers = curr_seeker.moves(ar.is_valid_position)
            if not next_seekers: break

            # Q-Learning BootStrapping
            max_est = max([estimate_seeker(Q, s, prey) for s in next_seekers])

            Q[h] = old_val + alpha * (seeker_reward(curr_seeker, prey) + gamma * max_est - old_val)
            if old_val == 0 and Q[h] != 0: non_zero = non_zero + 1

            # Take epsilon-greedy Step
            curr_seeker = new_greedy_move_seeker(Q, next_seekers, visited, prey) \
                if random.uniform(0, 1) < epsilon else new_random_move(next_seekers, visited)
        avg_time = (avg_time * i + (time.time() - start_time)) / (i + 1)
        # Simulated Episode Ends

        if i % 1000 == 0 and i != 0:
            p = non_zero / explored * 100
            print("\t\t{}. Health : {}/{} := {:.2f}%, Average Time for episode := "
                  "{:.2f}ms".format(i, non_zero, explored, p, avg_time * 1000))
            if early_exit and p > 0 and p - old_p < 0.5:
                break
            else:
                old_p = p

    p = (float(non_zero/explored)) * 100
    print("\t\tFinally. Health : {}/{} := {:.2f}%, Average Time for episode :=  "
          "{:.2f}ms".format(non_zero, explored, p, avg_time * 1000))
    return Q


def eval_seeker(ar, Q, start_seeker, prey, episode_len):
    episode = []
    curr = start_seeker
    visited = set()
    for i in range(episode_len):
        visited.add(curr)
        nexts = curr.moves(ar.is_valid_position)
        if not curr.caught(prey) and nexts:
            curr = new_greedy_move_seeker(Q, nexts, visited, prey)
            if not curr: break
        episode.append(curr)
        #print("Seeker := " + str(episode[-1].get_pos()))
    return episode


def eval_prey(ar, Q, start_seeker, prey, episode_len):
    curr_prey = shapes.Blob(prey)
    episode = []
    visited = set()
    for i in range(episode_len):
        visited.add(curr_prey.get_pos())

        nexts = curr_prey.moves(ar.is_valid_position)
        if not start_seeker.caught(curr_prey.get_pos()) and nexts:
            curr_prey = min_greedy_move_prey(Q, start_seeker, nexts, visited)
            if not curr_prey: break
        episode.append(curr_prey)
        #print("prey := " + str(episode[-1].get_pos()))
    return episode


if __name__ == "__main__":
    rows = 30
    cols = 40
    rounds =10#cols*rows
    episode_len=100
    episode_num= 5000
    arena = seeker.GameBoard(rows, cols, (4, 4), (int(rows/2), int(cols/2)))

    trace_seeker = False
    show = None
    prey = shapes.Blob(arena.prey)
    if trace_seeker:
        Q = q_learning_seeker(arena, arena.seeker, arena.prey, 0.6, 0.9, 0.5, episode_len, episode_num)
        if arena.seeker.get_hash() not in Q: Q[arena.seeker.get_hash()] = 0
        print("Q"+ str(arena.seeker.get_pos()) +" := " + str(Q[arena.seeker.get_hash()]))
        movement = eval_seeker(arena, Q, arena.seeker, arena.prey, episode_len)
        show = movement, [prey]*(len(movement))
    else:
        Q = q_learning_prey(arena, arena.seeker, arena.prey, 0.6, 0.9, 0.5, episode_len, episode_num)
        if prey.get_hash() not in Q: Q[prey.get_hash()] = 0
        print("Q" + str(prey.get_pos()) + " := " + str(Q[prey.get_hash()]))
        movement = eval_prey(arena, Q, arena.seeker, arena.prey, episode_len)
        show = [arena.seeker]*len(movement), movement
    ani = Draw.AnimateGameBoard(arena)
    ani.show_exact(show)
