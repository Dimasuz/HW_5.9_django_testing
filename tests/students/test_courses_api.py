# def test_example():
#     assert False, "Just test example"


import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student


# фикстура для api-client'а
@pytest.fixture
def client():
    return APIClient()

# фикстура для фабрики курсов
@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        # return baker.make(Course, make_m2m=True, *args, **kwargs)
        return baker.make(Course, *args, **kwargs)
    return factory

# фикстура для фабрики студентов
@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory

#фикстура максимального количества студентов
@pytest.fixture
def max_student_in_settings(settings):
    return settings.MAX_STUDENTS_PER_COURSE

# проверка получения одного курса (retrieve-логика)
# создаем курс через фабрику
# строим урл и делаем запрос через тестовый клиент
# проверяем, что вернулся именно тот курс, который запрашивали
@pytest.mark.django_db
def test_get_firstcourse(client, courses_factory):

    # Arrange
    courses = courses_factory()
    url = f'/api/v1/courses/{courses.id}/'

    # Act
    response = client.get(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data['id'] == courses.id


# проверка получения списка курсов (list-логика)
# аналогично – сначала вызываем фабрики, затем делаем запрос и проверяем результат
@pytest.mark.django_db
def test_get_list(client, courses_factory):

    # Arrange
    courses = courses_factory(_quantity=5)
    url = '/api/v1/courses/'

    # Act
    response = client.get(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == len(courses)
    for i, m in enumerate(data):
        assert m['name'] == courses[i].name


# проверка фильтрации списка курсов по id
# создаем курсы через фабрику, передать id одного курса в фильтр, проверить результат запроса с фильтром
@pytest.mark.django_db
def test_get_filtr_id(client, courses_factory):

    # Arrange
    courses = courses_factory(_quantity=5)
    url = '/api/v1/courses/'
    data = {'id': courses[0].id}

    # Act
    response = client.get(url, data=data)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['name'] == courses[0].name


# проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_get_filtr_name(client, courses_factory):
    # Arrange
    courses = courses_factory(_quantity=5)
    url = '/api/v1/courses/'
    data = {'name': courses[1].name}

    # Act
    response = client.get(url, data=data)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['id'] == courses[1].id


#тест успешного создания курса
#здесь фабрика не нужна, готовим JSON-данные и создаем курс
@pytest.mark.django_db
def test_create_course(client, students_factory):
    # Arrange
    count = Course.objects.count()
    students = students_factory()
    url = '/api/v1/courses/'
    data = {'name': 'test_name_course', 'students': [students.id]}

    # Act
    response = client.post(url, data=data)

    # Assert
    assert response.status_code == 201
    assert Course.objects.count() == count + 1


# тест успешного обновления курса
# сначала через фабрику создаем, потом обновляем JSON-данными
@pytest.mark.django_db
def test_update_course(client, courses_factory, students_factory):
    # Arrange
    courses = courses_factory()
    students = students_factory(_quantity=5)
    name = courses.name + 'test'

    # Act
    url = f'/api/v1/courses/{courses.id}/'
    students_list = [students[2].id, students[0].id, students[1].id, students[4].id]
    data = {'name': name, 'students': students_list,}
    resp = client.put(url, data=data)
    url = '/api/v1/courses/'
    data = {'id': courses.id}
    response = client.get(url, data=data)
    data = response.json()

    # Assert
    assert resp.status_code == 200
    assert response.status_code == 200
    assert data[0]['name'] == name
    assert data[0]['id'] == courses.id
    assert set(data[0]['students']) == set(students_list)


# тест успешного удаления курса
@pytest.mark.django_db
def test_delete_course(client, courses_factory):
    # Arrange
    courses = courses_factory()
    count = Course.objects.count()

    # Act
    url = f'/api/v1/courses/{courses.id}/'
    response = client.delete(url)
    resp = client.get(url)

    # Assert
    assert response.status_code == 204
    assert Course.objects.count() == count - 1
    assert resp.status_code == 404

# дополниетльное задание

# тест обновления курса с ограничением по количеству студентов
@pytest.mark.django_db
@pytest.mark.parametrize("num_student,status",[(-1, 200), (1, 400)],)
def test_update_course_maxstudent(client, max_student_in_settings, courses_factory, students_factory, num_student, status):
    # Arrange
    num_student += max_student_in_settings
    courses = courses_factory()
    students = students_factory(_quantity=num_student)
    # name = courses.name + 'test'

    # Act
    url = f'/api/v1/courses/{courses.id}/'
    students_list = [students[i].id for i in range(num_student)]
    data = {'name': courses.name, 'students': students_list,}
    resp = client.put(url, data=data)

    # Assert
    assert resp.status_code == status


#тест создания курса с ограничением по количеству студентов на курсе
@pytest.mark.django_db
@pytest.mark.parametrize("num_student,status,added",[(-1, 201, 1), (1, 400, 0)],)
def test_create_course_maxstudent(client, max_student_in_settings, students_factory, num_student, status, added):
    # Arrange
    num_student += max_student_in_settings
    count = Course.objects.count()
    students = students_factory(_quantity=num_student)
    students_list = [students[i].id for i in range(num_student)]
    url = '/api/v1/courses/'
    data = {'name': 'test_name_course', 'students': students_list,}

    # Act
    response = client.post(url, data=data)

    # Assert
    assert response.status_code == status
    assert Course.objects.count() == count + added



