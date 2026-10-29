from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class CyclePreprocessor:
    """
    Prepara y transforma la serie temporal para el análisis de ciclos.

    Responsabilidades:
    - Validar y ordenar observaciones.
    - Determinar si la serie debe analizarse en logaritmos o niveles.
    - Calcular crecimiento logarítmico o primera diferencia.
    - Eliminar tendencia lineal.
    - Aplicar el filtro Hodrick-Prescott.
    """

    # Ravn-Uhlig (2002); valor anual del propio Hodrick-Prescott (1997)
    HP_LAMBDA_BY_FREQUENCY = {
        1: 100.0,
        4: 1600.0,
        12: 129600.0,
    }

    MIN_OBSERVATIONS = 8

    @classmethod
    def default_hp_lambda(
        cls,
        observations_per_year: int,
    ) -> float:
        """
        Devuelve el lambda estándar de Hodrick-Prescott para la
        frecuencia dada (Ravn-Uhlig, 2002).

        Si la frecuencia no es 1, 4 o 12, no hay convención
        establecida en la literatura — se exige lambda explícito.
        """
        if observations_per_year in cls.HP_LAMBDA_BY_FREQUENCY:
            return cls.HP_LAMBDA_BY_FREQUENCY[observations_per_year]

        raise ValueError(
            "No existe un lambda HP estándar para "
            f"observations_per_year={observations_per_year}. "
            "Debe especificarse `lamb` explícitamente."
        )

    @staticmethod
    def prepare_series(
        observations: list[Any],
    ) -> tuple[pd.DatetimeIndex, np.ndarray, int, bool]:
        """
        Ordena y valida las observaciones.

        Determina automáticamente la transformación:

        - use_log=True:
          todas las observaciones son estrictamente positivas.

        - use_log=False:
          la serie contiene algún cero o valor negativo y debe
          analizarse en niveles.

        Los valores no finitos se eliminan, pero los ceros y
        negativos se conservan.
        """
        if not observations:
            raise ValueError(
                "No hay observaciones para analizar."
            )

        ordered = sorted(
            observations,
            key=lambda observation: observation.date,
        )

        dates = pd.to_datetime(
            [observation.date for observation in ordered]
        )

        values = np.asarray(
            [observation.value for observation in ordered],
            dtype=float,
        )

        # Eliminar únicamente valores no finitos.
        # Los ceros y negativos son válidos para análisis en niveles.
        valid = np.isfinite(values)

        dates = dates[valid]
        values = values[valid]

        if len(values) < 2:
            raise ValueError(
                "Se necesitan al menos dos observaciones válidas."
            )

        observations_per_year = (
            CyclePreprocessor.infer_observations_per_year(dates)
        )

        # Las series estrictamente positivas pueden analizarse
        # mediante logaritmos. Si cruzan cero, se analizan en niveles.
        use_log = bool(np.all(values > 0))

        return (
            dates,
            values,
            observations_per_year,
            use_log,
        )

    @staticmethod
    def infer_observations_per_year(
        dates: pd.DatetimeIndex,
    ) -> int:
        """
        Infiere la frecuencia de la serie a partir de sus fechas.

        Devuelve:
            1  -> anual
            4  -> trimestral
            12 -> mensual
        """
        if len(dates) < 2:
            raise ValueError(
                "Se necesitan al menos dos fechas para inferir la frecuencia."
            )

        periods = dates.to_period("M")

        month_differences = np.diff(
            periods.astype(int)
        )

        if len(month_differences) == 0:
            raise ValueError(
                "No se pudo determinar la frecuencia de la serie."
            )

        median_months = float(
            np.median(month_differences)
        )

        if median_months <= 1.5:
            return 12

        if median_months <= 4.5:
            return 4

        if median_months <= 12.5:
            return 1

        raise ValueError(
            "No se pudo determinar una frecuencia "
            "anual, trimestral o mensual."
        )

    @staticmethod
    def growth(
        values: np.ndarray,
        use_log: bool,
    ) -> np.ndarray:
        """
        Calcula la variación de la serie.

        Si use_log=True:
            crecimiento logarítmico.

        Si use_log=False:
            primera diferencia en niveles.

        En una serie como un tipo de interés, la primera diferencia
        representa el cambio de nivel entre observaciones.
        """
        values = np.asarray(
            values,
            dtype=float,
        )

        if not np.isfinite(values).all():
            raise ValueError(
                "La serie contiene valores no finitos."
            )

        if use_log:
            if not np.all(values > 0):
                raise ValueError(
                    "El crecimiento logarítmico requiere valores positivos."
                )

            return np.diff(
                np.log(values)
            )

        return np.diff(values)

    @staticmethod
    def log_growth(
        values: np.ndarray,
    ) -> np.ndarray:
        """
        Compatibilidad con el comportamiento anterior.

        Calcula siempre crecimiento logarítmico.
        """
        values = np.asarray(
            values,
            dtype=float,
        )

        if not np.isfinite(values).all():
            raise ValueError(
                "La serie contiene valores no finitos."
            )

        if not np.all(values > 0):
            raise ValueError(
                "El crecimiento logarítmico requiere valores positivos."
            )

        return np.diff(
            np.log(values)
        )

    @staticmethod
    def check_regularity(
        dates: pd.DatetimeIndex,
        observations_per_year: int,
    ) -> tuple[bool, int]:
        """
        Verifica si la secuencia temporal es estrictamente contigua
        y equiespaciada según la frecuencia inferida.

        Parameters
        ----------
        dates:
            Índice de fechas ordenadas cronológicamente.
        observations_per_year:
            Frecuencia anual: 1=anual, 4=trimestral, 12=mensual.

        Returns
        -------
        tuple[bool, int]
            (is_regular, missing_periods_count)
        """
        if len(dates) < 2:
            return True, 0

        if observations_per_year == 12:
            freq_rule = "M"
        elif observations_per_year == 4:
            freq_rule = "Q"
        elif observations_per_year == 1:
            freq_rule = "Y"
        else:
            return True, 0

        periods = dates.to_period(freq_rule)
        diffs = np.diff(periods.astype(int))

        if len(diffs) == 0:
            return True, 0

        # En una serie continua y regular, cada diff debe ser exactamente 1.
        # Cualquier valor > 1 indica períodos faltantes (huecos).
        gaps = diffs[diffs > 1]
        missing_count = int(np.sum(gaps - 1)) if len(gaps) > 0 else 0

        return missing_count == 0, missing_count

    @staticmethod
    def linear_detrend(
        values: np.ndarray,
        use_log: bool,
        *,
        dates: pd.DatetimeIndex | None = None,
    ) -> np.ndarray:
        """
        Elimina una tendencia lineal de la serie transformada.

        Si use_log=True:
            la tendencia se elimina sobre log(values).

        Si use_log=False:
            la tendencia se elimina directamente sobre los niveles.

        Si se proporcionan `dates`, la regresión lineal se ajusta
        sobre el tiempo físico transcurrido en años, evitando distorsiones
        en presencia de lagunas o fechas no contiguas.
        """
        values = np.asarray(
            values,
            dtype=float,
        )

        if not np.isfinite(values).all():
            raise ValueError(
                "La serie contiene valores no finitos."
            )

        if use_log:
            if not np.all(values > 0):
                raise ValueError(
                    "El análisis logarítmico requiere valores positivos."
                )

            transformed_values = np.log(values)

        else:
            transformed_values = values

        if dates is not None and len(dates) == len(transformed_values):
            t_seconds = (dates - dates[0]).total_seconds().to_numpy(dtype=float)
            x = t_seconds / (365.25 * 86400.0)
        else:
            x = np.arange(
                len(transformed_values),
                dtype=float,
            )

        coefficients = np.polyfit(
            x,
            transformed_values,
            1,
        )

        trend = np.polyval(
            coefficients,
            x,
        )

        return (
            transformed_values
            - trend
        )

    @staticmethod
    def hp_filter(
        values: np.ndarray,
        lamb: float | None = None,
        observations_per_year: int | None = None,
        use_log: bool = True,
    ) -> tuple[np.ndarray, np.ndarray, float]:
        """
        Aplica el filtro Hodrick-Prescott.

        Si use_log=True:
            el filtro se aplica sobre log(values).

        Si use_log=False:
            el filtro se aplica directamente sobre los niveles.

        Si lamb es None, se utiliza el valor estándar según
        observations_per_year.
        """
        if lamb is None:
            if observations_per_year is None:
                raise ValueError(
                    "Debe indicarse `lamb` o `observations_per_year` "
                    "para determinar el lambda por defecto."
                )

            resolved_lambda = (
                CyclePreprocessor.default_hp_lambda(
                    observations_per_year
                )
            )

        else:
            resolved_lambda = lamb

        values = np.asarray(
            values,
            dtype=float,
        )

        if not np.isfinite(values).all():
            raise ValueError(
                "La serie contiene valores no finitos."
            )

        if use_log:
            if not np.all(values > 0):
                raise ValueError(
                    "El filtro HP logarítmico requiere valores positivos."
                )

            transformed_values = np.log(values)

        else:
            transformed_values = values

        n = len(transformed_values)

        if n < 4:
            raise ValueError(
                "No hay suficientes observaciones "
                "para aplicar el filtro HP."
            )

        # Matriz de segunda diferencias.
        D = np.zeros(
            (n - 2, n)
        )

        for i in range(n - 2):
            D[i, i] = 1.0
            D[i, i + 1] = -2.0
            D[i, i + 2] = 1.0

        identity = np.eye(n)

        system = (
            identity
            + resolved_lambda * D.T @ D
        )

        trend = np.linalg.solve(
            system,
            transformed_values,
        )

        cycle = (
            transformed_values
            - trend
        )

        return (
            trend,
            cycle,
            resolved_lambda,
        )