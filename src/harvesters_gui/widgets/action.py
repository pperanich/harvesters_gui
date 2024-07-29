from qtpy.QtWidgets import QAction
from harvesters._private.core.subject import Subject
from harvesters_gui.widgets.icon import Icon


class Action(QAction, Subject):
    def __init__(
        self,
        icon=None,
        title="",
        parent=None,
        checkable=False,
        action=None,
        is_enabled=None,
    ):
        super().__init__(
            Icon(icon),
            title,
            parent,
        )

        self._dialog = None
        self._observers = []
        self._action = action
        self._is_enabled = is_enabled

        self.setCheckable(checkable)

    def execute(self):
        # Execute everything it's responsible for.
        if self._action:
            self._action()

        # Update itself.
        self.update()

        # Update its observers.
        self.update_observers()

    def update(self):
        if self._is_enabled:
            self.setEnabled(self._is_enabled())
        self._update()

    def _update(self):
        pass
