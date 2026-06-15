// ── MÓDULO REPORTES CSV ─────────────────────────────────────
// Exporta Entradas y Salidas a archivos CSV (UTF-8 con BOM) filtrables por
// área y por mes. Pensado para abrir en Excel / LibreOffice.
//
// SOLO LECTURA: nunca escribe localStorage, nunca muta el estado ni la lógica
// de inventario. Toma copias en memoria de los datos existentes y las
// transforma a CSV. No toca modStock, modSalidas ni modRespaldo.
//
// Patrón factory con inyección de dependencias (igual que modStock/modSalidas/
// modRespaldo). Dependencias inyectadas desde el IIFE principal:
//   - getEntradas(): Array de documentos de entrada (estado.documentos)
//   - getSalidas():  Array de salidas (localStorage 'zoo_tamatán_salidas_v1')
//   - TIPOS_DOC:     CONFIG.TIPOS_DOC (para el nombre legible del tipo)
//   - ui:     { toast(msg, tipo) } para notificaciones
//   - logger: { info(msg, entidad, accion) } para la bitácora
// Dependencias DOM (NO se inyectan): #rep-area, #rep-mes y la API APP.modReportes.
window.createModReportes = ({ getEntradas, getSalidas, TIPOS_DOC, ui, logger }) => {

    // Sello de tiempo para nombres de archivo: AAAA-MM-DD_HHMM
    const sello = () => {
      const d = new Date();
      const p = (n) => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}`;
    };

    // Fecha de registro (a partir de ts epoch) en ISO corto AAAA-MM-DD:
    // ordenable y sin ambigüedad de locale.
    const fechaRegistro = (ts) => {
      if (!ts) return '';
      const d = new Date(ts);
      const p = (n) => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
    };

    // Clave AAAA-MM derivada de un ts, para comparar con el filtro <input type=month>.
    const claveMes = (ts) => {
      if (!ts) return '';
      const d = new Date(ts);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    };

    // Slug para nombres de archivo: 'Nutrición' → 'nutricion'.
    const slug = (s) => (s || '')
      .toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');

    // Lee los filtros de la UI. mes = '' (todos) o 'AAAA-MM'.
    const leerFiltros = () => ({
      area: (document.getElementById('rep-area')?.value || '').trim(),
      mes:  (document.getElementById('rep-mes')?.value || '').trim(),
    });

    const coincideArea = (area, filtro) => !filtro || area === filtro;
    const coincideMes  = (ts, filtro)   => !filtro || claveMes(ts) === filtro;

    // Escapa un campo CSV: a texto, comillas dobladas, saltos de línea a espacio,
    // y SIEMPRE entre comillas (robusto ante comas y comillas en los datos).
    const esc = (v) => {
      const s = (v === null || v === undefined) ? '' : String(v);
      return '"' + s.replace(/"/g, '""').replace(/\r?\n/g, ' ') + '"';
    };

    // Construye el texto CSV (CRLF entre filas, coma entre campos).
    const construirCSV = (headers, filas) =>
      [headers, ...filas].map(row => row.map(esc).join(',')).join('\r\n');

    // Descarga un CSV con BOM UTF-8 para que Excel respete los acentos.
    const descargarCSV = (texto, nombre) => {
      const blob = new Blob(['﻿' + texto], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = nombre;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    };

    // Sufijo de filtros para el nombre de archivo.
    const sufijoFiltros = ({ area, mes }) =>
      `${area ? slug(area) : 'todas'}_${mes || 'todos'}`;

    // ── ENTRADAS ──────────────────────────────────────────────
    // Una fila por artículo. Filtra a nivel documento por área (areaDestino,
    // con fallback areaRequirente) y por mes (ts de registro).
    const filasEntradas = (filtros) => {
      const HEADERS = ['Fecha registro', 'Área', 'Tipo documento', 'Folio documento',
        'Responsable', 'Motivo', 'Código', 'Artículo', 'Cantidad', 'Precio unitario', 'Importe'];
      const filas = [];
      (getEntradas() || []).forEach(doc => {
        const area = doc.datos?.areaDestino || doc.datos?.areaRequirente || '';
        if (!coincideArea(area, filtros.area)) return;
        if (!coincideMes(doc.ts, filtros.mes)) return;
        const tipoNombre = TIPOS_DOC?.[doc.tipo]?.nombre || doc.tipo || '';
        const folioDoc   = doc.datos?.folioDocumento || '';
        const responsable = doc.datos?.responsable || '';
        const motivo     = doc.datos?.motivo || '';
        const fecha      = fechaRegistro(doc.ts);
        (doc.articulos || []).forEach(art => {
          const cantidad = parseFloat(art.cantidad) || 0;
          const unitario = parseFloat(art.unitario) || 0;
          const importe  = Math.round(cantidad * unitario * 100) / 100;
          filas.push([fecha, area, tipoNombre, folioDoc, responsable, motivo,
            art.codigo || '', art.nombre || '', cantidad, unitario, importe]);
        });
      });
      return { HEADERS, filas };
    };

    // ── SALIDAS ───────────────────────────────────────────────
    // Una fila por artículo. Filtra por área (sal.area) y por mes (ts).
    const filasSalidas = async (filtros) => {
      const HEADERS = ['Fecha registro', 'Área', 'Folio/ID', 'Responsable',
        'Motivo', 'Código', 'Artículo', 'Cantidad', 'Unidad'];
      const filas = [];
      (await getSalidas() || []).forEach(sal => {
        if (!coincideArea(sal.area || '', filtros.area)) return;
        if (!coincideMes(sal.ts, filtros.mes)) return;
        const fecha = fechaRegistro(sal.ts);
        (sal.articulos || []).forEach(art => {
          const cantidad = parseFloat(art.cantidad) || 0;
          filas.push([fecha, sal.area || '', sal.id || '', sal.responsable || '',
            sal.motivo || '', art.codigo || '', art.descripcion || '', cantidad, art.unidad || '']);
        });
      });
      return { HEADERS, filas };
    };

    return {
      exportarEntradas: () => {
        const filtros = leerFiltros();
        const { HEADERS, filas } = filasEntradas(filtros);
        if (!filas.length) {
          ui.toast('📭 No hay entradas para ese filtro', 'err');
          return;
        }
        descargarCSV(construirCSV(HEADERS, filas),
          `reporte_entradas_${sufijoFiltros(filtros)}_${sello()}.csv`);
        logger.info(
          `Reporte de entradas exportado (${filas.length} fila(s)) — área: ${filtros.area || 'todas'}, mes: ${filtros.mes || 'todos'}`,
          'Reportes', 'Exportar Entradas CSV');
        ui.toast(`✓ Entradas exportadas (${filas.length} fila(s))`, 'ok');
      },

      exportarSalidas: async () => {
        const filtros = leerFiltros();
        const { HEADERS, filas } = await filasSalidas(filtros);
        if (!filas.length) {
          ui.toast('📭 No hay salidas para ese filtro', 'err');
          return;
        }
        descargarCSV(construirCSV(HEADERS, filas),
          `reporte_salidas_${sufijoFiltros(filtros)}_${sello()}.csv`);
        logger.info(
          `Reporte de salidas exportado (${filas.length} fila(s)) — área: ${filtros.area || 'todas'}, mes: ${filtros.mes || 'todos'}`,
          'Reportes', 'Exportar Salidas CSV');
        ui.toast(`✓ Salidas exportadas (${filas.length} fila(s))`, 'ok');
      },
    };
};
