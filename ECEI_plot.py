#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QComboBox, QLabel, QLineEdit, QShortcut, QCheckBox
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import pyqtSlot, QRect
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np
import traceback  # better way to handle exceptions
import modules.my_funcs_class as my_funcs
import modules.ECI_sfLoad_osam as ECI


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'ECEI_plot'
        self.left = 100
        self.top = 100
        self.width = 1400
        self.height = 900
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.show()


class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tabs ----------------------------------
        self.tabs = QTabWidget()
        self.Load_data = QWidget()  # create tab 1
        self.Plot_chs = QWidget()  # create tab 2
        self.LOS_plot = QWidget()  # create tab 3
        self.FFT_plot = QWidget()  # create tab 4
        self.R_trace = QWidget()   # create tab 5
        self.R_single = QWidget()   # create tab 6
        self.Z_trace = QWidget()   # create tab 7
        self.Z_single = QWidget()   # create tab 8
        self.EQH_tab = QWidget()   # create tab 9
        self.Rz_tab = QWidget()   # create tab 9
        self.SettRzPlot_tab = QWidget()   # create tab 10
        self.tabs.resize(300, 200)

        # Add tabs to the Main WIndow
        self.tabs.addTab(self.Load_data, "Load data")  # tab 1
        self.tabs.addTab(self.Plot_chs, "Plot all chs")  # tab 2
        self.tabs.addTab(self.LOS_plot, "LOS")  # tab 3
        self.tabs.addTab(self.FFT_plot, "LOS_FFT")  # tab 4
        self.tabs.addTab(self.R_trace, "R trace")     # tab 5
        self.tabs.addTab(self.R_single, "R trace Single")     # tab 6
        self.tabs.addTab(self.Z_trace, "z trace")     # tab 7
        self.tabs.addTab(self.Z_single, "z trace Single")     # tab 8
        self.tabs.addTab(self.EQH_tab, "EQH")     # tab 9
        self.tabs.addTab(self.Rz_tab, "Rz plot")     # tab 9
        self.tabs.addTab(self.SettRzPlot_tab, "Rz plot Settings")     # tab 10

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.show()
        # ----------------------------------------------------------------------------------

        # Load_data tab - content
        self.data_loaded = False
        layout_load = QtWidgets.QVBoxLayout(self.Load_data)  # main layout
        sublayout_load = QtWidgets.QGridLayout()  # layout for inputs
        layout_load.addLayout(sublayout_load)

        # Input widgets
        # Shot
        self.Shot_lbl_load = QLabel(self.Load_data)
        self.Shot_lbl_load.setText('Shot # ')
        self.Shot_ed_load = QLineEdit(self.Load_data)
        self.Shot_ed_load.setText('25781')
        # Diag
        self.Diag_lbl_load = QLabel(self.Load_data)
        self.Diag_lbl_load.setText('Diag: ')
        self.Diag_load = QComboBox(self.Load_data)
        # self.Diag_load.addItems(['TDI', 'ECI'])
        self.Diag_load.addItems(['ECI', 'TDI'])
        # Load button
        self.Butt_load = QPushButton("Load ECEI data", self.Load_data)
        self.Butt_load.clicked.connect(self.Load_ECEI_data)
        # Monitor
        self.Monitor_load = QtWidgets.QTextBrowser(self.Load_data)
        self.Monitor_load.setText("Status:\nECEI data is not loaded")
        # IDA cross cal
        # self.tCalB_lbl_load = QLabel(self.Load_data)
        # self.tCalB_lbl_load.setText('tCalB:')
        # self.tCalE_lbl_load = QLabel(self.Load_data)
        # self.tCalE_lbl_load.setText('tCalE:')
        # self.tCalB_ed_load = QLineEdit(self.Load_data)
        # self.tCalB_ed_load.setText('4.0')
        # self.tCalE_ed_load = QLineEdit(self.Load_data)
        # self.tCalE_ed_load.setText('4.5')
        # self.Butt_cal_load = QPushButton("Cross Calib with IDA",self.Load_data)
        # self.Butt_cal_load.clicked.connect(self.CrossCal_ECEI_data)

        # Add widgets to layout
        sublayout_load.setSpacing(5)
        sublayout_load.addWidget(self.Diag_lbl_load, 0, 0)
        sublayout_load.addWidget(self.Diag_load, 0, 1)
        sublayout_load.addWidget(self.Shot_lbl_load, 1, 0)
        sublayout_load.addWidget(self.Shot_ed_load, 1, 1)
        # sublayout_load.addWidget(self.Butt_load, 3, 0, 3, 0)
        sublayout_load.addWidget(self.Butt_load, 3, 1)
        # sublayout_load.addWidget(self.tCalB_lbl_load, 20, 0)
        # sublayout_load.addWidget(self.tCalB_ed_load, 20, 1)
        # sublayout_load.addWidget(self.tCalE_lbl_load, 20, 2)
        # sublayout_load.addWidget(self.tCalE_ed_load, 20, 3)
        # sublayout_load.addWidget(self.Butt_cal_load, 20, 4)
        sublayout_load.addWidget(self.Monitor_load, 8, 0, 8, 0)
        layout_load.addStretch()  # stretch free space (compress widgets at the top)


# ----------------------------------------------------------------------------------
        # Plot_chs tab - content
        # Create layouts
        layout_plCh = QtWidgets.QVBoxLayout(self.Plot_chs)  # main layout
        sublayout_plCh = QtWidgets.QGridLayout()  # layout for inputs
        layout_plCh.addLayout(sublayout_plCh)

        # Input widgets
        # time
        # labels
        self.tB_lbl_plCh = QLabel(self.Plot_chs)
        self.tB_lbl_plCh.setText('tB [s]:')
        self.tE_lbl_plCh = QLabel(self.Plot_chs)
        self.tE_lbl_plCh.setText('tE [s]:')
        self.tCnt_lbl_plCh = QLabel(self.Plot_chs)
        self.tCnt_lbl_plCh.setText('tCenter [s] (optional):')
        self.dt_lbl_plCh = QLabel(self.Plot_chs)
        self.dt_lbl_plCh.setText('dt [s](optional) :')
        self.Fourier_lbl0_plCh = QLabel(self.Plot_chs)
        self.Fourier_lbl0_plCh.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_plCh = QLabel(self.Plot_chs)
        self.Fourier2_lbl0_plCh.setText('Fourier highpass f [kHz]:')
        self.SavGol_lbl0_plCh = QLabel(self.Plot_chs)
        self.SavGol_lbl0_plCh.setText('SavGol win_len:')
        self.SavGol_lbl1_plCh = QLabel(self.Plot_chs)
        self.SavGol_lbl1_plCh.setText('SavGol pol_ord:')
        self.Binning_lbl_plCh = QLabel(self.Plot_chs)
        self.Binning_lbl_plCh.setText('Binning [kHz]:')
        self.FourMult_lbl_plCh = QLabel(self.Plot_chs)
        self.FourMult_lbl_plCh.setText('Fourier multiple f [kHz]:')

        # line edits
        self.tB_ed_plCh = QLineEdit(self.Plot_chs)
        self.tB_ed_plCh.setText('4.488525')
        self.tB_ed_plCh.setMinimumSize(QtCore.QSize(65, 0))
        self.tE_ed_plCh = QLineEdit(self.Plot_chs)
        self.tE_ed_plCh.setText('4.489525')
        self.tE_ed_plCh.setMinimumSize(QtCore.QSize(65, 0))
        self.tCnt_ed_plCh = QLineEdit(self.Plot_chs)
        self.dt_ed_plCh = QLineEdit(self.Plot_chs)
        self.dt_ed_plCh.setText('0.001')
        self.Butt_dt_plCh = QPushButton("Calc t", self.Plot_chs)
        self.Butt_dt_plCh.clicked.connect(lambda: self.tBE_from_tCnt(1))
        # Filters
        self.Fourier_cut_plCh = QLineEdit(self.Plot_chs)
        self.Fourier_cut_plCh.setText('30.0')
        self.Fourier2_cut_plCh = QLineEdit(self.Plot_chs)
        self.Fourier2_cut_plCh.setText('2.0')
        self.SavGol_ed0_plCh = QLineEdit(self.Plot_chs)
        self.SavGol_ed0_plCh.setText('21')
        self.SavGol_ed1_plCh = QLineEdit(self.Plot_chs)
        self.SavGol_ed1_plCh.setText('3')
        self.Binning_ed_plCh = QLineEdit(self.Plot_chs)
        self.Binning_ed_plCh.setText('60.0')
        self.FourMult_ed_plCh = QLineEdit(self.Plot_chs)
        self.FourMult_ed_plCh.setText('13.0,15.0;26,30')

        # what to plot
        self.type_plot_plCh = QComboBox(self.Plot_chs)
        self.type_plot_plCh.addItems(['no filter',
                                      'Fourier highpass',
                                      'Fourier lowpass',
                                      'Fourier both',
                                      'Fourier multiple',
                                      'SavGol',
                                      'Binning'])
        # plot buttom
        self.Butt_plot_plCh = QPushButton("Plot ECEIrel", self.Plot_chs)
        self.Butt_plot_plCh.clicked.connect(self.plot_chs_all)

        # Add widgets to layout
        # First row
        sublayout_plCh.setSpacing(2)
        sublayout_plCh.addWidget(self.tB_lbl_plCh, 0, 0)
        sublayout_plCh.addWidget(self.tB_ed_plCh, 0, 1)
        sublayout_plCh.addWidget(self.tE_lbl_plCh, 0, 2)
        sublayout_plCh.addWidget(self.tE_ed_plCh, 0, 3)
        sublayout_plCh.addWidget(self.tCnt_lbl_plCh, 0, 4)
        sublayout_plCh.addWidget(self.tCnt_ed_plCh, 0, 5)
        sublayout_plCh.addWidget(self.dt_lbl_plCh, 0, 6)
        sublayout_plCh.addWidget(self.dt_ed_plCh, 0, 7)
        sublayout_plCh.addWidget(self.Butt_dt_plCh, 0, 8)
        # Second row

        sublayout_plCh.addWidget(self.Fourier2_lbl0_plCh, 1, 0)
        sublayout_plCh.addWidget(self.Fourier2_cut_plCh, 1, 1)
        sublayout_plCh.addWidget(self.Fourier_lbl0_plCh, 1, 2)
        sublayout_plCh.addWidget(self.Fourier_cut_plCh, 1, 3)
        sublayout_plCh.addWidget(self.FourMult_lbl_plCh, 1, 4)
        sublayout_plCh.addWidget(self.FourMult_ed_plCh, 1, 5)

        sublayout_plCh.addWidget(self.SavGol_lbl0_plCh, 1, 6)
        sublayout_plCh.addWidget(self.SavGol_ed0_plCh, 1, 7)
        sublayout_plCh.addWidget(self.SavGol_lbl1_plCh, 1, 8)
        sublayout_plCh.addWidget(self.SavGol_ed1_plCh, 1, 9)

        sublayout_plCh.addWidget(self.Binning_lbl_plCh, 1, 10)
        sublayout_plCh.addWidget(self.Binning_ed_plCh, 1, 11)

        sublayout_plCh.addWidget(self.type_plot_plCh, 0, 12)
        sublayout_plCh.addWidget(self.Butt_plot_plCh, 1, 12)

        # Add matplotlib plot
        self.figure_plCh = Figure(figsize=(5, 3))
        self.static_canvas_plCh = FigureCanvas(self.figure_plCh)
        layout_plCh.addWidget(
            self.static_canvas_plCh,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_plCh.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_plCh,
            self.Plot_chs,
            coordinates=True)  # add toolbar below the plot
        layout_plCh.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_plCh.figure.subplots()  # add axes


# ----------------------------------------------------------------------------------
        # LOS tab - content
        # Create layouts
        layout_LOS = QtWidgets.QVBoxLayout(self.LOS_plot)  # main layout
        sublayout_LOS = QtWidgets.QGridLayout()  # layout for inputs
        layout_LOS.addLayout(sublayout_LOS)

        # Input widgets
        # time
        # labels
        self.tB_lbl_LOS = QLabel(self.LOS_plot)
        self.tB_lbl_LOS.setText('tB [s]:')
        self.tE_lbl_LOS = QLabel(self.LOS_plot)
        self.tE_lbl_LOS.setText('tE [s]:')
        self.tCnt_lbl_LOS = QLabel(self.LOS_plot)
        self.tCnt_lbl_LOS.setText('tCenter [s] (optional):')
        self.dt_lbl_LOS = QLabel(self.LOS_plot)
        self.dt_lbl_LOS.setText('dt [s](optional) :')
        self.NLOS_lbl_LOS = QLabel(self.LOS_plot)
        self.NLOS_lbl_LOS.setText('LOS :')
        self.Fourier_lbl0_LOS = QLabel(self.LOS_plot)
        self.Fourier_lbl0_LOS.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_LOS = QLabel(self.LOS_plot)
        self.Fourier2_lbl0_LOS.setText('Fourier highpass f [kHz]:')
        self.SavGol_lbl0_LOS = QLabel(self.LOS_plot)
        self.SavGol_lbl0_LOS.setText('SavGol win_len:')
        self.SavGol_lbl1_LOS = QLabel(self.LOS_plot)
        self.SavGol_lbl1_LOS.setText('SavGol pol_ord:')
        self.Binning_lbl_LOS = QLabel(self.LOS_plot)
        self.Binning_lbl_LOS.setText('Binning [kHz]:')

        self.FourMult_lbl_LOS = QLabel(self.LOS_plot)
        self.FourMult_lbl_LOS.setText('Fourier multiple f [kHz]:')

        # line edits
        self.tB_ed_LOS = QLineEdit(self.LOS_plot)
        self.tB_ed_LOS.setText('4.488525')
        self.tB_ed_LOS.setMinimumSize(QtCore.QSize(65, 0))
        self.tE_ed_LOS = QLineEdit(self.LOS_plot)
        self.tE_ed_LOS.setText('4.489525')
        self.tE_ed_LOS.setMinimumSize(QtCore.QSize(65, 0))
        self.tCnt_ed_LOS = QLineEdit(self.LOS_plot)
        self.tCnt_ed_LOS.setMinimumSize(QtCore.QSize(50, 0))
        self.dt_ed_LOS = QLineEdit(self.LOS_plot)
        self.dt_ed_LOS.setText('0.001')
        self.dt_ed_LOS.setMinimumSize(QtCore.QSize(50, 0))
        self.Butt_dt_LOS = QPushButton("Calc t", self.LOS_plot)
        self.Butt_dt_LOS.clicked.connect(lambda: self.tBE_from_tCnt(2))
        # Filters
        self.Fourier_cut_LOS = QLineEdit(self.LOS_plot)
        self.Fourier_cut_LOS.setText('30.0')
        self.Fourier2_cut_LOS = QLineEdit(self.LOS_plot)
        self.Fourier2_cut_LOS.setText('2.0')
        self.SavGol_ed0_LOS = QLineEdit(self.LOS_plot)
        self.SavGol_ed0_LOS.setText('21')
        self.SavGol_ed0_LOS.setMinimumSize(QtCore.QSize(30, 0))
        self.SavGol_ed1_LOS = QLineEdit(self.LOS_plot)
        self.SavGol_ed1_LOS.setText('3')
        self.SavGol_ed1_LOS.setMinimumSize(QtCore.QSize(30, 0))
        self.Binning_ed_LOS = QLineEdit(self.LOS_plot)
        self.Binning_ed_LOS.setText('60.0')
        self.Binning_ed_LOS.setMinimumSize(QtCore.QSize(40, 0))
        self.FourMult_ed_LOS = QLineEdit(self.LOS_plot)
        self.FourMult_ed_LOS.setText('13.0,15.0;26,30')
        self.FourMult_ed_LOS.setMinimumSize(QtCore.QSize(40, 0))

        # what to plot
        self.NLOS_type_LOS = QComboBox(self.LOS_plot)
        self.NLOS_type_LOS.addItems(['data not loaded'])

        self.type_plot_LOS = QComboBox(self.LOS_plot)
        self.type_plot_LOS.addItems(['no filter',
                                     'Fourier highpass',
                                     'Fourier lowpass',
                                     'Fourier both',
                                     'Fourier multiple',
                                     'SavGol',
                                     'Binning'])
        # plot buttom
        self.Butt_plot_LOS = QPushButton("Plot ECEIrel", self.LOS_plot)
        self.Butt_plot_LOS.clicked.connect(self.f_LOS_plot)

        # Add widgets to layout
        # First row
        sublayout_LOS.setSpacing(2)
        sublayout_LOS.addWidget(self.tB_lbl_LOS, 0, 0)
        sublayout_LOS.addWidget(self.tB_ed_LOS, 0, 1)
        sublayout_LOS.addWidget(self.tE_lbl_LOS, 0, 2)
        sublayout_LOS.addWidget(self.tE_ed_LOS, 0, 3)
        sublayout_LOS.addWidget(self.tCnt_lbl_LOS, 0, 4)
        sublayout_LOS.addWidget(self.tCnt_ed_LOS, 0, 5)
        sublayout_LOS.addWidget(self.dt_lbl_LOS, 0, 6)
        sublayout_LOS.addWidget(self.dt_ed_LOS, 0, 7)
        sublayout_LOS.addWidget(self.Butt_dt_LOS, 0, 8)
        # Second row

        sublayout_LOS.addWidget(self.Fourier2_lbl0_LOS, 1, 0)
        sublayout_LOS.addWidget(self.Fourier2_cut_LOS, 1, 1)
        sublayout_LOS.addWidget(self.Fourier_lbl0_LOS, 1, 2)
        sublayout_LOS.addWidget(self.Fourier_cut_LOS, 1, 3)
        sublayout_LOS.addWidget(self.FourMult_lbl_LOS, 1, 4)
        sublayout_LOS.addWidget(self.FourMult_ed_LOS, 1, 5)

        sublayout_LOS.addWidget(self.SavGol_lbl0_LOS, 1, 6)
        sublayout_LOS.addWidget(self.SavGol_ed0_LOS, 1, 7)
        sublayout_LOS.addWidget(self.SavGol_lbl1_LOS, 1, 8)
        sublayout_LOS.addWidget(self.SavGol_ed1_LOS, 1, 9)

        sublayout_LOS.addWidget(self.Binning_lbl_LOS, 1, 10)
        sublayout_LOS.addWidget(self.Binning_ed_LOS, 1, 11)

        sublayout_LOS.addWidget(self.NLOS_lbl_LOS, 0, 10)
        sublayout_LOS.addWidget(self.NLOS_type_LOS, 0, 11)
        sublayout_LOS.addWidget(self.type_plot_LOS, 0, 12)
        sublayout_LOS.addWidget(self.Butt_plot_LOS, 1, 12)

        # Add matplotlib plot
        self.figure_LOS = Figure(figsize=(5, 3))
        self.static_canvas_LOS = FigureCanvas(self.figure_LOS)
        layout_LOS.addWidget(
            self.static_canvas_LOS,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_LOS.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_LOS,
            self.LOS_plot,
            coordinates=True)  # add toolbar below the plot
        layout_LOS.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_LOS.figure.subplots()  # add axes

# ----------------------------------------------------------------------------------
        # LOS_FFT tab - content
        # Create layouts
        layout_FFT = QtWidgets.QVBoxLayout(self.FFT_plot)  # main layout
        sublayout_FFT = QtWidgets.QGridLayout()  # layout for inputs
        layout_FFT.addLayout(sublayout_FFT)

        # Input widgets
        # time
        # labels
        self.tB_lbl_FFT = QLabel(self.FFT_plot)
        self.tB_lbl_FFT.setText('tB [s]:')
        self.tE_lbl_FFT = QLabel(self.FFT_plot)
        self.tE_lbl_FFT.setText('tE [s]:')
        self.tCnt_lbl_FFT = QLabel(self.FFT_plot)
        self.tCnt_lbl_FFT.setText('tCenter [s] (optional):')
        self.dt_lbl_FFT = QLabel(self.FFT_plot)
        self.dt_lbl_FFT.setText('dt [s](optional) :')
        self.NLOS_lbl_FFT = QLabel(self.FFT_plot)
        self.NLOS_lbl_FFT.setText('LOS :')
        self.SavGol_lbl0_FFT = QLabel(self.FFT_plot)
        self.SavGol_lbl0_FFT.setText('SavGol win_len:')
        self.SavGol_lbl1_FFT = QLabel(self.FFT_plot)
        self.SavGol_lbl1_FFT.setText('SavGol pol_ord:')
        self.Fourier_lbl0_FFT = QLabel(self.FFT_plot)
        self.Fourier_lbl0_FFT.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_FFT = QLabel(self.FFT_plot)
        self.Fourier2_lbl0_FFT.setText('Fourier highpass f [kHz]:')
        self.Binning_lbl_FFT = QLabel(self.FFT_plot)
        self.Binning_lbl_FFT.setText('Binning [kHz]:')
        self.FourMult_lbl_FFT = QLabel(self.FFT_plot)
        self.FourMult_lbl_FFT.setText('Fourier multiple f [kHz]:')

        # line edits
        self.tB_ed_FFT = QLineEdit(self.FFT_plot)
        self.tB_ed_FFT.setText('4.488525')
        self.tB_ed_FFT.setMinimumSize(QtCore.QSize(65, 0))
        self.tE_ed_FFT = QLineEdit(self.FFT_plot)
        self.tE_ed_FFT.setText('4.489525')
        self.tE_ed_FFT.setMinimumSize(QtCore.QSize(65, 0))
        self.tCnt_ed_FFT = QLineEdit(self.FFT_plot)
        self.tCnt_ed_FFT.setMinimumSize(QtCore.QSize(50, 0))
        self.dt_ed_FFT = QLineEdit(self.FFT_plot)
        self.dt_ed_FFT.setText('0.001')
        self.dt_ed_FFT.setMinimumSize(QtCore.QSize(50, 0))
        self.Butt_dt_FFT = QPushButton("Calc t", self.FFT_plot)
        self.Butt_dt_FFT.clicked.connect(lambda: self.tBE_from_tCnt(3))
        # Filters
        self.Fourier_cut_FFT = QLineEdit(self.FFT_plot)
        self.Fourier_cut_FFT.setText('30.0')
        self.Fourier2_cut_FFT = QLineEdit(self.FFT_plot)
        self.Fourier2_cut_FFT.setText('2.0')
        self.SavGol_ed0_FFT = QLineEdit(self.FFT_plot)
        self.SavGol_ed0_FFT.setText('21')
        self.SavGol_ed0_FFT.setMinimumSize(QtCore.QSize(30, 0))
        self.SavGol_ed1_FFT = QLineEdit(self.FFT_plot)
        self.SavGol_ed1_FFT.setText('3')
        self.SavGol_ed1_FFT.setMinimumSize(QtCore.QSize(30, 0))
        self.Binning_ed_FFT = QLineEdit(self.FFT_plot)
        self.Binning_ed_FFT.setText('60.0')
        self.Binning_ed_FFT.setMinimumSize(QtCore.QSize(40, 0))
        self.FourMult_ed_FFT = QLineEdit(self.FFT_plot)
        self.FourMult_ed_FFT.setText('13.0,15.0;26,30')
        self.FourMult_ed_FFT.setMinimumSize(QtCore.QSize(40, 0))

        # what to plot
        self.NLOS_type_FFT = QComboBox(self.FFT_plot)
        self.NLOS_type_FFT.addItems(['data not loaded'])

        self.type_plot_FFT = QComboBox(self.FFT_plot)
        self.type_plot_FFT.addItems(['no filter',
                                     'Fourier highpass',
                                     'Fourier lowpass',
                                     'Fourier both',
                                     'Fourier multiple',
                                     'SavGol',
                                     'Binning'])
        # plot buttom
        self.Butt_plot_FFT = QPushButton("Plot ECEIrel", self.FFT_plot)
        self.Butt_plot_FFT.clicked.connect(self.f_FFT_plot)

        # Add widgets to layout
        # First row
        sublayout_FFT.setSpacing(2)
        sublayout_FFT.addWidget(self.tB_lbl_FFT, 0, 0)
        sublayout_FFT.addWidget(self.tB_ed_FFT, 0, 1)
        sublayout_FFT.addWidget(self.tE_lbl_FFT, 0, 2)
        sublayout_FFT.addWidget(self.tE_ed_FFT, 0, 3)
        sublayout_FFT.addWidget(self.tCnt_lbl_FFT, 0, 4)
        sublayout_FFT.addWidget(self.tCnt_ed_FFT, 0, 5)
        sublayout_FFT.addWidget(self.dt_lbl_FFT, 0, 6)
        sublayout_FFT.addWidget(self.dt_ed_FFT, 0, 7)
        sublayout_FFT.addWidget(self.Butt_dt_FFT, 0, 8)
        # Second row

        sublayout_FFT.addWidget(self.Fourier2_lbl0_FFT, 1, 0)
        sublayout_FFT.addWidget(self.Fourier2_cut_FFT, 1, 1)
        sublayout_FFT.addWidget(self.Fourier_lbl0_FFT, 1, 2)
        sublayout_FFT.addWidget(self.Fourier_cut_FFT, 1, 3)
        sublayout_FFT.addWidget(self.FourMult_lbl_FFT, 1, 4)
        sublayout_FFT.addWidget(self.FourMult_ed_FFT, 1, 5)

        sublayout_FFT.addWidget(self.SavGol_lbl0_FFT, 1, 6)
        sublayout_FFT.addWidget(self.SavGol_ed0_FFT, 1, 7)
        sublayout_FFT.addWidget(self.SavGol_lbl1_FFT, 1, 8)
        sublayout_FFT.addWidget(self.SavGol_ed1_FFT, 1, 9)
        sublayout_FFT.addWidget(self.Binning_lbl_FFT, 1, 10)
        sublayout_FFT.addWidget(self.Binning_ed_FFT, 1, 11)

        sublayout_FFT.addWidget(self.NLOS_lbl_FFT, 0, 10)
        sublayout_FFT.addWidget(self.NLOS_type_FFT, 0, 11)
        sublayout_FFT.addWidget(self.type_plot_FFT, 0, 12)
        sublayout_FFT.addWidget(self.Butt_plot_FFT, 1, 12)

        # Add matplotlib plot
        self.figure_FFT = Figure(figsize=(5, 3))
        self.static_canvas_FFT = FigureCanvas(self.figure_FFT)
        layout_FFT.addWidget(
            self.static_canvas_FFT,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_FFT.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_FFT,
            self.FFT_plot,
            coordinates=True)  # add toolbar below the plot
        layout_FFT.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_FFT.figure.subplots()  # add axes

# ----------------------------------------------------------------------------------

        # R trace tab - content
        # Create layouts
        layout_Rtr = QtWidgets.QVBoxLayout(self.R_trace)  # main layout
        sublayout_Rtr = QtWidgets.QGridLayout()  # layout for inputs
        layout_Rtr.addLayout(sublayout_Rtr)

        # Input widgets
        # time
        # labels
        # time labels
        self.tB_lbl_Rtr = QLabel(self.R_trace)
        self.tB_lbl_Rtr.setText('tB [s]:')
        self.tE_lbl_Rtr = QLabel(self.R_trace)
        self.tE_lbl_Rtr.setText('tE [s]:')
        self.tCnt_lbl_Rtr = QLabel(self.R_trace)
        self.tCnt_lbl_Rtr.setText('tCenter [s] (optional):')
        self.dt_lbl_Rtr = QLabel(self.R_trace)
        self.dt_lbl_Rtr.setText('dt [s](optional) :')
        # filter labels
        self.Fourier_lbl0_Rtr = QLabel(self.R_trace)
        self.Fourier_lbl0_Rtr.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_Rtr = QLabel(self.R_trace)
        self.Fourier2_lbl0_Rtr.setText('Fourier highpass f [kHz]:')
        self.SavGol_lbl0_Rtr = QLabel(self.R_trace)
        self.SavGol_lbl0_Rtr.setText('SavGol win_len:')
        self.SavGol_lbl1_Rtr = QLabel(self.R_trace)
        self.SavGol_lbl1_Rtr.setText('SavGol pol_ord:')
        self.Binning_lbl_Rtr = QLabel(self.R_trace)
        self.Binning_lbl_Rtr.setText('Binning [kHz]:')
        self.Contour_lbl_Rtr = QLabel(self.R_trace)
        self.Contour_lbl_Rtr.setText('Contour [1 or 0]')
        self.NNcont_lbl_Rtr = QLabel(self.R_trace)
        self.NNcont_lbl_Rtr.setText('NNcont:')
        self.FourMult_lbl_Rtr = QLabel(self.R_trace)
        self.FourMult_lbl_Rtr.setText('Fourier multiple f [kHz]:')

        # plot params labels
        self.vmin_lbl_Rtr = QLabel(self.R_trace)
        self.vmin_lbl_Rtr.setText('vmin:')
        self.vmax_lbl_Rtr = QLabel(self.R_trace)
        self.vmax_lbl_Rtr.setText('vmax:')
        self.chzz_lbl_Rtr = QLabel(self.R_trace)
        self.chzz_lbl_Rtr.setText('Remove LOS:')
        self.chRR_lbl_Rtr = QLabel(self.R_trace)
        self.chRR_lbl_Rtr.setText('Remove R chs:')

        # line edits
        # time edits
        self.tB_ed_Rtr = QLineEdit(self.R_trace)
        self.tB_ed_Rtr.setText('4.488525')
        self.tB_ed_Rtr.setMinimumSize(QtCore.QSize(65, 0))
        self.tE_ed_Rtr = QLineEdit(self.R_trace)
        self.tE_ed_Rtr.setText('4.489525')
        self.tE_ed_Rtr.setMinimumSize(QtCore.QSize(65, 0))
        self.tCnt_ed_Rtr = QLineEdit(self.R_trace)
        self.tCnt_ed_Rtr.setMinimumSize(QtCore.QSize(50, 0))
        self.dt_ed_Rtr = QLineEdit(self.R_trace)
        self.dt_ed_Rtr.setText('0.001')
        self.dt_ed_Rtr.setMinimumSize(QtCore.QSize(50, 0))
        self.Butt_dt_Rtr = QPushButton("Calc t", self.R_trace)
        self.Butt_dt_Rtr.clicked.connect(lambda: self.tBE_from_tCnt(4))
        # plot params edits
        self.vmin_ed_Rtr = QLineEdit(self.R_trace)
        self.vmin_ed_Rtr.setText('None')
        self.vmin_ed_Rtr.setMinimumSize(QtCore.QSize(40, 0))
        self.vmax_ed_Rtr = QLineEdit(self.R_trace)
        self.vmax_ed_Rtr.setText('None')
        self.vmax_ed_Rtr.setMinimumSize(QtCore.QSize(40, 0))
        self.chzz_ed_Rtr = QLineEdit(self.R_trace)
        self.chRR_ed_Rtr = QLineEdit(self.R_trace)
        # Filters edits
        self.Fourier_cut_Rtr = QLineEdit(self.R_trace)
        self.Fourier_cut_Rtr.setText('30.0')
        self.Fourier2_cut_Rtr = QLineEdit(self.R_trace)
        self.Fourier2_cut_Rtr.setText('2.0')
        self.SavGol_ed0_Rtr = QLineEdit(self.R_trace)
        self.SavGol_ed0_Rtr.setText('21')
        self.SavGol_ed0_Rtr.setMinimumSize(QtCore.QSize(20, 0))
        self.SavGol_ed1_Rtr = QLineEdit(self.R_trace)
        self.SavGol_ed1_Rtr.setText('3')
        self.Binning_ed_Rtr = QLineEdit(self.R_trace)
        self.Binning_ed_Rtr.setText('60.0')
        self.Binning_ed_Rtr.setMinimumSize(QtCore.QSize(40, 0))
        self.Contour_ed_Rtr = QLineEdit(self.R_trace)
        self.Contour_ed_Rtr.setText('0')
        self.NNcont_ed_Rtr = QLineEdit(self.R_trace)
        self.NNcont_ed_Rtr.setText('20')
        self.FourMult_ed_Rtr = QLineEdit(self.R_trace)
        self.FourMult_ed_Rtr.setText('13.0,15.0;26,30')
        self.FourMult_ed_Rtr.setMinimumSize(QtCore.QSize(40, 0))

        # what to plot (type of filter)
        self.type_plot_Rtr = QComboBox(self.R_trace)
        self.type_plot_Rtr.addItems(['no filter',
                                     'Fourier highpass',
                                     'Fourier lowpass',
                                     'Fourier both',
                                     'Fourier multiple',
                                     'SavGol',
                                     'Binning'])
        # plot buttom
        self.Butt_plot_Rtr = QPushButton("Plot ECEIrel", self.R_trace)
        self.Butt_plot_Rtr.clicked.connect(self.plot_R_trace)
        shortcut = QShortcut(QKeySequence("Ctrl+p"), self.Butt_plot_Rtr)
        shortcut.activated.connect(self.plot_R_trace)
        shortcut.setEnabled(True)

        # Add widgets to layout
        # First row
        sublayout_Rtr.setSpacing(2)
        sublayout_Rtr.addWidget(self.tB_lbl_Rtr, 0, 0)
        sublayout_Rtr.addWidget(self.tB_ed_Rtr, 0, 1)
        sublayout_Rtr.addWidget(self.tE_lbl_Rtr, 0, 2)
        sublayout_Rtr.addWidget(self.tE_ed_Rtr, 0, 3)
        sublayout_Rtr.addWidget(self.tCnt_lbl_Rtr, 0, 4)
        sublayout_Rtr.addWidget(self.tCnt_ed_Rtr, 0, 5)
        sublayout_Rtr.addWidget(self.dt_lbl_Rtr, 0, 6)
        sublayout_Rtr.addWidget(self.dt_ed_Rtr, 0, 7)
        sublayout_Rtr.addWidget(self.Butt_dt_Rtr, 0, 8)
        ######
        # Second row
        sublayout_Rtr.addWidget(self.Fourier2_lbl0_Rtr, 1, 0)
        sublayout_Rtr.addWidget(self.Fourier2_cut_Rtr, 1, 1)
        sublayout_Rtr.addWidget(self.Fourier_lbl0_Rtr, 1, 2)
        sublayout_Rtr.addWidget(self.Fourier_cut_Rtr, 1, 3)
        sublayout_Rtr.addWidget(self.FourMult_lbl_Rtr, 1, 4)
        sublayout_Rtr.addWidget(self.FourMult_ed_Rtr, 1, 5)
        ######
        sublayout_Rtr.addWidget(self.SavGol_lbl0_Rtr, 1, 6)
        sublayout_Rtr.addWidget(self.SavGol_ed0_Rtr, 1, 7)
        sublayout_Rtr.addWidget(self.SavGol_lbl1_Rtr, 1, 8)
        sublayout_Rtr.addWidget(self.SavGol_ed1_Rtr, 1, 9)
        sublayout_Rtr.addWidget(self.Binning_lbl_Rtr, 1, 10)
        sublayout_Rtr.addWidget(self.Binning_ed_Rtr, 1, 11)
        ######
        # Third row
        ######
        sublayout_Rtr.addWidget(self.chzz_lbl_Rtr, 2, 0)
        sublayout_Rtr.addWidget(self.chzz_ed_Rtr, 2, 1)
        sublayout_Rtr.addWidget(self.chRR_lbl_Rtr, 2, 2)
        sublayout_Rtr.addWidget(self.chRR_ed_Rtr, 2, 3)
        ######
        sublayout_Rtr.addWidget(self.Contour_lbl_Rtr, 2, 8)
        sublayout_Rtr.addWidget(self.Contour_ed_Rtr, 2, 9)
        sublayout_Rtr.addWidget(self.NNcont_lbl_Rtr, 2, 10)
        sublayout_Rtr.addWidget(self.NNcont_ed_Rtr, 2, 11)
        ######
        sublayout_Rtr.addWidget(self.vmin_lbl_Rtr, 2, 4)
        sublayout_Rtr.addWidget(self.vmin_ed_Rtr, 2, 5)
        sublayout_Rtr.addWidget(self.vmax_lbl_Rtr, 2, 6)
        sublayout_Rtr.addWidget(self.vmax_ed_Rtr, 2, 7)
        ######
        sublayout_Rtr.addWidget(self.type_plot_Rtr, 1, 12)
        sublayout_Rtr.addWidget(self.Butt_plot_Rtr, 2, 12)

        # Add matplotlib plot
        self.figure_Rtr = Figure(figsize=(5, 3))
        self.static_canvas_Rtr = FigureCanvas(self.figure_Rtr)
        layout_Rtr.addWidget(
            self.static_canvas_Rtr,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_Rtr.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_Rtr,
            self.R_trace,
            coordinates=True)  # add toolbar below the plot
        layout_Rtr.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_Rtr.figure.subplots()  # add axes


# ----------------------------------------------------------------------------------

        # R Single tab - content
        # Create layouts
        layout_Rsing = QtWidgets.QVBoxLayout(self.R_single)  # main layout
        sublayout_Rsing = QtWidgets.QGridLayout()  # layout for inputs
        layout_Rsing.addLayout(sublayout_Rsing)

        # Input widgets
        # time
        # labels
        # time labels
        self.tB_lbl_Rsing = QLabel(self.R_single)
        self.tB_lbl_Rsing.setText('tB [s]:')
        self.tE_lbl_Rsing = QLabel(self.R_single)
        self.tE_lbl_Rsing.setText('tE [s]:')
        self.tCnt_lbl_Rsing = QLabel(self.R_single)
        self.tCnt_lbl_Rsing.setText('tCenter [s] (optional):')
        self.dt_lbl_Rsing = QLabel(self.R_single)
        self.dt_lbl_Rsing.setText('dt [s](optional) :')
        # filter labels
        self.Fourier_lbl0_Rsing = QLabel(self.R_single)
        self.Fourier_lbl0_Rsing.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_Rsing = QLabel(self.R_single)
        self.Fourier2_lbl0_Rsing.setText('Fourier highpass f [kHz]:')
        self.SavGol_lbl0_Rsing = QLabel(self.R_single)
        self.SavGol_lbl0_Rsing.setText('SavGol win_len:')
        self.SavGol_lbl1_Rsing = QLabel(self.R_single)
        self.SavGol_lbl1_Rsing.setText('SavGol pol_ord:')
        self.Binning_lbl_Rsing = QLabel(self.R_single)
        self.Binning_lbl_Rsing.setText('Binning [kHz]:')
        self.Contour_lbl_Rsing = QLabel(self.R_single)
        self.Contour_lbl_Rsing.setText('Contour [1 or 0]')
        self.NNcont_lbl_Rsing = QLabel(self.R_single)
        self.NNcont_lbl_Rsing.setText('NNcont:')
        self.LOStype_lbl_Rsing = QLabel(self.R_single)
        self.LOStype_lbl_Rsing.setText('LOS:')
        self.FourMult_lbl_Rsing = QLabel(self.R_single)
        self.FourMult_lbl_Rsing.setText('Fourier multiple f [kHz]:')
        # plot params labels
        self.vmin_lbl_Rsing = QLabel(self.R_single)
        self.vmin_lbl_Rsing.setText('vmin:')
        self.vmax_lbl_Rsing = QLabel(self.R_single)
        self.vmax_lbl_Rsing.setText('vmax:')
        self.chRR_lbl_Rsing = QLabel(self.R_single)
        self.chRR_lbl_Rsing.setText('Remove R chs:')

        # line edits
        # time edits
        self.tB_ed_Rsing = QLineEdit(self.R_single)
        self.tB_ed_Rsing.setText('4.488525')
        self.tB_ed_Rsing.setMinimumSize(QtCore.QSize(65, 0))
        self.tE_ed_Rsing = QLineEdit(self.R_single)
        self.tE_ed_Rsing.setText('4.489525')
        self.tE_ed_Rsing.setMinimumSize(QtCore.QSize(65, 0))
        self.tCnt_ed_Rsing = QLineEdit(self.R_single)
        self.tCnt_ed_Rsing.setMinimumSize(QtCore.QSize(50, 0))
        self.dt_ed_Rsing = QLineEdit(self.R_single)
        self.dt_ed_Rsing.setText('0.001')
        self.dt_ed_Rsing.setMinimumSize(QtCore.QSize(50, 0))
        self.Butt_dt_Rsing = QPushButton("Calc t", self.R_single)
        self.Butt_dt_Rsing.clicked.connect(lambda: self.tBE_from_tCnt(5))
        # plot params edits
        self.vmin_ed_Rsing = QLineEdit(self.R_single)
        self.vmin_ed_Rsing.setText('None')
        self.vmin_ed_Rsing.setMinimumSize(QtCore.QSize(40, 0))
        self.vmax_ed_Rsing = QLineEdit(self.R_single)
        self.vmax_ed_Rsing.setText('None')
        self.vmax_ed_Rsing.setMinimumSize(QtCore.QSize(40, 0))
        self.chRR_ed_Rsing = QLineEdit(self.R_single)
        # Filters edits
        self.Fourier_cut_Rsing = QLineEdit(self.R_single)
        self.Fourier_cut_Rsing.setText('30.0')
        self.Fourier2_cut_Rsing = QLineEdit(self.R_single)
        self.Fourier2_cut_Rsing.setText('2.0')
        self.SavGol_ed0_Rsing = QLineEdit(self.R_single)
        self.SavGol_ed0_Rsing.setText('21')
        self.SavGol_ed0_Rsing.setMinimumSize(QtCore.QSize(20, 0))
        self.SavGol_ed1_Rsing = QLineEdit(self.R_single)
        self.SavGol_ed1_Rsing.setText('3')
        self.Binning_ed_Rsing = QLineEdit(self.R_single)
        self.Binning_ed_Rsing.setText('60.0')
        self.Binning_ed_Rsing.setMinimumSize(QtCore.QSize(40, 0))
        self.Contour_ed_Rsing = QLineEdit(self.R_single)
        self.Contour_ed_Rsing.setText('0')
        self.NNcont_ed_Rsing = QLineEdit(self.R_single)
        self.NNcont_ed_Rsing.setText('20')
        self.FourMult_ed_Rsing = QLineEdit(self.R_single)
        self.FourMult_ed_Rsing.setText('13.0,15.0;26,30')

        # what to plot (type of filter)
        self.type_plot_Rsing = QComboBox(self.R_single)
        self.type_plot_Rsing.addItems(['no filter',
                                       'Fourier highpass',
                                       'Fourier lowpass',
                                       'Fourier both',
                                       'Fourier multiple',
                                       'SavGol',
                                       'Binning'])
        self.LOS_type_Rsing = QComboBox(self.R_single)
        self.LOS_type_Rsing.addItems(['data not loaded'])
        # plot buttom
        self.Butt_plot_Rsing = QPushButton("Plot ECEIrel", self.R_single)
        self.Butt_plot_Rsing.clicked.connect(self.plot_R_single)
        shortcut = QShortcut(QKeySequence("Ctrl+p"), self.Butt_plot_Rsing)
        shortcut.activated.connect(self.plot_R_single)
        shortcut.setEnabled(True)

        # Add widgets to layout
        # First row
        sublayout_Rsing.setSpacing(2)
        sublayout_Rsing.addWidget(self.tB_lbl_Rsing, 0, 0)
        sublayout_Rsing.addWidget(self.tB_ed_Rsing, 0, 1)
        sublayout_Rsing.addWidget(self.tE_lbl_Rsing, 0, 2)
        sublayout_Rsing.addWidget(self.tE_ed_Rsing, 0, 3)
        sublayout_Rsing.addWidget(self.tCnt_lbl_Rsing, 0, 4)
        sublayout_Rsing.addWidget(self.tCnt_ed_Rsing, 0, 5)
        sublayout_Rsing.addWidget(self.dt_lbl_Rsing, 0, 6)
        sublayout_Rsing.addWidget(self.dt_ed_Rsing, 0, 7)
        sublayout_Rsing.addWidget(self.Butt_dt_Rsing, 0, 8)
        ######
        # Second row
        sublayout_Rsing.addWidget(self.Fourier2_lbl0_Rsing, 1, 0)
        sublayout_Rsing.addWidget(self.Fourier2_cut_Rsing, 1, 1)
        sublayout_Rsing.addWidget(self.Fourier_lbl0_Rsing, 1, 2)
        sublayout_Rsing.addWidget(self.Fourier_cut_Rsing, 1, 3)
        sublayout_Rsing.addWidget(self.FourMult_lbl_Rsing, 1, 4)
        sublayout_Rsing.addWidget(self.FourMult_ed_Rsing, 1, 5)
        ######
        sublayout_Rsing.addWidget(self.SavGol_lbl0_Rsing, 1, 6)
        sublayout_Rsing.addWidget(self.SavGol_ed0_Rsing, 1, 7)
        sublayout_Rsing.addWidget(self.SavGol_lbl1_Rsing, 1, 8)
        sublayout_Rsing.addWidget(self.SavGol_ed1_Rsing, 1, 9)
        sublayout_Rsing.addWidget(self.Binning_lbl_Rsing, 1, 10)
        sublayout_Rsing.addWidget(self.Binning_ed_Rsing, 1, 11)
        ######
        # Third row
        sublayout_Rsing.addWidget(self.chRR_lbl_Rsing, 2, 2)
        sublayout_Rsing.addWidget(self.chRR_ed_Rsing, 2, 3)
        ######
        sublayout_Rsing.addWidget(self.vmin_lbl_Rsing, 2, 4)
        sublayout_Rsing.addWidget(self.vmin_ed_Rsing, 2, 5)
        sublayout_Rsing.addWidget(self.vmax_lbl_Rsing, 2, 6)
        sublayout_Rsing.addWidget(self.vmax_ed_Rsing, 2, 7)
        sublayout_Rsing.addWidget(self.Contour_lbl_Rsing, 2, 8)
        sublayout_Rsing.addWidget(self.Contour_ed_Rsing, 2, 9)
        sublayout_Rsing.addWidget(self.NNcont_lbl_Rsing, 2, 10)
        sublayout_Rsing.addWidget(self.NNcont_ed_Rsing, 2, 11)
        ######
        sublayout_Rsing.addWidget(self.LOStype_lbl_Rsing, 0, 11)
        sublayout_Rsing.addWidget(self.LOS_type_Rsing, 0, 12)
        sublayout_Rsing.addWidget(self.type_plot_Rsing, 1, 12)
        sublayout_Rsing.addWidget(self.Butt_plot_Rsing, 2, 12)

        # Add matplotlib plot
        self.figure_Rsing = Figure(figsize=(5, 3))
        self.static_canvas_Rsing = FigureCanvas(self.figure_Rsing)
        layout_Rsing.addWidget(
            self.static_canvas_Rsing,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_Rsing.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_Rsing,
            self.R_single,
            coordinates=True)  # add toolbar below the plot
        layout_Rsing.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_Rsing.figure.subplots()  # add axes

# ----------------------------------------------------------------------------------

        # Z trace tab - content

        # Create layouts
        layout_Ztr = QtWidgets.QVBoxLayout(self.Z_trace)  # main layout
        sublayout_Ztr = QtWidgets.QGridLayout()  # layout for inputs
        layout_Ztr.addLayout(sublayout_Ztr)

        # Input widgets
        # labels
        self.tB_lbl_Ztr = QLabel(self.Z_trace)
        self.tB_lbl_Ztr.setText('tB [s]:')
        self.tE_lbl_Ztr = QLabel(self.Z_trace)
        self.tE_lbl_Ztr.setText('tE [s]:')
        self.tCnt_lbl_Ztr = QLabel(self.Z_trace)
        self.tCnt_lbl_Ztr.setText('tCenter [s] (optional):')
        self.dt_lbl_Ztr = QLabel(self.Z_trace)
        self.dt_lbl_Ztr.setText('dt [s](optional) :')
        # filter labels
        self.Fourier_lbl0_Ztr = QLabel(self.Z_trace)
        self.Fourier_lbl0_Ztr.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_Ztr = QLabel(self.Z_trace)
        self.Fourier2_lbl0_Ztr.setText('Fourier highpass f [kHz]:')
        self.SavGol_lbl0_Ztr = QLabel(self.Z_trace)
        self.SavGol_lbl0_Ztr.setText('SavGol win_len:')
        self.SavGol_lbl1_Ztr = QLabel(self.Z_trace)
        self.SavGol_lbl1_Ztr.setText('SavGol pol_ord:')
        self.Binning_lbl_Ztr = QLabel(self.Z_trace)
        self.Binning_lbl_Ztr.setText('Binning [kHz]:')
        self.Contour_lbl_Ztr = QLabel(self.Z_trace)
        self.Contour_lbl_Ztr.setText('Contour [1 or 0]:')
        self.NNcont_lbl_Ztr = QLabel(self.Z_trace)
        self.NNcont_lbl_Ztr.setText('NNcont:')
        self.FourMult_lbl_Ztr = QLabel(self.Z_trace)
        self.FourMult_lbl_Ztr.setText('Fourier multiple f [kHz]:')
        # plot params labels
        self.vmin_lbl_Ztr = QLabel(self.Z_trace)
        self.vmin_lbl_Ztr.setText('vmin:')
        self.vmax_lbl_Ztr = QLabel(self.Z_trace)
        self.vmax_lbl_Ztr.setText('vmax:')
        self.chzz_lbl_Ztr = QLabel(self.Z_trace)
        self.chzz_lbl_Ztr.setText('Remove LOS:')

        # line edits
        # time edits
        self.tB_ed_Ztr = QLineEdit(self.Z_trace)
        self.tB_ed_Ztr.setText('4.488525')
        self.tB_ed_Ztr.setMinimumSize(QtCore.QSize(65, 0))
        self.tE_ed_Ztr = QLineEdit(self.Z_trace)
        self.tE_ed_Ztr.setText('4.489525')
        self.tE_ed_Ztr.setMinimumSize(QtCore.QSize(65, 0))
        self.tCnt_ed_Ztr = QLineEdit(self.Z_trace)
        self.tCnt_ed_Ztr.setMinimumSize(QtCore.QSize(50, 0))
        self.dt_ed_Ztr = QLineEdit(self.Z_trace)
        self.dt_ed_Ztr.setText('0.001')
        self.dt_ed_Ztr.setMinimumSize(QtCore.QSize(50, 0))
        self.Butt_dt_Ztr = QPushButton("Calc t", self.Z_trace)
        self.Butt_dt_Ztr.clicked.connect(lambda: self.tBE_from_tCnt(6))
        # plot params edits
        self.vmin_ed_Ztr = QLineEdit(self.Z_trace)
        self.vmin_ed_Ztr.setText('None')
        self.vmax_ed_Ztr = QLineEdit(self.Z_trace)
        self.vmax_ed_Ztr.setText('None')
        self.chzz_ed_Ztr = QLineEdit(self.Z_trace)
        # self.chRR_ed_Ztr = QLineEdit(self.Z_trace)
        # Filters edits
        self.Fourier_cut_Ztr = QLineEdit(self.Z_trace)
        self.Fourier_cut_Ztr.setText('30.0')
        self.Fourier2_cut_Ztr = QLineEdit(self.Z_trace)
        self.Fourier2_cut_Ztr.setText('2.0')
        self.SavGol_ed0_Ztr = QLineEdit(self.Z_trace)
        self.SavGol_ed0_Ztr.setText('21')
        self.SavGol_ed1_Ztr = QLineEdit(self.Z_trace)
        self.SavGol_ed1_Ztr.setText('3')
        self.Binning_ed_Ztr = QLineEdit(self.Z_trace)
        self.Binning_ed_Ztr.setText('60.0')
        self.Contour_ed_Ztr = QLineEdit(self.Z_trace)
        self.Contour_ed_Ztr.setText('0')
        self.NNcont_ed_Ztr = QLineEdit(self.Z_trace)
        self.NNcont_ed_Ztr.setText('20')
        self.FourMult_ed_Ztr = QLineEdit(self.Z_trace)
        self.FourMult_ed_Ztr.setText('13.0,15.0;26,30')

        # what to plot (type of filter)
        self.type_plot_Ztr = QComboBox(self.Z_trace)
        self.type_plot_Ztr.addItems(['no filter',
                                     'Fourier highpass',
                                     'Fourier lowpass',
                                     'Fourier both',
                                     'Fourier multiple',
                                     'SavGol',
                                     'Binning'])
        # plot buttom
        self.Butt_plot_Ztr = QPushButton("Plot ECEIrel", self.Z_trace)
        self.Butt_plot_Ztr.clicked.connect(self.plot_Z_trace)

        # Add widgets to layout
        # First row
        sublayout_Ztr.setSpacing(2)
        sublayout_Ztr.addWidget(self.tB_lbl_Ztr, 0, 0)
        sublayout_Ztr.addWidget(self.tB_ed_Ztr, 0, 1)
        sublayout_Ztr.addWidget(self.tE_lbl_Ztr, 0, 2)
        sublayout_Ztr.addWidget(self.tE_ed_Ztr, 0, 3)
        sublayout_Ztr.addWidget(self.tCnt_lbl_Ztr, 0, 4)
        sublayout_Ztr.addWidget(self.tCnt_ed_Ztr, 0, 5)
        sublayout_Ztr.addWidget(self.dt_lbl_Ztr, 0, 6)
        sublayout_Ztr.addWidget(self.dt_ed_Ztr, 0, 7)
        sublayout_Ztr.addWidget(self.Butt_dt_Ztr, 0, 8)

        # Second row
        sublayout_Ztr.addWidget(self.Fourier2_lbl0_Ztr, 1, 0)
        sublayout_Ztr.addWidget(self.Fourier2_cut_Ztr, 1, 1)
        sublayout_Ztr.addWidget(self.Fourier_lbl0_Ztr, 1, 2)
        sublayout_Ztr.addWidget(self.Fourier_cut_Ztr, 1, 3)
        sublayout_Ztr.addWidget(self.FourMult_lbl_Ztr, 1, 4)
        sublayout_Ztr.addWidget(self.FourMult_ed_Ztr, 1, 5)
        ######
        sublayout_Ztr.addWidget(self.SavGol_lbl0_Ztr, 1, 6)
        sublayout_Ztr.addWidget(self.SavGol_ed0_Ztr, 1, 7)
        sublayout_Ztr.addWidget(self.SavGol_lbl1_Ztr, 1, 8)
        sublayout_Ztr.addWidget(self.SavGol_ed1_Ztr, 1, 9)
        sublayout_Ztr.addWidget(self.Binning_lbl_Ztr, 1, 10)
        sublayout_Ztr.addWidget(self.Binning_ed_Ztr, 1, 11)
        ######
        # Third row
        sublayout_Ztr.addWidget(self.chzz_lbl_Ztr, 2, 0)
        sublayout_Ztr.addWidget(self.chzz_ed_Ztr, 2, 1)
        ######
        sublayout_Ztr.addWidget(self.vmin_lbl_Ztr, 2, 4)
        sublayout_Ztr.addWidget(self.vmin_ed_Ztr, 2, 5)
        sublayout_Ztr.addWidget(self.vmax_lbl_Ztr, 2, 6)
        sublayout_Ztr.addWidget(self.vmax_ed_Ztr, 2, 7)
        ######
        sublayout_Ztr.addWidget(self.Contour_lbl_Ztr, 2, 8)
        sublayout_Ztr.addWidget(self.Contour_ed_Ztr, 2, 9)
        sublayout_Ztr.addWidget(self.NNcont_lbl_Ztr, 2, 10)
        sublayout_Ztr.addWidget(self.NNcont_ed_Ztr, 2, 11)
        ######
        sublayout_Ztr.addWidget(self.type_plot_Ztr, 1, 12)
        sublayout_Ztr.addWidget(self.Butt_plot_Ztr, 2, 12)

        # Add matplotlib plot
        self.figure_Ztr = Figure(figsize=(5, 3))
        self.static_canvas_Ztr = FigureCanvas(self.figure_Ztr)
        layout_Ztr.addWidget(
            self.static_canvas_Ztr,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_Ztr.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_Ztr,
            self.Z_trace,
            coordinates=True)  # add toolbar below the plot
        layout_Ztr.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_Ztr.figure.subplots()  # add axes


# ----------------------------------------------------------------------------------

        # Z Single tab - content

        # Create layouts
        layout_Zsing = QtWidgets.QVBoxLayout(self.Z_single)  # main layout
        sublayout_Zsing = QtWidgets.QGridLayout()  # layout for inputs
        layout_Zsing.addLayout(sublayout_Zsing)

        # Input widgets
        # labels
        self.tB_lbl_Zsing = QLabel(self.Z_single)
        self.tB_lbl_Zsing.setText('tB [s]:')
        self.tE_lbl_Zsing = QLabel(self.Z_single)
        self.tE_lbl_Zsing.setText('tE [s]:')
        self.tCnt_lbl_Zsing = QLabel(self.Z_single)
        self.tCnt_lbl_Zsing.setText('tCenter [s] (optional):')
        self.dt_lbl_Zsing = QLabel(self.Z_single)
        self.dt_lbl_Zsing.setText('dt [s](optional) :')
        # filter labels
        self.Fourier_lbl0_Zsing = QLabel(self.Z_single)
        self.Fourier_lbl0_Zsing.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_Zsing = QLabel(self.Z_single)
        self.Fourier2_lbl0_Zsing.setText('Fourier highpass f [kHz]:')
        self.SavGol_lbl0_Zsing = QLabel(self.Z_single)
        self.SavGol_lbl0_Zsing.setText('SavGol win_len:')
        self.SavGol_lbl1_Zsing = QLabel(self.Z_single)
        self.SavGol_lbl1_Zsing.setText('SavGol pol_ord:')
        self.Binning_lbl_Zsing = QLabel(self.Z_single)
        self.Binning_lbl_Zsing.setText('Binning [kHz]:')
        self.Contour_lbl_Zsing = QLabel(self.Z_single)
        self.Contour_lbl_Zsing.setText('Contour [1 or 0]:')
        self.NNcont_lbl_Zsing = QLabel(self.Z_single)
        self.NNcont_lbl_Zsing.setText('NNcont:')
        self.Rtype_lbl_Zsing = QLabel(self.Z_single)
        self.Rtype_lbl_Zsing.setText('R:')
        # plot params labels
        self.vmin_lbl_Zsing = QLabel(self.Z_single)
        self.vmin_lbl_Zsing.setText('vmin:')
        self.vmax_lbl_Zsing = QLabel(self.Z_single)
        self.vmax_lbl_Zsing.setText('vmax:')
        self.chzz_lbl_Zsing = QLabel(self.Z_single)
        self.chzz_lbl_Zsing.setText('Remove LOS:')
        self.FourMult_lbl_Zsing = QLabel(self.Z_single)
        self.FourMult_lbl_Zsing.setText('Fourier multiple f [kHz]:')

        # line edits
        # time edits
        self.tB_ed_Zsing = QLineEdit(self.Z_single)
        self.tB_ed_Zsing.setText('4.488525')
        self.tB_ed_Zsing.setMinimumSize(QtCore.QSize(65, 0))
        self.tE_ed_Zsing = QLineEdit(self.Z_single)
        self.tE_ed_Zsing.setText('4.489525')
        self.tE_ed_Zsing.setMinimumSize(QtCore.QSize(65, 0))
        self.tCnt_ed_Zsing = QLineEdit(self.Z_single)
        self.tCnt_ed_Zsing.setMinimumSize(QtCore.QSize(50, 0))
        self.dt_ed_Zsing = QLineEdit(self.Z_single)
        self.dt_ed_Zsing.setText('0.001')
        self.dt_ed_Zsing.setMinimumSize(QtCore.QSize(50, 0))
        self.Butt_dt_Zsing = QPushButton("Calc t", self.Z_single)
        self.Butt_dt_Zsing.clicked.connect(lambda: self.tBE_from_tCnt(7))
        # plot params edits
        self.vmin_ed_Zsing = QLineEdit(self.Z_single)
        self.vmin_ed_Zsing.setText('None')
        self.vmax_ed_Zsing = QLineEdit(self.Z_single)
        self.vmax_ed_Zsing.setText('None')
        self.chzz_ed_Zsing = QLineEdit(self.Z_single)
        # self.chRR_ed_Zsing = QLineEdit(self.Z_single)
        # Filters edits
        self.Fourier_cut_Zsing = QLineEdit(self.Z_single)
        self.Fourier_cut_Zsing.setText('30.0')
        self.Fourier2_cut_Zsing = QLineEdit(self.Z_single)
        self.Fourier2_cut_Zsing.setText('2.0')
        self.SavGol_ed0_Zsing = QLineEdit(self.Z_single)
        self.SavGol_ed0_Zsing.setText('21')
        self.SavGol_ed1_Zsing = QLineEdit(self.Z_single)
        self.SavGol_ed1_Zsing.setText('3')
        self.Binning_ed_Zsing = QLineEdit(self.Z_single)
        self.Binning_ed_Zsing.setText('60.0')
        self.Contour_ed_Zsing = QLineEdit(self.Z_single)
        self.Contour_ed_Zsing.setText('0')
        self.NNcont_ed_Zsing = QLineEdit(self.Z_single)
        self.NNcont_ed_Zsing.setText('20')
        self.FourMult_ed_Zsing = QLineEdit(self.Z_single)
        self.FourMult_ed_Zsing.setText('13.0,15.0;26,30')

        # what to plot (type of filter)
        self.type_plot_Zsing = QComboBox(self.Z_single)
        self.type_plot_Zsing.addItems(['no filter',
                                       'Fourier highpass',
                                       'Fourier lowpass',
                                       'Fourier both',
                                       'Fourier multiple',
                                       'SavGol',
                                       'Binning'])
        self.R_type_Zsing = QComboBox(self.Z_single)
        self.R_type_Zsing.addItems(['data not loaded'])
        # plot buttom
        self.Butt_plot_Zsing = QPushButton("Plot ECEIrel", self.Z_single)
        self.Butt_plot_Zsing.clicked.connect(self.plot_Z_single)

        # Add widgets to layout
        # First row
        sublayout_Zsing.setSpacing(2)
        sublayout_Zsing.addWidget(self.tB_lbl_Zsing, 0, 0)
        sublayout_Zsing.addWidget(self.tB_ed_Zsing, 0, 1)
        sublayout_Zsing.addWidget(self.tE_lbl_Zsing, 0, 2)
        sublayout_Zsing.addWidget(self.tE_ed_Zsing, 0, 3)
        sublayout_Zsing.addWidget(self.tCnt_lbl_Zsing, 0, 4)
        sublayout_Zsing.addWidget(self.tCnt_ed_Zsing, 0, 5)
        sublayout_Zsing.addWidget(self.dt_lbl_Zsing, 0, 6)
        sublayout_Zsing.addWidget(self.dt_ed_Zsing, 0, 7)
        sublayout_Zsing.addWidget(self.Butt_dt_Zsing, 0, 8)
        # Second row
        sublayout_Zsing.addWidget(self.Fourier2_lbl0_Zsing, 1, 0)
        sublayout_Zsing.addWidget(self.Fourier2_cut_Zsing, 1, 1)
        sublayout_Zsing.addWidget(self.Fourier_lbl0_Zsing, 1, 2)
        sublayout_Zsing.addWidget(self.Fourier_cut_Zsing, 1, 3)
        sublayout_Zsing.addWidget(self.FourMult_lbl_Zsing, 1, 4)
        sublayout_Zsing.addWidget(self.FourMult_ed_Zsing, 1, 5)
        ######
        sublayout_Zsing.addWidget(self.SavGol_lbl0_Zsing, 1, 6)
        sublayout_Zsing.addWidget(self.SavGol_ed0_Zsing, 1, 7)
        sublayout_Zsing.addWidget(self.SavGol_lbl1_Zsing, 1, 8)
        sublayout_Zsing.addWidget(self.SavGol_ed1_Zsing, 1, 9)
        sublayout_Zsing.addWidget(self.Binning_lbl_Zsing, 1, 10)
        sublayout_Zsing.addWidget(self.Binning_ed_Zsing, 1, 11)
        ######
        # Third row
        sublayout_Zsing.addWidget(self.chzz_lbl_Zsing, 2, 0)
        sublayout_Zsing.addWidget(self.chzz_ed_Zsing, 2, 1)
        ######
        sublayout_Zsing.addWidget(self.vmin_lbl_Zsing, 2, 4)
        sublayout_Zsing.addWidget(self.vmin_ed_Zsing, 2, 5)
        sublayout_Zsing.addWidget(self.vmax_lbl_Zsing, 2, 6)
        sublayout_Zsing.addWidget(self.vmax_ed_Zsing, 2, 7)
        ######
        sublayout_Zsing.addWidget(self.Contour_lbl_Zsing, 2, 8)
        sublayout_Zsing.addWidget(self.Contour_ed_Zsing, 2, 9)
        sublayout_Zsing.addWidget(self.NNcont_lbl_Zsing, 2, 10)
        sublayout_Zsing.addWidget(self.NNcont_ed_Zsing, 2, 11)
        ######
        sublayout_Zsing.addWidget(self.Rtype_lbl_Zsing, 0, 11)
        sublayout_Zsing.addWidget(self.R_type_Zsing, 0, 12)
        sublayout_Zsing.addWidget(self.type_plot_Zsing, 1, 12)
        sublayout_Zsing.addWidget(self.Butt_plot_Zsing, 2, 12)

        # Add matplotlib plot
        self.figure_Zsing = Figure(figsize=(5, 3))
        self.static_canvas_Zsing = FigureCanvas(self.figure_Zsing)
        layout_Zsing.addWidget(
            self.static_canvas_Zsing,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_Zsing.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_Zsing,
            self.Z_single,
            coordinates=True)  # add toolbar below the plot
        layout_Zsing.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_Zsing.figure.subplots()  # add axes


# ----------------------------------------------------------------------------------

        # EQH tab - content
        # Create layouts
        layout_EQHt = QtWidgets.QVBoxLayout(self.EQH_tab)  # main layout
        sublayout_EQHt = QtWidgets.QGridLayout()  # layout for inputs
        layout_EQHt.addLayout(sublayout_EQHt)

        # Input widgets
        # time
        # labels
        self.Shot_EQHt = QLabel(self.EQH_tab)
        self.Shot_EQHt.setText('Shot #:')
        self.timepl_EQHt = QLabel(self.EQH_tab)
        self.timepl_EQHt.setText('time to plot [s]:')

        # line edits
        self.Shot_ed_EQHt = QLineEdit(self.EQH_tab)
        self.Shot_ed_EQHt.setText('25781')
        self.timepl_ed_EQHt = QLineEdit(self.EQH_tab)
        self.timepl_ed_EQHt.setText('2.0')
        # plot buttom
        self.Butt_plot_EQHt = QPushButton(
            "Load EQH, CEC, ECEI_fakeRz and Plot", self.EQH_tab)
        self.Butt_plot_EQHt.clicked.connect(self.plot_EQH)

        # Add widgets to layout
        # First row
        sublayout_EQHt.setSpacing(2)
        sublayout_EQHt.addWidget(self.Shot_EQHt, 0, 0)
        sublayout_EQHt.addWidget(self.Shot_ed_EQHt, 0, 1)
        sublayout_EQHt.addWidget(self.timepl_EQHt, 0, 2)
        sublayout_EQHt.addWidget(self.timepl_ed_EQHt, 0, 3)
        sublayout_EQHt.addWidget(self.Butt_plot_EQHt, 0, 6)

        # Add matplotlib plot
        self.figure_EQHt = Figure(figsize=(5, 3))
        self.static_canvas_EQHt = FigureCanvas(self.figure_EQHt)
        layout_EQHt.addWidget(
            self.static_canvas_EQHt,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_EQHt.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_EQHt,
            self.EQH_tab,
            coordinates=True)  # add toolbar below the plot
        layout_EQHt.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_EQHt.figure.subplots()  # add axes

# ----------------------------------------------------------------------------------
        # Rz plot tab - content
        # Create layouts
        layout_RzPl = QtWidgets.QVBoxLayout(self.Rz_tab)  # main layout
        sublayout_RzPl = QtWidgets.QGridLayout()  # layout for inputs
        layout_RzPl.addLayout(sublayout_RzPl)

        # Input widgets
        # labels
        self.tB_lbl_RzPl = QLabel(self.Rz_tab)
        self.tB_lbl_RzPl.setText('tB [s]:')
        self.tE_lbl_RzPl = QLabel(self.Rz_tab)
        self.tE_lbl_RzPl.setText('tE [s]:')
        self.tCnt_lbl_RzPl = QLabel(self.Rz_tab)
        self.tCnt_lbl_RzPl.setText('tCenter [s] (optional):')
        self.dt_lbl_RzPl = QLabel(self.Rz_tab)
        self.dt_lbl_RzPl.setText('dt [s](optional) :')
        # filter labels
        self.Fourier_lbl0_RzPl = QLabel(self.Rz_tab)
        self.Fourier_lbl0_RzPl.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_RzPl = QLabel(self.Rz_tab)
        self.Fourier2_lbl0_RzPl.setText('Fourier highpass f [kHz]:')
        self.SavGol_lbl0_RzPl = QLabel(self.Rz_tab)
        self.SavGol_lbl0_RzPl.setText('SavGol win_len:')
        self.SavGol_lbl1_RzPl = QLabel(self.Rz_tab)
        self.SavGol_lbl1_RzPl.setText('SavGol pol_ord:')
        self.Binning_lbl_RzPl = QLabel(self.Rz_tab)
        self.Binning_lbl_RzPl.setText('Binning [kHz]:')
        self.Contour_lbl_RzPl = QLabel(self.Rz_tab)
        self.Contour_lbl_RzPl.setText('Contour [1 or 0]')
        self.NNcont_lbl_RzPl = QLabel(self.Rz_tab)
        self.NNcont_lbl_RzPl.setText('NNcont:')
        self.tplot_lbl_RzPl = QLabel(self.Rz_tab)
        self.tplot_lbl_RzPl.setText('t_plot [s](within tB and tE):')
        self.dtplot_lbl_RzPl = QLabel(self.Rz_tab)
        self.dtplot_lbl_RzPl.setText('dt_plot [s]:')
        self.FourMult_lbl_RzPl = QLabel(self.Rz_tab)
        self.FourMult_lbl_RzPl.setText('Fourier multiple f [kHz]:')

        # plot params labels
        self.vmin_lbl_RzPl = QLabel(self.Rz_tab)
        self.vmin_lbl_RzPl.setText('vmin:')
        self.vmax_lbl_RzPl = QLabel(self.Rz_tab)
        self.vmax_lbl_RzPl.setText('vmax:')
        self.chzz_lbl_RzPl = QLabel(self.Rz_tab)
        self.chzz_lbl_RzPl.setText('Remove LOS:')
        self.chRR_lbl_RzPl = QLabel(self.Rz_tab)
        self.chRR_lbl_RzPl.setText('Remove R chs:')

        # line edits
        # time edits
        self.tB_ed_RzPl = QLineEdit(self.Rz_tab)
        self.tB_ed_RzPl.setText('4.488525')
        self.tB_ed_RzPl.setMinimumSize(QtCore.QSize(55, 0))
        self.tE_ed_RzPl = QLineEdit(self.Rz_tab)
        self.tE_ed_RzPl.setText('4.489525')
        self.tE_ed_RzPl.setMinimumSize(QtCore.QSize(55, 0))
        self.tCnt_ed_RzPl = QLineEdit(self.Rz_tab)
        self.tCnt_ed_RzPl.setMinimumSize(QtCore.QSize(50, 0))
        self.dt_ed_RzPl = QLineEdit(self.Rz_tab)
        self.dt_ed_RzPl.setText('0.001')
        self.dt_ed_RzPl.setMinimumSize(QtCore.QSize(100, 0))
        self.Butt_dt_RzPl = QPushButton("Calc t", self.Rz_tab)
        self.Butt_dt_RzPl.clicked.connect(lambda: self.tBE_from_tCnt(9))
        # plot params edits
        self.vmin_ed_RzPl = QLineEdit(self.Rz_tab)
        self.vmin_ed_RzPl.setText('None')
        self.vmin_ed_RzPl.setMinimumSize(QtCore.QSize(40, 0))
        self.vmax_ed_RzPl = QLineEdit(self.Rz_tab)
        self.vmax_ed_RzPl.setText('None')
        self.vmax_ed_RzPl.setMinimumSize(QtCore.QSize(40, 0))
        self.chzz_ed_RzPl = QLineEdit(self.Rz_tab)
        self.chzz_ed_RzPl.setMinimumSize(QtCore.QSize(100, 0))
        self.chRR_ed_RzPl = QLineEdit(self.Rz_tab)
        self.chRR_ed_RzPl.setMinimumSize(QtCore.QSize(100, 0))
        # Filters edits
        self.Fourier_cut_RzPl = QLineEdit(self.Rz_tab)
        self.Fourier_cut_RzPl.setText('30.0')
        self.Fourier2_cut_RzPl = QLineEdit(self.Rz_tab)
        self.Fourier2_cut_RzPl.setText('2.0')
        self.SavGol_ed0_RzPl = QLineEdit(self.Rz_tab)
        self.SavGol_ed0_RzPl.setText('11')
        self.SavGol_ed0_RzPl.setMinimumSize(QtCore.QSize(20, 0))
        self.SavGol_ed1_RzPl = QLineEdit(self.Rz_tab)
        self.SavGol_ed1_RzPl.setText('3')
        self.Binning_ed_RzPl = QLineEdit(self.Rz_tab)
        self.Binning_ed_RzPl.setText('60.0')
        self.Binning_ed_RzPl.setMinimumSize(QtCore.QSize(40, 0))
        self.Contour_ed_RzPl = QLineEdit(self.Rz_tab)
        self.Contour_ed_RzPl.setText('0')
        self.NNcont_ed_RzPl = QLineEdit(self.Rz_tab)
        self.NNcont_ed_RzPl.setText('60')
        self.tplot_ed_RzPl = QLineEdit(self.Rz_tab)
        self.tplot_ed_RzPl.setText('4.488550')
        self.tplot_ed_RzPl.setMinimumSize(QtCore.QSize(50, 0))
        self.dtplot_ed_RzPl = QLineEdit(self.Rz_tab)
        self.dtplot_ed_RzPl.setText('5.0e-6')
        self.dtplot_ed_RzPl.setMinimumSize(QtCore.QSize(50, 0))
        self.FourMult_ed_RzPl = QLineEdit(self.Rz_tab)
        self.FourMult_ed_RzPl.setText('13.0,15.0;26,30')
        self.FourMult_ed_RzPl.setMinimumSize(QtCore.QSize(100, 0))

        # what to plot (type of filter)
        self.ImgType_plot_RzPl = QComboBox(self.Rz_tab)
        self.ImgType_plot_RzPl.addItems(
            ['no Image filter', 'Gaussian', 'Median', 'Bilateral', 'Conservative_smoothing'])
        self.type_plot_RzPl = QComboBox(self.Rz_tab)
        self.type_plot_RzPl.addItems(['no 1D filter',
                                      'Fourier highpass',
                                      'Fourier lowpass',
                                      'Fourier both',
                                      'Fourier multiple',
                                      'SavGol',
                                      'Binning'])
        self.Interp_plot_RzPl = QComboBox(self.Rz_tab)
        self.Interp_plot_RzPl.addItems(
            ['no interpolation', 'with interpolation', 'set to zero'])
        # self.Interp_plot_RzPl.setMaximumSize(QtCore.QSize(90, 0))
        self.Save_plot_RzPl = QComboBox(self.Rz_tab)
        self.Save_plot_RzPl.addItems(
            ['do not save', 'save as pdf', 'save as png'])
        self.switch_plot_RzPl = QComboBox(self.Rz_tab)
        self.switch_plot_RzPl.addItems(
                ['default', 'velocimetry'])
        # plot buttom
        self.MinusTplot_butt_RzPl = QPushButton("< -dt", self.Rz_tab)
        self.PlusTplot_butt_RzPl = QPushButton("+dt >", self.Rz_tab)
        self.tplot_butt_RzPl = QPushButton("plot time", self.Rz_tab)
        self.MinusTplot_butt_RzPl.clicked.connect(lambda: self.f_Rz_plot(1))
        self.PlusTplot_butt_RzPl.clicked.connect(lambda: self.f_Rz_plot(2))
        self.tplot_butt_RzPl.clicked.connect(lambda: self.f_Rz_plot(3))

        # Shortcuts
        shortcut_plot_Rz = QShortcut(QKeySequence("Ctrl+p"),
                                     self.tplot_butt_RzPl)
        shortcut_plot_Rz.activated.connect(lambda: self.f_Rz_plot(3))
        shortcut_plot_Rz.setEnabled(True)

        shortcut_next_Rz = QShortcut(QKeySequence("Ctrl+j"),
                                     self.PlusTplot_butt_RzPl)
        shortcut_next_Rz.activated.connect(lambda: self.f_Rz_plot(2))
        shortcut_next_Rz.setEnabled(True)

        shortcut_prev_Rz = QShortcut(QKeySequence("Ctrl+k"),
                                     self.MinusTplot_butt_RzPl)
        shortcut_prev_Rz.activated.connect(lambda: self.f_Rz_plot(1))
        shortcut_prev_Rz.setEnabled(True)

        shortcut_tC_Rz = QShortcut(QKeySequence("Ctrl+t"),
                                   self.Butt_dt_RzPl)
        shortcut_tC_Rz.activated.connect(lambda: self.tBE_from_tCnt(9))
        shortcut_tC_Rz.setEnabled(True)
        # Add widgets to layout
        # First row
        sublayout_RzPl.setSpacing(2)
        sublayout_RzPl.addWidget(self.tB_lbl_RzPl, 0, 0)
        sublayout_RzPl.addWidget(self.tB_ed_RzPl, 0, 1)
        sublayout_RzPl.addWidget(self.tE_lbl_RzPl, 0, 2)
        sublayout_RzPl.addWidget(self.tE_ed_RzPl, 0, 3)
        sublayout_RzPl.addWidget(self.tCnt_lbl_RzPl, 0, 4)
        sublayout_RzPl.addWidget(self.tCnt_ed_RzPl, 0, 5)
        sublayout_RzPl.addWidget(self.dt_lbl_RzPl, 0, 6)
        sublayout_RzPl.addWidget(self.dt_ed_RzPl, 0, 7)
        sublayout_RzPl.addWidget(self.Butt_dt_RzPl, 0, 8)
        # Second row
        sublayout_RzPl.addWidget(self.Fourier2_lbl0_RzPl, 1, 0)
        sublayout_RzPl.addWidget(self.Fourier2_cut_RzPl, 1, 1)
        sublayout_RzPl.addWidget(self.Fourier_lbl0_RzPl, 1, 2)
        sublayout_RzPl.addWidget(self.Fourier_cut_RzPl, 1, 3)
        sublayout_RzPl.addWidget(self.FourMult_lbl_RzPl, 1, 4)
        sublayout_RzPl.addWidget(self.FourMult_ed_RzPl, 1, 5)
        ######
        sublayout_RzPl.addWidget(self.SavGol_lbl0_RzPl, 1, 6)
        sublayout_RzPl.addWidget(self.SavGol_ed0_RzPl, 1, 7)
        sublayout_RzPl.addWidget(self.SavGol_lbl1_RzPl, 1, 8)
        sublayout_RzPl.addWidget(self.SavGol_ed1_RzPl, 1, 9)
        sublayout_RzPl.addWidget(self.Binning_lbl_RzPl, 1, 10)
        sublayout_RzPl.addWidget(self.Binning_ed_RzPl, 1, 11)
        ######
        sublayout_RzPl.addWidget(self.chzz_lbl_RzPl, 2, 0)
        sublayout_RzPl.addWidget(self.chzz_ed_RzPl, 2, 1)
        sublayout_RzPl.addWidget(self.chRR_lbl_RzPl, 2, 2)
        sublayout_RzPl.addWidget(self.chRR_ed_RzPl, 2, 3)
        ######
        sublayout_RzPl.addWidget(self.vmin_lbl_RzPl, 2, 4)
        sublayout_RzPl.addWidget(self.vmin_ed_RzPl, 2, 5)
        sublayout_RzPl.addWidget(self.vmax_lbl_RzPl, 2, 6)
        sublayout_RzPl.addWidget(self.vmax_ed_RzPl, 2, 7)
        sublayout_RzPl.addWidget(self.Contour_lbl_RzPl, 2, 8)
        sublayout_RzPl.addWidget(self.Contour_ed_RzPl, 2, 9)
        sublayout_RzPl.addWidget(self.NNcont_lbl_RzPl, 2, 10)
        sublayout_RzPl.addWidget(self.NNcont_ed_RzPl, 2, 11)
        #####
        ######
        # Third row
        sublayout_RzPl.addWidget(self.tplot_lbl_RzPl, 3, 0)
        sublayout_RzPl.addWidget(self.tplot_ed_RzPl, 3, 1)
        sublayout_RzPl.addWidget(self.dtplot_lbl_RzPl, 3, 2)
        sublayout_RzPl.addWidget(self.dtplot_ed_RzPl, 3, 3)
        # Plot control
        sublayout_RzPl.addWidget(self.switch_plot_RzPl, 0, 12)
        sublayout_RzPl.addWidget(self.ImgType_plot_RzPl, 1, 12)
        sublayout_RzPl.addWidget(self.type_plot_RzPl, 2, 12)
        sublayout_RzPl.addWidget(self.Save_plot_RzPl, 3, 7)
        # sublayout_RzPl.addWidget(self.Info2_lbl_RzPl, 3, 8)
        sublayout_RzPl.addWidget(self.Interp_plot_RzPl, 3, 8)
        sublayout_RzPl.addWidget(self.MinusTplot_butt_RzPl, 3, 10)
        sublayout_RzPl.addWidget(self.PlusTplot_butt_RzPl, 3, 11)
        sublayout_RzPl.addWidget(self.tplot_butt_RzPl, 3, 12)

        # Add matplotlib plot
        self.figure_RzPl = Figure(figsize=(5, 3))
        self.static_canvas_RzPl = FigureCanvas(self.figure_RzPl)
        layout_RzPl.addWidget(
            self.static_canvas_RzPl,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_RzPl.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_RzPl,
            self.Rz_tab,
            coordinates=True)  # add toolbar below the plot
        layout_RzPl.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_RzPl.figure.subplots()  # add axes


# ----------------------------------------------------------------------------------
        # SettRz tab - content
        # Create layouts
        layout_RzSet = QtWidgets.QVBoxLayout(
            self.SettRzPlot_tab)  # main layout
        sublayout_RzSet = QtWidgets.QGridLayout()  # layout for inputs
        layout_RzSet.addLayout(sublayout_RzSet)

        # Input widgets
        # labels
        self.one_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.one_lbl_RzSet.setText('Gaussian filter:')
        self.two_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.two_lbl_RzSet.setText('Median filter:')
        self.three_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.three_lbl_RzSet.setText('Bilateral filter:')
        self.four_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.four_lbl_RzSet.setText('Conservative smoothing filter:')
        # filters parameters
        self.BilKernSize_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.BilKernSize_lbl_RzSet.setText('Kernel size:')
        self.BilS0_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.BilS0_lbl_RzSet.setText('s0:')
        self.BilS1_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.BilS1_lbl_RzSet.setText('s1:')
        self.MedKernSize_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.MedKernSize_lbl_RzSet.setText('Kernel size:')
        self.ConsSize_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.ConsSize_lbl_RzSet.setText('Neighborhood size:')
        self.GausSigma_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.GausSigma_lbl_RzSet.setText('sigma:')

        # Line edits (inputs)
        self.GausSigma_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.GausSigma_ed_RzSet.setText('1.0')
        self.BilKern_type_RzSet = QComboBox(self.SettRzPlot_tab)
        self.BilKern_type_RzSet.addItems(['disk', 'square'])
        self.BilKernSize_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.BilKernSize_ed_RzSet.setText('1')
        self.BilS0_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.BilS0_ed_RzSet.setText('100')
        self.BilS1_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.BilS1_ed_RzSet.setText('100')

        self.MedKern_type_RzSet = QComboBox(self.SettRzPlot_tab)
        self.MedKern_type_RzSet.addItems(['disk', 'square'])
        self.MedKernSize_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.MedKernSize_ed_RzSet.setText('1')
        self.ConsSize_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.ConsSize_ed_RzSet.setText('2')

        sublayout_RzSet.setSpacing(2)
        # First row
        sublayout_RzSet.addWidget(self.one_lbl_RzSet, 0, 0)
        sublayout_RzSet.addWidget(self.GausSigma_lbl_RzSet, 0, 2)
        sublayout_RzSet.addWidget(self.GausSigma_ed_RzSet, 0, 3)
        # Second row
        sublayout_RzSet.addWidget(self.two_lbl_RzSet, 1, 0)
        sublayout_RzSet.addWidget(self.MedKern_type_RzSet, 1, 1)
        sublayout_RzSet.addWidget(self.MedKernSize_lbl_RzSet, 1, 2)
        sublayout_RzSet.addWidget(self.MedKernSize_ed_RzSet, 1, 3)
        # Third row
        sublayout_RzSet.addWidget(self.three_lbl_RzSet, 2, 0)
        sublayout_RzSet.addWidget(self.BilKern_type_RzSet, 2, 1)
        sublayout_RzSet.addWidget(self.BilKernSize_lbl_RzSet, 2, 2)
        sublayout_RzSet.addWidget(self.BilKernSize_ed_RzSet, 2, 3)
        sublayout_RzSet.addWidget(self.BilS0_lbl_RzSet, 2, 4)
        sublayout_RzSet.addWidget(self.BilS0_ed_RzSet, 2, 5)
        sublayout_RzSet.addWidget(self.BilS1_lbl_RzSet, 2, 6)
        sublayout_RzSet.addWidget(self.BilS1_ed_RzSet, 2, 7)
        # Fourth row
        sublayout_RzSet.addWidget(self.four_lbl_RzSet, 3, 0)
        sublayout_RzSet.addWidget(self.ConsSize_lbl_RzSet, 3, 2)
        sublayout_RzSet.addWidget(self.ConsSize_ed_RzSet, 3, 3)

        sublayout1_RzSet = QtWidgets.QVBoxLayout()  # one more layout for title
        layout_RzSet.addLayout(sublayout1_RzSet)

        self.Info1_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.Info1_lbl_RzSet.setText(
            '====== Matrix for interpolation (scipy.interpolate.interp2d, type = cubic) or "set to zero" options ======')
        sublayout1_RzSet.addWidget(self.Info1_lbl_RzSet)

        sublayout2_RzSet = QtWidgets.QGridLayout()  # one more layout for interpolation
        layout_RzSet.addLayout(sublayout2_RzSet)

        LOSlabels = {}
        self.LOSlabels = {}
        for i_L in range(20):
            LOSlabels['%d' % (i_L)] = (i_L, 0)
        for sText, pos in LOSlabels.items():
            # QLabels
            self.LOSlabels[sText] = QLabel("LOS: %d" % (int(sText) + 1))
            sublayout2_RzSet.addWidget(
                self.LOSlabels[sText], pos[0] + 1, pos[1])

        checks = {}
        self.checks = {}
        for i_L in range(20):
            for i_R in range(8):
                checks['%d,%d' % (i_L, i_R)] = (i_L, i_R)
        for sText, pos in checks.items():
            # QCheckBoxes
            self.checks[sText] = QCheckBox("%d,%d" % (pos[0] + 1, pos[1] + 1))
            sublayout2_RzSet.addWidget(
                self.checks[sText], pos[0] + 1, pos[1] + 1)
        sublayout2_RzSet.setSpacing(2)

        sublayout3_RzSet = QtWidgets.QHBoxLayout()  # one more layout for path
        layout_RzSet.addLayout(sublayout3_RzSet)

        self.path_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.path_lbl_RzSet.setText(
            'Path to save Rz plots (path should end with "/" symbol):')

        self.path_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.path_ed_RzSet.setText('/afs/ipp/home/o/osam/Documents/output/')
        sublayout3_RzSet.addWidget(self.path_lbl_RzSet)
        sublayout3_RzSet.addWidget(self.path_ed_RzSet)

        layout_RzSet.addStretch()  # stretch free space (compress widgets at the top)
# ----------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------
    # ---------------METHODS-------------


    def tBE_from_tCnt(self, number):
        try:
            if (number == 1):
                t = float(self.tCnt_ed_plCh.text())
                dt = float(self.dt_ed_plCh.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_plCh.setText('%0.7g' % (tB))
                self.tE_ed_plCh.setText('%0.7g' % (tE))
                self.plot_chs_all()
            if (number == 2):
                t = float(self.tCnt_ed_LOS.text())
                dt = float(self.dt_ed_LOS.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_LOS.setText('%0.7g' % (tB))
                self.tE_ed_LOS.setText('%0.7g' % (tE))
                self.f_LOS_plot()
            if (number == 3):
                t = float(self.tCnt_ed_FFT.text())
                dt = float(self.dt_ed_FFT.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_FFT.setText('%0.7g' % (tB))
                self.tE_ed_FFT.setText('%0.7g' % (tE))
                self.f_FFT_plot()
            if (number == 4):
                t = float(self.tCnt_ed_Rtr.text())
                dt = float(self.dt_ed_Rtr.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_Rtr.setText('%0.7g' % (tB))
                self.tE_ed_Rtr.setText('%0.7g' % (tE))
                self.plot_R_trace()
            if (number == 5):
                t = float(self.tCnt_ed_Rsing.text())
                dt = float(self.dt_ed_Rsing.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_Rsing.setText('%0.7g' % (tB))
                self.tE_ed_Rsing.setText('%0.7g' % (tE))
                self.plot_R_single()
            if (number == 6):
                t = float(self.tCnt_ed_Ztr.text())
                dt = float(self.dt_ed_Ztr.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_Ztr.setText('%0.7g' % (tB))
                self.tE_ed_Ztr.setText('%0.7g' % (tE))
                self.plot_Z_trace()
            if (number == 7):
                t = float(self.tCnt_ed_Zsing.text())
                dt = float(self.dt_ed_Zsing.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_Zsing.setText('%0.7g' % (tB))
                self.tE_ed_Zsing.setText('%0.7g' % (tE))
                self.plot_Z_single()
            if (number == 9):
                t = float(self.tCnt_ed_RzPl.text())
                dt = float(self.dt_ed_RzPl.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_RzPl.setText('%0.7g' % (tB))
                self.tE_ed_RzPl.setText('%0.7g' % (tE))
                self.tplot_ed_RzPl.setText('%0.7g' % (np.mean([tB, tE])))
                self.f_Rz_plot(3)

        except Exception as exc:
            # Handle the error gracefully
            tb = traceback.format_exc()
            print(f"An error occurred: {exc}\nTraceback:\n{tb}")
            print("!!! Incorrect input. ERROR: %s" % (exc))
        pass

    def Load_ECEI_data(self):
        try:
            self.Shot = int(self.Shot_ed_load.text())
            self.Diag = self.Diag_load.currentText()
            self.Monitor_load.setText(
                "Status:\nLoading %s: #%d ... " %
                (self.Diag, self.Shot))
            allow_to_load = True
            self.Shot_ed_EQHt.setText(self.Shot_ed_load.text())
        except Exception as exc:
            # Handle the error gracefully
            tb = traceback.format_exc()
            print(f"An error occurred: {exc}\nTraceback:\n{tb}")
            print("!!! Incorrect input. ERROR: %s" % (exc))
            self.Monitor_load.setText("Status:\nPlease enter shot number.")
            allow_to_load = False

        if (self.Diag == 'TDI') & (allow_to_load):
            try:
                TD = TDI.TDI()
                TD.Load(self.Shot)
                TD.Load_FakeRz()
                self.ECEId = TD.ECEId.copy()
                self.ECEId_time = TD.time.copy()
                self.ECEId_RR = TD.RR_fake.copy()
                self.ECEId_zz = TD.zz_fake.copy()
                self.ECEId_R = TD.R_fake.copy()
                self.ECEId_z = TD.z_fake.copy()
                self.Monitor_load.setText("Status:\nTDI #%d\ntB = %g, tE = %g s\nLoaded succesfully." % (
                    self.Shot, TD.time[0], TD.time[-1]))
                NN_LOS = self.ECEId.shape[1]
                add_to_LOS = np.arange(1, NN_LOS + 1)
                add_to_LOS = [str(e) for e in add_to_LOS]
                self.NLOS_type_LOS.clear()
                self.NLOS_type_LOS.addItems(add_to_LOS)
                self.NLOS_type_FFT.clear()
                self.NLOS_type_FFT.addItems(add_to_LOS)
                self.LOS_type_Rsing.clear()
                self.LOS_type_Rsing.addItems(add_to_LOS)
                self.R_type_Zsing.clear()
                self.R_type_Zsing.addItems([str(e) for e in np.arange(1, 9)])

                self.data_loaded = True
                print("+++ The data has been loaded succesfully. +++")
            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
                print("!!! Coudn't load TDI. ERROR: %s" % (exc))
                self.Monitor_load.setText(
                    "Status:\nError in loading ECI data.")

        if (self.Diag == 'ECI') & (allow_to_load):
            try:
                EI = ECI.ECI()
                EI.Load(self.Shot)
                EI.Load_FakeRz()
                self.ECEId = EI.ECEId.copy()
                self.ECEId_time = EI.time.copy()
                self.ECEId_RR = EI.RR_fake.copy()
                self.ECEId_zz = EI.zz_fake.copy()
                self.ECEId_R = EI.R_fake.copy()
                self.ECEId_z = EI.z_fake.copy()
                self.Monitor_load.setText("Status:\nECI #%d\ntB = %g, tE = %g s\nLoaded succesfully." % (
                    self.Shot, EI.time[0], EI.time[-1]))
                NN_LOS = self.ECEId.shape[1]
                add_to_LOS = np.arange(1, NN_LOS + 1)
                add_to_LOS = [str(e) for e in add_to_LOS]
                self.NLOS_type_LOS.clear()
                self.NLOS_type_LOS.addItems(add_to_LOS)
                self.NLOS_type_FFT.clear()
                self.NLOS_type_FFT.addItems(add_to_LOS)
                self.LOS_type_Rsing.clear()
                self.LOS_type_Rsing.addItems(add_to_LOS)
                self.R_type_Zsing.clear()
                self.R_type_Zsing.addItems([str(e) for e in np.arange(1, 9)])
                self.data_loaded = True
                print("+++ The data has been loaded succesfully. +++")
            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
                print("!!! Coudn't load ECI. ERROR: %s" % (exc))
                self.Monitor_load.setText(
                    "Status:\nError in loading ECI data.")
        self.data_calibrated = False

    def plot_chs_all(self):

        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 6})
                # data preparation
                tB = float(self.tB_ed_plCh.text())
                tE = float(self.tE_ed_plCh.text())
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                if (self.data_calibrated):
                    time_plot, data_plot = mf.time_C, mf.ECEId_C
                else:
                    mf.relECEI(mf.ECEId_C)
                    time_plot, data_plot = mf.time_C, mf.ECEId_rel
                filter_status = "None"

                if (self.type_plot_plCh.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_plCh.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_plCh.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_plCh.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_plCh.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_plCh.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_plCh.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_plCh.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_plCh.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_plCh.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_plCh.text())
                    pol_ord = int(self.SavGol_ed1_plCh.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_plCh.currentText() == 'Binning'):
                    time_plot, data_plot
                    binning_freq = float(self.Binning_ed_plCh.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                # initiate plot
                self.figure_plCh.clf()  # clear previous figure and axes

                NN_LOS, NN_R = data_plot.shape[1], data_plot.shape[2]
                self._static_ax = self.static_canvas_plCh.figure.subplots(
                    NN_LOS, NN_R, sharex=True, sharey=False)  # add axes

                for L_i in range(NN_LOS):
                    for R_i in range(NN_R):
                        self._static_ax[L_i, R_i].plot(
                            time_plot, data_plot[:, L_i, R_i])
                # draw the figure
                self.figure_plCh.suptitle(
                    "ECEI, Shot #%d, deltaTrad/<Trad>, Filter: %s" %
                    (self.Shot, filter_status), fontsize=8)
                self.static_canvas_plCh.draw()
                self.sync_tabs(1)
                print("+++ The data has been plotted succesfully. +++")
            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data (first tab)")

    def f_LOS_plot(self):

        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 10})
                # data preparation
                tB = float(self.tB_ed_LOS.text())
                tE = float(self.tE_ed_LOS.text())
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                if (self.data_calibrated):
                    time_plot, data_plot = mf.time_C, mf.ECEId_C
                else:
                    mf.relECEI(mf.ECEId_C)
                    time_plot, data_plot = mf.time_C, mf.ECEId_rel
                LOStoPlot = int(self.NLOS_type_LOS.currentText()) - 1
                print("LOS to plot: %g" % (LOStoPlot + 1))
                filter_status = "None"

                if (self.type_plot_LOS.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_LOS.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_LOS.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_LOS.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_LOS.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_LOS.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_LOS.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_LOS.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_LOS.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_LOS.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_LOS.text())
                    pol_ord = int(self.SavGol_ed1_LOS.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_LOS.currentText() == 'Binning'):
                    time_plot, data_plot
                    binning_freq = float(self.Binning_ed_LOS.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                # initiate plot
                self.figure_LOS.clf()  # clear previous figure and axes

                self._static_ax = self.static_canvas_LOS.figure.subplots(
                    4, 2, sharex=True, sharey=False)  # add axes

                for i_R in range(8):
                    self._static_ax[i_R -
                                    4 *
                                    (i_R //
                                     4), i_R //
                                    4].plot(time_plot, data_plot[:, LOStoPlot, i_R])
                    self._static_ax[i_R - 4 * (i_R // 4),
                                    i_R // 4].set_title("R_ch=%g" % (i_R + 1))
                    self._static_ax[i_R - 4 * (i_R // 4),
                                    i_R // 4].set_ylabel("deltaTrad/<Trad>")
                    self._static_ax[i_R - 4 * (i_R // 4), i_R // 4].grid()
                    self._static_ax[3, 0].set_xlabel("t [s]")
                    self._static_ax[3, 1].set_xlabel("t [s]")
                # draw the figure
                self.figure_LOS.suptitle(
                    "ECEI, Shot #%d, LOS=%g, Filter: %s" %
                    (self.Shot, LOStoPlot + 1, filter_status), fontsize=10)
                self.static_canvas_LOS.draw()
                self.sync_tabs(2)
                print("+++ The data has been plotted succesfully. +++")
            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data (first tab)")

    def f_FFT_plot(self):

        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 10})
                # data preparation
                tB = float(self.tB_ed_FFT.text())
                tE = float(self.tE_ed_FFT.text())
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                if (self.data_calibrated):
                    time_plot, data_plot = mf.time_C, mf.ECEId_C
                else:
                    mf.relECEI(mf.ECEId_C)
                    time_plot, data_plot = mf.time_C, mf.ECEId_rel
                LOStoPlot = int(self.NLOS_type_FFT.currentText()) - 1
                print("LOS to plot: %g" % (LOStoPlot + 1))
                filter_status = "None"

                if (self.type_plot_FFT.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_FFT.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_FFT.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_FFT.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_FFT.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_FFT.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_FFT.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_FFT.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_FFT.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_FFT.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_FFT.text())
                    pol_ord = int(self.SavGol_ed1_FFT.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_FFT.currentText() == 'Binning'):
                    time_plot, data_plot
                    binning_freq = float(self.Binning_ed_FFT.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                # initiate plot
                self.figure_FFT.clf()  # clear previous figure and axes

                self._static_ax = self.static_canvas_FFT.figure.subplots(
                    4, 2, sharex=True, sharey=False)  # add axes

                for i_R in range(8):
                    freq_fft, Te_fft, offset = mf.fft_analysis(
                        time_plot, data_plot[:, LOStoPlot, i_R])
                    NN = len(freq_fft)
                    self._static_ax[i_R - 4 * (i_R // 4), i_R // 4].plot(
                        freq_fft[:int(NN / 2)] * 1e-3, np.abs(Te_fft[:int(NN / 2)]), "b")
                    self._static_ax[i_R - 4 * (i_R // 4),
                                    i_R // 4].set_title("R_ch=%g" % (i_R + 1))
                    self._static_ax[i_R - 4 * (i_R // 4),
                                    i_R // 4].set_ylabel("|FFT(deltaT/<T>)|")
                    self._static_ax[i_R - 4 * (i_R // 4), i_R // 4].grid()
                    self._static_ax[3, 0].set_xlabel("freq [kHz]")
                    self._static_ax[3, 1].set_xlabel("freq [kHz]")
                # draw the figure
                self.figure_FFT.suptitle(
                    "ECEI, Shot #%d, LOS=%g, Filter: %s" %
                    (self.Shot, LOStoPlot + 1, filter_status), fontsize=10)
                self.static_canvas_FFT.draw()
                self.sync_tabs(3)
                print("+++ The data has been plotted succesfully. +++")
            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data (first tab)")

    def plot_R_trace(self):

        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 6})
                # data preparation
                tB = float(self.tB_ed_Rtr.text())
                tE = float(self.tE_ed_Rtr.text())
                contour_check = self.Contour_ed_Rtr.text()
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                if (self.data_calibrated):
                    time_plot, data_plot = mf.time_C, mf.ECEId_C
                else:
                    mf.relECEI(mf.ECEId_C)
                    time_plot, data_plot = mf.time_C, mf.ECEId_rel
                filter_status = "None"

                if (self.type_plot_Rtr.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_Rtr.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_Rtr.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_Rtr.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_Rtr.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_Rtr.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_Rtr.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_Rtr.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_Rtr.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_Rtr.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_Rtr.text())
                    pol_ord = int(self.SavGol_ed1_Rtr.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_Rtr.currentText() == 'Binning'):
                    time_plot, data_plot
                    binning_freq = float(self.Binning_ed_Rtr.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                RR_plot, zz_plot = self.ECEId_RR, self.ECEId_zz

                removeLOS_ch = self.chzz_ed_Rtr.text()
                if removeLOS_ch:
                    removeLOS_ch = np.array(self.chzz_ed_Rtr.text().split(','))
                    removeLOS_ch = removeLOS_ch.astype(int) - 1
                else:
                    removeLOS_ch = []
                removeRR_ch = self.chRR_ed_Rtr.text()
                if removeRR_ch:
                    removeRR_ch = np.array(self.chRR_ed_Rtr.text().split(','))
                    removeRR_ch = removeRR_ch.astype(int) - 1
                else:
                    removeRR_ch = []

                NN_LOS, NN_R = data_plot.shape[1], data_plot.shape[2]
                ch_zz = np.arange(NN_LOS)
                ch_zz = np.delete(ch_zz, removeLOS_ch)
                ch_RR = np.arange(NN_R)
                ch_RR = np.delete(ch_RR, removeRR_ch)

                if (self.vmin_ed_Rtr.text().replace(
                        '-', '', 1).replace('.', '', 1).isdigit()):
                    vmin = float(self.vmin_ed_Rtr.text())
                else:
                    vmin = None

                if (self.vmax_ed_Rtr.text().replace('.', '', 1).isdigit()):
                    vmax = float(self.vmax_ed_Rtr.text())
                else:
                    vmax = None

                if (self.NNcont_ed_Rtr.text().replace('.', '', 1).isdigit()):
                    NN_cont = int(self.NNcont_ed_Rtr.text())
                else:
                    NN_cont = 20

                # plotting
                # initiate plot
                self.figure_Rtr.clf()  # clear previous figure and axes
                time_tr, R_tr = time_plot, RR_plot[ch_zz[0], ch_RR]
                time_tr, R_tr = np.meshgrid(time_tr, R_tr)
                self._static_ax = self.static_canvas_Rtr.figure.subplots(
                    1, len(ch_zz), sharex=False, sharey=True)  # add axes

                for i_z in range(len(ch_zz)):
                    contours = self._static_ax[i_z].contourf(
                        R_tr, time_tr, data_plot[:, ch_zz[i_z], ch_RR].T, vmin=vmin, vmax=vmax, levels=NN_cont, cmap='jet')
                    cbar = self.figure_Rtr.colorbar(
                        contours, ax=self._static_ax[i_z], orientation="horizontal", pad=0.07)
                    if contour_check == '1':
                        self._static_ax[i_z].contour(R_tr,
                                                     time_tr,
                                                     data_plot[:,
                                                               ch_zz[i_z],
                                                               ch_RR].T,
                                                     vmin=vmin,
                                                     vmax=vmax,
                                                     levels=NN_cont,
                                                     cmap='binary')
                    cbar.ax.tick_params(labelsize=8, rotation=90)
                    self._static_ax[i_z].set_xlabel(
                        "R [m](LOS=%g)" % (ch_zz[i_z] + 1))
                    self._static_ax[0].set_ylabel("t [s]")

                self.figure_Rtr.suptitle(
                    "ECEI, Shot #%d, deltaTrad/<Trad>, Filter: %s" %
                    (self.Shot, filter_status), fontsize=10)
                self.static_canvas_Rtr.draw()
                self.sync_tabs(4)
                print("+++ The data has been plotted succesfully. +++")

            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data (first tab)")

    def plot_R_single(self):

        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 10})
                # data preparation
                tB = float(self.tB_ed_Rsing.text())
                tE = float(self.tE_ed_Rsing.text())
                contour_check = self.Contour_ed_Rsing.text()
                LOStoPlot = int(self.LOS_type_Rsing.currentText()) - 1
                print("LOS to plot: %s " % (self.LOS_type_Rsing.currentText()))
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                if (self.data_calibrated):
                    time_plot, data_plot = mf.time_C, mf.ECEId_C
                else:
                    mf.relECEI(mf.ECEId_C)
                    time_plot, data_plot = mf.time_C, mf.ECEId_rel
                filter_status = "None"

                if (self.type_plot_Rsing.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_Rsing.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_Rsing.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_Rsing.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_Rsing.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_Rsing.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_Rsing.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_Rsing.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_Rsing.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_Rsing.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_Rsing.text())
                    pol_ord = int(self.SavGol_ed1_Rsing.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_Rsing.currentText() == 'Binning'):
                    time_plot, data_plot
                    binning_freq = float(self.Binning_ed_Rsing.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                RR_plot, zz_plot = self.ECEId_RR, self.ECEId_zz

                # removeLOS_ch = self.chzz_ed_Rsing.text()
                # if removeLOS_ch:
                # removeLOS_ch = np.array(self.chzz_ed_Rsing.text().split(','))
                # removeLOS_ch = removeLOS_ch.astype(int) - 1
                # else:
                # removeLOS_ch = []
                removeRR_ch = self.chRR_ed_Rsing.text()
                if removeRR_ch:
                    removeRR_ch = np.array(
                        self.chRR_ed_Rsing.text().split(','))
                    removeRR_ch = removeRR_ch.astype(int) - 1
                else:
                    removeRR_ch = []

                NN_LOS, NN_R = data_plot.shape[1], data_plot.shape[2]
                ch_zz = np.arange(NN_LOS)
                # ch_zz = np.delete(ch_zz, removeLOS_ch)
                ch_RR = np.arange(NN_R)
                ch_RR = np.delete(ch_RR, removeRR_ch)

                if (self.vmin_ed_Rsing.text().replace(
                        '-', '', 1).replace('.', '', 1).isdigit()):
                    vmin = float(self.vmin_ed_Rsing.text())
                else:
                    vmin = None

                if (self.vmax_ed_Rsing.text().replace('.', '', 1).isdigit()):
                    vmax = float(self.vmax_ed_Rsing.text())
                else:
                    vmax = None

                if (self.NNcont_ed_Rsing.text().replace('.', '', 1).isdigit()):
                    NN_cont = int(self.NNcont_ed_Rsing.text())
                else:
                    NN_cont = 20

                # plotting
                # initiate plot
                self.figure_Rsing.clf()  # clear previous figure and axes
                time_tr, R_tr = time_plot, RR_plot[ch_zz[0], ch_RR]
                time_tr, R_tr = np.meshgrid(time_tr, R_tr)
                ax = self.figure_Rsing.add_subplot(111)  # add axes

                contours = ax.contourf(time_tr,
                                       R_tr,
                                       data_plot[:,
                                                 LOStoPlot,
                                                 ch_RR].T,
                                       vmin=vmin,
                                       vmax=vmax,
                                       levels=NN_cont,
                                       cmap='jet')
                cbar = self.figure_Rsing.colorbar(contours, ax=ax)
                cbar.ax.set_ylabel('deltaTrad/<Trad>', rotation=90)
                if contour_check == '1':
                    ax.contour(time_tr,
                               R_tr,
                               data_plot[:,
                                         LOStoPlot,
                                         ch_RR].T,
                               vmin=vmin,
                               vmax=vmax,
                               levels=NN_cont,
                               cmap='binary')
                cbar.ax.tick_params(labelsize=8, rotation=90)
                ax.set_ylabel("R [m] (LOS=%g)" % (LOStoPlot + 1))
                ax.set_xlabel("t [s]")

                my_text = ch_RR
                for i in range(len(ch_RR)):
                    ax.annotate(ch_RR[i] +
                                1, (time_tr[i, 0], R_tr[i, 0]), size=10)

                self.figure_Rsing.suptitle(
                    "ECEI, Shot #%d, Filter: %s" %
                    (self.Shot, filter_status), fontsize=10)
                self.static_canvas_Rsing.draw()
                self.sync_tabs(5)
                print("+++ The data has been plotted succesfully. +++")

            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data (first tab)")

    def plot_Z_trace(self):

        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 6})
                # data preparation
                tB = float(self.tB_ed_Ztr.text())
                tE = float(self.tE_ed_Ztr.text())
                contour_check = self.Contour_ed_Ztr.text()
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                if (self.data_calibrated):
                    time_plot, data_plot = mf.time_C, mf.ECEId_C
                else:
                    mf.relECEI(mf.ECEId_C)
                    time_plot, data_plot = mf.time_C, mf.ECEId_rel
                filter_status = "None"

                if (self.type_plot_Ztr.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_Ztr.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_Ztr.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_Ztr.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_Ztr.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_Ztr.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_Ztr.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_Ztr.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_Ztr.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_Ztr.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_Ztr.text())
                    pol_ord = int(self.SavGol_ed1_Ztr.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_Ztr.currentText() == 'Binning'):
                    time_plot, data_plot
                    binning_freq = float(self.Binning_ed_Ztr.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                RR_plot, zz_plot = self.ECEId_RR, self.ECEId_zz

                removeLOS_ch = self.chzz_ed_Ztr.text()
                if removeLOS_ch:
                    removeLOS_ch = np.array(self.chzz_ed_Ztr.text().split(','))
                    removeLOS_ch = removeLOS_ch.astype(int) - 1
                else:
                    removeLOS_ch = []

                NN_LOS, NN_R = data_plot.shape[1], data_plot.shape[2]
                ch_zz = np.arange(NN_LOS)
                ch_zz = np.delete(ch_zz, removeLOS_ch)

                if (self.vmin_ed_Ztr.text().replace(
                        '-', '', 1).replace('.', '', 1).isdigit()):
                    vmin = float(self.vmin_ed_Ztr.text())
                else:
                    vmin = None

                if (self.vmax_ed_Ztr.text().replace('.', '', 1).isdigit()):
                    vmax = float(self.vmax_ed_Ztr.text())
                else:
                    vmax = None
                if (self.NNcont_ed_Ztr.text().replace('.', '', 1).isdigit()):
                    NN_cont = int(self.NNcont_ed_Ztr.text())
                else:
                    NN_cont = 20

                # plotting
                # initiate plot
                self.figure_Ztr.clf()  # clear previous figure and axes
                time_tr, z_tr = time_plot, zz_plot[ch_zz, 0]
                time_tr, z_tr = np.meshgrid(time_tr, z_tr)
                self._static_ax = self.static_canvas_Ztr.figure.subplots(
                    4, 2, sharex=True, sharey=False)  # add axes

                for i_R in range(8):
                    contours = self._static_ax[i_R - 4 * (i_R // 4), i_R // 4].contourf(
                        time_tr, z_tr, data_plot[:, ch_zz, i_R].T, vmin=vmin, vmax=vmax, levels=NN_cont, cmap='jet')
                    self.figure_Ztr.colorbar(
                        contours, ax=self._static_ax[i_R - 4 * (i_R // 4), i_R // 4])
                    if contour_check == '1':
                        self._static_ax[i_R - 4 * (i_R // 4),
                                        i_R // 4].contour(time_tr,
                                                          z_tr,
                                                          data_plot[:,
                                                                    ch_zz,
                                                                    i_R].T,
                                                          vmin=vmin,
                                                          vmax=vmax,
                                                          levels=NN_cont,
                                                          cmap='binary')
                    self._static_ax[i_R - 4 * (i_R // 4),
                                    i_R // 4].set_title("R_ch=%g" % (i_R + 1))
                    self._static_ax[i_R - 4 *
                                    (i_R // 4), i_R // 4].set_ylabel("z [m]")
                    self._static_ax[3, 0].set_xlabel("t [s]")
                    self._static_ax[3, 1].set_xlabel("t [s]")
                    my_text = ch_zz
                    for i in range(len(ch_zz)):
                        self._static_ax[i_R -
                                        4 *
                                        (i_R //
                                         4), i_R //
                                        4].annotate(ch_zz[i] +
                                                    1, (time_tr[i, 0], z_tr[i, 0]), size=6)

                self.figure_Ztr.suptitle(
                    "ECEI, Shot #%d, deltaTrad/<Trad>, Filter: %s" %
                    (self.Shot, filter_status), fontsize=10)
                self.static_canvas_Ztr.draw()
                self.sync_tabs(6)
                print("+++ The data has been plotted succesfully. +++")

            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data (first tab)")

    def plot_Z_single(self):

        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 10})
                # data preparation
                tB = float(self.tB_ed_Zsing.text())
                tE = float(self.tE_ed_Zsing.text())
                contour_check = self.Contour_ed_Zsing.text()
                RtoPlot = int(self.R_type_Zsing.currentText()) - 1
                print("R ch to plot: %s " % (self.R_type_Zsing.currentText()))
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                if (self.data_calibrated):
                    time_plot, data_plot = mf.time_C, mf.ECEId_C
                else:
                    mf.relECEI(mf.ECEId_C)
                    time_plot, data_plot = mf.time_C, mf.ECEId_rel
                filter_status = "None"

                if (self.type_plot_Zsing.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_Zsing.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_Zsing.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_Zsing.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_Zsing.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_Zsing.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_Zsing.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_Zsing.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_Zsing.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_Zsing.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_Zsing.text())
                    pol_ord = int(self.SavGol_ed1_Zsing.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_Zsing.currentText() == 'Binning'):
                    time_plot, data_plot
                    binning_freq = float(self.Binning_ed_Zsing.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                RR_plot, zz_plot = self.ECEId_RR, self.ECEId_zz

                removeLOS_ch = self.chzz_ed_Zsing.text()
                if removeLOS_ch:
                    removeLOS_ch = np.array(
                        self.chzz_ed_Zsing.text().split(','))
                    removeLOS_ch = removeLOS_ch.astype(int) - 1
                else:
                    removeLOS_ch = []

                NN_LOS, NN_R = data_plot.shape[1], data_plot.shape[2]
                ch_zz = np.arange(NN_LOS)
                ch_zz = np.delete(ch_zz, removeLOS_ch)

                if (self.vmin_ed_Zsing.text().replace(
                        '-', '', 1).replace('.', '', 1).isdigit()):
                    vmin = float(self.vmin_ed_Zsing.text())
                else:
                    vmin = None

                if (self.vmax_ed_Zsing.text().replace('.', '', 1).isdigit()):
                    vmax = float(self.vmax_ed_Zsing.text())
                else:
                    vmax = None
                if (self.NNcont_ed_Zsing.text().replace('.', '', 1).isdigit()):
                    NN_cont = int(self.NNcont_ed_Zsing.text())
                else:
                    NN_cont = 20

                # plotting
                # initiate plot
                self.figure_Zsing.clf()  # clear previous figure and axes
                time_tr, z_tr = time_plot, zz_plot[ch_zz, 0]
                time_tr, z_tr = np.meshgrid(time_tr, z_tr)
                ax = self.figure_Zsing.add_subplot(111)  # add axes

                contours = ax.contourf(time_tr,
                                       z_tr,
                                       data_plot[:,
                                                 ch_zz,
                                                 RtoPlot].T,
                                       vmin=vmin,
                                       vmax=vmax,
                                       levels=NN_cont,
                                       cmap='jet')
                cbar = self.figure_Zsing.colorbar(contours, ax=ax)
                cbar.ax.set_ylabel('deltaTrad/<Trad>', rotation=90)
                if contour_check == '1':
                    ax.contour(time_tr,
                               z_tr,
                               data_plot[:,
                                         ch_zz,
                                         RtoPlot].T,
                               vmin=vmin,
                               vmax=vmax,
                               levels=NN_cont,
                               cmap='binary')
                ax.set_title("R_ch=%g" % (RtoPlot + 1))
                ax.set_ylabel("z [m]")
                ax.set_xlabel("t [s]")
                my_text = ch_zz
                for i in range(len(ch_zz)):
                    ax.annotate(ch_zz[i] +
                                1, (time_tr[i, 0], z_tr[i, 0]), size=8)

                self.figure_Zsing.suptitle(
                    "ECEI, Shot #%d, Filter: %s" %
                    (self.Shot, filter_status), fontsize=10)
                self.static_canvas_Zsing.draw()
                self.sync_tabs(7)
                print("+++ The data has been plotted succesfully. +++")

            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data (first tab)")

    def CrossCal_ECEI_data(self):
        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                tCalB = float(self.tCalB_ed_load.text())
                tCalE = float(self.tCalE_ed_load.text())
                mf = my_funcs.my_funcs()
                mf.Cross_cal_IDA(
                    self.Shot,
                    self.ECEId,
                    self.ECEId_time,
                    self.ECEId_RR,
                    self.ECEId_zz,
                    tCalB,
                    tCalE)
                self.ECEId = mf.ECEId_cal
                self.data_calibrated = True
            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data")

    def plot_EQH(self):
        try:
            self.Shot_EQH = int(self.Shot_ed_EQHt.text())
            self.time_EQH = float(self.timepl_ed_EQHt.text())
            allow_to_load = True
        except Exception as exc:
            # Handle the error gracefully
            tb = traceback.format_exc()
            print(f"An error occurred: {exc}\nTraceback:\n{tb}")
            allow_to_load = False

        if (allow_to_load):
            try:
                import EQH_sfLoad_osam as EQH
                import ECE_sfLoad_osam as ECE
                import importlib
                import aug_sfutils as sf
                importlib.reload(EQH)
                importlib.reload(ECE)
                import matplotlib.pyplot as plt
                from scipy.constants import e, m_e

                # load EQH
                EQ = EQH.EQH()
                EQ.Load(self.Shot_EQH)
                EQ.getrRhop_forTime(self.time_EQH)
                print("+++ EQH has been loaded +++")

                # load CEC
                self.eqm = sf.EQU(self.Shot_EQH, diag="EQH")
                EC = ECE.ECE()
                EC.Load(eqm = self.eqm, Shotnumber=self.Shot_EQH, Diagnostic='CEC', tBegin=0.0, tEnd=10.0)
                EC.remove0chs()
                idx_rztime = EC.find_nearest_idx(EC.rztime, self.time_EQH)
                print("+++ CEC has been loaded +++")

                # load fake R and z from the mixer frequency and magn. field
                # use fake R and z only for general overview
                # correct way: ray tracing
                N_LOS, N_R = 20, 8
                path_to_eceilog = '/shares/departments/AUG/users/osam/LOG_ECEI/'
                with open(path_to_eceilog + "%d.log" % (self.Shot_EQH), 'r') as f:
                    ECEI_LOG = f.read()
                if (self.Shot_EQH > 30000):
                    Bt = float(ECEI_LOG.split(" ")[1])
                    f_LO = float(ECEI_LOG.split(" ")[3])
                else:
                    Bt = float(ECEI_LOG.split(" ")[0].split("=")[1])
                    f_LO = float(ECEI_LOG.split(" ")[1].split("=")[1])

                f_0 = 3.7  # [GHz] initial freq
                ch_spacing = 800  # MHz
                R0 = 1.65  # [m] AUG main radius
                f_array = np.zeros(N_R)
                z_array = np.zeros(N_LOS)
                dz = 0.0322  # [m] - fake dz between LOSs
                z_up = 0.3165  # [m] - fake LOS1 z position
                # z_up = 0.5165 # [m] - fake LOS1 z position

                f_array[0] = f_LO + f_0  # [GHz]
                for i in range(N_R - 1):
                    f_array[i + 1] = f_array[0] + \
                        ch_spacing * 1e-3 * (1 + i)  # [GHz]

                z_array[0] = z_up
                for i in range(N_LOS - 1):
                    z_array[i + 1] = z_array[0] - dz * (i + 1)

                R_array = 2 * e * np.abs(Bt) * R0 / \
                    (2 * np.pi * m_e * f_array * 1.e9)
                R_array = R_array[::-1]
                # z_array = 0.030 * np.ones(len(R_array))
                RR_array, zz_array = np.meshgrid(R_array,z_array)
                print("+++ FakeRz has been created +++")

                # initiate plot
                self.figure_EQHt.clf()  # clear previous figure and axes
                ax = self.figure_EQHt.add_subplot(111)  # create an axis
                contours_rhop = ax.contour(EQ.RR_t, EQ.zz_t, EQ.rhopM_t, 50)
                ax.clabel(contours_rhop, inline=True, fontsize=10)

                my_text = EC.chs_numbers.copy()
                for i, txt in enumerate(my_text):
                    ax.annotate(
                        txt, (EC.R[idx_rztime][i], EC.z[idx_rztime][i] + 0.002), fontsize=8)
                ax.plot(EC.R[idx_rztime], EC.z[idx_rztime], "ko", label="CEC")
                # ax.plot(R_array, z_array, "bo", label="ECEI_fakeRz")
                ax.plot(RR_array, zz_array, "bo", label="ECEI_fakeRz")
                my_text_2 = np.arange(1, 9)
                # for i, txt in enumerate(my_text_2):
                    # ax.annotate(
                        # txt, (R_array[i], z_array[i] + 0.002), fontsize=8)

                ax.set_xlabel("R [m]")
                ax.set_ylabel("z [m]")
                ax.legend()

                self.figure_EQHt.suptitle(
                    "EQH (rhop), Shot #%d, time = %g s" %
                    (self.Shot_EQH, self.time_EQH), fontsize=12)
                # draw the figure
                self.static_canvas_EQHt.draw()
                print("+++ EQH has been plotted +++")

            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
                print("!!! Couldn't load EQH, CEC, fakeRz")

    def f_Rz_plot(self, which_plot):
        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 10})
                # data preparation
                self.tB_ed_RzPl
                tB = float(self.tB_ed_RzPl.text())
                tE = float(self.tE_ed_RzPl.text())
                if (which_plot == 1):
                    tplot_old = float(self.tplot_ed_RzPl.text())
                    dtplot = float(self.dtplot_ed_RzPl.text())
                    tplot = tplot_old - dtplot
                    self.tplot_ed_RzPl.setText("%0.7g" % tplot)
                if (which_plot == 2):
                    tplot_old = float(self.tplot_ed_RzPl.text())
                    dtplot = float(self.dtplot_ed_RzPl.text())
                    tplot = tplot_old + dtplot
                    self.tplot_ed_RzPl.setText("%0.7g" % tplot)
                if (which_plot == 3):
                    tplot = float(self.tplot_ed_RzPl.text())
                    self.counter_save = 0

                dtplot = float(self.dtplot_ed_RzPl.text())
                contour_check = self.Contour_ed_RzPl.text()
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                if (self.data_calibrated):
                    time_plot, data_plot = mf.time_C, mf.ECEId_C
                else:
                    mf.relECEI(mf.ECEId_C)
                    time_plot, data_plot = mf.time_C, mf.ECEId_rel
                filter_status = "None"

                if (self.type_plot_RzPl.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_RzPl.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_RzPl.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_RzPl.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_RzPl.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_RzPl.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_RzPl.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_RzPl.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_RzPl.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_RzPl.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_RzPl.text())
                    pol_ord = int(self.SavGol_ed1_RzPl.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_RzPl.currentText() == 'Binning'):
                    binning_freq = float(self.Binning_ed_RzPl.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                RR_plot, zz_plot = self.ECEId_RR, self.ECEId_zz

                removeLOS_ch = self.chzz_ed_RzPl.text()
                if removeLOS_ch:
                    removeLOS_ch = np.array(
                        self.chzz_ed_RzPl.text().split(','))
                    removeLOS_ch = removeLOS_ch.astype(int) - 1
                else:
                    removeLOS_ch = []
                removeRR_ch = self.chRR_ed_RzPl.text()
                if removeRR_ch:
                    removeRR_ch = np.array(self.chRR_ed_RzPl.text().split(','))
                    removeRR_ch = removeRR_ch.astype(int) - 1
                else:
                    removeRR_ch = []

                NN_LOS, NN_R = data_plot.shape[1], data_plot.shape[2]
                ch_zz = np.arange(NN_LOS)
                ch_zz = np.delete(ch_zz, removeLOS_ch)
                ch_RR = np.arange(NN_R)
                ch_RR = np.delete(ch_RR, removeRR_ch)

                trace_1D = data_plot[:, 6, 3]
                # remove channels
                RR_plot = np.delete(RR_plot, removeLOS_ch, axis=0)
                RR_plot = np.delete(RR_plot, removeRR_ch, axis=1)
                zz_plot = np.delete(zz_plot, removeLOS_ch, axis=0)
                zz_plot = np.delete(zz_plot, removeRR_ch, axis=1)
                data_plot = np.delete(data_plot, removeLOS_ch, axis=1)
                data_plot = np.delete(data_plot, removeRR_ch, axis=2)

                check_vmin_vmax = 0
                if (self.vmin_ed_RzPl.text().replace(
                        '-', '', 1).replace('.', '', 1).isdigit()):
                    vmin = float(self.vmin_ed_RzPl.text())
                    check_vmin_vmax = 1
                else:
                    vmin = None

                if (self.vmax_ed_RzPl.text().replace('.', '', 1).isdigit()):
                    vmax = float(self.vmax_ed_RzPl.text())
                    check_vmin_vmax = 1
                else:
                    vmax = None

                if (self.NNcont_ed_RzPl.text().replace('.', '', 1).isdigit()):
                    NN_cont = int(self.NNcont_ed_RzPl.text())
                else:
                    NN_cont = 20

                # find time index of plot
                idx_tplot = mf.find_nearest_idx(time_plot, tplot)
                time_plot_t, data_plot_t = time_plot[idx_tplot], data_plot[idx_tplot, :, :]

                if (self.Interp_plot_RzPl.currentText() == 'with interpolation'):
                    interp_mask = np.full((NN_LOS, NN_R), False)
                    for i_L in range(NN_LOS):
                        for i_R in range(NN_R):
                            interp_mask[i_L, i_R] = self.checks['%d,%d' % (
                                i_L, i_R)].isChecked()

                    interp_mask = np.delete(interp_mask, removeLOS_ch, axis=0)
                    interp_mask = np.delete(interp_mask, removeRR_ch, axis=1)
                    data_to_interp = data_plot_t.copy()
                    data_to_interp[interp_mask] = np.NaN
                    data_plot_t = mf.nan_interp_2d(data_to_interp)

                if (self.Interp_plot_RzPl.currentText() == 'set to zero'):
                    interp_mask = np.full((NN_LOS, NN_R), False)
                    for i_L in range(NN_LOS):
                        for i_R in range(NN_R):
                            interp_mask[i_L, i_R] = self.checks['%d,%d' % (
                                i_L, i_R)].isChecked()

                    interp_mask = np.delete(interp_mask, removeLOS_ch, axis=0)
                    interp_mask = np.delete(interp_mask, removeRR_ch, axis=1)
                    data_plot_t[interp_mask] = 0.0

                if (self.ImgType_plot_RzPl.currentText() == 'Gaussian'):
                    sigma = float(self.GausSigma_ed_RzSet.text())
                    data_plot_t = mf.gaussian_filter(data_plot_t, sigma)
                    filter_status += "; Img filt: Gaussian, sigma=%g" % (sigma)

                if (self.ImgType_plot_RzPl.currentText() == 'Bilateral'):
                    kernel = self.BilKern_type_RzSet.currentText()
                    kern_size = int(self.BilKernSize_ed_RzSet.text())
                    s0 = int(self.BilS0_ed_RzSet.text())
                    s1 = int(self.BilS1_ed_RzSet.text())
                    data_plot_t = mf.bilateral_filter(
                        data_plot_t, kernel, kern_size, s0, s1)
                    filter_status += "; Img filt: Bilateral, %s, kern_size=%g, s0=%g, s1=%g" % (
                        kernel, kern_size, s0, s1)

                if (self.ImgType_plot_RzPl.currentText() == 'Median'):
                    kernel = self.MedKern_type_RzSet.currentText()
                    kern_size = int(self.MedKernSize_ed_RzSet.text())
                    data_plot_t = mf.median_filter(
                        data_plot_t, kernel, kern_size)
                    filter_status += "; Img filt: Median, %s, kern_size=%g" % (
                        kernel, kern_size)

                if (self.ImgType_plot_RzPl.currentText()
                        == 'Conservative_smoothing'):
                    size_filt = int(self.ConsSize_ed_RzSet.text())
                    data_plot_t = mf.conservative_smoothing_filter(
                        data_plot_t, size_filt)
                    filter_status += "; Img filt: Conservative smoothing, filt_size=%g" % (
                        size_filt)

                # plotting
                # initiate plot
                # default plot 
                if (self.switch_plot_RzPl.currentText() == 'default'):
                    self.figure_RzPl.clf()  # clear previous figure and axes
                    self._static_ax = self.static_canvas_RzPl.figure.subplots(
                        1, 2, sharex=False, sharey=False)  # add axes
                    if (check_vmin_vmax == 1):
                        levels_to_plot = np.linspace(vmin, vmax, NN_cont)
                    if (check_vmin_vmax == 0):
                        levels_to_plot = NN_cont
                    contours = self._static_ax[0].contourf(
                        RR_plot,
                        zz_plot,
                        data_plot_t,
                        vmin=vmin,
                        vmax=vmax,
                        levels=levels_to_plot,
                        cmap='jet')
                    cbar = self.figure_RzPl.colorbar(
                        contours, ax=self._static_ax[0], pad=0.07)
                    cbar.ax.set_ylabel('deltaTrad/<Trad>', rotation=90)
                    if contour_check == '1':
                        self._static_ax[0].contour(
                            RR_plot,
                            zz_plot,
                            data_plot_t,
                            vmin=vmin,
                            vmax=vmax,
                            levels=levels_to_plot,
                            cmap='binary')
                    # cbar.ax.tick_params(labelsize=8, rotation=90)
                    self._static_ax[0].plot(RR_plot, zz_plot, "ko", ms=2)

                    if (self.Interp_plot_RzPl.currentText() == 'set to zero') | (
                            self.Interp_plot_RzPl.currentText() == 'with interpolation'):
                        self._static_ax[0].plot(
                            RR_plot[interp_mask], zz_plot[interp_mask], "wo", ms=6)

                    self._static_ax[0].set_xlabel("R [m]")
                    self._static_ax[0].set_ylabel("z [m]")
                    self._static_ax[0].set_title("t = %0.7g" % (time_plot_t))

                    for i, txt in enumerate(ch_zz):
                        self._static_ax[0].annotate(
                            txt + 1, (RR_plot[i, 0], zz_plot[i, 0]), fontsize=8)

                    for i, txt in enumerate(ch_RR):
                        self._static_ax[0].annotate(
                            txt + 1, (RR_plot[0, i], zz_plot[0, i]), fontsize=8)

                    self._static_ax[1].plot(time_plot, trace_1D)
                    self._static_ax[1].set_xlabel("t [s]")
                    self._static_ax[1].set_ylabel("deltaTrad/<Trad>")
                    self._static_ax[1].set_title(
                        "LOS = 7, R_ch = 4, dt resolut = %g s" %
                        (time_plot[1] - time_plot[0]))
                    self._static_ax[1].axvline(x=time_plot_t, color="k")

                    self.figure_RzPl.suptitle(
                        "ECEI, Shot #%d, Filter: %s" %
                        (self.Shot, filter_status), fontsize=10)
                    if (self.Save_plot_RzPl.currentText() == 'save as pdf') | (
                            (self.Save_plot_RzPl.currentText() == 'save as pdf') & (self.counter_save == 0)):
                        path_to_save = self.path_ed_RzSet.text()
                        self.figure_RzPl.savefig(
                            path_to_save + 'p_%03d.pdf' %
                            (self.counter_save), bbox_inches='tight')
                        self.counter_save += 1
                    if (self.Save_plot_RzPl.currentText() == 'save as png') | (
                            (self.Save_plot_RzPl.currentText() == 'save as pdf') & (self.counter_save == 0)):
                        path_to_save = self.path_ed_RzSet.text()
                        self.figure_RzPl.savefig(
                            path_to_save + 'p_%03d.png' %
                            (self.counter_save), bbox_inches='tight')
                        self.counter_save += 1
                    click_coord = self.static_canvas_RzPl.mpl_connect(
                        'button_press_event', self.mouse_click_Rz)
                    self.static_canvas_RzPl.draw()
                    self.sync_tabs(9)
                    print("+++ The data has been plotted succesfully. +++")

                if (self.switch_plot_RzPl.currentText() == 'velocimetry'):
                    self.figure_RzPl.clf()  # clear previous figure and axes
                    ax = self.figure_RzPl.add_subplot(111,frameon=False)  # add axes
                    if (check_vmin_vmax == 1):
                        levels_to_plot = np.linspace(vmin, vmax, NN_cont)
                    if (check_vmin_vmax == 0):
                        levels_to_plot = NN_cont
                    contours = ax.contourf(
                        RR_plot,
                        zz_plot,
                        data_plot_t,
                        vmin=vmin,
                        vmax=vmax,
                        levels=levels_to_plot,
                        cmap='gray')
                    if contour_check == '1':
                        ax.contour(
                            RR_plot,
                            zz_plot,
                            data_plot_t,
                            vmin=vmin,
                            vmax=vmax,
                            levels=levels_to_plot,
                            cmap='binary')
                    ax.plot(RR_plot, zz_plot, "ko", ms=2)

                    if (self.Interp_plot_RzPl.currentText() == 'set to zero') | (
                            self.Interp_plot_RzPl.currentText() == 'with interpolation'):
                        ax.plot(
                            RR_plot[interp_mask], zz_plot[interp_mask], "wo", ms=6)

                    ax.axis('scaled')
                    ax.set_axis_off()
                    
                    if (self.Save_plot_RzPl.currentText() == 'save as pdf') | (
                            (self.Save_plot_RzPl.currentText() == 'save as pdf') & (self.counter_save == 0)):
                        path_to_save = self.path_ed_RzSet.text()
                        self.figure_RzPl.savefig(
                            path_to_save + 'p_%03d.pdf' %
                            (self.counter_save), bbox_inches='tight')
                        self.counter_save += 1
                    if (self.Save_plot_RzPl.currentText() == 'save as png') | (
                            (self.Save_plot_RzPl.currentText() == 'save as pdf') & (self.counter_save == 0)):
                        path_to_save = self.path_ed_RzSet.text()
                        self.figure_RzPl.savefig(
                            path_to_save + 'p_%03d.png' %
                            (self.counter_save), bbox_inches='tight')
                        self.counter_save += 1
                    click_coord = self.static_canvas_RzPl.mpl_connect(
                        'button_press_event', self.mouse_click_Rz)
                    self.static_canvas_RzPl.draw()
                    self.sync_tabs(9)
                    print("+++ The data has been plotted succesfully. +++")
            except Exception as exc:
                # Handle the error gracefully
                tb = traceback.format_exc()
                print(f"An error occurred: {exc}\nTraceback:\n{tb}")
        else:
            print("Please load the ECEI data (first tab)")

    def mouse_click_Rz(self, event):
        if event.button == 1:
            ix, iy = event.xdata, event.ydata
            print('x = %07g, y = %07g' % (
                ix, iy))
            self.tplot_ed_RzPl.setText("%0.7g" % (ix))
        elif event.button == 3:
            ix, iy = event.xdata, event.ydata
            print('x = %07g, y = %07g' % (
                ix, iy))

        if (event.dblclick == True) & (event.button == 1):
            self.f_Rz_plot(3)

    def sync_tabs(self, number):
        try:
            if (number == 1):
                tB_ed = self.tB_ed_plCh.text()
                tE_ed = self.tE_ed_plCh.text()
                tCnt_ed = self.tCnt_ed_plCh.text()
                dt_ed = self.dt_ed_plCh.text()
                Fourier_cut = self.Fourier_cut_plCh.text()
                Fourier2_cut = self.Fourier2_cut_plCh.text()
                Savgol_ed0 = self.SavGol_ed0_plCh.text()
                Savgol_ed1 = self.SavGol_ed1_plCh.text()
                Binning_ed = self.Binning_ed_plCh.text()

            if (number == 2):
                tB_ed = self.tB_ed_LOS.text()
                tE_ed = self.tE_ed_LOS.text()
                tCnt_ed = self.tCnt_ed_LOS.text()
                dt_ed = self.dt_ed_LOS.text()
                Fourier_cut = self.Fourier_cut_LOS.text()
                Fourier2_cut = self.Fourier2_cut_LOS.text()
                Savgol_ed0 = self.SavGol_ed0_LOS.text()
                Savgol_ed1 = self.SavGol_ed1_LOS.text()
                Binning_ed = self.Binning_ed_LOS.text()

            if (number == 3):
                tB_ed = self.tB_ed_FFT.text()
                tE_ed = self.tE_ed_FFT.text()
                tCnt_ed = self.tCnt_ed_FFT.text()
                dt_ed = self.dt_ed_FFT.text()
                Fourier_cut = self.Fourier_cut_FFT.text()
                Fourier2_cut = self.Fourier2_cut_FFT.text()
                Savgol_ed0 = self.SavGol_ed0_FFT.text()
                Savgol_ed1 = self.SavGol_ed1_FFT.text()
                Binning_ed = self.Binning_ed_FFT.text()

            if (number == 4):
                tB_ed = self.tB_ed_Rtr.text()
                tE_ed = self.tE_ed_Rtr.text()
                tCnt_ed = self.tCnt_ed_Rtr.text()
                dt_ed = self.dt_ed_Rtr.text()
                Fourier_cut = self.Fourier_cut_Rtr.text()
                Fourier2_cut = self.Fourier2_cut_Rtr.text()
                Savgol_ed0 = self.SavGol_ed0_Rtr.text()
                Savgol_ed1 = self.SavGol_ed1_Rtr.text()
                Binning_ed = self.Binning_ed_Rtr.text()

            if (number == 5):
                tB_ed = self.tB_ed_Rsing.text()
                tE_ed = self.tE_ed_Rsing.text()
                tCnt_ed = self.tCnt_ed_Rsing.text()
                dt_ed = self.dt_ed_Rsing.text()
                Fourier_cut = self.Fourier_cut_Rsing.text()
                Fourier2_cut = self.Fourier2_cut_Rsing.text()
                Savgol_ed0 = self.SavGol_ed0_Rsing.text()
                Savgol_ed1 = self.SavGol_ed1_Rsing.text()
                Binning_ed = self.Binning_ed_Rsing.text()

            if (number == 6):
                tB_ed = self.tB_ed_Ztr.text()
                tE_ed = self.tE_ed_Ztr.text()
                tCnt_ed = self.tCnt_ed_Ztr.text()
                dt_ed = self.dt_ed_Ztr.text()
                Fourier_cut = self.Fourier_cut_Ztr.text()
                Fourier2_cut = self.Fourier2_cut_Ztr.text()
                Savgol_ed0 = self.SavGol_ed0_Ztr.text()
                Savgol_ed1 = self.SavGol_ed1_Ztr.text()
                Binning_ed = self.Binning_ed_Ztr.text()

            if (number == 7):
                tB_ed = self.tB_ed_Zsing.text()
                tE_ed = self.tE_ed_Zsing.text()
                tCnt_ed = self.tCnt_ed_Zsing.text()
                dt_ed = self.dt_ed_Zsing.text()
                Fourier_cut = self.Fourier_cut_Zsing.text()
                Fourier2_cut = self.Fourier2_cut_Zsing.text()
                Savgol_ed0 = self.SavGol_ed0_Zsing.text()
                Savgol_ed1 = self.SavGol_ed1_Zsing.text()
                Binning_ed = self.Binning_ed_Zsing.text()

            if (number == 9):
                tB_ed = self.tB_ed_RzPl.text()
                tE_ed = self.tE_ed_RzPl.text()
                tCnt_ed = self.tCnt_ed_RzPl.text()
                dt_ed = self.dt_ed_RzPl.text()
                Fourier_cut = self.Fourier_cut_RzPl.text()
                Fourier2_cut = self.Fourier2_cut_RzPl.text()
                Savgol_ed0 = self.SavGol_ed0_RzPl.text()
                Savgol_ed1 = self.SavGol_ed1_RzPl.text()
                Binning_ed = self.Binning_ed_RzPl.text()

            # 1
            self.tB_ed_plCh.setText(tB_ed)
            self.tE_ed_plCh.setText(tE_ed)
            self.tCnt_ed_plCh.setText(tCnt_ed)
            self.dt_ed_plCh.setText(dt_ed)
            self.Fourier_cut_plCh.setText(Fourier_cut)
            self.Fourier2_cut_plCh.setText(Fourier2_cut)
            self.SavGol_ed0_plCh.setText(Savgol_ed0)
            self.SavGol_ed1_plCh.setText(Savgol_ed1)
            self.Binning_ed_plCh.setText(Binning_ed)
            # 2
            self.tB_ed_LOS.setText(tB_ed)
            self.tE_ed_LOS.setText(tE_ed)
            self.tCnt_ed_LOS.setText(tCnt_ed)
            self.dt_ed_LOS.setText(dt_ed)
            self.Fourier_cut_LOS.setText(Fourier_cut)
            self.Fourier2_cut_LOS.setText(Fourier2_cut)
            self.SavGol_ed0_LOS.setText(Savgol_ed0)
            self.SavGol_ed1_LOS.setText(Savgol_ed1)
            self.Binning_ed_LOS.setText(Binning_ed)
            # 3
            self.tB_ed_FFT.setText(tB_ed)
            self.tE_ed_FFT.setText(tE_ed)
            self.tCnt_ed_FFT.setText(tCnt_ed)
            self.dt_ed_FFT.setText(dt_ed)
            self.Fourier_cut_FFT.setText(Fourier_cut)
            self.Fourier2_cut_FFT.setText(Fourier2_cut)
            self.SavGol_ed0_FFT.setText(Savgol_ed0)
            self.SavGol_ed1_FFT.setText(Savgol_ed1)
            self.Binning_ed_FFT.setText(Binning_ed)
            # 4
            self.tB_ed_Rtr.setText(tB_ed)
            self.tE_ed_Rtr.setText(tE_ed)
            self.tCnt_ed_Rtr.setText(tCnt_ed)
            self.dt_ed_Rtr.setText(dt_ed)
            self.Fourier_cut_Rtr.setText(Fourier_cut)
            self.Fourier2_cut_Rtr.setText(Fourier2_cut)
            self.SavGol_ed0_Rtr.setText(Savgol_ed0)
            self.SavGol_ed1_Rtr.setText(Savgol_ed1)
            self.Binning_ed_Rtr.setText(Binning_ed)
            # 5
            self.tB_ed_Rsing.setText(tB_ed)
            self.tE_ed_Rsing.setText(tE_ed)
            self.tCnt_ed_Rsing.setText(tCnt_ed)
            self.dt_ed_Rsing.setText(dt_ed)
            self.Fourier_cut_Rsing.setText(Fourier_cut)
            self.Fourier2_cut_Rsing.setText(Fourier2_cut)
            self.SavGol_ed0_Rsing.setText(Savgol_ed0)
            self.SavGol_ed1_Rsing.setText(Savgol_ed1)
            self.Binning_ed_Rsing.setText(Binning_ed)
            # 6
            self.tB_ed_Ztr.setText(tB_ed)
            self.tE_ed_Ztr.setText(tE_ed)
            self.tCnt_ed_Ztr.setText(tCnt_ed)
            self.dt_ed_Ztr.setText(dt_ed)
            self.Fourier_cut_Ztr.setText(Fourier_cut)
            self.Fourier2_cut_Ztr.setText(Fourier2_cut)
            self.SavGol_ed0_Ztr.setText(Savgol_ed0)
            self.SavGol_ed1_Ztr.setText(Savgol_ed1)
            self.Binning_ed_Ztr.setText(Binning_ed)
            # 7
            self.tB_ed_Zsing.setText(tB_ed)
            self.tE_ed_Zsing.setText(tE_ed)
            self.tCnt_ed_Zsing.setText(tCnt_ed)
            self.dt_ed_Zsing.setText(dt_ed)
            self.Fourier_cut_Zsing.setText(Fourier_cut)
            self.Fourier2_cut_Zsing.setText(Fourier2_cut)
            self.SavGol_ed0_Zsing.setText(Savgol_ed0)
            self.SavGol_ed1_Zsing.setText(Savgol_ed1)
            self.Binning_ed_Zsing.setText(Binning_ed)
            # 9
            self.tB_ed_RzPl.setText(tB_ed)
            self.tE_ed_RzPl.setText(tE_ed)
            self.tCnt_ed_RzPl.setText(tCnt_ed)
            self.dt_ed_RzPl.setText(dt_ed)
            self.Fourier_cut_RzPl.setText(Fourier_cut)
            self.Fourier2_cut_RzPl.setText(Fourier2_cut)
            self.SavGol_ed0_RzPl.setText(Savgol_ed0)
            self.SavGol_ed1_RzPl.setText(Savgol_ed1)
            self.Binning_ed_RzPl.setText(Binning_ed)

        except Exception as exc:
            # Handle the error gracefully
            tb = traceback.format_exc()
            print(f"An error occurred: {exc}\nTraceback:\n{tb}")
            print("!!! Couldn't synchronize tabs.")


# -------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
