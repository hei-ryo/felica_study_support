import tkinter as tk
from tkinter import messagebox, Toplevel
from threading import Thread
import time
from data_manager import DataManager
from felica_reader import FeliCaReader

class PointManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ポイント管理システム")
        self.geometry("800x600")
        self.data_manager = DataManager()
        self.reader = FeliCaReader()
        self.mode = None
        self.elapsed_time = 0
        self.current_idm = None
        self.last_update_time = time.time()
        self.timer_label = None
        self.create_main_screen()
        self.update_card_status_thread = Thread(target=self.update_card_status, daemon=True)
        self.update_card_status_thread.start()

    def create_main_screen(self):
        self.clear_screen()
        self.status_label = tk.Label(self, text="カードの状態: 認識待ち", font=("Arial", 16))
        self.status_label.pack(pady=10)
        self.idm_label = tk.Label(self, text="IDm: ---", font=("Arial", 16))
        self.idm_label.pack(pady=10)

        stats_frame = tk.Frame(self)
        stats_frame.pack(pady=10)
        self.points_balance_label = tk.Label(stats_frame, text="ポイント残高: ---", font=("Arial", 16))
        self.points_balance_label.pack(side=tk.LEFT, padx=10)
        self.elapsed_time_label = tk.Label(stats_frame, text="経過時間: ---", font=("Arial", 16))
        self.elapsed_time_label.pack(side=tk.LEFT)

        modes_frame = tk.Frame(self)
        modes_frame.pack(pady=10)
        self.mode_var = tk.StringVar(value="A")
        tk.Radiobutton(modes_frame, text="モードA", variable=self.mode_var, value="A", font=("Arial", 16)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(modes_frame, text="モードB", variable=self.mode_var, value="B", font=("Arial", 16)).pack(side=tk.LEFT)

        self.action_button = tk.Button(self, text="スタート", command=self.toggle_point_management, font=("Arial", 16), width=20, height=2)
        self.action_button.pack(pady=20)
        tk.Button(self, text="ポイント履歴を見る", command=self.show_points_history, font=("Arial", 16), width=20, height=2).pack(pady=10)
        tk.Button(self, text="管理者ログイン", command=self.create_login_screen, font=("Arial", 16), width=20, height=2).pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)
        self.update_main_screen(visible=False)

    def toggle_point_management(self):
        if self.action_button.cget("text") == "スタート":
            self.start_point_management()
        else:
            self.stop_point_management()

    def create_login_screen(self):
        self.clear_screen()
        tk.Label(self, text="パスワード:", font=("Arial", 16)).pack(pady=10)
        self.password_entry = tk.Entry(self, show="*", font=("Arial", 16))
        self.password_entry.pack(pady=10)
        tk.Button(self, text="ログイン", command=self.login, font=("Arial", 16), width=20, height=2).pack(pady=10)
        tk.Button(self, text="戻る", command=self.create_main_screen, font=("Arial", 16), width=20, height=2).pack(pady=10)

    def login(self):
        password = self.password_entry.get()
        if password == "your_password":
            self.create_admin_screen()
        else:
            messagebox.showerror("エラー", "無効なパスワードです")

    def create_admin_screen(self):
        self.clear_screen()
        tk.Label(self, text="ポイントの加算または減算", font=("Arial", 16)).pack(pady=10)
        tk.Label(self, text="ポイント数:", font=("Arial", 16)).pack(pady=5)
        self.points_entry = tk.Entry(self, font=("Arial", 16))
        self.points_entry.pack(pady=5)

        buttons_frame = tk.Frame(self)
        buttons_frame.pack(pady=10)
        tk.Button(buttons_frame, text="加算", command=self.add_points, font=("Arial", 16), width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(buttons_frame, text="減算", command=self.deduct_points, font=("Arial", 16), width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(self, text="戻る", command=self.create_main_screen, font=("Arial", 16), width=20, height=2).pack(pady=10)

    def add_points(self):
        try:
            points = int(self.points_entry.get())
            if points > 0 and self.current_idm:
                current_balance = self.data_manager.get_points_balance(self.current_idm)
                new_balance = current_balance + points
                self.data_manager.update_points_balance(self.current_idm, new_balance)
                self.data_manager.add_points_history(self.current_idm, "加算", points)
                messagebox.showinfo("成功", f"{points} ポイントを加算しました")
                self.update_main_screen()
            else:
                messagebox.showwarning("警告", "ポイントは正の数でなければなりません")
        except ValueError:
            messagebox.showwarning("警告", "無効なポイント数です")

    def deduct_points(self):
        try:
            points = int(self.points_entry.get())
            if points > 0 and self.current_idm:
                current_balance = self.data_manager.get_points_balance(self.current_idm)
                if current_balance >= points:
                    new_balance = current_balance - points
                    self.data_manager.update_points_balance(self.current_idm, new_balance)
                    self.data_manager.add_points_history(self.current_idm, "減算", -points)
                    messagebox.showinfo("成功", f"{points} ポイントを減算しました")
                    self.update_main_screen()
                else:
                    messagebox.showwarning("警告", "ポイントが不足しています")
            else:
                messagebox.showwarning("警告", "ポイントは正の数でなければなりません")
        except ValueError:
            messagebox.showwarning("警告", "無効なポイント数です")

    def show_points_history(self):
        if not self.current_idm:
            messagebox.showwarning("警告", "現在カードが認識されていません")
            return

        history_window = Toplevel(self)
        history_window.title("ポイント履歴")
        history_window.geometry("400x300")

        tk.Label(history_window, text="ポイント履歴", font=("Arial", 16)).pack(pady=10)

        history_list = self.data_manager.get_points_history(self.current_idm)
        if not history_list:
            tk.Label(history_window, text="履歴はありません", font=("Arial", 16)).pack(pady=10)
        else:
            for entry in history_list:
                tk.Label(history_window, text=f"{entry['timestamp']}: {entry['action']} {entry['points']} ポイント", font=("Arial", 16)).pack(pady=2)

        tk.Button(history_window, text="閉じる", command=history_window.destroy, font=("Arial", 16), width=20, height=2).pack(pady=10)

    def start_point_management(self):
        if not self.current_idm:
            messagebox.showwarning("警告", "カードが認識されていません")
            return

        self.mode = self.mode_var.get()
        if self.mode == "B":
            points = 100
            current_balance = self.data_manager.get_points_balance(self.current_idm)
            if current_balance < points:
                messagebox.showwarning("警告", "ポイントが不足しています")
                return
            else:
                new_balance = current_balance - points
                self.data_manager.update_points_balance(self.current_idm, new_balance)
                self.data_manager.add_points_history(self.current_idm, "減算", -points)
                messagebox.showinfo("成功", f"{points} ポイントを減算しました")
        
        self.action_button.config(text="終了")
        self.mode_var.set(self.mode)
        self.last_update_time = time.time()
        self.elapsed_time = 0
        self.update_main_screen(visible=True)

    def stop_point_management(self):
        if self.mode == "A":
            elapsed_time = (time.time() - self.last_update_time) / 60
            points_earned = int(elapsed_time)
            if points_earned > 0:
                self.data_manager.add_points(self.current_idm, points_earned)
                self.data_manager.add_points_history(self.current_idm, "加算", points_earned)
            messagebox.showinfo("成功", f"{points_earned} ポイントを付与しました")
        elif self.mode == "B":
            elapsed_time = (time.time() - self.last_update_time) / 60
            if elapsed_time < 60:
                response = messagebox.askyesno("確認", "計測時間が1時間に満たないため、計測を続行しますか？")
                if response:
                    self.start_point_management()
                    return
            self.data_manager.add_points_history(self.current_idm, "減算", -100)
            messagebox.showinfo("成功", "計測を終了しました")

        self.action_button.config(text="スタート")
        self.update_main_screen()

    def update_card_status(self):
        while True:
            try:
                card_idm = self.reader.read_card_idm()
                if card_idm:
                    if card_idm != self.current_idm:
                        self.current_idm = card_idm
                        self.update_main_screen()
                else:
                    self.current_idm = None
                    self.update_main_screen()
            except Exception as e:
                print(f"エラー: {e}")
            time.sleep(3)  # 3秒ごとにカードの認識状況を更新

    def update_main_screen(self, visible=True):
        if not visible:
            self.status_label.config(text="カードの状態: 認識待ち")
            self.idm_label.config(text="IDm: ---")
            self.points_balance_label.config(text="ポイント残高: ---")
            self.elapsed_time_label.config(text="経過時間: ---")
        else:
            if self.current_idm:
                self.status_label.config(text="カードの状態: 認識済み")
                self.idm_label.config(text=f"IDm: {self.current_idm}")
                balance = self.data_manager.get_points_balance(self.current_idm)
                self.points_balance_label.config(text=f"ポイント残高: {balance}")
                self.elapsed_time_label.config(text=f"経過時間: {self.elapsed_time:.2f} 分")
            else:
                self.status_label.config(text="カードの状態: 認識待ち")
                self.idm_label.config(text="IDm: ---")

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = PointManagementApp()
    app.mainloop()
