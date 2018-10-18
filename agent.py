import random
import time
import math


class Agent(object):
    def __init__(self, game):
        self.game = game

    def getAction(self, state):
        raise Exception("Not implemented yet")

class RandomAgent(Agent):
    def getAction(self, state):
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)

class SimpleGreedyAgent(Agent):
    # a one-step-lookahead greedy agent that returns action with max vertical advance
    def getAction(self, state):
        legal_actions = self.game.actions(state)

        self.action = random.choice(legal_actions)

        player = self.game.player(state)
        if player == 1:
            max_vertical_advance_one_step = max([action[0][0] - action[1][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[0][0] - action[1][0] == max_vertical_advance_one_step]
        else:
            max_vertical_advance_one_step = max([action[1][0] - action[0][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[1][0] - action[0][0] == max_vertical_advance_one_step]
        self.action = random.choice(max_actions)

class betagob(Agent):
    def getLength(self, action, player):
        # return the vertical length change after the action for the player
        if (player == 1):
            return action[0][0] - action[1][0]
        else:
            return action[1][0] - action[0][0]
    def evaluate(self, state):
        # evalutaion of the whole board status
        score = 0
        board = state[1]
        l1, l2 = 0, 100
        for (i, j) in self.allPos:
            if board.board_status[(i, j)] == 1:
                score += self.w1[19 - i]
                l1 = max(l1, i)
            if board.board_status[(i, j)] == 2:
                score -= self.w1[i - 1]
                l2 = min(l2, i)
        board = state[1]
        poss = board.getPlayerPiecePositions(1)
        for pos in poss:
            acts = board.getAllHopPositions(pos)
            l = 0
            for act in acts:
                l = max(l, self.getLength([pos, act], 1))
            score += self.w2[l]

        poss = board.getPlayerPiecePositions(2)
        for pos in poss:
            acts = board.getAllHopPositions(pos)
            l = 0
            for act in acts:
                l = max(l, self.getLength([pos, act], 1))
            score -= self.w2[l]

        cnt1 = 0
        for i in range(1, 5):
            for j in range(1, i + 1):
                if (board.board_status[(i, j)] == 1): cnt1 += 1

        cnt2 = 0
        for i in range(16, 20):
            for j in range(1, 20 - i + 1):
                if (board.board_status[(i, j)] == 2): cnt2 += 1

        score += (cnt1 - cnt2) * 200
        score += ((20+1*cnt1*cnt1) * (-l1) + (20+1*cnt2*cnt2) * (-l2)) * 2
        return score

    def MinMaxSearch(self, state, alpha, beta, depth):
        if (depth >= 2):
            return self.evaluate(state)

        player = self.game.player(state)
        legal_actions = self.game.actions(state)
        legal_actions = [action for action in legal_actions if self.getLength(action, player) >= 0]
        legal_actions = [[self.getLength(action,player), action] for action in legal_actions]
        legal_actions.sort(reverse=True)
        if (player == 1):
            v = -1e10
            for action2 in legal_actions:
                action = action2[1]
                v = max(v, self.MinMaxSearch(self.game.succ(state, action), alpha, beta, depth + 1))
                if v > alpha:
                    alpha = v
                    if depth == 0: self.action = action
                if alpha >= beta: return v
            return v
        else:
            v = 1e10
            for action2 in legal_actions:
                action = action2[1]
                v = min(v, self.MinMaxSearch(self.game.succ(state, action), alpha, beta, depth + 1))
                if v < beta:
                    beta = v
                    if depth == 0: self.action = action
                if alpha >= beta: return v
            return v

    def check(self, state, player):
        board = state[1]
        max1 = 0
        min2 = 1e9
        for (i, j) in self.allPos:
            if board.board_status[(i, j)] == 1 and max1 < i:
                max1 = i
            if board.board_status[(i, j)] == 2 and min2 > i:
                min2 = i
        if (max1>=min2): return 2
        if (player==1): return max1>5
        if (player==2): return min2<15

    def miss(self, state, player):
        board = state[1]
        cnt1, s11, s12, s21, s22 = 0, 0, 0, 0, 0
        for i in range(1, 5):
            for j in range(1, i + 1):
                if (board.board_status[(i, j)] == 1): cnt1 += 1
                s11 += i
                s12 += j

        cnt2 = 0
        for i in range(16, 20):
            for j in range(1, 20 - i + 1):
                if (board.board_status[(i, j)] == 2): cnt2 += 1
                s21 += i
                s22 += j

        if player == 1:
            if cnt2 == 10: return [-1, s11, s12]
            return [10 - cnt1, s11, s12]

        if player == 2:
            if cnt1 == 10: return [-1, s21, s22]
            return [10 - cnt2, s21, s22]

    def sum(self, state, player):
        board = state[1]
        s1, s2 = 0, 0
        for i in range(1, 11):
            for j in range(1, i + 1):
                if board.board_status[(i, j)] == 1 and player == 1:
                    s1 += i
                    s2 += j
                if board.board_status[(i, j)] == 2 and player == 2:
                    s1 += i
                    s2 += j
        for i in range(11, 20):
            for j in range(1, 21 - i):
                if board.board_status[(i, j)] == 1 and player == 1:
                    s1 += i
                    s2 += j
                if board.board_status[(i, j)] == 2 and player == 2:
                    s1 += i
                    s2 += j
        return [s1, s2]

    def dfs(self, state, player, depth, act):
        p = self.game.player(state)
        legal_actions = self.game.actions(state)
        legal_actions = [action for action in legal_actions if self.getLength(action, p) >= 0]
        [cnt, s1, s2] = self.miss(state, player)
        s11, s22 = self.sum(state, player)
        if cnt < 0: return
        if p != player:
            self.dfs(self.game.succ(state, legal_actions[0]), player, depth, act)
            return
        if (depth + cnt >= self.best):
            return

        if (cnt == 0):
            self.action = act
            self.best = depth
            print ('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
            print (self.best)
            return

        acts = [[abs(s11 + action[1][0]  - action[0][0] - s1) + abs(s22 + action[1][1]  - action[0][1] - s2), action] for action in legal_actions]
        acts.sort()
        for action2 in acts:
            action = action2[1]
            if depth == 0:
                act = action
            self.dfs(self.game.succ(state, action), player, depth + 1, act)

    def GreedySearch(self, state, player, depth, act, summ, lastact):
        p = self.game.player(state)
        legal_actions = self.game.actions(state)
        legal_actions = [action for action in legal_actions if self.getLength(action, p) >= 0]
        [cnt, s1, s2] = self.miss(state, player)
        if cnt < 0: return
        if p != player:
            self.GreedySearch(self.game.succ(state, legal_actions[0]), player, depth, act,summ,act)
            return
        acts = [[self.getLength(action,player), action] for action in legal_actions]
        acts.sort(reverse=True)
        if (len(acts)==0):return
        t=max(summ/depth,(summ+acts[0][0])/(depth+1))
        if t>self.best:
            self.best=t
            self.action=act
            print ('best is',self.best, depth+1)

        if (depth >= 3):
            return

        for action2 in acts:
            action = action2[1]
            if (action[0]!=lastact[1]):continue
            if depth == 0:
                act = action
            self.GreedySearch(self.game.succ(state, action), player, depth + 1, act,summ+action2[0],action)

    def dist(self, action, player):
        if player==1: return action[0][0]-1
        else: return 19-action[0][0]

    def getAction(self, state):
        self.allPos = []
        for i in range(1, 11):
            for j in range(1, i + 1):
                self.allPos.append((i, j))
        for i in range(11, 20):
            for j in range(1, 21 - i):
                self.allPos.append((i, j))
        self.w1 = [10*i for i in range(25)]
        self.w2 = [5*i for i in range(25)]

        legal_actions = self.game.actions(state)
        player = self.game.player(state)
        legal_actions = [action for action in legal_actions if self.getLength(action, player) >= 0]

        if player == 1:
            max_vertical_advance_one_step = max([action[0][0] - action[1][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[0][0] - action[1][0] == max_vertical_advance_one_step]
        else:
            max_vertical_advance_one_step = max([action[1][0] - action[0][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[1][0] - action[0][0] == max_vertical_advance_one_step]
        self.action = random.choice(max_actions)
        print (self.action)

        stage = self.check(state, player)
        print ('stage is ',stage)
        if stage==2:
            self.MinMaxSearch(state, -1e10, 1e10, 0)
        elif stage==1:
            self.best=0
            legal_actions = [action for action in legal_actions if self.dist(action,player)>= 4]
            for act in legal_actions:
                self.GreedySearch(self.game.succ(state, act), player, 1, act,self.getLength(act,player), act)
        else:
            self.best = 4
            self.dfs(state, player, 0, 1)

