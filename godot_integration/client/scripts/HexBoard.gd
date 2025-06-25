extends Node3D
class_name HexBoard

signal cell_clicked(q: int, r: int)

func _ready() -> void:
    pass

func _on_cell_input(event: InputEvent, q: int, r: int) -> void:
    if event is InputEventMouseButton and event.pressed:
        emit_signal("cell_clicked", q, r)
