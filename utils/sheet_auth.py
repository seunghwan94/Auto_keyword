
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "config/GoogleSheets.json", scope)
    return gspread.authorize(credentials)

def get_user_info(email, sheet_url="https://docs.google.com/spreadsheets/d/1Bcc8Lf7lANn9DxVM-t6Knx6OEAWDpNLdRUl8d1ZttgE/edit#gid=0", sheet_name="AutoProgram"):
    try:
        client = get_gspread_client()
        doc = client.open_by_url(sheet_url)
        sheet = doc.worksheet(sheet_name)
        rows = sheet.get_all_records()  # 첫 행을 헤더로 인식함

        for row in rows:
            if str(row["이메일"]).strip().lower() == email.strip().lower():
                if str(row["keyword(0,1)"]).strip() == "1":
                    return {
                        "email": row["이메일"],
                        "grade": int(row["등급 (1,2,3)"]),
                        "allowed": True
                    }
                else:
                    return {
                        "email": row["이메일"],
                        "grade": int(row["등급 (1,2,3)"]),
                        "allowed": False
                    }

        return None
    except Exception as e:
        print("❌ 시트 인증 오류:", e)
        return None

def is_authorized_email(email):
    user = get_user_info(email)
    return user is not None and user["allowed"]
