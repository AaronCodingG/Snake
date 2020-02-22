# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import numpy
import time


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.mainInit()
        # set window title
        self.setWindowTitle("Snake")


    def mainInit(self):
        # use 40 by 40 grid
        self.grid = numpy.array([40, 40])
        self.scale = 16
        self.resettable = False
        self.food = numpy.random.randint(self.grid, size=2)
        self.snake = Snake(self.grid)
        self.threadpool = QtCore.QThreadPool()
        worker = Worker(self.eventLoop)
        self.threadpool.start(worker)
        self.show()
        self.setFixedSize(self.scale*self.grid[0], self.scale*self.grid[1])
        
        
    def closeEvent(self, event):
        # close window
        event.accept()
        
    def paintEvent(self, event):
        # this is where everything is being painted
        painter = QtGui.QPainter(self)
        # draw snake
        self.snake.draw(painter, self.scale)
        # draw food
        brush = QtGui.QBrush(QtCore.Qt.red)
        painter.fillRect(self.food[0]*self.scale, self.food[1]*self.scale, self.scale-1, self.scale-1, brush)
        # gameover text if resettable
        if self.resettable:
            painter.setPen(QtCore.Qt.red)
            painter.setFont(QtGui.QFont('Decorative', 28))
            painter.drawText(event.rect(), QtCore.Qt.AlignCenter,\
                             "Game Over\n Score: " + str(self.snake.length)\
                             + "\nPress ESC to restart")
        return
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            direct = numpy.array([1, 0])
            self.snake.setDirection(direct)
        elif event.key() == QtCore.Qt.Key_Left:
            direct = numpy.array([-1, 0])
            self.snake.setDirection(direct)
        elif event.key() == QtCore.Qt.Key_Up:
            direct = numpy.array([0, -1])
            self.snake.setDirection(direct)
        elif event.key() == QtCore.Qt.Key_Down:
            direct = numpy.array([0, 1])
            self.snake.setDirection(direct)
        elif event.key() == QtCore.Qt.Key_Escape and self.resettable:
            self.mainInit()
        return
    
    def eventLoop(self):
        while True:
            t0 = time.time()
            # update position snake
            if self.snake.update(self.food):
                # snake ate food -> generate new food
                self.food = numpy.random.randint(self.grid, size=2)
            # game over check
            if self.snake.gameoverCheck():
                break
            # update visualization
            self.update()
            # wait
            t1 = time.time()
            time.sleep(0.2-(t0-t1))
        # trigger gameover
        self.gameover()
    
    def gameover(self):
        self.snake.setDirection(numpy.zeros((2,1)))
        # write score + "if Esc it restarts"
        self.resettable = True
        self.update()
        
        
        
class Snake():
    def __init__(self, grid):
        self.length = 1
        minPos = numpy.array([3,3])
        maxPos = grid - numpy.array([3,3])
        self.pos = [numpy.random.randint(minPos, maxPos, size=2)]
        self.direction = numpy.array([0,0])
        self.grid = grid
        
    def update(self, food):
        # updates the position of all snake elements
        oldest = self.pos[-1]
        for i in range(self.length-1, 0, -1):
            self.pos[i] = self.pos[i-1]
        self.pos[0] = self.pos[0] + self.direction
        if (self.pos[0] == food).all():
            self.pos.append(oldest)
            self.length += 1
            return True
        return False
        
    def draw(self, painter, scale):
        # draws snake into canvas
        brush = QtGui.QBrush(QtCore.Qt.black)
        for pos in self.pos:
            painter.fillRect(pos[0]*scale, pos[1]*scale, scale-1, scale-1, brush)
        return
        
    def setDirection(self, direction):
        self.direction = direction
        return True
    
    def gameoverCheck(self):
        # check if snake hit itself
        ind = []
        for i, pos in enumerate(self.pos[1:]):
            if self.pos[0][0] == pos[0]\
               and self.pos[0][1] == pos[1]:
                ind.append(i)
        if len(ind) > 0:
            return True
        if (self.pos[0] < numpy.zeros((2,1))).any()\
           or (self.pos[0] > self.grid).any():
            # snake hit the wall
            return True
        return False
        
        

class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    
    
    @QtCore.pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())