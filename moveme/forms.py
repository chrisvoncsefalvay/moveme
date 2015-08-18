from types import NoneType
import npyscreen
from sys import exit
from utils.generate_uuid import generate_UUID
from moveme.utils.timestamp import make_timestamp

class PrintItemUUIDButton(npyscreen.ButtonPress):

    def whenPressed(self):
        self.parent.parentApp.application_logic.label(self.parent.wg_uuid.value)
        npyscreen.notify_wait("Printing item reference label. Please wait.")

class PrintBoxRefButton(npyscreen.ButtonPress):

    def whenPressed(self):
        try:
            _val = self.parent.parentApp.application_logic.query_boxids()[self.parent.wg_in_box.value]
        except Exception as e:
            _val = None

        if _val:
            self.parent.parentApp.application_logic.label(_val)
            npyscreen.notify_wait("Printing box reference label. Please wait.")
        else:
            npyscreen.notify_wait("Sorry, but I cannot print you a box label if you don't have a box selected.")

class PopupItemEditor(npyscreen.ActionPopupWide):
    def create(self):
        self.value = None
        self.wg_uuid = self.add(npyscreen.TitleFixedText, name="Item UUID: ")
        self.wg_description = self.add(npyscreen.TitleText, use_two_lines=False, name="Description: ")
        self.wg_in_box = self.add(npyscreen.TitleCombo,
                                  name="Box UUID: ",
                                  values=self.parentApp.application_logic.query_boxids())
        self.wg_last_modified = self.add(npyscreen.TitleFixedText, name="Last modified")
        self.print_button = self.add(PrintItemUUIDButton, name="Item label", relx=-18, rely=10)
        self.print_box = self.add(PrintBoxRefButton, name="Box label", relx=-18, rely=8)

    def beforeEditing(self):
        if self.value:
            self.preexisting_item=True
            record = self.parentApp.application_logic.query_item_by_uuid(self.value)
            self.name = record.item_uuid
            self.wg_last_modified.value = record.last_modified
            self.wg_uuid.value = record.item_uuid
            self.wg_description.value = record.description

            try:
                associated_box_value = self.parentApp.application_logic.query_boxids().index(record.in_box)
            except ValueError:
                npyscreen.notify(message="It looks like the box this item as associated with has been deleted. "
                                         "No worries, though - the box assignment of this item has now been zeroed.",
                                 title="Data integrity error",
                                 form_color="STANDOUT")

                associated_box_value = ""

            self.wg_in_box.value = associated_box_value
        else:
            self.preexisting_item=False
            self.name = "New item"
            self.wg_uuid.value = generate_UUID("item")
            self.wg_description.value = ""
            self.wg_in_box.value = ""
            self.wg_last_modified.value = "Just now"
        self.wg_in_box.values = self.parentApp.application_logic.query_boxids()

    def on_ok(self):
        if type(self.wg_in_box.value) is int:
            try:
                box = self.parentApp.application_logic.query_boxids()[self.wg_in_box.value]
            except IndexError, TypeError:
                box = None
        else:
            box = None

        if self.preexisting_item:
            self.parentApp.application_logic.alter_item_by_uuid(item_uuid=self.wg_uuid.value,
                                                                description=self.wg_description.value,
                                                                in_box=box)
        else:
            self.parentApp.application_logic.create_item(item_uuid=self.wg_uuid.value,
                                                         description=self.wg_description.value or None,
                                                         in_box=box)
        self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

# ItemList

class ItemList(npyscreen.MultiLineAction):

    def __init__(self, *args, **kwargs):
        super(ItemList, self).__init__(*args,
                                       **kwargs)
        self.add_handlers({
            "^N": self.when_add_item,
            "^D": self.when_delete_item,
            "^C": self.try_exit,
            "^T": self.switch_view
        })

    def when_add_item(self, *args, **kwargs):
        self.parent.parentApp.getForm("POPUPITEM").value = None
        self.parent.parentApp.switchForm("POPUPITEM")

    def when_delete_item(self, *args, **kwargs):
        delete_confirmation = npyscreen.notify_ok_cancel(message="You're about to delete this item. There's NO UNDO. "
                                                               "Are you sure?",
                                                         title="WARNING")

        if delete_confirmation is True:
            self.parent.parentApp.application_logic.delete_item_by_uuid(self.values[self.cursor_line][0])
            self.parent.update_list()

    def switch_view(self, *args,**kwargs):
        self.parent.parentApp.switchForm("BOXES")

    def try_exit(self):
        exit_confirmation = npyscreen.notify_ok_cancel(message="Really wanna exit?", title="Warning")
        if exit_confirmation is True:
            npyscreen.blank_terminal()
            exit(0)

    def actionHighlighted(self, act_on_this, keypress):
        self.parent.parentApp.getForm("POPUPITEM").value=act_on_this[0]
        self.parent.parentApp.switchForm("POPUPITEM")

    def display_value(self, vl):
        return("%s: %s" % (vl[0], vl[1]))

class ItemListDisplay(npyscreen.FormMuttActive):
    MAIN_WIDGET_CLASS = ItemList
    MAIN_WIDGET_CLASS_START_LINE = 1
    COMMAND_WIDGET_CLASS = npyscreen.FixedText

    def beforeEditing(self):
        self.update_list()

    def update_list(self):
        self.wMain.values = self.parentApp.application_logic.query_items()

        if type(self.wMain.values) is NoneType:
            table_size = 0
        else:
            table_size = len(self.wMain.values)

        self.wMain.values = self.parentApp.application_logic.query_items()
        self.wStatus1.value = "ITEM ENTRY PANEL \t \t Registering %s items in total." % table_size
        self.wStatus2.value = "Press ^N to create a new box. Press ^T to switch to item management."
        self.wCommand.value = "To search and filter, press 'l'."

        self.wMain.display()

# PopupBoxEditor

class PopupBoxEditor(npyscreen.ActionPopupWide):
    def create(self):
        self.value = None
        self.wg_uuid = self.add(npyscreen.TitleFixedText, name="Box UUID: ")
        self.wg_description = self.add(npyscreen.TitleText, use_two_lines=False, name="Description: ")
        self.wg_location = self.add(npyscreen.TitleCombo, name="Status: ", values=['In progress',
                                                                                 'Packed and open',
                                                                                 'Sealed',
                                                                                 'Loaded',
                                                                                 'Unloaded',
                                                                                 'Opened',
                                                                                 'Unpacked'])
        self.wg_last_modified = self.add(npyscreen.TitleFixedText, name="Last modified: ")
        self.print_box = self.add(PrintItemUUIDButton, name="Box label", relx=-18, rely=8)

    def beforeEditing(self):
        if self.value:
            self.preexisting_item=True
            record = self.parentApp.application_logic.query_box_by_uuid(self.value)
            self.name = record.box_uuid
            self.wg_uuid.value = record.box_uuid
            self.wg_description.value = record.description
            self.wg_location.value = record.location
            self.wg_last_modified = record.last_modified
        else:
            self.preexisting_item=False
            self.name = "New box"
            self.wg_uuid.value = generate_UUID("box")
            self.wg_description.value = ""
            self.wg_location.value = ""
            self.wg_last_modified = "Just now"

    def on_ok(self):
        if self.preexisting_item:
            self.parentApp.application_logic.alter_box_by_uuid(box_uuid=self.wg_uuid.value,
                                                               description=self.wg_description.value,
                                                               location=self.wg_location.value)
        else:
            self.parentApp.application_logic.create_box(box_uuid=self.wg_uuid.value,
                                                        description=self.wg_description.value or None,
                                                        location=self.wg_location.value or None)
        self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

# BoxList

class BoxList(npyscreen.MultiLineAction):

    def __init__(self, *args, **kwargs):
        super(BoxList, self).__init__(*args,
                                       **kwargs)
        self.add_handlers({
            "^N": self.when_add_box,
            "^D": self.when_delete_box,
            "^T": self.switch_view,
        })


    def when_add_box(self, *args, **kwargs):
        self.parent.parentApp.getForm("POPUPBOX").value = None
        self.parent.parentApp.switchForm("POPUPBOX")

    def when_delete_box(self, *args, **kwargs):
        delete_confirmation = npyscreen.notify_ok_cancel(message="You're about to delete this box. There's NO UNDO. "
                                                               "Are you sure?",
                                                         title="WARNING")

        if delete_confirmation is True:
            self.parent.parentApp.application_logic.delete_box_by_uuid(self.values[self.cursor_line][0])
            self.parent.update_list()

    def switch_view(self, *args, **kwargs):
        self.parent.parentApp.switchForm("MAIN")

    def actionHighlighted(self, act_on_this, keypress):
        self.parent.parentApp.getForm("POPUPBOX").value=act_on_this[0]
        self.parent.parentApp.switchForm("POPUPBOX")

    def display_value(self, vl):
        return("%s: %s" % (vl[0], vl[1]))

class BoxListDisplay(npyscreen.FormMuttActive):
    MAIN_WIDGET_CLASS = BoxList
    MAIN_WIDGET_NAME = "Box list"
    MAIN_WIDGET_CLASS_START_LINE = 1
    COMMAND_WIDGET_CLASS = npyscreen.FixedText

    def beforeEditing(self):
        self.update_list()

    def update_list(self):

        self.wMain.values = self.parentApp.application_logic.query_boxes()

        if type(self.wMain.values) is NoneType:
            table_size = 0
        else:
            table_size = len(self.wMain.values)

        self.wStatus1.value = "BOX ENTRY PANEL \t \t Registering %s boxes in total." % table_size
        self.wStatus2.value = "Press ^N to create a new box. Press ^T to switch to item management."
        self.wCommand.value = "To search and filter, press 'l'."
        self.wMain.display()




