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
window.createModScanner = ({ ui, registrarSalida, registrarEntrada, onRegistrado, guardarAlias }) => {
    const MOTIVO_SALIDA = 'Salida rápida por escaneo';
    const AREAS_OK = ['Snack', 'Tienda'];
    let artActual = null;   // { descripcion, codigo, unidad, precio, barcode } resuelto
    let vincBarcode = '';   // código físico no reconocido, pendiente de vincular (String crudo)
    let vincSel     = null; // { codigo, descripcion } destino elegido en el autocompletar
    let vincLista   = [];   // sugerencias actuales del autocompletar

    const $ = (id) => document.getElementById(id);

    // Escapa texto antes de interpolarlo en innerHTML (protege el markup y los
    // onclick generados). No altera el dato persistido: solo la salida visual.
    const escapeHtml = (str) => String(str ?? '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

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

    // Lista de artículos del área (código interno + descripción) para el
    // autocompletar de vinculación. Mismas fuentes que buscarPorCodigoInterno,
    // sin duplicar por código interno (base abril gana sobre maestro ene-abr).
    const listarArticulosArea = (area) => {
      const out = [], vistos = new Set();
      const push = (codigo, descripcion) => {
        const k = (codigo || '').trim();
        if (k && !vistos.has(k.toLowerCase())) { vistos.add(k.toLowerCase()); out.push({ codigo: k, descripcion }); }
      };
      (window.CATALOGO_INVENTARIO?.[area] || []).forEach(a => push(a.c, a.n));
      (window.CATALOGO_ARTICULOS_POR_AREA?.[area] || []).forEach(a => push(a.codigo, a.nombre));
      return out;
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
      vincBarcode = ''; vincSel = null; vincLista = [];
      const box = $('scan-resultado');
      if (box) box.innerHTML = '';
      setRegistrarHabilitado(false);
    };

    // Form de vinculación cuando el código no se reconoce: deja al usuario
    // asociar el código físico escaneado a un artículo interno del área.
    const renderVincForm = (barcode) => `<div style="padding:10px 12px;border:1px solid #fbd38d;background:#fffaf0;border-radius:8px;">
        <div style="font-size:13px;color:#975a16;margin-bottom:8px;">⚠️ Código <b style="font-family:monospace;">${escapeHtml(barcode)}</b> no reconocido. Vincúlalo a un artículo del área:</div>
        <input id="scan-vinc-q" type="text" autocomplete="off" placeholder="Nombre o código interno…"
          oninput="APP.modScanner.onVincInput()"
          style="display:block;width:100%;padding:8px;border:1px solid #cbd5e0;border-radius:6px;font-size:14px;margin-bottom:6px;">
        <div id="scan-vinc-sug"></div>
        <button id="scan-vinc-btn" class="btn btn-p" onclick="APP.modScanner.vincular()" disabled
          style="width:100%;padding:10px;font-size:14px;margin-top:6px;">🔗 Vincular código</button>
      </div>`;

    const renderResultado = (art) => {
      const box = $('scan-resultado');
      if (!box) return;
      vincSel = null; vincLista = [];
      if (!art) {
        vincBarcode = ($('scan-codigo')?.value || '').trim();
        box.innerHTML = renderVincForm(vincBarcode);
        return;
      }
      vincBarcode = '';
      if (art._mismatch) {
        box.innerHTML = `<div style="padding:10px 12px;border:1px solid #fbd38d;background:#fffaf0;border-radius:8px;color:#975a16;font-size:13px;">
          ⚠️ Ese código de barras pertenece al área <b>${escapeHtml(art._mismatch)}</b>. Cambia el área seleccionada.</div>`;
        return;
      }
      box.innerHTML = `<div style="padding:10px 12px;border:1px solid #9ae6b4;background:#f0fff4;border-radius:8px;">
        <div style="font-size:11px;color:#718096;font-family:monospace;">${escapeHtml(art.codigo || '—')}</div>
        <div style="font-size:15px;font-weight:700;color:#22543d;">${escapeHtml(art.descripcion)}</div>
        <div style="font-size:12px;color:#718096;">Unidad: ${escapeHtml(art.unidad)}</div>
        ${art.barcode ? `<div style="font-size:11px;color:#718096;font-family:monospace;">Código de barras: ${escapeHtml(art.barcode)}</div>
        <button class="btn btn-s" onclick="APP.modScanner.cambiarVinculo()" style="margin-top:8px;padding:6px 10px;font-size:12px;">🔁 Cambiar vínculo</button>` : ''}
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
      onCodigoInput: () => { if (artActual || vincBarcode) limpiarResultado(); },

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

      // Autocompletar destino: filtra los artículos del área por nombre o código
      // interno y pinta hasta 8 sugerencias (texto escapado).
      onVincInput: () => {
        const area = $('scan-area')?.value || '';
        const q = ($('scan-vinc-q')?.value || '').trim().toLowerCase();
        const sug = $('scan-vinc-sug');
        vincSel = null;
        if ($('scan-vinc-btn')) $('scan-vinc-btn').disabled = true;
        if (!sug) return;
        if (!q) { sug.innerHTML = ''; vincLista = []; return; }
        vincLista = listarArticulosArea(area)
          .filter(a => a.descripcion.toLowerCase().includes(q) || a.codigo.toLowerCase().includes(q))
          .slice(0, 8);
        sug.innerHTML = vincLista.length
          ? vincLista.map((a, i) => `<div onclick="APP.modScanner.seleccionarVinc(${i})"
              style="padding:6px 8px;border:1px solid #e2e8f0;border-radius:6px;margin-bottom:4px;cursor:pointer;font-size:13px;">
              <span style="font-family:monospace;color:#718096;">${escapeHtml(a.codigo)}</span> — ${escapeHtml(a.descripcion)}</div>`).join('')
          : `<div style="font-size:12px;color:#a0aec0;padding:4px;">Sin coincidencias</div>`;
      },

      // Fija el artículo destino elegido y habilita el botón Vincular.
      seleccionarVinc: (idx) => {
        vincSel = vincLista[idx] || null;
        if (!vincSel) return;
        if ($('scan-vinc-q')) $('scan-vinc-q').value = `${vincSel.codigo} — ${vincSel.descripcion}`;
        if ($('scan-vinc-sug')) $('scan-vinc-sug').innerHTML = '';
        if ($('scan-vinc-btn')) $('scan-vinc-btn').disabled = false;
      },

      // Reabre el mini-formulario para RE-vincular un código ya asociado (corrección
      // de captura). Reutiliza el mismo barcode y el flujo vincular()/guardarAlias
      // (sobrescritura con confirm() + WARN). Solo aplica a resultados por alias.
      cambiarVinculo: () => {
        if (!artActual || !artActual.barcode) return;
        vincBarcode = artActual.barcode;   // mismo código físico ya escaneado
        vincSel = null; vincLista = [];
        artActual = null;                  // sale de modo "registrar" hasta re-resolver
        setRegistrarHabilitado(false);
        const box = $('scan-resultado');
        if (box) box.innerHTML = renderVincForm(vincBarcode);
        $('scan-vinc-q')?.focus();
      },

      // Persiste el alias (vía guardarAlias inyectado), valida el destino y
      // re-resuelve para mostrar la tarjeta del artículo ya vinculado.
      vincular: async () => {
        const area = $('scan-area')?.value || '';
        if (!AREAS_OK.includes(area)) { ui.toast('❌ Selecciona Snack o Tienda', 'err'); return; }
        if (!vincBarcode) { ui.toast('❌ No hay código por vincular', 'err'); return; }
        if (!vincSel)     { ui.toast('❌ Elige el artículo destino', 'err'); return; }
        if (typeof guardarAlias !== 'function') { ui.toast('❌ Vinculación no disponible', 'err'); return; }
        // El destino debe seguir siendo un código interno válido del área.
        if (!buscarPorCodigoInterno(area, vincSel.codigo)) { ui.toast('❌ El artículo destino no existe en el área', 'err'); return; }
        const reVinculo = !!window.CATALOGO_CODIGOS_BARRAS?.[vincBarcode];  // ya tenía alias → es actualización
        const ok = await guardarAlias({ barcode: vincBarcode, area, codigo: vincSel.codigo });
        if (!ok) {                                   // colisión cancelada: nada cambia
          if ($('scan-codigo')) $('scan-codigo').value = vincBarcode;
          api.buscar();                              // re-resuelve y restaura la tarjeta vigente
          return;
        }
        ui.toast(reVinculo ? '🔁 Vínculo actualizado' : '🔗 Código vinculado', 'ok');
        if ($('scan-codigo')) $('scan-codigo').value = vincBarcode;
        api.buscar();      // re-resuelve: ahora cae por alias y muestra la tarjeta verde
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
