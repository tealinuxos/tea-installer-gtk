#!/usr/bin/python3

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Vte, GLib
from shutil import rmtree
import tarfile
import sys, os
from optparse import OptionParser
sys.path.append('/usr/share/gdebi')


class MainWindow(Gtk.Assistant):
    def __init__(self, filename):
        Gtk.Assistant.__init__(self)

        self.list_package = Gtk.ListStore(str)
        self.tea_file_chooser = Gtk.FileChooserButton()
        self.page1 = None
        self.page2 = None
        self.page3 = None

        self.create_page_1()
        self.create_page_2()
        self.create_page_3()
        self.connect('cancel', Gtk.main_quit)

        # add info button
        info_button = Gtk.MenuToolButton(label='info')
        info_menu = Gtk.Menu()
        help_menu_item = Gtk.MenuItem()
        help_menu_item.set_label('Bantuan')
        help_menu_item.connect('activate', self.help_activated)
        info_menu.append(help_menu_item)
        about_menu_item = Gtk.MenuItem()
        about_menu_item.set_label('Tentang')
        about_menu_item.connect('activate', self.about_activated)
        info_menu.append(about_menu_item)
        info_button.connect('clicked', self.popup_info, info_button)
        self.add_action_widget(info_button)
        info_button.set_menu(info_menu)
        self.set_size_request(400, 200)

        global opts, args
        print(args)
        if args:
            self.tea_file_chooser.set_filename(args[0])
            self.process_file_tea()
            self.set_current_page(1)
            self.commit()
        if opts.ask is True and args:
            self.set_current_page(2)
            self.install_packages()
            self.commit()
        self.connect('prepare', self.prepare_handler)
        self.show_all()
        Gtk.main()

    def popup_info(self, widget, event):
        info_menu = Gtk.Menu()
        help_menu_item = Gtk.MenuItem()
        help_menu_item.set_label('Bantuan')
        help_menu_item.connect('activate', self.help_activated)
        info_menu.append(help_menu_item)
        about_menu_item = Gtk.MenuItem()
        about_menu_item.set_label('Tentang')
        about_menu_item.connect('activate', self.about_activated)
        info_menu.append(about_menu_item)
        print('info clicked')
        print(dir(widget))
        print(event)
        info_menu.popup(None,
                        None,
                        None,
                        None,
                        widget,
                        Gtk.get_current_event_time())
        return True

    def help_activated(self, *args):
        print('help activated')
        print(args)

    def about_activated(self, *args):
        print('about activated')
        print(args)

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
        self.tea_file_chooser.set_hexpand(True)
        self.tea_file_chooser.add_filter(filter)
        self.tea_file_chooser.connect('selection-changed', self.tea_file_selected)

        # self.connect('prepare', self.process_file_tea, self.page2)
        self.page1 = Gtk.Box(spacing=6)
        self.page1.set_orientation(Gtk.Orientation.VERTICAL)
        self.page1.pack_start(welcome_label, 0, 0, 0)
        self.page1.pack_start(hint_label, 0, 0, 0)
        self.page1.pack_start(self.tea_file_chooser, 0, 1, 0)

        self.append_page(self.page1)
        self.set_page_type(self.page1, Gtk.AssistantPageType.INTRO)
        self.set_page_title(self.page1, 'Pilih file')
        # self.set_forward_page_func(self.process_file_tea)

    def tea_file_selected(self, *args):
        self.set_page_complete(self.page1, True)

    def process_file_tea(self, *args):
        try:
            try:
                rmtree('/tmp/.teatemp')
            except FileNotFoundError:
                pass
            open_file = tarfile.open(self.page1.get_children()[2].get_filename(), 'r:gz')
            print('nama file:'+self.page1.get_children()[2].get_filename())
            open_file.extractall('/tmp/.teatemp')
            open_file.close()
            self.list_package.clear()
            for item in os.listdir('/tmp/.teatemp'):
                if item.endswith('.deb'):
                    self.list_package.append([item[0:-4]])
                    print(item)
            self.text_on_page2.set_markup('<b>'+self.page1.get_children()[2].get_filename().split('/')[-1] + '</b> akan memasang paket-paket berikut:')
            with open('/tmp/.teatemp/size') as o:
                installed_size = o.readline()
                print(installed_size)
            self.text_bottom_page2.set_label('Ukuran berkas terpasang '+installed_size+'\n'
                                             'Lanjutkan memasang paket-paket tersebut?')
            # self.connect('prepare', self.install_packages)
        except (ValueError, FileNotFoundError):
            self.text_bottom_page2.set_label('Lanjutkan memasang paket-paket tersebut?')

    def create_page_2(self):
        self.text_bottom_page2 = Gtk.Label()
        self.text_on_page2 = Gtk.Label()
        treeview = Gtk.TreeView()
        treeview.set_model(self.list_package)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title='Nama Paket', cell_renderer=renderer, text=0)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_resizable(True)
        column.set_min_width(280)
        treeview.append_column(column)
        self.page2 = Gtk.Box(spacing=6)
        self.page2.set_orientation(Gtk.Orientation.VERTICAL)
        self.text_on_page2.set_halign(Gtk.Align.START)
        # self.text_on_page2.set_margin_bottom(6)
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
        self.set_page_complete(self.page2, True)

    def create_page_3(self):
        self.terminal = Vte.Terminal()
        self.page3 = Gtk.Box(spacing=6)
        self.page3.set_orientation(Gtk.Orientation.VERTICAL)
        label = Gtk.Label(label='Menginstall..')
        self.terminal.set_size_request(300,200)
        self.progress = Gtk.ProgressBar()
        self.progress.set_text('Memasang...')
        self.progress.set_show_text(True)
        self.page3.add(label)
        self.page3.add(self.progress)
        self.page3.add(self.terminal)
        self.append_page(self.page3)
        self.set_page_title(self.page3, 'Memasang')

    def install_packages(self, *args):
        try:
            command = ["/usr/bin/dpkg", "-i", "-G"]
            for deb in os.listdir('/tmp/.teatemp/'):
                if deb.endswith('.deb'):
                    command.append(deb)
            self.page3.set_orientation(Gtk.Orientation.VERTICAL)
            print(command)

            def install_complete(terminal, status, *args):
                self.progress.set_text('Selesai')
                self.progress.set_fraction(1)
                print("exit status: ")
                print(status)

            def pulse_bar(*args):
                self.progress.pulse()

            # self.terminal.connect('eof', install_complete)
            self.terminal.connect('child-exited', install_complete)
            self.terminal.connect('contents-changed', pulse_bar)
            self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT,
                '/tmp/.teatemp',
                command,
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None,

            )
        except (KeyError, FileNotFoundError):
            pass

    def prepare_handler(self, *args):
        if self.get_current_page() == 0:
            pass
        elif self.get_current_page() == 1:
            self.process_file_tea()
        else:
            self.install_packages()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-n', '--no-ask', dest='ask', default=False, action='store_true')
    (opts, args) = parser.parse_args()
    try:
        try:
            MainWindow(sys.argv[1])
        except IndexError:
            MainWindow(None)
    except KeyboardInterrupt:
        sys.exit()

