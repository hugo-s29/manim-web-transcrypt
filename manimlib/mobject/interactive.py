# import numpy as np
# from pyglet.window import key as PygletWindowKeys

from manimlib.constants import FRAME_HEIGHT, FRAME_WIDTH
from manimlib.constants import LEFT, RIGHT, UP, DOWN, ORIGIN
from manimlib.constants import SMALL_BUFF, MED_SMALL_BUFF, MED_LARGE_BUFF
from manimlib.constants import BLACK, GREY_A, GREY_C, RED, GREEN, BLUE, WHITE
from manimlib.mobject.mobject import Mobject, Group
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.geometry import Dot, Line, Square, Rectangle, RoundedRectangle, Circle
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.value_tracker import ValueTracker
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import get_norm, get_closest_point_on_line
from manimlib.utils.color import rgb_to_color, color_to_rgba, rgb_to_hex


# Interactive Mobjects

class MotionMobject(Mobject):
    """
        You could hold and drag this object to any position
    """

    def __init__(self, mobject, **kwargs):
        super().__init__(**kwargs)
        assert(isinstance(mobject, Mobject))
        self.mobject = mobject
        self.mobject.add_mouse_drag_listner(self.mob_on_mouse_drag)
        # To avoid locking it as static mobject
        self.mobject.add_updater(lambda mob: None)
        self.add(mobject)

    def mob_on_mouse_drag(self, mob, event_data):
        mob.move_to(event_data["point"])
        return False


class Button(Mobject):
    """
        Pass any mobject and register an on_click method

        The on_click method takes mobject as argument like updater
    """

    def __init__(self, mobject, on_click, **kwargs):
        super().__init__(**kwargs)
        assert(isinstance(mobject, Mobject))
        self.on_click = on_click
        self.mobject = mobject
        self.mobject.add_mouse_press_listner(self.mob_on_mouse_press)
        self.add(self.mobject)

    def mob_on_mouse_press(self, mob, event_data):
        self.on_click(mob)
        return False


# Controls

class ControlMobject(ValueTracker):
    def __init__(self, value, *mobjects, **kwargs):
        super().__init__(value=value, **kwargs)
        self.add(*mobjects)

        # To avoid lock_static_mobject_data while waiting in scene
        self.add_updater(lambda mob: None)
        self.fix_in_frame()

    def set_value(self, value):
        self.assert_value(value)
        self.set_value_anim(value)
        return ValueTracker.set_value(self, value)

    def assert_value(self, value):
        # To be implemented in subclasses
        pass

    def set_value_anim(self, value):
        # To be implemented in subclasses
        pass


class EnableDisableButton(ControlMobject):
    CONFIG = {
        "value_type": np.dtype(bool),
        "rect_kwargs": {
            "width": 0.5,
            "height": 0.5,
            "fill_opacity": 1.0
        },
        "enable_color": GREEN,
        "disable_color": RED
    }

    def __init__(self, value=True, **kwargs):
        digest_config(self, kwargs)
        self.box = Rectangle(**self.rect_kwargs)
        super().__init__(value, self.box, **kwargs)
        self.add_mouse_press_listner(self.on_mouse_press)

    def assert_value(self, value):
        assert(isinstance(value, bool))

    def set_value_anim(self, value):
        if value:
            self.box.set_fill(self.enable_color)
        else:
            self.box.set_fill(self.disable_color)

    def toggle_value(self):
        super().set_value(not self.get_value())

    def on_mouse_press(self, mob, event_data):
        mob.toggle_value()
        return False


class Checkbox(ControlMobject):
    CONFIG = {
        "value_type": np.dtype(bool),
        "rect_kwargs": {
            "width": 0.5,
            "height": 0.5,
            "fill_opacity": 0.0
        },

        "checkmark_kwargs": {
            "stroke_color": GREEN,
            "stroke_width": 6,
        },
        "cross_kwargs": {
            "stroke_color": RED,
            "stroke_width": 6,
        },
        "box_content_buff": SMALL_BUFF
    }

    def __init__(self, value=True, **kwargs):
        digest_config(self, kwargs)
        self.box = Rectangle(**self.rect_kwargs)
        self.box_content = self.get_checkmark() if value else self.get_cross()
        super().__init__(value, self.box, self.box_content, **kwargs)
        self.add_mouse_press_listner(self.on_mouse_press)

    def assert_value(self, value):
        assert(isinstance(value, bool))

    def toggle_value(self):
        super().set_value(not self.get_value())

    def set_value_anim(self, value):
        if value:
            self.box_content.become(self.get_checkmark())
        else:
            self.box_content.become(self.get_cross())

    def on_mouse_press(self, mob, event_data):
        mob.toggle_value()
        return False

    # Helper methods

    def get_checkmark(self):
        checkmark = VGroup(
            Line(UP / 2 + 2 * LEFT, DOWN + LEFT, **self.checkmark_kwargs),
            Line(DOWN + LEFT, UP + RIGHT, **self.checkmark_kwargs)
        )

        checkmark.stretch_to_fit_width(self.box.get_width())
        checkmark.stretch_to_fit_height(self.box.get_height())
        checkmark.scale(0.5)
        checkmark.move_to(self.box)
        return checkmark

    def get_cross(self):
        cross = VGroup(
            Line(UP + LEFT, DOWN + RIGHT, **self.cross_kwargs),
            Line(UP + RIGHT, DOWN + LEFT, **self.cross_kwargs)
        )

        cross.stretch_to_fit_width(self.box.get_width())
        cross.stretch_to_fit_height(self.box.get_height())
        cross.scale(0.5)
        cross.move_to(self.box)
        return cross


class LinearNumberSlider(ControlMobject):
    CONFIG = {
        "value_type": np.float64,
        "min_value": -10.0,
        "max_value": 10.0,
        "step": 1.0,

        "rounded_rect_kwargs": {
            "height": 0.075,
            "width": 2,
            "corner_radius": 0.0375
        },
        "circle_kwargs": {
            "radius": 0.1,
            "stroke_color": GREY_A,
            "fill_color": GREY_A,
            "fill_opacity": 1.0
        }
    }

    def __init__(self, value=0, **kwargs):
        digest_config(self, kwargs)
        self.bar = RoundedRectangle(**self.rounded_rect_kwargs)
        self.slider = Circle(**self.circle_kwargs)
        self.slider_axis = Line(
            start=self.bar.get_bounding_box_point(LEFT),
            end=self.bar.get_bounding_box_point(RIGHT)
        )
        self.slider_axis.set_opacity(0.0)
        self.slider.move_to(self.slider_axis)

        self.slider.add_mouse_drag_listner(self.slider_on_mouse_drag)

        super().__init__(value, self.bar, self.slider, self.slider_axis, ** kwargs)

    def assert_value(self, value):
        assert(self.min_value <= value <= self.max_value)

    def set_value_anim(self, value):
        prop = (value - self.min_value) / (self.max_value - self.min_value)
        self.slider.move_to(self.slider_axis.point_from_proportion(prop))

    def slider_on_mouse_drag(self, mob, event_data):
        self.set_value(self.get_value_from_point(event_data["point"]))
        return False

    # Helper Methods

    def get_value_from_point(self, point):
        start, end = self.slider_axis.get_start_and_end()
        point_on_line = get_closest_point_on_line(start, end, point)
        prop = get_norm(point_on_line - start) / get_norm(end - start)
        value = self.min_value + prop * (self.max_value - self.min_value)
        no_of_steps = int((value - self.min_value) / self.step)
        value_nearest_to_step = self.min_value + no_of_steps * self.step
        return value_nearest_to_step


class ColorSliders(Group):
    CONFIG = {
        "sliders_kwargs": {},
        "rect_kwargs": {
            "width": 2.0,
            "height": 0.5,
            "stroke_opacity": 1.0
        },
        "background_grid_kwargs": {
            "colors": [GREY_A, GREY_C],
            "single_square_len": 0.1
        },
        "sliders_buff": MED_LARGE_BUFF,
        "default_rgb_value": 255,
        "default_a_value": 1,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)

        rgb_kwargs = {"value": self.default_rgb_value, "min_value": 0, "max_value": 255, "step": 1}
        a_kwargs = {"value": self.default_a_value, "min_value": 0, "max_value": 1, "step": 0.04}

        self.r_slider = LinearNumberSlider(**self.sliders_kwargs, **rgb_kwargs)
        self.g_slider = LinearNumberSlider(**self.sliders_kwargs, **rgb_kwargs)
        self.b_slider = LinearNumberSlider(**self.sliders_kwargs, **rgb_kwargs)
        self.a_slider = LinearNumberSlider(**self.sliders_kwargs, **a_kwargs)
        self.sliders = Group(
            self.r_slider,
            self.g_slider,
            self.b_slider,
            self.a_slider
        )
        self.sliders.arrange(DOWN, buff=self.sliders_buff)

        self.r_slider.slider.set_color(RED)
        self.g_slider.slider.set_color(GREEN)
        self.b_slider.slider.set_color(BLUE)
        self.a_slider.slider.set_color_by_gradient([BLACK, WHITE])

        self.selected_color_box = Rectangle(**self.rect_kwargs)
        self.selected_color_box.add_updater(
            lambda mob: mob.set_fill(
                self.get_picked_color(), self.get_picked_opacity()
            )
        )
        self.background = self.get_background()

        super().__init__(
            Group(self.background, self.selected_color_box).fix_in_frame(),
            self.sliders,
            **kwargs
        )

        self.arrange(DOWN)

    def get_background(self):
        single_square_len = self.background_grid_kwargs["single_square_len"]
        colors = self.background_grid_kwargs["colors"]
        width = self.rect_kwargs["width"]
        height = self.rect_kwargs["height"]
        rows = int(height / single_square_len)
        cols = int(width / single_square_len)
        cols = (cols + 1) if (cols % 2 == 0) else cols

        single_square = Square(single_square_len)
        grid = single_square.get_grid(n_rows=rows, n_cols=cols, buff=0.0)
        grid.stretch_to_fit_width(width)
        grid.stretch_to_fit_height(height)
        grid.move_to(self.selected_color_box)

        for idx, square in enumerate(grid):
            assert(isinstance(square, Square))
            square.set_stroke(width=0.0, opacity=0.0)
            square.set_fill(colors[idx % len(colors)], 1.0)

        return grid

    def set_value(self, r, g, b, a):
        self.r_slider.set_value(r)
        self.g_slider.set_value(g)
        self.b_slider.set_value(b)
        self.a_slider.set_value(a)

    def get_value(self):
        r = self.r_slider.get_value() / 255
        g = self.g_slider.get_value() / 255
        b = self.b_slider.get_value() / 255
        alpha = self.a_slider.get_value()
        return color_to_rgba(rgb_to_color((r, g, b)), alpha=alpha)

    def get_picked_color(self):
        rgba = self.get_value()
        return rgb_to_hex(rgba[:3])

    def get_picked_opacity(self):
        rgba = self.get_value()
        return rgba[3]


class Textbox(ControlMobject):
    CONFIG = {
        "value_type": np.dtype(object),

        "box_kwargs": {
            "width": 2.0,
            "height": 1.0,
            "fill_color": WHITE,
            "fill_opacity": 1.0,
        },
        "text_kwargs": {
            "color": BLUE
        },
        "text_buff": MED_SMALL_BUFF,
        "isInitiallyActive": False,
        "active_color": BLUE,
        "deactive_color": RED,
    }

    def __init__(self, value="", **kwargs):
        digest_config(self, kwargs)
        self.isActive = self.isInitiallyActive
        self.box = Rectangle(**self.box_kwargs)
        self.box.add_mouse_press_listner(self.box_on_mouse_press)
        self.text = Text(value, **self.text_kwargs)
        super().__init__(value, self.box, self.text, **kwargs)
        self.update_text(value)
        self.active_anim(self.isActive)
        self.add_key_press_listner(self.on_key_press)

    def set_value_anim(self, value):
        self.update_text(value)

    def update_text(self, value):
        text = self.text
        self.remove(text)
        text.__init__(value, **self.text_kwargs)
        height = text.get_height()
        text.set_width(self.box.get_width() - 2 * self.text_buff)
        if text.get_height() > height:
            text.set_height(height)
        text.add_updater(lambda mob: mob.move_to(self.box))
        text.fix_in_frame()
        self.add(text)

    def active_anim(self, isActive):
        if isActive:
            self.box.set_stroke(self.active_color)
        else:
            self.box.set_stroke(self.deactive_color)

    def box_on_mouse_press(self, mob, event_data):
        self.isActive = not self.isActive
        self.active_anim(self.isActive)
        return False

    def on_key_press(self, mob, event_data):
        symbol = event_data["symbol"]
        modifiers = event_data["modifiers"]
        char = chr(symbol)
        if mob.isActive:
            old_value = mob.get_value()
            new_value = old_value
            if char.isalnum():
                if (modifiers & PygletWindowKeys.MOD_SHIFT) or (modifiers & PygletWindowKeys.MOD_CAPSLOCK):
                    new_value = old_value + char.upper()
                else:
                    new_value = old_value + char.lower()
            elif symbol in [PygletWindowKeys.SPACE]:
                new_value = old_value + char
            elif symbol == PygletWindowKeys.TAB:
                new_value = old_value + '\t'
            elif symbol == PygletWindowKeys.BACKSPACE:
                new_value = old_value[:-1] or ''
            mob.set_value(new_value)
            return False


class ControlPanel(Group):
    CONFIG = {
        "panel_kwargs": {
            "width": FRAME_WIDTH / 4,
            "height": MED_SMALL_BUFF + FRAME_HEIGHT,
            "fill_color": GREY_C,
            "fill_opacity": 1.0,
            "stroke_width": 0.0
        },
        "opener_kwargs": {
            "width": FRAME_WIDTH / 8,
            "height": 0.5,
            "fill_color": GREY_C,
            "fill_opacity": 1.0
        },
        "opener_text_kwargs": {
            "text": "Control Panel",
            "size": 0.4
        }
    }

    def __init__(self, *controls, **kwargs):
        digest_config(self, kwargs)

        self.panel = Rectangle(**self.panel_kwargs)
        self.panel.to_corner(UP + LEFT, buff=0)
        self.panel.shift(self.panel.get_height() * UP)
        self.panel.add_mouse_scroll_listner(self.panel_on_mouse_scroll)

        self.panel_opener_rect = Rectangle(**self.opener_kwargs)
        self.panel_info_text = Text(**self.opener_text_kwargs)
        self.panel_info_text.move_to(self.panel_opener_rect)

        self.panel_opener = Group(self.panel_opener_rect, self.panel_info_text)
        self.panel_opener.next_to(self.panel, DOWN, aligned_edge=DOWN)
        self.panel_opener.add_mouse_drag_listner(self.panel_opener_on_mouse_drag)

        self.controls = Group(*controls)
        self.controls.arrange(DOWN, center=False, aligned_edge=ORIGIN)
        self.controls.move_to(self.panel)

        super().__init__(
            self.panel, self.panel_opener,
            self.controls,
            **kwargs
        )

        self.move_panel_and_controls_to_panel_opener()
        self.fix_in_frame()

    def move_panel_and_controls_to_panel_opener(self):
        self.panel.next_to(
            self.panel_opener_rect,
            direction=UP,
            buff=0
        )

        controls_old_x = self.controls.get_x()
        self.controls.next_to(
            self.panel_opener_rect,
            direction=UP,
            buff=MED_SMALL_BUFF
        )

        self.controls.set_x(controls_old_x)

    def add_controls(self, *new_controls):
        self.controls.add(*new_controls)
        self.move_panel_and_controls_to_panel_opener()

    def remove_controls(self, *controls_to_remove):
        self.controls.remove(*controls_to_remove)
        self.move_panel_and_controls_to_panel_opener()

    def open_panel(self):
        panel_opener_x = self.panel_opener.get_x()
        self.panel_opener.to_corner(DOWN + LEFT, buff=0.0)
        self.panel_opener.set_x(panel_opener_x)
        self.move_panel_and_controls_to_panel_opener()
        return self

    def close_panel(self):
        panel_opener_x = self.panel_opener.get_x()
        self.panel_opener.to_corner(UP + LEFT, buff=0.0)
        self.panel_opener.set_x(panel_opener_x)
        self.move_panel_and_controls_to_panel_opener()
        return self

    def panel_opener_on_mouse_drag(self, mob, event_data):
        point = event_data["point"]
        self.panel_opener.match_y(Dot(point))
        self.move_panel_and_controls_to_panel_opener()
        return False

    def panel_on_mouse_scroll(self, mob, event_data):
        offset = event_data["offset"]
        factor = 10 * offset[1]
        self.controls.set_y(self.controls.get_y() + factor)
        return False
