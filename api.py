from datetime import datetime, timedelta


def errors_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)

        except ValueError:
            print(
                f"Parameters is not correct... Invalid date format. Use DD.MM.YYYY ")

    return wrapper


def normalize_users_date(users_list, today=datetime.today()):

    return [{"name": user.name, "birthday": user.birthday.value.date()
    .replace(year=today.year)} for user in users_list if user.birthday]


def modified_users_date(date):

    if date.weekday() in {5, 6}:
        return date + timedelta(days=7 - date.weekday())
    return date


def get_upcoming_birthdays(users_list: list) -> list:
    today = datetime.today()
    normalized_users = normalize_users_date(users_list)
    delta_max_period = today.date() + timedelta(days=7)
    delta_min_period = today.date() - timedelta(days=7)
    return [{"name": user['name'], "congratulation_date": modified_users_date(user['birthday']).strftime("%d.%m.%Y")}
            for user in normalized_users if delta_min_period <= user['birthday'] <= delta_max_period]


def command_parser(input_str: str):
    try:
        command, *args = input_str.lower().split()
        return command, *args
    except (TypeError, ValueError):
        print("Command is empty string...Try again!")


def help_api():
    return (
        "Available commands: \n"
        "- hello\n"
        "- add <name> <number>\n"
        "- find <name>\n"
        "- birthdays\n"
        "- show_birthday <name> \n"
        "- add_birthday <name> <date> \n"
        "- update <name> <old_number> <new_number>\n"
        "- delete <name>\n"
        "- all (saw all contacts)\n"
        "- help\n"
        "- exit\n"
    )

