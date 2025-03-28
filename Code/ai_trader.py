import requests
import time
import numpy as np
from enum import Enum

class Action(Enum):
    BUY = 0
    SELL = 1
    HOLD = 2

class SimpleTrader:
    def __init__(self, api_url="http://127.0.0.1:5000", rsi_threshold_low=30, rsi_threshold_high=70, learning_rate=0.1, discount_factor=0.9, epsilon=0.1, leverage=1):
        self.api_url = api_url
        self.rsi_threshold_low = rsi_threshold_low
        self.rsi_threshold_high = rsi_threshold_high
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.leverage = leverage  # اهرم برای AI
        self.q_table = np.zeros((3, len(Action)))
        self.last_action = None
        self.last_state = None
        self.open_trade_id = None

    def get_state(self, rsi):
        if rsi < self.rsi_threshold_low:
            return 0
        elif rsi > self.rsi_threshold_high:
            return 2
        else:
            return 1

    def decide_action(self, rsi):
        current_state = self.get_state(rsi)
        if np.random.random() < self.epsilon:
            action = np.random.choice(list(Action))
        else:
            action = Action(np.argmax(self.q_table[current_state]))
        self.last_state = current_state
        self.last_action = action
        return action

    def update_q_table(self, reward, new_rsi):
        if self.last_state is None or self.last_action is None:
            return
        new_state = self.get_state(new_rsi)
        old_value = self.q_table[self.last_state, self.last_action.value]
        future_reward = np.max(self.q_table[new_state])
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * future_reward - old_value)
        self.q_table[self.last_state, self.last_action.value] = new_value

    def get_reward(self, profit):
        if profit > 0:
            return 1.0
        elif profit < 0:
            return -1.0
        return 0.0

    def open_trade(self, trade_type):
        # ارسال اهرم به API (در این نسخه فرض می‌کنیم اهرم توی Simulator تنظیم شده)
        response = requests.post(f"{self.api_url}/open_trade", json={"trade_type": trade_type, "is_ai_trade": True})
        if response.status_code == 200:
            trade_id = response.json()["trade_id"]
            print(f"Opened {trade_type} trade with ID {trade_id} and leverage {self.leverage}")
            return trade_id
        return None

    def close_trade(self, trade_id):
        response = requests.post(f"{self.api_url}/close_trade", json={"trade_id": trade_id})
        if response.status_code == 200:
            profit = response.json()["profit"]
            print(f"Closed trade {trade_id} with profit: {profit}")
            return profit
        return None

    def run(self):
        print("AI Trader started. Press Ctrl+C to stop.")
        while True:
            try:
                response = requests.get(f"{self.api_url}/current_data")
                if response.status_code == 200:
                    data = response.json()
                    rsi = data["rsi"]
                    current_price = data["price"]
                else:
                    rsi = 50
                    current_price = None

                action = self.decide_action(rsi)
                profit = 0

                if action == Action.BUY and not self.open_trade_id:
                    self.open_trade_id = self.open_trade("buy")
                elif action == Action.SELL and not self.open_trade_id:
                    self.open_trade_id = self.open_trade("sell")
                elif action == Action.HOLD and self.open_trade_id:
                    profit = self.close_trade(self.open_trade_id)
                    self.open_trade_id = None

                reward = self.get_reward(profit)
                self.update_q_table(reward, rsi)
                time.sleep(1)
            except KeyboardInterrupt:
                print("AI Trader stopped.")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    trader = SimpleTrader(leverage=10)  # اهرم پیش‌فرض 10 برای AI
    trader.run()