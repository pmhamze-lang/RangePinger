import ipaddress
import subprocess
import platform
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.clock import Clock


class PingApp(App):
    def build(self):
        self.is_running = False
        self.threads = []

        # Main Layout
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Input Layout (IP or CIDR Range)
        self.ip_input = TextInput(
            text='5.202.10.96/27',
            hint_text='Enter IP or Range (e.g. 192.168.1.1 or 5.202.10.96/27)',
            multiline=False,
            size_hint_y=None,
            height='48dp'
        )
        root.add_widget(self.ip_input)

        # Control Buttons Layout
        btn_layout = BoxLayout(size_hint_y=None, height='48dp', spacing=10)
        
        self.btn_start = Button(text='Start Ping', background_color=(0.2, 0.8, 0.2, 1))
        self.btn_start.bind(on_press=self.start_ping)
        
        self.btn_stop = Button(text='Stop', background_color=(0.8, 0.2, 0.2, 1), disabled=True)
        self.btn_stop.bind(on_press=self.stop_ping)

        btn_layout.add_widget(self.btn_start)
        btn_layout.add_widget(self.btn_stop)
        root.add_widget(btn_layout)

        # Scrollable Output List
        self.scroll = ScrollView()
        self.output_label = Label(
            text='Ready...\n',
            size_hint_y=None,
            alignment=('left', 'top'),
            markup=True
        )
        self.output_label.bind(texture_size=self.output_label.setter('size'))
        self.scroll.add_widget(self.output_label)
        root.add_widget(self.scroll)

        return root

    def append_log(self, message):
        def update_text(dt):
            self.output_label.text += message + '\n'
            self.scroll.scroll_y = 0
        Clock.schedule_once(update_text)

    def ping_ip(self, ip_str):
        if not self.is_running:
            return
        
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        cmd = ['ping', param, '1', '-w', '1000', ip_str] if platform.system().lower() == 'windows' else ['ping', param, '1', '-W', '1', ip_str]

        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                self.append_log(f"[color=00ff00][+] {ip_str} is ONLINE[/color]")
            else:
                self.append_log(f"[color=888888][-] {ip_str} is OFFLINE[/color]")
        except Exception as e:
            self.append_log(f"[color=ff0000]Error pinging {ip_str}: {e}[/color]")

    def run_scanner(self, target_str):
        try:
            if '/' in target_str:
                net = ipaddress.ip_network(target_str, strict=False)
                ip_list = [str(ip) for ip in net.hosts()]
            else:
                ip_list = [str(ipaddress.ip_address(target_str))]

            self.append_log(f"[color=ffff00]Starting scan for {len(ip_list)} host(s)...[/color]\n")

            for ip in ip_list:
                if not self.is_running:
                    break
                t = threading.Thread(target=self.ping_ip, args=(ip,))
                t.daemon = True
                self.threads.append(t)
                t.start()
                # Limit active threads to prevent overload
                if len(self.threads) >= 20:
                    for active_t in self.threads:
                        active_t.join()
                    self.threads = []

            for t in self.threads:
                t.join()

            if self.is_running:
                self.append_log("\n[color=00ffff]--- Scan Completed ---[/color]")

        except ValueError as ve:
            self.append_log(f"[color=ff0000]Invalid IP / Range format: {ve}[/color]")
        finally:
            Clock.schedule_once(lambda dt: self.reset_buttons())

    def start_ping(self, instance):
        target = self.ip_input.text.strip()
        if not target:
            return
        
        self.is_running = True
        self.btn_start.disabled = True
        self.btn_stop.disabled = False
        self.output_label.text = ""
        
        scan_thread = threading.Thread(target=self.run_scanner, args=(target,))
        scan_thread.daemon = True
        scan_thread.start()

    def stop_ping(self, instance):
        self.is_running = False
        self.append_log("\n[color=ff9900]Stopping scan...[/color]")
        self.reset_buttons()

    def reset_buttons(self):
        self.btn_start.disabled = False
        self.btn_stop.disabled = True


if __name__ == '__main__':
    PingApp().run()