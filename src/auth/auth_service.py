from fastapi import HTTPException, Request

class AuthService:
    @staticmethod
    def get_current_user(request: Request):
        if not request.session or request.session.get("email") is None:
            raise HTTPException(status_code=401, detail="User not authenticated")
        return request.session.get("email")