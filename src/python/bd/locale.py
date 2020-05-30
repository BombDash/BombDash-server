def get_locale(key):
    return current_locale.get(key)


current_locale = {
        # category: texts
        'aggressive_text':
        'AGGRESSIVE!',
        'bomb_names_text':
        '=============== Названия бомб ===============',
        'crazy_text':
        'CRAZY!!',
        'dividing_strip_text':
        '=============================================',
        'elon_mine_defused_text':
        'Мина Илона Маска обезврежена!',
        'fatality_text':
        'FATALITY!!!',
        'first_blood_text':
        'FIRST BLOOD!',
        'player_ids_text':
        '========== Идентификаторы игроков ==========',
        'player_profiles_text':
        '============== Профили игрока ==============',
        'powerup_names_text':
        '============= Названия бонусов =============',
        'skin_names_text':
        '============ Названия персонажей ============',
        'you_are_banned_text':
        'Вы забанены на наших серверах.',
        'team_warn':
        'Предупреждение для ${name}: тим запрещен и карается баном',
        'kickvote_start':
        'Начато голосование за вылет ${name}.',
        'kickvote_type':
        "Наберите '1' для согласия или '0' для отказа",
        'kickvote_needed_num':
        'Нужно ${n} голосов',
        # category: errors
        'chat_command_not_args_error':
        ('Ошибка: нет или не хватает аргументов '
         'для этой чат-команды.'),
        'database_error':
        'Ошибка: база данных не отвечает.',
        'init_glowing_code_error':
        'Ошибка: неправильный код подсветки.',
        'kick_host_error':
        'Ошибка: нельзя выгнать сам сервер.',
        'not_player_error':
        'Ошибка: игрока с таким ID нет на сервере.',
        'permission_effect_error': ('Ошибка: неправильные данные эффектов, '
                                    'установлены стандартные.'),
        'time_arg_access_error': ('Ошибка: аргумент времени '
                                  'доступен только админам.'),
        # category: arrays
        'ad':
        ('На нашем сайте много полезного - bombdash.net',
         'Подписывайтесь на наше сообщество ВКонтакте - @bombdash'),
        'arg_bomb_options':
        ('> Стандартные бомбы:', 'ice - Ледяная', 'impact - Ударная',
         'landMine - Мина', 'normal - Обычная', 'sticky - Липучка',
         'tnt - TNT', '> Бомбы BombDash:', 'airstrike - Авиаудар',
         'elonMine - Мина Илона Маска'
         'heal - Лечебная', 'holy - Святая', 'portal - Портальная',
         'stickyGift - Липучий привет'),
        'arg_powerup_options':
        ('> Стандартные бонусы:', 'curse - Проклятие', 'health - Аптечка',
         'iceBombs - Ледяные бомбы', 'impactBombs - Ударные бомбы',
         'landMines - Мины', 'punch - Боксерские перчатки',
         'shield - Энергетический щит', 'stickyBombs - Бомбы-липучки',
         'tripleBombs - Тройные бомбы', '> Бонусы BombDash:',
         'airstrikeBombs - Авиаудар', 'cubeCompanion - Куб-компаньон',
         'elonMines - Мина Илона Маска', 'healBombs - Лечебная бомба'
         'highJump - Высокий прыжок', 'holyBombs - Святая бомба',
         'luckyBlock - Блок удачи', 'portalBombs - Портальная бомба',
         'speed - Ускорение', 'stickyGiftBombs - Липучий привет'),
        'cube_companion_phrases':
        ('Если жизнь дает тебе лимоны,\nне делай лимонад'
         'Как твои дела?', 'Не забывай меня', 'Привет',
         'Теперь ты меня слышишь', 'Торт - это ложь', 'Я жив', 'Я тебя люблю'),
        'powerup_names': {
            'airstrike_bombs': 'Авиаудар',
            'companion_cube': 'Куб-компаньон',
            'curse': 'Проклятие',
            'elon_mines': 'Мина Илона Маска',
            'heal_bombs': 'Лечебная бомба',
            'health': 'Аптечка',
            'jetpack': 'Jet-пак',
            'holy_bombs': 'Святая бомба',
            'ice_bombs': 'Ледяные бомбы',
            'impact_bombs': 'Ударные бомбы',
            'land_mines': 'Мины',
            'lucky_block': 'Блок удачи',
            'portal_bombs': 'Портальная бомба',
            'punch': 'Боксерские перчатки',
            'shield': 'Энергетический щит',
            'speed': 'Ускорение',
            'sticky_bombs': 'Бомбы-липучки',
            'sticky_gift_bombs': 'Липучий привет',
            'triple_bombs': 'Тройные бомбы'
        },
        'skin_names':
        ('agent - Агент Джонсон', 'ali - Талисман Таобао', 'bear - Бернард',
         'bones - Костяшка', 'bunny - Пасхальный кролик', 'cyborg - B-9000',
         'frosty - Снежный', 'jack - Джек Морган', 'kronk - Санта Клаус',
         'mel - Мэл', 'ninja - Тень Змеи', 'penguin - Паскаль',
         'pixel - Пиксель', 'random - Скин из случайных частей тела',
         'santa - Санта Клаус', 'spaz - Спаз', 'spazAngel - Спаз-ангел',
         'wizard - Грамблдорф', 'zoe - Зои', 'zombie - Зомби')
    }