from setuptools import setup, find_packages


setup(
    name='hotel_business_module',
    version='1.0',
    packages=find_packages(),
    description='Бизнес логика для работы с отелем',
    install_requires=[
        'bcrypt==4.0.1',
        'greenlet==2.0.2',
        'psycopg2==2.9.6',
        'PyJWT==2.6.0',
        'pytz==2023.3',
        'SQLAlchemy==2.0.9',
        'typing_extensions==4.5.0',
        'aiofiles==23.1.0',
        'types-aiofiles==23.1.0.1',
        'python-dotenv==1.0.0',
        'coverage==7.2.4',
    ],
)
