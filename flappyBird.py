import os
import random
import pygame as pg
import neat

ai_playing = False
generation = 0

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

IMG_PIPE = pg.transform.scale2x(pg.image.load(os.path.join('imgs','pipe.png')))
IMG_FLOOR = pg.transform.scale2x(pg.image.load(os.path.join('imgs','base.png')))
IMG_BG = pg.transform.scale2x(pg.image.load(os.path.join('imgs','bg.png')))
IMGS_BIRD =  [
  pg.transform.scale2x(pg.image.load(os.path.join('imgs','bird1.png'))),
  pg.transform.scale2x(pg.image.load(os.path.join('imgs','bird2.png'))),
  pg.transform.scale2x(pg.image.load(os.path.join('imgs','bird3.png')))
]

pg.font.init()
SCORE_FONT = pg.font.SysFont('arial', 40)


class Bird:
  IMGS = IMGS_BIRD
  # Rotation animations
  MAX_ROTATION = 25
  ROTATION_VELOCITY = 20
  ANIMATION_TIME = 5
  
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.angle = 0
    self.velocity = 0
    self.altura = self.y
    self.time = 0
    self.img_count = 0
    self.img = self.IMGS[0]
    
  def jump(self):
    self.velocity = -10.5
    self.time = 0
    self.altura = self.y
  
  def move(self):
    # Displacement calculation
    self.time += 1
    displacement = 1.5 * (self.time**2) + self.velocity * self.time
  
    # Restrict the displacement
    if displacement > 16:
      displacement = 16
    elif displacement < 0: # test without this
      displacement -= 2

    self.y += displacement

    # Bird angle
    if displacement < 0 or self.y < (self.altura + 50): # test without the self.y condition
      if self.angle < self.MAX_ROTATION:
        self.angle = self.MAX_ROTATION
    else:
      if self.angle > -90:
        self.angle -= self.ROTATION_VELOCITY
  
  def draw(self, screen):
    # Define the image to use
    self.img_count += 1

    if self.img_count < self.ANIMATION_TIME:
      self.img = self.IMGS[0]
    elif self.img_count < self.ANIMATION_TIME*2:
      self.img = self.IMGS[1]
    elif self.img_count < self.ANIMATION_TIME*3:
      self.img = self.IMGS[2]
    elif self.img_count < self.ANIMATION_TIME*4:
      self.img = self.IMGS[1]
    elif self.img_count >= self.ANIMATION_TIME*4 + 1:
      self.img = self.IMGS[0]
      self.img_count = 0

    # If the bird is droping, don't animate
    if self.angle <= -80:
      self.img = self.IMGS[1]
      self.img_count = self.ANIMATION_TIME*2
  
    # Draw the image
    img_rotated = pg.transform.rotate(self.img, self.angle)
    center_img = self.img.get_rect(topleft=(self.x, self.y)).center
    rect = img_rotated.get_rect(center=center_img)
    screen.blit(img_rotated, rect.topleft)
    
  def get_mask(self):
    return pg.mask.from_surface(self.img)

class Pipe:
  DISTANCE = 200
  VELOCITY = 5
  
  def __init__(self, x):
    self.x = x
    self.heigth = 0
    self.top_pos = 0
    self.bottom_pos = 0
    self.TOP_IMG = pg.transform.flip(IMG_PIPE, False, True)
    self.BOTTOM_IMG = IMG_PIPE
    self.passed = False
    self.define_heigth()
    
  def define_heigth(self):
    self.heigth = random.randrange(50, 450)
    self.top_pos = self.heigth - self.TOP_IMG.get_height()
    self.bottom_pos = self.heigth + self.DISTANCE
  
  def move(self):
    self.x -= self.VELOCITY
  
  def draw(self, screen):
    screen.blit(self.TOP_IMG, (self.x, self.top_pos))
    screen.blit(self.BOTTOM_IMG, (self.x, self.bottom_pos))
    
  def colide(self, bird):
    bird_mask = bird.get_mask()
    top_mask = pg.mask.from_surface(self.TOP_IMG)
    bottom_mask = pg.mask.from_surface(self.BOTTOM_IMG)
    distance_top = (self.x - bird.x, self.top_pos - round(bird.y))
    distance_bottom = (self.x - bird.x, self.bottom_pos - round(bird.y))
    top_point = bird_mask.overlap(top_mask, distance_top)
    bottom_point = bird_mask.overlap(bottom_mask, distance_bottom)
    if top_point or bottom_point:
      return True
    return False


class Floor:
  VELOCITY = 5
  WIDTH = IMG_FLOOR.get_width()
  IMG = IMG_FLOOR
  
  def __init__(self, y) -> None:
    self.y = y
    self.x1 = 0
    self.x2 = self.WIDTH
    
  def move(self):
    self.x1 -= self.VELOCITY
    self.x2 -= self.VELOCITY
    if self.x1 + self.WIDTH < 0:
      self.x1 = self.x2 + self.WIDTH
    if self.x2 + self.WIDTH < 0:
      self.x2 = self.x1 + self.WIDTH
  
  def draw(self, screen):
    screen.blit(self.IMG, (self.x1, self.y))
    screen.blit(self.IMG, (self.x2, self.y))
    
    
def draw_game(screen, birds, pipes, floor, score):
  screen.blit(IMG_BG, (0, 0))
  for bird in birds:
    bird.draw(screen)
  for pipe in pipes:
    pipe.draw(screen)
  text = SCORE_FONT.render(f'Score: {score}', 1, (255, 255, 255))
  screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
  if ai_playing:
    text = SCORE_FONT.render(f'Generation: {generation}', 1, (255, 255, 255))
    screen.blit(text, (10, 10))
  floor.draw(screen)
  pg.display.update()
  
def main(genomes, config): # Fitness function
  global generation
  generation += 1
  
  if ai_playing:
    neural_networks = []
    genome_list = []
    birds = []
    for _, genome in genomes:
      neural_network = neat.nn.FeedForwardNetwork.create(genome, config)
      neural_networks.append(neural_network)
      genome.fitness = 0
      genome_list.append(genome)
      birds.append(Bird(230, 350))
  else:
    birds = [Bird(230, 350)]
  floor = Floor(730)
  pipes = [Pipe(700)]
  screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  score = 0
  clock = pg.time.Clock()
  
  running = True
  while running:
    clock.tick(30)

    for event in pg.event.get():
      if event.type == pg.QUIT:
        running = False
        pg.quit()
        quit()
      if not ai_playing:
        if event.type == pg.KEYDOWN:
          if event.key == pg.K_ESCAPE:
            running = False
            pg.quit()
            quit()
          if event.key == pg.K_SPACE:
            for bird in birds:
              bird.jump()
        
    index_pipe = 0
    if len(birds) > 0:
      if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_IMG.get_width()):
        index_pipe = 1
    else:
      running = False
      break
    for i, bird in enumerate(birds):
      bird.move()
      if ai_playing:
        genome_list[i].fitness += 0.1
        output = neural_networks[i].activate((bird.y, 
                                              abs(bird.y - pipes[index_pipe].heigth), 
                                              abs(bird.y - pipes[index_pipe].bottom_pos)))
        if output[0] > 0.5:
          bird.jump()
    floor.move()
      
    add_pipe = False
    remove_pipes = []
    for pipe in pipes:
      for i, bird in enumerate(birds):
        if pipe.colide(bird):
          if ai_playing:
            genome_list[i].fitness -= 1
            genome_list.pop(i)
            neural_networks.pop(i)
          birds.pop(i)
        if not pipe.passed and bird.x > pipe.x:
          pipe.passed = True
          add_pipe = True
      pipe.move()
      if pipe.x + pipe.TOP_IMG.get_width() < 0:
        remove_pipes.append(pipe)
    if add_pipe:
      score += 1
      pipes.append(Pipe(600))
      if ai_playing:
        for genome in genome_list:
          genome.fitness += 5
    for pipe in remove_pipes:
      pipes.remove(pipe)
    for i, bird in enumerate(birds):
      if bird.y + bird.img.get_height() > floor.y or bird.y < 0:
        birds.pop(i)
        if ai_playing:
          genome_list.pop(i)
          neural_networks.pop(i)
    draw_game(screen, birds, pipes, floor, score)
    
def play(path_config):
  config = neat.config.Config(neat.DefaultGenome,
                              neat.DefaultReproduction,
                              neat.DefaultSpeciesSet,
                              neat.DefaultStagnation,
                              path_config)
  population = neat.Population(config)
  population.add_reporter(neat.StdOutReporter(True))
  population.add_reporter(neat.StatisticsReporter())
  if ai_playing:
    population.run(main, 50)
  else:
    main(None, None)
    
if __name__ == '__main__':
  path = os.path.dirname(__file__)
  path_config = os.path.join(path, 'config.txt')
  play(path_config)
