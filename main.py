import logging
import os
import pprint

from typedconf import AppConfig, ConfigModel, Field, ValidationError


# 1. Configure logging to see debug messages from the typedconf framework
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# 2. Define a custom configuration schema
# This demonstrates how a user would add their own specific settings.
class UserProfile(ConfigModel):
    """User profile configuration."""
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    role: str = Field(default="user", description="User role")


class CustomAppConfig(AppConfig):
    """
    Custom application config that extends the base AppConfig.
    It adds a new 'profile' section to the configuration.
    """
    profile: UserProfile = Field(..., description="User profile information")


def main():
    """
    An example of how to use the typedconf framework.
    """
    print("--- Running typedconf example ---")

    # 3. Set the environment for the application.
    # The framework will automatically look for a 'config.{APP_ENV}.toml' file.
    # Here, we set it to 'production' to demonstrate loading 'config.production.toml'.
    os.environ["APP_ENV"] = "production"
    print(f"\nSet APP_ENV to: '{os.environ['APP_ENV']}'\n")

    try:
        # 4. Instantiate the configuration class.
        # typedconf will now load and merge the files and environment variables.
        config = CustomAppConfig()

        # 5. Print the resulting configuration.
        # The output will show that 'app_name' and 'model.top_p' are from
        # 'config.production.toml', while other values are from 'config.default.toml'.
        print("\n--- Final Configuration ---")
        pprint.pprint(config.model_dump())
        print("---------------------------\n")

        print(f"Successfully loaded configuration for app: '{config.app_name}'")
        print(f"Model ID: {config.model.id}")
        print(f"Model Top P: {config.model.top_p}")
        print(f"User: {config.profile.name} ({config.profile.email})")
        print(f"Role: {config.profile.role}")

    except ValidationError as e:
        logging.error(f"Configuration validation failed!\n{e}")

    # 6. Demonstrate switching the environment
    os.environ["APP_ENV"] = "development"
    print(f"\nSwitched APP_ENV to: '{os.environ['APP_ENV']}'\n")
    try:
        config = CustomAppConfig()
        print("\n--- Final Configuration (Development) ---")
        pprint.pprint(config.model_dump())
        print("-----------------------------------------\n")
        print(f"Successfully loaded configuration for app: '{config.app_name}'")
        print(f"Model Top P: {config.model.top_p}")

    except ValidationError as e:
        logging.error(f"Configuration validation failed!\n{e}")


if __name__ == "__main__":
    main()
