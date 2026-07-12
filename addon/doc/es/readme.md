# Información de Texto

Este complemento proporciona a los usuarios información contextual, adecuada para una amplia variedad de casos de uso.
Con una sola tecla, puede darte el significado de una palabra, geolocalizar una dirección IP e informarte sobre un libro (mediante ISBN). Simplemente selecciona algo, usa el atajo asignado y espera.

## Servicios compatibles

Actualmente, se admiten las siguientes funciones:

* Información sobre direcciones IP. Incluye geolocalización, ISP, identificación de nodos de salida VPN/Tor y redes móviles.
* Definiciones del diccionario en inglés, categoría gramatical, oraciones de ejemplo, sinónimos, antónimos, etc. Cortesía de la [Free Dictionary API](https://dictionaryapi.dev/). Al mostrar la definición de una palabra en un diálogo navegable, se incluyen botones para escuchar su pronunciación, cuando el audio esté disponible
* Búsquedas por ISBN a través de la API de Google Books
* Verificación del tipo de tarjeta de crédito (Mastercard, Visa, Discover, Amex, etc.)

El complemento también implementa soporte para identificar números de teléfono y direcciones de correo electrónico, aunque no se obtiene información adicional sobre ellos. Es probable que esto cambie en cuanto encuentre algo que hacer con ellos y una API sencilla que cumpla nuestras especificaciones.

Nota: Se usan expresiones regulares internamente para verificar los datos. Esto significa que las direcciones de correo electrónico y los números de tarjeta nunca abandonarán tu dispositivo.

## Atajos de teclado

Nota: Estos atajos asumen un diseño de teclado en inglés y puede que no funcionen de otra forma. Si tienes algún problema, primero intenta cambiarlos en el diálogo de gestos de entrada.

* NVDA+; (punto y coma): proporciona información basada en el texto seleccionado
* NVDA+SHIFT+; (punto y coma): proporciona información sobre el texto del portapapeles
* NVDA+control+; (punto y coma): reproduce la última información reportada. Presiona dos veces rápidamente para verla en un diálogo navegable. Para definiciones de palabras, este diálogo también incluye botones para reproducir el audio de pronunciación, cuando esté disponible. Escape cierra el diálogo.

## Nota sobre Python 3

A partir de la versión 2019.3 de NVDA, todos los complementos deben ser compatibles con Python 3. Si por alguna razón usas una versión anterior, [1.0](https://github.com/cartertemm/text_information/releases/download/1.0/textInformation-1.0.nvda-addon) es la última versión utilizable con Python 2; además, las definiciones del diccionario ya no funcionan debido a la obsolescencia de Princeton Wordnetweb. Ambas versiones deben considerarse sin soporte.

## Contribuciones

Las contribuciones son bienvenidas. Puedes enviar un PR o ponerte en contacto a través de la siguiente información:

twitter: @cartertemm

email: cartertemm (at) gmail (dot) com

## Licencia

Este paquete se distribuye bajo los términos de la Licencia Pública General de GNU, versión 2 o posterior. Consulta el archivo COPYING.txt para más detalles.
