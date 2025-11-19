from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import TemperatureReading
from .serializers import TemperatureReadingSerializer


class TemperatureViewSet(viewsets.ModelViewSet):
    queryset = TemperatureReading.objects.all()
    serializer_class = TemperatureReadingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(device=self.request.user)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        reading = TemperatureReading.objects.first()
        if reading:
            serializer = self.get_serializer(reading)
            return Response(serializer.data)
        return Response({'error': 'Brak danych'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def average(self, request):
        readings = TemperatureReading.objects.all()
        if readings.exists():
            avg = sum(r.temperature for r in readings) / len(readings)
            return Response({'average_temperature': round(avg, 2)})
        return Response({'average_temperature': 0})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        readings = TemperatureReading.objects.all()[:100]
        if readings.exists():
            temps = [r.temperature for r in readings]
            return Response({
                'min': min(temps),
                'max': max(temps),
                'avg': round(sum(temps) / len(temps), 2),
                'count': len(temps)
            })
        return Response({'error': 'Brak danych'}, status=status.HTTP_404_NOT_FOUND)



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error = 'Nieprawidłowy login lub hasło'
        else:
            error = 'Proszę wypełnić wszystkie pola'
    
    return render(request, 'login.html', {'error': error})


@login_required(login_url='/')
def dashboard_view(request):
    return render(request, 'dashboard.html', {'user': request.user})


def logout_view(request):
    logout(request)
    return redirect('home')
