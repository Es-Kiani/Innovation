from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from concurrent.futures import ThreadPoolExecutor
import queue

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.ax2 = self.axes.twinx()
        super(MplCanvas, self).__init__(self.fig)
        self.last_drawn_index = -1
        self.candles = None
        self.line = None
        self.sma20_line = None
        self.sma50_line = None
        self.sma200_line = None
        self.rsi_line = None
        self.macd_line = None

class Dashboard(QtWidgets.QMainWindow):
    def __init__(self, data_manager, simulator):
        super().__init__()
        self.data_manager = data_manager
        self.simulator = simulator
        self.trade_history_chart_window = None
        self.trade_history_list_window = None
        self.is_playing = False
        self.play_speed = 500
        self.show_rsi = False  # پیش‌فرض غیرفعال
        self.show_macd = False  # پیش‌فرض غیرفعال
        self.show_sma20 = False  # پیش‌فرض غیرفعال
        self.show_sma50 = False  # پیش‌فرض غیرفعال
        self.show_sma200 = False  # پیش‌فرض غیرفعال
        self.use_candlestick = True
        self.data_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=50)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AUD/CAD Trading Simulator")
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout()

        self.canvas = MplCanvas(self, width=8, height=5, dpi=100)
        main_layout.addWidget(self.canvas)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.data_manager.data) - 1)
        self.slider.setValue(self.data_manager.current_index)
        self.slider.valueChanged.connect(self.slider_moved)
        main_layout.addWidget(self.slider)

        controls_layout = QtWidgets.QHBoxLayout()
        self.btn_backward = QtWidgets.QPushButton("Backward")
        self.btn_forward = QtWidgets.QPushButton("Forward")
        self.btn_play = QtWidgets.QPushButton("Play")
        self.btn_stop = QtWidgets.QPushButton("Stop")
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed_slider.setMinimum(1000)
        self.speed_slider.setMaximum(5000)
        self.speed_slider.setValue(self.play_speed)
        self.speed_slider.setTickInterval(150)
        self.speed_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.speed_label = QtWidgets.QLabel("Speed (ms):")
        self.btn_open_buy = QtWidgets.QPushButton("Open Buy")
        self.btn_open_sell = QtWidgets.QPushButton("Open Sell")
        self.btn_close_trade = QtWidgets.QPushButton("Close Trade (by ID)")
        self.trade_id_input = QtWidgets.QLineEdit()
        self.trade_id_input.setPlaceholderText("Trade ID")
        self.btn_report = QtWidgets.QPushButton("Generate Report")
        controls_layout.addWidget(self.btn_backward)
        controls_layout.addWidget(self.btn_forward)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.speed_label)
        controls_layout.addWidget(self.speed_slider)
        controls_layout.addWidget(self.btn_open_buy)
        controls_layout.addWidget(self.btn_open_sell)
        controls_layout.addWidget(self.trade_id_input)
        controls_layout.addWidget(self.btn_close_trade)
        controls_layout.addWidget(self.btn_report)
        
        self.btn_trade_history_chart = QtWidgets.QPushButton("Trade History Chart")
        self.btn_trade_history_list = QtWidgets.QPushButton("Trade History List")
        controls_layout.addWidget(self.btn_trade_history_chart)
        controls_layout.addWidget(self.btn_trade_history_list)
        
        main_layout.addLayout(controls_layout)

        self.status_label = QtWidgets.QLabel("System Status: ")
        self.current_price_label = QtWidgets.QLabel("Current Price: ")
        self.balance_label = QtWidgets.QLabel(f"Balance: {self.simulator.account_balance:.2f}")
        status_layout = QtWidgets.QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.current_price_label)
        status_layout.addWidget(self.balance_label)
        main_layout.addLayout(status_layout)

        risk_layout = QtWidgets.QHBoxLayout()
        self.risk_label = QtWidgets.QLabel("Risk %:")
        self.risk_input = QtWidgets.QLineEdit("10")  # پیش‌فرض 10%
        self.stop_loss_label = QtWidgets.QLabel("Stop Loss (pips):")
        self.stop_loss_input = QtWidgets.QLineEdit("20")
        self.leverage_label = QtWidgets.QLabel("Leverage:")
        self.leverage_input = QtWidgets.QLineEdit("1")
        risk_layout.addWidget(self.risk_label)
        risk_layout.addWidget(self.risk_input)
        risk_layout.addWidget(self.stop_loss_label)
        risk_layout.addWidget(self.stop_loss_input)
        risk_layout.addWidget(self.leverage_label)
        risk_layout.addWidget(self.leverage_input)
        main_layout.addLayout(risk_layout)

        self.open_trades_table = QtWidgets.QTableWidget()
        self.open_trades_table.setColumnCount(7)
        self.open_trades_table.setHorizontalHeaderLabels(["Trade ID", "Type", "Entry Price", "Size", "P&L", "Leverage", "Status"])
        main_layout.addWidget(self.open_trades_table)

        central_widget.setLayout(main_layout)

        menubar = self.menuBar()
        indicators_menu = menubar.addMenu('Indicators')
        settings_menu = menubar.addMenu('Settings')
        chart_menu = menubar.addMenu('Chart Type')
        
        self.rsi_action = QtWidgets.QAction('Show RSI', self, checkable=True)
        self.rsi_action.setChecked(False)  # پیش‌فرض غیرفعال
        self.rsi_action.triggered.connect(self.toggle_rsi)
        self.macd_action = QtWidgets.QAction('Show MACD', self, checkable=True)
        self.macd_action.setChecked(False)  # پیش‌فرض غیرفعال
        self.macd_action.triggered.connect(self.toggle_macd)
        self.sma20_action = QtWidgets.QAction('Show SMA20', self, checkable=True)
        self.sma20_action.setChecked(False)  # پیش‌فرض غیرفعال
        self.sma20_action.triggered.connect(self.toggle_sma20)
        self.sma50_action = QtWidgets.QAction('Show SMA50', self, checkable=True)
        self.sma50_action.setChecked(False)  # پیش‌فرض غیرفعال
        self.sma50_action.triggered.connect(self.toggle_sma50)
        self.sma200_action = QtWidgets.QAction('Show SMA200', self, checkable=True)
        self.sma200_action.setChecked(False)  # پیش‌فرض غیرفعال
        self.sma200_action.triggered.connect(self.toggle_sma200)
        indicators_menu.addAction(self.rsi_action)
        indicators_menu.addAction(self.macd_action)
        indicators_menu.addAction(self.sma20_action)
        indicators_menu.addAction(self.sma50_action)
        indicators_menu.addAction(self.sma200_action)

        self.balance_action = QtWidgets.QAction('Set Initial Balance', self)
        self.balance_action.triggered.connect(self.set_initial_balance)
        settings_menu.addAction(self.balance_action)

        self.candlestick_action = QtWidgets.QAction('Candlestick', self, checkable=True)
        self.candlestick_action.setChecked(True)
        self.candlestick_action.triggered.connect(self.set_candlestick)
        self.line_action = QtWidgets.QAction('Line (Close Price)', self, checkable=True)
        self.line_action.triggered.connect(self.set_line)
        chart_menu.addAction(self.candlestick_action)
        chart_menu.addAction(self.line_action)

        self.btn_forward.clicked.connect(self.step_forward)
        self.btn_backward.clicked.connect(self.step_backward)
        self.btn_play.clicked.connect(self.start_playing)
        self.btn_stop.clicked.connect(self.stop_playing)
        self.speed_slider.valueChanged.connect(self.set_play_speed)
        self.btn_open_buy.clicked.connect(lambda: self.open_trade("buy"))
        self.btn_open_sell.clicked.connect(lambda: self.open_trade("sell"))
        self.btn_close_trade.clicked.connect(self.close_trade)
        self.btn_trade_history_chart.clicked.connect(self.open_trade_history_chart)
        self.btn_trade_history_list.clicked.connect(self.open_trade_history_list)
        self.btn_report.clicked.connect(self.show_report)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start()

    def set_initial_balance(self):
        balance, ok = QtWidgets.QInputDialog.getDouble(
            self, "Set Initial Balance", "Enter initial balance:", 
            self.simulator.account_balance, 0, 1000000, 2
        )
        if ok:
            self.simulator.set_balance(balance)
            self.balance_label.setText(f"Balance: {self.simulator.account_balance:.2f}")
            self.status_label.setText(f"Initial balance set to {balance:.2f}")

    def toggle_rsi(self):
        self.show_rsi = self.rsi_action.isChecked()
        self.update_plot()

    def toggle_macd(self):
        self.show_macd = self.macd_action.isChecked()
        self.update_plot()

    def toggle_sma20(self):
        self.show_sma20 = self.sma20_action.isChecked()
        self.update_plot()

    def toggle_sma50(self):
        self.show_sma50 = self.sma50_action.isChecked()
        self.update_plot()

    def toggle_sma200(self):
        self.show_sma200 = self.sma200_action.isChecked()
        self.update_plot()

    def set_candlestick(self):
        self.use_candlestick = True
        self.candlestick_action.setChecked(True)
        self.line_action.setChecked(False)
        self.update_plot()

    def set_line(self):
        self.use_candlestick = False
        self.candlestick_action.setChecked(False)
        self.line_action.setChecked(True)
        self.update_plot()

    def slider_moved(self, value):
        self.data_manager.current_index = value
        self.data_manager.sub_index = 0
        self.fetch_data()

    def step_forward(self):
        self.data_manager.step_forward()
        self.slider.setValue(self.data_manager.current_index)
        self.fetch_data()

    def step_backward(self):
        self.data_manager.step_backward()
        self.slider.setValue(self.data_manager.current_index)
        self.fetch_data()

    def start_playing(self):
        self.is_playing = True
        self.timer.setInterval(self.play_speed)

    def stop_playing(self):
        self.is_playing = False
        self.timer.setInterval(500)

    def set_play_speed(self, value):
        self.play_speed = value
        if self.is_playing:
            self.timer.setInterval(self.play_speed)

    def open_trade(self, trade_type):
        try:
            risk_percentage = float(self.risk_input.text()) / 100
            stop_loss_pips = float(self.stop_loss_input.text())
            leverage = float(self.leverage_input.text())
            self.simulator.risk_percentage = risk_percentage
            self.simulator.set_leverage(leverage)
            trade_id = self.simulator.open_trade(trade_type, stop_loss_pips)
            if trade_id:
                size = self.simulator.calculate_position_size(stop_loss_pips)
                self.status_label.setText(f"Opened {trade_type} trade with ID {trade_id}, leverage {leverage}, size {size}")
            else:
                self.status_label.setText("Failed to open trade.")
            self.fetch_data()
        except ValueError:
            self.status_label.setText("Invalid Risk, Stop Loss, or Leverage value")

    def close_trade(self):
        trade_id_text = self.trade_id_input.text()
        try:
            trade_id = int(trade_id_text)
        except:
            self.status_label.setText("Invalid Trade ID")
            return
        profit = self.simulator.close_trade(trade_id)
        if profit is not None:
            self.status_label.setText(f"Closed trade {trade_id} with profit: {profit:.4f}")
            self.balance_label.setText(f"Balance: {self.simulator.account_balance:.2f}")
        else:
            self.status_label.setText("Trade not found or already closed.")
        self.fetch_data()

    def open_trade_history_chart(self):
        from trade_history import TradeHistoryChart
        self.trade_history_chart_window = TradeHistoryChart(self.data_manager, self.simulator)
        self.trade_history_chart_window.show()

    def open_trade_history_list(self):
        from trade_history import TradeHistoryList
        self.trade_history_list_window = TradeHistoryList(self.simulator)
        self.trade_history_list_window.show()

    def show_report(self):
        report = self.simulator.generate_report()
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Trading Report")
        msg.setText(report)
        msg.exec_()

    def fetch_data(self):
        def fetch_data_worker():
            data_window = self.data_manager.get_data_window()
            current_data = self.data_manager.get_current_data()
            current_price = self.data_manager.get_current_price()
            self.data_queue.put((data_window, current_data, current_price))

        def fetch_trades_worker():
            open_trades = self.simulator.get_open_trades()
            closed_trades = self.simulator.get_closed_trades()
            self.data_queue.put((None, None, None, open_trades, closed_trades))

        self.executor.submit(fetch_data_worker)
        self.executor.submit(fetch_trades_worker)

    def update_plot(self):
        while not self.data_queue.empty():
            data = self.data_queue.get()
            if len(data) == 3:
                data_window, current_data, current_price = data
                open_trades = self.simulator.get_open_trades()
                closed_trades = self.simulator.get_closed_trades()
            else:
                _, _, _, open_trades, closed_trades = data
                data_window = self.data_manager.get_data_window()
                current_data = self.data_manager.get_current_data()
                current_price = self.data_manager.get_current_price()

            if not data_window.empty:
                dates = mdates.date2num(data_window['date_time'])

                if self.canvas.last_drawn_index != self.data_manager.current_index:
                    self.canvas.axes.clear()
                    self.canvas.ax2.clear()
                    if self.use_candlestick:
                        ohlc_data = list(zip(dates, data_window['Open'], data_window['High'], 
                                             data_window['Low'], data_window['Close']))
                        from mpl_finance import candlestick_ohlc
                        self.canvas.candles = candlestick_ohlc(self.canvas.axes, ohlc_data, 
                                                               width=0.6/(24*60), colorup='g', colordown='r')
                        self.canvas.line = None
                    else:
                        self.canvas.line, = self.canvas.axes.plot(dates, data_window['Close'], color='blue', label='Close Price')
                        self.canvas.candles = None
                    
                    self.canvas.axes.set_ylabel('Price', color='black')
                    self.canvas.axes.yaxis.set_label_position('left')
                    self.canvas.axes.tick_params(axis='y', labelcolor='black', which='both', left=True, right=False)
                    self.canvas.ax2.set_ylabel('RSI / MACD', color='black')
                    self.canvas.ax2.yaxis.set_label_position('right')
                    self.canvas.ax2.tick_params(axis='y', labelcolor='black', which='both', left=False, right=True)
                    self.canvas.last_drawn_index = self.data_manager.current_index

                # چک کردن وجود ستون‌ها قبل از رسم
                if self.show_sma20 and 'sma20' in data_window.columns and not data_window['sma20'].isna().all():
                    if self.canvas.sma20_line is None:
                        self.canvas.sma20_line, = self.canvas.axes.plot(dates, data_window['sma20'], label='SMA20', color='orange')
                    else:
                        self.canvas.sma20_line.set_data(dates, data_window['sma20'])
                elif self.canvas.sma20_line:
                    self.canvas.sma20_line.set_data([], [])
                
                if self.show_sma50 and 'sma50' in data_window.columns and not data_window['sma50'].isna().all():
                    if self.canvas.sma50_line is None:
                        self.canvas.sma50_line, = self.canvas.axes.plot(dates, data_window['sma50'], label='SMA50', color='purple')
                    else:
                        self.canvas.sma50_line.set_data(dates, data_window['sma50'])
                elif self.canvas.sma50_line:
                    self.canvas.sma50_line.set_data([], [])
                
                if self.show_sma200 and 'sma200' in data_window.columns and not data_window['sma200'].isna().all():
                    if self.canvas.sma200_line is None:
                        self.canvas.sma200_line, = self.canvas.axes.plot(dates, data_window['sma200'], label='SMA200', color='blue')
                    else:
                        self.canvas.sma200_line.set_data(dates, data_window['sma200'])
                elif self.canvas.sma200_line:
                    self.canvas.sma200_line.set_data([], [])

                if self.show_rsi and 'rsi14' in data_window.columns and not data_window['rsi14'].isna().all():
                    if self.canvas.rsi_line is None:
                        self.canvas.rsi_line, = self.canvas.ax2.plot(dates, data_window['rsi14'], label='RSI14', color='green', linestyle='--')
                        self.canvas.ax2.set_ylim(0, 100)
                    else:
                        self.canvas.rsi_line.set_data(dates, data_window['rsi14'])
                elif self.canvas.rsi_line:
                    self.canvas.rsi_line.set_data([], [])

                if self.show_macd and 'MACD' in data_window.columns and not data_window['MACD'].isna().all():
                    if self.canvas.macd_line is None:
                        self.canvas.macd_line, = self.canvas.ax2.plot(dates, data_window['MACD'], label='MACD', color='red', linestyle='-')
                    else:
                        self.canvas.macd_line.set_data(dates, data_window['MACD'])
                elif self.canvas.macd_line:
                    self.canvas.macd_line.set_data([], [])

                for collection in self.canvas.axes.collections[:]:
                    collection.remove()
                window_start = data_window['date_time'].iloc[0]
                window_end = data_window['date_time'].iloc[-1]
                for trade in closed_trades:
                    if window_start <= trade.open_time <= window_end:
                        entry_time = mdates.date2num(trade.open_time)
                        self.canvas.axes.plot(entry_time, trade.entry_price, marker='o', color='blue', markersize=8)
                    if trade.close_time and window_start <= trade.close_time <= window_end:
                        exit_time = mdates.date2num(trade.close_time)
                        self.canvas.axes.plot(exit_time, trade.exit_price, marker='x', color='red', markersize=8)

                self.canvas.axes.set_xlim(dates[0] - 0.5, dates[-1] + 0.5)
                self.canvas.axes.xaxis_date()
                lines, labels = self.canvas.axes.get_legend_handles_labels()
                lines2, labels2 = self.canvas.ax2.get_legend_handles_labels()
                self.canvas.axes.legend(lines + lines2, labels + labels2, loc='upper left')
                self.canvas.fig.tight_layout()
                self.canvas.draw()

                self.open_trades_table.setRowCount(len(open_trades))
                for row, trade in enumerate(open_trades):
                    current_pnl = trade.get_profit(current_price) if current_price is not None else 0
                    self.open_trades_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(trade.trade_id)))
                    self.open_trades_table.setItem(row, 1, QtWidgets.QTableWidgetItem(trade.trade_type))
                    self.open_trades_table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{trade.entry_price:.5f}"))
                    self.open_trades_table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{trade.size:.2f}"))
                    self.open_trades_table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{current_pnl:.2f}"))
                    self.open_trades_table.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{trade.leverage}"))
                    self.open_trades_table.setItem(row, 6, QtWidgets.QTableWidgetItem("Open (AI)" if trade.is_ai_trade else "Open"))

    def update_dashboard(self):
        if self.is_playing:
            self.step_forward()
        self.executor.submit(self.simulator.update_trades)
        self.fetch_data()
        self.update_plot()
        current_price = self.data_manager.get_current_price()
        if current_price is not None:
            self.current_price_label.setText(f"Current Price: {current_price:.5f}")
        else:
            self.current_price_label.setText("Current Price: N/A")
        self.balance_label.setText(f"Balance: {self.simulator.account_balance:.2f}")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.step_backward()
        elif event.key() == QtCore.Qt.Key_Right:
            self.step_forward()
        else:
            super(Dashboard, self).keyPressEvent(event)

    def closeEvent(self, event):
        self.executor.shutdown()
        super().closeEvent(event)