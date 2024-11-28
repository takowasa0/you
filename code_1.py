from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# スコープの設定（YouTubeのデータを読み取る権限）
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    credentials = None
    # 過去の認証情報をロード
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    # 新規認証が必要な場合
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            credentials = flow.run_local_server(port=0)

        # 認証情報を保存
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    # YouTube APIクライアントを作成
    youtube = build("youtube", "v3", credentials=credentials)

    # 全件取得のためのリスト
    all_subscriptions = []
    next_page_token = None

    # ページネーションで全件取得
    while True:
        request = youtube.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=50,
            pageToken=next_page_token  # 次のページトークンを指定
        )
        response = request.execute()

        # 取得したアイテムをリストに追加
        all_subscriptions.extend(response.get("items", []))

        # 次のページがある場合はトークンを設定
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    # 結果を表示
    for item in all_subscriptions:
        title = item["snippet"]["title"]
        channel_id = item["snippet"]["resourceId"]["channelId"]
        print(f"Title: {title}, URL: https://www.youtube.com/channel/{channel_id}")

if __name__ == "__main__":
    main()
