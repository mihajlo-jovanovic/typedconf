from pydantic import ValidationError

from typedconf.user_config import AppConfig


def main():
    print("Hello from typedconf!")

    try:
        config = AppConfig()
        print(f"Running app: {config.app_name}")
        print(f"Model name: {config.model.id}")
    except ValidationError as e:
        print(f"Error: Configuration validation failed!\n{e}")


if __name__ == "__main__":
    main()
