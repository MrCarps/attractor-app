import WidgetClasses as wc
import PyQt5.QtWidgets as qt
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from vispy import app
import numpy as np
import time
import sys

def RKF45(y,f,h):
    '''Runge Kutta Fehlberg Method, forth order runge kutta method with fifth
       order error estimation'''
    start = time.time()
    y1 = y
    f1 = f(y1)
    y2 = y + h/4*f1
    f2 = f(y2)
    y3 = y + 3/32*h*f1 + 9/32*h*f2
    f3 = f(y3)
    y4 = y + 1932/2197*h*f1 - 7200/2197*h*f2 + 7296/2197*h*f3
    f4 = f(y4)
    y5 = y + 439/216*h*f1 - 8*h*f2 + 3680/513*h*f3 - 845/4104*h*f4
    f5 = f(y5)
    y6 = y - 8/27*h*f1 + 2*h*f2 - 3544/2565*h*f3 + 1859/4104*h*f4 \
           - 11/40*h*f5
    f6 = f(y6)
    yn1 = y + 16/135*h*f1 + 6656/12825*h*f3 + 28561/56430*h*f4 \
            - 9/50*h*f5 + 2/55*h*f6
    yn2 = y + 25/216*h*f1 + 1408/2565*h*f3 + 2197/4104*h*f4 \
            - 1/5*h*f5

    err = np.linalg.norm(yn1 - yn2)/np.linalg.norm(yn2)
    calc_time = time.time() - start
    return yn2,calc_time,err

def eRK4(y,f,h):
    '''Standard Runge Kutta Method, forth order runge kutta method with error
       estimation via additional calculation with halfed stepsize'''
    def calc(y,f,h):
        y1 = y
        f1 = f(y1)
        y2 = y + h/2*f1
        f2 = f(y2)
        y3 = y + h/2*f2
        f3 = f(y3)
        y4 = y + h*f3
        return y + h/6*(f1 + 2*f2 + 2*f3 + f(y4))

    start = time.time()
    yn = calc(y,f,h)
    yn_half = calc(calc(y,f,h/2),f,h/2)

    err = np.linalg.norm(yn_half - yn)/np.linalg.norm(yn)
    calc_time = time.time() - start
    return yn,calc_time,err

def expEul(y,f,h):
    '''Explicit Euler Method, first order runge kutta method with error
       estimation via additional calculation with halfed stepsize'''
    calc = lambda y,f,h : y + h*f(y)

    start = time.time()
    yn = calc(y,f,h)
    yn_half = calc(calc(y,f,h/2),f,h/2)

    err = np.linalg.norm(yn_half - yn)/np.linalg.norm(yn)
    calc_time = time.time() - start
    return yn,calc_time,err

def lorenzODE(param):
    def func(y):
        f = np.array([param[0]*(y[1]-y[0]),\
            y[0]*(param[1]-y[2])-y[1],\
            y[0]*y[1] - param[2]*y[2]])
        return f
    return func

def thomasODE(param):
    def func(y):
        f = np.array([np.sin(y[1]) - param[0]*y[0],\
            np.sin(y[2]) - param[0]*y[1],\
            np.sin(y[0]) - param[0]*y[2]])
        return f
    return func

def roesslerODE(param):
    def func(y):
        f = np.array([-y[1]-y[2],\
            y[0] + param[0]*y[1],\
            param[1] + y[2]*(y[0] - param[2])])
        return f
    return func

solverDic = {'Explicit Euler' : expEul,
             'Runge Kutta 4' : eRK4,
             'Fehlberg 4,5' : RKF45}
attractorDic = {'Lorenz' : {'ODE' : lorenzODE,
                            'Parameters' : [('a','b','c'),(10,28,8/3)],
                            'Interval' : [(1,100),(1,50),(0.1,10)],
                            'InVal' : [1,1,1]},
                'Thomas' : {'ODE' : thomasODE,
                            'Parameters' : [('b'),(0.208186,)],
                            'Interval' : [(0.0001,1)],
                            'InVal' : [0,-1,7]},
                'Roessler' :{'ODE' : roesslerODE,
                            'Parameters' : [('a','b','c'),(0.2,0.2,14)],
                            'Interval' : [(0,2),(0,2),(1,20)],
                            'InVal' : [1,1,0]}}

class Attractor(qt.QWidget):
    '''Attractor(parent=None,type={'Lorenz','Thomas'},solver={'Runge Kutta 4',
                 'Explicit Euler'})
       creates an Attractor object and embeds it into a surrunding GUI if PARENT
       is a valid QGridLayout
    '''
    def __init__(self,parent = None,type = 'Lorenz', solver = 'Runge Kutta 4'):
        super().__init__()

        self.parent = parent
        self.type = type
        self.solvName = solver
        self.ODE = attractorDic[type]['ODE']
        self.solver = solverDic[solver]

        self.initUI()
        self.config()

    def initUI(self):
        '''Create Widget Layout'''
        layout = qt.QVBoxLayout()

        # Creating Widget elements for plotting, settings and the sliders
        # and adding it to Attractor's layout
        self.plot = wc.plot(np.array([attractorDic[self.type]['InVal']]))
        self.settings = wc.settings(attractorDic.keys(), self.type,\
                                    solverDic.keys(), self.solvName,\
                                    attractorDic[self.type]['InVal'])
        self.sliders = wc.sliders(nams=attractorDic[self.type]['Parameters'][0],\
                                  vals=attractorDic[self.type]['Parameters'][1],\
                                  ints=attractorDic[self.type]['Interval'])
        layout.addWidget(self.plot.native)
        layout.addWidget(self.settings)
        layout.addWidget(self.sliders)
        self.setLayout(layout)

        # If the widget is embedded in a AttractorApp, Attractor is added to the
        # AttractorApp's layout
        if self.parent != None:
            self.parent.addWidget(self)

    def config(self):
        '''Configure Widget Elements'''

        # Initializing Variables for keeping track of the timestep, runtime,
        # calculation time (to be averaged), error estimates (to be averaged)
        self.timestep = []
        self.timeElapsed = 0
        self.prevTimeVals = []
        self.prevLocErr = []

        # Cross-connecting signals of GUI elements from plot, settings, sliders
        self.settings.AttrDropdown.currentIndexChanged.connect(self.updateAttractor)
        self.settings.SolvDropdown.currentIndexChanged.connect(self.updateSolver)
        self.settings.PauseButton.clicked.connect(self.pause)
        self.settings.RestartButton.clicked.connect(self.restart)
        self.sliders.Signal.changed.connect(self.updateParameters)

        # Setting up a timer to call draw-method repeatedly
        self.timer = app.Timer(interval = self.sliders.timestep_value(),\
                               connect = self.draw, start = True)

        self.updateParameters()

    def updateParameters(self):
        '''Called when any slider is moved.
           Requests values from sliders() and updates the timer as well as
           the ODE parameters accordingly'''
        self.timestep = self.sliders.timestep_value()
        self.odeParams = self.sliders.param_values()

        self.updateODE()
        self.updateTimer()

    def updateODE(self):
        '''Updates the ODE to be solved according to the current slider values'''
        self.ode2solve = self.ODE(self.sliders.param_values())

    def updateAttractor(self):
        '''Called when a new Attractor is selected from the dropdown menu.
           Pauses the current plots, removes the sliders and adds the ones
           corresponding to the current Attractor again, updates ODE to solve.'''
        self.settings.PauseButton.toggle()
        self.pause()

        self.type = self.settings.AttrDropdown.currentText()
        self.ODE = attractorDic[self.type]['ODE']

        self.settings.set_initVals(attractorDic[self.type]['InVal'])
        self.sliders.deleteLater()
        self.sliders = wc.sliders(nams=attractorDic[self.type]['Parameters'][0],\
                                  vals=attractorDic[self.type]['Parameters'][1],\
                                  ints=attractorDic[self.type]['Interval'])
        self.sliders.Signal.changed.connect(self.updateParameters)
        self.layout().addWidget(self.sliders)

        self.updateODE()

    def updateSolver(self):
        '''Called when a new Solver is selected from the dropdown menu.
           Updates the solver function accordingly.'''
        self.solvName = self.settings.SolvDropdown.currentText()
        self.solver = solverDic[self.solvName]

    def updateTimer(self):
        '''Called when any slider is moved. Updates the timer's interval.'''
        self.timer.interval = self.sliders.timestep_value()

    def draw(self,events):
        '''Solve the ODE for the next timestep and visualize it.'''
        # If plot is not paused
        if not self.settings.PauseButton.isChecked():
            # Solve ODE with previous timestep and current timestep value
            y = self.plot.CurveData[-1]
            delta_t = self.timestep
            yn,t,err = self.solver(y,self.ode2solve,delta_t)

            # Update the plot by adding the data to it and increasing the time
            self.timeElapsed += delta_t
            self.plot.add_data([yn])
            self.plot.update_runtime(self.timeElapsed)

            # Storing the values for speed and error, averaging and displaying
            # it by handing it to the plot
            self.prevTimeVals.append(t)
            self.prevLocErr.append(err)
            if len(self.prevTimeVals) > 20:
                self.plot.update_speed(np.average(self.prevTimeVals))
                self.plot.update_error(np.average(self.prevLocErr))
                self.prevTimeVals = []
                self.prevLocErr = []

    def pause(self):
        '''Called when the PauseButton is clicked. Pauses Plotting.'''
        if self.settings.PauseButton.isChecked():
            self.settings.PauseButton.setText(chr(9654))
            print('Paused ...')
        else:
            self.settings.PauseButton.setText('||')
            print('Continued ...')

    def restart(self):
        '''Called when the RestartButton is clicked. Restarts Plotting.'''
        # Try to set initial values from the values entered. If the strings
        # can't be converted to numbers an error is handled
        try:
            newInitVals = self.settings.get_initVals()
        except:
            # Plot data is reset but the initial value is taken from the
            # attractorDic, these values are also filled into the text edits
            self.plot.reset_data(np.array([attractorDic[self.type]['InVal']]))
            self.settings.set_initVals(attractorDic[self.type]['InVal'])
            print('Invalid Initial Values. Using standard Values instead.')
            # Let a possible overlying function know that an Exception was raised
            return -1
        else:
            # Reset the plot and set entered values as initial values
            self.plot.reset_data(np.array([newInitVals]))
            print('Restarted...')
            # Let a possible overlying function know that no Exception was raised
            return 0
        finally:
            # Reset no matter what
            self.timeElapsed = 0
            self.prevTimeVals = []

            # Resume plotting if paused
            if self.settings.PauseButton.isChecked():
                self.settings.PauseButton.toggle()
                self.pause()

class AttractorApp(qt.QMainWindow):
    '''AttractorApp(n = 2,types = list({'Lorenz','Thomas'})) creates a
       PyQt5-Application which features N Attractor-Objects aligned
       horizontally. The attractors' types can be set using the TYPES kwarg, but
       its length must match N.
    '''
    def __init__(self,n = 2,types = ['Lorenz']):
        super().__init__()

        self.nOfPlots = n
        self.attractors = []
        self.types = types
        if n > 1:
            self.types *= n

        self.initUI(n)
        self.config()

    def initUI(self,n):
        # Creating GUI Main Window
        self.setWindowTitle('AttractorApp')
        win = qt.QWidget()

        # Creating Layouts
        mainLayout = qt.QVBoxLayout()
        plotsLayout = qt.QHBoxLayout()
        buttonLayout = qt.QHBoxLayout()

        # Creating Widgets
        plots = qt.QGroupBox()
        buttons = qt.QGroupBox()

        # Creating Buttons
        self.restartButton = qt.QPushButton('Restart all')
        self.pauseButton = qt.QPushButton('Pause all')

        # Creating the right amount of Attractor()-Objects
        for k in range(self.nOfPlots):
            self.attractors.append(Attractor(parent = plotsLayout,\
                                             type = self.types[k]))

        # Attractos got added to the plotLayout within the constructor of
        # Attractor(), therefore the layout can already be added to the GroupBox
        plots.setLayout(plotsLayout)

        # Adding remaining Widgets to Layouts
        buttonLayout.addWidget(self.pauseButton)
        buttonLayout.addWidget(self.restartButton)
        buttons.setLayout(buttonLayout)

        mainLayout.addWidget(plots)
        mainLayout.addWidget(buttons)

        win.setLayout(mainLayout)
        self.setCentralWidget(win)

        # Create statusBar and menuBar
        self.Status = self.statusBar()
        self.makeMenuBar()

        self.show()

    def config(self):
        # Connecting and setting up Buttons
        self.pauseButton.setCheckable(True)
        self.restartButton.clicked.connect(self.restartAll)
        self.pauseButton.clicked.connect(self.pauseAll)

        # Redirecting stout to the status bar
        sys.stdout = wc.Status(self.Status)

    def restartAll(self):
        '''Restart all Attractors contained in the AttractorApp.'''
        # Performing a 'checksum' for possibly invalid inputs for initial values
        ret = 0
        for a in self.attractors:
            ret += a.restart()

        if self.pauseButton.isChecked():
            self.pauseButton.toggle()
            self.pauseAll()
        print('Restarted all...' if not ret else 'Restarted all... (one or '+\
               'more input Initial Values where invalid. The standard Values '+\
               'where used for those.)')

    def pauseAll(self):
        '''Pause/Restart all Attractors contained in the AttractorApp'''
        for a in self.attractors:
            if self.pauseButton.isChecked() != a.settings.PauseButton.isChecked():
                a.settings.PauseButton.toggle()
                a.pause()

        if self.pauseButton.isChecked():
            print('Paused all ...')
            self.pauseButton.setText('Continue all')
        else:
            print('Continued all ...')
            self.pauseButton.setText('Pause all')

    def makeMenuBar(self):
        # Creating menuBar and menus
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')
        aboutMenu = menuBar.addMenu('About')

        # Creating Actions
        newAction = qt.QAction('New',self)
        saveVAction = qt.QAction('Vispy',self)
        saveMAction = qt.QAction('Matplotlib',self)
        infoAction = qt.QAction('Information',self)
        aboutAction = qt.QAction('About',self)

        # Creating Shortcuts
        newAction.setShortcut('Ctrl+N')
        saveVAction.setShortcut('Ctrl+S')
        saveMAction.setShortcut('Ctrl+Shift+S')
        infoAction.setShortcut('Ctrl+I')

        # Adding Actions to menu-items
        fileMenu.addAction(newAction)
        saveMenu = fileMenu.addMenu('Save as...')
        saveMenu.addAction(saveVAction)
        saveMenu.addAction(saveMAction)
        fileMenu.addAction(infoAction)
        aboutMenu.addAction(aboutAction)

        # Setting functionality
        newAction.triggered.connect(self.newCall)
        saveVAction.triggered.connect(self.saveVCall)
        saveMAction.triggered.connect(self.saveMCall)
        infoAction.triggered.connect(self.infoCall)
        aboutAction.triggered.connect(self.aboutCall)

    def newCall(self):
        '''Called from the MenuBar to create a new Attractor()-Object.'''
        self.newAttr = Attractor()
        self.newAttr.show()
        self.attractors.append(self.newAttr)

    def saveVCall(self):
        '''Called from the MenuBar to export all created Attractors as vispy
           export (.png).'''
        self.pauseButton.toggle()
        self.pauseAll()
        for ind,a in enumerate(self.attractors):
            a.plot.export_vispy('vispyExport_'+str(ind)+'.png')
        print('Successfully exported with Vispy!')

    def saveMCall(self):
        '''Called from the MenuBar to export all created Attractors as
           matplotlib export (.png).'''
        self.pauseButton.toggle()
        self.pauseAll()
        for ind,a in enumerate(self.attractors):
            a.plot.export_plt('pltExport_'+str(ind)+'.png')
        print('Successfully exported with Matplotlib!')

    def infoCall(self):
        '''Called from the MenuBar to open InfoWindow.'''
        self.infoWin = wc.miniWindow('info')

    def aboutCall(self):
        '''Called from the MenuBar to open AboutWindow.'''
        self.aboutWin = wc.miniWindow('about')

if __name__ == '__main__':
    application = qt.QApplication(sys.argv)
    application.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.WindowText, Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15,15,15))
    palette.setColor(QtGui.QPalette.Text, Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ButtonText, Qt.white)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(255,255,255).lighter())
    application.setPalette(palette)
    a = AttractorApp()
    sys.exit(application.exec_())
