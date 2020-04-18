import random


def get_random_coordinates(rows, cols):
    return random.choice(list(range(rows))), random.choice(list(range(cols)))


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
    moves = [(0, 1), (2, 1), (1, 0), (1, 2), (0,0), (0, 2), (2, 0), (2, 2)]
    pw = []
    for i, j in moves:
        shift_y = y + (i - 1)
        shift_x = x + (j - 1)
        pw.append((shift_y, shift_x))
    return pw


class Snake:
    def __init__(self, head_cor, length):
        self.length = length
        self.head_cor = head_cor
        self.body = [(head_cor[0], head_cor[1] - i) for i in range(length)]

    def copy(self, body):
        ret = Snake(self.head_cor, len(body))
        ret.body = body
        return ret

    def moves(self, is_valid_pos):
        head = self.body[0]
        head_moves = get_manhattan_moves(head[0], head[1])
        ret = []
        for m in head_moves:
            if m not in set(self.body):
                new_body = [m] + self.body[:-1]
                if is_valid_pos(new_body):
                    ret.append(self.copy(new_body))
        return ret

    def reset(self):
        self.body = [(self.head_cor[0], self.head_cor[1] - i) for i in range(self.length)]

    def get_representation(self):
        return self.body[0], self.body

    def get_random(self, rows, cols, is_valid_pos):
        tries = 0
        body = []
        while len(body) < len(self.body) and tries < 50:
            body = []
            tries = tries + 1
            p = get_random_coordinates(rows, cols)
            body.append(p)
            seen = {p}
            while len(body) < len(self.body):
                if not body: break
                ms = [m for m in get_manhattan_moves(body[-1][0], body[-1][1]) if
                      is_valid_pos([m]) and (m not in seen)]
                if not ms:
                    body = body[:-1]
                else:
                    m = random.choice(ms)
                    body.append(m)
                    seen.add(m)
        if len(body) == len(self.body):
            return self.copy(body)
        else:
            return None

    def get_hash(self):
        return self.get_pos()

    def caught(self, pos):
        return pos in set(self.body)

    def get_pos(self):
        return self.body[0]


class Blob:
    def create_body_from_center(cor):
        body = {cor}
        body = body.union(get_manhattan_moves(cor[0], cor[1]))
        return body

    def __init__(self, center_cor):
        self.reset_center = center_cor
        self.center_cor = center_cor

    def copy(self, new_center):
        b = Blob(self.reset_center)
        b.center_cor = new_center
        return b

    def moves(self, is_valid_pos):
        return [self.copy(c) for c in get_neighbourhood(self.center_cor) if is_valid_pos(Blob.create_body_from_center(c))]

    def reset(self):
        self.center_cor = self.reset_center

    def get_representation(self):
        return self.center_cor, Blob.create_body_from_center(self.center_cor)

    def get_random(self, rows, cols, is_valid_pos):
        tries = 0
        while tries < 50:
            tries = tries + 1
            p = int(random.uniform(0, rows)), int(random.uniform(0, cols))
            if is_valid_pos(Blob.create_body_from_center(p)):
                return self.copy(p)
        return None

    def get_hash(self):
        return self.center_cor

    def caught(self, pos):
        return pos in set(Blob.create_body_from_center(self.center_cor))

    def get_pos(self):
        return self.center_cor
