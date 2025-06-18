import tkinter as tk
from tkinter import ttk

class VentanaTesteo:
    def __init__(self, motor_juego, jugador_actual_callback, on_close=None):
        self.motor = motor_juego
        self.jugador_actual_callback = jugador_actual_callback
        self.on_close = on_close

        self.window = tk.Toplevel()
        self.window.title("Auto-Battler - Controles de Testeo")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        self.window.bind("<Unmap>", self._evitar_minimizar)

        screen_width = self.window.winfo_screenwidth()
        x = screen_width - 400 - 10
        self.window.geometry(f"400x300+{x}+0")

        self._after_id = None

        self._construir_widgets()
        self.actualizar_informacion()

    def _construir_widgets(self):
        self.lbl_estado = ttk.Label(self.window, text="Estado: -")
        self.lbl_estado.pack(anchor="w", padx=10, pady=(10, 0))
        self.lbl_proximo = ttk.Label(self.window, text="Próximo Paso: -")
        self.lbl_proximo.pack(anchor="w", padx=10)
        self.lbl_turno = ttk.Label(self.window, text="Turno Activo: -")
        self.lbl_turno.pack(anchor="w", padx=10)

        ttk.Button(self.window, text="Ejecutar Siguiente Paso", command=self.ejecutar_paso).pack(pady=(5, 0))
        ttk.Button(self.window, text="Oro Infinito", command=self.asignar_oro_infinito).pack(pady=2)
        ttk.Button(self.window, text="Tokens Infinitos", command=self.asignar_tokens_infinitos).pack(pady=2)

        self.lbl_jugador = ttk.Label(self.window, text="Jugador Actual: -")
        self.lbl_jugador.pack(anchor="w", padx=10, pady=(10, 0))
        self.lbl_recursos = ttk.Label(self.window, text="Oro: - | Tokens: -")
        self.lbl_recursos.pack(anchor="w", padx=10)

    def _evitar_minimizar(self, event):
        if self.window.state() == "iconic":
            self.window.after(0, self.window.deiconify)

    def actualizar_informacion(self):
        jugador = self.jugador_actual_callback()
        if jugador:
            self.lbl_jugador.config(text=f"Jugador Actual: {jugador.nombre}")
            self.lbl_recursos.config(text=f"Oro: {jugador.oro} | Tokens: {jugador.tokens_reroll}")
        if self.motor:
            try:
                proximo = self.motor.describir_proximo_paso()
            except Exception:
                proximo = "-"
            self.lbl_proximo.config(text=f"Próximo Paso: {proximo}")
            self.lbl_estado.config(text=f"Estado: {self.motor.fase_actual}")
            turno = "-"
            if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
                t = self.motor.controlador_enfrentamiento.obtener_turno_activo()
                if t:
                    turno = t
            self.lbl_turno.config(text=f"Turno Activo: {turno}")
        self._after_id = self.window.after(500, self.actualizar_informacion)

    def ejecutar_paso(self):
        if self.motor:
            self.motor.ejecutar_siguiente_paso()

    def asignar_oro_infinito(self):
        jugador = self.jugador_actual_callback()
        if jugador:
            jugador.oro = 999999

    def asignar_tokens_infinitos(self):
        jugador = self.jugador_actual_callback()
        if jugador:
            jugador.tokens_reroll = 999

    def cerrar_ventana(self):
        if self._after_id:
            self.window.after_cancel(self._after_id)
            self._after_id = None
        if self.on_close:
            self.on_close()
        self.window.destroy()


class PanelTesteo(ttk.Frame):
    """Panel de testeo incrustado en la interfaz principal."""

    def __init__(self, master, motor_juego, jugador_actual_callback):
        super().__init__(master)
        self.motor = motor_juego
        self.jugador_actual_callback = jugador_actual_callback
        self._after_id = None

        self._construir_widgets()
        self.actualizar_informacion()

    def _construir_widgets(self):
        self.lbl_estado = ttk.Label(self, text="Estado: -")
        self.lbl_estado.pack(anchor="w", padx=10, pady=(10, 0))
        self.lbl_proximo = ttk.Label(self, text="Próximo Paso: -")
        self.lbl_proximo.pack(anchor="w", padx=10)
        self.lbl_turno = ttk.Label(self, text="Turno Activo: -")
        self.lbl_turno.pack(anchor="w", padx=10)

        ttk.Button(self, text="Ejecutar Siguiente Paso", command=self.ejecutar_paso).pack(pady=(5, 0))
        ttk.Button(self, text="Oro Infinito", command=self.asignar_oro_infinito).pack(pady=2)
        ttk.Button(self, text="Tokens Infinitos", command=self.asignar_tokens_infinitos).pack(pady=2)

        self.lbl_jugador = ttk.Label(self, text="Jugador Actual: -")
        self.lbl_jugador.pack(anchor="w", padx=10, pady=(10, 0))
        self.lbl_recursos = ttk.Label(self, text="Oro: - | Tokens: -")
        self.lbl_recursos.pack(anchor="w", padx=10)

    def actualizar_informacion(self):
        jugador = self.jugador_actual_callback()
        if jugador:
            self.lbl_jugador.config(text=f"Jugador Actual: {jugador.nombre}")
            self.lbl_recursos.config(text=f"Oro: {jugador.oro} | Tokens: {jugador.tokens_reroll}")
        if self.motor:
            try:
                proximo = self.motor.describir_proximo_paso()
            except Exception:
                proximo = "-"
            self.lbl_proximo.config(text=f"Próximo Paso: {proximo}")
            self.lbl_estado.config(text=f"Estado: {self.motor.fase_actual}")
            turno = "-"
            if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
                t = self.motor.controlador_enfrentamiento.obtener_turno_activo()
                if t:
                    turno = t
            self.lbl_turno.config(text=f"Turno Activo: {turno}")
        self._after_id = self.after(500, self.actualizar_informacion)

    def ejecutar_paso(self):
        if self.motor:
            self.motor.ejecutar_siguiente_paso()

    def asignar_oro_infinito(self):
        jugador = self.jugador_actual_callback()
        if jugador:
            jugador.oro = 999999

    def asignar_tokens_infinitos(self):
        jugador = self.jugador_actual_callback()
        if jugador:
            jugador.tokens_reroll = 999

    def detener(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
