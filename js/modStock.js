// ── MÓDULO STOCK ──────────────────────────────────────────────────────────
// Estado de Stock por área.
//   stock = exist. final abril (campo `e` del catálogo base)
//         + entradas registradas − salidas registradas
//
// Primer módulo extraído del HTML (roadmap-PR12: modularización).
// Patrón: factory con inyección de dependencias. Se invoca desde el IIFE
// principal con las dependencias del closure que necesita:
//   - calcularStockTeorico(area): { [key]: { entradas, salidas, ... } } por artículo
//   - AREAS_INV: configuración visual por área { icono, color, bg }
// Dependencias globales/DOM (NO se inyectan): window.CATALOGO_INVENTARIO,
// los elementos #stock-* del HTML y la API pública APP.modStock.
window.createModStock = ({ calcularStockTeorico, AREAS_INV }) => {
    let artsCache = [];

    const calcularArea = (area) => {
      const catBase = window.CATALOGO_INVENTARIO || {};
      const mov = calcularStockTeorico(area);
      const mapa = {};

      (catBase[area] || []).forEach(art => {
        const key = art.n.toLowerCase().trim();
        const m = mov[key] || { entradas: 0, salidas: 0 };
        mapa[key] = {
          codigo: art.c || '', descripcion: art.n, unidad: art.u || 'PZA',
          precio: art.p || 0, base: art.e || 0,
          entradas: m.entradas, salidas: m.salidas,
          stock: (art.e || 0) + m.entradas - m.salidas,
        };
      });

      Object.entries(mov).forEach(([key, m]) => {
        if (mapa[key]) return;
        mapa[key] = {
          codigo: m.codigo || '', descripcion: m.descripcion, unidad: m.unidad || 'PZA',
          precio: 0, base: 0,
          entradas: m.entradas, salidas: m.salidas,
          stock: m.entradas - m.salidas,
        };
      });

      return Object.values(mapa).sort((a, b) => a.descripcion.localeCompare(b.descripcion));
    };

    const renderTabla = (arts) => {
      const body = document.getElementById('stock-body');
      if (!body) return;
      if (!arts.length) {
        body.innerHTML = '<tr><td colspan="9" style="color:#a0aec0;text-align:center;padding:16px;">Sin artículos para mostrar</td></tr>';
        return;
      }
      body.innerHTML = arts.map(a => {
        const negativo = a.stock < 0;
        const stockColor = negativo ? '#c53030' : a.stock === 0 ? '#a0aec0' : '#276749';
        const valor = Math.max(0, a.stock) * a.precio;
        return `<tr style="${negativo ? 'background:#fff5f5' : ''}">
          <td style="font-size:11px;color:#718096;font-family:monospace">${a.codigo}</td>
          <td>${a.descripcion}</td>
          <td style="text-align:center">${a.unidad}</td>
          <td style="text-align:right;color:#4a5568">${a.precio > 0 ? '$'+a.precio.toLocaleString('es-MX',{minimumFractionDigits:2}) : '—'}</td>
          <td style="text-align:right;color:#718096">${a.base}</td>
          <td style="text-align:right;color:#2b6cb0;font-weight:${a.entradas > 0 ? '600':'400'}">${a.entradas > 0 ? '+'+a.entradas : a.entradas}</td>
          <td style="text-align:right;color:#c53030;font-weight:${a.salidas > 0 ? '600':'400'}">${a.salidas > 0 ? '-'+a.salidas : a.salidas}</td>
          <td style="text-align:right;font-weight:700;color:${stockColor}">${a.stock}</td>
          <td style="text-align:right">${a.precio > 0 ? '$'+valor.toLocaleString('es-MX',{minimumFractionDigits:2,maximumFractionDigits:2}) : '—'}</td>
        </tr>`;
      }).join('');
    };

    const render = () => {
      const area = (document.getElementById('stock-area')?.value || '').trim();
      const resumenEl = document.getElementById('stock-resumen');
      const tablaPanel = document.getElementById('stock-panel-tabla');

      if (!window.CATALOGO_INVENTARIO) {
        if (resumenEl) resumenEl.innerHTML = '<div class="panel" style="color:#718096;text-align:center;padding:16px;">📭 Catálogo de inventario no disponible</div>';
        if (tablaPanel) tablaPanel.style.display = 'none';
        return;
      }

      if (!area) {
        artsCache = [];
        const cards = Object.entries(AREAS_INV).map(([a, cfg]) => {
          const arts = calcularArea(a);
          const conStock = arts.filter(x => x.stock > 0).length;
          const sinStock = arts.filter(x => x.stock <= 0).length;
          const valor = arts.reduce((s, x) => s + Math.max(0, x.stock) * x.precio, 0);
          return `<div onclick="document.getElementById('stock-area').value='${a}';APP.modStock.render();"
            style="cursor:pointer;border:1px solid #e2e8f0;border-left:4px solid ${cfg.color};border-radius:8px;padding:12px;background:${cfg.bg};transition:transform .1s"
            onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">
            <div style="font-size:13px;font-weight:700;color:${cfg.color};margin-bottom:6px;">${cfg.icono} ${a}</div>
            <div style="font-size:20px;font-weight:700;color:#2d3748">${conStock}</div>
            <div style="font-size:11px;color:#718096;margin-bottom:4px;">artículos con stock</div>
            <div style="font-size:12px;font-weight:600;color:#276749;">$${valor.toLocaleString('es-MX',{minimumFractionDigits:2,maximumFractionDigits:2})}</div>
            ${sinStock > 0 ? `<div style="font-size:10px;color:#e53e3e;margin-top:2px;">⚠ ${sinStock} en cero</div>` : ''}
          </div>`;
        }).join('');
        if (resumenEl) resumenEl.innerHTML = `<div class="panel">
          <p style="font-size:11px;color:#718096;margin-bottom:10px;">Haz clic en un área para ver el detalle.</p>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;">${cards}</div>
        </div>`;
        if (tablaPanel) tablaPanel.style.display = 'none';
        return;
      }

      artsCache = calcularArea(area);
      const conStock = artsCache.filter(x => x.stock > 0).length;
      const sinStock = artsCache.filter(x => x.stock <= 0).length;
      const valor = artsCache.reduce((s, x) => s + Math.max(0, x.stock) * x.precio, 0);
      const cfg = AREAS_INV[area] || { color: '#2b6cb0' };

      if (resumenEl) resumenEl.innerHTML = `<div class="panel" style="border-left:4px solid ${cfg.color}">
        <div style="display:flex;flex-wrap:wrap;gap:20px;align-items:center;">
          <div><span style="font-size:22px;font-weight:700;color:#2d3748">${artsCache.length}</span>
               <div style="font-size:11px;color:#718096">artículos</div></div>
          <div><span style="font-size:22px;font-weight:700;color:#276749">${conStock}</span>
               <div style="font-size:11px;color:#718096">con stock</div></div>
          ${sinStock > 0 ? `<div><span style="font-size:22px;font-weight:700;color:#c53030">${sinStock}</span>
               <div style="font-size:11px;color:#718096">en cero o negativo</div></div>` : ''}
          <div><span style="font-size:18px;font-weight:700;color:#276749">$${valor.toLocaleString('es-MX',{minimumFractionDigits:2,maximumFractionDigits:2})}</span>
               <div style="font-size:11px;color:#718096">valor actual en stock</div></div>
        </div>
      </div>`;

      if (tablaPanel) tablaPanel.style.display = 'block';
      const buscar = document.getElementById('stock-buscar')?.value || '';
      filtrar(buscar);
    };

    const filtrar = (texto) => {
      if (!texto.trim()) { renderTabla(artsCache); return; }
      const t = texto.toLowerCase();
      renderTabla(artsCache.filter(a =>
        a.descripcion.toLowerCase().includes(t) || a.codigo.toLowerCase().includes(t)
      ));
    };

    return { render, filtrar };
};
