from datetime import date

from app.database.database import get_connection
from app.models.observation import Observation

from app.services.catalog.region_service import RegionService
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.source_service import SourceService


class ObservationRepository:

    @staticmethod
    def create_table():
        """
        Crea la tabla observations y sus índices si no existen.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                region_code TEXT NOT NULL,
                indicator_code TEXT NOT NULL,
                source_code TEXT NOT NULL,

                date TEXT NOT NULL,
                value REAL NOT NULL,

                UNIQUE (
                    region_code,
                    indicator_code,
                    source_code,
                    date
                )
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_observations_indicator_region
            ON observations (indicator_code, region_code);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_observations_region_indicator
            ON observations (region_code, indicator_code);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_observations_indicator
            ON observations (indicator_code);
        """)

        connection.commit()
        connection.close()


    @staticmethod
    def save_observations(observations: list[Observation]):
        """
        Guarda una lista de observaciones.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.executemany(
            """
            INSERT OR IGNORE INTO observations (
                region_code,
                indicator_code,
                source_code,
                date,
                value
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    observation.region.code.upper(),
                    observation.indicator.code.upper(),
                    observation.source.code.upper(),
                    observation.date.isoformat(),
                    observation.value,
                )
                for observation in observations
            ]
        )

        connection.commit()
        connection.close()


    @staticmethod
    def exists(
        indicator_code: str,
        region_code: str | None = None,
    ) -> bool:
        """
        Comprueba si existen observaciones para un indicador
        (y opcionalmente para una región concreta).
        """

        connection = get_connection()
        cursor = connection.cursor()

        if region_code:
            cursor.execute(
                """
                SELECT 1
                FROM observations
                WHERE indicator_code = ?
                  AND region_code = ?
                LIMIT 1
                """,
                (indicator_code.upper(), region_code.upper()),
            )
        else:
            cursor.execute(
                """
                SELECT 1
                FROM observations
                WHERE indicator_code = ?
                LIMIT 1
                """,
                (indicator_code.upper(),),
            )

        row = cursor.fetchone()
        connection.close()

        return row is not None


    @staticmethod
    def get_observations(indicator_code: str) -> list[Observation]:
        """
        Recupera todas las observaciones de un indicador.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                region_code,
                indicator_code,
                source_code,
                date,
                value
            FROM observations
            WHERE indicator_code = ?
            ORDER BY region_code, date
            """,
            (indicator_code.upper(),)
        )

        rows = cursor.fetchall()

        connection.close()

        return ObservationRepository._rows_to_observations(rows)


    @staticmethod
    def get_by_region(region_code: str) -> list[Observation]:
        """
        Recupera todas las observaciones de una región.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                region_code,
                indicator_code,
                source_code,
                date,
                value
            FROM observations
            WHERE region_code = ?
            ORDER BY indicator_code, date
            """,
            (region_code.upper(),)
        )

        rows = cursor.fetchall()

        connection.close()

        return ObservationRepository._rows_to_observations(rows)

    @staticmethod
    def get_by_indicator(indicator_code: str) -> list[Observation]:
        """
        Recupera todas las observaciones de un indicador.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                region_code,
                indicator_code,
                source_code,
                date,
                value
            FROM observations
            WHERE indicator_code = ?
            ORDER BY
                region_code,
                date
            """,
            (indicator_code.upper(),)
        )

        rows = cursor.fetchall()

        connection.close()

        return ObservationRepository._rows_to_observations(rows)


    @staticmethod
    def get_by_region_and_indicator(
        region_code: str,
        indicator_code: str
    ) -> list[Observation]:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                region_code,
                indicator_code,
                source_code,
                date,
                value
            FROM observations
            WHERE
                region_code = ?
                AND indicator_code = ?
            ORDER BY date
            """,
            (region_code.upper(), indicator_code.upper())
        )

        rows = cursor.fetchall()

        connection.close()

        return ObservationRepository._rows_to_observations(rows)
    
    @staticmethod
    def get_by_regions_and_indicator(
        region_codes: list[str],
        indicator_code: str
    ) -> list[Observation]:
        if not region_codes:
            return []

        connection = get_connection()
        cursor = connection.cursor()

        placeholders = ",".join("?" * len(region_codes))

        cursor.execute(
            f"""
            SELECT
                region_code,
                indicator_code,
                source_code,
                date,
                value
            FROM observations
            WHERE
                indicator_code = ?
                AND region_code IN ({placeholders})
            ORDER BY
                region_code,
                date
            """,
            [indicator_code.upper()] + [r.upper() for r in region_codes]
        )

        rows = cursor.fetchall()

        connection.close()

        return ObservationRepository._rows_to_observations(rows)


    @staticmethod
    def _rows_to_observations(rows) -> list[Observation]:
        
        """
        Convierte filas SQLite en objetos Observation.
        """

        observations = []

        for row in rows:

            observations.append(
                Observation(
                    region=RegionService.get_region(row[0]),
                    indicator=IndicatorService.get_indicator(row[1]),
                    source=SourceService.get_by_code(row[2]),
                    date=date.fromisoformat(row[3]),
                    value=row[4]
                )
            )

        return observations

    @staticmethod
    def delete_by_indicator(indicator_code: str):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM observations
            WHERE indicator_code = ?
            """,
            (indicator_code.upper(),)
        )

        connection.commit()
        connection.close()

    @staticmethod
    def delete_by_region_indicator_source(
        region_code: str,
        indicator_code: str,
        source_code: str,
    ):
        """Elimina observaciones de una región, indicador y fuente."""

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM observations
            WHERE region_code = ?
              AND indicator_code = ?
              AND source_code = ?
            """,
            (
                region_code.upper(),
                indicator_code.upper(),
                source_code.upper(),
            ),
        )

        deleted_count = cursor.rowcount

        connection.commit()
        connection.close()

        return deleted_count

    @staticmethod
    def replace_by_region_indicator_source(
        region_code: str,
        indicator_code: str,
        source_code: str,
        observations: list[Observation],
    ) -> int:
        """Reemplaza observaciones de una región, indicador y fuente."""

        return ObservationRepository.replace_batch(
            {
                (region_code, indicator_code, source_code): observations
            }
        )

    @staticmethod
    def replace_batch(
        grouped_observations: dict[tuple[str, str, str], list[Observation]],
    ) -> int:
        """
        Reemplaza múltiples grupos de observaciones (region, indicator, source)
        en una única transacción atómica de base de datos.
        """
        if not grouped_observations:
            return 0

        # Validación previa de contratos
        for (
            region_code,
            indicator_code,
            source_code,
        ), observations in grouped_observations.items():
            r_code = region_code.upper()
            i_code = indicator_code.upper()
            s_code = source_code.upper()

            for obs in observations:
                if (
                    obs.region.code.upper() != r_code
                    or obs.indicator.code.upper() != i_code
                    or obs.source.code.upper() != s_code
                ):
                    raise ValueError(
                        "Todas las observaciones deben pertenecer a "
                        f"{r_code} + {i_code} + {s_code}."
                    )

        connection = get_connection()

        try:
            cursor = connection.cursor()
            total_deleted = 0

            for (
                region_code,
                indicator_code,
                source_code,
            ), observations in grouped_observations.items():
                r_code = region_code.upper()
                i_code = indicator_code.upper()
                s_code = source_code.upper()

                cursor.execute(
                    """
                    DELETE FROM observations
                    WHERE region_code = ?
                      AND indicator_code = ?
                      AND source_code = ?
                    """,
                    (r_code, i_code, s_code),
                )

                total_deleted += cursor.rowcount

                cursor.executemany(
                    """
                    INSERT INTO observations (
                        region_code,
                        indicator_code,
                        source_code,
                        date,
                        value
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            obs.region.code,
                            obs.indicator.code,
                            obs.source.code,
                            obs.date.isoformat(),
                            obs.value,
                        )
                        for obs in observations
                    ],
                )

            connection.commit()
            return total_deleted

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()