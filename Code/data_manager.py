import pandas as pd

class DataManager:
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file, parse_dates=[['date', 'time']])
        self.data.sort_values('date_time', inplace=True)
        self.current_index = 0
        self.sub_index = 0

    def get_current_data(self):
        if self.current_index < len(self.data):
            return self.data.iloc[self.current_index]
        return None

    def get_current_price(self):
        if self.current_index >= len(self.data):
            return None
        row = self.data.iloc[self.current_index]
        if self.sub_index == 0:
            return row['Open']
        elif self.sub_index == 1:
            return row['High'] if row['Close'] >= row['Open'] else row['Low']
        elif self.sub_index == 2:
            return row['Low'] if row['Close'] >= row['Open'] else row['High']
        elif self.sub_index == 3:
            return row['Close']
        return None

    def step_forward(self, steps=1):
        for _ in range(steps):
            if self.sub_index < 3:
                self.sub_index += 1
            else:
                self.sub_index = 0
                self.current_index = min(self.current_index + 1, len(self.data) - 1)

    def step_backward(self, steps=1):
        for _ in range(steps):
            if self.sub_index > 0:
                self.sub_index -= 1
            else:
                self.sub_index = 3
                self.current_index = max(self.current_index - 1, 0)

    def get_data_window(self, window_size=100):  # حداکثر 100 کندل
        start = max(self.current_index - window_size + 1, 0)
        return self.data.iloc[start:self.current_index + 1]