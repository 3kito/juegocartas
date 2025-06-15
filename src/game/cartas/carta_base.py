"""
Clase base para todas las cartas del juego
"""

from typing import List, Dict, Any

from src.game.combate.interacciones.interaccion_modelo import TipoInteraccion, Interaccion
from src.utils.helpers import log_evento

class Habilidad:
    """Representa una habilidad de carta"""

    def __init__(self, datos_habilidad: Dict[str, Any]):
        self.nombre = datos_habilidad.get('nombre', 'Habilidad Sin Nombre')
        self.tipo = datos_habilidad.get('tipo', 'pasiva')  # 'activa' o 'pasiva'
        self.descripcion = datos_habilidad.get('descripcion', '')

        # Propiedades para habilidades activas
        self.costo_mana = datos_habilidad.get('costo_mana', 0)
        self.cooldown = datos_habilidad.get('cooldown', 0)
        self.cooldown_actual = 0
        self.rango = datos_habilidad.get('rango', 1)
        self.duracion = datos_habilidad.get('duracion', 0)


        # Propiedades para habilidades pasivas
        self.trigger = datos_habilidad.get('trigger', 'permanente')
        self.area = datos_habilidad.get('area', 'single')

        # Propiedades especiales
        self.propiedades = {k: v for k, v in datos_habilidad.items()
                            if k not in ['nombre', 'tipo', 'descripcion', 'costo_mana',
                                         'cooldown', 'rango', 'duracion', 'trigger', 'area']}

    def puede_usar(self) -> bool:
        """Verifica si la habilidad puede ser usada"""
        if self.tipo == 'activa':
            return self.cooldown_actual <= 0
        return True


    def usar(self):
        """Marca la habilidad como usada (inicia cooldown)"""
        if self.tipo == 'activa':
            self.cooldown_actual = self.cooldown
            log_evento(f"Habilidad '{self.nombre}' usada (Cooldown: {self.cooldown})")

    def reducir_cooldown(self):
        """Reduce el cooldown en 1"""
        if self.cooldown_actual > 0:
            self.cooldown_actual -= 1

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    def __repr__(self):
        return f"Habilidad(nombre='{self.nombre}', tipo='{self.tipo}')"


class CartaBase:
    """Clase base para todas las cartas del juego"""

    def __init__(self, datos_carta: Dict[str, Any]):
        # Identificación
        self.duenio = None
        self.id = datos_carta.get('id', 0)
        self.nombre = datos_carta.get('nombre', 'Carta Sin Nombre')
        self.descripcion = datos_carta.get('descripcion', '')

        # Metadatos
        self.tier = datos_carta.get('tier', 1)
        self.costo = datos_carta.get('costo', 1)
        self.rol = datos_carta.get('rol', 'basico')
        self.categoria = datos_carta.get('categoria', 'general')

        # Stats base (de los datos JSON)
        stats_data = datos_carta.get('stats', {})
        self.vida_maxima = stats_data.get('vida', 100)
        self.vida_actual = self.vida_maxima
        self.dano_fisico_base = stats_data.get('dano_fisico', 10)
        self.dano_magico_base = stats_data.get('dano_magico', 0)
        self.defensa_fisica_base = stats_data.get('defensa_fisica', 0)
        self.defensa_magica_base = stats_data.get('defensa_magica', 0)
        self.rango_movimiento_base = stats_data.get('rango_movimiento', 1)
        self.rango_ataque_base = stats_data.get('rango_ataque', 1)
        self.velocidad_movimiento = stats_data.get('velocidad_movimiento', 1.0)
        self.velocidad_ataque = stats_data.get('velocidad_ataque', 1.5)
        self.rango_vision = stats_data.get('rango_vision', 2)

        # Stats actuales (pueden ser modificados por efectos)
        self.dano_fisico_actual = self.dano_fisico_base
        self.dano_magico_actual = self.dano_magico_base
        self.defensa_fisica_actual = self.defensa_fisica_base
        self.defensa_magica_actual = self.defensa_magica_base
        self.rango_movimiento_actual = self.rango_movimiento_base
        self.rango_ataque_actual = self.rango_ataque_base

        # Sistema de mana
        self.mana_maxima = 100
        self.mana_actual = 0

        # Habilidades
        self.habilidades: List[Habilidad] = []
        self._cargar_habilidades(datos_carta.get('habilidades', []))

        # Estado de la carta
        self.viva = True
        self.puede_actuar = True
        self.efectos_activos = []

        # Posición (será asignada cuando se coloque en tablero)
        self.coordenada = None

        # Estadísticas de combate
        self.stats_combate = {
            'dano_infligido': 0,
            'dano_recibido': 0,
            'habilidades_usadas': 0,
            'enemigos_eliminados': 0
        }
        self.modo_control = "pasivo"  # 'activo', 'pasivo' u 'orden_manual'
        self.orden_manual_pendiente = False
        self.orden_actual = None

    @classmethod
    def crear_basica(cls, id, nombre="Carta", tier=1):
        return cls({
            "id": id,
            "nombre": nombre,
            "tier": tier,
            "stats": {"vida": 100, "dano_fisico": 10}
        })

    def _cargar_habilidades(self, habilidades_data: List[Dict[str, Any]]):
        """Carga las habilidades desde los datos JSON"""
        for hab_data in habilidades_data:
            habilidad = Habilidad(hab_data)
            self.habilidades.append(habilidad)

    # === MÉTODOS DE VIDA Y ESTADO ===

    def esta_viva(self) -> bool:
        """Retorna True si la carta puede seguir en combate"""
        return self.vida_actual > 0 and self.viva

    def recibir_dano(self, cantidad: int, tipo_dano: str = 'fisico') -> int:
        """Recibe daño y actualiza vida"""
        if not self.esta_viva():
            return 0

        # Calcular defensa aplicable
        if tipo_dano == 'fisico':
            defensa = self.defensa_fisica_actual
        elif tipo_dano == 'magico':
            defensa = self.defensa_magica_actual
        else:
            defensa = 0

        # Aplicar defensa
        dano_reducido = max(1, cantidad - defensa)  # Mínimo 1 de daño

        # CORRECCIÓN: Asegurar que el daño se aplique correctamente
        dano_aplicado = min(dano_reducido, self.vida_actual)
        self.vida_actual -= dano_aplicado

        # Verificar muerte
        if self.vida_actual <= 0:
            self.vida_actual = 0
            self.viva = False

        # Actualizar estadísticas
        self.stats_combate['dano_recibido'] += dano_aplicado

        return dano_aplicado

    def curar(self, cantidad: int) -> int:
        """Cura a la carta sin exceder vida máxima"""
        if not self.viva:
            return 0

        vida_anterior = self.vida_actual
        self.vida_actual = min(self.vida_maxima, self.vida_actual + cantidad)
        cantidad_curada = self.vida_actual - vida_anterior

        if cantidad_curada > 0:
            log_evento(f"💚 {self.nombre} se cura {cantidad_curada} puntos")

        return cantidad_curada

    # === MÉTODOS DE MANA ===

    def ganar_mana(self, cantidad: int):
        """Gana mana sin exceder el máximo"""
        self.mana_actual = min(self.mana_maxima, self.mana_actual + cantidad)

    def gastar_mana(self, cantidad: int) -> bool:
        """Gasta mana si tiene suficiente"""
        if self.mana_actual >= cantidad:
            self.mana_actual -= cantidad
            return True
        return False

    def puede_usar_habilidad(self, indice_habilidad: int) -> bool:
        """Verifica si puede usar una habilidad específica"""
        if not self.esta_viva() or not self.puede_actuar:
            return False

        if 0 <= indice_habilidad < len(self.habilidades):
            habilidad = self.habilidades[indice_habilidad]
            return (habilidad.puede_usar() and
                    self.mana_actual >= habilidad.costo_mana)

        return False

    def usar_habilidad(self, indice_habilidad: int) -> bool:
        """Intenta usar una habilidad"""
        if not self.puede_usar_habilidad(indice_habilidad):
            return False

        habilidad = self.habilidades[indice_habilidad]

        # Gastar mana y usar habilidad
        self.gastar_mana(habilidad.costo_mana)
        habilidad.usar()

        # Actualizar estadísticas
        self.stats_combate['habilidades_usadas'] += 1

        log_evento(f"✨ {self.nombre} usa {habilidad.nombre}")
        return True

    # === MÉTODOS DE STATS ===

    def obtener_dano_total(self) -> int:
        """Retorna el daño total (físico + mágico)"""
        return self.dano_fisico_actual + self.dano_magico_actual

    def obtener_defensa_total(self) -> int:
        """Retorna la defensa total promedio"""
        return (self.defensa_fisica_actual + self.defensa_magica_actual) // 2

    def aplicar_modificador_stat(self, stat: str, valor: int, permanente: bool = False):
        """Aplica un modificador a un stat específico"""
        if permanente:
            # Modificar stats base
            if stat == 'dano_fisico':
                self.dano_fisico_base += valor
                self.dano_fisico_actual += valor
            elif stat == 'dano_magico':
                self.dano_magico_base += valor
                self.dano_magico_actual += valor
            elif stat == 'defensa_fisica':
                self.defensa_fisica_base += valor
                self.defensa_fisica_actual += valor
            elif stat == 'defensa_magica':
                self.defensa_magica_base += valor
                self.defensa_magica_actual += valor
            elif stat == 'vida_maxima':
                self.vida_maxima += valor
                self.vida_actual += valor  # También aumenta vida actual
        else:
            # Modificar solo stats actuales (temporal)
            if stat == 'dano_fisico':
                self.dano_fisico_actual += valor
            elif stat == 'dano_magico':
                self.dano_magico_actual += valor
            # ... etc para otros stats

    def resetear_stats_temporales(self):
        """Resetea los stats actuales a los valores base"""
        self.dano_fisico_actual = self.dano_fisico_base
        self.dano_magico_actual = self.dano_magico_base
        self.defensa_fisica_actual = self.defensa_fisica_base
        self.defensa_magica_actual = self.defensa_magica_base
        self.rango_movimiento_actual = self.rango_movimiento_base
        self.rango_ataque_actual = self.rango_ataque_base

    # === MÉTODOS DE TURNO ===
    def generar_interacciones(self, tablero) -> list[Interaccion]:
        """
        En modo pasivo, decide generar ataques contra enemigos en rango.
        """
        if self.modo_control != "pasivo" or self.vida_actual <= 0:
            return []

        coord = tablero.obtener_coordenada_de(self)
        if coord is None:
            return []

        interacciones = []
        enemigos_en_rango = tablero.obtener_cartas_en_rango(coord, self.rango)

        for otra_coord, otra_carta in enemigos_en_rango:
            if otra_carta is self:
                continue
            if not self.es_aliado_de(otra_carta):
                interacciones.append(
                    Interaccion(
                        fuente_id=self.id,
                        objetivo_id=otra_carta.id,
                        tipo=TipoInteraccion.ATAQUE,
                        metadata={"dano_base": self.dano_fisico_actual}
                    )
                )

        return interacciones
    
    def iniciar_turno(self):
        """Acciones al inicio del turno de la carta"""
        if not self.esta_viva():
            return

        # Ganar mana por turno
        self.ganar_mana(10)  # TODO: Hacer configurable

        # Reducir cooldowns
        for habilidad in self.habilidades:
            habilidad.reducir_cooldown()

        # Permitir actuar
        self.puede_actuar = True

    def finalizar_turno(self):
        """Acciones al final del turno de la carta"""
        self.puede_actuar = False

    # === MÉTODOS DE INFORMACIÓN ===

    def tiene_orden_manual(self) -> bool:
        """Indica si la carta tiene una orden manual en curso"""
        return (
            self.orden_actual is not None
            and self.orden_actual.get("progreso") in {"pendiente", "ejecutando"}
        )

    def marcar_orden_manual(self, tipo: str, objetivo=None, datos_adicionales=None):
        """Registra una nueva orden manual para la carta"""
        self.orden_actual = {
            "tipo": tipo,
            "objetivo": objetivo,
            "progreso": "pendiente",
            "datos_adicionales": datos_adicionales or {},
        }
        self.modo_control = "orden_manual"
        self.orden_manual_pendiente = True

    def limpiar_orden_manual(self):
        self.orden_manual_pendiente = False
        self.orden_actual = None
        if self.modo_control == "orden_manual":
            self.modo_control = "pasivo"
    def obtener_habilidades_disponibles(self) -> List[Habilidad]:
        """Retorna lista de habilidades que pueden ser usadas"""
        return [hab for i, hab in enumerate(self.habilidades)
                if self.puede_usar_habilidad(i)]

    def obtener_info_basica(self) -> Dict[str, Any]:
        """Retorna información básica de la carta"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tier': self.tier,
            'rol': self.rol,
            'categoria': self.categoria,
            'vida': f"{self.vida_actual}/{self.vida_maxima}",
            'mana': f"{self.mana_actual}/{self.mana_maxima}",
            'dano_total': self.obtener_dano_total(),
            'viva': self.esta_viva()
        }

    def obtener_info_completa(self) -> Dict[str, Any]:
        """Retorna información completa de la carta"""
        info = self.obtener_info_basica()
        info.update({
            'descripcion': self.descripcion,
            'costo': self.costo,
            'stats': {
                'vida_actual': self.vida_actual,
                'vida_maxima': self.vida_maxima,
                'dano_fisico': self.dano_fisico_actual,
                'dano_magico': self.dano_magico_actual,
                'defensa_fisica': self.defensa_fisica_actual,
                'defensa_magica': self.defensa_magica_actual,
                'rango_movimiento': self.rango_movimiento_actual,
                'rango_ataque': self.rango_ataque_actual
            },
            'habilidades': [str(hab) for hab in self.habilidades],
            'stats_combate': self.stats_combate.copy(),
            'coordenada': str(self.coordenada) if self.coordenada else None
        })
        return info

    def es_aliado_de(self, otra_carta) -> bool:
        return self.duenio is not None and self.duenio == otra_carta.duenio
    
    def __str__(self):
        """Representación en string de la carta"""
        estado = "VIVA" if self.esta_viva() else "MUERTA"
        return f"{self.nombre} ({self.vida_actual}/{self.vida_maxima} vida) [{estado}]"

    def __repr__(self):
        """Representación para debugging"""
        return f"CartaBase(id={self.id}, nombre='{self.nombre}', tier={self.tier})"

