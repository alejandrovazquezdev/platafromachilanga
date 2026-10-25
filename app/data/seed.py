"""Datos de demostración del directorio y del panel."""

from .. import db
from datetime import datetime

from ..models import Comercio, Noticia, Producto, slugify


def _horario(de="09:00", a="19:00", dias=None):
    dias = set(dias or ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"])
    return {
        dia: {"abre": dia in dias, "de": de, "a": a}
        for dia in ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    }


def seed_if_empty():
    if Comercio.query.count() > 0:
        return

    datos = [
        {
            "nombre": "Mercado de la Merced",
            "tipo": "mercado",
            "giro": "abarrotes",
            "descripcion": "Locales de abarrotes, chiles secos, especias y productos de la canasta básica en el corazón de la Merced.",
            "anios_operando": "40 años",
            "personas": 4,
            "alcaldia": "Venustiano Carranza",
            "colonia": "Centro",
            "calle": "Calle de la Merced 120, Local 18",
            "referencias": "Pasillo de chiles secos, junto a la entrada norte.",
            "horario": _horario("08:00", "18:00", ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]),
            "telefono": "55 5555 0101",
            "whatsapp": "55 5555 0101",
            "email": "merced@chilangaton.mx",
            "contacto_nombre": "Rosa Martínez",
            "metodos_pago": ["efectivo", "transferencia"],
            "interes_pos": "si",
            "visitas": 342,
            "lat": 19.4265,
            "lng": -99.1235,
            "productos": [
                ("Chile guajillo", "Chiles y especias", "$120", "kg"),
                ("Chile pasilla", "Chiles y especias", "$140", "kg"),
                ("Canasta básica", "Abarrotes", "$95", "paquete"),
            ],
        },
        {
            "nombre": "Tianguis El Salado",
            "tipo": "tianguis",
            "giro": "frutas",
            "descripcion": "Frutas y verduras de temporada directo del campo. Puesto familiar con más de 15 años en la plancha.",
            "anios_operando": "15 años",
            "personas": 3,
            "alcaldia": "Iztapalapa",
            "colonia": "El Salado",
            "calle": "Plancha 14, calle Ejido",
            "referencias": "A un costado de la iglesia del barrio.",
            "horario": _horario("07:00", "15:00", ["martes", "sabado"]),
            "dias_tianguis": "Martes y sábado",
            "numero_puesto": "P-14",
            "telefono": "55 5555 0102",
            "whatsapp": "55 5555 0102",
            "email": "elsalado@chilangaton.mx",
            "contacto_nombre": "Jorge Ramírez",
            "metodos_pago": ["efectivo", "transferencia", "pedidos"],
            "interes_pos": "si",
            "visitas": 287,
            "lat": 19.3650,
            "lng": -99.0450,
            "productos": [
                ("Jitomate saladet", "Frutas y verduras", "$28", "kg"),
                ("Aguacate hass", "Frutas y verduras", "$55", "kg"),
                ("Naranja valencia", "Frutas y verduras", "$18", "kg"),
                ("Mango ataulfo", "Frutas y verduras", "$42", "kg"),
            ],
        },
        {
            "nombre": "Abarrotes Doña Mari",
            "tipo": "tienda",
            "giro": "abarrotes",
            "descripcion": "La tienda de la esquina: abarrotes, lácteos, botanas y recargas. Pedidos a domicilio en la colonia.",
            "anios_operando": "12 años",
            "personas": 2,
            "alcaldia": "Coyoacán",
            "colonia": "Del Carmen",
            "calle": "Av. Universidad 1450, Local B",
            "referencias": "Frente al parque de la colonia, esquina con Calle 5.",
            "horario": _horario("08:30", "20:30", ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]),
            "telefono": "55 5555 0103",
            "whatsapp": "55 5555 0103",
            "email": "donamari@chilangaton.mx",
            "contacto_nombre": "María López",
            "metodos_pago": ["efectivo", "transferencia", "vales", "pedidos"],
            "interes_pos": "si",
            "visitas": 218,
            "lat": 19.3500,
            "lng": -99.1620,
            "productos": [
                ("Leche entera", "Lácteos", "$26", "litro"),
                ("Huevo blanco", "Abarrotes", "$48", "kg"),
                ("Recarga de celular", "Servicios", "$20", "recarga"),
            ],
        },
        {
            "nombre": "Tamales La Güera",
            "tipo": "local",
            "giro": "alimentos",
            "descripcion": "Tamales de guajillo, rajas y dulce; atole de temporada. Para llevar o por encargo.",
            "anios_operando": "8 años",
            "personas": 3,
            "alcaldia": "Tlalpan",
            "colonia": "Tlalpan Centro",
            "calle": "Calle Juárez 32",
            "referencias": "A media cuadra del mercado de Tlalpan.",
            "horario": _horario("06:30", "14:00"),
            "telefono": "55 5555 0104",
            "whatsapp": "55 5555 0104",
            "email": "laguera@chilangaton.mx",
            "contacto_nombre": "Guadalupe Hernández",
            "metodos_pago": ["efectivo", "transferencia", "pedidos"],
            "interes_pos": "no",
            "visitas": 176,
            "lat": 19.2900,
            "lng": -99.1800,
            "productos": [
                ("Tamal de guajillo", "Tamales", "$22", "pieza"),
                ("Tamal de rajas", "Tamales", "$22", "pieza"),
                ("Atole de arroz", "Bebidas", "$18", "vaso"),
            ],
        },
        {
            "nombre": "Artesanías Xochimilco",
            "tipo": "local",
            "giro": "artesanias",
            "descripcion": "Bordados, barro y textiles hechos por artesanas de San Andrés. Piezas únicas y encargos.",
            "anios_operando": "20 años",
            "personas": 5,
            "alcaldia": "Xochimilco",
            "colonia": "San Andrés",
            "calle": "Calle 5 de Mayo 8",
            "referencias": "Junto al embarcadero principal.",
            "horario": _horario("10:00", "18:00", ["miercoles", "jueves", "viernes", "sabado", "domingo"]),
            "telefono": "55 5555 0105",
            "whatsapp": "55 5555 0105",
            "email": "xochimilco@chilangaton.mx",
            "contacto_nombre": "Elena Flores",
            "metodos_pago": ["efectivo", "transferencia", "tarjeta"],
            "interes_pos": "ya",
            "visitas": 154,
            "lat": 19.2600,
            "lng": -99.1050,
            "productos": [
                ("Blusa bordada", "Textiles", "$480", "pieza"),
                ("Jarrón de barro", "Barro", "$320", "pieza"),
                ("Rebozo de algodón", "Textiles", "$650", "pieza"),
            ],
        },
        {
            "nombre": "Frutería El Güero",
            "tipo": "tienda",
            "giro": "frutas",
            "descripcion": "Fruta picada, jugos naturales y verdura fresca. Servicio rápido para la oficina y la casa.",
            "anios_operando": "6 años",
            "personas": 2,
            "alcaldia": "Cuauhtémoc",
            "colonia": "Doctores",
            "calle": "Dr. Lavista 88",
            "referencias": "Metro Hospital General, salida sur.",
            "horario": _horario("07:00", "19:00", ["lunes", "martes", "miercoles", "jueves", "viernes"]),
            "telefono": "55 5555 0106",
            "whatsapp": "55 5555 0106",
            "email": "elguero@chilangaton.mx",
            "contacto_nombre": "Arturo Sánchez",
            "metodos_pago": ["efectivo", "transferencia"],
            "interes_pos": "si",
            "visitas": 132,
            "lat": 19.4200,
            "lng": -99.1600,
            "productos": [
                ("Vaso de fruta", "Frutas y verduras", "$35", "vaso"),
                ("Jugo verde", "Bebidas", "$32", "vaso"),
                ("Jícama", "Frutas y verduras", "$24", "kg"),
            ],
        },
        {
            "nombre": "Ropa La Pulga",
            "tipo": "tianguis",
            "giro": "ropa",
            "descripcion": "Ropa de segunda mano seleccionada, tenis y accesorios. Nuevos lotes cada domingo.",
            "anios_operando": "9 años",
            "personas": 2,
            "alcaldia": "Iztacalco",
            "colonia": "Agrícola Oriental",
            "calle": "Plancha 22, calle Sur 16",
            "referencias": "Atrás del deportivo, junto a los puestos de antojitos.",
            "horario": _horario("08:00", "16:00", ["domingo"]),
            "dias_tianguis": "Domingo",
            "numero_puesto": "22",
            "telefono": "55 5555 0107",
            "whatsapp": "55 5555 0107",
            "email": "lapulga@chilangaton.mx",
            "contacto_nombre": "Luis Ortega",
            "metodos_pago": ["efectivo", "transferencia"],
            "interes_pos": "no",
            "visitas": 98,
            "lat": 19.3950,
            "lng": -99.0900,
            "productos": [
                ("Chamarra de mezclilla", "Ropa", "$180", "pieza"),
                ("Tenis deportivos", "Calzado", "$250", "par"),
                ("Blusa casual", "Ropa", "$90", "pieza"),
            ],
        },
        {
            "nombre": "Fonda La Esperanza",
            "tipo": "local",
            "giro": "alimentos",
            "descripcion": "Comida corrida casera, caldo del día y postres. Comedor familiar con servicio para llevar.",
            "anios_operando": "15 años",
            "personas": 4,
            "alcaldia": "Gustavo A. Madero",
            "colonia": "Nueva Atzacoalco",
            "calle": "Av. San Juan de Aragón 410",
            "referencias": "Frente a la secundaria, portón verde.",
            "horario": _horario("09:00", "17:00", ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]),
            "telefono": "55 5555 0108",
            "whatsapp": "55 5555 0108",
            "email": "esperanza@chilangaton.mx",
            "contacto_nombre": "Esperanza Ruiz",
            "metodos_pago": ["efectivo", "transferencia", "pedidos"],
            "interes_pos": "si",
            "visitas": 201,
            "lat": 19.4800,
            "lng": -99.1100,
            "productos": [
                ("Comida corrida", "Comida", "$75", "comida"),
                ("Caldo de pollo", "Comida", "$55", "plato"),
                ("Agua de horchata", "Bebidas", "$20", "vaso"),
            ],
        },
    ]

    for i, data in enumerate(datos, start=1):
        productos = data.pop("productos")
        comercio = Comercio(
            folio=f"CH-2026-{1000 + i}",
            slug=f"demo-{i}",
            estado="publicado",
            **data,
        )
        db.session.add(comercio)
        db.session.flush()
        # El slug se genera con el nombre una vez que el objeto existe.
        comercio.slug = f"{comercio.id}-{slugify(comercio.nombre)[:60]}"
        for nombre, categoria, precio, unidad in productos:
            db.session.add(
                Producto(
                    comercio_id=comercio.id,
                    nombre=nombre,
                    categoria=categoria,
                    precio=precio,
                    unidad=unidad,
                )
            )

    db.session.commit()



def seed_noticias():
    if Noticia.query.count() > 0:
        return

    noticias = [
        {
            "titulo": "Aviso de funcionamiento: revisa si tu giro lo necesita",
            "resumen": "No todos los comercios deben presentarlo, pero los de mayor afluencia sí. Te decimos dónde preguntar y qué tener a la mano.",
            "categoria": "regulacion",
            "fuente_nombre": "Gobierno de la Ciudad de México",
            "fuente_url": "https://www.cdmx.gob.mx/",
            "destacada": True,
            "creada_en": datetime(2026, 10, 22, 9, 0),
            "cuerpo": """El aviso de funcionamiento es un trámite que algunos establecimientos mercantiles deben presentar ante su alcaldía. No aplica igual para todos los giros ni para todos los tamaños de local.

Antes de gastar en gestores, pregunta en la ventanilla de tu alcaldía si tu actividad está dentro del catálogo que lo requiere. Lleva una identificación, la dirección del local y una descripción clara de lo que vendes.

Si tu comercio está en un mercado público o en un tianguis, el trámite puede tener un camino distinto. Pregunta primero en la administración del mercado o en la coordinación de tianguis.

Este contenido es informativo y de ejemplo. Confirma siempre los requisitos vigentes en la fuente oficial o en la ventanilla correspondiente.""",
        },
        {
            "titulo": "Apoyos para mercados públicos: convocatoria y requisitos",
            "resumen": "Programas de fortalecimiento para locales, equipo y digitalización. Revisa si tu mercado o tu puesto puede participar.",
            "categoria": "apoyos",
            "fuente_nombre": "SEDECO CDMX",
            "fuente_url": "https://www.sedeco.cdmx.gob.mx/",
            "destacada": True,
            "creada_en": datetime(2026, 10, 20, 10, 30),
            "cuerpo": """Los programas de apoyo a mercados públicos suelen abrirse por convocatoria y no de forma permanente. Muchas personas se enteran cuando el plazo ya cerró.

Arma una carpeta básica: identificación, comprobante de domicilio del local, datos de la persona responsable y una descripción de lo que necesitas financiar. Tenerla lista te ahorra días cuando salga la convocatoria.

Pregunta en la administración de tu mercado y revisa los canales oficiales de SEDECO. Desconfía de quien te pida dinero por “apartar” un apoyo.

Este contenido es informativo y de ejemplo; los montos, fechas y requisitos cambian en cada convocatoria.""",
        },
        {
            "titulo": "Separación de residuos: lo que conviene revisar en tianguis y mercados",
            "resumen": "Una guía práctica para organizar la basura del puesto, evitar multas y mantener limpio el pasillo.",
            "categoria": "regulacion",
            "fuente_nombre": "Secretaría del Medio Ambiente CDMX",
            "fuente_url": "https://www.sedema.cdmx.gob.mx/",
            "destacada": False,
            "creada_en": datetime(2026, 10, 18, 8, 0),
            "cuerpo": """La separación de residuos es una obligación cotidiana y también una forma de cuidar el espacio donde vendes. En tianguis y mercados, la basura acumulada ahuyenta clientes y complica la convivencia.

Separa al menos en orgánico, inorgánico reciclable y no reciclable. Usa botes o costales distintos y acuerda con tus vecinos de pasillo quién baja la basura al final de la jornada.

Si vendes alimentos preparados, revisa también el manejo de aceite usado y residuos orgánicos. Pregunta a la administración del mercado cuál es el punto de acopio más cercano.

Este contenido es informativo y de ejemplo; verifica las reglas de tu alcaldía y de tu mercado.""",
        },
        {
            "titulo": "Punto de venta: cómo cobrar con tarjeta sin complicarte",
            "resumen": "Comisiones, conectividad y propinas: lo que conviene preguntar antes de contratar una terminal.",
            "categoria": "digitalizacion",
            "fuente_nombre": "Chilangatón",
            "fuente_url": "",
            "destacada": False,
            "creada_en": datetime(2026, 10, 16, 12, 0),
            "cuerpo": """Una terminal puede ayudarte a vender más, pero no todas cuestan lo mismo. Antes de firmar, pregunta por la comisión por transacción, la renta mensual, el costo de la terminal y el tiempo en que te depositan.

Revisa si el equipo funciona con la señal de tu local. Si no tienes internet fijo, pregunta si la terminal usa chip celular y cuánto cuesta.

Empieza con lo básico: cobrar con tarjeta y consultar tus ventas. Después puedes sumar propinas, pagos a meses o facturación. No contrates un paquete grande si todavía no lo necesitas.

En Chilangatón podemos orientarte sin costo; el equipo y las comisiones los define cada proveedor.""",
        },
        {
            "titulo": "Campaña de seguridad en mercados y tianguis",
            "resumen": "Recomendaciones para proteger tu mercancía, tu dinero y a las personas que trabajan contigo.",
            "categoria": "seguridad",
            "fuente_nombre": "Gobierno de la Ciudad de México",
            "fuente_url": "https://www.cdmx.gob.mx/",
            "destacada": False,
            "creada_en": datetime(2026, 10, 14, 17, 0),
            "cuerpo": """La seguridad se construye entre todas las personas que comparten el mercado o la plancha. Acuerda horarios para guardar la mercancía y evita mover grandes cantidades de efectivo sola o solo.

Si puedes, usa un punto de venta o transferencias para reducir el efectivo en caja. Lleva un registro diario de lo que entra y lo que sale; te ayuda a detectar faltantes.

Identifica a la persona responsable de seguridad del mercado o del tianguis y guarda el número de la coordinación. Reporta los incidentes, aunque parezcan menores: los patrones se ven cuando se suman.

Este contenido es informativo y de ejemplo; no sustituye a las autoridades de seguridad.""",
        },
        {
            "titulo": "Antes de la temporada alta: actualiza tu ficha y tus precios",
            "resumen": "Una ficha completa con horarios y productos actualizados recibe más visitas y evita confusiones.",
            "categoria": "avisos",
            "fuente_nombre": "Chilangatón",
            "fuente_url": "",
            "destacada": False,
            "creada_en": datetime(2026, 10, 12, 11, 0),
            "cuerpo": """Cada temporada cambian los precios, los horarios y los productos de temporada. Tu ficha pública también debe cambiar.

Entra a tu panel y revisa tres cosas: que el horario de hoy sea correcto, que al menos tres productos tengan precio de referencia y que tu WhatsApp esté activo.

Si vas a abrir un puesto especial o ampliar horario, publícalo con unos días de anticipación. Una ficha desactualizada genera llamadas que no llevan a una venta.

Puedes editar tu ficha desde el panel cuando quieras; los cambios se reflejan en el directorio.""",
        },
    ]

    for item in noticias:
        slug = slugify(item["titulo"])
        base = slug
        i = 2
        while Noticia.query.filter_by(slug=slug).first():
            slug = f"{base}-{i}"
            i += 1
        db.session.add(Noticia(slug=slug, **item))
    db.session.commit()
