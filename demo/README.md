# Demo — Lumé Cosmetics dashboard

Dashboard interactivo pensado para un equipo de marketing. Usa una
marca ficticia (**Lumé Cosmetics**, línea de skincare) y simula el
análisis de sentimiento del lanzamiento de un sérum facial durante 14
días en Facebook e Instagram.

Qué contiene:

- KPIs ejecutivos: posts, comentarios, net sentiment, % positivo, % negativo
- Distribución de sentimiento y por plataforma
- Evolución temporal del sentimiento día a día
- Engagement vs sentiment score
- Nube de palabras coloreada por sentimiento dominante
- Top keywords + tabla de top posts por engagement
- **Insights accionables**: alertas automáticas con recomendaciones
  concretas para marketing (tipo “'precio' aparece X veces con
  sentimiento negativo → considerar comunicar mejor el valor”)

Cambia de escenario con el botón **Escenario** (Lanzamiento / Crisis de
reviews / Mes orgánico) y pulsa **Regenerar** para re-rollear los datos
manteniendo el escenario.

## Detalles técnicos

- HTML/CSS/JS puro, sin build.
- Gráficos: [Plotly.js](https://plotly.com/javascript/) desde CDN.
- Nube de palabras: [wordcloud2.js](https://github.com/timdream/wordcloud2.js).
- Fuente: Inter (Google Fonts).
- Responsive: grid en 5/3/2/1 columnas según ancho. Los gráficos se
  redimensionan automáticamente y la nube se redibuja al hacer resize.

## Deploy en Vercel

Esta carpeta está pensada para desplegarse **sola**, sin tocar el
código Python del repo padre.

En [vercel.com/new](https://vercel.com/new), al importar el repo:

1. **Framework Preset**: `Other`
2. **Root Directory**: `demo` ← clave, si no Vercel intenta buildar Python
3. Build Command: vacío
4. Output Directory: vacío
5. Deploy

Vercel publica `demo/index.html` como root del sitio en ~30 segundos.

## Probar en local

```bash
cd social-sentiment-analyzer/demo
python3 -m http.server 8000
# abrir http://localhost:8000
```

O simplemente arrastra `index.html` al navegador.

## Por qué Lumé Cosmetics

Quería un caso que le cuente algo creíble a alguien de marketing:
una marca de skincare en Meta, con mezcla de buzz positivo, quejas
típicas (precio, envío, irritación) y eventos típicos (lanzamiento,
crisis de reviews). La demo no representa a ninguna empresa real.
