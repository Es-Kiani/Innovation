# trade_history.py
import matplotlib.dates as mdates
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# کلاسی مشابه MplCanvas جهت استفاده در TradeHistoryChart
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class TradeHistoryChart(QtWidgets.QMainWindow):
    def __init__(self, data_manager, simulator):
        super().__init__()
        self.data_manager = data_manager
        self.simulator = simulator
        self.setWindowTitle("Trade History Chart")
        self.canvas = MplCanvas(self, width=8, height=5, dpi=100)
        self.setCentralWidget(self.canvas)
        self.update_chart()

    def update_chart(self):
        data_window = self.data_manager.get_data_window( window_size=len(self.data_manager.data) )
        if data_window.empty:
            return
        self.canvas.axes.clear()
        dates = mdates.date2num(data_window['date_time'])
        ohlc_data = list(zip(dates,
                              data_window['Open'],
                              data_window['High'],
                              data_window['Low'],
                              data_window['Close']))
        # استفاده از mpl_finance برای رسم کندل استیک
        from mpl_finance import candlestick_ohlc
        candlestick_ohlc(self.canvas.axes, ohlc_data, width=0.6/(24*60), colorup='g', colordown='r')
        
        # رسم نقاط معاملات بسته شده به عنوان تاریخچه
        closed_trades = self.simulator.get_closed_trades()
        for trade in closed_trades:
            # رسم نقطه ورود (با علامت دایره آبی)
            entry_time = mdates.date2num(trade.open_time)
            self.canvas.axes.plot(entry_time, trade.entry_price, marker='o', color='blue', markersize=8, label='Entry')
            # رسم نقطه خروج (با علامت ضربدر قرمز)
            exit_time = mdates.date2num(trade.close_time)
            self.canvas.axes.plot(exit_time, trade.exit_price, marker='x', color='red', markersize=8, label='Exit')
        self.canvas.axes.xaxis_date()
        self.canvas.axes.legend()
        self.canvas.draw()

class TradeHistoryList(QtWidgets.QMainWindow):
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.setWindowTitle("Trade History List")
        self.table = QtWidgets.QTableWidget()
        self.setCentralWidget(self.table)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Trade ID", "Type", "Entry Price", "Exit Price", "Profit", "Open Time", "Close Time"])
        self.update_list()

    def update_list(self):
        closed_trades = self.simulator.get_closed_trades()
        self.table.setRowCount(len(closed_trades))
        for row, trade in enumerate(closed_trades):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(trade.trade_id)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(trade.trade_type))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{trade.entry_price:.2f}"))
            exit_price = f"{trade.exit_price:.2f}" if trade.exit_price is not None else ""
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(exit_price))
            # سود/ضرر نهایی
            profit = trade.get_profit(trade.exit_price) if trade.exit_price is not None else 0
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{profit:.2f}"))
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(str(trade.open_time)))
            self.table.setItem(row, 6, QtWidgets.QTableWidgetItem(str(trade.close_time)))
