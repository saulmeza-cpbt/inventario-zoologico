// ── MÓDULO RESPALDO Y MIGRACIÓN ─────────────────────────────
// Exportar/importar todos los datos del usuario (localStorage) a un archivo JSON.
// Motivación: el localStorage está particionado por ORIGEN, así que los datos
// capturados en http://localhost no aparecen en https://*.github.io y viceversa.
// Esta herramienta permite respaldar y mover datos entre ambientes.
//
// Patrón factory con inyección de dependencias (igual que modStock/modSalidas).
// Dependencias inyectadas desde el IIFE principal:
//   - ui: { toast(msg, tipo) } para notificaciones
//   - logger: { info(msg, entidad, accion) } para la bitácora
//   - refrescarTodo(): recarga Entradas a memoria y re-renderiza todas las vistas
// Estrategia de importación: REEMPLAZAR las 5 claves conocidas + respaldo de
// seguridad automático del estado actual antes de sobrescribir. SIN merge.
window.createModRespaldo = ({ ui, logger, refrescarTodo }) => {
    // Registro canónico de claves de localStorage (con los acentos EXACTOS).
    const CLAVES = {
      'zoo_tamatán_entradas_v3':       'entradas',
      'zoo_tamatán_salidas_v1':        'salidas',
      'zoo_tamatán_solicitudes_v1':    'solicitudes',
      'zoo_tamatán_levantamientos_v1': 'levantamientos',
      'zoo_tamatán_bitacora_v3':       'bitacora',
    };
    // Aliases de códigos de barras: su valor es un OBJETO mapa (barcode→{codigo,area,...}),
    // NO un array → se respalda aparte del loop de CLAVES.
    const CLAVE_CODIGOS_BARRAS = 'zoo_tamatán_codigos_barras_v1';

    const leerClave = (k) => {
      try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch { return []; }
    };
    const leerMapa = (k) => {
      try { return JSON.parse(localStorage.getItem(k) || '{}'); } catch { return {}; }
    };

    // Sello de tiempo para nombres de archivo: AAAA-MM-DD_HHMM
    const sello = () => {
      const d = new Date();
      const p = (n) => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}`;
    };

    const construirPayload = () => {
      const datos = {};
      const conteos = {};
      Object.keys(CLAVES).forEach(k => {
        const arr = leerClave(k);
        datos[k] = arr;
        conteos[CLAVES[k]] = Array.isArray(arr) ? arr.length : 0;
      });
      // Aliases de códigos de barras (objeto-mapa, no array).
      const aliases = leerMapa(CLAVE_CODIGOS_BARRAS);
      datos[CLAVE_CODIGOS_BARRAS] = aliases;
      conteos.codigosBarras = Object.keys(aliases).length;
      return {
        _meta: {
          app: 'zoo-tamatan-inventario',
          version: 'v3.0',
          exportadoEn: new Date().toISOString(),
          origen: location.origin,
          conteos,
        },
        datos,
      };
    };

    const descargar = (texto, nombre) => {
      const blob = new Blob([texto], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = nombre;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    };

    const exportarComo = (nombre) => {
      const payload = construirPayload();
      descargar(JSON.stringify(payload, null, 2), nombre);
      return payload._meta.conteos;
    };

    return {
      exportar: () => {
        const conteos = exportarComo(`respaldo_zoo_inventario_${sello()}.json`);
        const total = Object.values(conteos).reduce((s, n) => s + n, 0);
        logger.info(`Respaldo exportado (${total} registros)`, 'Respaldo', 'Exportar JSON');
        ui.toast('✓ Respaldo exportado', 'ok');
      },

      importar: (file) => {
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
          let obj;
          try { obj = JSON.parse(reader.result); }
          catch { ui.toast('❌ El archivo no es un JSON válido', 'err'); return; }

          // Validación de estructura: debe existir el bloque "datos".
          if (!obj || typeof obj !== 'object' || !obj.datos || typeof obj.datos !== 'object') {
            ui.toast('❌ Estructura inválida: falta el bloque "datos"', 'err');
            return;
          }

          // Solo se consideran claves CONOCIDAS que sean arrays; el resto se ignora.
          const aImportar = {};
          const resumen = [];
          Object.keys(CLAVES).forEach(k => {
            if (Array.isArray(obj.datos[k])) {
              aImportar[k] = obj.datos[k];
              resumen.push(`  • ${CLAVES[k]}: ${obj.datos[k].length}`);
            }
          });
          // Aliases de códigos de barras: objeto plano (no array, no null).
          const aliasObj = obj.datos[CLAVE_CODIGOS_BARRAS];
          const hayAlias = aliasObj && typeof aliasObj === 'object' && !Array.isArray(aliasObj);
          if (hayAlias) resumen.push(`  • códigos de barras: ${Object.keys(aliasObj).length}`);

          if (!Object.keys(aImportar).length && !hayAlias) {
            ui.toast('❌ El respaldo no contiene datos reconocibles', 'err');
            return;
          }

          const origen = (obj._meta && obj._meta.origen) || 'desconocido';
          const fecha  = (obj._meta && obj._meta.exportadoEn) || 'desconocida';
          const msg = 'Vas a REEMPLAZAR los datos actuales con este respaldo.\n\n'
            + 'Origen del respaldo: ' + origen + '\n'
            + 'Fecha: ' + fecha + '\n\n'
            + 'Se importará:\n' + resumen.join('\n') + '\n\n'
            + 'Antes se descargará un respaldo de seguridad del estado actual.\n\n¿Continuar?';
          if (!confirm(msg)) return;

          // Red de seguridad: respaldar el estado ACTUAL antes de sobrescribir.
          exportarComo(`respaldo_seguridad_${sello()}.json`);

          // Reemplazo total de las claves conocidas presentes en el archivo.
          Object.entries(aImportar).forEach(([k, v]) => {
            try { localStorage.setItem(k, JSON.stringify(v)); } catch {}
          });
          // Aliases de códigos de barras (objeto-mapa): persistir y reflejar EN VIVO en el
          // global que lee modScanner, para que queden activos sin recargar (§3.2e).
          if (hayAlias) {
            try { localStorage.setItem(CLAVE_CODIGOS_BARRAS, JSON.stringify(aliasObj)); } catch {}
            window.CATALOGO_CODIGOS_BARRAS = Object.assign(window.CATALOGO_CODIGOS_BARRAS || {}, aliasObj);
          }

          logger.info(`Datos importados desde respaldo (origen: ${origen})`, 'Respaldo', 'Importar JSON');
          refrescarTodo();
          ui.toast(`✓ Respaldo importado (${resumen.length} colecciones)`, 'ok');
        };
        reader.onerror = () => ui.toast('❌ No se pudo leer el archivo', 'err');
        reader.readAsText(file);
      },
    };
};
