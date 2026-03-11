from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("adicionar/", views.adicionar_medicao, name="adicionar_medicao"),
    path("historico/", views.historico, name="historico"),
    path("editar/<int:medicao_id>/", views.editar_medicao, name="editar_medicao"),
    path("excluir/<int:medicao_id>/", views.excluir_medicao, name="excluir_medicao"),
    path("editar-perfil/", views.editar_perfil, name="editar_perfil"),
    path("trocar-senha/", views.trocar_senha, name="trocar_senha"),
    path("admin/", views.admin_view, name="admin"),
    path("admin/aprovar/<int:user_id>/", views.aprovar_usuario, name="aprovar_usuario"),
    path("admin/rejeitar/<int:user_id>/", views.rejeitar_usuario, name="rejeitar_usuario"),
]
