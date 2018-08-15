# Copyright (C) 2011 Chris Dekter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import typing

if typing.TYPE_CHECKING:
    import autokey.iomediator


class Mouse:
    """
    Provides access to send mouse clicks
    """
    def __init__(self, mediator):
        self.mediator = mediator  # type: autokey.iomediator.IoMediator
        self.interface = self.mediator.interface

    def click_relative(self, x, y, button):
        """
        Send a mouse click relative to the active window

        Usage: C{mouse.click_relative(x, y, button)}

        @param x: x-coordinate in pixels, relative to upper left corner of window
        @param y: y-coordinate in pixels, relative to upper left corner of window
        @param button: mouse button to simulate (left=1, middle=2, right=3)
        """
        self.interface.send_mouse_click(x, y, button, True)

    def click_relative_self(self, x, y, button):
        """
        Send a mouse click relative to the current mouse position

        Usage: C{mouse.click_relative_self(x, y, button)}

        @param x: x-offset in pixels, relative to current mouse position
        @param y: y-offset in pixels, relative to current mouse position
        @param button: mouse button to simulate (left=1, middle=2, right=3)
        """
        self.interface.send_mouse_click_relative(x, y, button)

    def click_absolute(self, x, y, button):
        """
        Send a mouse click relative to the screen (absolute)

        Usage: C{mouse.click_absolute(x, y, button)}

        @param x: x-coordinate in pixels, relative to upper left corner of window
        @param y: y-coordinate in pixels, relative to upper left corner of window
        @param button: mouse button to simulate (left=1, middle=2, right=3)
        """
        self.interface.send_mouse_click(x, y, button, False)

    def wait_for_click(self, button, timeOut=10.0):
        """
        Wait for a mouse click

        Usage: C{mouse.wait_for_click(self, button, timeOut=10.0)}

        @param button: they mouse button click to wait for as a button number, 1-9
        @param timeOut: maximum time, in seconds, to wait for the keypress to occur
        """
        button = int(button)
        w = autokey.iomediator.Waiter(None, None, button, timeOut)
        w.wait()

    def press_mouse_buttons(self, buttons: typing.Union[int, typing.Iterable[int]]):
        """
        Press and hold the given mouse button(s). The buttons parameter accepts both a single button as an integer or
        any iterable containing multiple mouse buttons. The button(s) are pressed at the current mouse cursor position.

        Usage: C{mouse.press_mouse_buttons(1)} to press and hold the left mouse button
        Or: C{mouse.press_mouse_buttons([2, 3])} to press and hold both the middle and right mouse button

        @param buttons: Mouse button or list of mouse buttons (left=1, middle=2, right=3)
        """
        self.interface.press_mouse_buttons(buttons)

    def release_mouse_buttons(self, buttons: typing.Union[int, typing.Iterable[int]]):
        """
        Release the currently held, given mouse button(s). The buttons parameter accepts both a single button as an
        integer or any iterable containing multiple mouse buttons. The button(s) are released at the current mouse
        cursor position.

        Usage: C{mouse.release_mouse_buttons(1)} to release the (currently pressed) left mouse button
        Or: C{mouse.release_mouse_buttons([2, 3])} to to release the (currently pressed) middle and right mouse button

        @param buttons: Mouse button or list of mouse buttons (left=1, middle=2, right=3)
        """
        self.interface.release_mouse_buttons(buttons)

    def move_mouse_cursor(self, cursor_path, default_steps: int=1, default_duration_ms: float=0):
        """
        Move the mouse cursor alongside a given path.
        @param cursor_path:
        @param default_steps: Number of interpolation steps for each given movement operation. Used, if the path element
        itself does not provide this value
        @param default_duration_ms:
        :return:
        """
        pass
