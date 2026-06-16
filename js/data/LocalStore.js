// ── CAPA DE PERSISTENCIA: LocalStore (Fase 2) ───────────────────────────────
// Implementación del contrato DataStore sobre localStorage. Es la primera de dos
// implementaciones intercambiables (mañana: ApiStore contra un backend). Los
// módulos consumen SOLO este contrato vía un `repo`, sin tocar localStorage.
//
// CONTRATO DataStore (nivel-colección, async — todo devuelve Promise):
//   getEntradas()            -> Promise<Entrada[]>        saveEntradas(arr)        -> Promise<void>
//   getSalidas()             -> Promise<Salida[]>         saveSalidas(arr)         -> Promise<void>
//   getSolicitudes()         -> Promise<Solicitud[]>      saveSolicitudes(arr)     -> Promise<void>
//   getLevantamientos()      -> Promise<Levantamiento[]>  saveLevantamientos(arr)  -> Promise<void>
//   getBitacora()            -> Promise<Evento[]>         saveBitacora(arr)        -> Promise<void>
//   registrarBitacora(ev)    -> Promise<void>   // añade 1 evento (unshift + cap 200), NO reemplaza
//   getCodigosBarras()       -> Promise<{[barcode]:alias}>  saveCodigosBarras(obj) -> Promise<void>  // alias barcode→interno (MAPA objeto)
//
// IMPORTANTE: este store es ASÍNCRONO desde el día 1 (devuelve promesas) aunque
// hoy resuelva al instante sobre localStorage. Así, al migrar a ApiStore, la
// firma no cambia y los módulos no se reescriben.
//
// NOTA DE FASE 2: solo `modSolicitudes` consume este repo (piloto). El resto del
// contrato queda LISTO pero sin consumir todavía; los demás módulos siguen con su
// propio acceso a localStorage y conviven sobre la MISMA clave sin inconsistencia.
//
// Se preserva EXACTAMENTE el comportamiento actual de los módulos:
//   - claves canónicas con acento exacto (`á`),
//   - colección vacía -> [] (`|| '[]'`),
//   - el try/catch que traga el error de cuota de localStorage,
//   - JSON.stringify sin formato (idéntico a los `guardarLS` actuales),
//   - bitácora: unshift (más reciente primero) + tope de 200 (LIFO).
window.createLocalStore = () => {
  // Registro canónico de claves (acentos EXACTOS). Igual que js/modRespaldo.js.
  const KEYS = {
    entradas:       'zoo_tamatán_entradas_v3',
    salidas:        'zoo_tamatán_salidas_v1',
    solicitudes:    'zoo_tamatán_solicitudes_v1',
    levantamientos: 'zoo_tamatán_levantamientos_v1',
    bitacora:       'zoo_tamatán_bitacora_v3',
    codigosBarras:  'zoo_tamatán_codigos_barras_v1',
  };

  const MAX_BITACORA = 200;

  const leer  = (k)    => { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch { return []; } };
  const grabar = (k, d) => { try { localStorage.setItem(k, JSON.stringify(d)); } catch {} };
  // Lectura para colecciones tipo MAPA (objeto), p. ej. aliases de códigos de barras.
  const leerMapa = (k) => { try { return JSON.parse(localStorage.getItem(k) || '{}'); } catch { return {}; } };

  return {
    // ── Entradas ──────────────────────────────────────────────
    getEntradas:  async ()    => leer(KEYS.entradas),
    saveEntradas: async (arr) => grabar(KEYS.entradas, arr),

    // ── Salidas ───────────────────────────────────────────────
    getSalidas:  async ()    => leer(KEYS.salidas),
    saveSalidas: async (arr) => grabar(KEYS.salidas, arr),

    // ── Solicitudes (consumido por el piloto modSolicitudes) ──
    getSolicitudes:  async ()    => leer(KEYS.solicitudes),
    saveSolicitudes: async (arr) => grabar(KEYS.solicitudes, arr),

    // ── Levantamientos ────────────────────────────────────────
    getLevantamientos:  async ()    => leer(KEYS.levantamientos),
    saveLevantamientos: async (arr) => grabar(KEYS.levantamientos, arr),

    // ── Bitácora ──────────────────────────────────────────────
    getBitacora:  async ()    => leer(KEYS.bitacora),
    saveBitacora: async (arr) => grabar(KEYS.bitacora, arr),
    // Añade UN evento conservando la regla del logger actual (LIFO, tope 200).
    registrarBitacora: async (ev) => {
      const logs = leer(KEYS.bitacora);
      logs.unshift(ev);
      if (logs.length > MAX_BITACORA) logs.pop();
      grabar(KEYS.bitacora, logs);
    },

    // ── Códigos de barras (alias barcode→interno; MAPA objeto, no array) ──
    getCodigosBarras:  async ()    => leerMapa(KEYS.codigosBarras),
    saveCodigosBarras: async (obj) => grabar(KEYS.codigosBarras, obj),
  };
};
