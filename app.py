import logging

from aiogram.utils import executor

from loader import dp


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


if __name__ == "__main__": # ФАЙЛ ЗАПУСКА. ДЛЯ ЗАПУСКА БОТА НУЖНО ЗАПУСТИТЬ ЭТОТ ФАЙЛ.
    import poster
    executor.start_polling(dispatcher=dp)
