

#self.tetris_o

#have to add the stopping function + test


import pygame
import sys
import widgets
from pygame import Color,Rect
from random import randint, choice
from pygame.sprite import Sprite
from math import ceil

#tetris_items as in the pygame repere
tetris_items=([[0,2],[0,1],[0,-1]], #I shape
              [[0,1],[0,-1],[-1, 1]], #J shape
              [[0,1],[0,-1],[1,1]], #L shape
              [[0,1],[-1,1],[-1,0]], #o shape
              [[1,0],[0,1],[-1,1]], #S shape
              [[-1,0],[0,1],[1,1]], #Z shape
              [[1,0],[-1,0],[0,1]] #T shape
    )

class block(Sprite):
    def __init__(self,surface_object,pos,color,speed,gridsize, widgets):
        """Pos is the position of the block relative to a center block
           in tbock object for instance let _+_ be a tobj
           in this case the + is the center block and _ has coordinate (-1,0) (1,0)
           speed is the speed that the block has without user input
        """
        Sprite.__init__(self)
        self.surface_object=surface_object
        self.pos = pos
        self.color = color
        self.speed = speed
        self.gridsize = gridsize
        self.widget = widgets
        self.rect = widgets.get_internal_rect()
        self.x, self.y = self.rect.topleft
        self.x2, self.y2 = self.rect.bottomright
        #real position to be used after killed
        self.real_pos = None

    def draw(self,position_of_center = None):
        """Function that draws the block"""
        if position_of_center:
            position = [position_of_center[0]+self.pos[0]*self.gridsize,position_of_center[1]+self.pos[1]*self.gridsize]
        else:
            position = self.real_pos
        pygame.draw.rect(self.surface_object,self.color,(position[0],position[1],self.gridsize,self.gridsize))


    def get_pos(self):
        """Returns the relative pos"""
        return self.pos

    def xy_to_n(self,position_of_center):
        """Turns coordinates from reel to gridsize, position of center must be given in coordinate of gridsize"""
        self.gridsize_pos = list(position_of_center)
        self.pos = self.get_pos()
        self.gridsize_pos[0] += self.pos[0]
        self.gridsize_pos[1] += self.pos[1]
        return self.gridsize_pos

    def set_real_pos(self, position_of_center):
        #position of center in realsize
        # this function is used when tobj becomes idle so that we can give the draw function
        # the self.real_pos as argument
        self.real_pos = [position_of_center[0] + (self.pos[0] * self.gridsize), position_of_center[1] + (self.pos[1] * self.gridsize)]
        self.pos = [0, 0]

    def get_real_pos_n(self):
        posx = (self.real_pos[0] - self.x) / self.gridsize
        posy = (self.real_pos[1] - self.y) / self.gridsize
        assert (posx == int(posx), "Float value of posx in get_real_pos_n does not match its integer value")
        assert (posy == int(posy), "Float value of posy in get_real_pos_n does not match its integer value")
        return int(posx), int(posy)

class tobj(object):
    def __init__(self,surface_object,holder_class,color, nrows ,ncols ,gridsize ,widgets,direction=0):
        """surface_object: surface to draw to
           widget: widget in wich the game is played
           center_pos is the position of the center block
            """
        self.surface_object = surface_object
        self.widget = widgets

        self.holder = holder_class

        self.rect = widgets.get_internal_rect()
        self.x, self.y = self.rect.topleft
        self.x2, self.y2 = self.rect.bottomright

        self.nrows = nrows
        self.ncols = ncols
        self.gridsize = gridsize

        self.states = ["Alive", "Dying", "Idle","stored"]
        self.State = "Alive" #3 possible values Alive Dying Idle,  Dying when the block has reached the bottom the user can still move left or right for a small time, Idle block can't be moved anymore, stored i.e block is in the holder class
        self.blocks_pos = choice(tetris_items) #tetris blocks
        self.color = color
        self.direction = direction
        self.speed = 1 #in gridsize per second
        self.user_speed = 1 #in gridsize per second
        self.time = 500
        self.death_timer = self.time #in seconds the time that the user still has to move the block

        Center = block(self.surface_object,[0,0], self.color, self.speed, self.gridsize, self.widget)

        self.tetris_o = pygame.sprite.Group()


        for i in range(len(self.blocks_pos)):
        #Create the tetris block
            a = block(self.surface_object, self.blocks_pos[i], self.color, self.speed, self.gridsize, self.widget)
            self.tetris_o.add(a)

        max_y = self.get_down_coord()
        max_x = self.get_right()
        min_x = self.get_left()

        posx = randint(1, ncols-1)*self.gridsize + self.x
        posy = self.y

        if posx + max_x * self.gridsize > (self.x2 - self.gridsize) or posx + min_x*self.gridsize < self.x :
            if posx + max_x * self.gridsize > (self.x2 - self.gridsize):
                posx -= max_x * self.gridsize
            else:
                posx -= min_x*self.gridsize

        if max_y > 0:
            posy -= (max_y)*self.gridsize

        self.center_pos = [posx, posy] #pos of center in real coord
        self.tetris_o.add(Center)

    def can_rotate_counter_c(self):
        """check if can rotate anti_clockwise"""
        left_m = self.get_left()
        #left_m becomes the most bottom coord (the highest in pygame coord)

        #we have to check if there is empty space under the block then
        #Check if there is empty space below
        left_m -= self.gridsize
        if not self.can_move_d(left_m):
            #print "1"
            return False

        down_m = self.get_down_coord()
        #down_m becomes the rightmost coord
        down_m -= self.gridsize
        if not self.can_move_r(down_m):
            #print "2"
            return False
        #print "can rotate_a"
        return True

    def can_rotate_c(self):
        """check if can rotate clockwise"""
        right_m = self.get_right()
        right_m -= self.gridsize
        # Right m becomes the most bottom block
        if not self.can_move_d(right_m):
            return False

        up_m = self.get_up_coord()
        up_m -= self.gridsize
        #up most block becomes the rightmost block
        if not self.can_move_r(up_m):
            return False

        return True

    def can_move_l(self, left_m = None):
        """Function to see if block can move left by one"""
        if not left_m:
            left_m = self.get_left()
        pos = left_m*self.gridsize + self.center_pos[0]
        if pos - self.x >= self.gridsize:
            pass
        else:
            return False
        for object in self.tetris_o:
            posx, posy = object.xy_to_n(self.xy_to_n())
            if self.holder.holder_pos[posx-1][posy]:
                return False
        return True

    def can_move_r(self, right_m = None):
        """Function to see if block can move right by one"""
        if not right_m:
            right_m = self.get_right()
        pos = right_m*self.gridsize + self.center_pos[0]
        if self.x2 - pos > self.gridsize:
            pass
        else:
            return False
        for object in self.tetris_o:
            posx, posy = object.xy_to_n(self.xy_to_n())

            if self.holder.holder_pos[posx + 1][posy]:
                return False
        return True

    def can_move_d(self, down_coord = None): #THis func needs to be update it with the values in holder class
        """Function to see if block can move down by one, if used by can_rotate
           down_coord is passed as an argument (it is the future lowest block after a rotation) """
        if not down_coord:
            down_coord = self.get_down_coord()
        pos = down_coord*self.gridsize + self.center_pos[1]
        if self.y2 - pos > self.gridsize:
            pass
        else:
            self.State = self.states[1]
            return False
        for object in self.tetris_o:
            posx, posy = object.xy_to_n(self.xy_to_n())
            if posy < 0:
                continue
            if self.holder.holder_pos[posx][posy + 1]: # check pos directly under
                self.State = self.states[1]
                return False
        return True

    def draw(self):
        for blah in self.tetris_o:
            blah.draw(self.center_pos)

    def dying(self, time_passed): #Time passed must be given in seconds not milliseconds
        self.death_timer -= time_passed
        if self.death_timer < 0:
            self.State = self.states[2]

    def get_left(self):
        """Get the relative coord of the leftmost block in grids coord"""
        min = 0
        for block in self.tetris_o:
            pos = block.get_pos()[0]
            if min > pos:
                min = pos
        return min

    def get_right(self):
        """Get the relative coord of the rightmost block in grids coord"""
        max = 0
        for block in self.tetris_o:
            pos = block.get_pos()[0]
            if max < pos:
                max = pos
        return max

    def get_down_coord(self):  # Remember the most bottom block has the max coord in the Pygame coord.
        """Get the relative coord of the most bottom block in grids coord"""
        max = 0
        for block in self.tetris_o:
            pos = block.get_pos()[1]
            if max < pos:
                max = pos

        return max

    def get_up_coord(self):  # Remember the highest block has the lowest y coord in the pygame coord
        """Get the relative coord of the highest block in gridcoord"""
        min = 0
        for block in self.tetris_o:
            pos = block.get_pos()[1]
            if min > pos:
                min = pos

        return min

    def kill(self):
        """Store the tetris block in class holder"""
        pos = self.xy_to_n()
        for sprite in self.tetris_o:
                position = sprite.xy_to_n(pos)
                sprite.set_real_pos(self.center_pos)
                self.holder.holder_pos[position[0]][position[1]] = True
                self.holder.holder_sprite.add(sprite)
        self.State = self.states[3]
        self.tetris_o.empty()

    def rotate_counter_c(self):
        """Rotate counter_clockwise using euler definition exp(ik)
           counter_c rotation is a rotation by -90 in the pygame coord,
           i.e: Transformation from  cosk + isink into ==>  sink -icosk
           then switch x = y and y =-x"""
        if not self.can_rotate_counter_c():
            return None #exit the function

        for block in self.tetris_o:
            a = block.pos[0]
            b = block.pos[1]
            block.pos[0] = b
            block.pos[1] = -a

    def reset(self):
        self.death_timer = self.time
        self.State = self.states[0]

    def rotate_clockwise(self):
        """Rotate clockwise using euler definition exp(iK)
           clockwise rotation is a rotation by +90 in the pygame coord, cos90 =0 sin 90 =1
           then y = x and x = -y"""
        if not self.can_rotate_c():
            return None #exit the function

        for block in self.tetris_o:
            a = block.pos[0]
            b = block.pos[1]
            block.pos[0] = -b
            block.pos[1] = a

    def update(self, time_passed): # have to add a lot of stuff
        """Updates the tetris obj moves them by the correct margin"""
        time_passed1 = ceil(float(time_passed) / 1000)
        if self.can_move_d():
            self.reset()
        #if self.State == self.states[0]:
            self.center_pos[1] += self.speed * self.gridsize * time_passed1
        elif self.State == self.states[1]:
            self.dying(time_passed)
        else:
            self.kill()

    def move_horiz(self, value):
        """moves left or right according to user input

           value 1 or positive for right value negative or -1
           for left"""
        if value > 0:
            value = 1
            if not self.can_move_r():
                return None # exit the function
        elif value < 0:
            value = -1
            if not self.can_move_l():
                return None #exit the function
        else:
            return None

        self.center_pos[0] += value*self.user_speed*self.gridsize

    def move_vertical(self):
        if self.can_move_d():
            self.center_pos[1] += self.user_speed*self.gridsize

    def xy_to_n(self):
        """Turns coordinates from reel to gridsize"""
        pos = list(self.center_pos)
        pos[0] = float((self.center_pos[0] - self.x) / self.gridsize)
        pos[1] = float ((self.center_pos[1]- self.y) / self.gridsize)
        if int(pos[0])!= pos[0] or int(pos[1]) != pos[1]:
            raise ValueError
        else:
            return [int(pos[0]),int(pos[1])]

class holder(object): #A class to track the idle tblocks
    def __init__(self, ncol, nrow, gridsize):
        self.holder_pos = [] #list either true or false true when there exist a block at specific pos

        self.holder_sprite = pygame.sprite.Group() # list that holds the block
        self.ncol = ncol
        self.nrow = nrow
        self.gridsized = gridsize

    def generate_empty(self):
        self.holder_pos = []
        #self.holder_sprite = []
        for col in range(self.ncol):
            self.holder_pos.append(self.nrow * [False])   #so that I can test with self.holder_pos[posx][posy]-
            #self.holder_sprite.append(self.nrow*[False])
            #self.holder_sprite.append([self.nrow*None]) THis isn't necessary

    def generate_full(self):#For testing purposes
        self.holder_pos = []
        for col in range(self.ncol):
            self.holder_pos.append(self.nrow * [True])

    #j is nrow
    def check_row(self, j):
        for i in range(self.ncol):
            if self.holder_pos[i][j] == False:
                return False
        else:
            return True

    def flash(self, i, row):
        # Function to be used in a for loop to flash the sprite in the given row
        color = Color(i, 255, i)
        for sprite in self.generate_sprite_row(row):
            sprite.color = color

    def generate_sprite_row(self, row):
        for sprite in self.holder_sprite:
            if sprite.get_real_pos_n()[1] == row:
                yield sprite

    def draw(self):
        for sprite in self.holder_sprite:
            sprite.draw()

    def kill_row(self, row):
        for sprite in self.generate_sprite_row(row):
            pos = sprite.get_real_pos_n()
            self.holder_sprite.remove(sprite)
            self.holder_pos[pos[0]][pos[1]] = False

        for row_choice in range(row):
            for sprite in self.generate_sprite_row(row_choice):
                pos1 = sprite.get_real_pos_n()
                sprite.real_pos[1] += self.gridsize
                pos2 = sprite.get_real_pos_n()
                self.holder_pos[pos1[0]][pos1[1]] = False
                self.holder_pos[pos2[0]][pos2[1]] = True



if __name__== "__main__":
    pygame.init()
    SCREEN_W,SCREEN_H = 500, 500
    screen = pygame.display.set_mode((SCREEN_W,SCREEN_H), 0, 32)

    clock = pygame.time.Clock()

    boxx,boxy = 100, 100
    box_w, box_h = 200, 300
    box = widgets.Box(screen,Rect(boxx , boxy , box_w , box_h),Color('white'))

    black_box = widgets.Box(screen, Rect(0, 0, SCREEN_W, boxy),Color('black')) # widget so that blocks that are above box won't appear

    Gridsize=10
    nrows = box_h/Gridsize
    ncols = box_w/Gridsize

    holder_class = holder(ncols, nrows, Gridsize)
    holder_class.generate_empty()
    blah = tobj(screen, holder_class, Color("green"), nrows, ncols, Gridsize, box)

    gridlines = widgets.grid(screen,box,Gridsize)

    #Main game loop
    while True:
        if blah.State == blah.states[2]:
            blah.kill()

            blah = tobj(screen, holder_class, Color('green'), nrows, ncols, Gridsize, box)
        time_passed = clock.tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    blah.move_vertical()
                elif event.key == pygame.K_a:
                    blah.move_horiz(-1)
                elif event.key == pygame.K_d:
                    blah.move_horiz(1)
                elif event.key == pygame.K_e:
                    blah.rotate_clockwise()
                elif event.key == pygame.K_q:
                    blah.rotate_counter_c()
        #list = pygame.key.get_pressed()

        for i in range(nrows):
           if holder_class.check_row(i):
               for j in range(0,255, 10):
                   holder_class.flash(j, i)
                   holder_class.draw()
                   pygame.display.flip()
               for j in range(255, -1, -10):
                   holder_class.flash(j, i)
                   holder_class.draw()
                   pygame.display.flip()
               holder_class.kill_row(i)



        box.draw()
        holder_class.draw()
        blah.update(time_passed)
        #blah.move_vertical()
        blah.draw()
        gridlines.draw_grid()
        black_box.draw()

        pygame.display.flip()



