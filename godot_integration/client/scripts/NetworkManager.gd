extends Node
class_name NetworkManager

var url: String = "ws://localhost:8000/ws"
var _client := WebSocketClient.new()
var _reconnect_timer: Timer
var game_data: GameData

func _ready() -> void:
    game_data = GameData.new()
    _reconnect_timer = Timer.new()
    _reconnect_timer.wait_time = 2.0
    _reconnect_timer.one_shot = true
    add_child(_reconnect_timer)
    _reconnect_timer.connect("timeout", Callable(self, "_on_reconnect_timeout"))
    _client.connect("connection_closed", Callable(self, "_on_connection_closed"))
    _client.connect("connection_error", Callable(self, "_on_connection_error"))
    _client.connect("connection_established", Callable(self, "_on_connected"))
    _client.connect("data_received", Callable(self, "_on_data_received"))
    _connect()

func _process(delta: float) -> void:
    if _client.get_connection_status() != WebSocketClient.CONNECTION_DISCONNECTED:
        _client.poll()

func _connect() -> void:
    print("[Network] Connecting to %s" % url)
    var err = _client.connect_to_url(url)
    if err != OK:
        print("[Network] Connection failed: %s" % err)
        _schedule_reconnect()

func _on_connected(protocol: String) -> void:
    print("[Network] Connected")

func _on_connection_closed(was_clean: bool) -> void:
    print("[Network] Connection closed")
    _schedule_reconnect()

func _on_connection_error() -> void:
    print("[Network] Connection error")
    _schedule_reconnect()

func _on_data_received() -> void:
    var peer = _client.get_peer(1)
    if peer == null:
        return
    while peer.get_available_packet_count() > 0:
        var pkt = peer.get_packet()
        var text = pkt.get_string_from_utf8()
        _handle_message(text)

func _handle_message(text: String) -> void:
    var result = JSON.parse_string(text)
    if typeof(result) == TYPE_DICTIONARY:
        var data: Dictionary = result
        if data.get("type", "") == "game_state":
            game_data.update_from_dict(data)
            print("Fase: %s" % game_data.phase)
            print("Oro: %d" % game_data.gold)
            print("Tiempo restante: %f" % game_data.time_remaining)
        else:
            print("[Network] Received: %s" % text)
    else:
        print("[Network] Non-JSON message: %s" % text)

func _schedule_reconnect() -> void:
    if not _reconnect_timer.is_stopped():
        return
    print("[Network] Attempting to reconnect in %s seconds" % _reconnect_timer.wait_time)
    _reconnect_timer.start()

func _on_reconnect_timeout() -> void:
    _connect()
