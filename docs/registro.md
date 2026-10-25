# Módulo de registro — decisiones de producto

## El reto

El comercio popular de la CDMX no tiene un lugar único donde la población pueda
saber **dónde está, cuándo abre y qué ofrece**. La información está fragmentada y
la mayoría de los negocios no tiene presencia digital. El miedo a la visibilidad
(seguridad, fiscalidad) es real y no se resuelve ocultando el registro: se resuelve
con **control sobre lo que se publica**.

## Qué incluye el módulo

1. **Landing pública** con el problema, beneficios, datos del reto y FAQ.
2. **Página “Cómo funciona”** que explica qué implica registrarse, qué se necesita
   y qué no se necesita.
3. **Registro en 4 pasos** con guardado de avance en sesión:
   - Comercio: nombre, tipo, giro, descripción, antigüedad, personas, RFC opcional.
   - Ubicación y horarios: alcaldía, colonia, calle/referencia, días, horario y
     datos de tianguis.
   - Oferta: hasta 6 productos, categoría, precio, unidad, formas de pago e interés
     en punto de venta.
   - Contacto y publicación: persona de contacto, teléfono, WhatsApp, correo
     opcional, consentimiento y resumen editable.
4. **Confirmación** con folio, ficha pública, QR y siguientes pasos.
5. **Panel del comercio** con visibilidad, completitud, productos, QR y actividad.
6. **Directorio público** con búsqueda, filtros, mapa y ficha individual.
7. **Aviso de privacidad** y consentimiento explícito.

## Decisiones para reducir la fricción

- **RFC opcional** y nunca público. Se aclara que no se usa para trámites fiscales.
- **Correo opcional**; el teléfono/WhatsApp es el canal principal.
- **Ubicación granular**: se puede publicar solo colonia y referencia; la calle y
  número se usan para la ficha, pero el prototipo no geocodifica exactamente.
- **Publicación inmediata** al terminar, sin esperar validación (el reto pide
  reducir burocracia); el panel permite completar después.
- **Edición** desde el panel: el mismo wizard precarga los datos y actualiza el
  registro en lugar de crear otro.
- **Privacidad explícita**: aviso, consentimiento, campos que se publican y campos
  que no, y opción de ocultar la ficha.

## Modelo de datos

```
Comercio
  id, folio, slug, nombre, tipo, giro, descripcion,
  anios_operando, personas, rfc,
  alcaldia, colonia, calle, referencias, horario (JSON),
  dias_tianguis, numero_puesto,
  telefono, whatsapp, email, contacto_nombre,
  metodos_pago (JSON), interes_pos, como_se_entero,
  estado, visitas, lat, lng, creado_en
Producto
  id, comercio_id, nombre, categoria, precio, unidad, descripcion
```

- `folio`: `CH-AAAA-NNNN`, único.
- `slug`: `id-nombre-slug`, único y estable.
- `horario`: `{ "lunes": {"abre": true, "de": "09:00", "a": "19:00"}, ... }`.
- `estado`: `publicado` por defecto (prototipo); se puede ocultar.

## Rutas

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Landing |
| GET | `/como-funciona` | Explicación del registro |
| GET | `/aviso-de-privacidad` | Aviso |
| GET | `/registro` | Redirige al paso 1 |
| GET/POST | `/registro/paso-1..4` | Wizard |
| GET | `/registro/confirmacion/<folio>` | Confirmación + QR |
| GET | `/registro/reiniciar` | Limpia el borrador |
| GET | `/directorio` | Listado con filtros y mapa |
| GET | `/comercio/<slug>` | Ficha pública |
| GET | `/panel` | Panel del comercio |
| GET | `/panel/editar` | Precarga el wizard para editar |
| GET | `/salud` | Health check para CI/CD |

## Validación y seguridad

- CSRF por sesión en todos los POST.
- Honeypot `sitio_web` contra bots.
- Validación de teléfono (10 dígitos), correo y RFC (si se proporciona).
- Horarios validados (`HH:MM`, cierre > apertura, al menos un día).
- Cookie `Secure` en producción, `HttpOnly`, `SameSite=Lax`.
- Cabeceras de seguridad y CSP.
- Sin datos sensibles; se pide no ingresarlos.

## Limitaciones del prototipo

- No hay autenticación de comercios: el panel usa la sesión o una ficha demo.
- No hay validación documental ni integración con trámites de la alcaldía.
- La ubicación es aproximada por alcaldía; no hay geocodificación.
- El QR y los enlaces usan el dominio de despliegue.
- La base es SQLite para simplificar el hackathon; puede migrarse a PostgreSQL.

## Módulo Digitaliza (beneficio del registro)

Se inspira en la operación de **caja, ventas e inventario** del proyecto
`~/dev/merp`, rama `main`: terminal, cierre de caja, productos y reportes. **No se
implementa la pasarela de pagos ni el cobro en línea**; el objetivo es orientar y
capturar una solicitud de diagnóstico, no procesar dinero.

El módulo se presenta como un beneficio para quien ya registró su comercio:
diagnóstico sin costo, propuesta de terminal/inventario y acompañamiento. Los
proveedores externos definen comisiones y contratos; Chilangatón no retiene ventas.

La tabla `solicitudes_digitalizacion` guarda los leads del formulario. Se pueden
ver en el panel de operación (`/admin/`), junto con noticias y dispositivos push.
