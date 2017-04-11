from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update/', views.update, name='update'),
    url(r'^monitor/', views.monitor, name='monitor'),
    url(r'^getbuildorder/', views.get_build_order, name='getbuildorder'),
    url(r'^getbuildorderids/', views.get_build_order_ids, name='getbuildorderids'),
    url(r'^nextbuild/', views.next_build, name='nextbuild'),
    url(r'^probe/', views.probe, name='probe'),
    url(r'^unit_history/', views.unit_history, name='unit_history'),
    url(r'^history/', views.fitness_history, name='fitness_history'),
    url(r'^pop_history/', views.pop_history, name='pop_history'),
    url(r'^update_history/', views.update_history, name='update_history'),
    url(r'^timing/', views.timing, name='timing')
]