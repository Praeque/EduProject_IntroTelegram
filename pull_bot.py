from error_taker import save_error


def pulling_bot():
    while True:
        try:
            import bot_rent_apartment
        except Exception as error:
            save_error(error)


if __name__ == '__main__':
    pulling_bot()
