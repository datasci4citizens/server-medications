from datetime import date

def parse_date(birthday_str: str | None) -> date | None:
    if birthday_str:
        return date.fromisoformat(birthday_str)
    return None