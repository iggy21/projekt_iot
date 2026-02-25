## Monitor Temperatury (Django)

Aplikacja webowa do monitorowania temperatury i wilgotności z czujnika IoT.  
Zaimplementowałam logowanie użytkownika, prosty dashboard z bieżącymi danymi oraz REST API do obsługi odczytów.

**Technologie:** Django, Django REST Framework, SQLite, HTML/CSS.

**Funkcje:**
- Logowanie i ochrona dostępu do panelu.
- Dashboard z aktualną temperaturą, średnią, podstawowymi statystykami i listą ostatnich odczytów.
- REST API (CRUD + endpointy `/latest`, `/average`, `/statistics`).
- Panel admina do podglądu i usuwania danych.
- Testy jednostkowe modeli, widoków, API i serializera (`python manage.py test`).

