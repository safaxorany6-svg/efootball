"""
⚽ PRO SOCCER MOBILE 2026
eFootball Style Mobile Game | Production Ready
Kivy 2.3.0 | Android Ready | 60 FPS
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Rectangle, Line, RoundedRectangle, PushMatrix, PopMatrix
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.metrics import dp, sp
from kivy.config import Config

import math
import random
import gc

# =========================================================
# ==================== ڕێکخستن ============================
# =========================================================
Config.set('graphics', 'multisamples', '0')  # بۆ FPS باشتر
Config.set('graphics', 'preserve_context', '1')  # preservation
Config.set('kivy', 'exit_on_escape', '0')

# =========================================================
# ==================== ڕەنگەکان ===========================
# =========================================================
GRASS_DARK = (0.12, 0.47, 0.12, 1)
GRASS_LIGHT = (0.16, 0.57, 0.16, 1)
LINE_WHITE = (0.94, 0.94, 0.94, 1)
RED = (0.84, 0.18, 0.18, 1)
BLUE = (0.18, 0.37, 0.84, 1)
WHITE = (1, 1, 1, 1)
BLACK = (0.06, 0.07, 0.1, 1)
YELLOW = (1, 0.84, 0, 1)
GREEN_UI = (0.24, 0.78, 0.39, 1)
DARK_UI = (0.07, 0.09, 0.13, 0.85)
SKIN = (0.94, 0.78, 0.63, 1)
HAIR = (0.22, 0.14, 0.1, 1)
ORANGE = (1, 0.55, 0, 1)
PURPLE = (0.6, 0.2, 0.8, 1)


# =========================================================
# ==================== فەنکشنی یارمەتیدەر ==================
# =========================================================
def safe_normalize(v):
    """normalized بەبێ division by zero"""
    length = v.length()
    if length > 0.0001:
        return v / length
    return Vector(0, 0)


def vec_length_squared(v):
    """length squared بەبێ Vector.length_squared"""
    return v.x * v.x + v.y * v.y


def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t


def clamp(value, min_val, max_val):
    """سنووردارکردنی نرخ"""
    return max(min_val, min(max_val, value))


# =========================================================
# ==================== یاریگا =============================
# =========================================================
class Field:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.margin = dp(20)
        self.field_w = max(1, w - self.margin * 2)
        self.field_h = max(1, h - self.margin * 2)
        self.goal_height = self.field_h * 0.22
        self.goal_depth = dp(30)
        self.goal_y = (h - self.goal_height) / 2
        self.left_x = self.margin
        self.right_x = w - self.margin

    def get_goal_center(self, side):
        """ناوەندی گۆڵ"""
        if side == "left":
            x = self.left_x - self.goal_depth / 2
        else:
            x = self.right_x + self.goal_depth / 2
        return Vector(x, self.h / 2)


# =========================================================
# ==================== تۆپ ================================
# =========================================================
class Ball:
    MAX_TRAIL = 12

    def __init__(self, x, y):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.radius = dp(11)
        self.friction = 0.985
        self.bounce = 0.72
        self.trail = []

    def update(self, dt, field):
        # بەرەنگاری لە خێرایی زۆر
        dt = min(dt, 0.05)

        # جوڵە
        self.pos.x += self.vel.x * dt * 60
        self.pos.y += self.vel.y * dt * 60

        # Friction (نەرم)
        friction_factor = self.friction ** (dt * 60)
        self.vel.x *= friction_factor
        self.vel.y *= friction_factor

        # Bounce لە دیوارەکان
        if self.pos.x - self.radius < field.left_x:
            if not (field.goal_y < self.pos.y < field.goal_y + field.goal_height):
                self.pos.x = field.left_x + self.radius
                self.vel.x = abs(self.vel.x) * self.bounce
        if self.pos.x + self.radius > field.right_x:
            if not (field.goal_y < self.pos.y < field.goal_y + field.goal_height):
                self.pos.x = field.right_x - self.radius
                self.vel.x = -abs(self.vel.x) * self.bounce
        if self.pos.y - self.radius < field.margin:
            self.pos.y = field.margin + self.radius
            self.vel.y = abs(self.vel.y) * self.bounce
        if self.pos.y + self.radius > field.h - field.margin:
            self.pos.y = field.h - field.margin - self.radius
            self.vel.y = -abs(self.vel.y) * self.bounce

        # وەستان
        if self.vel.length() < 0.05:
            self.vel = Vector(0, 0)

        # Trail
        speed = self.vel.length()
        if speed > 8:
            self.trail.append([Vector(self.pos.x, self.pos.y), 1.0])
            if len(self.trail) > self.MAX_TRAIL:
                self.trail.pop(0)

        for i in range(len(self.trail) - 1, -1, -1):
            self.trail[i][1] -= dt * 3
            if self.trail[i][1] <= 0:
                self.trail.pop(i)

    def kick(self, direction, power):
        """لێدان بە ئاراستە و هێز"""
        norm_dir = safe_normalize(direction)
        if norm_dir.length() > 0:
            self.vel.x += norm_dir.x * power
            self.vel.y += norm_dir.y * power

    def reset(self, x, y):
        """ڕیسێتی تۆپ"""
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.trail.clear()


# =========================================================
# ==================== یاریزان ============================
# =========================================================
class Player:
    def __init__(self, x, y, color, team, number=10, is_user=False):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.color = color
        self.team = team
        self.number = number
        self.is_user = is_user
        self.radius = dp(15)

        # خێرایی
        self.base_speed = dp(4.5)
        self.dash_speed = dp(7)
        self.finesse_speed = dp(3)
        self.accel = 0.5
        self.friction = 0.85

        # شووت
        self.kick_power = 16
        self.shoot_power = 20
        self.cooldown = 0
        self.cooldown_max = 0.35

        # دۆخ
        self.facing = Vector(1, 0)
        self.anim_t = 0
        self.skill_timer = 0
        self.skill_type = None
        self.stamina = 100.0
        self.dash_trail = []

    def move(self, move_vec, dash=False, finesse=False, dt=0.016):
        dt = min(dt, 0.05)

        # Cooldown
        if self.cooldown > 0:
            self.cooldown -= dt
            if self.cooldown < 0:
                self.cooldown = 0

        # جوڵە
        if move_vec.length() > 0.05:
            move_vec = safe_normalize(move_vec)

            if dash and self.stamina > 20:
                target_speed = self.dash_speed
                self.stamina = max(0, self.stamina - 30 * dt)
                self.dash_trail.append([Vector(self.pos.x, self.pos.y), 1.0])
            elif finesse:
                target_speed = self.finesse_speed
            else:
                target_speed = self.base_speed
                self.stamina = min(100, self.stamina + 15 * dt)

            self.vel.x += move_vec.x * self.accel
            self.vel.y += move_vec.y * self.accel
            self.facing = Vector(move_vec.x, move_vec.y)

            if self.vel.length() > target_speed:
                self.vel = safe_normalize(self.vel) * target_speed
        else:
            self.vel.x *= self.friction
            self.vel.y *= self.friction
            self.stamina = min(100, self.stamina + 25 * dt)

        if self.vel.length() < 0.05:
            self.vel = Vector(0, 0)

        self.pos.x += self.vel.x * dt * 60
        self.pos.y += self.vel.y * dt * 60

        # Trail decay
        for i in range(len(self.dash_trail) - 1, -1, -1):
            self.dash_trail[i][1] -= dt * 3
            if self.dash_trail[i][1] <= 0:
                self.dash_trail.pop(i)

        # Animation
        self.anim_t += self.vel.length() * dt * 8
        if self.skill_timer > 0:
            self.skill_timer -= dt
            if self.skill_timer <= 0:
                self.skill_type = None

    def clamp_to_field(self, field):
        """سنووردارکردن بە یاریگا"""
        min_x = field.left_x + self.radius
        max_x = field.right_x - self.radius
        min_y = field.margin + self.radius
        max_y = field.h - field.margin - self.radius

        self.pos.x = clamp(self.pos.x, min_x, max_x)
        self.pos.y = clamp(self.pos.y, min_y, max_y)

    def collides_ball(self, ball):
        """پشکنینی بەرکەوتن لەگەڵ تۆپ"""
        dx = ball.pos.x - self.pos.x
        dy = ball.pos.y - self.pos.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < self.radius + ball.radius + dp(5)

    def shoot(self, ball, field, power_mult=1.0):
        """شووت بە Smart Aim"""
        if self.cooldown > 0 or not self.collides_ball(ball):
            return False

        goal_side = "right" if self.team == "left" else "left"
        goal = field.get_goal_center(goal_side)
        direction = Vector(goal.x - self.pos.x, goal.y - self.pos.y)

        power = self.shoot_power * power_mult
        ball.kick(direction, power)
        self.cooldown = self.cooldown_max
        return True

    def pass_ball(self, ball, target, high=False):
        """پاس"""
        if self.cooldown > 0 or not self.collides_ball(ball):
            return False

        if target:
            dx = target.pos.x - self.pos.x
            dy = target.pos.y - self.pos.y
            direction = Vector(dx, dy)
            distance = math.sqrt(dx * dx + dy * dy)
            if high:
                power = min(26, 12 + distance * 0.05)
            else:
                power = min(22, 8 + distance * 0.04)
        else:
            direction = Vector(self.facing.x, self.facing.y)
            power = 12 if not high else 16

        ball.kick(direction, power)
        self.cooldown = 0.2
        return True

    def skill_move(self, ball, skill_name, direction):
        """Skill Moves وەک eFootball"""
        if self.skill_timer > 0 or not self.collides_ball(ball):
            return False

        direction = safe_normalize(direction)
        if direction.length() < 0.01:
            direction = self.facing

        if skill_name == "marseille":
            self.skill_timer = 0.5
            self.skill_type = "marseille"
            ball.vel.x += direction.x * 14
            ball.vel.y += direction.y * 14
            self.vel.x = -direction.x * 4
            self.vel.y = -direction.y * 4
            return True

        elif skill_name == "rainbow":
            self.skill_timer = 0.6
            self.skill_type = "rainbow"
            ball.vel.x += direction.x * 10
            ball.vel.y += direction.y * 10 - 8
            return True

        elif skill_name == "elastico":
            self.skill_timer = 0.4
            self.skill_type = "elastico"
            perp = Vector(-direction.y, direction.x)
            ball.vel.x += perp.x * 10 + direction.x * 8
            ball.vel.y += perp.y * 10 + direction.y * 8
            return True

        elif skill_name == "roulette":
            self.skill_timer = 0.55
            self.skill_type = "roulette"
            ball.vel.x += direction.x * 12
            ball.vel.y += direction.y * 12
            return True

        elif skill_name == "stepover":
            self.skill_timer = 0.3
            self.skill_type = "stepover"
            ball.vel.x += direction.x * 8
            ball.vel.y += direction.y * 8
            self.vel.x = direction.x * 2
            self.vel.y = direction.y * 2
            return True

        return False

    def reset(self, x, y):
        """ڕیسێتی یاریزان"""
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.stamina = 100.0
        self.cooldown = 0
        self.skill_timer = 0
        self.skill_type = None
        self.dash_trail.clear()


# =========================================================
# ==================== Smart Assist =======================
# =========================================================
class SmartAssist:
    def __init__(self, players, ball, field):
        self.players = players
        self.ball = ball
        self.field = field

    def find_best_pass_target(self, player):
        """دۆزینەوەی باشترین یاریزان بۆ پاس"""
        teammates = [p for p in self.players
                     if p.team == player.team and p is not player]

        if not teammates:
            return None

        best_score = -float('inf')
        best_target = None
        goal_x = self.field.right_x if player.team == "left" else self.field.left_x

        for t in teammates:
            dx = t.pos.x - player.pos.x
            dy = t.pos.y - player.pos.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < dp(30):
                continue

            score = 100 - dist * 0.1

            # بەرەو گۆڵ باشتر
            if (goal_x - t.pos.x) * (1 if player.team == "left" else -1) > 0:
                score += 40

            # نزیکی دوژمن خراپتر
            for opp in self.players:
                if opp.team != player.team:
                    odx = opp.pos.x - t.pos.x
                    ody = opp.pos.y - t.pos.y
                    if math.sqrt(odx * odx + ody * ody) < dp(80):
                        score -= 30
                        break

            if score > best_score:
                best_score = score
                best_target = t

        return best_target

    def find_closest_to_ball(self, team):
        """نزیکترین یاریزان بۆ تۆپ"""
        candidates = [p for p in self.players if p.team == team]
        if not candidates:
            return None

        closest = None
        min_dist = float('inf')

        for p in candidates:
            dx = p.pos.x - self.ball.pos.x
            dy = p.pos.y - self.ball.pos.y
            dist = dx * dx + dy * dy
            if dist < min_dist:
                min_dist = dist
                closest = p

        return closest


# =========================================================
# ==================== AI Brain ===========================
# =========================================================
class AIBrain:
    def __init__(self, player, ball, players, field):
        self.player = player
        self.ball = ball
        self.players = players
        self.field = field
        self.decision_timer = 0
        self.action = "chase"

    def update(self, dt):
        self.decision_timer -= dt
        if self.decision_timer > 0:
            return
        self.decision_timer = 0.15

        dx = self.ball.pos.x - self.player.pos.x
        dy = self.ball.pos.y - self.player.pos.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < dp(40):
            self.action = "attack"
        elif self.player.team == "right":
            if self.ball.pos.x > self.field.w / 2:
                self.action = "chase"
            else:
                self.action = "defend"
        else:
            self.action = "chase"

    def get_move(self):
        """ئاراستەی جوڵە بۆ AI"""
        if self.action == "chase":
            d = Vector(self.ball.pos.x - self.player.pos.x,
                       self.ball.pos.y - self.player.pos.y)
            if d.length() > 0.1:
                return safe_normalize(d)

        elif self.action == "defend":
            home = Vector(self.field.right_x - dp(100), self.field.h / 2)
            d = Vector(home.x - self.player.pos.x, home.y - self.player.pos.y)
            if d.length() > dp(10):
                return safe_normalize(d)

        elif self.action == "attack":
            goal = Vector(self.field.left_x, self.field.h / 2)
            d = Vector(goal.x - self.player.pos.x, goal.y - self.player.pos.y)
            if d.length() > 0.1:
                return safe_normalize(d)

        return Vector(0, 0)


# =========================================================
# ==================== Virtual Joystick ===================
# =========================================================
class Joystick(Widget):
    """Virtual Joystick وەک eFootball Mobile"""

    def __init__(self, center_x, center_y, radius, side='left', **kwargs):
        kwargs.setdefault('size_hint', (None, None))
        kwargs.setdefault('size', (int(radius * 2), int(radius * 2)))
        kwargs.setdefault('pos', (int(center_x - radius), int(center_y - radius)))
        super().__init__(**kwargs)

        self.center = Vector(center_x, center_y)
        self.radius = radius
        self.knob_pos = Vector(center_x, center_y)
        self.active = False
        self.touch_id = None
        self.side = side
        self.output = Vector(0, 0)
        self.is_moving = False

    def on_touch_down(self, touch):
        if self.active:
            return False

        # ناوچە گەورە بۆ جوڵە (وەک eFootball)
        if touch.x < Window.width * 0.5 and touch.y < Window.height * 0.7:
            self.active = True
            self.touch_id = touch.id
            self.center = Vector(touch.x, touch.y)
            self.knob_pos = Vector(touch.x, touch.y)
            self.is_moving = True
            return True
        return False

    def on_touch_move(self, touch):
        if not (self.active and touch.id == self.touch_id):
            return False

        self.knob_pos = Vector(touch.x, touch.y)
        delta = Vector(self.knob_pos.x - self.center.x,
                       self.knob_pos.y - self.center.y)

        if delta.length() > self.radius:
            delta = safe_normalize(delta) * self.radius
            self.knob_pos = Vector(self.center.x + delta.x, self.center.y + delta.y)

        # Deadzone
        if self.radius > 0:
            self.output = Vector(delta.x / self.radius, delta.y / self.radius)

        return True

    def on_touch_up(self, touch):
        if self.active and touch.id == self.touch_id:
            self.active = False
            self.touch_id = None
            self.knob_pos = Vector(self.center.x, self.center.y)
            self.output = Vector(0, 0)
            self.is_moving = False
            return True
        return False

    def get_movement(self):
        return self.output


# =========================================================
# ==================== Action Button ======================
# =========================================================
class ActionButton(Widget):
    """دوگمەی Action وەک eFootball Mobile"""

    def __init__(self, cx, cy, radius, label, color, callback=None, **kwargs):
        kwargs.setdefault('size_hint', (None, None))
        kwargs.setdefault('size', (int(radius * 2), int(radius * 2)))
        kwargs.setdefault('pos', (int(cx - radius), int(cy - radius)))
        super().__init__(**kwargs)

        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.label = label
        self.color = color
        self.callback = callback
        self.pressed = False
        self.touch_id = None
        self.hold_timer = 0

    def on_touch_down(self, touch):
        dx = touch.x - self.cx
        dy = touch.y - self.cy
        if math.sqrt(dx * dx + dy * dy) < self.radius * 1.3:  # ئاسانتر بۆ لێدان
            self.pressed = True
            self.touch_id = touch.id
            self.hold_timer = 0
            if self.callback:
                self.callback('press')
            return True
        return False

    def on_touch_up(self, touch):
        if self.pressed and touch.id == self.touch_id:
            self.pressed = False
            self.touch_id = None
            if self.callback:
                self.callback('release')
            return True
        return False

    def update(self, dt):
        if self.pressed:
            self.hold_timer += dt


# =========================================================
# ==================== Soccer Game ========================
# =========================================================
class SoccerGame(Widget):
    MATCH_TIME = 120.0

    def __init__(self, **kwargs):
        kwargs.setdefault('size_hint', (1, 1))
        kwargs.setdefault('pos_hint', {'x': 0, 'y': 0})
        super().__init__(**kwargs)

        self.bind(size=self._on_resize)

        # داتا
        self.field = None
        self.ball = None
        self.players = []
        self.blue_team = []
        self.red_team = []
        self.user = None
        self.ai_brains = {}
        self.smart = None

        # دۆخ
        self.score_blue = 0
        self.score_red = 0
        self.match_time = self.MATCH_TIME
        self.game_over = False
        self.goal_banner = 0
        self.goal_team = None
        self.skill_popup_timer = 0
        self.skill_popup_name = None

        # UI
        self.move_joystick = None
        self.buttons = []

        self._initialized = False

    def _on_resize(self, instance, size):
        if size[0] < 10 or size[1] < 10:
            return
        self.field = Field(size[0], size[1])
        if not self._initialized:
            self._initialized = True
            self.init_game()
        else:
            self.rebuild_layout()

    def init_game(self):
        """دەستپێکردنی یاری"""
        w, h = self.width, self.height

        # تۆپ
        self.ball = Ball(w / 2, h / 2)

        # تیمەکان
        self.blue_team, self.red_team = self.create_teams()
        self.players = self.blue_team + self.red_team
        self.user = self.blue_team[0]

        # AI
        self.ai_brains = {}
        for p in self.players:
            if p is not self.user:
                self.ai_brains[p] = AIBrain(p, self.ball, self.players, self.field)

        self.smart = SmartAssist(self.players, self.ball, self.field)

        # UI
        self.build_controls()

        # ڕیسێت
        self.score_blue = 0
        self.score_red = 0
        self.match_time = self.MATCH_TIME
        self.game_over = False
        self.goal_banner = 0
        self.goal_team = None

    def build_controls(self):
        """دروستکردنی Joystick و دوگمەکان"""
        # پاککردنەوە
        if self.move_joystick:
            self.remove_widget(self.move_joystick)
        for b in self.buttons:
            self.remove_widget(b)
        self.buttons = []

        # Joystick
        jx = self.width * 0.18
        jy = self.height * 0.22
        jr = min(dp(75), self.width * 0.12)
        self.move_joystick = Joystick(jx, jy, jr, side='left')
        self.add_widget(self.move_joystick)

        # دوگمەکان
        r = min(dp(38), self.width * 0.06)
        base_x = self.width - dp(80)
        base_y = self.height * 0.22

        # شووت (B) - گەورەترین
        self.add_action(base_x, base_y, r * 1.3, "⚽",
                        (0.84, 0.18, 0.18, 0.85), self.on_shoot)

        # پاسی کورت (A)
        self.add_action(base_x - dp(105), base_y + dp(45), r, "➤",
                        (0.18, 0.37, 0.84, 0.85), self.on_pass_low)

        # پاسی بەرز (X)
        self.add_action(base_x - dp(105), base_y - dp(45), r, "↑",
                        (0.24, 0.78, 0.39, 0.85), self.on_pass_high)

        # Through Ball (Y)
        self.add_action(base_x - dp(195), base_y, r, "⇢",
                        (1, 0.84, 0, 0.85), self.on_through)

        # Dash (RT)
        self.add_action(base_x, base_y + dp(95), r * 0.9, "🏃",
                        (1, 0.55, 0, 0.85), self.on_dash)

        # Skill
        self.add_action(base_x, base_y - dp(95), r * 0.9, "✦",
                        (0.6, 0.2, 0.8, 0.85), self.on_skill)

    def add_action(self, cx, cy, radius, label, color, callback):
        btn = ActionButton(cx, cy, radius, label, color, callback=callback)
        self.buttons.append(btn)
        self.add_widget(btn)

    def rebuild_layout(self):
        """نوێکردنەوەی layout لە کاتی گۆڕینی قەبارە"""
        if not self._initialized:
            return
        self.build_controls()

    def create_teams(self):
        """دروستکردنی تیمەکان"""
        w, h = self.width, self.height
        m = self.field.margin

        blue = [
            Player(m + dp(100), h / 2, BLUE, "left", 10, is_user=True),
            Player(m + dp(50), h / 2 - dp(80), BLUE, "left", 7),
            Player(m + dp(50), h / 2 + dp(80), BLUE, "left", 9),
            Player(m + dp(20), h / 2 - dp(140), BLUE, "left", 4),
            Player(m + dp(20), h / 2 + dp(140), BLUE, "left", 5),
        ]
        red = [
            Player(w - m - dp(100), h / 2, RED, "right", 10),
            Player(w - m - dp(50), h / 2 - dp(80), RED, "right", 7),
            Player(w - m - dp(50), h / 2 + dp(80), RED, "right", 9),
            Player(w - m - dp(20), h / 2 - dp(140), RED, "right", 4),
            Player(w - m - dp(20), h / 2 + dp(140), RED, "right", 5),
        ]
        return blue, red

    # ========== Actions ==========
    def on_shoot(self, action):
        if action == 'press' and self.user and self.field:
            self.user.shoot(self.ball, self.field, 1.0)

    def on_pass_low(self, action):
        if action == 'press' and self.user:
            target = self.smart.find_best_pass_target(self.user)
            self.user.pass_ball(self.ball, target, high=False)

    def on_pass_high(self, action):
        if action == 'press' and self.user:
            target = self.smart.find_best_pass_target(self.user)
            self.user.pass_ball(self.ball, target, high=True)

    def on_through(self, action):
        if action == 'press' and self.user:
            if self.user.collides_ball(self.ball) and self.user.cooldown <= 0:
                direction = self.user.facing if self.user.facing.length() > 0.1 else Vector(1, 0)
                self.ball.kick(direction, 22)
                self.user.cooldown = 0.3

    def on_dash(self, action):
        if action == 'press' and self.user:
            self.user.stamina = max(0, self.user.stamina - 15)

    def on_skill(self, action):
        if action == 'press' and self.user:
            direction = self.move_joystick.get_movement()
            if direction.length() < 0.1:
                direction = self.user.facing
            skills = ["marseille", "roulette", "elastico", "stepover", "rainbow"]
            chosen = random.choice(skills)
            if self.user.skill_move(self.ball, chosen, direction):
                self.skill_popup_name = chosen
                self.skill_popup_timer = 1.2

    # ========== Update ==========
    def update(self, dt):
        if self.game_over or not self._initialized:
            return

        dt = min(dt, 0.05)

        # یاریزان
        move_vec = self.move_joystick.get_movement()
        dash = any(b.pressed for b in self.buttons if b.label == "🏃")
        self.user.move(move_vec, dash=dash, dt=dt)
        self.user.clamp_to_field(self.field)

        # AI
        for p in self.players:
            if p is self.user:
                continue
            brain = self.ai_brains[p]
            brain.update(dt)
            ai_move = brain.get_move()

            # AI شووت / پاس
            if p.collides_ball(self.ball) and p.cooldown <= 0:
                goal_x = self.field.left_x if p.team == "right" else self.field.right_x
                dist_to_goal = abs(p.pos.x - goal_x)
                if dist_to_goal < dp(300):
                    p.shoot(self.ball, self.field, 1.0)
                else:
                    target = self.smart.find_best_pass_target(p)
                    p.pass_ball(self.ball, target)

            p.move(ai_move, dt=dt)
            p.clamp_to_field(self.field)

        # تۆپ
        self.ball.update(dt, self.field)

        # گۆڵ
        self.check_goal()

        # کات
        self.match_time -= dt
        if self.match_time <= 0:
            self.match_time = 0
            self.game_over = True

        # Timers
        if self.goal_banner > 0:
            self.goal_banner -= dt
        if self.skill_popup_timer > 0:
            self.skill_popup_timer -= dt

        # دوگمەکان
        for b in self.buttons:
            b.update(dt)

    def check_goal(self):
        """پشکنینی گۆڵ"""
        ball = self.ball
        # گۆڵی چەپ (خاڵی ڕاست)
        if ball.pos.x + ball.radius < self.field.left_x:
            if self.field.goal_y < ball.pos.y < self.field.goal_y + self.field.goal_height:
                self.score_red += 1
                self.reset_after_goal()
                return
        # گۆڵی ڕاست (خاڵی شین)
        if ball.pos.x - ball.radius > self.field.right_x:
            if self.field.goal_y < ball.pos.y < self.field.goal_y + self.field.goal_height:
                self.score_blue += 1
                self.reset_after_goal()

    def reset_after_goal(self):
        """ڕیسێت دوای گۆڵ"""
        self.goal_banner = 2.0
        self.goal_team = "left" if self.score_blue > self.score_red else "right"

        # ڕیسێتی تۆپ
        self.ball.reset(self.width / 2, self.height / 2)

        # ڕیسێتی یاریزانەکان
        w, h = self.width, self.height
        m = self.field.margin

        blue_pos = [
            (m + dp(100), h / 2), (m + dp(50), h / 2 - dp(80)),
            (m + dp(50), h / 2 + dp(80)), (m + dp(20), h / 2 - dp(140)),
            (m + dp(20), h / 2 + dp(140)),
        ]
        red_pos = [
            (w - m - dp(100), h / 2), (w - m - dp(50), h / 2 - dp(80)),
            (w - m - dp(50), h / 2 + dp(80)), (w - m - dp(20), h / 2 - dp(140)),
            (w - m - dp(20), h / 2 + dp(140)),
        ]

        for p, pos in zip(self.blue_team, blue_pos):
            p.reset(pos[0], pos[1])
        for p, pos in zip(self.red_team, red_pos):
            p.reset(pos[0], pos[1])

    # ========== Draw ==========
    def draw_field(self):
        # گیا
        stripe_h = self.height / 10
        for i in range(10):
            if i % 2 == 0:
                Color(*GRASS_LIGHT)
            else:
                Color(*GRASS_DARK)
            Rectangle(pos=(0, i * stripe_h), size=(self.width, stripe_h))

        # سنووری یاریگا
        Color(*LINE_WHITE)
        Line(rectangle=(
            self.field.left_x, self.field.margin,
            self.field.field_w, self.field.field_h
        ), width=dp(2))

        # هێڵی نیوە
        Line(points=[
            self.width / 2, self.field.margin,
            self.width / 2, self.field.margin + self.field.field_h
        ], width=dp(2))

        # بازنە ناوەند
        Line(circle=(self.width / 2, self.height / 2, dp(60)), width=dp(2))

        # گۆڵەکان
        Line(rectangle=(
            self.field.left_x - self.field.goal_depth,
            self.field.goal_y, self.field.goal_depth, self.field.goal_height
        ), width=dp(2))
        Line(rectangle=(
            self.field.right_x, self.field.goal_y,
            self.field.goal_depth, self.field.goal_height
        ), width=dp(2))

        # Penalty Areas
        pen_w = dp(100)
        pen_h = self.field.field_h * 0.5
        Line(rectangle=(
            self.field.left_x, self.height / 2 - pen_h / 2, pen_w, pen_h
        ), width=dp(2))
        Line(rectangle=(
            self.field.right_x - pen_w, self.height / 2 - pen_h / 2, pen_w, pen_h
        ), width=dp(2))

    def draw_ball(self):
        # Trail
        for trail_pos, alpha in self.ball.trail:
            Color(1, 1, 1, alpha * 0.4)
            Ellipse(
                pos=(trail_pos.x - self.ball.radius * alpha,
                     trail_pos.y - self.ball.radius * alpha),
                size=(self.ball.radius * 2 * alpha, self.ball.radius * 2 * alpha)
            )

        # سێبەر
        Color(0, 0, 0, 0.3)
        Ellipse(
            pos=(self.ball.pos.x - self.ball.radius,
                 self.ball.pos.y + self.ball.radius * 0.7),
            size=(self.ball.radius * 2, self.ball.radius * 0.6)
        )

        # تۆپ
        Color(*WHITE)
        Ellipse(
            pos=(self.ball.pos.x - self.ball.radius,
                 self.ball.pos.y - self.ball.radius),
            size=(self.ball.radius * 2, self.ball.radius * 2)
        )

        # دەرکار
        Color(*BLACK)
        Line(circle=(self.ball.pos.x, self.ball.pos.y, self.ball.radius), width=dp(1.5))

    def draw_player(self, p):
        # Dash trail
        for trail_pos, alpha in p.dash_trail:
            Color(p.color[0], p.color[1], p.color[2], alpha * 0.3)
            Ellipse(
                pos=(trail_pos.x - p.radius * alpha,
                     trail_pos.y - p.radius * alpha),
                size=(p.radius * 2 * alpha, p.radius * 2 * alpha)
            )

        # سێبەر
        Color(0, 0, 0, 0.3)
        Ellipse(
            pos=(p.pos.x - p.radius, p.pos.y + p.radius * 0.7),
            size=(p.radius * 2, p.radius * 0.6)
        )

        # جەستە
        Color(*p.color)
        Ellipse(
            pos=(p.pos.x - p.radius, p.pos.y - p.radius),
            size=(p.radius * 2, p.radius * 2)
        )

        # دەرکار
        Color(*BLACK)
        Line(circle=(p.pos.x, p.pos.y, p.radius), width=dp(1.5))

        # سەر
        Color(*SKIN)
        Ellipse(
            pos=(p.pos.x - dp(8), p.pos.y - p.radius - dp(14)),
            size=(dp(16), dp(16))
        )

        # ئاماژەی یاریزانی بەکارهێنەر
        if p.is_user:
            Color(*YELLOW)
            Line(circle=(p.pos.x, p.pos.y, p.radius + dp(5)), width=dp(2.5))
            Line(points=[
                p.pos.x - dp(8), p.pos.y - p.radius - dp(22),
                p.pos.x, p.pos.y - p.radius - dp(32),
                p.pos.x + dp(8), p.pos.y - p.radius - dp(22),
            ], width=dp(2.5))

            # Stamina bar
            bar_w = dp(35)
            bar_h = dp(4)
            bar_x = p.pos.x - bar_w / 2
            bar_y = p.pos.y + p.radius + dp(10)

            Color(0, 0, 0, 0.7)
            Rectangle(pos=(bar_x - dp(1), bar_y - dp(1)),
                     size=(bar_w + dp(2), bar_h + dp(2)))

            if p.stamina > 50:
                Color(*GREEN_UI)
            elif p.stamina > 20:
                Color(*YELLOW)
            else:
                Color(*RED)
            Rectangle(pos=(bar_x, bar_y), size=(bar_w * p.stamina / 100, bar_h))

    def draw_ui(self):
        # Scoreboard
        Color(*DARK_UI)
        RoundedRectangle(
            pos=(self.width / 2 - dp(100), dp(10)),
            size=(dp(200), dp(50)),
            radius=[dp(12)]
        )

        # Goal banner
        if self.goal_banner > 0:
            alpha = min(1.0, self.goal_banner / 1.5)
            Color(0, 0, 0, 0.6 * alpha)
            Rectangle(
                pos=(0, self.height / 2 - dp(60)),
                size=(self.width, dp(120))
            )

    def draw(self, dt=None):
        """وێنەکێشان"""
        if not self._initialized:
            return

        self.canvas.clear()

        with self.canvas:
            self.draw_field()
            for p in self.players:
                self.draw_player(p)
            self.draw_ball()
            self.draw_ui()

    # ========== Touch ==========
    def on_touch_down(self, touch):
        if self.move_joystick and self.move_joystick.on_touch_down(touch):
            return True
        for b in self.buttons:
            if b.on_touch_down(touch):
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.move_joystick and self.move_joystick.on_touch_move(touch):
            return True
        for b in self.buttons:
            if b.on_touch_move(touch):
                return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.move_joystick and self.move_joystick.on_touch_up(touch):
            return True
        for b in self.buttons:
            if b.on_touch_up(touch):
                return True
        return super().on_touch_up(touch)


# =========================================================
# ==================== UI Overlay =========================
# =========================================================
class GameUI(FloatLayout):
    """UI overlay"""

    def __init__(self, game, **kwargs):
        kwargs.setdefault('size_hint', (1, 1))
        kwargs.setdefault('pos_hint', {'x': 0, 'y': 0})
        super().__init__(**kwargs)
        self.game = game

        self.score_label = Label(
            text="0 - 0", font_size=sp(28), bold=True, color=WHITE,
            pos_hint={'center_x': 0.5, 'top': 0.97},
            size_hint=(None, None), size=(dp(200), dp(50))
        )
        self.add_widget(self.score_label)

        self.time_label = Label(
            text="02:00", font_size=sp(18), bold=True, color=YELLOW,
            pos_hint={'center_x': 0.5, 'top': 0.91},
            size_hint=(None, None), size=(dp(100), dp(30))
        )
        self.add_widget(self.time_label)

        # Block touch
        self.bind(size=self._on_size)

    def _on_size(self, *args):
        pass

    def update_ui(self, dt):
        g = self.game
        if not g or not g._initialized:
            return
        self.score_label.text = f"{g.score_blue} - {g.score_red}"
        minutes = int(g.match_time) // 60
        seconds = int(g.match_time) % 60
        self.time_label.text = f"{minutes:02d}:{seconds:02d}"


# =========================================================
# ==================== App ================================
# =========================================================
class SoccerApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.08, 1)

        self.root_widget = FloatLayout()

        # یاری
        self.game = SoccerGame()
        self.root_widget.add_widget(self.game)

        # UI
        self.ui = GameUI(self.game)
        self.root_widget.add_widget(self.ui)

        # یەک Clock بۆ هەموو
        Clock.schedule_interval(self.tick, 1 / 60.0)

        return self.root_widget

    def tick(self, dt):
        """یەک clock: update + draw"""
        if self.game:
            self.game.update(dt)
            self.game.draw(dt)
        if self.ui:
            self.ui.update_ui(dt)

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        # پاککردنەوە
        Clock.unschedule(self.tick)
        gc.collect()


# =========================================================
# ==================== دەستپێکردن =========================
# =========================================================
if __name__ == "__main__":
    SoccerApp().run()