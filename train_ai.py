import random
import pickle

class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.winner = None
        self.done = False

    def reset(self):
        self.board = [" " for _ in range(9)]
        self.winner = None
        self.done = False
        return self.get_state()

    def get_state(self):
        return "".join(self.board)

    def available_actions(self):
        return [i for i, cell in enumerate(self.board) if cell == " "]

    def make_move(self, action, player):
        if self.board[action] != " ":
            return False
        self.board[action] = player
        self.check_game_status()
        return True

    def check_game_status(self):
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]

        for pattern in win_patterns:
            a, b, c = pattern
            if self.board[a] == self.board[b] == self.board[c] != " ":
                self.winner = self.board[a]
                self.done = True
                return

        if " " not in self.board:
            self.winner = "Draw"
            self.done = True

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.9995, epsilon_min=0.05):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state, available_actions):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_actions)

        q_values = [self.get_q_value(state, a) for a in available_actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(available_actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def update_q_value(self, state, action, reward, next_state, next_actions, done):
        current_q = self.get_q_value(state, action)
        max_future_q = 0 if done else max([self.get_q_value(next_state, a) for a in next_actions], default=0)
        updated_q = current_q + self.alpha * (reward + self.gamma * max_future_q - current_q)
        self.q_table[(state, action)] = updated_q

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            if self.epsilon < self.epsilon_min:
                self.epsilon = self.epsilon_min

def random_opponent_move(env):
    action = random.choice(env.available_actions())
    env.make_move(action, "O")

def train_agent(episodes=50000):
    env = TicTacToe()
    agent = QLearningAgent()

    for episode in range(episodes):
        state = env.reset()

        while not env.done:
            actions = env.available_actions()
            action = agent.choose_action(state, actions)
            env.make_move(action, "X")

            if env.done:
                if env.winner == "X":
                    reward = 1
                elif env.winner == "Draw":
                    reward = 0.5
                else:
                    reward = -1
                agent.update_q_value(state, action, reward, env.get_state(), [], True)
                break

            random_opponent_move(env)

            if env.done:
                if env.winner == "O":
                    reward = -1
                elif env.winner == "Draw":
                    reward = 0.5
                else:
                    reward = 0
                agent.update_q_value(state, action, reward, env.get_state(), [], True)
                break

            next_state = env.get_state()
            next_actions = env.available_actions()
            reward = 0
            agent.update_q_value(state, action, reward, next_state, next_actions, False)
            state = next_state

        agent.decay_epsilon()

        if (episode + 1) % 5000 == 0:
            print(f"Episode {episode + 1} completed, epsilon = {agent.epsilon:.4f}")

    return agent

def save_q_table(agent, filename="q_table.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(agent.q_table, f)

if __name__ == "__main__":
    agent = train_agent(episodes=50000)
    save_q_table(agent)
    print("Training complete. Q-table saved as q_table.pkl")