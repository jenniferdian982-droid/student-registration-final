from ._anvil_designer import MainTemplate
from anvil import *
import anvil.server
import anvil.users

MAROON = "#800000"
DARK_GREEN = "#1F6F3F"
YELLOW = "#F5C518"
CREAM = "#FFFBEA"
CARD_BORDER = "1px solid #E3C35A"
INPUT_BORDER = "1px solid #1F6F3F"

OK_COLOR = "#14532D"      # dark green  - success
ERROR_COLOR = "#800000"   # maroon      - errors / rejected actions
INFO_COLOR = "#6B4E00"    # dark gold   - neutral information


class Main(MainTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.apply_theme()
        self.role = None
        self.records_loaded = False
        self.records_panel.items = []
        self.show_logged_out("Please log in to continue.")

    # ------------------------------------------------------------------
    # Colour theme (yellow / green / maroon), applied in code so it always shows
    # ------------------------------------------------------------------
    def _style(self, comp, **props):
        for key, value in props.items():
            try:
                setattr(comp, key, value)
            except Exception:
                pass

    def apply_theme(self):
        self._style(self, background=CREAM)

        # Header banner
        self._style(self.header_panel, background=MAROON)
        self._style(self.title_label, foreground=YELLOW, bold=True, font_size=24)
        self._style(self.subtitle_label, foreground="#F3E3B0", italic=True, font_size=13)
        self._style(self.user_label, foreground="#FFFFFF", bold=True)
        for b in (self.login_button, self.logout_button):
            self._style(b, background=YELLOW, foreground=MAROON, bold=True)

        # Status bar
        self._style(self.status_label, background="#FFF1B8", bold=True,
                    border="1px solid " + YELLOW)

        # Cards and section bars
        self._style(self.app_panel, background=CREAM)
        for card in (self.register_card, self.records_card, self.delete_card):
            self._style(card, background="#FFFFFF", border=CARD_BORDER)
        for bar in (self.reg_heading, self.rec_heading, self.del_heading):
            self._style(bar, background=DARK_GREEN, foreground="#FFFFFF",
                        bold=True, font_size=16)

        # Field captions and inputs
        for cap in (self.student_id_box_caption, self.name_box_caption,
                    self.course_dropdown_caption, self.year_dropdown_caption,
                    self.delete_id_caption):
            self._style(cap, foreground=MAROON, bold=True)
        for box in (self.student_id_box, self.name_box, self.delete_id_box,
                    self.course_dropdown, self.year_dropdown):
            self._style(box, background="#FFFFFF", border=INPUT_BORDER)

        # Buttons
        self._style(self.register_button, background=DARK_GREEN,
                    foreground="#FFFFFF", bold=True)
        self._style(self.view_button, background=YELLOW,
                    foreground=MAROON, bold=True)
        self._style(self.delete_button, background=MAROON,
                    foreground="#FFFFFF", bold=True)
        self._style(self.delete_hint, foreground="#666666", italic=True)
        self._style(self.records_area, border=CARD_BORDER)

    # ------------------------------------------------------------------
    # Status helper (colour shows success / error / info)
    # ------------------------------------------------------------------
    def set_status(self, message, kind="info"):
        self.status_label.text = message
        self.status_label.foreground = {
            "ok": OK_COLOR, "error": ERROR_COLOR}.get(kind, INFO_COLOR)

    # ------------------------------------------------------------------
    # Login / logout
    # ------------------------------------------------------------------
    def form_show(self, **event_args):
        if anvil.users.get_user() is None:
            self.do_login()
        else:
            self.show_logged_in()

    def login_button_click(self, **event_args):
        self.do_login()

    def do_login(self):
        try:
            user = anvil.users.login_with_form(allow_cancel=True)
            if user is None:
                self.show_logged_out("Login is required to use this application.")
            else:
                self.show_logged_in()
        except Exception as e:
            self.show_logged_out(str(e))

    def show_logged_in(self):
        try:
            # The server decides the role; the client only displays it.
            anvil.server.call("ensure_default_role")
            self.role = anvil.server.call("get_my_role")
            user = anvil.users.get_user()
            self.user_label.text = "Logged in as {} ({})".format(user["email"], self.role)
        except Exception:
            self.user_label.text = "Logged in"
        self.app_panel.visible = True
        self.login_button.visible = False
        self.logout_button.visible = True
        self.set_status("Welcome! You may register students and view records.", "ok")

    def show_logged_out(self, message):
        self.role = None
        self.records_loaded = False
        self.records_panel.items = []
        self.app_panel.visible = False
        self.login_button.visible = True
        self.logout_button.visible = False
        self.user_label.text = "Not logged in"
        self.set_status(message, "info")

    def logout_button_click(self, **event_args):
        anvil.users.logout()
        self.student_id_box.text = ""
        self.name_box.text = ""
        self.delete_id_box.text = ""
        self.course_dropdown.selected_value = None
        self.year_dropdown.selected_value = None
        self.show_logged_out("You have been logged out. Please log in to continue.")

    # ------------------------------------------------------------------
    # Register
    # ------------------------------------------------------------------
    def register_button_click(self, **event_args):
        try:
            result = anvil.server.call(
                "register_student",
                self.student_id_box.text,
                self.name_box.text,
                self.course_dropdown.selected_value,
                self.year_dropdown.selected_value
            )
            self.student_id_box.text = ""
            self.name_box.text = ""
            self.course_dropdown.selected_value = None
            self.year_dropdown.selected_value = None
            self.load_records(show_message=False)
            self.set_status(result, "ok")
        except Exception as e:
            self.set_status(str(e), "error")

    # ------------------------------------------------------------------
    # View
    # ------------------------------------------------------------------
    def view_button_click(self, **event_args):
        self.load_records(show_message=True)

    def load_records(self, show_message=True):
        try:
            user = anvil.users.get_user()
            if user is None:
                self.set_status("Please log in first.", "error")
                return

            # Display choice only. The SERVER enforces who may see what.
            role = anvil.server.call("get_my_role")
            if role == "Admin":
                records = anvil.server.call("get_all_registrations")
            else:
                records = anvil.server.call("get_my_registrations")

            self.records_panel.items = records
            self.records_loaded = True
            if show_message:
                self.set_status("Loaded {} registration(s).".format(len(records)), "ok")
        except Exception as e:
            self.set_status(str(e), "error")

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete_button_click(self, **event_args):
        try:
            result = anvil.server.call(
                "delete_registration",
                self.delete_id_box.text
            )
            self.delete_id_box.text = ""
            self.load_records(show_message=False)
            self.set_status(result, "ok")
        except Exception as e:
            self.set_status(str(e), "error")
