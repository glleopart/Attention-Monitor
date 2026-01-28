# Guía Paso a Paso - Construcción del Proyecto

Esta guía te llevará por cada paso de la construcción del proyecto, desde cero hasta la ejecución final.

## Paso 1: Estructura de Directorios

```bash
mkdir attention-monitor
cd attention-monitor
mkdir src config tests scripts examples
```

**¿Por qué esta estructura?**
- `src/`: Código fuente principal
- `config/`: Configuración separada del código
- `tests/`: Tests unitarios
- `scripts/`: Utilidades adicionales
- `examples/`: Ejemplos de uso

---

## Paso 2: Crear requirements.txt

**Archivo**: `requirements.txt`

```txt
opencv-python==4.8.1.78
mediapipe==0.10.8
numpy==1.24.3
```

**¿Por qué estas dependencias?**
- **opencv-python**: Captura de video, geometría 3D, UI
- **mediapipe**: Detección facial rápida (30+ FPS en CPU)
- **numpy**: Cálculos matemáticos optimizados

**Instalar**:
```bash
pip install -r requirements.txt
```

---

## Paso 3: Configuración (config/settings.py)

**Archivo**: `config/settings.py`

Este archivo contiene todos los parámetros ajustables:

```python
# Umbrales de detección
ALERT_THRESHOLD = 5.0      # Segundos antes de alerta
YAW_THRESHOLD = 25.0       # Grados (izquierda-derecha)
PITCH_THRESHOLD = 20.0     # Grados (arriba-abajo)

# Suavizado temporal
SMOOTHING_WINDOW = 5       # Número de frames
MIN_CONSECUTIVE_FRAMES = 3 # Frames para confirmar cambio

# Cámara
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TARGET_FPS = 30
```

**Decisiones clave**:
- **5 segundos**: Balance entre detección rápida y evitar falsas alarmas
- **25°/20°**: Rango cómodo de visión periférica
- **5 frames**: ~167ms de suavizado (imperceptible pero efectivo)

---

## Paso 4: Detector Facial (src/face_detector.py)

### Funcionalidad Principal

1. **Inicializar MediaPipe**
```python
self.face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,  # Modo tracking (más rápido)
    max_num_faces=1,          # Solo 1 cara
    min_detection_confidence=0.5
)
```

2. **Detectar Cara**
```python
def detect_face(self, frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = self.face_mesh.process(rgb_frame)
    return (success, landmarks, rgb_frame)
```

3. **Estimar Pose de Cabeza**
```python
def estimate_head_pose(self, landmarks, frame_shape):
    # 1. Extraer 6 puntos clave 2D
    image_points = [nariz, barbilla, ojo_izq, ojo_der, boca_izq, boca_der]
    
    # 2. Modelo 3D estándar
    model_points = [(0,0,0), (0,-330,-65), ...]
    
    # 3. Resolver PnP (Perspective-n-Point)
    cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)
    
    # 4. Convertir a ángulos Euler
    return (yaw, pitch, roll)
```

**¿Por qué PnP?**
- Algoritmo estándar para convertir puntos 2D→3D
- Usado en AR, robótica, visión por computadora
- Robusto y rápido

---

## Paso 5: Tracker de Atención (src/attention_tracker.py)

### Máquina de Estados

```
┌─────────────┐                    ┌──────────────────┐
│   LOOKING   │───(gira cabeza)───→│  NOT_LOOKING     │
│ time = 0    │                    │ time += delta_t  │
└─────────────┘←──(vuelve a mirar)─└──────────────────┘
                                           │
                                    (time ≥ 5s)
                                           ↓
                                      [ALERT!]
```

### Componentes Clave

1. **Clasificación**
```python
def classify_attention(self, yaw, pitch):
    if yaw is None or pitch is None:
        return "not_looking"
    
    is_looking = (abs(yaw) < 25 and abs(pitch) < 20)
    return "looking" if is_looking else "not_looking"
```

2. **Suavizado Temporal**
```python
# Buffer de últimos N estados
self.state_buffer = deque(maxlen=5)
self.state_buffer.append(current_state)

# Voto mayoritario
looking_count = state_buffer.count("looking")
smoothed = "looking" if looking_count > 2.5 else "not_looking"
```

3. **Confirmación de Transición**
```python
# Requiere N frames consecutivos para cambiar estado
if new_state != current_state:
    consecutive_count += 1
    if consecutive_count >= 3:
        current_state = new_state
```

**¿Por qué este diseño?**
- **Buffer**: Reduce ruido de detección
- **Confirmación**: Evita cambios por frames individuales malos
- **Dos capas**: Máxima estabilidad

---

## Paso 6: UI Overlay (src/ui_overlay.py)

### Elementos Visuales

1. **Barra de Estado** (arriba)
```
┌─────────────────────────────────────┐
│ Estado: LOOKING  Tiempo: 2.3s  Conf: 0.85 │
└─────────────────────────────────────┘
```

2. **Barra de Progreso** (abajo, cuando no miras)
```
         2.3s / 5.0s
┌─────────────────────────────┐
│████████░░░░░░░░░░░░░░░░░░░░│ 46%
└─────────────────────────────┘
Verde → Amarillo → Rojo
```

3. **Alerta** (centro, pulsante)
```
┌────────────────────────────────┐
│                                │
│  ⚠️ ¡ATENCIÓN!                 │
│  No estás mirando la pantalla  │
│  Tiempo sin mirar: 7.2s        │
│                                │
└────────────────────────────────┘
```

**Animación de pulso**:
```python
alpha += 0.05 * direction
if alpha >= 1.0: direction = -1
if alpha <= 0.5: direction = 1
color = (R*alpha, G*alpha, B*alpha)
```

---

## Paso 7: Aplicación Principal (src/main.py)

### Loop Principal

```python
while running:
    # 1. Capturar frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Mirror
    
    # 2. Detectar cara
    detected, landmarks = face_detector.detect_face(frame)
    
    # 3. Estimar pose
    yaw, pitch, roll = face_detector.estimate_head_pose(landmarks, frame.shape)
    
    # 4. Actualizar tracker
    state_info = attention_tracker.update(yaw, pitch)
    
    # 5. Dibujar UI
    frame = ui_overlay.draw_status_bar(frame, state_info)
    if state_info['alert_active']:
        frame = ui_overlay.draw_alert(frame, ...)
    
    # 6. Mostrar
    cv2.imshow('Attention Monitor', frame)
    
    # 7. Manejar teclas
    key = cv2.waitKey(1)
    if key == ord('q'): break
```

**Timing del loop** (~30ms):
- Captura: 5ms
- Detección: 15ms
- Pose: 3ms
- Tracker: <1ms
- UI: 5ms
- Display: <1ms

---

## Paso 8: Tests (tests/test_basic.py)

### Tests Implementados

1. **Inicialización**
```python
def test_face_detector():
    detector = FaceDetector()
    assert detector is not None
```

2. **Clasificación**
```python
def test_classification():
    tracker = AttentionTracker()
    assert tracker.classify_attention(0, 0) == "looking"
    assert tracker.classify_attention(30, 0) == "not_looking"
```

3. **Transiciones**
```python
def test_state_transitions():
    tracker = AttentionTracker()
    for _ in range(5):
        tracker.update(30, 0)  # Mirar hacia otro lado
    assert tracker.current_state == "not_looking"
```

4. **Suavizado**
```python
def test_smoothing():
    # Estados alternantes no deberían causar flickering
    for i in range(10):
        yaw = 30 if i % 2 == 0 else 0
        tracker.update(yaw, 0)
    # Debe estabilizarse, no cambiar 10 veces
```

---

## Paso 9: Verificación

### Ejecutar Tests
```bash
python tests/test_basic.py
```

**Resultado esperado**:
```
==================================================
EJECUTANDO TESTS
==================================================

Test 1: FaceDetector initialization... ✓
Test 2: AttentionTracker initialization... ✓
Test 3: Classification logic... ✓
Test 4: State transitions... ✓
Test 5: UIOverlay... ✓
Test 6: Temporal smoothing... ✓

==================================================
✓ TODOS LOS TESTS PASARON
==================================================
```

---

## Paso 10: Ejecución

### Primera Ejecución
```bash
python src/main.py
```

**Deberías ver**:
```
Inicializando sistema...
✓ Sistema inicializado
✓ Cámara: 640x480
✓ Umbral: 5.0s

Presiona Q o ESC para salir
```

### Ventana de Video
- Estado en la parte superior
- Tu cara con landmarks verdes (si debug activo)
- Barra de progreso cuando no miras
- Alerta pulsante después de 5 segundos

---

## Paso 11: Ajustes Comunes

### Más Sensible (Gaming)
```python
# config/settings.py
ALERT_THRESHOLD = 3.0
YAW_THRESHOLD = 20.0
PITCH_THRESHOLD = 15.0
```

### Menos Sensible (Oficina)
```python
ALERT_THRESHOLD = 8.0
YAW_THRESHOLD = 30.0
PITCH_THRESHOLD = 25.0
SMOOTHING_WINDOW = 7
```

### Mejor Rendimiento
```python
CAMERA_WIDTH = 640  # Ya está al mínimo
CAMERA_HEIGHT = 480
SMOOTHING_WINDOW = 3  # Menos cálculos
```

---

## Resumen de Archivos Creados

```
attention-monitor/
├── requirements.txt           [3 líneas]
├── config/
│   └── settings.py           [~30 líneas]
├── src/
│   ├── face_detector.py      [~100 líneas]
│   ├── attention_tracker.py  [~120 líneas]
│   ├── ui_overlay.py         [~150 líneas]
│   └── main.py               [~150 líneas]
└── tests/
    └── test_basic.py         [~100 líneas]

Total: ~650 líneas de código funcional
```

---

## Conceptos Clave Aprendidos

1. **MediaPipe Face Mesh**: Detección facial moderna y rápida
2. **PnP Algorithm**: Convertir puntos 2D a pose 3D
3. **Temporal Smoothing**: Reducir ruido con ventanas deslizantes
4. **State Machine**: Gestión de estados con transiciones
5. **Real-time CV**: Pipeline de procesamiento <33ms

---

## Próximos Pasos

### Mejoras Opcionales
1. **Logging**: Guardar datos de atención en CSV
2. **Sonido**: Alertas auditivas
3. **ML**: Entrenar modelo supervisado para mejor accuracy
4. **Multi-persona**: Detectar múltiples caras
5. **Dashboard**: Web interface con estadísticas

### Integración
- Conectar con sistemas de productividad
- API REST para aplicaciones externas
- Pause automático de media
- Break reminders inteligentes

---

¡Proyecto completo! Ahora puedes modificar y extender según tus necesidades.
