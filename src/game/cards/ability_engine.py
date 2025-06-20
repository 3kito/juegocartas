class AbilityEngine:
    """Motor simple para ejecutar habilidades definidas en JSON."""

    def ejecutar_habilidad(self, caster, habilidad, objetivo=None):
        """Ejecuta los efectos de una habilidad."""
        for efecto in habilidad.efectos:
            tipo = efecto.get("tipo")
            if tipo == "dano" and objetivo is not None:
                cantidad = efecto.get("cantidad", 0)
                objetivo.recibir_dano(cantidad, efecto.get("dano_tipo", "fisico"))
            elif tipo == "curacion" and objetivo is not None:
                cantidad = efecto.get("cantidad", 0)
                objetivo.curar(cantidad)
            elif tipo == "buff":
                stat = efecto.get("stat")
                valor = efecto.get("valor", 0)
                (objetivo or caster).aplicar_modificador_stat(stat, valor, False)
            # Se pueden agregar más tipos de efecto en el futuro


ability_engine = AbilityEngine()
