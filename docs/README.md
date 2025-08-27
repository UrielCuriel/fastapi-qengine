# Documentación de fastapi-qengine

Este sitio usa Docus (Nuxt Content) para documentar la librería. El contenido principal está en `docs/content/`.

## Desarrollo local

```bash
cd docs
npm install
npm run dev
```

## Estructura

- `content/index.md`: portada de la librería
- `content/1.getting-started/`: instalación y cómo funciona
- `content/2.backends/`: creación de backends (SQLAlchemy) y contribución
- `3.references/`: referencias API generadas por `pydoc-markdown`

Genera la referencia con:

```bash
pydoc-markdown
```

Luego sirve el sitio con `npm run dev`.
