# import numpy as np
import math

from manimlib.constants import *
from manimlib.animation.animation import Animation
from manimlib.animation.movement import Homotopy
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.composition import Succession
from manimlib.animation.creation import ShowCreation
from manimlib.animation.creation import ShowPartial
from manimlib.animation.fading import FadeOut
from manimlib.animation.transform import Transform
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Dot
from manimlib.mobject.shape_matchers import SurroundingRectangle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.geometry import Line
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import there_and_back
from manimlib.utils.rate_functions import wiggle


class FocusOn(Transform):
    CONFIG = {
        "opacity": 0.2,
        "color": GREY,
        "run_time": 2,
        "remover": True,
    }

    def __init__(self, focus_point, **kwargs):
        self.focus_point = focus_point
        # Initialize with blank mobject, while create_target
        # and create_starting_mobject handle the meat
        super().__init__(VMobject(), **kwargs)

    def create_target(self):
        little_dot = Dot(radius=0)
        little_dot.set_fill(self.color, opacity=self.opacity)
        little_dot.add_updater(
            lambda d: d.move_to(self.focus_point)
        )
        return little_dot

    def create_starting_mobject(self):
        return Dot(
            radius=FRAME_X_RADIUS + FRAME_Y_RADIUS,
            stroke_width=0,
            fill_color=self.color,
            fill_opacity=0,
        )


class Indicate(Transform):
    CONFIG = {
        "rate_func": there_and_back,
        "scale_factor": 1.2,
        "color": YELLOW,
    }

    def create_target(self):
        target = self.mobject.copy()
        target.scale(self.scale_factor)
        target.set_color(self.color)
        return target


class Flash(AnimationGroup):
    CONFIG = {
        "line_length": 0.2,
        "num_lines": 12,
        "flash_radius": 0.3,
        "line_stroke_width": 3,
        "run_time": 1,
    }

    def __init__(self, point, color=YELLOW, **kwargs):
        self.point = point
        self.color = color
        digest_config(self, kwargs)
        self.lines = self.create_lines()
        animations = self.create_line_anims()
        super().__init__(
            *animations,
            group=self.lines,
            **kwargs,
        )

    def create_lines(self):
        lines = VGroup()
        for angle in np.arange(0, TAU, TAU / self.num_lines):
            line = Line(ORIGIN, self.line_length * RIGHT)
            line.shift((self.flash_radius - self.line_length) * RIGHT)
            line.rotate(angle, about_point=ORIGIN)
            lines.add(line)
        lines.set_stroke(
            color=self.color,
            width=self.line_stroke_width
        )
        lines.add_updater(lambda l: l.move_to(self.point))
        return lines

    def create_line_anims(self):
        return [
            ShowCreationThenDestruction(line)
            for line in self.lines
        ]


class CircleIndicate(Indicate):
    CONFIG = {
        "rate_func": there_and_back,
        "remover": True,
        "circle_config": {
            "color": YELLOW,
        },
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        circle = self.get_circle(mobject)
        super().__init__(circle, **kwargs)

    def get_circle(self, mobject):
        circle = Circle(**self.circle_config)
        circle.add_updater(lambda c: c.surround(mobject))
        return circle

    def interpolate_mobject(self, alpha):
        super().interpolate_mobject(alpha)
        self.mobject.set_stroke(opacity=alpha)


class ShowPassingFlash(ShowPartial):
    CONFIG = {
        "time_width": 0.1,
        "remover": True,
    }

    def get_bounds(self, alpha):
        tw = self.time_width
        upper = interpolate(0, 1 + tw, alpha)
        lower = upper - tw
        upper = min(upper, 1)
        lower = max(lower, 0)
        return (lower, upper)

    def finish(self):
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.pointwise_become_partial(start, 0, 1)


class VShowPassingFlash(Animation):
    CONFIG = {
        "time_width": 0.3,
        "taper_width": 0.1,
        "remover": True,
    }

    def begin(self):
        self.mobject.align_stroke_width_data_to_points()
        super().begin()

    def interpolate_submobject(self, submobject, starting_sumobject, alpha):
        original_widths = starting_sumobject.get_stroke_widths()
        # anchor_widths = np.array([*original_widths[0::3, 0], original_widths[-1, 0]])
        anchor_widths = np.array([0, *original_widths[3::3, 0], 0])
        n_anchors = len(anchor_widths)
        time_width = self.time_width
        # taper_width = self.taper_width
        # Create a gaussian such that 3 sigmas out on either side
        # will equals time_width * (number of points)
        sigma = time_width / 6
        mu = interpolate(-time_width / 2, 1 + time_width / 2, alpha)
        offset = math.exp(-4.5)  # 3 sigmas out

        def kernel_func(x):
            result = math.exp(-0.5 * ((x - mu) / sigma)**2) - offset
            result = max(result, 0)
            # if x < taper_width:
            #     result *= x / taper_width
            # elif x > 1 - taper_width:
            #     result *= (1 - x) / taper_width
            return result

        kernel_array = np.array([
            kernel_func(n / (n_anchors - 1))
            for n in range(n_anchors)
        ])
        scaled_widths = anchor_widths * kernel_array
        new_widths = np.zeros(submobject.get_num_points())
        new_widths[0::3] = scaled_widths[:-1]
        new_widths[1::3] = (scaled_widths[:-1] + scaled_widths[1:]) / 2
        new_widths[2::3] = scaled_widths[1:]
        submobject.set_stroke(width=new_widths)

    def finish(self):
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.match_style(start)


class ShowCreationThenDestruction(ShowPassingFlash):
    CONFIG = {
        "time_width": 2.0,
        "run_time": 1,
    }


class ShowCreationThenFadeOut(Succession):
    CONFIG = {
        "remover": True,
    }

    def __init__(self, mobject, **kwargs):
        super().__init__(
            ShowCreation(mobject),
            FadeOut(mobject),
            **kwargs
        )


class AnimationOnSurroundingRectangle(AnimationGroup):
    CONFIG = {
        "surrounding_rectangle_config": {},
        # Function which takes in a rectangle, and spits
        # out some animation.  Could be some animation class,
        # could be something more
        "rect_animation": Animation
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        if "surrounding_rectangle_config" in kwargs:
            kwargs.pop("surrounding_rectangle_config")
        self.mobject_to_surround = mobject

        rect = self.get_rect()
        rect.add_updater(lambda r: r.move_to(mobject))

        super().__init__(
            self.rect_animation(rect, **kwargs),
        )

    def get_rect(self):
        return SurroundingRectangle(
            self.mobject_to_surround,
            **self.surrounding_rectangle_config
        )


class ShowPassingFlashAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_animation": ShowPassingFlash
    }


class ShowCreationThenDestructionAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_animation": ShowCreationThenDestruction
    }


class ShowCreationThenFadeAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_animation": ShowCreationThenFadeOut
    }


class ApplyWave(Homotopy):
    CONFIG = {
        "direction": UP,
        "amplitude": 0.2,
        "run_time": 1,
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs, locals())
        left_x = mobject.get_left()[0]
        right_x = mobject.get_right()[0]
        vect = self.amplitude * self.direction

        def homotopy(x, y, z, t):
            alpha = (x - left_x) / (right_x - left_x)
            power = np.exp(2.0 * (alpha - 0.5))
            nudge = there_and_back(t**power)
            return np.array([x, y, z]) + nudge * vect

        super().__init__(homotopy, mobject, **kwargs)


class WiggleOutThenIn(Animation):
    CONFIG = {
        "scale_value": 1.1,
        "rotation_angle": 0.01 * TAU,
        "n_wiggles": 6,
        "run_time": 2,
        "scale_about_point": None,
        "rotate_about_point": None,
    }

    def get_scale_about_point(self):
        if self.scale_about_point is None:
            return self.mobject.get_center()

    def get_rotate_about_point(self):
        if self.rotate_about_point is None:
            return self.mobject.get_center()

    def interpolate_submobject(self, submobject, starting_sumobject, alpha):
        submobject.match_points(starting_sumobject)
        submobject.scale(
            interpolate(1, self.scale_value, there_and_back(alpha)),
            about_point=self.get_scale_about_point()
        )
        submobject.rotate(
            wiggle(alpha, self.n_wiggles) * self.rotation_angle,
            about_point=self.get_rotate_about_point()
        )


class TurnInsideOut(Transform):
    CONFIG = {
        "path_arc": TAU / 4,
    }

    def create_target(self):
        return self.mobject.copy().reverse_points()
