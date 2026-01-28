# Instrucciones para Subir a GitHub

## Pasos para Publicar el Proyecto

### 1. Preparación Local

```bash
# Navega al directorio del proyecto
cd attention-monitor

# Inicializa repositorio git
git init

# Añade todos los archivos
git add .

# Primer commit
git commit -m "Initial commit: Real-time attention monitoring system"
```

### 2. Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. **Repository name**: `attention-monitor`
3. **Description**: "Real-time computer vision system for attention detection using webcam"
4. **Visibility**: Public o Private (tu elección)
5. **NO marques**: Initialize with README (ya lo tienes)
6. Click "Create repository"

### 3. Conectar y Subir

```bash
# Conecta tu repositorio local con GitHub
git remote add origin https://github.com/TU-USUARIO/attention-monitor.git

# Sube el código
git branch -M main
git push -u origin main
```

### 4. Configurar README Badges (Opcional)

Añade al inicio de `README.md`:

```markdown
# Real-Time Attention Monitoring System

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.8+-green.svg)
![MediaPipe](https://img.shields.io/badge/mediapipe-0.10-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

... (resto del README)
```

### 5. Añadir LICENSE

Crea archivo `LICENSE` con contenido MIT:

```
MIT License

Copyright (c) 2025 [Tu Nombre]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Luego:
```bash
git add LICENSE
git commit -m "Add MIT license"
git push
```

### 6. Añadir Topics en GitHub

En tu repositorio GitHub:
1. Click en el icono de configuración (⚙️) junto a "About"
2. Añade topics: `computer-vision`, `opencv`, `mediapipe`, `python`, `attention-detection`, `face-detection`, `real-time`

### 7. Crear Release (Opcional)

```bash
# Tag la versión
git tag -a v1.0.0 -m "Release v1.0.0: Initial stable version"
git push origin v1.0.0
```

Luego en GitHub:
1. Ve a "Releases" → "Create a new release"
2. Choose tag: `v1.0.0`
3. Release title: `v1.0.0 - Initial Release`
4. Description:
```markdown
## Features
- Real-time attention detection using webcam
- Head pose estimation with MediaPipe
- Temporal smoothing to reduce false positives
- Customizable alert thresholds
- Statistics tracking and visualization
- Comprehensive documentation

## Installation
```bash
pip install -r requirements.txt
```

## Quick Start
```bash
python src/main.py
```

See [README.md](README.md) for full documentation.
```

### 8. Estructura Final en GitHub

Tu repositorio se verá así:

```
attention-monitor/
├── README.md               ← Documentación principal (se muestra en portada)
├── QUICK_START.md         ← Visible como archivo
├── ARCHITECTURE.md        ← Visible como archivo
├── LICENSE                ← Muestra en sidebar
├── requirements.txt       ← Mostrado en sidebar
├── .gitignore
├── config/
├── src/
├── tests/
├── scripts/
└── examples/
```

### 9. README Preview

GitHub renderizará automáticamente `README.md` en la página principal del repo con:
- Tabla de contenidos
- Enlaces internos
- Bloques de código con syntax highlighting
- Tablas formateadas
- Badges

### 10. Habilitar GitHub Pages (Opcional)

Si quieres documentación web:

1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: main, folder: /docs
4. Crear `docs/index.md` con contenido del README

### 11. Comandos Git Útiles

```bash
# Ver estado
git status

# Ver cambios
git diff

# Añadir cambios específicos
git add src/main.py

# Commit con mensaje
git commit -m "Fix: bug description"

# Subir cambios
git push

# Ver historial
git log --oneline

# Crear branch para feature
git checkout -b feature/nueva-funcionalidad

# Volver a main
git checkout main

# Merge feature
git merge feature/nueva-funcionalidad
```

### 12. .github Workflows (CI/CD Opcional)

Crear `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python tests/test_basic.py
```

### 13. GitHub Issues Templates

Crear `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**System (please complete):**
 - OS: [e.g. Windows 10]
 - Python version: [e.g. 3.8]
 - Webcam: [e.g. built-in, external USB]

**Additional context**
Any other context about the problem.
```

### 14. CONTRIBUTING.md (Opcional)

```markdown
# Contributing to Attention Monitor

## How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Coding Standards

- Follow PEP 8 style guide
- Add docstrings to functions
- Write tests for new features
- Update documentation

## Testing

```bash
python tests/test_basic.py
```

## Questions?

Open an issue for discussion.
```

### 15. Promoción del Proyecto

Una vez publicado:

1. **Twitter/X**: Tweetea sobre el proyecto con hashtags
2. **Reddit**: Comparte en r/computervision, r/Python
3. **Hacker News**: Submit si tiene tracción
4. **LinkedIn**: Post sobre el proyecto
5. **Dev.to**: Escribe artículo técnico

### 16. Mantenimiento

```bash
# Pull últimos cambios antes de trabajar
git pull

# Mantén dependencies actualizadas
pip list --outdated

# Actualiza README con nuevas features
git add README.md
git commit -m "docs: update README with new features"
git push
```

---

## Checklist Final Antes de Publicar

- [ ] README.md completo y actualizado
- [ ] LICENSE añadido
- [ ] requirements.txt verificado
- [ ] Tests pasando
- [ ] .gitignore configurado
- [ ] Commits descriptivos
- [ ] Remote origin configurado
- [ ] Código comentado
- [ ] Documentación clara
- [ ] Badges añadidos (opcional)

---

## Comandos Completos

```bash
# Setup inicial
cd attention-monitor
git init
git add .
git commit -m "Initial commit: Real-time attention monitoring system"

# Conectar con GitHub
git remote add origin https://github.com/TU-USUARIO/attention-monitor.git
git branch -M main
git push -u origin main

# Añadir license
# (crear archivo LICENSE)
git add LICENSE
git commit -m "Add MIT license"
git push

# Tag release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

¡Listo! Tu proyecto estará visible en:
`https://github.com/TU-USUARIO/attention-monitor`
