import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2

class SimpleBrowser(Gtk.Window):
    def __init__(self):
        super(SimpleBrowser, self).__init__()

        self.set_title("Reptile")
        self.set_default_size(1200, 800)

        # Create a vertical box to hold the WebView and the loading bar
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.vbox)

        # Create a WebView widget
        self.webview = WebKit2.WebView()
        self.homepage_url = "https://juanvel4000.serv00.net/reptile/"  # Set homepage URL
        self.webview.load_uri(self.homepage_url)  # Default home page
        self.vbox.pack_start(self.webview, True, True, 0)

        # Create a Navigation Bar
        self.navigation_bar = Gtk.HeaderBar(title="Reptile")
        self.navigation_bar.set_show_close_button(True)
        self.set_titlebar(self.navigation_bar)

        # Create Navigation Buttons with Icons
        back_button = Gtk.Button.new_from_icon_name("go-previous", Gtk.IconSize.BUTTON)
        back_button.connect("clicked", self.on_back_clicked)
        self.navigation_bar.pack_start(back_button)

        forward_button = Gtk.Button.new_from_icon_name("go-next", Gtk.IconSize.BUTTON)
        forward_button.connect("clicked", self.on_forward_clicked)
        self.navigation_bar.pack_start(forward_button)

        reload_button = Gtk.Button.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON)
        reload_button.connect("clicked", self.on_reload_clicked)
        self.navigation_bar.pack_start(reload_button)

        home_button = Gtk.Button.new_from_icon_name("home", Gtk.IconSize.BUTTON)
        home_button.connect("clicked", self.on_home_clicked)
        self.navigation_bar.pack_start(home_button)

        # URL entry
        self.url_entry = Gtk.Entry()
        self.url_entry.connect("activate", self.on_url_activate)
        self.navigation_bar.pack_end(self.url_entry)

        # Hamburger menu button
        menu_button = Gtk.Button(label="☰")  # Use a hamburger icon
        menu_button.connect("clicked", self.on_menu_button_clicked)
        self.navigation_bar.pack_end(menu_button)

        # Create the menu
        self.menu = Gtk.Menu()

        # Help menu item
        help_item = Gtk.MenuItem(label="Help")
        help_item.connect("activate", self.on_help_clicked)
        self.menu.append(help_item)

        # Exit menu item
        exit_item = Gtk.MenuItem(label="Exit")
        exit_item.connect("activate", Gtk.main_quit)
        self.menu.append(exit_item)

        self.menu.show_all()  # Show the menu items

        # Progress bar at the bottom
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Loading...")
        self.vbox.pack_start(self.progress_bar, False, False, 0)

        # Update URL entry and window title when the page changes
        self.webview.connect("load_changed", self.on_load_changed)

        # Connect the title-changed event to update window title
        self.webview.connect("notify::title", self.on_title_changed)

        # Show all widgets
        self.show_all()

    def on_load_changed(self, webview, load_event):
        if load_event == WebKit2.LoadEvent.COMMITTED:
            # Get the current URI
            current_uri = webview.get_uri()
            if current_uri == self.homepage_url:
                # Change displayed URL to reptile://homepage if it matches the homepage URL
                self.url_entry.set_text("reptile://homepage")
            else:
                # Update URL entry with the current URI
                self.url_entry.set_text(current_uri)
            self.progress_bar.set_fraction(0.0)  # Reset the progress bar
            self.progress_bar.show()  # Show progress bar

        elif load_event == WebKit2.LoadEvent.FINISHED:
            self.progress_bar.set_fraction(1.0)  # Full progress
            self.progress_bar.set_text("Loaded")  # Update text
            self.progress_bar.hide()  # Hide the progress bar after loading is complete

        elif load_event == WebKit2.LoadEvent.STARTED:
            self.progress_bar.set_text("Loading...")  # Update text to "Loading..."
            self.progress_bar.show()  # Show the progress bar when loading starts

    def on_title_changed(self, webview, param):
        # Get the current title and set the window title as "(Page Name) - Reptile"
        title = webview.get_title() if webview.get_title() else "Reptile"
        self.set_title(f"{title} - Reptile")

    def on_help_clicked(self, menu_item):
        # Display a message dialog when Help is clicked
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "About Reptile")
        dialog.format_secondary_text(
            "Reptile Web Browser Version 0.1.\n Developed by nBudjer Project"
        )
        dialog.run()
        dialog.destroy()

    def on_menu_button_clicked(self, button):
        # Show the menu below the button
        self.menu.popup(None, None, None, button, 0, Gtk.get_current_event_time())

    def on_back_clicked(self, button):
        if self.webview.can_go_back():
            self.webview.go_back()

    def on_forward_clicked(self, button):
        if self.webview.can_go_forward():
            self.webview.go_forward()

    def on_reload_clicked(self, button):
        self.webview.reload()

    def on_home_clicked(self, button):
        self.webview.load_uri(self.homepage_url)  # Load your desired homepage here

    def on_url_activate(self, entry):
        uri = entry.get_text()
        if uri == "reptile://homepage":
            self.webview.load_uri(self.homepage_url)  # Load the actual homepage
        elif not (uri.startswith("http://") or uri.startswith("https://")):
            uri = "http://" + uri  # Prepend "http://" if no scheme is provided
        self.webview.load_uri(uri)

if __name__ == "__main__":
    win = SimpleBrowser()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
