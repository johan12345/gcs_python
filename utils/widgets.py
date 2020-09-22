from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec, SubplotSpec
from matplotlib.widgets import Slider, TextBox


class SliderAndTextbox:
    def __init__(self, fig: Figure, gs: SubplotSpec, label, min, max, valinit):
        grid = gs.subgridspec(2, 1)
        self._slider = Slider(fig.add_subplot(grid[0, 0]), label, min, max, valinit)
        self._textbox = TextBox(fig.add_subplot(grid[1, 0]), '', valinit)

        slider_cid = None
        textbox_cid = None

        def update_textbox(*_):
            nonlocal textbox_cid

            self._textbox.disconnect(textbox_cid)
            self._textbox.set_val('{:.2f}'.format(self._slider.val))
            textbox_cid = self._textbox.on_submit(update_slider)

        def update_slider(*_):
            nonlocal slider_cid

            try:
                value = float(self._textbox.text)

                self._slider.disconnect(slider_cid)
                self._slider.set_val(value)
                slider_cid = self._slider.on_changed(update_textbox)
            except ValueError:

                pass

        slider_cid = self._slider.on_changed(update_textbox)
        textbox_cid = self._textbox.on_submit(update_slider)

    @property
    def val(self):
        return self._slider.val

    def on_changed(self, callback):
        self._slider.on_changed(callback)