import pickle
from collections import UserDict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from api import errors_handler, get_upcoming_birthdays, help_api, command_parser


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.value}"


class Birthday(Field):
    def __init__(self, value):
        if not self.is_valid_date_format(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        self.value = datetime.strptime(value, "%d.%m.%Y")

    def is_valid_date_format(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    def __repr__(self):
        return f'{self.value.strftime("%d.%m.%Y")}'


class Name(Field): ...


class Phone(Field): ...


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    @errors_handler
    def add_birthday(self, value):
        self.birthday = Birthday(value)

    @errors_handler
    def show_birthday(self):
        if not self.birthday:
            return print(f'Error')
        return print(f'{self.name.value} have birthday: {self.birthday.value.strftime("%d.%m.%Y")}')

    @staticmethod
    def phone_is_exist(data, phone):
        for p in data:
            if p.value == phone:
                return True

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return f"Phone {old_phone} edited to {new_phone}"
        else:
            return f"Phone {old_phone} is not exist!"

    def add_phone(self, phone):
        if self.phone_is_exist(self.phones, phone):
            return print("This number already exist")

        self.phones.append(Phone(phone))

    def __str__(self):
        if self.birthday:
            return f"Contact name: {self.name.value} \nPhones: {'; '.join(p.value for p in self.phones)}\nBirthday: {self.birthday.value.strftime("%d.%m.%Y")}\n"

        return f"Contact name: {self.name.value} \nPhones: {'; '.join(p.value for p in self.phones)}\nBirthday: {self.birthday}\n"


class AddressBook(UserDict):
    @errors_handler
    def birthdays(self):
        data = list(self.data.values())
        upcoming_birthdays = get_upcoming_birthdays(data)
        if len(upcoming_birthdays):
            return upcoming_birthdays
        else:
            return "No users with upcoming birthdays"

    def add_record(self, record):
        self.data[record.name] = record

    def find_record(self, target):
        for i in self.data.values():
            if i.name.value.lower() == target.lower():
                return i

    def show(self):
        if len(self.data) == 0:
            return "No data exist!"
        for record in self.data.values():
            return record

    def remove(self, target):
        for record in list(self.data.keys()):
            if record.value == target:
                del self.data[record]
                return f"User {target} has been deleted!"


class UserInterface(ABC):
    @abstractmethod
    def show_message(self, message):
        pass


class CLIUserInterface(UserInterface):
    def show_message(self,message):
        print(message)


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    cli = CLIUserInterface()
    exit_commands = ["q", "quit", "exit", "leave", "left"]
    cli.show_message('Welcome to assistant bot! You can use "help" command to see more')

    while True:
        params = input(">>>  ")
        if not params:
            cli.show_message("Please, enter not empty string! ")
            continue

        command, *args = command_parser(params)
        if len(args) != 0:
            name = args[0]

        match (command):
            case "hello" | "start":
                cli.show_message("Welcome to CLI assistant 🔥")

            case "add" | "create":
                if len(args) < 2:
                    cli.show_message("Please enter, correct args. Example: 'add Oleh 0932244555'")
                    continue
                new_contact = Record(name)
                exist_record = book.find_record(name)
                if exist_record:
                    exist_record.add_phone(args[1])
                else:
                    new_contact.add_phone(args[1])
                    book.add_record(new_contact)

            case "find" | "get":
                exist = book.find_record(name)
                cli.show_message(exist)

            case "birthdays" | "b":
                cli.show_message(book.birthdays())

            case "show_birthday":
                if len(args) < 1:
                    cli.show_message("Please enter, correct args. Example: 'show_birthday Oleh'")
                    continue
                exist_record = book.find_record(name)
                if exist_record:
                    exist_record.show_birthday()
                else:
                    cli.show_message("User is not exist")

            case "add_birthday":
                if len(args) < 2:
                    cli.show_message(
                        "Please enter, correct args. Example: 'add_birthday Oleh 22.03.2024'"
                    )
                    continue
                exist_record = book.find_record(name)
                if exist_record:
                    exist_record.add_birthday(args[1])
                else:
                    cli.show_message(
                        "User is not exist. Please, add user first. Example: 'add_birthday Oleh 22.03.2024'"
                    )

            case "update":
                if len(args) < 3:
                    cli.show_message(
                        "Please enter, correct args. Example: 'update Oleh 0932244555 05012345678'"
                    )
                    continue
                exist = book.find_record(name)
                if exist:
                    exist.edit_phone(args[1], args[2])
                else:
                    cli.show_message(f'User "{name}" is not found')

            case "delete" | "del":
                book.remove(name)

            case "all" | "show":
                cli.show_message(book.show())

            case "help" | "info":
                cli.show_message(help_api())

            case command if command in exit_commands:
                save_data(book)
                cli.show_message("Bye!")
                break
            case _:
                cli.show_message("Invalid command! Try again...\n")


if __name__ == "__main__":
    main()
