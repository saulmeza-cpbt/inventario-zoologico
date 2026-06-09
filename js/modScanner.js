// ── MÓDULO SALIDA RÁPIDA (SCANNER) ──────────────────────────
// Demo de salida rápida para Snack y Tienda:
//   código del artículo → buscar → cantidad → registrar salida → Stock actualizado.
//
// FASE 1 (esta versión): captura MANUAL del código. La cámara (BarcodeDetector)
// se añade como mejora progresiva en una fase posterior, sin librerías externas.
//
// Reutiliza la lógica de Salidas: registra vía registrarSalida() inyectada
// (validación + bloqueo suave de stock + confirm + persistencia + logger + toast
// + bitácora). NO escribe localStorage directamente ni edita otros módulos.
//
// Patrón factory con inyección de dependencias:
//   - ui:             { toast(msg, tipo) }
//   - registrarSalida({ area, motivo, responsable, articulos }) -> boolean
//   - onRegistrado(): callback tras un registro OK (refresca Stock + Salidas)
// Dependencias globales (NO se inyectan): window.CATALOGO_INVENTARIO,
// window.CATALOGO_ARTICULOS_POR_AREA, los elementos #scan-* del HTML y la API
// pública APP.modScanner.
window.createModScanner = ({ ui, registrarSalida, onRegistrado }) => {
    const MOTIVO = 'Salida rápida por escaneo';
    const AREAS_OK = ['Snack', 'Tienda'];
    let artActual = null;   // { descripcion, codigo, unidad } resuelto del catálogo

    const $ = (id) => document.getElementById(id);

    // Busca un artículo por código EXACTO dentro del área indicada.
    //   1) catálogo base abril (campos c/n/u)
    //   2) catálogo maestro ene-abr (campos codigo/nombre; unidad → 'PZA')
    const buscarPorCodigo = (area, codigo) => {
      const norm = (codigo || '').trim().toLowerCase();
      if (!norm) return null;
      const base = window.CATALOGO_INVENTARIO?.[area] || [];
      const hb = base.find(a => (a.c || '').trim().toLowerCase() === norm);
      if (hb) return { descripcion: hb.n, codigo: hb.c, unidad: hb.u || 'PZA' };
      const maestro = window.CATALOGO_ARTICULOS_POR_AREA?.[area] || [];
      const hm = maestro.find(a => (a.codigo || '').trim().toLowerCase() === norm);
      if (hm) return { descripcion: hm.nombre, codigo: hm.codigo, unidad: 'PZA' };
      return null;
    };

    const setRegistrarHabilitado = (on) => {
      const btn = $('scan-registrar');
      if (btn) btn.disabled = !on;
    };

    const limpiarResultado = () => {
      artActual = null;
      const box = $('scan-resultado');
      if (box) box.innerHTML = '';
      setRegistrarHabilitado(false);
    };

    const renderResultado = (art) => {
      const box = $('scan-resultado');
      if (!box) return;
      if (!art) {
        box.innerHTML = `<div style="padding:10px 12px;border:1px solid #fed7d7;background:#fff5f5;border-radius:8px;color:#9b2c2c;font-size:13px;">
          ❌ No se encontró ningún artículo con ese código en el área seleccionada.</div>`;
        return;
      }
      box.innerHTML = `<div style="padding:10px 12px;border:1px solid #9ae6b4;background:#f0fff4;border-radius:8px;">
        <div style="font-size:11px;color:#718096;font-family:monospace;">${art.codigo || '—'}</div>
        <div style="font-size:15px;font-weight:700;color:#22543d;">${art.descripcion}</div>
        <div style="font-size:12px;color:#718096;">Unidad: ${art.unidad}</div>
      </div>`;
    };

    const api = {
      onAreaChange: () => {
        if ($('scan-codigo')) $('scan-codigo').value = '';
        limpiarResultado();
      },

      // Al cambiar el texto del código se invalida el resultado previo, para no
      // registrar un artículo que ya no corresponde a lo escrito.
      onCodigoInput: () => { if (artActual) limpiarResultado(); },

      buscar: () => {
        const area   = $('scan-area')?.value || '';
        const codigo = $('scan-codigo')?.value?.trim() || '';
        if (!AREAS_OK.includes(area)) { ui.toast('❌ Selecciona Snack o Tienda', 'err'); return; }
        if (!codigo) { ui.toast('❌ Escribe o escanea un código', 'err'); $('scan-codigo')?.focus(); return; }
        const art = buscarPorCodigo(area, codigo);
        renderResultado(art);
        if (art) {
          artActual = art;
          setRegistrarHabilitado(true);
          $('scan-cant')?.focus();
        } else {
          artActual = null;
          setRegistrarHabilitado(false);
        }
      },

      registrar: () => {
        const area = $('scan-area')?.value || '';
        if (!AREAS_OK.includes(area)) { ui.toast('❌ Selecciona Snack o Tienda', 'err'); return; }
        if (!artActual) { ui.toast('❌ Primero busca un artículo por código', 'err'); return; }
        const cantidad = parseFloat($('scan-cant')?.value || 0);
        if (!(cantidad > 0)) { ui.toast('❌ La cantidad debe ser mayor a 0', 'err'); $('scan-cant')?.focus(); return; }
        const responsable = $('scan-responsable')?.value?.trim() || '';

        // Una salida = un artículo por registro (alcance de esta demo).
        const ok = registrarSalida({
          area,
          motivo: MOTIVO,
          responsable,
          articulos: [{
            descripcion: artActual.descripcion,
            codigo:      artActual.codigo || '',
            unidad:      artActual.unidad || 'PZA',
            cantidad,
          }],
        });
        if (!ok) return;   // validación falló o se canceló el override de stock

        // Refresca Stock + historial de Salidas (solo APIs públicas).
        if (typeof onRegistrado === 'function') onRegistrado();

        // Listo para el siguiente escaneo: conserva el área, limpia lo demás.
        if ($('scan-codigo')) $('scan-codigo').value = '';
        if ($('scan-cant'))   $('scan-cant').value = '1';
        limpiarResultado();
        $('scan-codigo')?.focus();
      },

      // Llamado al entrar a la pestaña: estado limpio y foco en el código.
      onShow: () => {
        limpiarResultado();
        if ($('scan-codigo')) $('scan-codigo').value = '';
        if ($('scan-cant'))   $('scan-cant').value = '1';
        $('scan-codigo')?.focus();
      },
    };

    return api;
};
