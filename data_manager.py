import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, file_path='data.json'):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # IDmをキーとして辞書に変換
                    return {entry['idm']: entry for entry in data}
            except json.JSONDecodeError:
                print("Warning: data.json is invalid. Loading default data.")
                return {}
        else:
            return {}

    def save_data(self):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            # 辞書をリスト形式に変換して保存
            json.dump(list(self.data.values()), file, ensure_ascii=False, indent=4)

    def get_entry_by_idm(self, idm):
        return self.data.get(idm, None)

    def create_entry(self, idm):
        new_entry = {
            "idm": idm,
            "points_history": [],
            "elapsed_time": 0,
            "points_balance": 0
        }
        self.data[idm] = new_entry
        self.save_data()
        return new_entry

    def get_or_create_entry(self, idm):
        entry = self.get_entry_by_idm(idm)
        if entry is None:
            entry = self.create_entry(idm)
        return entry

    def update_points_balance(self, idm, new_balance):
        entry = self.get_or_create_entry(idm)
        entry["points_balance"] = new_balance
        self.save_data()

    def add_points_history(self, idm, action, points):
        entry = self.get_or_create_entry(idm)
        entry["points_history"].append({
            "action": action,
            "points": points,
            "timestamp": str(datetime.now())
        })
        self.save_data()

    def update_elapsed_time(self, idm, elapsed_time):
        entry = self.get_or_create_entry(idm)
        entry["elapsed_time"] = elapsed_time
        self.save_data()

    def get_points_balance(self, idm):
        entry = self.get_or_create_entry(idm)
        return entry["points_balance"]

    def get_points_history(self, idm):
        entry = self.get_or_create_entry(idm)
        return entry["points_history"]

    def get_elapsed_time(self, idm):
        entry = self.get_or_create_entry(idm)
        return entry["elapsed_time"]
