# members/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URLs para socios
    path('', views.socio_list, name='socio_list'),
    path('socios/', views.socio_list, name='socio_list'),
    path('socio/<int:pk>/', views.socio_detail, name='socio_detail'),
    path('socio/new/', views.socio_new, name='socio_new'),
    path('socio/<int:pk>/edit/', views.socio_edit, name='socio_edit'),
    path('socio/<int:pk>/delete/', views.socio_delete, name='socio_delete'),
    
    # URLs para pagos
    path('pagos/', views.pago_list, name='pago_list'),
    path('pago/<int:pk>/', views.pago_detail, name='pago_detail'),
    path('pago/new/', views.pago_new, name='pago_new'),
    path('pago/<int:pk>/edit/', views.pago_edit, name='pago_edit'),
    path('pago/<int:pk>/delete/', views.pago_delete, name='pago_delete'),
    path('pago/<int:pk>/delete/', views.pago_delete, name='pago_delete'),
    path('pago/<int:pk>/delete/confirm/', views.pago_delete_confirmation, name='pago_delete_confirmation'),
    path('socio/<int:pk>/delete/error/', views.socio_delete_error, name='socio_delete_error'),

    # URLs para reportes
    path('ingresos-mensuales/', views.ingresos_mensuales, name='ingresos_mensuales'),
    path('pagos-atrasados/', views.pagos_atrasados, name='pagos_atrasados'),
    path('ingresos_mensuales/', views.ingresos_mensuales_view, name='ingresos_mensuales'),
    path('informe-metodo-pago/', views.informe_metodo_pago, name='informe_metodo_pago'),
    path('informes/', views.generar_informe_excel, name='generar_informe_excel'),
    
    #URLs para ingreso  
    path('verificar-estado-entrada/<int:id_socio>/', views.verificar_estado_entrada, name='verificar_estado_entrada'),
]
