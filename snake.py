import pygame
import random
import datetime

class Game:

    STATE_PLAYING = 0
    STATE_MENU = 1
    STATE_DYING = 2

    DIRECTIONS = {
        "u": [0, -1],
        "d": [0, 1],
        "l": [-1, 0],
        "r": [1, 0]
    }

    def __init__(self, height, width, grid_scale):
        pygame.init()
        #initialisation
        self.win = pygame.display.set_mode((width*grid_scale, height*grid_scale)) 
        pygame.display.set_caption("Snake")
    
        self.height = height
        self.width = width
        self.grid_scale = grid_scale
        self.frame_count = 0

        #changement des ressources
        self.load_resources()        

        #initilisation états
        self.reset_game()

        self.state = self.STATE_PLAYING

        self.menu_selection = 0

        self.running = True

        self.play_pos = ((self.width//8)*self.grid_scale, (self.height//5)*self.grid_scale)
        self.quit_pos = ((self.width//8)*self.grid_scale, ((self.height//2)+(self.height//5))*self.grid_scale)
        self.scr_pos1 = ((self.width//2 + self.width//14)*self.grid_scale, (self.height//10)*self.grid_scale)
        self.scr_pos2 = ((self.width//2 + self.width//6)*self.grid_scale, (self.height//10)*self.grid_scale)
        self.score_pos = ((self.width//2 + self.width//3)*self.grid_scale, (self.height//10)*self.grid_scale)

    def load_resources(self):
        self.slurp_noise0 = pygame.mixer.Sound("slurp0.wav")
        self.slurp_noise1 = pygame.mixer.Sound("slurp1.wav")
        self.death_noise = pygame.mixer.Sound("death.wav")

        self.wall_render = pygame.image.load("tile1.png")
        self.wall_render = pygame.transform.scale(self.wall_render,(self.grid_scale, self.grid_scale))

        self.wall_corner = pygame.image.load("tile0.png")
        self.wall_corner = pygame.transform.scale(self.wall_corner,(self.grid_scale, self.grid_scale))

        self.apple_render = pygame.image.load("apple.png")
        self.apple_render = pygame.transform.scale(self.apple_render,(self.grid_scale, self.grid_scale))

        self.snake_head_closed_render = pygame.image.load("snake_head_closed.png")
        self.snake_head_closed_render = pygame.transform.scale(self.snake_head_closed_render,(self.grid_scale, self.grid_scale))

        self.snake_head_open_render = pygame.image.load("snake_head_open.png")
        self.snake_head_open_render = pygame.transform.scale(self.snake_head_open_render,(self.grid_scale, self.grid_scale))

        self.snake_tail0_render = pygame.image.load("snake_tail0.png")
        self.snake_tail0_render = pygame.transform.scale(self.snake_tail0_render,(self.grid_scale, self.grid_scale))

        self.snake_tail1_render = pygame.image.load("snake_tail1.png")
        self.snake_tail1_render = pygame.transform.scale(self.snake_tail1_render,(self.grid_scale, self.grid_scale))

        self.snake_tail2_render = pygame.image.load("snake_tail2.png")
        self.snake_tail2_render = pygame.transform.scale(self.snake_tail2_render,(self.grid_scale, self.grid_scale))

        self.font0 = pygame.font.SysFont("Courrier New", 4*self.grid_scale)
        self.font1 = pygame.font.SysFont("Courrier New", 3*self.grid_scale)
        self.font2 = pygame.font.SysFont("Courrier New", 2*self.grid_scale)

    def pick_rd_pos(self):
        x = random.randint(1, self.width - 2)
        y = random.randint(1, self.height - 2)
        for [sx, sy] in self.snake_pos:
            if sx == x and sy == y:
                return self.pick_rd_pos()
        return [x, y]

    def run(self): # permet de jouer au jeu, le lance
        self.reset_game()
        while self.running:
            pygame.time.delay(100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.frame_count += 1
            if self.state == self.STATE_PLAYING:
                self.update_playing()
                self.render_playing()

            elif self.state == self.STATE_DYING:
                self.update_dying()
                self.render_dying()

            elif self.state == self.STATE_MENU:
                self.update_menu()
                self.render_menu()

        pygame.quit() 
    
    def update_playing(self): 
        keys = pygame.key.get_pressed()  

        # gestion des entrées utilisateur
        if keys[pygame.K_LEFT] and self.dir != "r":
            self.dir = "l"

        elif keys[pygame.K_RIGHT] and self.dir != "l":
            self.dir = "r"

        elif keys[pygame.K_UP] and self.dir != "d":
            self.dir = "u"

        elif keys[pygame.K_DOWN] and self.dir != "u":
            self.dir = "d"

        # logique du fruit
        if self.snake_pos[0][0] == self.fruit_pos[0] and self.snake_pos[0][1] == self.fruit_pos[1]:
            noise = random.randint(0, 1)
            if noise == 0:
                self.slurp_noise0.play()
            else:
                self.slurp_noise1.play()
            self.snake_pos.append(self.snake_pos[len(self.snake_pos) - 1].copy())
            self.fruit_pos = self.pick_rd_pos()

        # mise à jour de la position
        for i in range (len(self.snake_pos) - 1, 0, -1):
            self.snake_pos[i] = self.snake_pos[i - 1].copy()

        delta = self.DIRECTIONS[self.dir]
        self.snake_pos[0][0] += delta[0]
        self.snake_pos[0][1] += delta[1]

        # collision serpent-mur
        if self.snake_pos[0][0] == 0 or self.snake_pos[0][0] == self.width-1 or self.snake_pos[0][1] == 0 or self.snake_pos[0][1] == self.height -1:
            self.death_noise.play()
            self.state = self.STATE_DYING
            self.append_score(len(self.snake_pos))
            return

        # collision serpent-serpent
        for i in range(1,len(self.snake_pos)):
            if self.snake_pos[0][0] == self.snake_pos[i][0] and self.snake_pos[0][1] == self.snake_pos[i][1]:
                self.death_noise.play()
                self.state = self.STATE_DYING
                self.append_score(len(self.snake_pos))
                return

    def render_playing(self):
        self.win.fill((255,255,255)) 

        #mur
        self.render_wall()
        self.win.blit(self.apple_render, (self.fruit_pos[0]*self.grid_scale, self.fruit_pos[1]*self.grid_scale))
        
        self.render_snake()
        
        #score
        score = self.font0.render(str(len(self.snake_pos)-2), True, (200,0,200))
        self.win.blit(score, self.score_pos)

        pygame.display.update()

    def render_snake(self):
        SNAKE_BODY_SPRITES = {
            ((0,1),(0,-1)): (self.snake_tail0_render, 90),
            ((0,-1),(0,1)): (self.snake_tail0_render, 90),

            ((0,1),(1,0)): (self.snake_tail1_render, 180),
            ((1,0),(0,1)): (self.snake_tail1_render, 180),

            ((0,-1),(1,0)): (self.snake_tail1_render, -90),
            ((1,0),(0,-1)): (self.snake_tail1_render, -90),

            ((-1,0),(1,0)): (self.snake_tail0_render, 0),
            ((1,0),(-1,0)): (self.snake_tail0_render, 0),
            
            ((-1,0),(0,-1)): (self.snake_tail1_render, 0),
            ((0,-1),(-1,0)): (self.snake_tail1_render, 0),
            
            ((-1,0),(0,1)): (self.snake_tail1_render, 90),
            ((0,1),(-1,0)): (self.snake_tail1_render, 90),
        }

        SNAKE_HEAD_SPRITES = {
            (0,1): -90,
            (-1,0): 180,
            (0,-1): 90,
            (1,0): 0
        }

        for i in range (1, len(self.snake_pos)-1, 1):
            n_i_m = tuple(self.snake_pos[i-1])
            n_i_p = tuple(self.snake_pos[i+1])
            delta1 = (self.snake_pos[i][0]-self.snake_pos[i+1][0], self.snake_pos[i][1]-self.snake_pos[i+1][1])
            delta2 = (self.snake_pos[i][0]-self.snake_pos[i-1][0], self.snake_pos[i][1]-self.snake_pos[i-1][1])
            sprite, rotation = SNAKE_BODY_SPRITES[delta1,delta2]
            img = pygame.transform.rotate(sprite, rotation)
            self.win.blit(img, (self.snake_pos[i][0]*self.grid_scale, self.snake_pos[i][1]*self.grid_scale))
        
        #tete
        id = 0
        delta = (self.snake_pos[id][0]-self.snake_pos[id+1][0], self.snake_pos[id][1]-self.snake_pos[id+1][1])
        rotation = SNAKE_HEAD_SPRITES[delta]
        if self.frame_count % 2 == 0:
            sprite = self.snake_head_closed_render
        else:
            sprite = self.snake_head_open_render

        img = pygame.transform.rotate(sprite, rotation)
        self.win.blit(img, (self.snake_pos[id][0]*self.grid_scale, self.snake_pos[id][1]*self.grid_scale))

        #queue
        id = len(self.snake_pos)-1
        delta = (self.snake_pos[id-1][0]-self.snake_pos[id][0], self.snake_pos[id-1][1]-self.snake_pos[id][1])
        rotation = SNAKE_HEAD_SPRITES[delta]
        img = pygame.transform.rotate(self.snake_tail2_render, rotation)
        self.win.blit(img, (self.snake_pos[id][0]*self.grid_scale, self.snake_pos[id][1]*self.grid_scale))

    def render_wall(self):
        sprite = pygame.transform.rotate(self.wall_render, 90)
        for i in range (1, self.height - 1, 1):
            self.win.blit(sprite, (0, i*self.grid_scale))
        sprite = pygame.transform.rotate(self.wall_render, -90)
        for i in range (1, self.height - 1, 1):
            self.win.blit(sprite, ((self.width-1)*self.grid_scale, i*self.grid_scale))
        sprite = pygame.transform.rotate(self.wall_render, 0)
        for i in range (1, self.width - 1, 1):
            self.win.blit(sprite, (i*self.grid_scale, 0))
        sprite = pygame.transform.rotate(self.wall_render, 180)
        for i in range (1, self.width - 1, 1):
            self.win.blit(sprite, (i*self.grid_scale, (self.height-1)*self.grid_scale))

        self.win.blit(pygame.transform.rotate(self.wall_corner, 90), (0, 0))
        self.win.blit(pygame.transform.rotate(self.wall_corner, 180), (0, self.grid_scale*(self.height-1)))
        self.win.blit(pygame.transform.rotate(self.wall_corner, 0), (self.grid_scale*(self.width-1), 0))
        self.win.blit(pygame.transform.rotate(self.wall_corner, -90), (self.grid_scale*(self.width-1), self.grid_scale*(self.height-1)))

    def update_dying(self):
        if len(self.snake_pos)>2:
            self.snake_pos.pop()
        else:
            self.state = self.STATE_PLAYING
            self.reset_game()
    
    def reset_game(self):
        self.snake_pos = [[1, 1],[0, 1]] #heigth puis height
        self.dir = "r"
        self.fruit_pos = self.pick_rd_pos()
        self.state = self.STATE_MENU

    def render_dying(self):
        self.win.fill((255,255,255)) 
        self.render_wall()
        self.render_snake()
        pygame.display.update()

    def update_menu(self):
        keys = pygame.key.get_pressed()  

        # gestion des entrées utilisateur
        if keys[pygame.K_UP] :
            self.menu_selection = 0
        elif keys[pygame.K_DOWN]:
            self.menu_selection = 1
        elif keys[pygame.K_RETURN]:
            if self.menu_selection == 0 :
                self.state = self.STATE_PLAYING
            else:
                self.running = False

    def render_menu(self):
        self.win.fill((255,255,255)) 
        
        # affichage sélection 
        play_str = "  PLAY"
        if self.menu_selection == 0:
            play_str = "> PLAY"
        quit_str = "  QUIT"
        if self.menu_selection == 1:
            quit_str = "> QUIT"
        play_txt = self.font0.render(play_str, True, (200,0,200))
        quit_txt = self.font0.render(quit_str, True, (200,0,200))

        self.win.blit(play_txt, self.play_pos)
        self.win.blit(quit_txt, self.quit_pos)

        # affichage séparation 

        #t^ete
        head_pos = ((self.width//2)*self.grid_scale, self.grid_scale)
        img = pygame.transform.rotate(self.snake_head_open_render, 90)
        self.win.blit(img, head_pos)

        #corps
        for i in range (2, self.height - 1):
            body_pos = ((self.width//2)*self.grid_scale, i*self.grid_scale)
            img = pygame.transform.rotate(self.snake_tail0_render, 90)
            self.win.blit(img, body_pos)

        #queue
        queue_pos = ((self.width//2)*self.grid_scale, (self.height - 1)*self.grid_scale)
        img = pygame.transform.rotate(self.snake_tail2_render, 90)
        self.win.blit(img, queue_pos)

        #affichage scores
        scores = self.fetch_score()
        scr = self.font1.render("Meilleurs scores:", True, (200,0,200))
        self.win.blit(scr, self.scr_pos1)

        for i in range (len(scores)-1, 0, -1):
            sco = scores[i].split(" ")
            scr = self.font2.render(sco[0]+"     "+sco[1], True, (200,0,200))
            self.win.blit(scr, (self.scr_pos2[0],self.scr_pos2[1] + 2*(len(scores)-i+1)*self.grid_scale))

        pygame.display.update()

    def append_score(self, score):
        scores = self.fetch_score()
        scores.append(f"{str(score-2)} {datetime.datetime.now()}")
        self.sort_score(scores)
        if len(scores)>10:
            scores.pop(0)
        self.save_score(scores)
            
    def sort_score(self, scores):
        scores.sort(key=lambda x: int((x.split(" ")[0])) )

    def fetch_score(self):
        score = []
        with open("score.txt", mode = "r") as file:
            lines = file.read().split("\n")
            for line in lines:
                if len(line) == 0:
                    continue
                score.append(line)
        return score

    def save_score(self, scores):
        with open("score.txt", mode = "w") as file:
            for score_str in scores:
                file.write(score_str + "\n")

def main() :
    game = Game(25, 40, 32)
    game.run()

if __name__ == "__main__":
    main()