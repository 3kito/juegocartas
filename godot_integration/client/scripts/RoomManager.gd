extends Node
class_name RoomManager

var room_id: String = ""
var base_url: String = "http://localhost:8000"

func join_room(id: String, player_id: int) -> void:
    room_id = id
    var http := HTTPRequest.new()
    add_child(http)
    var body = {"player_id": player_id}
    http.request(base_url + "/rooms/" + id + "/join", [], HTTPClient.METHOD_POST, JSON.stringify(body))
    http.queue_free()
