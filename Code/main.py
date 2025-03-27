import sys
from PyQt5 import QtWidgets
from data_manager import DataManager
from simulator import Simulator
from dashboard import Dashboard
from api import create_api
import threading

def run_api(simulator):
    app = create_api(simulator)
    app.run(port=5000, debug=False, use_reloader=False)

def main():
    data_manager = DataManager("D:/Innovation/Dataset/AUDCAD_Dataset.csv")
    simulator = Simulator(data_manager)

    api_thread = threading.Thread(target=run_api, args=(simulator,))
    api_thread.setDaemon(True)
    api_thread.start()

    app = QtWidgets.QApplication(sys.argv)
    dashboard = Dashboard(data_manager, simulator)
    dashboard.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
