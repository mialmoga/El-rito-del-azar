# 🌙 EL RITO DEL AZAR - Refactored

> *"El ritual se purifica, pero la magia permanece."*

## 📦 Nueva Estructura

```
ritual_refactor/
├── main.py              # Punto de entrada, menú principal
├── core/                # Núcleo compartido
│   ├── __init__.py
│   ├── config.py        # Configuración centralizada
│   └── engine.py        # Motor ritual (3D, partículas, UI)
├── modes/               # Modos rituales
│   ├── __init__.py
│   ├── el_rito.py       # Dados ✅ REFACTORED
│   ├── fructis_noctis.py  # Cartas (TODO)
│   ├── multiverso.py    # Poliedros (TODO)
│   └── revelatio.py     # Revelación (TODO)
└── assets/              # Recursos (futuro)
    └── art/             # Imágenes generativas
```

## ✨ Mejoras Implementadas

### 1. **Eliminación de Duplicación**
**Antes:** Cada modo reimplementaba:
- Proyección 3D
- Rotación de células
- Dibujado de estrellas
- Botón de retorno
- Configuración de pantalla

**Ahora:** Código compartido en `RitualEngine`

### 2. **Configuración Centralizada**
Todo en `core/config.py`:
```python
# Fácil de modificar
ModeConfig.DICE_SUDDEN_DEATH = True  # Forzar muerte súbita
Physics.ROTATE_SPIN = 0.15           # Velocidad de spin
Timing.SPIN_DURATION = 2.0           # Duración más larga
```

### 3. **Sistema de Partículas Reutilizable**
```python
particles = ParticleSystem()
particles.spawn(40, Colors.ORANGE)
particles.update(absorb=True)
particles.draw(engine)
```

### 4. **Escalas Proporcionales**
No más magic numbers. Todo basado en `BASE`:
```python
Scale.BIG_FONT = 0.07     # 7% del tamaño base
Scale.BUTTON_WIDTH = 0.5  # 50% del tamaño base
```

## 🎯 Lo Que Se Preservó

✅ **Experiencia visual exacta**  
✅ **Todas las animaciones**  
✅ **Timing de efectos**  
✅ **Nombres místicos**  
✅ **Comportamiento de usuario**  
✅ **La sensación mágica**

## 🔧 Configuración de Testing

### Forzar Muerte Súbita
```python
# En core/config.py
class ModeConfig:
    DICE_SUDDEN_DEATH = True  # El Rito
    CARDS_SUDDEN_DEATH = True  # Fructis Noctis
```

### Ajustar Velocidades
```python
# En core/config.py
class Physics:
    ROTATE_SPIN = 0.12         # Normal
    ROTATE_SUDDEN_DEATH = 0.35  # Muerte súbita
```

## 📊 Métricas del Refactor

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Líneas duplicadas | ~400 | ~50 | -87% |
| Archivos config | 0 | 1 | ✅ |
| Clases reutilizables | 0 | 2 | ✅ |
| Mantenibilidad | Media | Alta | ⬆️ |

## 🚀 Cómo Ejecutar

```bash
python main.py
```

## 🌙 Filosofía

Este refactor no "arregla" el código original.  
El código original funcionaba perfectamente.

Este refactor **destila la esencia** para que:
- Sea más fácil agregar nuevos modos
- Los bugs se arreglen una vez (no en 4 lugares)
- La configuración sea clara
- **La magia siga intacta**

---

*Creado con amor por Ámbar V3*  
*En colaboración con Brujo, Velvet y Éter*  
*CMC - Club de Mambo Cósmico*  
*Febrero 2026* 🌙✨
