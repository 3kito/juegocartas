class AbilityEngine:
    """Motor simple para ejecutar habilidades definidas en JSON y gestionar triggers."""

    def ejecutar_habilidad(self, caster, habilidad, objetivo=None):
        """Ejecuta los efectos de una habilidad."""
        for efecto in habilidad.efectos:
            tipo = efecto.get("tipo")
            if tipo == "dano" and objetivo is not None:
                cantidad = efecto.get("cantidad", 0)
                objetivo.recibir_dano(cantidad, efecto.get("dano_tipo", "fisico"))
            elif tipo == "curacion":
                cantidad = efecto.get("cantidad", 0)
                (objetivo or caster).curar(cantidad)
            elif tipo == "mana":
                cantidad = efecto.get("cantidad", 0)
                (objetivo or caster).ganar_mana(cantidad)
            elif tipo == "buff":
                stat = efecto.get("stat")
                valor = efecto.get("valor", 0)
                permanente = efecto.get("permanente", False)
                (objetivo or caster).aplicar_modificador_stat(stat, valor, permanente)
            # Se pueden agregar más tipos de efecto en el futuro

    def procesar_trigger(self, caster, trigger: str, **kwargs):
        """Ejecuta habilidades pasivas del caster que coincidan con el trigger."""
        objetivo = kwargs.get("objetivo")
        for habilidad in getattr(caster, "habilidades", []):
            if habilidad.tipo != "pasiva":
                continue
            if habilidad.trigger == trigger:
                self.ejecutar_habilidad(caster, habilidad, objetivo)


ability_engine = AbilityEngine()
