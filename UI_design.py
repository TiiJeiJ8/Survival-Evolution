'''
Author: TiiJeiJ8
Project: Survival & Evolution  
Info: A simulation of biological evolution
Project Start Date: 2025-02-28

Module: UI_Design
Propose: To design user interface and other visual elements
'''

# import modules
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pygame
import random
import sys

from creature_def import Predator, Prey
from vegetation import Plant

# 初始化Pygame
pygame.init()

class GameCanvas:
    """游戏主画布"""
    def __init__(self, width=1500, height=1000):
        # 检测GPU加速支持
        self.gpu_accelerated = False
        try:
            # 尝试使用硬件加速模式
            self.screen = pygame.display.set_mode(
                (width, height), 
                pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED
            )
            self.gpu_accelerated = self._check_gpu_support()
        except pygame.error:
            # 回退到软件渲染
            self.screen = pygame.display.set_mode((width, height))
        # 在初始化日志中显示加速状态
        print(f"GPU Acceleration: {'Enabled' if self.gpu_accelerated else 'Disabled'}")

        # 初始化Pygame
        self.screen = pygame.display.set_mode((width, height))
        self.width = width
        self.height = height
        pygame.display.set_caption("Survival & Evolution")
        self.clock = pygame.time.Clock()
        self.bg_color = (44,64,73)  # 背景颜色
        self.executor = ThreadPoolExecutor(max_workers=6) # 线程池
        # 数据记录属性
        self.predator_counts = []
        self.prey_counts = []
        self.plant_history = []  # 植物历史记录
        self.last_plant_spawn = 0  # 上次生成植物的时间
        self.plant_spawn_interval = random.choice(range(900,2300))  # 植物生成的时间间隔（毫秒）
        self.current_plants = 0  # 植物生成计数器
        self.MAX_PLANTS = 200  # 最大植物生成数量
        chart_width = 230
        chart_start_y = height - 600 # 图表起始Y坐标
        self.charts = {
            'total': pygame.Rect(20, chart_start_y, chart_width, 130),
            'predator': pygame.Rect(20, chart_start_y + 150, chart_width, 130),
            'prey': pygame.Rect(20, chart_start_y + 300, chart_width, 130),
            'plant': pygame.Rect(20, chart_start_y + 450, chart_width, 130),
        }
        self.total_counts = []
        self.chart_update_interval = 500 # 图表更新的时间间隔（毫秒）
        self.last_chart_update = 0 # 上次图表更新的时间
        self.current_tick = 0 # 当前游戏的tick计数
        # 生物组（将在后续连接生物模块）
        self.predators = pygame.sprite.Group()
        self.prey = pygame.sprite.Group()
        self.plants = pygame.sprite.Group()

    def _check_gpu_support(self):
        """检测系统GPU加速支持"""
        drivers = ['direct3d', 'opengl', 'opengles2']
        current_driver = pygame.display.get_driver()
        return current_driver in drivers

    def draw_single_chart(self, surface, chart_rect, data, color, title):
        """绘制单个图表组件"""
        # 绘制背景
        bg_surface = pygame.Surface(chart_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (30,30,30,25), (0,0,*chart_rect.size), border_radius=10)
        surface.blit(bg_surface, chart_rect.topleft)
        # 全时段数据分析
        all_data = data  # 使用全部历史数据
        max_value = max(all_data) if all_data else 1
        min_value = min(all_data) if all_data else 0
        # 动态计算纵坐标范围（添加10%余量）
        value_range = max_value - min_value
        y_max = max_value + value_range * 0.1
        y_min = max(min_value - value_range * 0.1, 0)
        y_scale = chart_rect.height / (y_max - y_min) if (y_max - y_min) > 0 else 1
        # 横坐标缩放
        x_step = chart_rect.width / max(len(all_data)-1, 1)
        # 生成全局坐标点
        if len(all_data) > 1:
            points = [
                (chart_rect.left + i * x_step,
                 chart_rect.bottom - 10 - (d - y_min) * y_scale)
                for i, d in enumerate(all_data)
            ]
            pygame.draw.lines(surface, color, False, points, 2)
        # 优化标题位置
        font = pygame.font.SysFont('Arial', 15)
        current_value = data[-1] if data else 0
        text = font.render(f'{title}: {current_value}', True, 'white')
        surface.blit(text, (chart_rect.left + 5, chart_rect.top + 3))

    def draw_charts(self):
        """绘制图表"""
        # 使用带透明度的表面
        chart_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # 在图表表面添加tick显示
        font = pygame.font.SysFont('Arial', 16)
        tick_text = font.render(f'Tick: {self.current_tick}', True, (255,255,255))
        self.screen.blit(tick_text, (10, 5))
        # 使用循环绘制图表
        chart_configs = [
            ('total', self.total_counts, (104, 140, 200)),
            ('predator', self.predator_counts, (205, 82, 87)),
            ('prey', self.prey_counts, (239, 197, 127)),
            ('plant', self.plant_history, (147, 205, 147))
        ]
        for chart_type, data, color in chart_configs:
            self.draw_single_chart(chart_surface, self.charts[chart_type], 
                                 data, color, chart_type.capitalize())
        self.screen.blit(chart_surface, (0,0))

    def fps_display(self):
        """显示当前帧率"""
        font = pygame.font.SysFont('Arial', 16)
        fps_text = font.render(f'FPS: {int(self.clock.get_fps())}', True, (255,255,255))
        self.screen.blit(fps_text, (self.width-70, 5))

    def draw_background(self):
        """绘制自然环境背景"""
        self.screen.fill(self.bg_color)
        # 这里可以添加地形、植物等静态元素

    def _update_predators(self, prey_group):
        """并行更新捕食者状态"""
        for predator in self.predators:
            predator.update(prey_group)
    
    def _update_prey(self, predator_group, plant_group):
        """并行更新被捕食者状态"""
        for prey in self.prey:
            prey.update(predator_group, plant_group)

    def _spawn_plant_cluster(self):
        """生成植物簇"""
        if self.current_plants >= self.MAX_PLANTS:
            return
        cluster_size = random.randint(3,5)
        actual_size = min(cluster_size, self.MAX_PLANTS - self.current_plants)
        center_x = random.randint(50, self.width-50)
        center_y = random.randint(50, self.height-50)
        cluster_id = id(self)
        # 在一个区域内生成多个植物
        for _ in range(actual_size):
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            self.plants.add(Plant(
                center_x + offset_x,
                center_y + offset_y,
                cluster_id
            ))
            self.current_plants += 1

    def update(self):
        """更新画布内容"""
        self.current_tick += 1
        current_time = pygame.time.get_ticks()
        if current_time - self.last_plant_spawn >= self.plant_spawn_interval:
            self._spawn_plant_cluster()
            self.last_plant_spawn = current_time
        # 数据记录
        if current_time - self.last_chart_update >= self.chart_update_interval:
            self.last_chart_update = current_time
            pred_count = len(self.predators)
            prey_count = len(self.prey)
            self.predator_counts.append(pred_count)
            self.prey_counts.append(prey_count)
            self.plant_history.append(self.current_plants)
            self.total_counts.append(pred_count + prey_count + self.current_plants)
        # 并行更新生物状态
        future_pred = self.executor.submit(self._update_predators, self.prey)
        future_prey = self.executor.submit(self._update_prey, self.predators, self.plants)
        future_pred.result()
        future_prey.result()
        # 更新所有生物屏幕边界
        for obj in (*self.predators, *self.prey):
            obj.screen_rect = pygame.Rect(0, 0, self.width, self.height)
        self.current_plants = len(self.plants) # 更新当前植物数量
        # 绘制流程
        self.draw_background()              # 1.先绘制背景
        self.prey.draw(self.screen)         # 2.绘制被捕食者
        self.predators.draw(self.screen)    # 3.绘制捕食者
        self.plants.draw(self.screen)       # 3.绘制植物
        self.fps_display()                  # 4.绘制帧率
        self.draw_charts()                  # 5.最后绘制图表
        # 显示刷新与帧率控制
        pygame.display.flip()
        self.clock.tick(60)

def startUp(PREDATOR_COUNT, PREY_COUNT):
    """启动"""
    pygame.init()
    canvas = GameCanvas()
    # 配置生成参数
    PREDATOR_COUNT = PREDATOR_COUNT  # 捕食者数量
    PREY_COUNT = PREY_COUNT      # 被捕食者数量
    AREA_WIDTH = canvas.width  # 生成区域留边50px
    AREA_HEIGHT = canvas.height
    # 生成捕食者（随机位置）
    for _ in range(PREDATOR_COUNT):
        x = random.randint(50, AREA_WIDTH)
        y = random.randint(50, AREA_HEIGHT)
        canvas.predators.add(Predator(x, y))
    # 生成被捕食者（随机位置） 
    for _ in range(PREY_COUNT):
        x = random.randint(50, AREA_HEIGHT)
        y = random.randint(50, AREA_HEIGHT)
        canvas.prey.add(Prey(x, y))
    # 生成植物簇（随机位置）
    for _ in range(canvas.MAX_PLANTS):
        x = random.randint(50, AREA_WIDTH)
        y = random.randint(50, AREA_HEIGHT)
        canvas._spawn_plant_cluster()
    # 主循环
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        canvas.update()

# 示例用法
if __name__ == "__main__":
    canvas = GameCanvas()
    # 配置生成参数
    PREDATOR_COUNT = 13  # 捕食者数量
    PREY_COUNT = 30      # 被捕食者数量
    AREA_WIDTH = canvas.width - 50  # 生成区域留边50px
    AREA_HEIGHT = canvas.height - 50
    # 生成捕食者（随机位置）
    for _ in range(PREDATOR_COUNT):
        x = random.randint(50, AREA_WIDTH)
        y = random.randint(50, AREA_HEIGHT)
        canvas.predators.add(Predator(x, y))
    # 生成被捕食者（随机位置） 
    for _ in range(PREY_COUNT):
        x = random.randint(50, AREA_HEIGHT)
        y = random.randint(50, AREA_HEIGHT)
        canvas.prey.add(Prey(x, y))
    # 生成植物簇（随机位置）
    for _ in range(canvas.MAX_PLANTS):
        x = random.randint(50, AREA_WIDTH)
        y = random.randint(50, AREA_HEIGHT)
        canvas._spawn_plant_cluster()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        canvas.update()
