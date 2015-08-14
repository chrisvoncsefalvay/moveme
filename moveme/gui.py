import npyscreen, curses
from forms import *
import yaml
from os import path, getcwd
from moveme.db.objects import Application

class MoveApp(npyscreen.NPSAppManaged):
    def onStart(self):
        # When Application starts, set up the Forms that will be used.

        cfg = yaml.safe_load(open('config.yaml'))
        if cfg["database"]["engine"] == "sqlite":
            engine_string = "sqlite:///%s" % (path.join(getcwd(), cfg["database"]["path"]))
        else:
            engine_string = "%s://%s" % (cfg["database"]["engine"], cfg["database"]["path"])

        self.application_logic = Application(printer_name=cfg["printer"]["name"], db_path=engine_string)
        npyscreen.setTheme(eval("npyscreen.Themes.%s" % cfg["gui"]["theme"]))

        self.addForm("MAIN", ItemListDisplay, name="Items")
        self.addForm("BOXES", BoxListDisplay, name="Boxes")
        self.addForm("POPUPITEM", PopupItemEditor, name="Item editor")
        self.addForm("POPUPBOX", PopupBoxEditor, name="Box editor")


def main():
    MA = MoveApp()
    MA.run()