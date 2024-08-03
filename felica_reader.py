from smartcard.scard import *
from smartcard.util import toHexString

class FeliCaReader:
    GET_IDM_CMD = [0xFF, 0xCA, 0x00, 0x00, 0x00]  # 定数化

    def __init__(self):
        self.context = None
        self.reader = None
        self.connection = None
        self.dwActiveProtocol = None
        self.initialize_reader()

    def initialize_reader(self):
        try:
            hresult, self.context = SCardEstablishContext(SCARD_SCOPE_USER)
            if hresult != SCARD_S_SUCCESS:
                raise Exception(f"コンテキストの確立に失敗しました: {hresult}")

            hresult, readers = SCardListReaders(self.context, [])
            if hresult != SCARD_S_SUCCESS or len(readers) == 0:
                raise Exception("カードリーダーが見つかりません")

            self.reader = readers[0]
            print(f"リーダー: {self.reader}")

        except Exception as e:
            print(f"カードリーダーの初期化に失敗しました: {e}")

    def connect(self):
        try:
            if self.connection:
                self.close()  # 既存の接続がある場合は閉じる

            if not self.context:
                self.initialize_reader()

            hresult, self.connection, self.dwActiveProtocol = SCardConnect(
                self.context,
                self.reader,
                SCARD_SHARE_SHARED,
                SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1
            )
            if hresult != SCARD_S_SUCCESS:
                self.connection = None
                raise Exception(f"リーダーへの接続に失敗しました: {hresult}")

            print("リーダーに接続しました")

        except Exception as e:
            print(f"リーダーへの接続に失敗しました: {e}")

    def check_card_presence(self):
        if not self.connection:
            self.connect()
            if not self.connection:
                return False

        try:
            hresult, response = SCardTransmit(self.connection, self.dwActiveProtocol, self.GET_IDM_CMD)
            if hresult != SCARD_S_SUCCESS:
                raise Exception(f"SCardTransmitに失敗しました: {hresult}")

            print(f"応答: {response}")

            if len(response) >= 2 and response[-2] == 0x90 and response[-1] == 0x00:
                print("カードが検出されました")
                return True
            else:
                print("カードが検出されません")
                self.close()
                return False
        except Exception as e:
            print(f"カードの検出に失敗しました: {e}")
            self.close()
            return False

    def get_idm(self):
        if not self.check_card_presence():
            return None

        try:
            hresult, response = SCardTransmit(self.connection, self.dwActiveProtocol, self.GET_IDM_CMD)
            if hresult != SCARD_S_SUCCESS:
                raise Exception(f"SCardTransmitに失敗しました: {hresult}")

            print(f"応答: {response}")

            if len(response) >= 8:
                idm = toHexString(response[:8])
                print(f"取得したIDm: {idm}")
                return idm
            else:
                print("IDmの取得に失敗しました")
                return None
        except Exception as e:
            print(f"IDmの取得に失敗しました: {e}")
            return None

    def close(self):
        if self.connection:
            SCardDisconnect(self.connection, SCARD_LEAVE_CARD)
            self.connection = None
        if self.context:
            SCardReleaseContext(self.context)
            self.context = None

if __name__ == "__main__":
    reader = FeliCaReader()
    idm = reader.get_idm()
    print(f"IDm: {idm}")
    reader.close()
