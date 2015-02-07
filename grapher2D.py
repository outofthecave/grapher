#!/usr/bin/python
# coding: UTF-8

import math
import sys
from argparse import *
import pygame
from pygame.locals import *

# CLI
SHORT_DESCR = "draw the graph for a single-parameter function f(x)."
LONG_DESCR = """\
All functions and constants from the `math' module are available for all 
command-line arguments without prefix."""
parser = ArgumentParser(description=SHORT_DESCR, epilog=LONG_DESCR)
#parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
#    default=False, help="be verbose")
parser.add_argument("-p", "--parameter", dest="x", type=str,
    default="x", help="name of the parameter (default: `x')")
parser.add_argument("-x", "--x-axis", dest="xaxis", type=str,
    default="(-1,1,0.2)", help="part of the x-axis to show and step between "
    "two labels (format: `(low,high,step)', default: `(-1,1,0.2)')")
parser.add_argument("-y", "--y-axis", dest="yaxis", type=str,
    default="(-1,1,0.2)", help="part of the y-axis to show and step between "
    "two labels (format: `(low,high,step)', default: `(-1,1,0.2)')")
parser.add_argument("-g", "--grid", action="store_true", dest="show_grid", 
    default=False, help="display a grid in gray")
parser.add_argument("--plot", action="store_true", dest="plot_mode", 
    default=False, help="plot the curve, but don't connect the points")
parser.add_argument("term", metavar="TERM", type=str,
    help="the function term, everything after `f(x)='")

EPSILON = 10**(-12)

WIDTH, HEIGHT = 760, 560
FRAMEWIDTH, FRAMEHEIGHT = 20, 20

# minimum distance between an axis and a label
AXIS_LABEL_DIST = 5
# size of the marks on the axes (is doubled)
AXIS_MARK_SIZE = 2


def main(raw_cl_args):
    global cl
    cl = parser.parse_args(raw_cl_args)

    # user namespace
    var_dict = {}
    for name in math.__dict__:
        if not name.startswith("_"):
            var_dict[name] = math.__dict__[name]

    # scaling of the axes
    (xaxis_lo, xaxis_hi, xaxis_step) = eval(cl.xaxis, var_dict)
    xaxis_d = xaxis_hi - xaxis_lo
    (yaxis_lo, yaxis_hi, yaxis_step) = eval(cl.yaxis, var_dict)
    yaxis_d = yaxis_hi - yaxis_lo

    # helpers to convert between pygame's pixel counts and mathematical values
    def x2i(x):
        return int(round(float(x - xaxis_lo) / xaxis_d * WIDTH))
    def i2x(i):
        return xaxis_lo + xaxis_d * (float(i) / WIDTH)
    def y2j(y):
        return int(round((1 - float(y - yaxis_lo) / yaxis_d) * HEIGHT))
    def j2y(j):
        return yaxis_lo + yaxis_d * (1 - (float(j) / HEIGHT))

    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    
    # screen
    screen = pygame.display.set_mode(
        (WIDTH+2*FRAMEWIDTH-1, HEIGHT+2*FRAMEHEIGHT-1))
    pygame.display.set_caption('Graph for f(%s)=%s' %(cl.x, cl.term))
    screen.fill(Color("white"))

    # user function
    def f(x):
        var_dict[cl.x] = x
        return eval(cl.term, var_dict)

    # main surface
    surf = pygame.Surface((WIDTH+1, HEIGHT+1))
    surf.fill(Color("white"))
    
    # axes
    i_zero = x2i(0)
    j_zero = y2j(0)
    
    # labels
    xaxis_label = font.render(cl.x, True, Color("black"))
    yaxis_label = font.render("f(%s)" %(cl.x), True, Color("black"))
    xaxis_label_rect = xaxis_label.get_rect()
    xaxis_label_rect.right = WIDTH - 10
    xaxis_label_rect.top = j_zero + AXIS_LABEL_DIST * 2
    yaxis_label_rect = yaxis_label.get_rect()
    yaxis_label_rect.right = i_zero - AXIS_LABEL_DIST * 2
    yaxis_label_rect.top = 10
    surf.blit(xaxis_label, xaxis_label_rect)
    surf.blit(yaxis_label, yaxis_label_rect)

    # number labels and grid
    x = xaxis_lo
    while x <= xaxis_hi:
        if abs(x) < EPSILON:
            x = 0
        i = x2i(x)
        # grid
        if cl.show_grid:
            pygame.draw.line(surf, Color("gray"), (i, 0), (i, HEIGHT))
        # mark
        pygame.draw.line(surf, Color("black"), (i, j_zero-AXIS_MARK_SIZE), 
            (i, j_zero+AXIS_MARK_SIZE))
        # label
        label = font.render(str(x), True, Color("black"))
        label_rect = label.get_rect()
        label_rect.centerx = i
        label_rect.top = j_zero + AXIS_LABEL_DIST
        surf.blit(label, label_rect)
        x += xaxis_step
    y = yaxis_lo
    while y <= yaxis_hi:
        if abs(y) < EPSILON:
            y = 0
        j = y2j(y)
        # grid
        if cl.show_grid:
            pygame.draw.line(surf, Color("gray"), (0, j), (WIDTH, j))
        # mark
        pygame.draw.line(surf, Color("black"), (i_zero-AXIS_MARK_SIZE, j), 
            (i_zero+AXIS_MARK_SIZE, j))
        # label
        label = font.render(str(y), True, Color("black"))
        label_rect = label.get_rect()
        label_rect.right = i_zero - AXIS_LABEL_DIST
        label_rect.centery = j
        surf.blit(label, label_rect)
        y += yaxis_step

    # draw axes
    pygame.draw.line(surf, Color("black"), (0, j_zero), (WIDTH, j_zero))
    pygame.draw.line(surf, Color("black"), (i_zero, 0), (i_zero, HEIGHT))

    # curve
    pix_array = pygame.PixelArray(surf)
    prev_point = None
    for i in range(WIDTH):
        x = i2x(i)
        j = y2j(f(x))
        #pix_array[i][j] = Color("red")
        point = (i, j)
        if prev_point is None or cl.plot_mode:
            prev_point = point
        pygame.draw.line(surf, Color("red"), prev_point, point)
        prev_point = point
    surf.unlock()
    del pix_array

    screen.blit(surf, (FRAMEWIDTH, FRAMEHEIGHT))

    # main loop
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
        # TODO follow mouse with a crosshairs and show curve values
        #pygame.display.update()



if __name__ == "__main__":
    main(sys.argv[1:])
