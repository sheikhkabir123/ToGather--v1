# frontend/main.py
import kivy
kivy.require("2.3.0")



from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock

from api import BASE_URL, login, register, me, get_token, set_token, clear_session, \
                events_feed, attending_events, my_events, create_event

from api import BASE_URL, login, register, me, get_token, set_token, clear_session, update_location, get_buddies_locations


KV = f"""
#:import dp kivy.metrics.dp
#:import FadeTransition kivy.uix.screenmanager.FadeTransition


<Notice@Label>:
    color: 1,1,1,1
    font_size: dp(14)
    size_hint_y: None
    height: self.texture_size[1] + dp(8)
    text_size: self.width, None
    halign: "center"

<TextBox@TextInput>:
    size_hint_y: None
    height: dp(44)
    padding: dp(10), dp(12)
    multiline: False
    write_tab: False

<PrimaryButton@Button>:
    size_hint_y: None
    height: dp(48)
    font_size: dp(16)

<SmallLink@Button>:
    background_normal: ""
    background_color: 0,0,0,0
    color: .7,.7,1,1
    size_hint_y: None
    height: dp(34)

<LoginScreen>:
    name: "login"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(12)
        canvas.before:
            Color: 
                rgba: .06,.06,.06,1
            Rectangle:
                pos: self.pos
                size: self.size

        Widget:  # spacer
            size_hint_y: None
            height: dp(40)

        Label:
            text: "ToGather — Login"
            color: 1,1,1,1
            font_size: dp(22)
            size_hint_y: None
            height: self.texture_size[1] + dp(12)

        Notice:
            text: "BASE_URL: {BASE_URL}"
            color: .8,.8,.8,1

        TextBox:
            id: user_in
            hint_text: "Username"
        TextBox:
            id: pass_in
            hint_text: "Password"
            password: True

        PrimaryButton:
            text: "Login"
            on_release: root.do_login(user_in.text.strip(), pass_in.text)

        Notice:
            id: msg
            text: root.message
            color: 1,.6,.6,1

        Widget:
            size_hint_y: None
            height: dp(10)

        SmallLink:
            text: "No account? Register"
            on_release: app.sm.current = "register"

        Widget:
            size_hint_y: 1

<RegisterScreen>:
    name: "register"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(12)
        canvas.before:
            Color: 
                rgba: .06,.06,.06,1
            Rectangle:
                pos: self.pos
                size: self.size

        Widget:
            size_hint_y: None
            height: dp(40)

        Label:
            text: "ToGather — Register"
            color: 1,1,1,1
            font_size: dp(22)
            size_hint_y: None
            height: self.texture_size[1] + dp(12)

        Notice:
            text: "BASE_URL: {BASE_URL}"
            color: .8,.8,.8,1

        TextBox:
            id: user_in
            hint_text: "Username"
        TextBox:
            id: email_in
            hint_text: "Email"
        TextBox:
            id: pass_in
            hint_text: "Password"
            password: True
        TextBox:
            id: pass2_in
            hint_text: "Confirm Password"
            password: True

        PrimaryButton:
            text: "Create Account"
            on_release: root.do_register(user_in.text.strip(), email_in.text.strip(), pass_in.text, pass2_in.text)
            

        Notice:
            id: msg
            text: root.message
            color: 1,.6,.6,1

        Widget:
            size_hint_y: None
            height: dp(10)

        SmallLink:
            text: "Have an account? Login"
            on_release: app.sm.current = "login"

        Widget:
            size_hint_y: 1

<HomeScreen>:
    name: "home"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(12)
        canvas.before:
            Color: 
                rgba: .06,.06,.06,1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "ToGather — Home"
            color: 1,1,1,1
            font_size: dp(22)
            size_hint_y: None
            height: self.texture_size[1] + dp(10)

        Notice:
            id: hello
            text: root.header_text
            color: .8,.9,1,1

        PrimaryButton:
            text: "Events Feed"
            on_release: app.sm.current = "events"

        PrimaryButton:
            text: "Create Event"
            on_release: app.sm.current = "create_event"

        PrimaryButton:
            text: "Refresh /auth/me"
            on_release: root.refresh_me()

        PrimaryButton:
            text: "Logout"
            on_release: root.do_logout()


        PrimaryButton:
            text: "Send my location"
            on_release: app.sm.current = "loc"

        PrimaryButton:
            text: "See buddies' locations"
            on_release: app.sm.current = "buddies"

        PrimaryButton:
            text: "Buddy Locations"
            on_release: app.sm.current = "buddies"



        Widget:

<EventsScreen>:
    name: "events"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: .06,.06,.06,1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(10)
            Label:
                text: "Events — Feed"
                color: 1,1,1,1
                font_size: dp(18)
            Button:
                size_hint_x: None
                width: dp(90)
                text: "Back"
                on_release: app.sm.current = "home"

        Notice:
            id: msg
            text: root.message
            color: .9,.7,.7,1

        ScrollView:
            GridLayout:
                id: listbox
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                padding: 0, dp(4)

<CreateEventScreen>:
    name: "create_event"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: .06,.06,.06,1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(10)
            Label:
                text: "Create Event"
                color: 1,1,1,1
                font_size: dp(18)
            Button:
                size_hint_x: None
                width: dp(90)
                text: "Back"
                on_release: app.sm.current = "home"

        Notice:
            text: "Enter starts_at as ISO UTC like 2025-08-23T10:00:00Z"
            color: .8,.8,1,1

        TextBox:
            id: title_in
            hint_text: "Title"
        TextBox:
            id: desc_in
            hint_text: "Description (optional)"
        TextBox:
            id: starts_in
            hint_text: "Starts at (ISO 8601, UTC, e.g. 2025-08-23T10:00:00Z)"
        TextBox:
            id: place_in
            hint_text: "Place name (optional)"

        PrimaryButton:
            text: "Create Event"
            on_release: root.do_create(title_in.text.strip(), desc_in.text.strip(), starts_in.text.strip(), place_in.text.strip())

            

            

        Notice:
            id: msg
            text: root.message
            color: .9,.7,.7,1

<LocationUpdateScreen>:
    name: "loc"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: .06,.06,.06,1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Send Location"
            color: 1,1,1,1
            font_size: dp(20)
            size_hint_y: None
            height: self.texture_size[1] + dp(8)

        Notice:
            text: "Manual entry (good on desktop). On mobile, we can wire GPS later."
            color: .8,.8,.8,1

        TextBox:
            id: lat_in
            hint_text: "Latitude (e.g. 37.7765)"
        TextBox:
            id: lon_in
            hint_text: "Longitude (e.g. -122.4164)"
        TextBox:
            id: acc_in
            hint_text: "Accuracy meters (optional)"
        TextBox:
            id: heading_in
            hint_text: "Heading degrees (optional)"
        TextBox:
            id: speed_in
            hint_text: "Speed m/s (optional)"

        PrimaryButton:
            text: "Send once"
            on_release: root.do_send(lat_in.text, lon_in.text, acc_in.text, heading_in.text, speed_in.text)

        Notice:
            id: msg
            text: root.message
            color: 1,.7,.7,1

        SmallLink:
            text: "Back"
            on_release: app.sm.current = "home"

<BuddiesLocationsScreen>:
    name: "buddies"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: .06,.06,.06,1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Buddies' Locations"
            color: 1,1,1,1
            font_size: dp(20)
            size_hint_y: None
            height: self.texture_size[1] + dp(8)

        PrimaryButton:
            text: "Refresh"
            on_release: root.refresh()

        ScrollView:
            GridLayout:
                id: rows
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: dp(40)
                row_force_default: False
                spacing: dp(6)
                padding: dp(4)

        SmallLink:
            text: "Back"
            on_release: app.sm.current = "home"

<BuddyLocationsScreen>:
    name: "buddies"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(12)
        canvas.before:
            Color: 
                rgba: .06,.06,.06,1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Buddy Locations"
            color: 1,1,1,1
            font_size: dp(22)
            size_hint_y: None
            height: self.texture_size[1] + dp(10)

        Notice:
            id: info
            text: root.status_text
            color: .8,.9,1,1

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(8)
            PrimaryButton:
                text: "Refresh now"
                on_release: root.refresh_list()
            ToggleButton:
                id: auto
                text: "Auto-refresh"
                size_hint_x: .6
                on_state: root.toggle_auto(self.state)

        RecycleView:
            id: rv
            viewclass: "Label"
            RecycleBoxLayout:
                default_size: None, dp(34)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: "vertical"

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(8)

            PrimaryButton:
                text: "Share my location"
                on_release: root.share_my_location()

            SmallLink:
                text: "Back"
                on_release: app.sm.current = "home"



ScreenManager:
    id: sm
    transition: FadeTransition()
    LoginScreen:
    RegisterScreen:
    HomeScreen:
    EventsScreen:
    CreateEventScreen:
    LocationUpdateScreen:
    BuddiesLocationsScreen:
"""

class LoginScreen(Screen):
    message = StringProperty("")

    def do_login(self, username: str, password: str):
        self.message = ""
        if not username or not password:
            self.message = "Please enter username and password."
            return
        ok, data = login(username, password)
        if ok:
            App.get_running_app().sm.current = "home"
        else:
            self.message = (data.get("detail") if isinstance(data, dict) else str(data)) or "Login failed."

class RegisterScreen(Screen):
    message = StringProperty("")

    def do_register(self, username: str, email: str, pw1: str, pw2: str):
        self.message = ""
        if not username or not email or not pw1 or not pw2:
            self.message = "Fill all fields."
            return
        if pw1 != pw2:
            self.message = "Passwords do not match."
            return
        ok, data = register(username, email, pw1)
        if ok:
            if not get_token():
                self.message = "Registered! Now login with your credentials."
                App.get_running_app().sm.current = "login"
                return
            App.get_running_app().sm.current = "home"
        else:
            self.message = (data.get("detail") if isinstance(data, dict) else str(data)) or "Registration failed."

class HomeScreen(Screen):
    header_text = StringProperty("(loading…)")

    def on_enter(self, *args):
        if not get_token():
            App.get_running_app().sm.current = "login"
            return
        Clock.schedule_once(lambda *_: self.refresh_me(), 0)

    def refresh_me(self):
        ok, data = me()
        if ok and isinstance(data, dict):
            self.header_text = f"Hello, {data.get('first_name') or data.get('username')}!"
        else:
            self.header_text = f"Auth error: {(data.get('detail') if isinstance(data, dict) else data)}"
            if "Invalid token" in str(data) or "Authentication" in str(data):
                clear_session()
                App.get_running_app().sm.current = "login"

    def do_logout(self):
        clear_session()
        App.get_running_app().sm.current = "login"

from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

class BuddyLocationsScreen(Screen):
    status_text = StringProperty("")

    _auto_ev = None  # Clock event handle

    def on_enter(self, *args):
        # Load immediately when entering
        self.refresh_list()

    def on_leave(self, *args):
        # Stop auto-refresh when leaving
        self._cancel_auto()

    def _cancel_auto(self):
        if self._auto_ev is not None:
            self._auto_ev.cancel()
            self._auto_ev = None

    def toggle_auto(self, state):
        if state == "down":
            # refresh every 10s
            self._cancel_auto()
            self._auto_ev = Clock.schedule_interval(lambda *_: self.refresh_list(), 10)
            self.status_text = "Auto-refresh: ON (every 10s)"
        else:
            self._cancel_auto()
            self.status_text = "Auto-refresh: OFF"

    def refresh_list(self):
        # get_buddies_locations returns (ok, data_or_error)
        ok, data = get_buddies_locations()
        if not ok:
            self.status_text = f"Error: {data.get('detail') or data}"
            self.ids.rv.data = []
            return

        # Expecting a list of {username, latitude, longitude, accuracy, updated_at}
        rows = []
        for item in data:
            uname = item.get("username", "unknown")
            lat = item.get("latitude")
            lon = item.get("longitude")
            acc = item.get("accuracy")
            updated = item.get("updated_at", "")
            rows.append({
                "text": f"{uname} — lat:{lat} lon:{lon} acc:{acc} — {updated}",
                "color": (0.9, 0.9, 0.9, 1),
                "font_size": "14sp",
            })
        self.ids.rv.data = rows
        self.status_text = f"{len(rows)} buddy location(s) loaded."

    def share_my_location(self):
        # Dummy coords for now. Replace with real device/location integration later
        # (you can wire GPS here or read from a config)
        lat, lon = 37.776, -122.416
        ok, data = update_location(latitude=lat, longitude=lon, accuracy=15.0, heading=None, speed=None)
        if ok:
            self.status_text = "Location shared! (lat/long updated)"
            # optionally refresh list after sharing
            self.refresh_list()
        else:
            self.status_text = f"Share failed: {data.get('detail') or data}"


class LocationUpdateScreen(Screen):
    message = StringProperty("")

    def do_send(self, lat, lon, acc, heading, speed):
        self.message = ""
        try:
            if not lat or not lon:
                self.message = "Latitude and Longitude are required."
                return
            ok, data = update_location(lat, lon, acc or None, heading or None, speed or None)
            if ok:
                self.message = f"Location updated ✓"
            else:
                self.message = data.get("detail") or str(data)
        except ValueError:
            self.message = "Please enter valid numeric values."
        except Exception as e:
            self.message = str(e)

class BuddiesLocationsScreen(Screen):
    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        rows = self.ids.rows
        rows.clear_widgets()
        ok, data = get_buddies_locations()
        if not ok:
            from kivy.uix.label import Label
            rows.add_widget(Label(text=f"[error] {data.get('detail') or data}", color=(1, .7, .7, 1), markup=False, size_hint_y=None, height=32))
            return

        # data should be a list of objects with: username, latitude, longitude, updated_at, etc.
        # Show newest first
        try:
            sorted_data = sorted(
                data,
                key=lambda d: d.get("updated_at") or "",
                reverse=True
            )
        except Exception:
            sorted_data = data

        from kivy.uix.label import Label
        if not sorted_data:
            rows.add_widget(Label(text="No buddy locations yet.", color=(.8, .8, .8, 1), size_hint_y=None, height=32))
            return

        for item in sorted_data:
            username = str(item.get("username") or "?")
            lat = item.get("latitude")
            lon = item.get("longitude")
            ts = item.get("updated_at") or ""
            rows.add_widget(
                Label(
                    text=f"{username}: {lat}, {lon}  •  {ts}",
                    color=(.9, .95, 1, 1),
                    size_hint_y=None,
                    height=28
                )
            )


class EventsScreen(Screen):
    message = StringProperty("")

    def on_pre_enter(self, *args):
        self.message = "Loading…"
        Clock.schedule_once(lambda *_: self._load(), 0)

    def _add_item(self, event: dict):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        row = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(90))
        title = event.get("title","(no title)")
        who = event.get("creator_username","")
        when = event.get("starts_at","")
        place = event.get("place_name") or ""
        lbl = Label(
            text=f"[b]{title}[/b]\\nby {who} — {when}\\n{place}",
            markup=True, color=(1,1,1,1),
            size_hint_y=None
        )
        # Let label compute its height
        lbl.bind(texture_size=lambda *_: setattr(lbl, "height", lbl.texture_size[1]+6))
        row.add_widget(lbl)

        self.ids.listbox.add_widget(row)

    def _load(self):
        # Show all events (you can also call attending_events(), my_events())
        ok, data = events_feed()
        self.ids.listbox.clear_widgets()
        if not ok:
            self.message = (data.get("detail") if isinstance(data, dict) else str(data)) or "Failed to load."
            return
        if not isinstance(data, list) or not data:
            self.message = "No events yet. Create one!"
            return
        self.message = f"{len(data)} event(s)"
        for ev in data:
            self._add_item(ev)

class CreateEventScreen(Screen):
    message = StringProperty("")

    def do_create(self, title, description, starts_at, place_name):
        from api import create_event
        self.message = ""

        if not title or not starts_at:
            self.message = "Title and starts_at are required."
            return

        ok, data = create_event(
            title=title,
            starts_at=starts_at,
            place_name=place_name or None,
            visibility="buddies",
            description=description or ""
        )

        if ok:
            self.message = "✅ Event created!"
            # optional: clear fields
            try:
                self.ids.title_in.text = ""
                self.ids.desc_in.text = ""
                self.ids.starts_in.text = ""
                self.ids.place_in.text = ""
            except Exception:
                pass
            # optional: go to feed
            # App.get_running_app().sm.current = "events_feed"
        else:
            # backend returns JSON with details
            self.message = str(data.get("detail") or data)

class ToGatherApp(App):
    def build(self):
        self.title = "ToGather"
        self.sm = Builder.load_string(KV)
        if get_token():
            Clock.schedule_once(lambda *_: self._post_build_nav(), 0.1)
        return self.sm

    def _post_build_nav(self):
        ok, _data = me()
        self.sm.current = "home" if ok else "login"

# dp helper for Python-side sizing
from kivy.metrics import dp

if __name__ == "__main__":
    ToGatherApp().run()
