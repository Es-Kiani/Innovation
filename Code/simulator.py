import logging
import os
from datetime import datetime

log_dir = "../Log"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, 'trading_log.log'), level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Trade:
    def __init__(self, trade_id, trade_type, entry_price, size, open_time, spread, commission_per_lot, stop_loss_pips, leverage, is_ai_trade=False):
        self.trade_id = trade_id
        self.trade_type = trade_type
        self.entry_price = entry_price
        self.size = size
        self.open_time = open_time
        self.close_time = None
        self.exit_price = None
        self.spread = spread
        self.commission_per_lot = commission_per_lot
        self.stop_loss_pips = stop_loss_pips
        self.leverage = leverage
        self.is_ai_trade = is_ai_trade

    def get_profit(self, current_price):
        if self.trade_type == "buy":
            profit = (current_price - self.entry_price - self.spread * 0.0001) * self.size * 10000 * self.leverage
        else:  # sell
            profit = (self.entry_price - current_price - self.spread * 0.0001) * self.size * 10000 * self.leverage
        profit -= self.commission_per_lot * self.size
        return profit

    def close(self, exit_price, close_time):
        self.exit_price = exit_price
        self.close_time = close_time
        profit = self.get_profit(exit_price)
        logging.info(f"Trade {self.trade_id} closed: Type={self.trade_type}, Profit={profit:.4f}, Leverage={self.leverage}, AI={self.is_ai_trade}")
        return profit

class Simulator:
    def __init__(self, data_manager, initial_balance=1000, risk_percentage=0.10, spread=2, commission_per_lot=7, leverage=1):
        self.data_manager = data_manager
        self.trades = []
        self.trade_counter = 0
        self.account_balance = initial_balance
        self.risk_percentage = risk_percentage
        self.spread = spread
        self.commission_per_lot = commission_per_lot
        self.leverage = leverage
        logging.info(f"Simulator initialized with balance={initial_balance}, risk={risk_percentage*100}%, leverage={leverage}")

    def set_balance(self, new_balance):
        self.account_balance = new_balance
        logging.info(f"Initial balance updated to {new_balance}")

    def set_leverage(self, leverage):
        self.leverage = leverage
        logging.info(f"Leverage set to {leverage}")

    def calculate_position_size(self, stop_loss_pips):
        pip_value = 10
        risk_amount = self.account_balance * self.risk_percentage
        position_size = (risk_amount / (stop_loss_pips * pip_value)) * self.leverage
        return round(position_size, 2)

    def open_trade(self, trade_type, stop_loss_pips=20, is_ai_trade=False):
        current_data = self.data_manager.get_current_data()
        current_price = self.data_manager.get_current_price()
        if current_data is None or current_price is None:
            return None
        
        self.trade_counter += 1
        size = self.calculate_position_size(stop_loss_pips)
        trade = Trade(self.trade_counter, trade_type, current_price, size, current_data['date_time'], 
                      self.spread, self.commission_per_lot, stop_loss_pips, self.leverage, is_ai_trade)
        self.trades.append(trade)
        logging.info(f"Trade {self.trade_counter} opened: Type={trade_type}, Size={size}, Entry={current_price}, Leverage={self.leverage}, AI={is_ai_trade}")
        return self.trade_counter

    def close_trade(self, trade_id):
        for trade in self.trades:
            if trade.trade_id == trade_id and trade.close_time is None:
                current_data = self.data_manager.get_current_data()
                current_price = self.data_manager.get_current_price()
                if current_data is None or current_price is None:
                    return None
                profit = trade.close(current_price, current_data['date_time'])
                self.account_balance += profit
                logging.info(f"Balance updated to {self.account_balance:.2f} after closing trade {trade_id}")
                return profit
        return None

    def update_trades(self):
        current_price = self.data_manager.get_current_price()
        if current_price is None:
            return
        for trade in self.trades:
            if trade.close_time is None:
                stop_price = trade.entry_price - trade.stop_loss_pips * 0.0001 if trade.trade_type == "buy" else trade.entry_price + trade.stop_loss_pips * 0.0001
                if (trade.trade_type == "buy" and current_price <= stop_price) or (trade.trade_type == "sell" and current_price >= stop_price):
                    profit = trade.close(stop_price, self.data_manager.get_current_data()['date_time'])
                    self.account_balance += profit
                    logging.info(f"Trade {trade.trade_id} hit stop loss. Balance updated to {self.account_balance:.2f}")

    def get_open_trades(self):
        return [trade for trade in self.trades if trade.close_time is None]

    def get_closed_trades(self):
        return [trade for trade in self.trades if trade.close_time is not None and not trade.is_ai_trade]

    def generate_report(self):
        closed_trades = self.get_closed_trades()
        total_profit = sum(trade.get_profit(trade.exit_price) for trade in closed_trades)
        winning_trades = len([t for t in closed_trades if t.get_profit(t.exit_price) > 0])
        losing_trades = len(closed_trades) - winning_trades
        report = (
            f"Trading Report:\n"
            f"Account Balance: {self.account_balance:.2f}\n"
            f"Total Profit: {total_profit:.2f}\n"
            f"Total Trades: {len(closed_trades)}\n"
            f"Winning Trades: {winning_trades}\n"
            f"Losing Trades: {losing_trades}\n"
            f"Win Rate: {winning_trades / len(closed_trades) * 100 if closed_trades else 0:.2f}%\n"
            f"Leverage: {self.leverage}"
        )
        logging.info(report)
        return report