'''
Author: TiiJeiJ8
Project: Survival & Evolution
Info: A simulation of biological evolution
Project Start Date: 2025-02-28

Module: animal_def
Propose: To define the visual representation of animals
'''

# import modules
import pygame
import random
import math

class Predator(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.screen_rect = pygame.Rect(0, 0, 800, 600)
        """捕食者视觉定义"""
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (205, 82, 87), (8, 8), 3)
        self.rect = self.image.get_rect(center=(x, y))
        """能量系统定义"""
        self.energy = 100.0
        self.radius = 3  # 用于圆形碰撞检测（半径）
        """捕食者行为定义"""
        self.speed = 1.7
        angle = random.uniform(0, 360)
        self.direction = pygame.math.Vector2(1, 0).rotate(angle)  # 从0度方向开始随机旋转
        self.direction.normalize_ip()
        """捕食者属性定义"""
        self.stamina = 150 # 耐力
        self.max_speed = 3.8 # 最大速度
        self.fov_angle = 220 # 视野角度
        self.sensory_distance = 100 # 感知范围
        self.hearing_radius = 60 # 听觉范围
        self.is_chasing = False # 是否追逐
        self.chase_stamina_threshold = 20 # 耐力阈值
        self.energy_emergency_threshold = 30 # 能量阈值
        self.emergency_speed_boost = 1.3 # 紧急速度加成
        """捕食者攻击属性"""
        self.hunt_cooldown = 0    # 成功捕猎冷却（帧）
        self.HUNT_COOLDOWN = 3200   # 成功捕猎冷却时间
        """捕食者繁殖属性"""
        self.is_reproducing = False # 是否繁殖
        self.reproduce_duration = 0 # 繁殖持续时间（帧）
        self.max_energy = 100 # 最大能量
        self.reproduce_threshold_ratio = 0.85 # 繁殖能量阈值
        self.reproduce_timer = 0 # 达标持续时间（帧）
        self.wander_duration = 0 # 游荡持续时间（帧）
        self.reproduce_cooldown = 0 # 繁殖冷却时间（帧）
    
    def wander(self):
        """游荡行为"""
        if not self.is_chasing:
            # 被动追踪逻辑
            visible_prey = [
                p for p in self.groups()[0]
                if self._is_in_cone(p.rect.center) and 
                self._is_within_distance(p.rect.center) and
                isinstance(p, Prey)
            ]
            if visible_prey:
                # 仅调整方向不触发正式追逐
                dx = visible_prey[0].rect.centerx - self.rect.centerx
                dy = visible_prey[0].rect.centery - self.rect.centery
                try:
                    target_dir = pygame.math.Vector2(dx, dy).normalize()
                    self.direction = self.direction.lerp(target_dir, 0.1).normalize()
                except ValueError:
                    pass
            # 保持随机转向逻辑
            if random.random() < 0.02:
                self.direction = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
            # 游荡速度维持
            if visible_prey:
                self.speed = min(self.max_speed, self.speed + 0.01)  # 发现猎物时加速但限制上限
            elif self.energy <= self.max_energy * 0.3:  # 低能量状态
                self.speed = min(2.5, self.speed + 0.01)  # 保持较高速度寻找食物
            else:
                self.speed = max(1.5, self.speed - 0.02)  # 正常状态缓慢减速
            self.stamina = min(self.stamina + 1, 100)

    def _is_in_cone(self, target_pos):
        """锥形视野检测"""
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        target_angle = math.degrees(math.atan2(-dy, dx)) % 360
        source_angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) % 360
        angle_diff = abs(target_angle - source_angle) % 360
        return angle_diff <= self.fov_angle / 2 or angle_diff >= 360 - self.fov_angle / 2
    
    def _is_within_distance(self, target_pos, radius=None):
        """距离检测"""
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        return (dx ** 2 + dy ** 2) ** 0.5 <= (radius or self.sensory_distance)

    def _chase(self, target_pos):
        """追逐行为"""
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        if dx == 0 and dy == 0:
            self.direction = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
            return
        try:
            target_dir = pygame.math.Vector2(dx, dy).normalize()
            self.direction = self.direction.lerp(target_dir, 0.2).normalize() # 平滑转向
        except ValueError:
            direction = self.direction.rotate(30).normalize()
        direction = pygame.math.Vector2(dx, dy).normalize()
        self.direction = self.direction.lerp(direction, 0.15).normalize() # 平滑转向
        self.speed = min(self.max_speed, self.speed * 1.08)
        self.stamina = max(self.stamina - 0.4, 0)
        self.energy = max(self.energy - 0.05, 0)
        self.is_chasing = True

    def _reproduce(self):
        """繁殖行为"""
        offset = random.uniform(2, 5) # 防止重叠
        child = Predator(self.rect.centerx + offset, self.rect.centery + offset)
        child.energy = self.max_energy * self.reproduce_threshold_ratio # 新个体能量为繁殖能量阈值的85%（避免新生儿刚落地就能生，太生草了）
        child.hunt_cooldown = child.HUNT_COOLDOWN # 添加捕猎冷却（不能一出生就是杀手吧？）
        return child
    
    def _edge_bounce(self, prey_group):
        """边缘反弹"""
        prev_rect = self.rect.copy()
        self.rect.clamp_ip(self.screen_rect)
        if self.rect.left != prev_rect.left or self.rect.right!= prev_rect.right:
            self.direction.x *= -1
        if self.rect.top!= prev_rect.top or self.rect.bottom!= prev_rect.bottom:
            self.direction.y *= -1

    def _attack(self, prey_group):
        """攻击行为"""
        collied_preys = pygame.sprite.spritecollide(self, prey_group, False, pygame.sprite.collide_circle)
        for prey in collied_preys:
            if prey.alive:
                dx = prey.rect.centerx - self.rect.centerx
                dy = prey.rect.centery - self.rect.centery
                if dx == 0 and dy == 0:
                    direction = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
                else:
                    direction = pygame.math.Vector2(dx, dy).normalize()
                repel_distance = 2 # 击退距离
                self.rect.centerx -= direction.x * repel_distance
                self.rect.centery -= direction.y * repel_distance
                prey.rect.centerx += direction.x * repel_distance
                prey.rect.centery += direction.y * repel_distance
                self.speed = max(1.5, self.speed - 0.3) # 捕食者速度减缓
                prey.energy -= 15 # 猎物扣除15点能量
                self.energy = min(self.energy + 7, 100) # 捕食者增加7点能量
                if prey.energy <= 0:
                    self.hunt_cooldown = self.HUNT_COOLDOWN # 成功捕猎冷却
                    prey.kill()
                    self.is_chasing = False
                    self.speed = max(1.5, self.speed - 0.1) # 捕食者速度减缓

    def update(self, prey_group):
        """更新捕食者状态"""
        # 边缘反弹
        self._edge_bounce(prey_group)
        # 移动逻辑
        if not self.is_reproducing:
            self.rect.center += self.direction * self.speed
            visible_prey = [
                p for p in prey_group
                if self._is_in_cone(p.rect.center) and self._is_within_distance(p.rect.center)
            ]
            # 正常行为
            if visible_prey and visible_prey[0].alive and self.hunt_cooldown <= 0:
                self._chase(visible_prey[0].rect.center) # 有猎物，出动!
                if self.stamina <= self.chase_stamina_threshold: # 低耐力时开始游荡
                    self.is_chasing = False
                    self.wander() # 无猎物，游荡一会儿...
            else:
                self.wander() # 无猎物，游荡一会儿...
        else:
            self.reproduce_duration -= 1
            if self.reproduce_duration <= 0:
                self.is_reproducing = False
        # 两种生物发生碰撞即捕食者发出攻击
        self._attack(prey_group)
        self.hunt_cooldown = max(0, self.hunt_cooldown - 1)
        # 繁殖
        if(
            not self.is_reproducing and # 繁殖中
            self.energy >= self.max_energy * self.reproduce_threshold_ratio and
            self.reproduce_cooldown <= 0 # 繁殖冷却
        ):
            self.reproduce_timer += 1 # 1帧
            self.wander_duration += 1 # 1帧
            if not self.is_chasing:
                self.wander_duration += 1
        else:
            self.reproduce_timer = max(0, self.reproduce_timer - 2)
            self.wander_duration = 0
        if (
            self.reproduce_timer >= 180 and # 180帧
            self.wander_duration >= 60 and # 60帧
            not self.is_chasing and # 不在追逐状态
            self.reproduce_cooldown <= 0 and # 繁殖冷却
            random.random() < 0.4
        ):
            # 触发繁殖强制重置追逐状态
            self.is_chasing = False
            self.is_reproducing = True
            self.reproduce_duration = 60 # 繁殖60帧
            child = self._reproduce()
            if child:
                self.groups()[0].add(child)
            self.energy = max(self.energy * 0.6, 0)
            self.reproduce_cooldown = 10800
        self.reproduce_cooldown =  max(0, self.reproduce_cooldown - 1) # 繁殖冷却
        # 每帧消耗基础能量
        self.energy = max(self.energy - 0.01, 0)
        if self.energy <= 0:
            self.kill()

class Prey(Predator):
    def __init__(self, x, y):
        super().__init__(x, y)
        """被捕食者视觉定义"""
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (239, 197, 127), (8, 8), 2)
        self.rect = self.image.get_rect(center=(x, y))
        """能量系统定义"""
        self.energy = 100
        self.radius = 2.5  # 用于圆形碰撞检测（半径）
        self.hunger_threshold = 40 # 饥饿阈值
        """被捕食者行为定义"""
        self.speed = 1.5
        angle = random.uniform(0, 360)
        self.direction = pygame.math.Vector2(1, 0).rotate(angle)
        self.direction.normalize_ip()
        """被捕食者属性定义"""
        self.stamina = 100 # 耐力
        self.max_speed = 3.2 # 最大速度
        self.fov_angle = 85 # 视野角度
        self.sensory_distance = 100 # 感知范围
        self.hearing_radius = 56 # 听觉范围
        self.alive = True # 是否存活
        self.is_fleeing = False # 是否逃跑
        """被捕食者繁殖属性"""
        self.max_energy = 100 # 最大能量
        self.reproduce_threshold_ratio = 0.85 # 繁殖能量阈值
        self.reproduce_timer = 0 # 达标持续时间（帧）
        self.wander_duration = 0 # 游荡持续时间（帧）
        self.reproduce_cooldown = 0 # 繁殖冷却时间（帧）

    def _eat_plant(self, plant_group):
        """进食植物"""
        eaten = pygame.sprite.spritecollide(self, plant_group, True) # 碰撞检测并移除植物
        if eaten:
            if hasattr(self, 'canvas'):
                self.canvas.current_plants -= len(eaten)
                self.canvas.plants.remove(*eaten) # 移除被吃植物
            self.energy = min(self.energy + eaten[0].energy, self.max_energy) # 进食能量
            self.stamina = min(self.stamina + 15 * len(eaten), 100) # 体力恢复
    
    def kill(self):
        self.alive = False
        super().kill()

    def _flee(self, threat_pos):
        """逃离威胁"""
        self.is_fleeing = True
        dx = self.rect.centerx - threat_pos[0]
        dy = self.rect.centery - threat_pos[1]
        if dx == 0 and dy == 0:
            self.direction = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
            return
        try:
            target_dir = pygame.math.Vector2(dx, dy).normalize()
            self.direction = self.direction.lerp(target_dir, 0.25).normalize() # 平滑转向
        except ValueError:
            direction = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
        direction = pygame.math.Vector2(dx, dy).normalize()
        self.direction = direction
        self.speed = min(self.max_speed, self.speed + 0.05)
        self.stamina = max(self.stamina - 2.3, 0)
        self.energy = max(self.energy - 0.04, 0) # 被追逐消耗能量

    def wander(self):
        """游荡行为"""
        if pygame.time.get_ticks() % 100 < 30:
            angle = random.uniform(-45, 45)  # 被捕食者转向更灵活
            self.direction = self.direction.rotate(angle).normalize()
        self.speed = max(1.5, self.speed - 0.05)
        self.stamina = min(self.stamina + 0.04, 90)

    def _is_within_hearing(self, target_pos):
        """听觉检测"""
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        return (dx ** 2 + dy ** 2) ** 0.5 <= self.hearing_radius
    
    def _reproduce(self):
        """繁殖行为"""
        offset = random.uniform(2, 5)
        child = Prey(self.rect.centerx + offset, self.rect.centery + offset)
        child.energy = self.max_energy * self.reproduce_threshold_ratio # 新个体能量为繁殖能量阈值的85%（避免新生儿刚落地就能生，太生草了）
        return child

    def update(self, predator_group, plant_group):
        """更新被捕食者状态"""
        nearby_predators = [
            p for p in predator_group
            if ((self._is_in_cone(p.rect.center) and self._is_within_distance(p.rect.center))
            or self._is_within_hearing(p.rect.center)) 
            and (p.rect.centerx != self.rect.centerx or p.rect.centery != self.rect.centery)
        ]
        if nearby_predators and self.stamina > 0 and nearby_predators[0].alive:
            self._flee(nearby_predators[0].rect.center) # 有捕食者，逃离！
        elif self.energy < self.hunger_threshold:
            # 寻找最近可食用植物
            nearby_plants = [
                p for p in plant_group
                if self._is_within_distance(p.rect.center, 45)
            ]
            if nearby_plants:
                target = min(nearby_plants,
                             key=lambda p: (p.rect.centerx - self.rect.centerx) ** 2 + (p.rect.centery - self.rect.centery) ** 2)
                dx = target.rect.centerx - self.rect.centerx
                dy = target.rect.centery - self.rect.centery
                if dx == 0 and dy == 0:
                    foot_dir = pygame.math.Vector2(dx, dy).normalize()
                    self.direction = self.direction.lerp(foot_dir, 0.15).normalize()
                    self.speed = min(self.speed * 1.05, self.max_speed)
                else:
                    target_dir = pygame.math.Vector2(dx, dy).normalize()
                    self.direction = self.direction.lerp(target_dir, 0.2).normalize()
                    self.speed = min(self.speed * 1.07, self.max_speed)
                    self.wander()
        else:
            self.wander() # 无捕食者，游荡一会儿...
        super().update([])
        self._eat_plant(plant_group)
        # 繁殖
        if (
            self.energy >= self.max_energy * self.reproduce_threshold_ratio and
            self.reproduce_cooldown <= 0
            and not self.is_fleeing
        ):
            self.reproduce_timer += 1
            self.wander_duration += 1
        else:
            self.reproduce_timer = max(0, self.reproduce_timer-1)
            self.wander_duration = 0
        if(
            self.reproduce_timer >= 180 and
            self.wander_duration >= 60 and
            self.reproduce_cooldown <= 0 and
            random.random() < 0.6
        ):
            child = self._reproduce()
            if child:
                self.groups()[0].add(child)
            self.energy = max(self.energy * 0.6, 0)
            self.reproduce_cooldown = 90
        self.reproduce_cooldown = max(0, self.reproduce_cooldown-1)
        self.is_fleeing = False
        # 每帧消耗基础能量
        self.energy = max(self.energy - 0.004, 0)
        if self.energy <= 0:
            self.kill()