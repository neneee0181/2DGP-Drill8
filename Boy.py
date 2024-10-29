from pico2d import load_image, get_time

from state_machine import space_down, time_out, right_down, left_down, left_up, \
    right_up, start_event, auto_run
from state_machine import StateMachine


class Idle:
    @staticmethod
    def enter(boy, e):
        if left_up(e) or right_down(e):
            boy.action = 2
            boy.face_dir = -1
        elif right_up(e) or left_down(e) or start_event(e):
            boy.action = 3
            boy.face_dir = 1

        boy.dir = 0
        boy.frame = 0
        # 시작 시간을 기록
        boy.start_time = get_time()
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        if get_time() - boy.start_time > 5:
            # 이벤트 발생
            boy.state_machine.add_event(('TIME_OUT', 0))
        boy.frame = (boy.frame + 1) % 8
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class Sleep:
    @staticmethod
    def enter(boy, e):
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        pass

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                3.141592 / 2,  # 회전 각도
                '',  # 좌우상하 반전 X
                boy.x - 25, boy.y - 25, 100, 100
            )
        elif boy.face_dir == -1:
            boy.image.clip_composite_draw(
                boy.frame * 100, 200, 100, 100,
                -3.141592 / 2,  # 회전 각도
                '',  # 좌우상하 반전 X
                boy.x + 25, boy.y - 25, 100, 100
            )
        pass


class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.action = 1
            boy.dir = 1
        elif left_down(e) or right_up(e):
            boy.action = 0
            boy.dir = -1
        boy.frame = 0
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * boy.speed
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            boy.x, boy.y
        )
        pass


class AutoRun:

    @staticmethod
    def enter(boy, e):
        if boy.action == 1 or boy.action == 3:
            boy.action = 1
            boy.dir = 1
        elif boy.action == 0 or boy.action == 2:
            boy.action = 0
            boy.dir = -1
        # 시작 시간을 기록
        boy.start_time = get_time()
        pass

    @staticmethod
    def exit(boy, e):
        # 값 초기화
        boy.size_x = 100
        boy.size_y = 100
        boy.speed = 3
        boy.y = 90
        pass

    @staticmethod
    def do(boy):

        if get_time() - boy.start_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))
            boy.speed = 3
            # 종료 -> 방향
            if boy.action == 0: boy.action = 2
            if boy.action == 1: boy.action = 3

        # 좌우 변환
        if boy.x >= 785:
            boy.dir = -1
            boy.action = 0
        elif boy.x <= 25:
            boy.dir = 1
            boy.action = 1

        # 스피드 증가
        boy.speed += 0.1

        # 크기 증가
        if get_time() - boy.start_time < 2.5:
            boy.size_x += 2
            boy.size_y += 2
            boy.y += 0.7 # 캐릭터 y 좌표 값 증가
        else:
            boy.size_x -= 2
            boy.size_y -= 2
            boy.y -= 0.7

        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * boy.speed
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            boy.x, boy.y, boy.size_x, boy.size_y
        )
        pass


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.speed = 3
        self.action = 3
        self.size_x = 100
        self.size_y = 100
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)  # 어떤 객체를 위한 상태 머신인지 알려줄 필요가 있음
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep,
                       auto_run: AutoRun},
                Run: {right_down: Idle, left_down: Idle, left_up: Idle, right_up: Idle, auto_run: AutoRun},
                Sleep: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, space_down: Idle,
                        auto_run: AutoRun},
                AutoRun: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Idle}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # event : input event
        # state machine event : (이벤트종류, 값)
        self.state_machine.add_event(
            ('INPUT', event)
        )

        pass

    def draw(self):
        self.state_machine.draw()
