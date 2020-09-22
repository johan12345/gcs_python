from functools import wraps


def debounce(wait, fig):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """

    def decorator(fn):
        @wraps(fn)
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)

            try:
                debounced.t[args].stop()
            except (KeyError, ValueError):
                pass
            timer = fig.canvas.new_timer(wait * 1000)
            timer.add_callback(call_it)
            timer.single_shot = True
            timer.start()
            debounced.t[args] = timer

        debounced.t = {}
        return debounced

    return decorator
