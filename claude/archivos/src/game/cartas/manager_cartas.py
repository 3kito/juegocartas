"""
Manager para cargar y gestionar la base de datos de cartas con sistema de copias múltiples
"""

import random
from typing import List, Dict, Optional, Any

from src.data.config.game_config import GameConfig

from src.game.cartas.carta_base import CartaBase
from src.utils.helpers import cargar_json, log_evento


class ManagerCartas:
    """Gestiona la carga, creación y distribución de cartas con sistema de copias múltiples"""

    def __init__(self, config: GameConfig | None = None):
        # Base de datos de cartas
        self.datos_cartas: Dict[int, Dict[str, Any]] = {}
        self.cartas_por_tier: Dict[int, List[int]] = {1: [], 2: [], 3: []}
        self.cartas_por_categoria: Dict[str, List[int]] = {}
        self.cartas_por_rol: Dict[str, List[int]] = {}

        # NUEVO: Sistema de copias múltiples (configurable)

        # NUEVO: Pool mejorado con instancias únicas
        self.pool_instancias: Dict[int, List[CartaBase]] = {}  # carta_id: [instancia1, instancia2, ...]
        self.pool_disponibles: Dict[int, int] = {}  # carta_id: cantidad_disponible

        # Pool global de cartas disponibles (LEGACY - mantenido por compatibilidad)
        self.pool_global: Dict[int, int] = {}  # {carta_id: cantidad_disponible}

        # Configuración
        self.config = config or GameConfig()
        self.copias_por_tier = {
            1: self.config.copias_por_tier.get(1, 5),
            2: self.config.copias_por_tier.get(2, 3),
            3: self.config.copias_por_tier.get(3, 2),
        }
        self.max_cartas_por_tier = self.config.max_cartas_por_tier
        self.cartas_activas = set(self.config.cartas_activas)

        self.archivo_cartas = "src/data/cartas/personajes_historicos.json"

        # Estado de carga
        self.cartas_cargadas = False

    def cargar_cartas(self) -> bool:
        """Carga todas las cartas desde el archivo JSON y crea instancias múltiples"""
        try:
            datos = cargar_json(self.archivo_cartas)
            if not datos:
                log_evento("❌ No se pudieron cargar los datos de cartas", "ERROR")
                return False

            # Filtrar cartas activas si se especifica
            if self.cartas_activas:
                datos = [d for d in datos if d.get('id') in self.cartas_activas]

            # Limitar cantidad de tipos por tier
            if any(v > 0 for v in self.max_cartas_por_tier.values()):
                cuenta_tier = {1: 0, 2: 0, 3: 0}
                filtradas = []
                for d in datos:
                    tier = d.get('tier', 1)
                    limite = self.max_cartas_por_tier.get(tier, 0)
                    if limite == 0 or cuenta_tier[tier] < limite:
                        filtradas.append(d)
                        cuenta_tier[tier] += 1
                datos = filtradas

            # Limpiar datos anteriores
            self.datos_cartas.clear()
            self.cartas_por_tier = {1: [], 2: [], 3: []}
            self.cartas_por_categoria.clear()
            self.cartas_por_rol.clear()

            # Procesar cada carta
            for carta_data in datos:
                carta_id = carta_data.get('id')
                if carta_id is None:
                    log_evento(f"⚠️ Carta sin ID encontrada: {carta_data.get('nombre', 'Sin nombre')}", "WARNING")
                    continue

                # Guardar datos de la carta
                self.datos_cartas[carta_id] = carta_data

                # Organizar por tier
                tier = carta_data.get('tier', 1)
                if tier in self.cartas_por_tier:
                    self.cartas_por_tier[tier].append(carta_id)

                # Organizar por categoría
                categoria = carta_data.get('categoria', 'general')
                if categoria not in self.cartas_por_categoria:
                    self.cartas_por_categoria[categoria] = []
                self.cartas_por_categoria[categoria].append(carta_id)

                # Organizar por rol
                rol = carta_data.get('rol', 'basico')
                if rol not in self.cartas_por_rol:
                    self.cartas_por_rol[rol] = []
                self.cartas_por_rol[rol].append(carta_id)

            # Inicializar pools (nuevo y legacy)
            self._inicializar_pool_instancias()
            self._inicializar_pool_global()

            self.cartas_cargadas = True
            log_evento(f"✅ Cargadas {len(self.datos_cartas)} cartas exitosamente")
            log_evento(f"   Tier 1: {len(self.cartas_por_tier[1])} tipos de carta")
            log_evento(f"   Tier 2: {len(self.cartas_por_tier[2])} tipos de carta")
            log_evento(f"   Tier 3: {len(self.cartas_por_tier[3])} tipos de carta")
            log_evento(f"   Categorías: {len(self.cartas_por_categoria)}")
            log_evento(f"   Roles: {len(self.cartas_por_rol)}")

            # Mostrar estadísticas de instancias creadas
            stats_pool = self.obtener_estadisticas_pool()
            log_evento(f"   📦 Total instancias creadas: {stats_pool['total_instancias_creadas']}")
            log_evento(
                f"   📊 Por tier: T1={stats_pool['cartas_por_tier_total'][1]}, T2={stats_pool['cartas_por_tier_total'][2]}, T3={stats_pool['cartas_por_tier_total'][3]}")

            return True

        except Exception as e:
            log_evento(f"❌ Error cargando cartas: {e}", "ERROR")
            return False

    def _inicializar_pool_instancias(self):
        """Inicializa el pool de instancias únicas para cada carta"""
        self.pool_instancias.clear()
        self.pool_disponibles.clear()

        log_evento("🏭 Creando instancias múltiples de cartas...")

        for carta_id, carta_data in self.datos_cartas.items():
            tier = carta_data.get('tier', 1)
            cantidad_copias = self.copias_por_tier.get(tier, 1)

            # Crear múltiples instancias de la misma carta
            instancias = []
            for copia in range(cantidad_copias):
                # Crear instancia única con ID compuesto
                carta_data_copia = carta_data.copy()
                id_unico = f"{carta_id}_{copia:03d}"  # Formato: 1_001, 1_002, etc.
                carta_data_copia['id'] = id_unico
                carta_data_copia['carta_base_id'] = carta_id  # Referencia al ID original
                carta_data_copia['numero_copia'] = copia

                try:
                    instancia = CartaBase(carta_data_copia)
                    instancia._en_uso = False  # Marcar como disponible
                    instancias.append(instancia)
                except Exception as e:
                    log_evento(f"❌ Error creando instancia {id_unico}: {e}", "ERROR")

            self.pool_instancias[carta_id] = instancias
            self.pool_disponibles[carta_id] = len(instancias)

            log_evento(f"   📦 {carta_data['nombre']}: {len(instancias)} copias (Tier {tier})")

    def _inicializar_pool_global(self):
        """Inicializa el pool global (legacy) para compatibilidad"""
        self.pool_global.clear()

        for carta_id, carta_data in self.datos_cartas.items():
            tier = carta_data.get('tier', 1)
            cantidad = self.copias_por_tier.get(tier, 1)
            self.pool_global[carta_id] = cantidad

    def obtener_carta_por_id(self, carta_id: int) -> Optional[CartaBase]:
        """Retorna una instancia nueva de carta por su ID (legacy method)"""
        if not self.cartas_cargadas:
            log_evento("⚠️ Las cartas no han sido cargadas aún", "WARNING")
            return None

        if carta_id not in self.datos_cartas:
            log_evento(f"❌ Carta con ID {carta_id} no encontrada", "ERROR")
            return None

        try:
            carta_data = self.datos_cartas[carta_id]
            carta = CartaBase(carta_data)
            return carta
        except Exception as e:
            log_evento(f"❌ Error creando carta {carta_id}: {e}", "ERROR")
            return None

    def obtener_cartas_aleatorias_por_nivel(self, nivel_jugador: int, cantidad: int = 5) -> List[CartaBase]:
        """Obtiene cartas aleatorias usando el sistema de instancias únicas"""
        if not self.cartas_cargadas:
            log_evento("⚠️ Cartas no cargadas, retornando lista vacía")
            return []

        probabilidades = self._obtener_probabilidades_tier(nivel_jugador)
        cartas_seleccionadas = []

        log_evento(f"🎲 Generando {cantidad} cartas para nivel {nivel_jugador}")
        log_evento(
            f"   Probabilidades: T1={probabilidades[1]:.0%}, T2={probabilidades[2]:.0%}, T3={probabilidades[3]:.0%}")

        for i in range(cantidad):
            tier_elegido = self._seleccionar_tier_aleatorio(probabilidades)

            # Obtener cartas disponibles de ese tier
            cartas_disponibles = [
                carta_id for carta_id in self.cartas_por_tier[tier_elegido]
                if self.pool_disponibles.get(carta_id, 0) > 0
            ]

            if cartas_disponibles:
                carta_id = random.choice(cartas_disponibles)
                instancia = self._tomar_instancia_del_pool(carta_id)

                if instancia:
                    cartas_seleccionadas.append(instancia)
                    log_evento(f"   ✅ Carta {i + 1}: {instancia.nombre} (Tier {instancia.tier}, ID: {instancia.id})")
                else:
                    log_evento(f"   ❌ Error tomando instancia de carta {carta_id}")
            else:
                log_evento(f"   ⚠️ No hay cartas disponibles de tier {tier_elegido}")
                # Intentar con otro tier si hay cartas disponibles
                for tier_alternativo in [1, 2, 3]:
                    if tier_alternativo != tier_elegido:
                        cartas_alt = [
                            cid for cid in self.cartas_por_tier[tier_alternativo]
                            if self.pool_disponibles.get(cid, 0) > 0
                        ]
                        if cartas_alt:
                            carta_id = random.choice(cartas_alt)
                            instancia = self._tomar_instancia_del_pool(carta_id)
                            if instancia:
                                cartas_seleccionadas.append(instancia)
                                log_evento(
                                    f"   🔄 Carta {i + 1} (tier alternativo): {instancia.nombre} (Tier {instancia.tier})")
                                break

        log_evento(f"   📊 Total generadas: {len(cartas_seleccionadas)}/{cantidad}")

        # Mostrar cartas disponibles restantes si generamos pocas
        if len(cartas_seleccionadas) < cantidad:
            disponibles_total = sum(self.pool_disponibles.values())
            log_evento(f"   ⚠️ Solo se generaron {len(cartas_seleccionadas)}/{cantidad} cartas")
            log_evento(f"   📦 Cartas restantes en pool: {disponibles_total}")

        return cartas_seleccionadas

    def _tomar_instancia_del_pool(self, carta_id: int) -> Optional[CartaBase]:
        """Toma una instancia específica del pool y la marca como usada"""
        if carta_id not in self.pool_instancias or self.pool_disponibles.get(carta_id, 0) <= 0:
            return None

        # Buscar primera instancia disponible
        for instancia in self.pool_instancias[carta_id]:
            if not getattr(instancia, '_en_uso', False):
                instancia._en_uso = True
                self.pool_disponibles[carta_id] -= 1

                # También actualizar pool legacy
                if carta_id in self.pool_global:
                    self.pool_global[carta_id] = max(0, self.pool_global[carta_id] - 1)

                return instancia

        return None

    def devolver_carta_al_pool(self, carta: CartaBase):
        """Devuelve una carta al pool marcándola como disponible"""
        try:
            # Obtener el ID base de la carta
            if hasattr(carta, 'carta_base_id'):
                carta_base_id = carta.carta_base_id
            else:
                # Fallback para cartas sin el nuevo sistema
                carta_id_str = str(carta.id)
                if '_' in carta_id_str:
                    carta_base_id = int(carta_id_str.split('_')[0])
                else:
                    carta_base_id = carta.id

            if carta_base_id in self.pool_instancias:
                # Buscar la instancia específica
                for instancia in self.pool_instancias[carta_base_id]:
                    if instancia.id == carta.id:
                        instancia._en_uso = False
                        self.pool_disponibles[carta_base_id] += 1

                        # También actualizar pool legacy
                        if carta_base_id in self.pool_global:
                            self.pool_global[carta_base_id] += 1

                        log_evento(f"🔄 {carta.nombre} (ID: {carta.id}) devuelta al pool")
                        return

                log_evento(f"⚠️ No se encontró la instancia específica de {carta.nombre} para devolver")
            else:
                log_evento(f"⚠️ Carta base ID {carta_base_id} no encontrada en pool de instancias")

        except Exception as e:
            log_evento(f"❌ Error devolviendo carta al pool: {e}")

    def _obtener_probabilidades_tier(self, nivel_jugador: int) -> Dict[int, float]:
        """Calcula probabilidades de tier según nivel del jugador"""
        # Configuración base (ajustable)
        if nivel_jugador <= 2:
            return {1: 0.75, 2: 0.25, 3: 0.00}
        elif nivel_jugador <= 4:
            return {1: 0.55, 2: 0.35, 3: 0.10}
        elif nivel_jugador <= 6:
            return {1: 0.35, 2: 0.45, 3: 0.20}
        elif nivel_jugador <= 8:
            return {1: 0.20, 2: 0.50, 3: 0.30}
        else:  # nivel 9-10
            return {1: 0.10, 2: 0.40, 3: 0.50}

    def _seleccionar_tier_aleatorio(self, probabilidades: Dict[int, float]) -> int:
        """Selecciona un tier aleatoriamente según probabilidades"""
        rand = random.random()
        acumulado = 0.0

        for tier, prob in probabilidades.items():
            acumulado += prob
            if rand <= acumulado:
                return tier

        return 1  # Fallback tier 1

    def obtener_cartas_por_categoria(self, categoria: str) -> List[int]:
        """Retorna lista de IDs de cartas de una categoría específica"""
        return self.cartas_por_categoria.get(categoria, []).copy()

    def obtener_cartas_por_rol(self, rol: str) -> List[int]:
        """Retorna lista de IDs de cartas de un rol específico"""
        return self.cartas_por_rol.get(rol, []).copy()

    def calcular_sinergias(self, cartas: List[CartaBase]) -> Dict[str, int]:
        """Calcula las sinergias activas entre un grupo de cartas"""
        if not cartas:
            return {}

        # Contar por categoría
        categorias = {}
        roles = {}

        for carta in cartas:
            if carta.esta_viva():
                # Contar categorías
                if carta.categoria not in categorias:
                    categorias[carta.categoria] = 0
                categorias[carta.categoria] += 1

                # Contar roles
                if carta.rol not in roles:
                    roles[carta.rol] = 0
                roles[carta.rol] += 1

        # Calcular bonificaciones de sinergia
        sinergias_activas = {}

        # Sinergias por categoría (necesita al menos 2 de la misma)
        for categoria, cantidad in categorias.items():
            if cantidad >= 2:
                sinergias_activas[f"categoria_{categoria}"] = cantidad

        # Sinergias por rol (necesita al menos 2 del mismo)
        for rol, cantidad in roles.items():
            if cantidad >= 2:
                sinergias_activas[f"rol_{rol}"] = cantidad

        return sinergias_activas

    def aplicar_sinergias(self, cartas: List[CartaBase], sinergias: Dict[str, int]):
        """Aplica bonificaciones de sinergia a las cartas"""
        for carta in cartas:
            if not carta.esta_viva():
                continue

            # Bonificaciones por categoría
            clave_categoria = f"categoria_{carta.categoria}"
            if clave_categoria in sinergias:
                nivel_sinergia = sinergias[clave_categoria]
                # Bonificación: +5 vida y +2 daño por cada carta adicional de la categoría
                bonus_vida = (nivel_sinergia - 1) * 5
                bonus_dano = (nivel_sinergia - 1) * 2

                carta.vida_maxima += bonus_vida
                carta.vida_actual += bonus_vida
                carta.aplicar_modificador_stat('dano_fisico', bonus_dano, False)
                carta.aplicar_modificador_stat('dano_magico', bonus_dano, False)

            # Bonificaciones por rol
            clave_rol = f"rol_{carta.rol}"
            if clave_rol in sinergias:
                nivel_sinergia = sinergias[clave_rol]
                # Bonificación específica por rol
                if carta.rol == 'lider':
                    # Líderes dan bonificación a todos los aliados
                    bonus_defensa = nivel_sinergia * 3
                    carta.aplicar_modificador_stat('defensa_fisica', bonus_defensa, False)
                elif carta.rol == 'especialista':
                    # Especialistas ganan daño mágico extra
                    bonus_magico = nivel_sinergia * 8
                    carta.aplicar_modificador_stat('dano_magico', bonus_magico, False)
                # ... más bonificaciones por rol según necesidad

    def obtener_estadisticas_pool(self) -> Dict[str, Any]:
        """Retorna estadísticas completas del pool de instancias"""
        total_instancias = sum(len(instancias) for instancias in self.pool_instancias.values())
        total_disponibles = sum(self.pool_disponibles.values())
        total_en_uso = total_instancias - total_disponibles

        cartas_por_tier_disponibles = {1: 0, 2: 0, 3: 0}
        cartas_por_tier_total = {1: 0, 2: 0, 3: 0}
        cartas_por_tier_en_uso = {1: 0, 2: 0, 3: 0}

        for carta_id, instancias in self.pool_instancias.items():
            if carta_id in self.datos_cartas:
                tier = self.datos_cartas[carta_id].get('tier', 1)
                disponibles = self.pool_disponibles.get(carta_id, 0)
                total_carta = len(instancias)
                en_uso = total_carta - disponibles

                cartas_por_tier_disponibles[tier] += disponibles
                cartas_por_tier_total[tier] += total_carta
                cartas_por_tier_en_uso[tier] += en_uso

        return {
            'total_instancias_creadas': total_instancias,
            'total_disponibles': total_disponibles,
            'total_en_uso': total_en_uso,
            'cartas_por_tier_disponibles': cartas_por_tier_disponibles,
            'cartas_por_tier_total': cartas_por_tier_total,
            'cartas_por_tier_en_uso': cartas_por_tier_en_uso,
            'cartas_agotadas': [carta_id for carta_id, cant in self.pool_disponibles.items() if cant == 0],
            'configuracion_copias': self.copias_por_tier.copy(),
            'total_tipos_carta': len(self.datos_cartas)
        }

    def configurar_copias_por_tier(self, tier: int, cantidad: int):
        """Permite modificar la cantidad de copias por tier"""
        if tier in [1, 2, 3] and cantidad > 0:
            antigua_cantidad = self.copias_por_tier.get(tier, 0)
            self.copias_por_tier[tier] = cantidad
            log_evento(f"🔧 Tier {tier}: {antigua_cantidad} → {cantidad} copias por carta")
            log_evento("   ⚠️ Requiere recargar cartas para aplicar cambios")
        else:
            log_evento(f"❌ Configuración inválida: tier {tier}, cantidad {cantidad}")

    def resetear_pool(self):
        """Resetea todos los pools a su estado inicial"""
        log_evento("🔄 Reseteando pools de cartas...")

        # Marcar todas las instancias como disponibles
        for carta_id, instancias in self.pool_instancias.items():
            for instancia in instancias:
                instancia._en_uso = False
            self.pool_disponibles[carta_id] = len(instancias)

        # Resetear pool legacy
        self._inicializar_pool_global()

        stats = self.obtener_estadisticas_pool()
        log_evento(f"✅ Pool reseteado: {stats['total_disponibles']} cartas disponibles")

    def obtener_info_carta(self, carta_id: int) -> Optional[Dict[str, Any]]:
        """Retorna información completa de una carta sin crear instancia"""
        return self.datos_cartas.get(carta_id, None)

    def listar_todas_las_cartas(self) -> List[Dict[str, Any]]:
        """Retorna lista con información básica de todas las cartas"""
        cartas_info = []
        for carta_id, carta_data in self.datos_cartas.items():
            disponibles = self.pool_disponibles.get(carta_id, 0)
            total_instancias = len(self.pool_instancias.get(carta_id, []))
            en_uso = total_instancias - disponibles

            info_basica = {
                'id': carta_id,
                'nombre': carta_data.get('nombre', ''),
                'tier': carta_data.get('tier', 1),
                'rol': carta_data.get('rol', ''),
                'categoria': carta_data.get('categoria', ''),
                'costo': carta_data.get('costo', 1),
                'instancias_totales': total_instancias,
                'disponibles': disponibles,
                'en_uso': en_uso,
                'pool_legacy': self.pool_global.get(carta_id, 0)
            }
            cartas_info.append(info_basica)

        return sorted(cartas_info, key=lambda x: (x['tier'], x['nombre']))

    def obtener_cartas_en_uso(self) -> List[CartaBase]:
        """Retorna lista de todas las cartas actualmente en uso"""
        cartas_en_uso = []
        for instancias in self.pool_instancias.values():
            for instancia in instancias:
                if getattr(instancia, '_en_uso', False):
                    cartas_en_uso.append(instancia)
        return cartas_en_uso

    def verificar_integridad_pool(self) -> bool:
        """Verifica que el estado del pool sea consistente"""
        errores = []

        for carta_id, instancias in self.pool_instancias.items():
            # Contar instancias marcadas como en uso
            en_uso_real = sum(1 for inst in instancias if getattr(inst, '_en_uso', False))
            disponibles_real = len(instancias) - en_uso_real
            disponibles_registradas = self.pool_disponibles.get(carta_id, 0)

            if disponibles_real != disponibles_registradas:
                errores.append(
                    f"Carta {carta_id}: disponibles_real={disponibles_real}, registradas={disponibles_registradas}")

        if errores:
            log_evento("❌ Errores de integridad en pool:")
            for error in errores:
                log_evento(f"   {error}")
            return False
        else:
            log_evento("✅ Integridad del pool verificada correctamente")
            return True

    def __str__(self):
        return f"ManagerCartas({len(self.datos_cartas)} tipos, {sum(len(inst) for inst in self.pool_instancias.values())} instancias)"

    def __repr__(self):
        stats = self.obtener_estadisticas_pool()
        return f"ManagerCartas(tipos={len(self.datos_cartas)}, instancias={stats['total_instancias_creadas']}, disponibles={stats['total_disponibles']})"


# Instancia global del manager (singleton)
manager_cartas = ManagerCartas()
