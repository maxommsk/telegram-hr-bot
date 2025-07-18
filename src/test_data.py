from main import app
from user import db, User
from job import Job
from application import Application
from subscription import Subscription

with app.app_context():
    # Создание тестового работодателя
    employer = User(
        telegram_id=123456789,
        username='test_employer',
        first_name='Тест',
        last_name='Работодатель',
        user_type='employer',
        is_active=True
    )
    db.session.add(employer)
    db.session.flush()  # Получаем ID работодателя

    # Создание тестового пользователя-соискателя
    candidate = User(
        telegram_id=987654321,
        username='test_candidate',
        first_name='Тест',
        last_name='Соискатель',
        user_type='jobseeker',
        is_active=True
    )
    db.session.add(candidate)

    # Создание тестовой вакансии
    job = Job(
        title='Python разработчик',
        description='Требуется опытный Python разработчик для работы над интересными проектами.',
        company='ТестКомпания',
        location='Москва',
        salary_min=100000,
        salary_max=150000,
        employment_type='full-time',
        experience_level='middle',
        skills_required='Python, Flask, PostgreSQL',
        employer_id=employer.id,  # ИСПОЛЬЗУЕМ РЕАЛЬНЫЙ ID!
        is_active=True
    )
    db.session.add(job)

    db.session.commit()
    print('Test data created successfully!')
