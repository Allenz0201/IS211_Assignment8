import argparse
import random
import time

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
    def decide(self, turn_total, opponent_score):
        return "h"
    def reset(self):
        self.score = 0

class HumanPlayer(Player):
    def decide(self, turn_total, opponent_score):
        while True:
            choice = input(f"{self.name}: roll(r) or hold(h)? ").strip().lower()
            if choice in ("r","h"):
                return choice

class ComputerPlayer(Player):
    def decide(self, turn_total, opponent_score):
        hold_at = min(25, 100 - self.score)
        if turn_total >= hold_at:
            return "h"
        return "r"

class PlayerFactory:
    @staticmethod
    def create(kind, name):
        k = kind.strip().lower()
        if k == "human":
            return HumanPlayer(name)
        if k == "computer":
            return ComputerPlayer(name)
        raise ValueError("invalid player kind")

class Game:
    def __init__(self, p1, p2):
        self.players = [p1, p2]
        self.current = 0
        self.winner = None
    def roll_die(self):
        return random.randint(1,6)
    def next_player(self):
        self.current = 1 - self.current
    def play(self):
        for p in self.players:
            p.reset()
        self.winner = None
        while True:
            player = self.players[self.current]
            opponent = self.players[1 - self.current]
            turn_total = 0
            print(f"\n{player.name}'s turn. Scores: {player.name}={player.score}, {opponent.name}={opponent.score}")
            while True:
                decision = player.decide(turn_total, opponent.score)
                if decision == "r":
                    die = self.roll_die()
                    print(f"{player.name} rolled: {die}")
                    if die == 1:
                        turn_total = 0
                        print(f"{player.name} busts. Turn ends.")
                        break
                    else:
                        turn_total += die
                        print(f"Turn total now: {turn_total}")
                else:
                    player.score += turn_total
                    print(f"{player.name} holds. New score: {player.score}")
                    break
            if player.score >= 100:
                self.winner = player
                print(f"\nWinner: {player.name} with {player.score} points.")
                return self.winner
            self.next_player()

class TimedGameProxy:
    def __init__(self, game, limit_seconds=60):
        self.game = game
        self.limit = limit_seconds
        self.start_time = None
    def time_up(self):
        return (time.time() - self.start_time) >= self.limit
    def leading_player(self):
        p0, p1 = self.game.players
        if p0.score > p1.score:
            return p0
        if p1.score > p0.score:
            return p1
        return None
    def play(self):
        for p in self.game.players:
            p.reset()
        self.game.winner = None
        self.start_time = time.time()
        while True:
            if self.time_up():
                lead = self.leading_player()
                if lead is None:
                    print("\nTime up. Scores tied. Next point wins sudden death.")
                else:
                    self.game.winner = lead
                    print(f"\nTime up. Winner: {lead.name} with {lead.score} points.")
                    return self.game.winner
            player = self.game.players[self.game.current]
            opponent = self.game.players[1 - self.game.current]
            turn_total = 0
            print(f"\n{player.name}'s turn. Scores: {player.name}={player.score}, {opponent.name}={opponent.score}")
            while True:
                if self.time_up():
                    lead = self.leading_player()
                    if lead is None:
                        die = self.game.roll_die()
                        print(f"{player.name} rolled: {die}")
                        if die == 1:
                            turn_total = 0
                            print(f"{player.name} busts. Turn ends.")
                            break
                        else:
                            turn_total += die
                            print(f"Turn total now: {turn_total}")
                            if turn_total >= 1:
                                player.score += turn_total
                                print(f"{player.name} holds due to sudden death. New score: {player.score}")
                                lead2 = self.leading_player()
                                if lead2 is None:
                                    pass
                                else:
                                    self.game.winner = lead2
                                    print(f"\nSudden death winner: {lead2.name} with {lead2.score} points.")
                                    return self.game.winner
                                break
                    else:
                        self.game.winner = lead
                        print(f"\nTime up. Winner: {lead.name} with {lead.score} points.")
                        return self.game.winner
                decision = player.decide(turn_total, opponent.score)
                if decision == "r":
                    die = self.game.roll_die()
                    print(f"{player.name} rolled: {die}")
                    if die == 1:
                        turn_total = 0
                        print(f"{player.name} busts. Turn ends.")
                        break
                    else:
                        turn_total += die
                        print(f"Turn total now: {turn_total}")
                else:
                    player.score += turn_total
                    print(f"{player.name} holds. New score: {player.score}")
                    break
            if player.score >= 100:
                self.game.winner = player
                print(f"\nWinner: {player.name} with {player.score} points.")
                return self.game.winner
            self.game.next_player()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--player1", choices=["human","computer"], default="human")
    parser.add_argument("--player2", choices=["human","computer"], default="human")
    parser.add_argument("--timed", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    p1 = PlayerFactory.create(args.player1, "Player 1")
    p2 = PlayerFactory.create(args.player2, "Player 2")
    base_game = Game(p1, p2)
    if args.timed:
        proxy = TimedGameProxy(base_game, 60)
        proxy.play()
    else:
        base_game.play()

if __name__ == "__main__":
    main()