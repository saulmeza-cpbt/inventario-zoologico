// ── MÓDULO MOVIMIENTO RÁPIDO (SCANNER) ──────────────────────
// Entrada y salida rápida para Snack y Tienda:
//   tipo de movimiento → área → código (interno o de barras) → buscar →
//   cantidad → registrar → Stock actualizado.
//
// FASE 1 (esta versión): captura MANUAL del código o lector USB tipo teclado
// (el Enter dispara la búsqueda). La cámara (BarcodeDetector) se añade como
// mejora progresiva en una fase posterior, sin librerías externas.
//
// El CÓDIGO INTERNO administrativo es el identificador principal. El código de
// barras físico/comercial funciona como ALIAS: si el código escrito no es un
// código interno, se busca en window.CATALOGO_CODIGOS_BARRAS y se resuelve al
// código interno antes de localizar el producto en el catálogo del área.
//
// Reutiliza la lógica existente de cada flujo (sin reimplementarla):
//   - Salida:  registrarSalida()  inyectada desde modSalidas (incluye la
//              validación/bloqueo suave contra stock disponible).
//   - Entrada: registrarEntrada() inyectada desde modEntradas
//              (registrarEntradaRapida: crea documento tipo entrada_rapida).
// NO escribe localStorage directamente ni edita otros módulos.
//
// Patrón factory con inyección de dependencias:
//   - ui:               { toast(msg, tipo) }
//   - registrarSalida({ area, motivo, responsable, articulos }) -> Promise<boolean>
//   - registrarEntrada({ area, responsable, articulos })        -> boolean
//   - onRegistrado(): callback tras un registro OK (refresca Stock + Salidas)
// Dependencias globales (NO se inyectan): window.CATALOGO_INVENTARIO,
// window.CATALOGO_ARTICULOS_POR_AREA, window.CATALOGO_CODIGOS_BARRAS, los
// elementos #scan-* del HTML y la API pública APP.modScanner.
window.createModScanner = ({ ui, registrarSalida, registrarEntrada, onRegistrado }) => {
    const MOTIVO_SALIDA = 'Salida rápida por escaneo';
    const AREAS_OK = ['Snack', 'Tienda'];
    let artActual = null;   // { descripcion, codigo, unidad, precio, barcode } resuelto

    const $ = (id) => document.getElementById(id);

    const tipoMov = () => ($('scan-tipo')?.value || 'salida');

    // Busca un artículo por código INTERNO exacto dentro del área indicada.
    //   1) catálogo base abril (campos c/n/u/p)
    //   2) catálogo maestro ene-abr (campos codigo/nombre; unidad → 'PZA', sin precio)
    const buscarPorCodigoInterno = (area, codigo) => {
      const norm = (codigo || '').trim().toLowerCase();
      if (!norm) return null;
      const base = window.CATALOGO_INVENTARIO?.[area] || [];
      const hb = base.find(a => (a.c || '').trim().toLowerCase() === norm);
      if (hb) return { descripcion: hb.n, codigo: hb.c, unidad: hb.u || 'PZA', precio: parseFloat(hb.p) || 0 };
      const maestro = window.CATALOGO_ARTICULOS_POR_AREA?.[area] || [];
      const hm = maestro.find(a => (a.codigo || '').trim().toLowerCase() === norm);
      if (hm) return { descripcion: hm.nombre, codigo: hm.codigo, unidad: 'PZA', precio: 0 };
      return null;
    };

    // Resuelve el código escrito/escaneado siguiendo el orden:
    //   1) ¿es un código interno del área? → devuelve el artículo (sin barcode).
    //   2) si no, ¿está en CATALOGO_CODIGOS_BARRAS? → resuelve al interno y lo
    //      busca en el área seleccionada (devuelve el artículo + barcode físico).
    //   3) si el alias existe pero apunta a otra área → { _mismatch: <área> }.
    //   4) si nada coincide → null.
    const resolverCodigo = (area, escaneado) => {
      const directo = buscarPorCodigoInterno(area, escaneado);
      if (directo) return { ...directo, barcode: '' };
      const alias = window.CATALOGO_CODIGOS_BARRAS?.[(escaneado || '').trim()];
      if (alias) {
        const porAlias = buscarPorCodigoInterno(area, alias.codigo);
        if (porAlias) return { ...porAlias, barcode: (escaneado || '').trim() };
        if (alias.area && alias.area !== area) return { _mismatch: alias.area };
      }
      return null;
    };

    const setRegistrarHabilitado = (on) => {
      const btn = $('scan-registrar');
      if (btn) btn.disabled = !on;
    };

    // Texto del botón según el tipo de movimiento seleccionado.
    const actualizarBotonRegistrar = () => {
      const btn = $('scan-registrar');
      if (btn) btn.textContent = tipoMov() === 'entrada' ? '📥 Registrar entrada' : '📤 Registrar salida';
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
      if (art._mismatch) {
        box.innerHTML = `<div style="padding:10px 12px;border:1px solid #fbd38d;background:#fffaf0;border-radius:8px;color:#975a16;font-size:13px;">
          ⚠️ Ese código de barras pertenece al área <b>${art._mismatch}</b>. Cambia el área seleccionada.</div>`;
        return;
      }
      box.innerHTML = `<div style="padding:10px 12px;border:1px solid #9ae6b4;background:#f0fff4;border-radius:8px;">
        <div style="font-size:11px;color:#718096;font-family:monospace;">${art.codigo || '—'}</div>
        <div style="font-size:15px;font-weight:700;color:#22543d;">${art.descripcion}</div>
        <div style="font-size:12px;color:#718096;">Unidad: ${art.unidad}</div>
        ${art.barcode ? `<div style="font-size:11px;color:#718096;font-family:monospace;">Código de barras: ${art.barcode}</div>` : ''}
      </div>`;
    };

    const api = {
      onTipoChange: () => {
        actualizarBotonRegistrar();
        if ($('scan-codigo')) $('scan-codigo').value = '';
        limpiarResultado();
        $('scan-codigo')?.focus();
      },

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
        const art = resolverCodigo(area, codigo);
        renderResultado(art);
        if (art && !art._mismatch) {
          artActual = art;
          setRegistrarHabilitado(true);
          $('scan-cant')?.focus();
        } else {
          artActual = null;
          setRegistrarHabilitado(false);
        }
      },

      registrar: async () => {
        const area = $('scan-area')?.value || '';
        if (!AREAS_OK.includes(area)) { ui.toast('❌ Selecciona Snack o Tienda', 'err'); return; }
        if (!artActual) { ui.toast('❌ Primero busca un artículo por código', 'err'); return; }
        const cantidad = parseFloat($('scan-cant')?.value || 0);
        if (!(cantidad > 0)) { ui.toast('❌ La cantidad debe ser mayor a 0', 'err'); $('scan-cant')?.focus(); return; }
        const responsable = $('scan-responsable')?.value?.trim() || '';

        // Una operación = un artículo por registro (alcance de esta demo).
        const articulo = {
          descripcion: artActual.descripcion,
          codigo:      artActual.codigo || '',
          unidad:      artActual.unidad || 'PZA',
          precio:      parseFloat(artActual.precio) || 0,
          cantidad,
        };

        let ok;
        if (tipoMov() === 'entrada') {
          // Entrada rápida: el stock SUBE. El precio (si el catálogo lo trae) se
          // pasa para que los reportes de entradas queden mejor; si no, será 0.
          ok = registrarEntrada({ area, responsable, articulos: [articulo] });
        } else {
          // Salida rápida: reutiliza la validación/bloqueo suave de stock.
          ok = await registrarSalida({ area, motivo: MOTIVO_SALIDA, responsable, articulos: [articulo] });
        }
        if (!ok) return;   // validación falló o se canceló el override de stock

        // Refresca Stock + historial de Salidas (solo APIs públicas). El
        // historial de Entradas y el Dashboard los refresca registrarEntradaRapida.
        if (typeof onRegistrado === 'function') onRegistrado();

        // Listo para el siguiente escaneo: conserva tipo y área, limpia lo demás.
        if ($('scan-codigo')) $('scan-codigo').value = '';
        if ($('scan-cant'))   $('scan-cant').value = '1';
        limpiarResultado();
        $('scan-codigo')?.focus();
      },

      // Llamado al entrar a la pestaña: estado limpio y foco en el código.
      onShow: () => {
        actualizarBotonRegistrar();
        limpiarResultado();
        if ($('scan-codigo')) $('scan-codigo').value = '';
        if ($('scan-cant'))   $('scan-cant').value = '1';
        $('scan-codigo')?.focus();
      },
    };

    return api;
};
