from pathlib import Path


def main():
    import dorm

    dorm.setup(settings_dir=Path(__file__).parent.parent.resolve())
    dorm.ensure_setup()

    print("dorm setup is done.")


if __name__ == "__main__":
    main()
