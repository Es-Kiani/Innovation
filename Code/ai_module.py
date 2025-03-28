import numpy as np
from enum import Enum

# اقدامات ممکن برای عامل
class Action(Enum):
    BUY = 0
    SELL = 1
    HOLD = 2

class SimpleTrader:
    def __init__(self, rsi_threshold_low=30, rsi_threshold_high=70, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.rsi_threshold_low = rsi_threshold_low  # آستانه پایین RSI برای خرید
        self.rsi_threshold_high = rsi_threshold_high  # آستانه بالا RSI برای فروش
        self.learning_rate = learning_rate  # نرخ یادگیری
        self.discount_factor = discount_factor  # فاکتور تخفیف برای پاداش آینده
        self.epsilon = epsilon  # احتمال اکتشاف تصادفی (Exploration)
        # جدول Q برای یادگیری (حالت‌ها: RSI در سه بازه - پایین، نرمال، بالا)
        self.q_table = np.zeros((3, len(Action)))  # 3 حالت برای RSI و 3 اقدام
        self.last_action = None
        self.last_state = None

    def get_state(self, rsi):
        """تبدیل مقدار RSI به یک حالت گسسته"""
        if rsi < self.rsi_threshold_low:
            return 0  # اشباع فروش
        elif rsi > self.rsi_threshold_high:
            return 2  # اشباع خرید
        else:
            return 1  # حالت نرمال

    def decide_action(self, rsi, balance, open_trades):
        """تصمیم‌گیری برای اقدام بعدی"""
        current_state = self.get_state(rsi)

        # استراتژی epsilon-greedy برای تعادل بین اکتشاف و بهره‌برداری
        if np.random.random() < self.epsilon:
            action = np.random.choice(list(Action))
        else:
            action = Action(np.argmax(self.q_table[current_state]))

        # اعمال محدودیت: اگر معامله باز داریم، فقط می‌تونیم نگه داریم یا ببندیم
        if len(open_trades) > 0:
            return Action.HOLD  # برای سادگی، فعلاً فقط نگه می‌داریم

        self.last_state = current_state
        self.last_action = action
        return action

    def update_q_table(self, reward, new_rsi):
        """به‌روزرسانی جدول Q بر اساس پاداش"""
        if self.last_state is None or self.last_action is None:
            return

        new_state = self.get_state(new_rsi)
        old_value = self.q_table[self.last_state, self.last_action.value]
        future_reward = np.max(self.q_table[new_state])
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * future_reward - old_value)
        self.q_table[self.last_state, self.last_action.value] = new_value

    def get_reward(self, profit, balance_change):
        """محاسبه پاداش بر اساس سود و تغییر بالانس"""
        if profit > 0:
            return 1.0  # پاداش مثبت برای سود
        elif profit < 0:
            return -1.0  # جریمه برای ضرر
        return 0.0  # بدون تغییر