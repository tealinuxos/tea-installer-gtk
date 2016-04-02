#!/usr/bin/python3

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk
from shutil import rmtree
import tarfile
import sys, os

class MainWindow(Gtk.Assistant):
    def __init__(self, filename):
        Gtk.Assistant.__init__(self)
        self.page1 = None
        self.page2 = None

        self.create_page_1()
        self.create_page_2()

        self.set_size_request(400, 200)
        self.show_all()
        Gtk.main()

    def create_page_1(self):
        welcome_label = Gtk.Label("Selamat datang di Tea Installer")
        welcome_label.set_halign(Gtk.Align.START)
        welcome_label.set_margin_bottom(6)

        hint_label = Gtk.Label(label="Pilih sebuah file .tea")
        hint_label.set_line_wrap(True)
        hint_label.set_halign(Gtk.Align.START)
        hint_label.set_line_wrap_mode(Gtk.WrapMode.WORD)

        filter = Gtk.FileFilter()
        filter.add_pattern('*.tea')
        filter.set_name('.tea file')
        tea_file_chooser = Gtk.FileChooserButton()
        tea_file_chooser.set_hexpand(True)
        tea_file_chooser.add_filter(filter)
        tea_file_chooser.connect('selection-changed', self.tea_file_selected)

        self.connect('prepare', self.process_file_tea, self.page2)

        self.page1 = Gtk.Box(spacing=6)
        self.page1.set_orientation(Gtk.Orientation.VERTICAL)
        self.page1.pack_start(welcome_label, 0, 0, 0)
        self.page1.pack_start(hint_label, 0, 0, 0)
        self.page1.pack_start(tea_file_chooser, 0, 1, 0)

        self.append_page(self.page1)
        self.set_page_type(self.page1, Gtk.AssistantPageType.INTRO)
        self.set_page_title(self.page1, 'Pilih file')
        # self.set_forward_page_func(self.process_file_tea)

    def tea_file_selected(self, *args):
        self.set_page_complete(self.page1, True)

    def process_file_tea(self, *args):
        try:
            try:
                rmtree('/tmp/teatemp')
            except FileNotFoundError:
                pass
            open_file = tarfile.open(self.page1.get_children()[2].get_filename(), 'r:gz')
            print('nama file:'+self.page1.get_children()[2].get_filename())
            open_file.extractall('/tmp/teatemp')
            open_file.close()
            self.list_package.clear()
            for item in os.listdir('/tmp/teatemp'):
                if item.endswith('.deb'):
                    self.list_package.append([item[0:-4]])
                    print(item)
            self.text_on_page2.set_markup('<b>'+self.page1.get_children()[2].get_filename().split('/')[-1] + '</b> akan memasang paket-paket berikut:')
            with open('/tmp/teatemp/size') as o:
                self.installed_size = o.readline()
                print(self.installed_size)
            self.text_bottom_page2.set_label('Ukuran berkas terpasang '+self.installed_size+'\n'
                                             'Lanjutkan memasang paket-paket tersebut?')
        except ValueError:
            pass

    def create_page_2(self):
        treeview = Gtk.TreeView()
        self.list_package = Gtk.ListStore(str)
        treeview.set_model(self.list_package)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title='Nama Paket', cell_renderer=renderer, text=0)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_resizable(True)
        column.set_min_width(280)
        treeview.append_column(column)
        self.page2 = Gtk.Box(spacing=6)
        self.page2.set_orientation(Gtk.Orientation.VERTICAL)
        self.text_on_page2 = Gtk.Label()
        self.text_on_page2.set_halign(Gtk.Align.START)
        # self.text_on_page2.set_margin_bottom(6)
        self.text_bottom_page2 = Gtk.Label()
        self.text_bottom_page2.set_halign(Gtk.Align.START)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.add(treeview)
        self.page2.add(self.text_on_page2)
        self.page2.add(scroll)
        self.page2.add(self.text_bottom_page2)
        self.append_page(self.page2)
        self.set_page_title(self.page2, 'Konfirmasi')
        # self.set_page_type(self.page2, Gtk.AssistantPageType.CUSTOM)

if __name__ == '__main__':
    try:
        MainWindow(sys.argv[1])
    except IndexError:
        MainWindow(None)
