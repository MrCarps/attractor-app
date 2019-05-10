from PyQt5.QtCore import Qt, QObject, pyqtSignal
from vispy import scene, io, color
from mpl_toolkits import mplot3d
import PyQt5.QtWidgets as qt
import matplotlib.pyplot as plt
import numpy as np
import sys

class Signal(QObject):
    '''Signal creates a pyqtSignal to be emitted in other classes.'''
    changed = pyqtSignal()

class Status():
    '''Status corresponds to a StatusBar object of a QMainWindow and
       redirects the write() method to the showMessage() method of StatusBar.
       This is important to use StatusBar as stdout.'''

    def __init__(self,statusbar):
        self.statusbar = statusbar

    def write(self,string):
        '''Redirect write() to showMessage()'''
        # Only update if string is longer than 3 characters, because when used
        # as stdout, write() receives newlines which cannot be displayed in
        # statusBar
        if len(string)>3:
            self.statusbar.showMessage(string)

    def flush(self):
        '''Only defined for use as stdout.'''
        pass

class plot(scene.SceneCanvas):
    '''PLOT features a vispyCanvas for plotting which includes a line object as
       well as three textboxes. It delivers methods for updating the line's data
       and the text boxes' values. PLOT can be embedded into pyqt applications
       when plot.native is used. The constructor takes an optional input
       'initData' which sets the curve's initial data.'''

    def __init__(self,initData=None):
        super().__init__()
        super().unfreeze() # Necessary for vispy object to add new attributes
        self.CurveData = initData if initData is not None else np.array([[0,0,0]])

        self.initUI()
        self.config()

    def initUI(self):
        view = self.central_widget.add_view()
        axis = scene.visuals.XYZAxis(parent=view.scene)
        cam = scene.TurntableCamera(elevation=30, azimuth=30,distance=500)
        cam.set_range((-30, 30), (-30, 30), (-30, 30))
        view.camera = cam

        # Create graphical objects
        self.InfoTime = scene.visuals.Text(parent=self.scene, anchor_x='left',\
                                           text = 'Time elapsed:')
        self.InfoSpeed = scene.visuals.Text(parent=self.scene, anchor_x='left',\
                                            text = 'Calculation Time (avg):')
        self.InfoError = scene.visuals.Text(parent=self.scene, anchor_x='left',\
                                            text = 'Estimated local Error (avg):')

        self.Curve = scene.visuals.Line(np.array(self.CurveData),\
                                        parent=view.scene,\
                                        width = 1,\
                                        #color = 'hsl')
                                        color = (245/255,187/255,32/255))

    def config(self):
        # Format TextBoxes
        self.InfoTime.pos = 10, 30
        self.InfoTime.font_size = 7
        self.InfoTime.color = 'white'

        self.InfoSpeed.pos = 10, 45
        self.InfoSpeed.font_size = 7
        self.InfoSpeed.color = 'white'

        self.InfoError.pos = 10, 60
        self.InfoError.font_size = 7
        self.InfoError.color = 'white'

    def add_data(self,data):
        '''Adds data to the curve to be plotted.'''
        self.CurveData = np.append(self.CurveData,data,0)
        self.Curve.set_data(pos = self.CurveData)

    def reset_data(self,newData=None):
        '''Deletes the data of the plotted curve. Takes optional argument
           'newData' which can be used as a starting value. If 'newData' is not
           defined, the curve's data is set to be empty.'''
        self.CurveData = newData if newData is not None else np.array([[]])

    def get_data(self):
        '''Returns the curve's current data.'''
        return self.CurveData

    def update_runtime(self,rt):
        '''Updates the plots 'Time elapsed:'-textBox.'''
        self.InfoTime.text = 'Time elapsed: %.2f s' %rt

    def update_speed(self,sp):
        '''Updates the plots 'Calculation Time:'-textBox.'''
        self.InfoSpeed.text = 'Calculation Time (avg): %.2e s' %sp

    def update_error(self,err):
        '''Updates the plots 'Estimated local Error:'-textBox.'''
        self.InfoError.text = 'Estimated local Error (avg): %.2e %%' %(err*100)

    def export_vispy(self,name):
        '''Exports the current plot via Vispy's render()-method as .png. The
           snapshot includes the curve as well as the textboxes.'''
        img = self.render()
        io.write_png(name,img)

    def export_plt(self,name):
        '''Exports the current plot via Matplotlib's savefig()-method as .png.
           The snapshot only includes the curve's data (and axes).'''
        data = self.CurveData
        ax = plt.axes(projection='3d')
        ax.plot3D(data[:,0], data[:,1], data[:,2])
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        plt.savefig(name)

class settings(qt.QGroupBox):
    '''SETTINGS(attr,currA,solv,currS,inits) features a QGroupBox with two
       dropdownMenus including 'attr' (set to 'currA') and 'solv' (set to
       'currS') as well as TextEdits for initialValues (set to 'inits').
       It also features two buttons (Pause and Restart) the actions of which
       can be set outside of SETTINGS. SETTINGS can be embedded into pyqt
       applications.'''

    def __init__(self,attr,currA,solv,currS,inits):
        super().__init__()
        self.setTitle('Settings and Initial Values')

        self.AttrNames = attr
        self.SolvNames = solv
        self.InitVals = inits

        self.initUI()
        self.config(currA,currS)

    def initUI(self):
        layout = qt.QHBoxLayout()

        # Creating UI Elements
        self.AttrDropdown = qt.QComboBox()
        self.SolvDropdown = qt.QComboBox()
        self.PauseButton = qt.QPushButton('||')
        self.RestartButton = qt.QPushButton(chr(8635))

        initLabels = [qt.QLabel('x:'),qt.QLabel('y:'),qt.QLabel('z:')]
        self.initEdits = [qt.QLineEdit(str(v)) for v in self.InitVals]

        layout.addWidget(self.AttrDropdown)
        layout.addWidget(self.SolvDropdown)

        for l,e in zip(initLabels,self.initEdits):
            layout.addWidget(l)
            layout.addWidget(e)

        layout.addWidget(self.PauseButton)
        layout.addWidget(self.RestartButton)
        self.setLayout(layout)

    def config(self,currA,currS):
        # Filling dropboxes with values passed to the constuctor.
        self.PauseButton.setCheckable(True)
        self.AttrDropdown.addItems(self.AttrNames)
        self.SolvDropdown.addItems(self.SolvNames)

        # Set current items to the ones specified within the constructor.
        self.AttrDropdown.setCurrentIndex(self.AttrDropdown.findText(currA))
        self.SolvDropdown.setCurrentIndex(self.SolvDropdown.findText(currS))

    def get_initVals(self):
        '''Returns the current initial Values typed into the textBoxes and
           converts them to floats. If the input might be invalid, possible
           Exceptions must be handled outside SETTINGS.'''
        return [float(e.text()) for e in self.initEdits]

    def set_initVals(self,vals):
        '''Takes an input 'vals', which is a list of three values and sets the
           contents of the textEdits' contents accordingly.'''
        for e,v in zip(self.initEdits,vals):
            e.setText(str(v))

class sliders(qt.QGroupBox):
    '''SLIDERS(tStep=1e-2,tRange=(1e-6,1e-1),nams=None,vals=None,ints=None)
       creates a QGroupBox which featurs n + 1 sliders where n is the number of
       elements in 'nams' which must be of the same size as 'vals' and 'ints'.
       The n+1 sliders get named as ['Timestep',nams], are set to the values
       'vals' and the interval of possible slider values is set to 'ints'.
       SLIDERS can be embedded into pyqt-Applications.'''

    def __init__(self,tStep=-2,tRange=(-5,0),nams=None,vals=None,ints=None):
        # timestep values and ranges to be understood as powers of 10
        super().__init__()
        self.setTitle('Parameters')

        self.Names = ['Timestep'] + list(nams)
        self.fString = ['%7.6f']+['%g']*len(nams)
        self.Values = [tStep] + list(vals)
        self.Intervals = [tRange] + list(ints)

        self.Sliders = []
        self.Labels = []

        self.map2Ind = []
        self.map2Val = []

        self.Signal = Signal()

        self.initUI()
        self.configSliders()

    def initUI(self):
        # Creating UI Elements.
        layout = qt.QGridLayout()

        for ind,(n,v,fs) in enumerate(zip(self.Names,self.Values,self.fString)):
            # Display for timestep value is treated lograrithmically
            if ind == 0:
                v = 10**v
            self.Labels.append(qt.QLabel(n + ': '+ fs % v))
            self.Sliders.append(qt.QSlider(Qt.Horizontal))

        for ind,(lab,sl) in enumerate(zip(self.Labels,self.Sliders)):
            layout.addWidget(lab,ind,0)
            layout.addWidget(sl,ind,1)
        self.setLayout(layout)

    def configSliders(self):
        # Setting up sliders to have the correct value range and slider position.
        for s in self.Intervals:
            self.map2Ind.append(self.sliderMap(s[0],s[1],toInd = True))
            self.map2Val.append(self.sliderMap(s[0],s[1],toInd = False))

        for s,f,v in zip(self.Sliders,self.map2Ind,self.Values):
            # Setting slider's value.
            s.setValue(f(v))
            # If slider is moved the corresponding label should be updated.
            s.valueChanged.connect(self.update)

    def update(self):
        '''Called when any slider is moved. It retrieves all sliders' values,
           saves them and updates corresponding labels accordingly. When update()
           is called, a SIGNAL called 'changed' is emitted which can be used
           to take actions outside of SLIDERS whenever a slider is moved.'''
        for ind, (s,l,n,f,fs) in enumerate(zip(self.Sliders,self.Labels,\
                                               self.Names,self.map2Val,\
                                               self.fString)):
            val = f(s.value())
            self.Values[ind] = val
            # Display for timestep value is treated lograrithmically
            if ind == 0:
                val = 10**val
            l.setText(n + ': ' + fs %val)

        self.Signal.changed.emit()

    def sliderMap(self,min,max,toInd = False):
        '''sliderMap(min,max,toInd=False) returns a mapping function which maps
           a slider's position (index) to a value within the interval [min,max]
           if 'toInd' is set to False or a function which maps a value within
           said interval to a slider-index if 'toInd' is set to True.'''
        if toInd: # return the index
            def f(val):
                return np.ceil(99/(max-min)*(val-min))
        else: # return the value
            def f(ind):
                return min + (max - min)*ind/99
        return f

    def timestep_value(self):
        '''Returns the current value set for 'Timestep'. Logarithmic.'''
        return 10**self.Values[0]

    def param_values(self):
        '''Returns the current values of all sliders except 'Timestep'.'''
        return self.Values[1:]

class miniWindow(qt.QMainWindow):
    '''MINIWINDOW creates a QMainWindow which only features a central QLabel-
       Widget which is either the about-string or the information-string.
       MINIWINDOW is used for ATTRACTORAPP. The constructor takes an input
       'which', which can either be 'about' or 'info'.'''

    def __init__(self,which):
        super().__init__()
        self.initUI(which)
        self.show()

    def initUI(self,which):
        lab = qt.QLabel('test text.')

        # Allow to open external links
        lab.setOpenExternalLinks(True)

        # Decide which window to create and read contents from html-file
        if which == 'about':
            self.setWindowTitle('About')
            self.resize(300,150)
            with open('about.html') as f:
                text = f.read()
        elif which == 'info':
            self.setWindowTitle('Informations')
            self.resize(600,300)
            with open('info.html') as f:
                text = f.read()
        else:
            text = ''

        # Add text to label object
        lab.setText(text)
        self.setCentralWidget(lab)

if __name__ == '__main__':
    application = qt.QApplication(sys.argv)
    #a = sliders(nams=['a','b','c'],vals=[1.5,5,3],ints=[(1,2),(1,10),(1,10)])
    #b = settings(['L','T'],'T',['a','b'],'b',[1,1,1])
    #c = plot()
    #a.show()
    #b.show()
    #c.show()
    d = miniWindow('about')
    sys.exit(application.exec_())
