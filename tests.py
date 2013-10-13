__author__ = 'win7'

import unittest
import tetris_obj
import widgets
import pygame
from random import choice


##Am having problem with number of columns the value is sometimes 7

class TestTetris(unittest.TestCase):
    def setUp(self):
        pygame.init()
        screen_w, screen_h = 500, 500
        self.screen = pygame.display.set_mode((screen_w, screen_h), 0, 32)
        boxx,boxy = 100, 100
        box_w, box_h = 70, 70
        self.box = widgets.Box(self.screen, pygame.Rect(boxx, boxy, box_w, box_h), pygame.Color('white'))
        self.gridsize = 10
        self.nrows = 7
        self.ncols = 7
        self.holder_class = tetris_obj.holder(self.ncols, self.nrows)
        self.tobj_class = tetris_obj.tobj(self.screen, self.holder_class, pygame.Color('blue'), self.nrows, self.ncols, self.gridsize, self.box)

    def test_holder_class(self):
        test_list =  [self.nrows * [False] for i in range(self.ncols)]
        self.holder_class.generate_empty()
        self.assertEqual(self.holder_class.holder_pos, test_list)
        self.assertEqual(len(self.holder_class.holder_pos),self.ncols)
        self.tobj_class.kill()
        self.assertNotEqual(self.holder_class.holder_pos, test_list)
        #undo changes
        self.tobj_class = tetris_obj.tobj(self.screen, self.holder_class, pygame.Color('blue'), self.nrows, self.ncols, self.gridsize, self.box)

    def test_can_move_down(self):
        self.tobj_class.holder.generate_empty()
        down_coord = self.tobj_class.get_down_coord()
        down_coord = down_coord + self.tobj_class.xy_to_n()[1]
        for i in range(len(self.tobj_class.holder.holder_pos)):
            self.tobj_class.holder.holder_pos[i][down_coord + 1] = True
        self.assertFalse(self.tobj_class.can_move_d())

    def test_can_move_l(self):
        self.tobj_class.holder.generate_empty()
        left_coord = self.tobj_class.get_left()
        left_coord = left_coord + self.tobj_class.xy_to_n()[0]
        if left_coord == 0:
            return None
        for i in range(len(self.tobj_class.holder.holder_pos[left_coord - 1])):
            self.tobj_class.holder.holder_pos[left_coord - 1][i] = True
        self.assertFalse(self.tobj_class.can_move_l())

    def test_can_move_r(self):
        self.tobj_class.holder.generate_empty()
        right_coord = self.tobj_class.get_right()
        right_coord = right_coord + self.tobj_class.xy_to_n()[0]
        if right_coord == self.tobj_class.ncols - 1:
            return None
        for i in range(len(self.tobj_class.holder.holder_pos[right_coord + 1])):
            self.tobj_class.holder.holder_pos[right_coord + 1][i] = True
        self.assertFalse(self.tobj_class.can_move_r())

    def test_generate_full(self):
        self.tobj_class.holder.generate_empty()
        self.tobj_class.holder.generate_full()
        a = []
        for i in range(self.tobj_class.holder.ncol):
            a.append(self.tobj_class.holder.nrow * [True])
        self.assertEqual(a, self.tobj_class.holder.holder_pos)

    def test_state(self):
        self.tobj_class.holder.generate_full()
        self.assertEqual(self.tobj_class.State, self.tobj_class.states[0])
        self.assertFalse(self.tobj_class.can_move_d())
        self.assertEqual(self.tobj_class.State, self.tobj_class.states[1])

    def test_dying(self):
        time_passed = 800
        self.tobj_class.dying(time_passed)
        self.assertEqual(self.tobj_class.State, self.tobj_class.states[2])

    def test_reset(self):
        time_passed = self.tobj_class.death_timer - 100
        self.tobj_class.dying(time_passed)
        self.assertTrue(self.tobj_class.death_timer > 0)
        self.tobj_class.reset()
        self.assertTrue(self.tobj_class.death_timer == self.tobj_class.time)

    def test_update(self):
        self.holder_class.generate_full()
        self.tobj_class.reset()
        time_passed = 700
        self.tobj_class.State = self.tobj_class.states[1]
        self.tobj_class.update(time_passed)
        self.assertTrue(self.tobj_class.death_timer < self.tobj_class.time)

    def test_kill(self):
        self.holder_class.generate_full()
        self.tobj_class.reset()
        time_passed = 800
        self.tobj_class.dying(time_passed)
        self.assertTrue(self.tobj_class.State == self.tobj_class.states[2])
        self.tobj_class.State = self.tobj_class.states[3] #To enter the kill state
        self.assertTrue(self.tobj_class.State == self.tobj_class.states[3])
        position = self.tobj_class.xy_to_n()
        for sprite in self.tobj_class.tetris_o:
            pos = sprite.xy_to_n(position)
            self.assertTrue(self.tobj_class.holder.holder_pos[pos[0]][pos[1]])
            #self.assertFalse(self.tobj_class.holder.holder_sprite[pos[0]][pos[1]] == False)

    def test_set_real_pos(self):
        center_pos = self.tobj_class.center_pos
        a_block = choice(self.tobj_class.tetris_o.sprites())
        relative_pos = a_block.get_pos()
        real_position = [center_pos[0] + (relative_pos[0] * self.gridsize), center_pos[1] + (relative_pos[1] * self.gridsize)]
        self.assertTrue(relative_pos != [0,0])
        a_block.set_real_pos(center_pos)
        self.assertEqual(a_block.real_pos, real_position)
        self.assertEqual(a_block.get_pos(), [0, 0])

    def test_check_row(self):
        row = 6
        self.holder_class.generate_empty()
        for i in range(self.ncols):
            self.holder_class.holder_pos[i][row] = True
        self.assertTrue(self.holder_class.check_row(row))

    def test_get_real_pos_n(self):
        self.holder_class.generate_empty()
        self.tobj_class.kill()
        for sprite in self.tobj_class.tetris_o:
            pos = sprite.get_real_pos_n()
            self.assertEqual(pos[0], int(pos[0]))
            self.assertEqual(pos[1], int(pos[1]))


if __name__ == "__main__":
    unittest.main()