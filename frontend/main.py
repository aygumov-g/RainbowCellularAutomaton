import pygame as pgm
import requests


class Window:
	def __init__(
			self, pygame, width, height, background_color,
			net_color, default_cell_color, effect_cell_color,
			long_time_cell_colors, cell_size
	):
		"""
		Это функция инициализации, всё то что
		здесь, выполняется только один раз.
		"""
		
		# задаём цвет сетки
		self.net_color = net_color
		
		# задаём цвет фона
		self.background_color = background_color
		
		# задаём цвета для клеток
		self.default_cell_color = default_cell_color
		self.effect_cell_color = effect_cell_color
		self.long_time_cell_colors = long_time_cell_colors
		
		# размер клеток
		self.cell_size = cell_size

		# прокидываем основной "pygame"
		self.pygame = pygame

		# высота и ширина окна с игрой
		self.width = width // self.cell_size * self.cell_size
		self.height = height // self.cell_size * self.cell_size

		# создаём поверхность (это нужно чтобы была возможность рисовать)
		self.surface = self.pygame.display.set_mode((self.width, self.height+50))

		# создаем словарь с данными игры
		#self.net = {f"{i}:{j}": False for j in range(self.height // self.cell_size) for i in range(self.width // self.cell_size)}
		self.net = {f"{i}:{j}": {
			"status": False,
			"color": self.default_cell_color,
			"long_time": 0,
		} for j in range(self.height // self.cell_size) for i in range(self.width // self.cell_size)}

		# создаём список кнопок
		self.buttons = [
			{"id": 1, "color": (50, 205, 50), "text": "START", "rect": self.pygame.Rect(self.width // 3 * 0, self.height, self.width // 3, 50)},
			{"id": 2, "color": (255, 215, 0), "text": "STOP","rect": self.pygame.Rect(self.width // 3 * 1, self.height, self.width // 3, 50)},
			{"id": 3, "color": (178, 34, 34), "text": "RESTART","rect": self.pygame.Rect(self.width // 3 * 2, self.height, self.width // 3 + self.width % 3, 50)},
		]
		
		# задаём значение, которое показывает,
		# остановлена ли игра или нет
		self.pause = True

		# считываем количество кадров в секунду
		self.fps_controller = self.pygame.time.Clock()
		
		# задаём следующий момент времени, когда будет обновлено
		# содержимое экрана связанное с логикой игры
		self.last_update_time = self.pygame.time.get_ticks()
	
	def request(self):
		"""
		Этой функцией отправляем запросы к API.
		"""
		
		# Формируем структуру POST запроса, далее отправляем её на сервер,
		# принимаем ответ, а после если не произошло никаких ошибок, то
		# обновляем игровое поле на то, которое пришло в ответе.
		try:
			request = {
				"net": self.net,
				"default_cell_color": self.default_cell_color,
				"effect_cell_color": self.effect_cell_color,
				"long_time_cell_colors": self.long_time_cell_colors,
			}
			response = requests.post("http://localhost:12345", json=request, timeout=1)
			self.net = response.json()
		except requests.Timeout as exception:
			print(f"Время ожидания ответа от сервера истекло. {exception=}")
		except Exception as exception:
			print(f"Произошла неизвестная ошибка. {exception=}")
	
	def handle_button_click(self, mouse_pos):
		"""
		Этой функцией считываем нажатия на кнопки.
		"""
		
		for button in self.buttons:
			if button["rect"].collidepoint(mouse_pos):
				
				if button["id"] == 1:
					
					# если нажата кнопка "START", то убираем паузу
					self.pause = False
				
				elif button["id"] == 2:
		
					# если нажата кнопка "STOP", то ставим паузу
					self.pause = True
				
				elif button["id"] == 3:
		
					# если нажата кнопка "RESTART", то проходимся по всем
					# клеткам игры и очищаем каждую, а также, не забываем
					# поставить игру на паузу
					for cell in self.net:
						self.net[cell]["status"] = (
							False
						)
						
						# ставим игру на паузу
						self.pause = True
	
	def backlight(self, mouse_x, mouse_y):
		"""
		Этой функцией подсвечиваем клетку при наведении мышкой.
		"""
		
		if 0 <= mouse_x < self.width / self.cell_size and 0 <= mouse_y < self.height / self.cell_size:
			self.pygame.draw.rect(
				self.surface, (0, 255, 0),
				self.pygame.Rect(
					mouse_x * self.cell_size,
					mouse_y * self.cell_size,
					self.cell_size,
					self.cell_size
				), 3
			)
	
	def draw_buttons(self, mouse_pos, mouse_pressed):
		"""
		Этой функцией отрисовываем кнопки.
		"""
		
		for button in self.buttons:
			
			# Задаём цвет для текущей кнопки, в
			# зависимости от её состояния
			if button["rect"].collidepoint(mouse_pos):
				if mouse_pressed[0]:
					
					# при нажатии
					color = [i // 2 for i in button["color"]]
				else:
					
					# при наведении
					color = [min(i + 30, 255) for i in button["color"]]
			
			else:
				
				# в противном случае
				color = button["color"]
			
			# здесь ещё раз изменяем цвет текущей кнопки, в зависимости
			# от состояния игры (на паузе ли, или нет)
			if not self.pause and button["id"] == 1:
				
				# если игра на паузе, то делаем имитацию того,
				# что кнопка "START" якобы недоступна
				color = [i // 2 for i in button["color"]]
			
			elif self.pause and button["id"] == 2:
				
				# если игра не на паузе, то делаем имитацию того,
				# что кнопка "STOP" якобы недоступна
				color = [i // 2 for i in button["color"]]
			
			# отрисовываем кнопки, а также надписи на этих кнопках
			self.pygame.draw.rect(self.surface, color, button["rect"], border_radius=5)
			text_surf = self.pygame.font.Font("fonts/interface_font.otf", round(7.2 / 100 * self.width)).render(button["text"], True, (0, 0, 0))
			text_rect = text_surf.get_rect(center=button["rect"].center)
			self.surface.blit(
				text_surf,
				text_rect
			)
	
	def draw(self):
		"""
		Этой функцией отрисовываем сетку игры и квадратики.
		"""

		for x in range(0, self.width, self.cell_size):
			for y in range(0, self.height, self.cell_size):
				rect = self.pygame.Rect(x, y, self.cell_size, self.cell_size)
				key = f"{x // self.cell_size}:{y // self.cell_size}"
				if self.net.get(key, {"status": False})["status"]:
					self.pygame.draw.rect(self.surface, self.net[key]["color"], rect)
				self.pygame.draw.rect(self.surface, self.net_color, rect, 1)

	def start(self):
		"""
		Это основная функция для запуска игры.
		"""

		self.pygame.init()       # инициализируем сам модуль "pygame"
		self.pygame.font.init()  # инициализируем шрифты модуля "pygame"
		self.pygame.display.set_caption("Клеточный автомат")                    # устанавливаем заголовок окна
		self.pygame.display.set_icon(self.pygame.image.load("image/icon.png"))  # устанавливаем иконку окна
		while True:

			# для начало заливаем весь экран в сплошной цвет,
			# а после будем отрисовывать всё по новой
			self.surface.fill(self.background_color)

			# получаем позицию мышки
			mouse_pos = self.pygame.mouse.get_pos()
			mouse_pressed = pgm.mouse.get_pressed()
			mouse_x = mouse_pos[0] // self.cell_size
			mouse_y = mouse_pos[1] // self.cell_size

			# проверяем все поступившие на данные момент ивенты
			# и если среди них есть нажатие на крестик
			# то, закрываем окно с игрой
			for event in self.pygame.event.get():
				if event.type == self.pygame.QUIT:
					quit()
				elif (event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1) or mouse_pressed[0]:
					if self.pause:
						
						# при нажатии на какую-либо клетку левой кнопкой мыши (или при зажатии)
						# заполняем её только в том случае, если игра стоит на паузе
						self.net[f"{mouse_x}:{mouse_y}"] = {
							"status": True,
							"color": self.default_cell_color
						}
					
					if not mouse_pressed[0]:
					
						# если левая кнопка мыши не зажата, то запускаем специальную
						# функцию, которая обрабатывает нажатия на кнопки
						self.handle_button_click(mouse_pos)
					
				elif (event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 3) or mouse_pressed[2]:
					if self.pause:
						
						# при нажатии на какую-либо клетку правой кнопкой мыши (или при зажатии),
						# очищаем её только в том случае, если игра стоит на паузе
						self.net[f"{mouse_x}:{mouse_y}"] = {
								"status": False,
								"color": self.default_cell_color
							}
			
			# задаём в течении какого времени будут происходить события связанные
			# с основной логикой игры, а также, инициализируем саму логику игры
			current_time = self.pygame.time.get_ticks()
			if current_time - self.last_update_time >= 100:
				self.last_update_time = current_time

				if not self.pause:
					
					# если игра не стоит на паузе, то
					# отправляем запрос к API
					self.request()
				
			self.draw()                                  # отрисовка клеток и сетки
			self.draw_buttons(mouse_pos, mouse_pressed)  # отрисовка всех кнопок
			if self.pause:
				
				# при наведении мышки на какую-либо клетку, подсвечиваем
				# её только в том случае, если игра стоит на паузе
				self.backlight(mouse_x, mouse_y)
			
			self.fps_controller.tick(120)  # задаём количество кадров в секунду
			self.pygame.display.flip()     # обновляем содержимое экрана


Window(
	pygame=pgm,                            # объект окна
	width=900,                             # длина окна
	height=900,                            # ширина окна
	net_color=[200, 200, 200],             # цвет сетки
	background_color=[255, 255, 255],      # цвет фона
	default_cell_color=[0, 0, 0],          # цвет неподвижной клетки
	effect_cell_color=[220, 20, 60],       # цвет подвижной клетки
	long_time_cell_colors=[
		[[50, 205, 50], [20], [0]],    # зелёный цвет сработает на 20-ом ходе (0 - моргнуть)
		[[255, 140, 0], [45], [0]],    # оранжевый цвет сработает на 45-ом ходе (0 - моргнуть)
		[[30, 144, 255], [123], [1]],  # синий цвет сработает на 123-ем ходе (1 - перекрасить)
	],  # цвета для долго живучих клеток
	cell_size=10,
).start()
