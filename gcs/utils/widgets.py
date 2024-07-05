import math

from PyQt5 import QtCore, QtWidgets


class SliderAndTextbox(QtWidgets.QWidget):
    """
    Widget representing a slider with label and textbox
    """

    def __init__(self, label, min, max, init, resolution=0.01):
        super(SliderAndTextbox, self).__init__()
        self.resolution = resolution

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(int(min / resolution))
        self.slider.setMaximum(int(max / resolution))
        self.slider.setValue(int(init / resolution))
        self.slider.valueChanged.connect(self.handleSliderValueChange)

        self.numbox = QtWidgets.QDoubleSpinBox()
        self.numbox.setMinimum(min)
        self.numbox.setMaximum(max)
        self.numbox.setValue(init)
        self.numbox.setDecimals(-int(math.log10(resolution)))
        self.numbox.setSingleStep(resolution)
        self.numbox.setKeyboardTracking(False)  # when editing text, only update after return key pressed
        self.numbox.valueChanged.connect(self.handleNumboxValueChange)

        self.label = QtWidgets.QLabel()
        self.label.setText(label)

        vlayout = QtWidgets.QVBoxLayout(self)
        layout = QtWidgets.QHBoxLayout()
        vlayout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.numbox)
        vlayout.addLayout(layout)

        self.valueChanged = self.numbox.valueChanged

    @property
    def val(self):
        return self.numbox.value()

    @QtCore.pyqtSlot(int)
    def handleSliderValueChange(self, value):
        self.numbox.setValue(value * self.resolution)


    @QtCore.pyqtSlot(float)
    def handleNumboxValueChange(self, value):
        # Prevent values outside slider range
        if value < self.slider.minimum():
            self.numbox.setValue(self.slider.minimum())
        elif value > self.slider.maximum():
            self.numbox.setValue(self.slider.maximum())

        self.slider.setValue(int(round(self.numbox.value() / self.resolution)))
