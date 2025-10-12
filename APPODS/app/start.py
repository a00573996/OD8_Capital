from app.main import main as launch_main

def _start():
    # Intentar usar el splash si está disponible
    try:
        from app.splash import run_splash_then
    except Exception:
        # No hay splash o falló la importación → ir directo a main
        launch_main()
        return

    # Ejecutar con firma moderna primero
    try:
        run_splash_then(launch_main)
        return
    except TypeError:
        # Compatibilidad con versiones que requieren duración
        try:
            run_splash_then(launch_main, 1800)  # argumento posicional por compatibilidad
            return
        except Exception:
            pass
    except Exception:
        pass

    # Si algo salió mal con el splash, continuar a main
    launch_main()

if __name__ == "__main__":
    _start()