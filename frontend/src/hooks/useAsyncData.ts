import { useEffect, useEffectEvent, useState } from "react";

/**
 * Estado interno: el resultado se guarda junto a la clave de la petición
 * que lo produjo. Así `loading` se deriva comparando claves, sin necesidad
 * de llamar a setState de forma síncrona dentro del efecto.
 */
interface AsyncState<T> {
  key: string | null;
  data: T | null;
  error: unknown;
}

export interface AsyncResult<T> {
  data: T | null;
  error: unknown;
  loading: boolean;
}

/**
 * Carga datos asíncronos asociados a una clave.
 *
 * - `key === null` desactiva la petición (devuelve data=null, loading=false).
 * - Cada cambio de `key` lanza una nueva petición y aborta la anterior
 *   mediante AbortController, evitando condiciones de carrera: una respuesta
 *   lenta de una región/indicador previo nunca sobrescribe la actual.
 * - Los datos de una clave anterior nunca se exponen para la clave actual.
 *
 * @param key     Identificador determinista de la petición (p.ej. "GDP|ES").
 * @param fetcher Función que realiza la petición; recibe un AbortSignal.
 */
export function useAsyncData<T>(
  key: string | null,
  fetcher: (signal: AbortSignal) => Promise<T>,
): AsyncResult<T> {
  const [state, setState] = useState<AsyncState<T>>({
    key: null,
    data: null,
    error: null,
  });

  // El fetcher se lee siempre en su versión más reciente sin
  // convertirlo en dependencia del efecto.
  const runFetch = useEffectEvent((signal: AbortSignal) => fetcher(signal));

  useEffect(() => {
    if (key === null) {
      return;
    }

    const controller = new AbortController();

    runFetch(controller.signal).then(
      (data) => {
        if (!controller.signal.aborted) {
          setState({ key, data, error: null });
        }
      },
      (error: unknown) => {
        if (!controller.signal.aborted) {
          console.error(`[useAsyncData] Error cargando "${key}":`, error);
          setState({ key, data: null, error });
        }
      },
    );

    return () => controller.abort();
  }, [key]);

  const settled = key !== null && state.key === key;

  return {
    data: settled ? state.data : null,
    error: settled ? state.error : null,
    loading: key !== null && !settled,
  };
}
