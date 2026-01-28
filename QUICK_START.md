# Quick Start Guide

## Instalación rápida (3 minutos)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/attention-monitor.git
cd attention-monitor

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar tests
python tests/test_basic.py

# 5. ¡Ejecutar el sistema!
python src/main.py
```

## Uso básico

### Comando básico
```bash
python src/main.py
```

### Con opciones personalizadas
```bash
# Cambiar umbral de alerta a 3 segundos
python src/main.py --alert-threshold 3.0

# Usar cámara externa (índice 1)
python src/main.py --camera 1

# Sin estadísticas en pantalla
python src/main.py --no-stats

# Sin información de debug
python src/main.py --no-debug
```

## Controles durante ejecución

| Tecla | Acción |
|-------|--------|
| **Q** o **ESC** | Salir del programa |
| **R** | Resetear contador de tiempo |
| **S** | Mostrar/ocultar estadísticas |
| **D** | Mostrar/ocultar información de debug |

## Ajustar parámetros

Edita `config/settings.py` para cambiar:

```python
# Tiempo antes de alerta (segundos)
ALERT_THRESHOLD = 5.0

# Tolerancia de rotación horizontal (grados)
YAW_THRESHOLD = 25.0

# Tolerancia de rotación vertical (grados)
PITCH_THRESHOLD = 20.0

# Suavizado temporal (número de frames)
SMOOTHING_WINDOW = 5
```

### Guía de ajuste según tu caso de uso:

**Para trabajo de oficina (menos sensible):**
```python
ALERT_THRESHOLD = 8.0
YAW_THRESHOLD = 30.0
PITCH_THRESHOLD = 25.0
```

**Para gaming/streaming (más sensible):**
```python
ALERT_THRESHOLD = 3.0
YAW_THRESHOLD = 20.0
PITCH_THRESHOLD = 15.0
```

**Para estudios (balance):**
```python
ALERT_THRESHOLD = 5.0
YAW_THRESHOLD = 25.0
PITCH_THRESHOLD = 20.0
```

## Interpretación de la pantalla

### Barra superior (Status Bar)
- **Estado**: Muestra si estás mirando ("LOOKING") o no ("NOT_LOOKING")
- **Tiempo**: Segundos acumulados sin mirar
- **Conf**: Confianza de la detección (0.0-1.0)

### Barra de progreso (cuando no miras)
- Verde: <50% del umbral
- Amarillo: 50-80% del umbral
- Rojo: >80% del umbral

### Alerta (cuando excedes el umbral)
- Aparece mensaje central en rojo pulsante
- Contador de tiempo sin mirar
- Se oculta inmediatamente al volver a mirar

### Estadísticas (esquina inferior derecha)
- FPS actual
- Total de frames procesados
- Ratio de atención
- Frames mirando vs no mirando

### Información de debug (esquina superior izquierda)
- Yaw: Rotación horizontal (-izquierda, +derecha)
- Pitch: Rotación vertical (-abajo, +arriba)
- Roll: Rotación lateral
- EAR: Eye Aspect Ratio (si está habilitado)

## Solución de problemas comunes

### La cámara no se detecta
```bash
# Prueba diferentes índices
python src/main.py --camera 0
python src/main.py --camera 1
python src/main.py --camera 2

# Lista todas las cámaras disponibles (Linux)
v4l2-ctl --list-devices

# Windows: abre la aplicación de cámara para verificar
```

### FPS muy bajo
1. Reduce resolución en `config/settings.py`:
   ```python
   CAMERA_WIDTH = 640
   CAMERA_HEIGHT = 480
   ```

2. Aumenta ventana de suavizado (menos cálculos):
   ```python
   SMOOTHING_WINDOW = 10
   ```

3. Cierra aplicaciones pesadas en segundo plano

### Demasiadas falsas alarmas
1. Aumenta umbrales:
   ```python
   YAW_THRESHOLD = 30.0
   PITCH_THRESHOLD = 25.0
   ```

2. Aumenta tiempo de alerta:
   ```python
   ALERT_THRESHOLD = 7.0
   ```

3. Aumenta suavizado:
   ```python
   SMOOTHING_WINDOW = 7
   ```

### No detecta cuando miro hacia otro lado
1. Reduce umbrales:
   ```python
   YAW_THRESHOLD = 20.0
   PITCH_THRESHOLD = 15.0
   ```

2. Reduce suavizado:
   ```python
   SMOOTHING_WINDOW = 3
   ```

## Casos de uso reales

### 1. Productividad en home office
Detecta distracciones durante trabajo remoto.
```bash
python src/main.py --alert-threshold 10.0
```

### 2. Estudios y lectura
Mantén concentración durante sesiones de estudio.
```bash
python src/main.py --alert-threshold 5.0
```

### 3. Gaming/Streaming
Asegura que mantienes atención en pantalla durante stream.
```bash
python src/main.py --alert-threshold 3.0 --no-stats
```

### 4. Pruebas de UI/UX
Registra cuando usuarios miran hacia otro lado durante tests.
```bash
# TODO: Implementar modo de grabación de logs
```

## Siguientes pasos

### Upgrade a Machine Learning
Para mejorar precisión con modelo supervisado, lee:
- `docs/ML_UPGRADE.md` (por crear)
- Ejecuta `python scripts/train_model.py --help`

### Integración con otras aplicaciones
El sistema puede integrarse con:
- Sistemas de time tracking
- Aplicaciones de productividad
- Software de videoconferencia
- Herramientas de gamificación

### Personalización avanzada
- Añadir alertas por sonido
- Integración con webhooks
- Logging a base de datos
- Dashboard web en tiempo real

## Recursos adicionales

- [MediaPipe Face Mesh Documentation](https://google.github.io/mediapipe/solutions/face_mesh.html)
- [Head Pose Estimation Tutorial](https://learnopencv.com/head-pose-estimation-using-opencv-and-dlib/)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

## Contribuir

Pull requests son bienvenidos. Para cambios mayores:
1. Abre un issue primero para discutir
2. Sigue las convenciones de código del proyecto
3. Añade tests para nueva funcionalidad
4. Actualiza documentación correspondiente
