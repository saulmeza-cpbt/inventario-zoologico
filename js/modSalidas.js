// ── MÓDULO SALIDAS ──────────────────────────────────────────
// Registro de salidas de inventario por área (motivo obligatorio).
// Persiste vía repo.getSalidas() / repo.saveSalidas() (DataStore async, Fase 2).
//
// Segundo módulo extraído del HTML (roadmap-PR12: modularización).
// Patrón: factory con inyección de dependencias. Se invoca desde el IIFE
// principal con las dependencias del closure que necesita:
//   - ui: { toast(msg, tipo) } para notificaciones
//   - logger: { info(msg, entidad, accion) } para la bitácora
//   - repo: { getSalidas(), saveSalidas(arr) } contrato DataStore
// Dependencias globales (NO se inyectan): window.CATALOGO_INVENTARIO,
// window.CATALOGO_ARTICULOS_POR_AREA, los elementos #sal-* del HTML y la
// API pública APP.modSalidas.
window.createModSalidas = ({ ui, logger, calcularStockTeorico, repo }) => {
    let artsTemp = [];

    // Stock disponible por artículo en un área, con la MISMA fórmula que el módulo
    // Stock: base (existencia del catálogo) + entradas - salidas. Reutiliza
    // calcularStockTeorico (movimientos) y la base de window.CATALOGO_INVENTARIO.
    const stockDisponible = (area) => {
      const mov = calcularStockTeorico(area);
      const out = {};
      (window.CATALOGO_INVENTARIO?.[area] || []).forEach(art => {
        out[art.n.toLowerCase().trim()] = (art.e || 0);
      });
      Object.entries(mov).forEach(([k, m]) => {
        out[k] = (out[k] || 0) + (m.entradas || 0) - (m.salidas || 0);
      });
      return out;
    };

    const renderArts = () => {
      const tbody = document.getElementById('sal-arts-body');
      if (!tbody) return;
      if (!artsTemp.length) {
        tbody.innerHTML = '<tr><td colspan="5" style="color:#a0aec0;text-align:center;padding:8px;">Sin artículos</td></tr>';
        return;
      }
      tbody.innerHTML = artsTemp.map((a, i) => `<tr>
        <td class="mono" style="font-size:11px;color:#718096;">${a.codigo||'—'}</td>
        <td>${a.descripcion}</td>
        <td class="mono">${a.cantidad}</td>
        <td style="font-size:12px;color:#718096;">${a.unidad}</td>
        <td><button class="btn btn-r btn-sm" onclick="APP.modSalidas.removeArt(${i})">✕</button></td>
      </tr>`).join('');
    };

    const api = {
      onAreaChange: () => {
        document.getElementById('sal-art-nombre').value = '';
        document.getElementById('sal-art-codigo').value = '';
        const box = document.getElementById('sal-art-sugerencias');
        if (box) box.style.display = 'none';
      },

      filtrarCatalogo: (texto) => {
        const box = document.getElementById('sal-art-sugerencias');
        const inp = document.getElementById('sal-art-nombre');
        if (!box || !inp) return;
        const q = texto.trim().toLowerCase();
        if (!q) { box.style.display = 'none'; return; }

        const area = document.getElementById('sal-area')?.value || '';
        const catBase = window.CATALOGO_INVENTARIO || {};
        const mapa = {};
        const codigosVistos = new Set();
        const areasBase = area ? [area] : Object.keys(catBase);
        areasBase.forEach(a => {
          (catBase[a] || []).forEach(art => {
            const key = art.n.toLowerCase().trim();
            if (!mapa[key]) { mapa[key] = { nombre: art.n, codigo: art.c||'', unidad: art.u||'PZA' }; if (art.c) codigosVistos.add(art.c); }
          });
        });
        // Capa maestro Enero-Abril (dedup por código, backfill de unidad por código).
        const catMaestro = window.CATALOGO_ARTICULOS_POR_AREA || {};
        const idxUnidad = {};
        Object.values(catBase).forEach(arr => (arr||[]).forEach(art => { if (art.c) idxUnidad[art.c] = art.u || 'PZA'; }));
        const areasMaestro = area ? [area] : Object.keys(catMaestro);
        areasMaestro.forEach(a => {
          (catMaestro[a] || []).forEach(art => {
            const cod = art.codigo || '';
            if (cod && codigosVistos.has(cod)) return;
            const key = (art.nombre||'').toLowerCase().trim();
            if (!key || mapa[key]) return;
            mapa[key] = { nombre: art.nombre, codigo: cod, unidad: (cod && idxUnidad[cod]) || 'PZA' };
            if (cod) codigosVistos.add(cod);
          });
        });
        const coincidencias = Object.values(mapa).filter(a =>
          a.nombre.toLowerCase().includes(q) || (a.codigo && a.codigo.toLowerCase().includes(q))
        ).slice(0, 8);

        if (!coincidencias.length) { box.style.display = 'none'; return; }

        const r = inp.getBoundingClientRect();
        box.style.top   = (r.bottom + 2) + 'px';
        box.style.left  = r.left + 'px';
        box.style.width = r.width + 'px';
        box.dataset.catalogo = JSON.stringify(coincidencias);
        box.innerHTML = coincidencias.map((a, i) => `
          <div onclick="APP.modSalidas.seleccionarSugerencia(${i})"
            style="padding:8px 12px;cursor:pointer;border-bottom:1px solid #f0f4f8;display:flex;justify-content:space-between;"
            onmouseover="this.style.background='#ebf4ff'" onmouseout="this.style.background=''">
            <span>${a.codigo ? `<span style="font-family:monospace;font-size:11px;color:#718096;margin-right:6px;">${a.codigo}</span>` : ''}<strong>${a.nombre}</strong></span>
            <span style="font-size:11px;color:#718096;">${a.unidad}</span>
          </div>`).join('');
        box.style.display = 'block';
      },

      seleccionarSugerencia: (idx) => {
        const box = document.getElementById('sal-art-sugerencias');
        if (!box) return;
        const cat = JSON.parse(box.dataset.catalogo || '[]');
        const art = cat[idx];
        if (!art) return;
        document.getElementById('sal-art-nombre').value  = art.nombre;
        document.getElementById('sal-art-codigo').value  = art.codigo || '';
        document.getElementById('sal-art-unidad').value  = art.unidad || 'PZA';
        document.getElementById('sal-art-cant').focus();
        box.style.display = 'none';
      },

      addArt: () => {
        const nombre = document.getElementById('sal-art-nombre')?.value?.trim();
        const cantidad = parseFloat(document.getElementById('sal-art-cant')?.value || 0);
        if (!nombre || cantidad <= 0) { ui.toast('❌ Artículo y cantidad son obligatorios', 'err'); return; }
        artsTemp.push({
          descripcion: nombre,
          codigo:   document.getElementById('sal-art-codigo')?.value?.trim() || '',
          unidad:   document.getElementById('sal-art-unidad')?.value?.trim() || 'PZA',
          cantidad
        });
        document.getElementById('sal-art-nombre').value = '';
        document.getElementById('sal-art-codigo').value = '';
        document.getElementById('sal-art-cant').value   = '1';
        document.getElementById('sal-art-unidad').value = '';
        renderArts();
      },

      removeArt: (i) => { artsTemp.splice(i, 1); renderArts(); },

      // Lógica COMPARTIDA de registro de salida: validación + bloqueo suave de
      // stock (confirm + warn en bitácora si hay override) + persistencia +
      // logger + toast. NO toca el DOM ni re-renderiza (eso queda en cada
      // llamador). Devuelve true si registró, false si falló validación o se
      // canceló el override. La usan guardar() (formulario) y modScanner.
      registrarSalida: async ({ area, motivo, responsable = '', articulos = [] }) => {
        if (!area)   { ui.toast('❌ Selecciona el área origen', 'err'); return false; }
        if (!motivo) { ui.toast('❌ El motivo es obligatorio', 'err'); return false; }
        if (!articulos.length) { ui.toast('❌ Agrega al menos un artículo', 'err'); return false; }

        // Bloqueo suave de stock: ninguna salida debe dejar el stock en negativo.
        // Si excede, se advierte y se pide confirmación; al aceptar, se registra y
        // se deja evidencia en bitácora (override por stock insuficiente).
        const disp = stockDisponible(area);
        const solicitado = {};
        articulos.forEach(a => {
          const k = a.descripcion.toLowerCase().trim();
          solicitado[k] = (solicitado[k] || 0) + (parseFloat(a.cantidad) || 0);
        });
        const conflictos = [];
        Object.entries(solicitado).forEach(([k, cant]) => {
          const d = disp[k] || 0;
          if (cant > d) {
            const art = articulos.find(a => a.descripcion.toLowerCase().trim() === k);
            conflictos.push({ desc: art ? art.descripcion : k, disp: d, cant });
          }
        });
        if (conflictos.length) {
          const detalle = conflictos
            .map(c => `• ${c.desc}: disponible ${c.disp}, solicitas ${c.cant}`)
            .join('\n');
          const ok = confirm(`⚠️ Esta salida dejaría el stock en NEGATIVO:\n\n${detalle}\n\n¿Registrar de todas formas?`);
          if (!ok) return false;
          logger.warn(`Salida con stock insuficiente (override) — Área: ${area} — ${conflictos.length} artículo(s) sobre stock`, area, 'Salida sobre stock');
        }
        const datos = {
          id: 'sal-' + Date.now(), area, motivo,
          responsable: responsable || '',
          articulos:   [...articulos],
          fecha:       new Date().toLocaleDateString('es-MX'),
          ts:          Date.now()
        };
        const lista = await repo.getSalidas();
        lista.unshift(datos);
        await repo.saveSalidas(lista);
        logger.info(`Salida registrada — Área: ${area} — ${datos.articulos.length} artículo(s)`, area, 'Registrar salida');
        ui.toast(`✓ Salida registrada correctamente`, 'ok');
        return true;
      },

      guardar: async () => {
        // Lee el formulario y delega en la lógica compartida; conserva el
        // comportamiento previo (reset del form + re-render del historial).
        const ok = await api.registrarSalida({
          area:        document.getElementById('sal-area')?.value,
          motivo:      document.getElementById('sal-motivo')?.value?.trim(),
          responsable: document.getElementById('sal-responsable')?.value?.trim() || '',
          articulos:   artsTemp,
        });
        if (!ok) return;
        artsTemp = [];
        api.limpiar();
        await api.render();
      },

      limpiar: () => {
        document.getElementById('sal-area').value        = '';
        document.getElementById('sal-responsable').value = '';
        document.getElementById('sal-art-nombre').value  = '';
        document.getElementById('sal-art-codigo').value  = '';
        document.getElementById('sal-art-cant').value    = '1';
        document.getElementById('sal-art-unidad').value  = '';
        document.getElementById('sal-motivo').value      = '';
        artsTemp = [];
        renderArts();
      },

      render: async () => {
        const container = document.getElementById('sal-historial');
        if (!container) return;
        const filtroArea = document.getElementById('sal-filtro-area')?.value || '';
        let lista = await repo.getSalidas();
        if (filtroArea) lista = lista.filter(s => s.area === filtroArea);
        if (!lista.length) {
          container.innerHTML = '<div class="empty" style="padding:24px;">📭 Sin salidas registradas</div>';
          return;
        }
        container.innerHTML = lista.map(s => {
          const artsHTML = (s.articulos || []).map(a =>
            `<span style="font-size:11px;background:#fff5f5;border:1px solid #fed7d7;border-radius:3px;padding:1px 6px;margin:1px;font-family:monospace;">${a.cantidad} ${a.unidad} — ${a.descripcion}</span>`
          ).join(' ');
          return `<div style="padding:12px 16px;border-bottom:1px solid #f0f4f8;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap;">
              <div>
                <span style="font-size:12px;background:#ebf4ff;color:#2b6cb0;padding:1px 8px;border-radius:10px;">${s.area}</span>
                <span style="margin-left:8px;font-size:12px;color:#718096;">${s.fecha}</span>
                ${s.responsable ? `<span style="margin-left:8px;font-size:11px;color:#a0aec0;">— ${s.responsable}</span>` : ''}
              </div>
            </div>
            <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:2px;">${artsHTML}</div>
            <div style="font-size:11px;color:#718096;margin-top:4px;"><b>Motivo:</b> ${s.motivo}</div>
          </div>`;
        }).join('');
      }
    };

    return api;
};
