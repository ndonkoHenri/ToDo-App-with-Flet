import time
import flet
from flet import (Page, Text, Row, TextField, ElevatedButton, Column, Checkbox, Ref, IconButton, FloatingActionButton,
                  icons, UserControl, Tabs, Tab, Divider, Theme, SnackBar, AlertDialog, TextButton, colors,
                  ProgressBar, )
from flet.control_event import ControlEvent


# import logging
# logging.basicConfig(level=logging.DEBUG)


class ToDO(UserControl):

    def __init__(self):
        super().__init__()
        self.main_container = None
        self.tasks_view = None
        self.text_field = None
        self.tabs = None
        self.delete_dialog = AlertDialog(
            modal=True,
            title=Text("Please confirm"),
            content=Text("Do you really want to delete this item?"),
            actions=[
                TextButton("Yes", on_click=self.delete_confirmed),
                TextButton("No", on_click=self.close_dialog),
            ],
            actions_alignment="end",
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        # the item which caused the opening of the delete-dialog box
        self._actual_deleted_item = None

    def close_dialog(self, e):
        """when the 'No' button of the delete-dialog is triggered, the dialog is just closed"""
        self.delete_dialog.open = False
        e.page.update()

    def delete_confirmed(self, e):
        """
        when the 'Yes' button of the delete-dialog is triggered,
        the item is deleted and the delete-dialog is closed
        """
        self.delete_item_callback(self._actual_deleted_item)
        self.delete_dialog.open = False
        e.page.update()
        e.page.show_snack_bar(
            SnackBar(
                Text("Deleted Item successfully!"),
                action="OK!",
                open=True
            )
        )

    def open_delete_dialog(self, item):
        """opens the delete-dialog, and keeps a reference to the item which triggered it(self._actual_deleted_item)"""
        item.page.dialog = self.delete_dialog
        item.page.dialog.open = True
        self._actual_deleted_item = item
        item.page.update()

    def update(self):
        """
        The update function is called when the user changes tabs.
        It hides or shows the to-do items depending on which tab is selected.
        """
        # index 0 refers to 'all' tab, index 1 refers to 'not yet done' tab, index 2 refers to 'done' tab,
        index = self.tabs.current.selected_index

        # Looping through the list of controls in the tasks_view, and then setting the visibility of each control
        # to True or False depending on the selected tab(precisely, it's index).
        for todo_item_control in self.tasks_view.current.controls:
            if index == 1:
                # show tasks that have not yet been done
                todo_item_control.visible = not todo_item_control.item_checkbox.current.value
            elif index == 2:
                # show tasks that have already been done
                todo_item_control.visible = todo_item_control.item_checkbox.current.value
            else:
                # show all tasks
                todo_item_control.visible = True
        super().update()

    def delete_item_callback(self, item):
        """
        It removes the item from the list of controls in the current view, and then updates the view

        :param item: The to-do item to be deleted
        """
        self.tasks_view.current.controls.remove(item)
        self.update()

    def submit_item(self, e: ControlEvent):
        """
        It creates a new TodoItem object, adds it to the list of controls in the tasks_view(below the tabs),
        and then clears the text field

        :param e: The event object (ControlEvent)
        """
        if self.text_field.current.value:
            item = TodoItem(self.text_field.current.value, self.update, self.open_delete_dialog)
            self.tasks_view.current.controls.append(item)
            self.text_field.current.value = ""
            self.text_field.current.counter_text = '0 chars'
            self.page.show_snack_bar(
                SnackBar(
                    Text("Added New To-Do Item"),
                    action="OK!",
                    open=True
                )
            )
            self.update()

    def tabs_change(self, e):
        """
        It updates the UI when the user changes tabs

        :param e: The event object (ControlEvent)
        """
        self.update()

    def counter_text_change(self, e: ControlEvent):
        """
        It updates the counter text of the text field.

        :param e: The event object (ControlEvent)
        """
        self.text_field.current.counter_text = f'{len(e.data)} chars'
        self.text_field.current.update()

    def build(self):
        """
        It builds the UI with a maximum width of 600px.
        :return: A Column widget with a Row widget and a Tabs widget as its children.
        """
        self.text_field = Ref[TextField]()
        self.tasks_view = Ref[Column]()
        self.main_container = Ref[Column]()
        self.tabs = Ref[Tabs]()

        return Column(ref=self.main_container,
                      controls=[
                          Row(
                              controls=[
                                  TextField(
                                      ref=self.text_field,
                                      helper_text="What do you plan to do?",
                                      hint_text="ex: learn flutter..",
                                      counter_text='0 chars',
                                      keyboard_type="text",
                                      label="New Item",
                                      expand=True,
                                      text_size=20,
                                      tooltip="Field for new items",
                                      prefix_icon=icons.LIST_ALT_ROUNDED,
                                      autofocus=True,
                                      on_change=self.counter_text_change,
                                      on_submit=self.submit_item
                                  ),
                                  FloatingActionButton(
                                      icon=icons.ADD,
                                      tooltip="add item",
                                      on_click=self.submit_item
                                  )
                              ]
                          ),
                          Tabs(
                              ref=self.tabs,
                              tabs=[
                                  Tab(text='all', icon=icons.CHECKLIST_OUTLINED),
                                  Tab(text='not yet done', icon=icons.CHECK),
                                  Tab(text='done', icon=icons.DONE_ALL)
                              ],
                              selected_index=0,
                              on_change=self.tabs_change
                          ),
                          Column(
                              ref=self.tasks_view,
                              scroll="always"
                          )
                      ],
                      spacing=24,
                      width=630
                      )


class TodoItem(UserControl):
    def __init__(self, item_text, checkbox_change, delete_dialog_callback):
        """
        The function takes in three arguments: item_text, checkbox_change, and delete_callback. It then calls the
        super() function, which is a special function that allows you to call a method from the parent class.

        :param item_text: The text that will be displayed in the item
        :param checkbox_change: This is a callback function that will be called when the value of checkbox changes
        :param delete_dialog_callback: This is a function that will be called when the delete button of an item is pressed
        """
        super().__init__()
        self.item_text = item_text
        self.open_delete_dialog = delete_dialog_callback
        self.checkbox_change = checkbox_change
        self.normal_view = Ref[Row]()
        self.edit_view = Ref[Row]()
        self.item_checkbox = Ref[Checkbox]()
        self.text_field = Ref[TextField]()

    def save_edit(self, e):
        """
        It makes the normal_view visible, the edit_view invisible and sets the
        label of the checkbox to the value from the text field in the edit_view

        :param e: The event that triggered the function (ControlEvent)
        """
        self.normal_view.current.visible = True
        self.edit_view.current.visible = False
        self.text_field.current.autofocus = False
        self.item_checkbox.current.label = self.text_field.current.value
        # It updates the UI.
        self.update()
        e.page.show_snack_bar(
            SnackBar(
                Text("Updated Item successfully!"),
                action="OK!",
                open=True
            )
        )

    def edit_item(self, e):
        """
        Changes the view to an editable view. By setting the normal_view to invisible, and the edit_view to visible.

        :param e: The event that triggered this function (ControlEvent)
        """
        self.normal_view.current.visible = False
        self.edit_view.current.visible = True
        self.text_field.current.autofocus = True
        self.update()

    def delete_item(self, e):
        """
        It calls the delete_callback function which will delete/remove this item from the to-do listbox(tasks_view)

        :param e: The event that triggered the callback (ControlEvent)
        """
        self.open_delete_dialog(self)

    def item_checkbox_value_change(self, e):
        """
        Listens to changes on the value(bool) of our checkbox.
        For any change, we update the UI to correctly show the Item in the corresponding tab.

        :param e: The event object (ControlEvent)
        """
        self.checkbox_change()

    def build(self):
        """
        Building up of the UI for a To-Do Item.

                            Row(Checkbox and a Row with two IconButtons)
        :return: Column --<
                            Row (Textfield and an Update button)
        """
        return Column(
            controls=[
                Row(
                    ref=self.normal_view,
                    controls=[
                        Checkbox(
                            ref=self.item_checkbox,
                            label=self.item_text,
                            value=False,
                            on_change=self.item_checkbox_value_change),
                        Row(
                            controls=[
                                IconButton(
                                    icon=icons.EDIT,
                                    icon_color=colors.LIGHT_GREEN_ACCENT_700,
                                    on_click=self.edit_item,
                                    tooltip="update item",
                                ),
                                IconButton(
                                    icon=icons.DELETE_FOREVER,
                                    icon_color=colors.RED_900,
                                    tooltip="delete item",
                                    on_click=self.delete_item,
                                ),
                            ]
                        )
                    ],
                    alignment="spaceBetween"
                ),
                Row(
                    ref=self.edit_view,
                    visible=False,
                    controls=[
                        TextField(
                            ref=self.text_field,
                            value=self.item_text,
                            tooltip="field to edit the item",
                            autofocus=False,
                            label="Edit Item",
                            expand=True,
                            on_submit=self.save_edit,
                            suffix=ElevatedButton(text="Update", on_click=self.save_edit))
                    ],
                )
            ],
        )


def main(page: Page):
    """
    The entry/main Page of the APP

    :param page: Page: The page object that is passed to the main function
    :type page: Page
    """

    # set a custom title for the page
    page.title = "myToDo App"

    # make the window always on top of other windows.
    # page.window_always_on_top = True

    # set the width and height of the window.
    page.window_width = 562
    page.window_height = 720

    # set the horizontal alignment of the page to center(in the horizontal middle).
    page.horizontal_alignment = "center"

    # set the vertical alignment of the page to start, similar to the top of the page.
    page.vertical_alignment = "start"

    # add a custom font found in the assets/fonts file
    page.fonts = {"SF-simple": "/fonts/San-Francisco/SFUIDisplay-Light.ttf",
                  "SF-bold": "/fonts/San-Francisco/SFUIDisplay-Bold.ttf"}

    page.theme_mode = "light"
    page.theme = Theme(
        font_family="SF-simple",
        use_material3=True,
        visual_density="compact",
    )

    page.splash = ProgressBar(bar_height=3.5, visible=False)

    def change_bg_theme(e):
        """
        Changes the theme of the application from a Light to Dark theme or the reverse.

        :param e: The event that triggered the callback (ControlEvent)
        """
        page.splash.visible = True
        page.update()
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        page.splash.visible = False
        theme_icon_button.selected = not theme_icon_button.selected
        time.sleep(1.2)
        page.update()

    todo = ToDO()

    theme_icon_button = IconButton(
        icons.DARK_MODE,
        selected_icon=icons.LIGHT_MODE,
        selected=False,
        on_click=change_bg_theme, icon_size=40
    )

    page.add(
        Row(
            controls=[
                Text(
                    value="myToDo App",
                    text_align="center",
                    selectable=False,
                    font_family="SF-bold",
                    weight="bold",
                    size=40
                ),
                theme_icon_button
            ],
            alignment="spaceAround",
        ),
        Divider(),
        todo,
        Text(
            "Made by TheEthicalBoy",
            italic=True, color="blue",
            text_align="end",
            expand=True,
        )
    )


# running the app
flet.app(target=main, view=flet.WEB_BROWSER, assets_dir="assets")
