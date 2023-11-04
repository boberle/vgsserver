import getpass

import typer

from users import UserData, hash_password

app = typer.Typer(add_completion=False)


@app.command()
def make_user(
    username: str = typer.Option(..., help="the username"),
) -> None:
    p1 = getpass.getpass("Enter the password: ")
    p2 = getpass.getpass("Repeat the password: ")
    if p1 != p2:
        print("The password are different. Aborting")
    password = p1.encode()
    password_hash = hash_password(password)
    user_data = UserData(
        username=username.encode(),
        password_hash=password_hash,
    )
    print(user_data.model_dump_json(indent=2))


@app.callback()
def callback() -> None:
    """To make it ask a command if there is only one.

    See: "https://typer.tiangolo.com/tutorial/commands/one-or-multiple/
    """


if __name__ == "__main__":
    app()
