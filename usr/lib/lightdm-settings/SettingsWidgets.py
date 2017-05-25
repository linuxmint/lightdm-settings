#!/usr/bin/python3

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk, GLib, GdkPixbuf

CONF_PATH = "/etc/lightdm/slick-greeter.conf"
GROUP_NAME = "Greeter"

LIGHTDM_CONF_PATH = "/etc/lightdm/lightdm.conf"
LIGHTDM_GROUP_NAME = "Seat:*"

def list_header_func(row, before, user_data):
    if before and not row.get_header():
        row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

class SettingsPage(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(15)
        self.set_margin_left(80)
        self.set_margin_right(80)
        self.set_margin_top(15)
        self.set_margin_bottom(15)

    def add_section(self, title):
        section = SettingsBox(title)
        self.pack_start(section, False, False, 0)

        return section

class SettingsBox(Gtk.Frame):

    def __init__(self, title):
        Gtk.Frame.__init__(self)
        self.set_shadow_type(Gtk.ShadowType.IN)
        frame_style = self.get_style_context()
        frame_style.add_class("view")
        self.size_group = Gtk.SizeGroup()
        self.size_group.set_mode(Gtk.SizeGroupMode.VERTICAL)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        toolbar = Gtk.Toolbar.new()
        toolbar_context = toolbar.get_style_context()
        Gtk.StyleContext.add_class(Gtk.Widget.get_style_context(toolbar), "cs-header")

        label = Gtk.Label.new()
        label.set_markup("<b>%s</b>" % title)
        title_holder = Gtk.ToolItem()
        title_holder.add(label)
        toolbar.add(title_holder)
        self.box.add(toolbar)

        toolbar_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.box.add(toolbar_separator)
        separator_context = toolbar_separator.get_style_context()
        frame_color = frame_style.get_border_color(Gtk.StateFlags.NORMAL).to_string()
        # css_provider = Gtk.CssProvider()
        # css_provider.load_from_data(".separator { -GtkWidget-wide-separators: 0; \
        #                                            color: %s;                    \
        #                                         }" % frame_color)
        # separator_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.set_header_func(list_header_func, None)
        self.box.add(self.list_box)

    def add_row(self, row):
        self.list_box.add(row)


class SettingsRow(Gtk.ListBoxRow):

    def __init__(self, label, main_widget, alternative_widget=None):

        self.main_widget = main_widget
        self.alternative_widget = alternative_widget
        self.label = label
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)

        self.stack.add_named(main_widget, "main_widget")
        if alternative_widget is not None:
            self.stack.add_named(self.alternative_widget, "alternative_widget")

        Gtk.ListBoxRow.__init__(self)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_border_width(5)
        hbox.set_margin_left(20)
        hbox.set_margin_right(20)
        self.add(hbox)

        grid = Gtk.Grid()
        grid.set_column_spacing(15)
        hbox.pack_start(grid, True, True, 0)

        self.description_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.description_box.props.hexpand = True
        self.description_box.props.halign = Gtk.Align.START
        self.description_box.props.valign = Gtk.Align.CENTER
        self.label.props.xalign = 0.0
        self.description_box.add(self.label)

        grid.attach(self.description_box, 0, 0, 1, 1)
        grid.attach_next_to(self.stack, self.description_box, Gtk.PositionType.RIGHT, 1, 1)

    def show_alternative_widget(self):
        if self.alternative_widget is not None:
            self.stack.set_visible_child(self.alternative_widget)

class SettingsSwitch(Gtk.Switch):
    def __init__(self, keyfile, settings, key):
        self.key = key
        self.keyfile = keyfile
        try:
            self.value = keyfile.get_boolean(GROUP_NAME, key)
        except:
            self.value = settings.get_boolean(key)
        Gtk.Switch.__init__(self)
        self.set_active(self.value)
        self.connect("notify::active", self.on_toggled)

    def on_toggled(self, widget, data=None):
        self.keyfile.set_boolean(GROUP_NAME, self.key, self.get_active())
        self.keyfile.save_to_file(CONF_PATH)

class SettingsPictureChooser(Gtk.Box):
    def __init__(self, keyfile, settings, key):
        Gtk.Box.__init__(self)
        self.get_style_context().add_class("linked")
        self.key = key
        self.keyfile = keyfile
        try:
            self.value = keyfile.get_string(GROUP_NAME, key)
        except:
            self.value = settings.get_string(key)

        self.bind_object = Gtk.Entry()
        self.image_button = Gtk.Button()

        self.preview = Gtk.Image.new()
        layout = self.image_button.create_pango_layout ("Black");
        ink, logical = layout.get_pixel_extents ();

        self.height = logical.height

        self.preview.set_size_request (logical.width, logical.height);
        self.image_button.add(self.preview)

        self.pack_start(self.bind_object, True, True, 0)
        self.pack_start(self.image_button, True, True, 0)

        self.image_button.connect("clicked", self.on_button_pressed)
        self.handler = self.bind_object.connect("changed", self.set_icon)

        self.bind_object.set_text(self.value)
        self.set_icon()

    def set_icon(self, *args):
        val = self.bind_object.get_text()

        if os.path.exists(val) and not os.path.isdir(val):
            img = GdkPixbuf.Pixbuf.new_from_file_at_size(val, -1, self.height)
            self.preview.set_from_pixbuf(img)

            if val == self.value:
                return

            self.value = val
            self.keyfile.set_string(GROUP_NAME, self.key, val)
            self.keyfile.save_to_file(CONF_PATH)
        else:
            self.preview.set_from_icon_name("document-open", Gtk.IconSize.BUTTON)

            if val == self.value:
                return

            self.keyfile.set_string(GROUP_NAME, self.key, "")
            self.keyfile.save_to_file(CONF_PATH)

    def on_button_pressed(self, widget):
        dialog = Gtk.FileChooserDialog(title=_("Choose an Image File"),
                                       action=Gtk.FileChooserAction.OPEN,
                                       transient_for=self.get_toplevel(),
                                       buttons=(_("_Cancel"), Gtk.ResponseType.CANCEL,
                                                _("_Open"), Gtk.ResponseType.OK))

        filter_text = Gtk.FileFilter()
        filter_text.set_name(_("Image files"))
        filter_text.add_mime_type("image/*")
        dialog.add_filter(filter_text)

        backgrounds = "/usr/share/backgrounds"

        if os.path.exists(self.value):
            dialog.set_filename(self.value)

        if os.path.exists(backgrounds):
            dialog.add_shortcut_folder(backgrounds)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.frame = Gtk.Frame(visible=False, no_show_all=True)
        preview = Gtk.Image(visible=True)

        box.pack_start(self.frame, False, False, 0)
        self.frame.add(preview)
        dialog.set_preview_widget(box)
        dialog.set_preview_widget_active(True)
        dialog.set_use_preview_label(False)

        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_size_request(320, -1)

        dialog.connect("update-preview", self.update_icon_preview_cb, preview)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.bind_object.set_text(filename)

        dialog.destroy()

    def update_icon_preview_cb(self, dialog, preview):
        # Different widths make the dialog look really crappy as it resizes -
        # constrain the width and adjust the height to keep perspective.
        filename = dialog.get_preview_filename()
        if filename is not None:
            if os.path.isfile(filename):
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 320, -1)
                    if pixbuf is not None:
                        preview.set_from_pixbuf(pixbuf)
                        self.frame.show()
                        return
                except GLib.Error as e:
                    print("Unable to generate preview for file '%s' - %s\n", filename, e.message)

        preview.clear()
        self.frame.hide()

class SettingsColorChooser(Gtk.ColorButton):
    def __init__(self, keyfile, settings, key):
        self.key = key
        self.keyfile = keyfile
        try:
            self.value = keyfile.get_string(GROUP_NAME, key)
        except:
            self.value = settings.get_string(key)
        Gtk.ColorButton.__init__(self)
        rgba = Gdk.RGBA()
        rgba.parse(self.value)
        self.set_rgba(rgba)
        self.connect("color-set", self.on_color_set)

    def on_color_set(self, widget):
        self.keyfile.set_string(GROUP_NAME, self.key, self.get_hex_code())
        self.keyfile.save_to_file(CONF_PATH)

    def get_hex_code(self):
            color = self.get_rgba()
            #code = "#"
            code = ""
            for i in (color.red, color.green, color.blue):
                i = hex(int(i*255.0))[2:]
                if len(i) == 1:
                    code = code + "0" + i
                else:
                    code = code + i
            return code

class SettingsCombo(Gtk.ComboBox):
    def __init__(self, keyfile, settings, key, options, valtype="string"):
        self.key = key
        self.keyfile = keyfile
        try:
            self.value = keyfile.get_string(GROUP_NAME, key)
        except:
            self.value = settings.get_string(key)
        Gtk.ComboBox.__init__(self)
        renderer_text = Gtk.CellRendererText()
        self.pack_start(renderer_text, True)
        self.add_attribute(renderer_text, "text", 1)
        self.set_valign(Gtk.Align.CENTER)

        # assume all keys are the same type (mixing types is going to cause an error somewhere)
        var_type = type(options[0][0])
        self.model = Gtk.ListStore(var_type, str)
        self.valtype = valtype
        self.option_map = {}
        for option in options:
            self.option_map[option[0]] = self.model.append([option[0], option[1]])

        self.set_model(self.model)
        self.set_id_column(0)

        if self.value in self.option_map.keys():
            self.set_active_iter(self.option_map[self.value])

        self.connect("changed", self.on_changed)

    def on_changed(self, widget):
        tree_iter = widget.get_active_iter()
        if tree_iter != None:
            value = self.model[tree_iter][0]
            self.keyfile.set_string(GROUP_NAME, self.key, value)
            self.keyfile.save_to_file(CONF_PATH)

class LightDMSwitch(Gtk.Switch):
    def __init__(self, keyfile, key, value):
        self.key = key
        self.keyfile = keyfile
        Gtk.Switch.__init__(self)
        self.set_active(value)
        self.connect("notify::active", self.on_toggled)

    def on_toggled(self, widget, data=None):
        self.keyfile.set_boolean(LIGHTDM_GROUP_NAME, self.key, self.get_active())
        self.keyfile.save_to_file(LIGHTDM_CONF_PATH)
