seo:
  title: fastapi-qengine – Motor de consultas para FastAPI
  description: Construye consultas complejas desde la URL con una sintaxis flexible inspirada en Loopback 4. Integración mínima con FastAPI y Beanie.
---

::u-page-hero
#title
fastapi-qengine

#description
Motor de consultas para FastAPI inspirado en Loopback 4. Construye filtros complejos desde la URL con mínima integración.

#links
  :::u-button
  ---
  color: neutral
  size: xl
  to: /1.getting-started/installation
  trailing-icon: i-lucide-arrow-right
  ---
  Empezar
  :::

  :::u-button
  ---
  color: neutral
  icon: simple-icons-github
  size: xl
  to: https://github.com/tuusuario/fastapi-qengine
  variant: outline
  ---
  GitHub
  :::
::

::u-page-section
#title
Características clave

#features
  :::u-page-feature
  ---
  icon: i-lucide-filter
  ---
  #title
  Sintaxis de filtro flexible
  
  #description
  Soporta JSON en string y parámetros anidados en la URL.
  :::

  :::u-page-feature
  ---
  icon: i-lucide-git-branch
  ---
  #title
  Operadores avanzados
  
  #description
  `$gt`, `$gte`, `$in`, `$or`, `$and`, proyección y orden.
  :::

  :::u-page-feature
  ---
  icon: i-lucide-cog
  ---
  #title
  Integración mínima
  
  #description
  Úsalo como dependencia de FastAPI con Beanie/PyMongo.
  :::
::
