# Informe del Proyecto: Driver de Caracteres y Aplicación de Usuario

## Grupo Foobar

- Juan Pablo Sanchez Busso
- Leonardo Ariel Sánchez
- Godoy Emiliano
- Cirrincione, Franco

## Introducción
Este informe detalla el desarrollo de un **Driver de Caracteres** (CDD) y una aplicación de usuario para sensar y graficar señales externas. El proyecto cumple con los requisitos establecidos en el trabajo práctico (TP), incluyendo la implementación de un driver que administra señales externas y una aplicación que permite la selección y visualización de dichas señales.

---

## Objetivos del Proyecto
1. Diseñar y construir un **Driver de Caracteres** que permita sensar dos señales externas con un período de **un segundo**.
2. Implementar una aplicación de usuario que:
   - Lea una de las señales sensadas.
   - Grafique la señal en función del tiempo.
   - Permita seleccionar cuál señal leer.
   - Realice correcciones de escala de las mediciones, si es necesario.

---

## Diagrama de Bloques del Proyecto

```mermaid
graph TD
    A[SenialesExternas] --> B[DriverCaracteres]
    B --> C[AppUsuario]
    C --> D[GraficaTiempoReal]
    C -->|Seleccion| B
```

Se genera el siguiente diagrama de bloques, como una primera aproximación a la resolución del problema. En el mismo se detallan los componentes principales de la implementación.

A continuación se detallan cada uno de los módulos presentes en el diagrama.

## Desarrollo del Driver de Caracteres

En primer lugar, tenemos el driver encargado de la generación de las señales. Este módulo de kernel simula tres tipos de señales generadas por software en el espacio del kernel. El mismo implementa el manejo de dispositivos de caracteres, temporizadores y sincronización mediante mutex.

### Funcionalidad del Driver
El driver (`foobar_sdec.c`) implementa las siguientes señales:
- **Señal cuadrada:** Alterna entre 0 y 1 con un período configurable.
- **Señal triangular:** Incrementa o decrementa su valor entre 0 y 100, alternando dirección al alcanzar los límites.
- **Señal diente de sierra:** Incrementa su valor de 0 a 100 y se reinicia al alcanzar el límite.

#### **Código Relevante**
El driver utiliza un temporizador (`timer_list`) para actualizar las señales periódicamente. A continuación, se muestra un fragmento del código que actualiza las señales:
```c
static void update_signals(struct timer_list *t) {
    mutex_lock(&signal_mutex);

    // Actualización de la señal cuadrada
    if (time_after(jiffies, last_square_jiffies + msecs_to_jiffies(SQUARE_PERIOD_MS))) {
        square_state = !square_state;
        last_square_jiffies = jiffies;
    }

    // Actualización de la señal triangular
    triangular_value += triangular_dir * TRIANGULAR_STEP;
    if (triangular_value >= 100 || triangular_value <= 0)
        triangular_dir *= -1;

    // Actualización de la señal diente de sierra
    sawtooth_value += SAWTOOTH_STEP;
    if (sawtooth_value >= 100)
        sawtooth_value = 0;

    mutex_unlock(&signal_mutex);
    mod_timer(&signal_timer, jiffies + msecs_to_jiffies(next_period));
}
```

### Capturas de Pantalla

Se adjunta a continuación la captura de pantalla de la consola de Linux, donde se muestra la carga y descarga del módulo anteriormente descrito.

![Captura de la Aplicación](capturas/carga.png)

*Figura 1: Carga y descarga del módulo.*

## Desarrollo de la Aplicación de Usuario

En segundo lugar, encontramos la aplicación encargada de la interfaz gráfica de usuario que se conecta con el CDD (driver de caracteres). La misma nos permite visualizar el funcionamiento del driver en tiempo real.

### Funcionalidad de la Aplicación
La aplicación (`gui.py`) permite:
- Seleccionar la señal a sensar mediante botones de radio.
- Graficar la señal seleccionada en tiempo real utilizando Matplotlib.
- Resetear el gráfico.
- Ajustar la escala de magnitud en los ejes de ordenadas y abscisas.

#### **Código Relevante**
La aplicación utiliza PySide6 para la interfaz gráfica y Matplotlib para la visualización de las señales. A continuación, se muestra un fragmento del código que implementa la selección de señales:

```python
def change_signal(self):
    signal = self.signal_group.checkedId()
    self.reader.write_signal(signal)
```

### Capturas de Pantalla

![Captura de Señales](capturas/waveforms.webm)

*Figura 2: Visualización de las señales en tiempo real en la aplicación de usuario.*

Dado el tamaño del video, su visualización requiere la descarga previa. Por este motivo, se incluyen capturas del mismo con el objetivo de facilitar la corrección. Cabe aclarar que en el video se puede observar el cambio de señal en tiempo real, lo cual no es apreciable en las capturas.

![Captura de señal cuadrada](capturas/cuadrada.jpg)  
*Figura 3: Visualización de la señal cuadrada en la interfaz gráfica.*

![Captura de señal triangular](capturas/triangular.jpg)  
*Figura 4: Visualización de la señal triangular en la interfaz gráfica.*

![Captura de señal diente de sierra](capturas/dientesierra.jpg)  
*Figura 5: Visualización de la señal diente de sierra en la interfaz gráfica.*

## Pruebas Realizadas

Se realizaron pruebas de carga y descarga del módulo en Linux utilizando los comandos `insmod` y `rmmod`, verificando la correcta creación del dispositivo en `/dev`. Además, se probó la aplicación gráfica seleccionando cada tipo de señal y observando la actualización en tiempo real del gráfico.

## Posibles Mejoras y Trabajos Futuros

- Agregar soporte para más tipos de señales.
- Permitir la configuración dinámica de los parámetros de las señales desde la aplicación de usuario.
- Mejorar la interfaz gráfica con más opciones de visualización.
- Implementar soporte multiplataforma.

### Conclusiones

El desarrollo del Driver de Caracteres y su correspondiente aplicación de usuario cumplió con todos los objetivos propuestos al inicio del proyecto:

- **Implementación del Driver de Caracteres:**  
  Se diseñó exitosamente un driver de tipo carácter que simula tres señales distintas (cuadrada, triangular y diente de sierra) dentro del espacio del kernel.

- **Aplicación de Usuario:**  
  Se desarrolló una interfaz gráfica utilizando PySide6, que permite al usuario seleccionar qué señal visualizar, mostrando en tiempo real su comportamiento mediante gráficos con Matplotlib.  
  La aplicación también permite ajustar escalas y reiniciar la visualización, facilitando la interpretación de las señales.

En conclusión, el trabajo logró satisfacer los objetivos técnicos y funcionales propuestos, consolidando conocimientos sobre desarrollo de drivers en Linux, comunicación con aplicaciones de usuario y visualización en tiempo real. La experiencia adquirida resulta de gran valor para proyectos futuros relacionados con sistemas embebidos y sensado de señales.

## Referencias

- Documentación oficial de Linux Device Drivers.
- Tutoriales de PySide6 y Matplotlib.
- Apuntes de la cátedra.
