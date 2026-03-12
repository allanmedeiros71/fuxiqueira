import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User as CustomUser

from .forms import MeasurementForm
from .models import Measurement


def is_admin(user):
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_view(request):
    # Estatísticas
    total_usuarios = CustomUser.objects.count()
    usuarios_ativos = CustomUser.objects.filter(is_active=True).count()
    usuarios_pendentes = CustomUser.objects.filter(is_active=False).count()

    # Listas
    usuarios_pendentes_list = CustomUser.objects.filter(is_active=False).order_by("-date_joined")
    todos_usuarios = CustomUser.objects.all().order_by("-date_joined")

    context = {
        "total_usuarios": total_usuarios,
        "usuarios_ativos": usuarios_ativos,
        "usuarios_pendentes": usuarios_pendentes,
        "usuarios_pendentes_list": usuarios_pendentes_list,
        "todos_usuarios": todos_usuarios,
    }

    return render(request, "measurements/admin.html", context)


@login_required
@user_passes_test(is_admin)
def aprovar_usuario(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"Usuário {user.username} aprovado com sucesso!")
    return redirect("admin")


@login_required
@user_passes_test(is_admin)
def rejeitar_usuario(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f"Usuário {username} rejeitado e removido do sistema!")
    return redirect("admin")


@login_required
def dashboard(request):
    user = request.user

    # Última medição
    ultima_medicao = user.medicoes.first()
    
    # Primeira medição (para galeria antes/depois)
    primeira_medicao = user.medicoes.last() if user.medicoes.count() > 1 else None

    # Medição anterior (para comparação)
    medicao_anterior = None
    comparacoes = {}

    if ultima_medicao:
        medicao_anterior = user.medicoes.filter(data_hora__lt=ultima_medicao.data_hora).first()

        if medicao_anterior:
            # Calcular diferenças
            comparacoes = {
                "peso_diff": float(ultima_medicao.peso) - float(medicao_anterior.peso),
                "gordura_diff": float(ultima_medicao.percentual_gordura) - float(medicao_anterior.percentual_gordura),
                "massa_muscular_diff": float(ultima_medicao.percentual_massa_muscular) - float(medicao_anterior.percentual_massa_muscular),
                "metabolismo_diff": ultima_medicao.metabolismo_basal - medicao_anterior.metabolismo_basal,
            }

    # Últimas 30 medições para o gráfico (em ordem cronológica)
    ultimas_medicoes = list(user.medicoes.order_by("data_hora")[:30])

    # Preparar dados para o gráfico
    chart_data = {
        "labels": [m.data_hora.strftime("%d/%m/%Y") for m in ultimas_medicoes],
        "peso": [float(m.peso) for m in ultimas_medicoes],
        "imc": [float(m.imc) for m in ultimas_medicoes],
        "percentual_gordura": [float(m.percentual_gordura) for m in ultimas_medicoes],
        "percentual_massa_muscular": [float(m.percentual_massa_muscular) for m in ultimas_medicoes],
        "metabolismo_basal": [m.metabolismo_basal for m in ultimas_medicoes],
        "idade_metabolica": [m.idade_metabolica for m in ultimas_medicoes],
        "indice_gordura_visceral": [float(m.indice_gordura_visceral) for m in ultimas_medicoes],
    }

    # Interpretações médicas/nutricionais
    interpretacoes = {}
    if ultima_medicao:
        interpretacoes = get_interpretacoes(ultima_medicao)

    context = {
        "ultima_medicao": ultima_medicao,
        "primeira_medicao": primeira_medicao,
        "medicao_anterior": medicao_anterior,
        "comparacoes": comparacoes,
        "chart_data": json.dumps(chart_data),
        "interpretacoes": interpretacoes,
    }

    return render(request, "measurements/dashboard.html", context)


def get_interpretacoes(medicao):
    """Retorna interpretações médicas/nutricionais para cada indicador"""
    interpretacoes = {}

    # IMC
    imc = float(medicao.imc)
    if imc < 18.5:
        interpretacoes["imc"] = {"status": "Abaixo do peso", "cor": "text-blue-600", "descricao": "Seu IMC indica que você está abaixo do peso ideal. Considere aumentar a ingestão calórica com alimentos nutritivos."}
    elif imc < 25:
        interpretacoes["imc"] = {"status": "Peso normal", "cor": "text-green-600", "descricao": "Parabéns! Seu IMC está na faixa considerada saudável. Mantenha seus hábitos atuais."}
    elif imc < 30:
        interpretacoes["imc"] = {"status": "Sobrepeso", "cor": "text-yellow-600", "descricao": "Seu IMC indica sobrepeso. Considere uma dieta equilibrada e aumento da atividade física."}
    else:
        interpretacoes["imc"] = {"status": "Obesidade", "cor": "text-red-600", "descricao": "Seu IMC indica obesidade. É recomendado buscar orientação médica e nutricional para um plano de emagrecimento saudável."}

    # Percentual de Gordura
    gordura = float(medicao.percentual_gordura)
    if gordura < 6:
        interpretacoes["gordura"] = {"status": "Essencial", "cor": "text-blue-600", "descricao": "Percentual de gordura essencial. Aumente ligeiramente para níveis mais saudáveis."}
    elif gordura < 14:
        interpretacoes["gordura"] = {"status": "Atleta", "cor": "text-green-600", "descricao": "Percentual de gordura de atleta. Excelente nível!"}
    elif gordura < 18:
        interpretacoes["gordura"] = {"status": "Fitness", "cor": "text-green-600", "descricao": "Percentual de gordura de fitness. Ótimo para saúde e estética."}
    elif gordura < 25:
        interpretacoes["gordura"] = {"status": "Aceitável", "cor": "text-yellow-600", "descricao": "Percentual aceitável, mas poderia ser melhorado com dieta e exercícios."}
    else:
        interpretacoes["gordura"] = {"status": "Excesso", "cor": "text-red-600", "descricao": "Percentual de gordura elevado. Recomendado programa de emagrecimento."}

    # Massa Muscular
    massa = float(medicao.percentual_massa_muscular)
    if massa < 30:
        interpretacoes["massa"] = {"status": "Baixa", "cor": "text-red-600", "descricao": "Massa muscular baixa. Considere treinamento de resistência para aumentar."}
    elif massa < 35:
        interpretacoes["massa"] = {"status": "Moderada", "cor": "text-yellow-600", "descricao": "Massa muscular moderada. Espaço para melhoria com treinos adequados."}
    elif massa < 45:
        interpretacoes["massa"] = {"status": "Boa", "cor": "text-green-600", "descricao": "Boa massa muscular. Continue com seus treinos atuais."}
    else:
        interpretacoes["massa"] = {"status": "Excelente", "cor": "text-green-600", "descricao": "Massa muscular excelente! Ótimo trabalho."}

    # Idade Metabólica
    idade_meta = medicao.idade_metabolica
    idade_cronologica = (timezone.now().date() - medicao.usuario.data_nascimento).days // 365

    if idade_meta < idade_cronologica - 5:
        interpretacoes["idade_meta"] = {"status": "Excelente", "cor": "text-green-600", "descricao": f"Sua idade metabólica ({idade_meta} anos) é muito menor que sua idade cronológica. Parabéns!"}
    elif idade_meta < idade_cronologica:
        interpretacoes["idade_meta"] = {"status": "Boa", "cor": "text-green-600", "descricao": f"Sua idade metabólica ({idade_meta} anos) é menor que sua idade cronológica. Continue assim!"}
    elif idade_meta == idade_cronologica:
        interpretacoes["idade_meta"] = {"status": "Normal", "cor": "text-yellow-600", "descricao": f"Sua idade metabólica ({idade_meta} anos) é igual à sua idade cronológica. Há espaço para melhoria."}
    else:
        interpretacoes["idade_meta"] = {"status": "Atenção", "cor": "text-red-600", "descricao": f"Sua idade metabólica ({idade_meta} anos) é maior que sua idade cronológica. Considere mudanças no estilo de vida."}

    # Gordura Visceral
    visceral = float(medicao.indice_gordura_visceral)
    if visceral < 10:
        interpretacoes["visceral"] = {"status": "Normal", "cor": "text-green-600", "descricao": "Nível normal de gordura visceral. Continue mantendo hábitos saudáveis."}
    elif visceral < 15:
        interpretacoes["visceral"] = {"status": "Moderado", "cor": "text-yellow-600", "descricao": "Nível moderado de gordura visceral. Considere reduzir açúcares e aumentar atividade física."}
    else:
        interpretacoes["visceral"] = {"status": "Alto", "cor": "text-red-600", "descricao": "Nível elevado de gordura visceral. Fator de risco para doenças cardiovasculares. Busque orientação médica."}

    return interpretacoes


@login_required
def editar_perfil(request):
    from accounts.forms import UserProfileForm

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect("dashboard")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "measurements/editar_perfil.html", {"form": form})


@login_required
def trocar_senha(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Senha alterada com sucesso! Faça login novamente.")
            return redirect("login")
        else:
            messages.error(request, "Erro ao alterar senha. Verifique os dados.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "measurements/trocar_senha.html", {"form": form})


@login_required
def adicionar_medicao(request):
    if request.method == "POST":
        form = MeasurementForm(request.POST)
        if form.is_valid():
            medicao = form.save(commit=False)
            medicao.usuario = request.user

            # Calcular IMC se não fornecido
            if not medicao.imc and request.user.altura:
                medicao.imc = round(float(medicao.peso) / (float(request.user.altura) ** 2), 2)

            medicao.save()
            messages.success(request, "Medição adicionada com sucesso!")

            if request.headers.get("HX-Request"):
                return JsonResponse({"success": True})
            return redirect("dashboard")
    else:
        form = MeasurementForm()

    return render(request, "measurements/adicionar_medicao.html", {"form": form})


@login_required
def editar_medicao(request, medicao_id):
    medicao = get_object_or_404(Measurement, id=medicao_id, usuario=request.user)

    if request.method == "POST":
        form = MeasurementForm(request.POST, instance=medicao)
        if form.is_valid():
            medicao = form.save(commit=False)

            # Calcular IMC se não fornecido
            if not medicao.imc and request.user.altura:
                medicao.imc = round(float(medicao.peso) / (float(request.user.altura) ** 2), 2)

            medicao.save()
            messages.success(request, "Medição atualizada com sucesso!")

            if request.headers.get("HX-Request"):
                return JsonResponse({"success": True})
            return redirect("historico")
    else:
        # Formatar data_hora para o formato datetime-local
        form = MeasurementForm(instance=medicao)
        data_hora_formatada = ""
        # Converter datetime para formato esperado pelo input datetime-local
        if medicao.data_hora:
            # Garantir que estamos usando timezone local
            from django.utils import timezone

            local_time = timezone.localtime(medicao.data_hora)
            data_hora_formatada = local_time.strftime("%Y-%m-%dT%H:%M")
            form.fields["data_hora"].widget.attrs["value"] = data_hora_formatada

    return render(request, "measurements/editar_medicao.html", {"form": form, "medicao": medicao, "data_hora_formatada": data_hora_formatada})


@login_required
def historico(request):
    medicoes = request.user.medicoes.all()

    # Preparar dados para o gráfico evolutivo
    chart_data = {
        "labels": [m.data_hora.strftime("%d/%m/%Y") for m in reversed(medicoes)],
        "peso": [float(m.peso) for m in reversed(medicoes)],
        "imc": [float(m.imc) for m in reversed(medicoes)],
        "percentual_gordura": [float(m.percentual_gordura) for m in reversed(medicoes)],
        "percentual_massa_muscular": [float(m.percentual_massa_muscular) for m in reversed(medicoes)],
        "metabolismo_basal": [m.metabolismo_basal for m in reversed(medicoes)],
        "idade_metabolica": [m.idade_metabolica for m in reversed(medicoes)],
        "indice_gordura_visceral": [float(m.indice_gordura_visceral) for m in reversed(medicoes)],
    }

    return render(request, "measurements/historico.html", {"medicoes": medicoes, "chart_data": json.dumps(chart_data)})


@login_required
@require_POST
def excluir_medicao(request, medicao_id):
    medicao = get_object_or_404(Measurement, id=medicao_id, usuario=request.user)
    medicao.delete()
    messages.success(request, "Medição excluída com sucesso!")

    if request.headers.get("HX-Request"):
        return JsonResponse({"success": True})
    return redirect("historico")
