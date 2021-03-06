# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
import random

pygame.init()
pygame.mixer.init()

# ----- Gera tela principal
WIDTH = 480
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Navinha')

# ----- Inicia assets
METEOR_WIDTH = 50
METEOR_HEIGHT = 38
BIG_METEOR_HEIGHT = 115
BIG_METEOR_WIDTH  = 80
SMALL_METEOR_WIDTH = 25
SMALL_METEOR_HEIGHT = 20

SHIP_WIDTH = 50
SHIP_HEIGHT = 38
assets = {}
assets['background'] = pygame.image.load('assets/img/starfield.png').convert()
assets['meteor_img'] = pygame.image.load('assets/img/meteorBrown_med1.png').convert_alpha()
assets['meteor_img'] = pygame.transform.scale(assets['meteor_img'], (METEOR_WIDTH, METEOR_HEIGHT))
assets['big_meteor_img'] = pygame.image.load('assets/img/meteorBrown_big2.png').convert_alpha()
assets['big_meteor_img'] = pygame.transform.scale(assets['big_meteor_img'], (BIG_METEOR_WIDTH ,BIG_METEOR_HEIGHT))
assets['small_meteor_img'] = pygame.image.load('assets/img/meteorBrown_small1.png').convert_alpha()
assets['small_meteor_img'] = pygame.transform.scale(assets['small_meteor_img'], (SMALL_METEOR_WIDTH ,SMALL_METEOR_HEIGHT))
assets['ship_img'] = pygame.image.load('assets/img/playerShip1_orange.png').convert_alpha()
assets['ship_img'] = pygame.transform.scale(assets['ship_img'], (SHIP_WIDTH, SHIP_HEIGHT))
assets['bullet_img'] = pygame.image.load('assets/img/laserRed16.png').convert_alpha()

explosion_anim = []
for i in range(9):
    # Os arquivos de animação são numerados de 00 a 08
    filename = 'assets/img/regularExplosion0{}.png'.format(i)
    img = pygame.image.load(filename).convert()
    img = pygame.transform.scale(img, (32, 32))

    explosion_anim.append(img)

assets["explosion_anim"] = explosion_anim
assets["score_font"] = pygame.font.Font('assets/font/PressStart2P.ttf', 28)

# Carrega os sons do jogo
pygame.mixer.music.load('assets/snd/tgfcoder-FrozenJam-SeamlessLoop.ogg')
pygame.mixer.music.set_volume(0.4)
assets['boom_sound'] = pygame.mixer.Sound('assets/snd/expl3.wav')
assets['destroy_sound'] = pygame.mixer.Sound('assets/snd/expl6.wav')
assets['pew_sound'] = pygame.mixer.Sound('assets/snd/pew.wav')

# ----- Inicia estruturas de dados
# Definindo os novos tipos
class Ship(pygame.sprite.Sprite):
    def __init__(self, groups, assets):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.image = assets['ship_img']
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.groups = groups
        self.assets = assets
        
        # Só será possível atirar uma vez a cada 500 milissegundos
        self.last_shot = pygame.time.get_ticks()
        self.shoot_ticks = 300

    def update(self):
        # Atualização da posição da nave
        self.rect.x += self.speedx

        
        self.speedx = 0
        self.speedy = 0
        
        # Move a nave horizontalmente
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        
        # Move a nave verticalmente
        if keystate[pygame.K_UP]:
            self.speedy = -8
        if keystate[pygame.K_DOWN]:
            self.speedy = 8
        
        self.rect.x += self.speedx
        self.rect.y += self.speedy


        # Mantem dentro da tela
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        # Verifica se pode atirar
        now = pygame.time.get_ticks()
        # Verifica quantos ticks se passaram desde o último tiro.
        elapsed_ticks = now - self.last_shot

        # Se já pode atirar novamente...
        if elapsed_ticks > self.shoot_ticks:
            # Marca o tick da nova imagem.
            self.last_shot = now
            # A nova bala vai ser criada logo acima e no centro horizontal da nave
            new_bullet = Bullet(self.assets, self.rect.top, self.rect.centerx)
            self.groups['all_sprites'].add(new_bullet)
            self.groups['all_bullets'].add(new_bullet)
            self.assets['pew_sound'].play()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, assets):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        self.lives = 2
        self.dano = 2
        self.image_orig = assets['meteor_img']
        self.mask = pygame.mask.from_surface(self.image_orig)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .9 /2)
        #pygame.draw.circle(self.image_orig,(255,0,0),self.rect.center,self.radius)
        self.rect.x = random.randint(0, WIDTH-METEOR_WIDTH)
        self.rect.y = random.randint(-100, -METEOR_HEIGHT)
        self.speedx = random.randint(-3, 3)
        self.speedy = random.randint(2, 9)
        self.rot = 0
        self.rot_speed = random.randrange(-13,13)
        self.last_update = pygame.time.get_ticks()
    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    
    def update(self):
        # Atualizando a posição do meteoro
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Se o meteoro passar do final da tela, volta para cima e sorteia
        # novas posições e velocidades
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.rect.x = random.randint(0, WIDTH-METEOR_WIDTH)
            self.rect.y = random.randint(-100, -METEOR_HEIGHT)
            self.speedx = random.randint(-3, 3)
            self.speedy = random.randint(2, 9)

# Classe Bullet que representa os tiros

class Big_meteor(pygame.sprite.Sprite):
    def __init__(self, assets):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        self.lives = 3
        self.dano = 3
        self.image_orig = assets['big_meteor_img']
        self.mask = pygame.mask.from_surface(self.image_orig)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .9 /2)
        #pygame.draw.circle(self.image_orig,(255,0,0),self.rect.center,self.radius)
        self.rect.x = random.randint(0, WIDTH - BIG_METEOR_WIDTH)
        self.rect.y = random.randint(-BIG_METEOR_HEIGHT-10,-BIG_METEOR_HEIGHT)
        self.speedx = random.randint(-3, 3)
        self.speedy = random.randint(2, 9)
        self.rot = 0
        self.rot_speed = random.randrange(-8,8)
        self.last_update = pygame.time.get_ticks()


    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    
    def update(self):
        # Atualizando a posição do meteoro
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Se o meteoro passar do final da tela, volta para cima e sorteia
        # novas posições e velocidades
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.rect.x = random.randint(0, WIDTH-BIG_METEOR_WIDTH)
            self.rect.y = random.randint(-BIG_METEOR_HEIGHT-10,-BIG_METEOR_HEIGHT)
            self.speedx = random.randint(-3, 3)
            self.speedy = random.randint(2, 9)

class Small_Meteor(pygame.sprite.Sprite):
    def __init__(self, assets):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        self.lives = 1
        self.dano = 1
        self.image_orig = assets['small_meteor_img']
        self.mask = pygame.mask.from_surface(self.image_orig)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .9 /2)
        #pygame.draw.circle(self.image_orig,(255,0,0),self.rect.center,self.radius)
        self.rect.x = random.randint(0, WIDTH-SMALL_METEOR_WIDTH)
        self.rect.y = random.randint(-100, -SMALL_METEOR_HEIGHT)
        self.speedx = random.randint(-3, 3)
        self.speedy = random.randint(5, 13)
        self.rot = 0
        self.rot_speed = random.randrange(-13,13)
        self.last_update = pygame.time.get_ticks()
    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    
    def update(self):
        # Atualizando a posição do meteoro
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Se o meteoro passar do final da tela, volta para cima e sorteia
        # novas posições e velocidades
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.rect.x = random.randint(0, WIDTH-SMALL_METEOR_WIDTH)
            self.rect.y = random.randint(-100, - SMALL_METEOR_HEIGHT)
            self.speedx = random.randint(-3, 3)
            self.speedy = random.randint(2, 9)
   
class Bullet(pygame.sprite.Sprite):
    # Construtor da classe.
    def __init__(self, assets, bottom, centerx):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.image = assets['bullet_img']
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

        # Coloca no lugar inicial definido em x, y do constutor
        self.rect.centerx = centerx
        self.rect.bottom = bottom
        self.speedy = -10  # Velocidade fixa para cima

    def update(self):
        # A bala só se move no eixo y
        self.rect.y += self.speedy

        # Se o tiro passar do inicio da tela, morre.
        if self.rect.bottom < 0:
            self.kill()


# Classe que representa uma explosão de meteoro
class Explosion(pygame.sprite.Sprite):
    # Construtor da classe.
    def __init__(self, center, assets):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        # Armazena a animação de explosão
        self.explosion_anim = assets['explosion_anim']

        # Inicia o processo de animação colocando a primeira imagem na tela.
        self.frame = 0  # Armazena o índice atual na animação
        self.image = self.explosion_anim[self.frame]  # Pega a primeira imagem
        self.rect = self.image.get_rect()
        self.rect.center = center  # Posiciona o centro da imagem

        # Guarda o tick da primeira imagem, ou seja, o momento em que a imagem foi mostrada
        self.last_update = pygame.time.get_ticks()

        # Controle de ticks de animação: troca de imagem a cada self.frame_ticks milissegundos.
        # Quando pygame.time.get_ticks() - self.last_update > self.frame_ticks a
        # próxima imagem da animação será mostrada
        self.frame_ticks = 50

    def update(self):
        # Verifica o tick atual.
        now = pygame.time.get_ticks()
        # Verifica quantos ticks se passaram desde a ultima mudança de frame.
        elapsed_ticks = now - self.last_update

        # Se já está na hora de mudar de imagem...
        if elapsed_ticks > self.frame_ticks:
            # Marca o tick da nova imagem.
            self.last_update = now

            # Avança um quadro.
            self.frame += 1

            # Verifica se já chegou no final da animação.
            if self.frame == len(self.explosion_anim):
                # Se sim, tchau explosão!
                self.kill()
            else:
                # Se ainda não chegou ao fim da explosão, troca de imagem.
                center = self.rect.center
                self.image = self.explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Variável para o ajuste de velocidade
clock = pygame.time.Clock()
FPS = 30

# Criando um grupo de meteoros
all_sprites = pygame.sprite.Group()
all_meteors = pygame.sprite.Group()
all_bullets = pygame.sprite.Group()
groups = {}
groups['all_sprites'] = all_sprites
groups['all_meteors'] = all_meteors
groups['all_bullets'] = all_bullets

# Criando o jogador
player = Ship(groups, assets)
all_sprites.add(player)
# Criando os meteoros
for i in range(4):
    meteor = Meteor(assets)
    all_sprites.add(meteor)
    all_meteors.add(meteor)

DONE = 0
PLAYING = 1
EXPLODING = 2
GAMEOVER= 3
state = PLAYING

keys_down = {}
score = 0
lives = 5


# ===== Loop principal =====
pygame.mixer.music.play(loops=-1)
while state != DONE and state != GAMEOVER:
    clock.tick(FPS)

    # ----- Trata eventos
    for event in pygame.event.get():
        # ----- Verifica consequências
        if event.type == pygame.QUIT:
            state = DONE
        # Só verifica o teclado se está no estado de jogo
        if state == PLAYING:
            # Verifica se apertou alguma tecla.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
            # Verifica se soltou alguma tecla.
            

    # ----- Atualiza estado do jogo
    # Atualizando a posição dos meteoros
    all_sprites.update()

    if state == PLAYING:
        # Verifica se houve colisão entre tiro e meteoro
        hits = pygame.sprite.groupcollide(all_meteors, all_bullets, False, True, pygame.sprite.collide_mask)
        for meteor in hits: # As chaves são os elementos do primeiro grupo (meteoros) que colidiram com alguma bala
            # O meteoro e destruido e precisa ser recriado
            meteor.lives -= 1
            if meteor.lives == 0:
                meteor.kill()
                m = Meteor(assets)
                all_sprites.add(m)
                all_meteors.add(m)
                assets['destroy_sound'].play()

            # No lugar do meteoro antigo, adicionar uma explosão.
                explosao = Explosion(meteor.rect.center, assets)
                all_sprites.add(explosao)

            # Ganhou pontos!
                score += 100
                if score % 2000 == 0:
                    lives += 1
            
            # Impõe limite maximo de tres vidas
                if lives > 5:
                    lives = 5 
            
            # Adiciona um novo meteoro a cada 5000 pontos 
                if score % 5000 == 0:
                    m = Meteor(assets)
                    all_sprites.add(m)
                    all_meteors.add(m)

                if score % 900 == 0:
                    bm = Big_meteor(assets)
                    all_sprites.add(bm)
                    all_meteors.add(bm)
                
                if score % 200 == 0:
                    sm = Small_Meteor(assets)
                    all_sprites.add(sm)
                    all_meteors.add(sm)
        # Verifica se houve colisão entre nave e meteoro
        hits = pygame.sprite.spritecollide(player, all_meteors, True, pygame.sprite.collide_mask)
        if len(hits) > 0:
            # Toca o som da colisão
            assets['boom_sound'].play()
            m = Meteor(assets)
            all_sprites.add(m)
            all_meteors.add(m)
            player.kill()
            lives -= meteor.dano
            explosao = Explosion(player.rect.center, assets)
            all_sprites.add(explosao)
            state = EXPLODING
            keys_down = {}
            explosion_tick = pygame.time.get_ticks()
            explosion_duration = explosao.frame_ticks * len(explosao.explosion_anim) + 400
    elif state == EXPLODING:
        now = pygame.time.get_ticks()
        if now - explosion_tick > explosion_duration:
            if lives <= 0:
                state = DONE
            else:
                state = PLAYING
                player = Ship(groups, assets)
                all_sprites.add(player)

    # ----- Gera saídas
    window.fill((0, 0, 0))  # Preenche com a cor branca
    window.blit(assets['background'], (0, 0))
    # Desenhando meteoros
    all_sprites.draw(window)

    # Desenhando o score
    text_surface = assets['score_font'].render("{:08d}".format(score), True, (255, 255, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (WIDTH / 2,  10)
    window.blit(text_surface, text_rect)

    # Desenhando as vidas
    text_surface = assets['score_font'].render(chr(9829) * lives, True, (255, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.bottomleft = (10, HEIGHT - 10)
    window.blit(text_surface, text_rect)

    pygame.display.update()  # Mostra o novo frame para o jogador
# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados