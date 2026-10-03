"""
⚽ PRO SOCCER MOBILE 2026
eFootball Style Mobile Game
Kivy-based | Touch Controls | Smart Assist | Skill Moves
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Rectangle, Line, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.properties import NumericProperty, BooleanProperty
from kivy.metrics import dp
import math
import random

# =========================================================
# ==================== ڕێکخستن ============================
# =========================================================
# قەبارەی گونجاو بۆ مۆبایل (هەموو ئامێرەکان)
Window.softinput_mode = 'below_target'

# ڕەنگەکان
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


# =========================================================
# ==================== یاریگا =============================
# =========================================================
class Field:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.margin = dp(20)
        self.field_w = w - self.margin * 2
        self.field_h = h - self.margin * 2
        self.goal_height = self.field_h * 0.22
        self.goal_depth = dp(30)
        self.goal_y = (h - self.goal_height) / 2
        self.left_x = self.margin
        self.right_x = w - self.margin

    def get_goal_center(self, side):
        """ناوەندی گۆڵ: side='left' یان 'right'"""
        x = self.left_x - self.goal_depth / 2 if side == "left" else self.right_x + self.goal_depth / 2
        return Vector(x, self.h / 2)

    def is_inside(self, x, y):
        return (self.left_x < x < self.right_x and
                self.margin < y < self.h - self.margin)


# =========================================================
# ==================== تۆپ ================================
# =========================================================
class Ball:
    def __init__(self, x, y):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.radius = dp(11)
        self.friction = 0.982
        self.bounce = 0.72
        self.trail = []

    def update(self, dt, field):
        # جوڵە
        self.pos += self.vel * dt * 60

        # Friction
        self.vel *= self.friction ** (dt * 60)

        # Bounce لە دیوارەکان (جگە لە گۆڵ)
        if self.pos.x - self.radius < field.left_x:
            if not (field.goal_y < self.pos.y < field.goal_y + field.goal_height):
                self.pos.x = field.left_x + self.radius
                self.vel.x *= -self.bounce
        if self.pos.x + self.radius > field.right_x:
            if not (field.goal_y < self.pos.y < field.goal_y + field.goal_height):
                self.pos.x = field.right_x - self.radius
                self.vel.x *= -self.bounce
        if self.pos.y - self.radius < field.margin:
            self.pos.y = field.margin + self.radius
            self.vel.y *= -self.bounce
        if self.pos.y + self.radius > field.h - field.margin:
            self.pos.y = field.h - field.margin - self.radius
            self.vel.y *= -self.bounce

        if self.vel.length() < 0.05:
            self.vel = Vector(0, 0)

        # Trail
        if self.vel.length() > 8:
            self.trail.append([Vector(self.pos), 1.0])
        for i in range(len(self.trail) - 1, -1, -1):
            self.trail[i][1] -= dt * 3
            if self.trail[i][1] <= 0:
                self.trail.pop(i)
        if len(self.trail) > 10:
            self.trail.pop(0)

    def kick(self, direction, power):
        if direction.length() > 0:
            self.vel += direction.normalized() * power


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

        self.base_speed = dp(4.5)
        self.dash_speed = dp(7)
        self.finesse_speed = dp(3)
        self.accel = 0.5
        self.friction = 0.85

        self.kick_power = 16
        self.shoot_power = 20
        self.cooldown = 0

        self.facing = Vector(1, 0)
        self.anim_t = 0
        self.skill_timer = 0
        self.skill_type = None
        self.stamina = 100.0
        self.dash_trail = []

    def move(self, move_vec, dash=False, finesse=False, dt=0.016):
        if self.cooldown > 0:
            self.cooldown -= dt

        if move_vec.length() > 0.05:
            move_vec = move_vec.normalized()

            if dash and self.stamina > 20:
                target_speed = self.dash_speed
                self.stamina -= 30 * dt
                self.dash_trail.append([Vector(self.pos), 1.0])
            elif finesse:
                target_speed = self.finesse_speed
            else:
                target_speed = self.base_speed
                self.stamina = min(100, self.stamina + 15 * dt)

            self.vel += move_vec * self.accel
            self.facing = move_vec

            if self.vel.length() > target_speed:
                self.vel = self.vel.normalized() * target_speed
        else:
            self.vel *= self.friction
            self.stamina = min(100, self.stamina + 25 * dt)

        if self.vel.length() < 0.05:
            self.vel = Vector(0, 0)

        self.pos += self.vel * dt * 60

        # Trail decay
        for i in range(len(self.dash_trail) - 1, -1, -1):
            self.dash_trail[i][1] -= dt * 3
            if self.dash_trail[i][1] <= 0:
                self.dash_trail.pop(i)

        self.anim_t += self.vel.length() * dt * 8
        if self.skill_timer > 0:
            self.skill_timer -= dt

    def clamp_to_field(self, field):
        self.pos.x = max(field.left_x + self.radius,
                         min(field.right_x - self.radius, self.pos.x))
        self.pos.y = max(field.margin + self.radius,
                         min(field.h - field.margin - self.radius, self.pos.y))

    def collides_ball(self, ball):
        return (Vector(ball.pos) - Vector(self.pos)).length() < self.radius + ball.radius + dp(5)

    def shoot(self, ball, power_mult=1.0):
        if self.cooldown > 0 or not self.collides_ball(ball):
            return False

        # Smart aim بۆ گۆڵ
        goal = field.get_goal_center("right" if self.team == "left" else "left")
        direction = (goal - self.pos).normalized()

        power = self.shoot_power * power_mult
        ball.kick(direction, power)
        self.cooldown = 0.35
        return True

    def pass_ball(self, ball, target, high=False):
        if self.cooldown > 0 or not self.collides_ball(ball):
            return False

        if target:
            direction = (target.pos - self.pos).normalized()
            distance = (target.pos - self.pos).length()
            power = min(22, 8 + distance * 0.04) if not high else min(26, 12 + distance * 0.05)
        else:
            direction = self.facing.normalized() if self.facing.length() > 0 else Vector(1, 0)
            power = 12 if not high else 16

        ball.kick(direction, power)
        self.cooldown = 0.2
        return True

    def skill_move(self, ball, skill_name, direction):
        if self.skill_timer > 0 or not self.collides_ball(ball):
            return False

        if skill_name == "marseille":
            self.skill_timer = 0.5
            self.skill_type = "marseille"
            ball.vel += direction * 14
            self.vel = direction * -4
        elif skill_name == "rainbow":
            self.skill_timer = 0.6
            self.skill_type = "rainbow"
            ball.vel += direction * 10
            ball.vel.y -= 8
        elif skill_name == "elastico":
            self.skill_timer = 0.4
            self.skill_type = "elastico"
            perp = Vector(-direction.y, direction.x)
            ball.vel += perp * 10 + direction * 8
        elif skill_name == "roulette":
            self.skill_timer = 0.55
            self.skill_type = "roulette"
            ball.vel += direction * 12
        elif skill_name == "stepover":
            self.skill_timer = 0.3
            self.skill_type = "stepover"
            ball.vel += direction * 8
            self.vel = direction * 2
        return True


# =========================================================
# ==================== Smart Assist =======================
# =========================================================
class SmartAssist:
    def __init__(self, players, ball, field):
        self.players = players
        self.ball = ball
        self.field = field

    def find_best_pass_target(self, player):
        teammates = [p for p in self.players if p.team == player.team and p != player]
        if not teammates:
            return None

        best_score = -float('inf')
        best_target = None
        goal_x = self.field.right_x if player.team == "left" else self.field.left_x

        for t in teammates:
            dist = (Vector(t.pos) - Vector(player.pos)).length()
            if dist < dp(30):
                continue

            score = 100 - dist * 0.1

            # بەرەو گۆڵ باشتر
            if (goal_x - t.pos.x) * (1 if player.team == "left" else -1) > 0:
                score += 40

            # ئەگەر یاریزانی بەرامبەر نزیکە، خراپتر
            for opp in self.players:
                if opp.team != player.team:
                    if (Vector(opp.pos) - Vector(t.pos)).length() < dp(80):
                        score -= 30

            if score > best_score:
                best_score = score
                best_target = t

        return best_target

    def find_closest_to_ball(self, team):
        candidates = [p for p in self.players if p.team == team]
        if not candidates:
            return None
        return min(candidates, key=lambda p: (Vector(p.pos) - Vector(self.ball.pos)).length())


# =========================================================
# ==================== AI =================================
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

        dist = (Vector(self.ball.pos) - Vector(self.player.pos)).length()

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
        if self.action == "chase":
            d = Vector(self.ball.pos) - Vector(self.player.pos)
            if d.length() > 0:
                return d.normalized()
        elif self.action == "defend":
            home = Vector(self.field.right_x - dp(100), self.field.h / 2)
            d = home - Vector(self.player.pos)
            if d.length() > dp(10):
                return d.normalized()
        elif self.action == "attack":
            goal = Vector(self.field.left_x, self.field.h / 2)
            d = goal - Vector(self.player.pos)
            if d.length() > 0:
                return d.normalized()
        return Vector(0, 0)


# =========================================================
# ==================== Virtual Joystick ===================
# =========================================================
class Joystick(Widget):
    """Virtual Joystick بۆ مۆبایل (وەک eFootball)"""

    def __init__(self, center_x, center_y, radius, side='left', **kwargs):
        super().__init__(**kwargs)
        self.center = Vector(center_x, center_y)
        self.radius = radius
        self.knob_pos = Vector(center_x, center_y)
        self.active = False
        self.touch_id = None
        self.side = side
        self.output = Vector(0, 0)

    def on_touch_down(self, touch):
        if self.active:
            return False
        # ناوچەی جوڵە
        if self.side == 'left':
            # بۆ جوڵە، هەموو شاشەی چەپ کار دەکات
            if touch.x < Window.width / 2 and touch.y < Window.height * 0.6:
                self.active = True
                self.touch_id = touch.id
                self.center = Vector(touch.x, touch.y)
                self.knob_pos = Vector(touch.x, touch.y)
                return True
        return False

    def on_touch_move(self, touch):
        if self.active and touch.id == self.touch_id:
            self.knob_pos = Vector(touch.x, touch.y)
            delta = self.knob_pos - self.center
            if delta.length() > self.radius:
                delta = delta.normalized() * self.radius
                self.knob_pos = self.center + delta
            self.output = delta / self.radius
            return True
        return False

    def on_touch_up(self, touch):
        if self.active and touch.id == self.touch_id:
            self.active = False
            self.touch_id = None
            self.knob_pos = Vector(self.center)
            self.output = Vector(0, 0)
            return True
        return False

    def get_movement(self):
        return self.output


# =========================================================
# ==================== دوگمەکانی Action ===================
# =========================================================
class ActionButton(Widget):
    """دوگمەیەکی گەرد بۆ Action (وەک eFootball Mobile)"""

    def __init__(self, cx, cy, radius, label, color, callback=None, **kwargs):
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
        if (Vector(touch.x, touch.y) - Vector(self.cx, self.cy)).length() < self.radius:
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
# ==================== یاری سەرەکی ========================
# =========================================================
class SoccerGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.on_resize)

        # داتا
        self.field = None
        self.ball = None
        self.players = []
        self.user = None
        self.ai_brains = {}
        self.smart = None

        self.score_blue = 0
        self.score_red = 0
        self.match_time = 120.0
        self.game_over = False
        self.goal_banner = 0
        self.goal_team = None
        self.skill_popup_timer = 0
        self.skill_popup_name = None

        # Joysticks و دوگمەکان
        self.move_joystick = None
        self.buttons = []

        Clock.schedule_interval(self.update, 1 / 60.0)

    def on_resize(self, *args):
        """دروستکردنەوەی هەموو شتێک لەگەڵ قەبارەی نوێ"""
        self.field = Field(self.width, self.height)
        self.init_game()

    def init_game(self):
        # تۆپ
        self.ball = Ball(self.width / 2, self.height / 2)

        # تیمەکان
        blue, red = self.create_teams()
        self.players = blue + red
        self.user = blue[0]

        # AI
        self.ai_brains = {}
        for p in self.players:
            if p != self.user:
                self.ai_brains[p] = AIBrain(p, self.ball, self.players, self.field)

        self.smart = SmartAssist(self.players, self.ball, self.field)

        # Joystick
        self.move_joystick = Joystick(
            self.width * 0.2, self.height * 0.15, dp(70), side='left'
        )
        self.add_widget(self.move_joystick)

        # دوگمەکانی Action
        self.create_action_buttons()

        self.score_blue = 0
        self.score_red = 0
        self.match_time = 120.0
        self.game_over = False

    def create_action_buttons(self):
        """دوگمەکانی Action وەک eFootball"""
        # پاککردنەوە
        for b in self.buttons:
            self.remove_widget(b)
        self.buttons = []

        r = dp(38)  # قەبارەی دوگمەکان
        base_x = self.width - dp(90)
        base_y = self.height * 0.15

        # شووت (B) - گەورەترین
        shoot_btn = ActionButton(
            base_x, base_y, r * 1.2, "⚽",
            (0.84, 0.18, 0.18, 0.7),
            callback=self.on_shoot
        )
        self.buttons.append(shoot_btn)
        self.add_widget(shoot_btn)

        # پاسی کورت (A)
        pass_btn = ActionButton(
            base_x - dp(100), base_y + dp(50), r, "➤",
            (0.18, 0.37, 0.84, 0.7),
            callback=self.on_pass_low
        )
        self.buttons.append(pass_btn)
        self.add_widget(pass_btn)

        # پاسی بەرز (X)
        high_btn = ActionButton(
            base_x - dp(100), base_y - dp(50), r, "↑",
            (0.24, 0.78, 0.39, 0.7),
            callback=self.on_pass_high
        )
        self.buttons.append(high_btn)
        self.add_widget(high_btn)

        # Through Ball (Y)
        through_btn = ActionButton(
            base_x - dp(180), base_y, r, "⇢",
            (1, 0.84, 0, 0.7),
            callback=self.on_through
        )
        self.buttons.append(through_btn)
        self.add_widget(through_btn)

        # Dash (RT) - لە ژوورەوە
        dash_btn = ActionButton(
            base_x, base_y + dp(90), r * 0.9, "🏃",
            (1, 0.55, 0, 0.7),
            callback=self.on_dash
        )
        self.buttons.append(dash_btn)
        self.add_widget(dash_btn)

        # Skill (RT + Direction) - لە ژوورەوە
        skill_btn = ActionButton(
            base_x, base_y - dp(90), r * 0.9, "✦",
            (0.6, 0.2, 0.8, 0.7),
            callback=self.on_skill
        )
        self.buttons.append(skill_btn)
        self.add_widget(skill_btn)

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

    # ========== Action Callbacks ==========
    def on_shoot(self, action):
        if action == 'press':
            self.user.shoot(self.ball, 1.0)

    def on_pass_low(self, action):
        if action == 'press':
            target = self.smart.find_best_pass_target(self.user)
            self.user.pass_ball(self.ball, target, high=False)

    def on_pass_high(self, action):
        if action == 'press':
            target = self.smart.find_best_pass_target(self.user)
            self.user.pass_ball(self.ball, target, high=True)

    def on_through(self, action):
        if action == 'press':
            if self.user.collides_ball(self.ball) and self.user.cooldown <= 0:
                direction = self.user.facing.normalized() if self.user.facing.length() > 0 else Vector(1, 0)
                self.ball.kick(direction, 22)
                self.user.cooldown = 0.3

    def on_dash(self, action):
        if action == 'press':
            self.user.stamina = max(0, self.user.stamina - 15)

    def on_skill(self, action):
        if action == 'press':
            direction = self.move_joystick.get_movement()
            if direction.length() < 0.1:
                direction = self.user.facing.normalized()
            skills = ["marseille", "roulette", "elastico", "stepover", "rainbow"]
            chosen = random.choice(skills)
            if self.user.skill_move(self.ball, chosen, direction):
                self.skill_popup_name = chosen
                self.skill_popup_timer = 1.2

    # ========== نوێکردنەوە ==========
    def update(self, dt):
        if self.game_over:
            return

        # جوڵەی یاریزان
        move_vec = self.move_joystick.get_movement()
        dash = any(b.pressed for b in self.buttons if b.label == "🏃")
        self.user.move(move_vec, dash=dash, dt=dt)
        self.user.clamp_to_field(self.field)

        # AI
        for p in self.players:
            if p == self.user:
                continue
            brain = self.ai_brains[p]
            brain.update(dt)
            ai_move = brain.get_move()

            # AI شووت و پاس
            if p.collides_ball(self.ball) and p.cooldown <= 0:
                dist_to_goal = abs(p.pos.x - (self.field.left_x if p.team == "right" else self.field.right_x))
                if dist_to_goal < dp(300):
                    p.shoot(self.ball, 1.0)
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
        ball = self.ball
        # گۆڵی چەپ
        if ball.pos.x - ball.radius < self.field.left_x:
            if self.field.goal_y < ball.pos.y < self.field.goal_y + self.field.goal_height:
                self.score_red += 1
                self.reset_after_goal("right")
                return
        # گۆڵی ڕاست
        if ball.pos.x + ball.radius > self.field.right_x:
            if self.field.goal_y < ball.pos.y < self.field.goal_y + self.field.goal_height:
                self.score_blue += 1
                self.reset_after_goal("left")

    def reset_after_goal(self, team):
        self.goal_banner = 2.0
        self.goal_team = team

        self.ball.pos = Vector(self.width / 2, self.height / 2)
        self.ball.vel = Vector(0, 0)
        self.ball.trail.clear()

        w, h = self.width, self.height
        m = self.field.margin

        positions_blue = [
            (m + dp(100), h / 2), (m + dp(50), h / 2 - dp(80)),
            (m + dp(50), h / 2 + dp(80)), (m + dp(20), h / 2 - dp(140)),
            (m + dp(20), h / 2 + dp(140)),
        ]
        positions_red = [
            (w - m - dp(100), h / 2), (w - m - dp(50), h / 2 - dp(80)),
            (w - m - dp(50), h / 2 + dp(80)), (w - m - dp(20), h / 2 - dp(140)),
            (w - m - dp(20), h / 2 + dp(140)),
        ]
        for p, pos in zip([p for p in self.players if p.team == "left"], positions_blue):
            p.pos = Vector(pos)
            p.vel = Vector(0, 0)
        for p, pos in zip([p for p in self.players if p.team == "right"], positions_red):
            p.pos = Vector(pos)
            p.vel = Vector(0, 0)

    # ========== وێنەکێشان ==========
    def draw_field(self):
        # گیا بە چرچر
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

        # بازنەی ناوەند
        Line(circle=(
            self.width / 2, self.height / 2, dp(60)
        ), width=dp(2))

        # گۆڵەکان
        # چەپ
        Color(*LINE_WHITE)
        Line(rectangle=(
            self.field.left_x - self.field.goal_depth,
            self.field.goal_y,
            self.field.goal_depth,
            self.field.goal_height
        ), width=dp(2))

        # ڕاست
        Line(rectangle=(
            self.field.right_x,
            self.field.goal_y,
            self.field.goal_depth,
            self.field.goal_height
        ), width=dp(2))

        # Penalty Areas
        pen_w = dp(100)
        pen_h = self.field.field_h * 0.5
        Line(rectangle=(
            self.field.left_x,
            self.height / 2 - pen_h / 2,
            pen_w, pen_h
        ), width=dp(2))
        Line(rectangle=(
            self.field.right_x - pen_w,
            self.height / 2 - pen_h / 2,
            pen_w, pen_h
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
        Line(circle=(
            self.ball.pos.x, self.ball.pos.y, self.ball.radius
        ), width=dp(1.5))

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

            # ئەڵقەی سەرەوە
            Line(points=[
                p.pos.x - dp(8), p.pos.y - p.radius - dp(22),
                p.pos.x, p.pos.y - p.radius - dp(32),
                p.pos.x + dp(8), p.pos.y - p.radius - dp(22),
            ], width=dp(2.5))

            # Stamina
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
            Rectangle(pos=(bar_x, bar_y),
                     size=(bar_w * p.stamina / 100, bar_h))

    def draw_ui(self):
        # Scoreboard
        Color(*DARK_UI)
        RoundedRectangle(
            pos=(self.width / 2 - dp(100), dp(10)),
            size=(dp(200), dp(50)),
            radius=[dp(12)]
        )

        # خاڵ و کات بە Label
        # (بۆ ئاسانی، لە draw_label بەکار دەهێنین)

        # Goal Banner
        if self.goal_banner > 0:
            alpha = min(1.0, self.goal_banner / 1.5)
            Color(0, 0, 0, 0.6 * alpha)
            Rectangle(
                pos=(0, self.height / 2 - dp(60)),
                size=(self.width, dp(120))
            )

    def draw(self):
        # پاککردنەوە
        self.canvas.clear()

        with self.canvas:
            # یاریگا
            self.draw_field()

            # یاریزانەکان
            for p in self.players:
                self.draw_player(p)

            # تۆپ
            self.draw_ball()

            # UI
            self.draw_ui()

    def on_touch_down(self, touch):
        # پێش دوگمەکان و joystick
        if self.move_joystick.on_touch_down(touch):
            return True
        for b in self.buttons:
            if b.on_touch_down(touch):
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.move_joystick.on_touch_move(touch):
            return True
        for b in self.buttons:
            if b.on_touch_move(touch):
                return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.move_joystick.on_touch_up(touch):
            return True
        for b in self.buttons:
            if b.on_touch_up(touch):
                return True
        return super().on_touch_up(touch)


# =========================================================
# ==================== UI Overlay =========================
# =========================================================
class GameUI(FloatLayout):
    """UI ناوەکی بۆ پیشاندانی خاڵ و کات"""

    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game

        # Scoreboard
        self.score_label = Label(
            text="0 - 0",
            font_size=dp(28),
            bold=True,
            color=WHITE,
            pos_hint={'center_x': 0.5, 'top': 0.97},
            size_hint=(None, None),
            size=(dp(200), dp(50))
        )
        self.add_widget(self.score_label)

        # کات
        self.time_label = Label(
            text="02:00",
            font_size=dp(18),
            bold=True,
            color=YELLOW,
            pos_hint={'center_x': 0.5, 'top': 0.91},
            size_hint=(None, None),
            size=(dp(100), dp(30))
        )
        self.add_widget(self.time_label)

        # تیمی شین
        self.blue_label = Label(
            text="🔵 BLUE",
            font_size=dp(14),
            bold=True,
            color=BLUE,
            pos_hint={'center_x': 0.35, 'top': 0.97},
            size_hint=(None, None),
            size=(dp(100), dp(30))
        )
        self.add_widget(self.blue_label)

        # تیمی سوور
        self.red_label = Label(
            text="RED 🔴",
            font_size=dp(14),
            bold=True,
            color=RED,
            pos_hint={'center_x': 0.65, 'top': 0.97},
            size_hint=(None, None),
            size=(dp(100), dp(30))
        )
        self.add_widget(self.red_label)

        Clock.schedule_interval(self.update_ui, 0.1)

    def update_ui(self, dt):
        g = self.game
        self.score_label.text = f"{g.score_blue} - {g.score_red}"
        minutes = int(g.match_time) // 60
        seconds = int(g.match_time) % 60
        self.time_label.text = f"{minutes:02d}:{seconds:02d}"


# =========================================================
# ==================== App ================================
# =========================================================
class SoccerApp(App):
    def build(self):
        # ڕێکخستنی شاشە
        Window.clearcolor = (0.05, 0.05, 0.08, 1)

        root = FloatLayout()

        # یاری
        game = SoccerGame(size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        root.add_widget(game)

        # UI
        ui = GameUI(game, size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        ui.disabled = True  # بۆ ئەوەی touch بە game بگات
        root.add_widget(ui)

        # وێنەکێشان لە game
        Clock.schedule_interval(lambda dt: game.draw(), 1 / 60.0)

        return root

    def on_pause(self):
        return True

    def on_resume(self):
        pass


# =========================================================
# ==================== دەستپێکردن =========================
# =========================================================
if __name__ == "__main__":
    SoccerApp().run()