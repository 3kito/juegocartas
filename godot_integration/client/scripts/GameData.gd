extends Node
class_name GameData

var phase: String = ""
var gold: int = 0
var time_remaining: float = 0.0
var board_state := []
var shop_cards := []
var auction_data := {}

func update_from_dict(data: Dictionary) -> void:
    if data.has("phase"):
        phase = str(data["phase"])
    if data.has("player_data"):
        var pd = data["player_data"]
        if pd is Dictionary:
            gold = int(pd.get("gold", gold))
    if data.has("time_remaining"):
        time_remaining = float(data["time_remaining"])
    if data.has("board_state"):
        board_state = data["board_state"]
    if data.has("shop_cards"):
        shop_cards = data["shop_cards"]
    if data.has("auction_data"):
        auction_data = data["auction_data"]
