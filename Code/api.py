from flask import Flask, request, jsonify

def create_api(simulator):
    app = Flask(__name__)

    @app.route('/open_trade', methods=['POST'])
    def open_trade():
        data = request.json
        trade_type = data.get("trade_type")
        if trade_type not in ["buy", "sell"]:
            return jsonify({"error": "Invalid trade type"}), 400
        trade_id = simulator.open_trade(trade_type)
        if trade_id:
            return jsonify({"trade_id": trade_id}), 200
        else:
            return jsonify({"error": "Unable to open trade"}), 400

    @app.route('/close_trade', methods=['POST'])
    def close_trade():
        data = request.json
        trade_id = data.get("trade_id")
        try:
            trade_id = int(trade_id)
        except:
            return jsonify({"error": "Invalid trade ID"}), 400
        profit = simulator.close_trade(trade_id)
        if profit is not None:
            return jsonify({"profit": profit}), 200
        else:
            return jsonify({"error": "Trade not found or already closed"}), 400

    return app
