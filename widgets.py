import pygame
from pygame import Rect, Color
import sys


class Box(object):
    """Widget that contains special boxes for the game,such as the
        game box, the next_piece box,and the tetris sign"""
    def __init__(self,surface,rect,bgcolor,border_color=(0,0,0),border_width=0):
        self.surface=surface
        self.rect=rect
        self.bgcolor=bgcolor
        self.border_color=border_color
        self.border_width=border_width
        """
            Surface: The surface on wich we blit our images
            Rect: outer rect
            border: The border around our inner rect.Border+inner_rect=outer_rect
        """
        self.inner_rect=Rect(self.rect.left + self.border_width,
            self.rect.top+self.border_width,
            self.rect.width-border_width,self.rect.height-border_width)

    def draw(self):
        pygame.draw.rect(self.surface,self.border_color,self.rect)
        pygame.draw.rect(self.surface,self.bgcolor,self.rect)

    def get_internal_rect(self):
        """
        The internal rect of the box.
        """
        return self.inner_rect


class Messagebox(object):
    """Widget that contains textbox that have special utilities such as a
       pause button or restart"""
    def __init__(self,surface,x_y,text,font=('arial', 20),font_color=Color('red'),bgcolor=Color('gray25'),border_width=0,border_color=Color('black')):
        """ surface,bgcolor,border_width,border_color same meaning as in the Box widget.
            x_y=xy coord of top left of text rect
            text: the text to be displayed
            value:  True = button clicked
                    False = button unclicked
        """

        self.surface = surface
        self.x_y = x_y
        self.text = text
        self.font = pygame.font.SysFont(*font)
        self.font_color = font_color
        self.bgcolor = bgcolor
        self.border_width=border_width
        self.border_color=border_color
        self.value=False

    def draw(self):
        #First draw container rect,then draw text rect inside it
        self.text_surface= self.font.render(self.text, True,self.font_color,self.bgcolor)
        self.text_size=self.text_surface.get_size()
        container_rect=Rect(self.x_y[0]-self.border_width,self.x_y[1] - self.border_width,self.text_size[0] + self.border_width,self.text_size[1]+self.border_width)
        container_rect.top=self.x_y[1]
        container_rect.left=self.x_y[0]
        self.text_dest=self.x_y+(self.border_width,self.border_width)

        pygame.draw.rect(self.surface,self.border_color,container_rect)
        self.surface.blit(self.text_surface,self.text_dest)


    def collide(self,coord):
        """Check if coord are inside the rect"""
        if self.text_rect.collidepoint(coord):
            return True

    def get_val(self):

        #Return the clicked or unclicked value
        return self.value

    def change_val(self):
        self.value= not self.value


class grid(object):
    def __init__(self,surface_object,widget,gridsize):
        """
           surface_object the pygame  window
           widget: the game area from class widgets
           gridsize cell size
        """
        self.surface_object=surface_object
        self.widget=widget
        self.gridsize=gridsize

        self.rect = self.widget.get_internal_rect()
        self.nrows=float(self.rect.height/self.gridsize)
        self.ncols=float(self.rect.width/self.gridsize)

        if int(self.nrows)!=self.nrows or int(self.ncols)!=self.ncols:
            raise UserWarning,'screen size not appropriate'
        else:
            self.nrows=int(self.nrows)
            self.ncols=int(self.ncols)

    def draw_grid(self):
        x,y=self.rect.topleft
        for i in range(self.nrows+1):
            starting_pos=[]
            starting_pos.append(x)
            starting_pos.append(y+i*self.gridsize)
            end_pos=[]
            end_pos.append(starting_pos[0]+self.ncols*self.gridsize)
            end_pos.append(starting_pos[1])
            pygame.draw.line(self.surface_object,Color('gray'),starting_pos,end_pos)

        for i in range(self.ncols+1):

            starting_pos=[x+i*self.gridsize,y]
            end_pos=[x+i*self.gridsize,y+self.nrows*self.gridsize]

            pygame.draw.line(self.surface_object,Color('gray'),starting_pos,end_pos)



if __name__ == "__main__":
    pygame.init()
    SCREEN_W,SCREEN_H=500,500
    screen = pygame.display.set_mode((SCREEN_W,SCREEN_H),0,32)
    clock = pygame.time.Clock()
    box = Box(screen,Rect(100 , 100 , 200 ,300),Color('blue'))



    box2= Box(screen, Rect(350,100,50,50),Color('red'))

    mb = Messagebox(screen,(250,50),'test')
    gridlines=grid(screen,box,10)

    while True:
        time_passed = clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        box.draw()
        box2.draw()
        mb.draw()
        gridlines.draw_grid()
        pygame.display.flip()

