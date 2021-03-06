import string
from ctypes import windll
import subprocess
import shutil
import sys
from threading import Thread
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import os
import pandas as pd
from functools import partial
from datetime import date
import time

app = QtWidgets.QApplication([])

prog = uic.loadUi('layout.ui')

'''
THREADS
'''


class th(Thread):
    # declarar as variaveis que terão interação da funcao com a interface UI
    def __init__(self, drive, jogo, status, botao_copia, botao_lista, botao_tudo, pesquisa, frame):
        # variaveis que herdam os componentes
        self.drive = drive
        self.jogo = jogo
        self.status = status
        self.botao = botao_copia
        self.botao_lista = botao_lista
        self.botao_tudo = botao_tudo
        self.pesquisa = pesquisa
        self.frame = frame

        super().__init__()

    def copia_arquivos(self):

        try:
            caminho = os.path.join(os.getcwd(), 'Jogos',
                                   self.jogo.currentItem().text())

            from os import walk
            filenames = next(walk(caminho), (None, None, []))[
                2]  # [] if no file
            # copia os arquivos para a pasta de destino
            contador_arquivo = 0
            total_arquivos = len(filenames)
            for file in filenames:
                contador_arquivo += 1
                self.status.setText(
                    f'Copiando o arquivo {file}, {contador_arquivo}/{total_arquivos}...')
                self.botao.setEnabled(False)
                self.botao_lista.setEnabled(False)
                self.botao_tudo.setEnabled(False)
                dst = os.path.join(self.drive.currentText(), file)
                src = os.path.join(caminho, file)
                shutil.copyfile(src, dst)
            self.botao.setEnabled(True)
            self.botao_lista.setEnabled(True)
            self.botao_tudo.setEnabled(True)
            self.status.setText(
                f'{total_arquivos} arquivos copiados com sucesso!')
            self.pesquisa.setFocus()
        except Exception as e:
            print(e)
            self.status.setText('Ocorreu um erro! {}'.format(e))

    def run(self):
        self.copia_arquivos()
        self.jogo.clear()
        self.frame.setVisible(False)
        destino = self.drive.currentText()
        print(destino[:2])
        subprocess.call("explorer " + destino[:2], shell=True)


'''
FIM THREADS
'''


def exibeTudo():
    inicia, caminhos = verifica_path()

    if caminhos:
        prog.listWidget.clear()
        for pasta in caminhos:
            pasta = pasta.replace('\\', '/')
            for diretorio, subpastas, arquivos in os.walk(pasta):
                pastas = diretorio.split('\\')
                try:
                    prog.listWidget.addItem(
                        diretorio.replace('\\', '/').upper())
                except:
                    pass
    else:
        pasta = './jogos'
        prog.listWidget.clear()
        for diretorio, subpastas, arquivos in os.walk(pasta):
            pastas = diretorio.split('\\')
            try:
                prog.listWidget.addItem(pastas[1])
            except:
                prog.label_status.setText('Nenhum jogo encontrado!')
                prog.frame.setVisible(False)
                # prog.listWidget.addItem('Não foi possível listar')
    prog.label_status.setText(
        'Foi encontrado ' + str(prog.listWidget.count()) + ' jogos')
    if prog.listWidget.count() == 0:
        prog.label_status.setText('Nenhum jogo encontrado!')
        prog.frame.setVisible(False)
    else:
        prog.frame.setVisible(True)
    prog.lineEdit.setFocus()


def pesquisa(nome):
    inicia, caminhos = verifica_path()

    if caminhos:
        prog.listWidget.clear()
        for pasta in caminhos:
            pasta = pasta.replace('\\', '/')
            for diretorio, subpastas, arquivos in os.walk(pasta):
                try:
                    pastas = diretorio.split('\\')

                    if str(nome).lower() in str(pastas[1]).lower():
                        prog.listWidget.addItem(
                            str(diretorio).replace('\\', '/').upper())
                except:
                    pass
    else:
        pasta = './jogos'
        prog.listWidget.clear()
        for diretorio, subpastas, arquivos in os.walk(pasta):
            try:
                pastas = diretorio.split('\\')

                if str(nome).lower() in str(pastas[1]).lower():
                    prog.listWidget.addItem(str(pastas[1]).upper())
            except:
                pass
    prog.label_status.setText(
        'Foi encontrado ' + str(prog.listWidget.count()) + ' jogos')
    if prog.listWidget.count() == 0:
        prog.label_status.setText('Nenhum jogo encontrado!')
        prog.frame.setVisible(False)
    else:
        prog.frame.setVisible(True)
    prog.lineEdit.setFocus()


def current_drive():
    print(current_drive())
    return os.path.splitdrive(os.getcwd())[0]


def abre_pasta():
    inicia, caminhos = verifica_path()
    if caminhos:
        try:
            caminho = os.path.join(prog.listWidget.currentItem().text())
            caminho = caminho.replace('/', '\\')
            print(caminho)
            subprocess.Popen(f'explorer "{caminho}"')
        except Exception as e:
            print(e)

    else:
        caminho = os.path.join(os.getcwd(), 'Jogos',
                               prog.listWidget.currentItem().text())
        print(caminho)
        subprocess.call("explorer " + caminho)


def lista_drivers():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter+':/')
        bitmask >>= 1
    prog.combo_drive.addItems(drives)
    return drives


def copiar_arquivos():
    t = th(prog.combo_drive, prog.listWidget,
           prog.label_status, prog.bt_copiar, prog.pushButton_2, prog.pushButton, prog.lineEdit, prog.frame)

    retorno = t.start()


def geralista():
    inicia, caminhos = verifica_path()

    if inicia:
        if caminhos:
            with open('lista_dos_jogos.txt', 'w+') as f:
                for pasta in caminhos:
                    pasta = pasta.replace('\\', '/')
                    try:
                        for diretorio, subpastas, arquivos in os.walk(pasta):
                            pastas = diretorio.split('\\')
                            try:
                                f.write(pastas[1]+'\n')
                            except:
                                pass
                    except Exception as e:
                        print(e)
        else:
            pasta = './jogos'
            with open('lista_dos_jogos.txt', 'w+') as f:
                for diretorio, subpastas, arquivos in os.walk(pasta):
                    pastas = diretorio.split('\\')
                    try:
                        f.write(pastas[1]+'\n')
                    except:
                        pass


def verifica_path():
    with open('path.txt', 'r') as f:
        linhas = f.readlines()
        uso = ''
        txt = ''
        caminhos = []

        for linha in linhas:
            if not '#' in linha:
                print('leitura: ' + linha)
                if 'TXT=SIM' in linha:
                    txt = linha.split('=')[1].strip()
                if 'HABILITA=SIM' in linha:
                    uso = linha.split('=')[1].strip()
                if 'CAMINHO1=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO2=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO3=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO4=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO5=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO6=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO7=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO8=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO9=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
                if 'CAMINHO10=' in linha:
                    caminhos.append(linha.split('=')[1].strip())
            # else:
            #     print('leitura #: ' + linha)
        if uso == 'SIM':
            return txt, caminhos
        else:
            return txt, False


prog.frame.setVisible(False)
lista_drivers()
geralista()

prog.lineEdit.setFocus()
prog.pushButton.clicked.connect(lambda: exibeTudo())
prog.pushButton_2.clicked.connect(lambda: pesquisa(prog.lineEdit.text()))
prog.listWidget.itemDoubleClicked.connect(lambda: abre_pasta())
prog.bt_copiar.clicked.connect(lambda: copiar_arquivos())
prog.show()
app.exec()
