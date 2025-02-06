# Kivy & KivyMD Core
from kivy.graphics import Fbo
from kivy.core.window import Window

# Example of initializing FBO with different parameters
fbo = Fbo(size=Window.size, with_stencilbuffer=False)

from kivymd.app import MDApp, App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty, DictProperty
from kivymd.uix.list import MDList, TwoLineIconListItem



# KivyMD Components
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.theming import ThemeManager
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDIconButton
from kivymd.uix.toolbar import toolbar





# Python Standard Library
from datetime import datetime

# Third Party Libraries
import pyrebase
from plyer import notification



# Firebase configuration
config = {
    "apiKey": "AIzaSyDjODBYFW3qWxGnyToLJQ4JOc-qZjWmDOg",
    "authDomain": "home-service-provider-ap-54db3.firebaseapp.com",
    "databaseURL": "https://home-service-provider-ap-54db3-default-rtdb.firebaseio.com",
    "projectId": "home-service-provider-ap-54db3",
    "storageBucket": "home-service-provider-ap-54db3.firebasestorage.app",
    "packageName": "com.example.homeserviceprovider"
}
#establishing connection
firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()

# functional code starts here

#welcome screen
class WelcomeScreen(Screen):
    def goto_user_login(self):
        self.manager.current = 'user_login'

    def goto_serviceman_login(self):
        self.manager.current = 'serviceman_login'
#userlogin screen  
    
class UserLoginScreen(Screen):
    def login(self):
        # Get input values
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()
       
        # Validation for empty fields
        if not email or not password:
            self.ids.status_label.text = "Both email and password fields are required!"
            self.ids.status_label.theme_text_color = "Error"
            return
            
        try:
            # Firebase Authentication
            user = auth.sign_in_with_email_and_password(email, password)
            App.get_running_app().user = user
            App.get_running_app().user_type = 'user'
            self.manager.current = 'userdashboard'
           
        except Exception as e:
            # Display error message
            error_message = str(e)
            self.ids.status_label.text = f"Login Failed, {str(e)}Try again."
            self.ids.status_label.text_color = [1, 0, 0, 1]

    def goto_signup(self):
        """Navigate to the signup screen."""
        self.manager.current = 'user_signup'


#user register screen
class UserSignupScreen(Screen):
    
    def signup(self):
        email = self.ids.email.text
        password = self.ids.password.text
        name = self.ids.name.text
        phone = self.ids.phone.text
        
        # Input Validation: Check if any field is empty
        if not name or not email or not password or not phone:
            self.show_label("All fields are required.", "red")
            return
        
        try:
            # Firebase signup (assuming authentication setup is correct)
            user = auth.create_user_with_email_and_password(email, password)
            user_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'type': 'user'
            }
            db.child('users').child(user['localId']).set(user_data)
            self.show_label("Signup Successful! Please login to continue.", "green")
            self.manager.current = 'user_login'
        except Exception as e:
            self.show_label(f"Signup Failed: {str(e)}", "red")
    
    def goto_login(self):
        self.manager.current = 'user_login'
    
    def show_label(self, message, color):
        # Access the MDLabel to update its text and color
        status_label = self.ids.status_label
        status_label.text = message
        if color == "green":
            status_label.text_color = (0, 1, 0, 1)  # Green for success
        else:
            status_label.text_color = (1, 0, 0, 1)  # Red for error

        # Optionally, clear the label text after a short delay
        Clock.schedule_once(lambda dt: self.clear_label(), 3)
    
    def clear_label(self):
        # Clear the label text after the message disappears
        self.ids.status_label.text = ''
        
#user dashboard
class UserDashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()  # Store app reference
        
    def go_back(self):
        self.manager.current = 'login'  # Add the screen you want to go back to
        
        
    def on_enter(self):
        self.load_services()
        
    def load_services(self):
        services = db.child('services').get()
        container = self.ids.services_container
        container.clear_widgets()
        
        if services:
            for service in services.each():
                service_data = service.val()
                self.create_service_card(service_data, service.key())
                
    def create_service_card(self, service_data, service_key):
        container = self.ids.services_container
        
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=dp(15),
            spacing=dp(5),
            radius=[15],
            elevation=1,
            md_bg_color=[0.95, 0.95, 0.95, 1]
        )
        
        name_label = MDLabel(
            text=service_data['name'],
            font_style="H6",
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        
        price_label = MDLabel(
            text=f"₹{service_data['price']}",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            theme_text_color="Secondary"
        )
        
        book_btn = MDRaisedButton(
            text='Book Now',
            size_hint_y=None,
            height=dp(40),
            md_bg_color=[0.13, 0.59, 0.95, 1]
        )
        book_btn.service_id = service_key
        book_btn.bind(on_press=self.book_service)
        
        
        card.add_widget(name_label)
        card.add_widget(price_label)
        card.add_widget(book_btn)
        
        container.add_widget(card)
    
    def search_services(self, text):
        if not text:
            self.load_services()
            return
            
        services = db.child('services').get()
        container = self.ids.services_container
        container.clear_widgets()
        
        if services:
            for service in services.each():
                service_data = service.val()
                if text.lower() in service_data['name'].lower():
                    self.create_service_card(service_data, service.key())
    
    def book_service(self, instance):
        self.app.current_service = instance.service_id
        self.manager.current = 'booking'

class BookServiceScreen(Screen):
    def confirm_booking(self):
        # Retrieve the app instance for shared data
        service_id = App.get_running_app().current_service
        user_id = App.get_running_app().user['localId']
        
        # Fetch data from input fields
        date = self.ids.date.text.strip()
        time = self.ids.time.text.strip()
        location = self.ids.location.text.strip()
        address = self.ids.address.text.strip()
        mobile = self.ids.mobile.text.strip()
        
        # Clear any previous error messages
        if 'error_message' in self.ids:
            self.ids.error_message.text = ""
        
        # Validate input fields
        if not date or not time or not location or not address or not mobile:
            self.show_error("All fields are required!")
            return
            
        if len(mobile) != 10 or not mobile.isdigit():
            self.show_error("Enter a valid 10-digit mobile number.")
            return
        
        # Prepare booking data
        booking_data = {
            'service_id': service_id,
            'user_id': user_id,
            'date': date,
            'time': time,
            'location': location,
            'address': address,
            'mobile': mobile,
            'status': 'pending',
            'timestamp': {'.sv': 'timestamp'}
        }
        
        # Push to database
        db.child('bookings').push(booking_data)
        self.send_notification("Booking Confirmed", "Your service has been booked!")
        self.goto_dashboard()

    def goto_dashboard(self):
        self.manager.current = 'userdashboard'

    def send_notification(self, title, message):
        """Display notification using MDSnackbar."""
        Snackbar(
            text=f"{title}: {message}",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=0.9,
            bg_color=self.theme_cls.primary_color,  # Uses the theme's primary color
            duration=2.5  # Duration in seconds
        ).open()

    def show_error(self, message):
        """Display error messages using MDSnackbar."""
        Snackbar(
            text=message,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=0.9,
            bg_color=(1, 0, 0, 1),  # Red color for errors
            duration=2.5
        ).open()
        
class BookServiceScreen(Screen):
    def confirm_booking(self):
        # Retrieve the app instance for shared data
        service_id = App.get_running_app().current_service
        user_id = App.get_running_app().user['localId']
        
        # Fetch data from input fields
        date = self.ids.date.text.strip()
        time = self.ids.time.text.strip()
        location = self.ids.location.text.strip()
        address = self.ids.address.text.strip()
        mobile = self.ids.mobile.text.strip()
        
        # Clear any previous error messages
        if 'error_message' in self.ids:
            self.ids.error_message.text = ""

        # Validate input fields
        if not date or not time or not location or not address or not mobile:
            self.show_error("All fields are required!")
            return
        
        if len(mobile) != 10 or not mobile.isdigit():
            self.show_error("Enter a valid 10-digit mobile number.")
            return

        # Prepare booking data
        booking_data = {
            'service_id': service_id,
            'user_id': user_id,
            'date': date,
            'time': time,
            'location': location,
            'address': address,
            'mobile': mobile,
            'status': 'pending',
            'timestamp': {'.sv': 'timestamp'}
        }
        
        # Push to database
        db.child('bookings').push(booking_data)
        self.send_notification("Booking Confirmation", "Your Booking Request has been Sent. Please wait for further information.")
        self.goto_dashboard()

    def show_error(self, message):
        """Display the error message in the validation label"""
        self.ids.validation_label.text = message

    def goto_dashboard(self):
        self.manager.current = 'userdashboard'

    def send_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_icon=None,
            timeout=10,
        )

class BookingHistoryScreen(Screen):
    def on_enter(self):
        """Fetch booking history when the screen is entered"""
        self.fetch_booking_history()

    def fetch_booking_history(self):
        """Fetch booking history from Firebase"""
        user_id = App.get_running_app().user['localId']
        
        # Fetch the user's bookings from Firebase
        bookings_ref = db.child('bookings').order_by_child('user_id').equal_to(user_id).get()

        if bookings_ref.each():
            for booking in bookings_ref.each():
                self.display_booking(booking.val())
        else:
            self.show_no_bookings_message()

    def display_booking(self, booking):
        """Display a single booking's details in the UI"""
        # Create a card for each booking
        booking_card = MDCard(size_hint_y=None, height="200dp", padding="10dp", spacing="10dp")
        
        service_details = f"Service: {booking['service_id']}\nDate: {booking['date']}\nTime: {booking['time']}\nLocation: {booking['location']}\nAddress: {booking['address']}\nMobile: {booking['mobile']}"
        booking_status = f"Status: {booking['status']}"
        
        # Adding the service details as a label
        booking_card.add_widget(MDLabel(text=service_details, theme_text_color="Secondary"))

        # Adding the status as a label
        booking_card.add_widget(MDLabel(text=booking_status, theme_text_color="Primary"))

        # Adding the card to the ScrollView
        self.ids.booking_history_box.add_widget(booking_card)

    def show_no_bookings_message(self):
        """Display a message when no bookings are found"""
        no_bookings_label = MDLabel(text="You have no booking history.", halign="center", theme_text_color="Error")
        self.ids.booking_history_box.add_widget(no_bookings_label)

    def goto_dashboard(self):
        """Go back to the dashboard screen"""
        self.manager.current = 'userdashboard'
        

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None

    def on_enter(self):
        # Check if user is logged in
        if auth.current_user:
            self.user_id = auth.current_user['localId']
            self.fetch_user_data()
        else:
            self.ids.notification_label.text = "User not logged in"

    def fetch_user_data(self):
        # Fetch user data from Firebase
        user_data = db.child("users").child(self.user_id).get().val()

        if user_data:
            self.ids.name.text = user_data.get("name", "N/A")
            self.ids.email.text = user_data.get("email", "N/A")
            self.ids.phone.text = user_data.get("phone", "N/A")
            self.ids.notification_label.text = "User data loaded successfully"
        else:
            self.ids.notification_label.text = "Failed to load user data"

    def enable_edit_mode(self):
        # Enable editing
        self.ids.name.disabled = False
        self.ids.email.disabled = False
        self.ids.phone.disabled = False
        self.ids.notification_label.text = "Edit mode enabled"

    def save_profile(self):
        # Get updated data from fields
        new_name = self.ids.name.text.strip()
        new_email = self.ids.email.text.strip()
        new_phone = self.ids.phone.text.strip()

        if new_name and new_email and new_phone:
            updated_data = {
                "name": new_name,
                "email": new_email,
                "phone": new_phone,
            }
            # Save to Firebase
            db.child("users").child(self.user_id).update(updated_data)
            self.ids.notification_label.text = "Profile updated successfully"

            # Disable editing
            self.ids.name.disabled = True
            self.ids.email.disabled = True
            self.ids.phone.disabled = True
        else:
            self.ids.notification_label.text = "All fields are required"

    def change_password(self):
        old_password = self.ids.old_password.text.strip()
        new_password = self.ids.new_password.text.strip()

        if old_password and new_password:
            try:
                # Reauthenticate user with old password
                user = auth.sign_in_with_email_and_password(
                    self.ids.email.text, old_password
                )
                # Update password
                auth.update_password(user['idToken'], new_password)
                self.ids.notification_label.text = "Password changed successfully"
                self.ids.old_password.text = ""
                self.ids.new_password.text = ""
            except:
                self.ids.notification_label.text = "Password change failed"
        else:
            self.ids.notification_label.text = "Both fields are required"

#serviceman screens------
        
#servicemanlogin
class ServiceManLoginScreen(Screen):
    def login(self):
        email = self.ids.email.text
        password = self.ids.password.text

        # Input Validation: Check if fields are empty
        if not email or not password:
            self.show_label("All fields are required.", "red")
            return

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            App.get_running_app().user = user
            App.get_running_app().user_type = 'serviceman'
            self.manager.current = 'service_dashboard'
            self.show_label("Login Successful", "green")
        except Exception as e:
            self.show_label(f"Login Failed: {str(e)}", "red")
            
    def goto_signup(self):
        self.manager.current = 'serviceman_signup'
        
    def show_label(self, message, color):
        # Access the MDLabel to update its text and color
        status_label = self.ids.status_label
        status_label.text = message
        
        if color == "green":
            status_label.text_color = (0, 1, 0, 1)  # Green for success
        else:
            status_label.text_color = (1, 0, 0, 1)  # Red for error

        # Optionally, clear the label text after a short delay
        Clock.schedule_once(lambda dt: self.clear_label(), 3)
    
    def clear_label(self):
        # Clear the label text after the message disappears
        self.ids.status_label.text = ''
        

class ServiceManSignupScreen(Screen):
    def signup(self):
        email = self.ids.email.text
        password = self.ids.password.text
        name = self.ids.name.text
        phone = self.ids.phone.text
        profession = self.ids.profession.text
        experience = self.ids.experience.text
        location = self.ids.location.text

        # Input Validation: Check if any field is empty
        if not name or not email or not password or not phone or not profession or not experience or not location:
            self.show_label("All fields are required.", "red")
            return

        try:
            # Firebase signup
            user = auth.create_user_with_email_and_password(email, password)
            user_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'profession': profession,
                'experience': experience,
                'location': location,
                'type': 'serviceman'
            }
            db.child('users').child(user['localId']).set(user_data)
            self.show_label("Signup Successful! Please login to continue.", "green")
            self.manager.current = 'serviceman_login'
        except Exception as e:
            self.show_label(f"Signup Failed: {str(e)}", "red")

    def goto_login(self):
        self.manager.current = 'serviceman_login'

    def show_label(self, message, color):
        # Access the MDLabel to update its text and color
        status_label = self.ids.status_label
        status_label.text = message
        
        if color == "green":
            status_label.text_color = (0, 1, 0, 1)  # Green for success
        else:
            status_label.text_color = (1, 0, 0, 1)  # Red for error

        # Optionally, clear the label text after a short delay
        Clock.schedule_once(lambda dt: self.clear_label(), 3)
    
    def clear_label(self):
        # Clear the label text after the message disappears
        self.ids.status_label.text = ''


class BookingCard(MDCard):
    def __init__(self, booking_data, service_data, user_data, on_accept, on_reject, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(250)
        self.md_bg_color = [0.9, 0.9, 0.9, 1]
        self.radius = [15]
        
        details = f"Service: {service_data['name']}\n"
        details += f"Customer: {user_data['name']}\n"
        details += f"Date: {booking_data['date']}\n"
        details += f"Time: {booking_data['time']}\n"
        details += f"Location: {booking_data['location']}\n"
        details += f"Mobile: {booking_data['mobile']}"
        
        label = MDLabel(
            text=details,
            size_hint_y=None,
            height=dp(150)
        )
        
        buttons_box = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )
        
        accept_btn = MDRaisedButton(
            text="Accept",
            on_press=on_accept,
            md_bg_color=[0.2, 0.8, 0.2, 1]
        )
        reject_btn = MDRaisedButton(
            text="Reject",
            on_press=on_reject,
            md_bg_color=[0.8, 0.2, 0.2, 1]
        )
        
        buttons_box.add_widget(accept_btn)
        buttons_box.add_widget(reject_btn)
        
        self.add_widget(label)
        self.add_widget(buttons_box)

class ServiceCard(MDCard):
    def __init__(self, service_data, on_edit, on_delete, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(200)
        self.md_bg_color = [0.95, 0.95, 0.95, 1]
        self.radius = [15]
        
        details = f"Service: {service_data['name']}\n"
        details += f"Price: ₹{service_data['price']}"
        
        label = MDLabel(
            text=details,
            size_hint_y=None,
            height=dp(100)
        )
        
        buttons_box = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )
        
        edit_btn = MDRaisedButton(
            text="Edit",
            on_press=on_edit,
            md_bg_color=[0.2, 0.6, 0.8, 1]
        )
        delete_btn = MDRaisedButton(
            text="Delete",
            on_press=on_delete,
            md_bg_color=[0.8, 0.2, 0.2, 1]
        )
        
        buttons_box.add_widget(edit_btn)
        buttons_box.add_widget(delete_btn)
        
        self.add_widget(label)
        self.add_widget(buttons_box)

class ServiceManDashboardScreen(Screen):
    def on_enter(self):
        self.load_bookings()
        self.load_services()
        
    def load_bookings(self):
        user_id = App.get_running_app().user['localId']
        bookings = db.child('bookings').order_by_child('status').equal_to('pending').get()
        grid = self.ids.bookings_grid
        grid.clear_widgets()
        
        header = MDLabel(
            text='Pending Bookings',
            font_style='H5',
            adaptive_height=True,
            padding=[0, dp(20)]
        )
        grid.add_widget(header)
        
        if bookings:
            for booking in bookings.each():
                booking_data = booking.val()
                service = db.child('services').child(booking_data['service_id']).get().val()
                user = db.child('users').child(booking_data['user_id']).get().val()
                
                card = BookingCard(
                    booking_data=booking_data,
                    service_data=service,
                    user_data=user,
                    on_accept=lambda x, bid=booking.key(): self.accept_booking(bid),
                    on_reject=lambda x, bid=booking.key(): self.reject_booking(bid)
                )
                grid.add_widget(card)
        else:
            no_bookings = MDLabel(
                text='No pending bookings available',
                adaptive_height=True,
                halign='center'
            )
            grid.add_widget(no_bookings)

    def accept_booking(self, booking_id):
        db.child('bookings').child(booking_id).update({
            'status': 'accepted',
            'provider_id': App.get_running_app().user['localId']
        })
        self.send_notification("Booking Accepted", "You have accepted a new booking!")
        self.load_bookings()
        
    def reject_booking(self, booking_id):
        db.child('bookings').child(booking_id).update({
            'status': 'rejected',
            'provider_id': App.get_running_app().user['localId']
        })
        self.send_notification("Booking Rejected", "You have rejected a booking")
        self.load_bookings()

    def load_services(self):
        user_id = App.get_running_app().user['localId']
        services = db.child('services').order_by_child('provider_id').equal_to(user_id).get()
        grid = self.ids.services_grid
        grid.clear_widgets()
        
        header = MDLabel(
            text='My Services',
            font_style='H5',
            adaptive_height=True,
            padding=[0, dp(20)]
        )
        grid.add_widget(header)
        
        if services:
            for service in services.each():
                service_data = service.val()
                card = ServiceCard(
                    service_data=service_data,
                    on_edit=lambda x, sid=service.key(), sdata=service_data: self.edit_service(sid, sdata),
                    on_delete=lambda x, sid=service.key(): self.delete_service(sid)
                )
                grid.add_widget(card)

    def show_add_service(self):
        self.dialog = MDDialog(
            title="Add New Service",
            type="custom",
            content_cls=MDBoxLayout(
                MDTextField(
                    hint_text="Service Name",
                    id="name_input"
                ),
                MDTextField(
                    hint_text="Price",
                    id="price_input"
                ),
                MDTextField(
                    hint_text="Service Description",
                    id="description_input",
                    multiline=True
                ),
                orientation="vertical",
                spacing=dp(10),
                padding=dp(20),
                adaptive_height=True
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ADD",
                    on_release=self.add_service
                ),
            ],
        )
        self.dialog.open()

    def add_service(self, *args):
        content = self.dialog.content_cls
        name = content.ids.name_input.text
        price = content.ids.price_input.text
        description = content.ids.description_input.text
        
        if name and price:
            service_data = {
                'name': name,
                'price': price,
                'description': description,
                'provider_id': App.get_running_app().user['localId']
            }
            db.child('services').push(service_data)
            self.send_notification("Success", "Service added successfully!")
            self.load_services()
            self.dialog.dismiss()
        else:
            self.send_notification("Error", "Please fill all required fields")

    def edit_service(self, service_id, service_data):
        self.dialog = MDDialog(
            title="Edit Service",
            type="custom",
            content_cls=MDBoxLayout(
                MDTextField(
                    hint_text="Service Name",
                    text=service_data.get('name', ''),
                    id="name_input"
                ),
                MDTextField(
                    hint_text="Price",
                    text=str(service_data.get('price', '')),
                    id="price_input"
                ),
                MDTextField(
                    hint_text="Service Description",
                    text=service_data.get('description', ''),
                    id="description_input",
                    multiline=True
                ),
                orientation="vertical",
                spacing=dp(10),
                padding=dp(20),
                adaptive_height=True
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="UPDATE",
                    on_release=lambda x: self.update_service(service_id)
                ),
            ],
        )
        self.dialog.open()

    def update_service(self, service_id, *args):
        content = self.dialog.content_cls
        name = content.ids.name_input.text
        price = content.ids.price_input.text
        description = content.ids.description_input.text
        
        if name and price:
            service_data = {
                'name': name,
                'price': price,
                'description': description,
                'provider_id': App.get_running_app().user['localId']
            }
            db.child('services').child(service_id).update(service_data)
            self.send_notification("Success", "Service updated successfully!")
            self.load_services()
            self.dialog.dismiss()
        else:
            self.send_notification("Error", "Please fill all required fields")

    def delete_service(self, service_id):
        self.dialog = MDDialog(
            title="Delete Service",
            text="Are you sure you want to delete this service?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=[0.8, 0.2, 0.2, 1],
                    on_release=lambda x: self.confirm_delete(service_id)
                ),
            ],
        )
        self.dialog.open()

    def confirm_delete(self, service_id):
        db.child('services').child(service_id).remove()
        self.send_notification("Success", "Service deleted successfully!")
        self.load_services()
        self.dialog.dismiss()

    def logout(self):
        App.get_running_app().user = None
        self.manager.current = 'welcome'
        
    def send_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_icon=None,
            timeout=10,
        )

#main func

class HomeServiceApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Light"  # or "Dark"
        self.theme_cls.primary_palette = "Blue"  # Primary color scheme
        self.theme_cls.accent_palette = "Amber"  # Accent color scheme
        self.theme_cls.primary_hue = "500"  # Default primary color shade

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        
        # Add all screens to the manager
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(UserLoginScreen(name='user_login'))
        sm.add_widget(UserSignupScreen(name='user_signup'))
        sm.add_widget(UserDashboardScreen(name='userdashboard'))
        sm.add_widget(BookServiceScreen(name='booking'))
        sm.add_widget(BookingHistoryScreen(name='booking_history'))
        sm.add_widget(ProfileScreen(name="profile_screen")) 
        sm.add_widget(ServiceManLoginScreen(name='serviceman_login'))
        sm.add_widget(ServiceManSignupScreen(name='serviceman_signup'))
        sm.add_widget(ProfileScreen(name='profile_screen'))
        # sm.add_widget(ServiceManDashboardScreen(name="dashboard"))
        #sm.add_widget(AddServiceScreen(name="add_service"))
        sm.add_widget(ServiceManDashboardScreen(name="service_dashboard"))  # For managing bookings
 # For adding and deleting services
        sm.add_widget(ProfileScreen(name="profile"))
        
        return sm

if __name__ == '__main__':
    HomeServiceApp().run()