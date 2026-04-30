from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from django.views.decorators.http import require_POST

from .models import Patient, Analyse


# ─────────────────────────────
# 🔐 LOGIN
# ─────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants incorrects")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────
# 🏠 HOME
# ─────────────────────────────
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, "home.html")


# ─────────────────────────────
# 📊 DASHBOARD
# ─────────────────────────────
@login_required
def dashboard(request):
    context = {
        "nb_patients": Patient.objects.count(),
        "nb_analyses": Analyse.objects.count(),
        "nb_termines": Analyse.objects.filter(statut='termine').count(),
        "nb_en_attente": Analyse.objects.filter(statut='en_attente').count(),
        "latest": Analyse.objects.select_related('patient').order_by('-date_creation')[:5],
    }
    return render(request, "dashboard.html", context)


# ─────────────────────────────
# 👨‍⚕️ PATIENTS
# ─────────────────────────────
@login_required
def patients(request):
    qs = Patient.objects.all()

    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search)
        )

    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    patients = paginator.get_page(page)

    return render(request, "patients.html", {"patients": patients})


# ─────────────────────────────
# 🧪 ANALYSES
# ─────────────────────────────
@login_required
def analyses(request):
    qs = Analyse.objects.select_related('patient').all()
    return render(request, "analyses.html", {"analyses": qs})


# ─────────────────────────────
# 📄 EXPORT PDF
# ─────────────────────────────
@login_required
def export_analyses_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="analyses.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Liste des analyses", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["Patient", "Type", "Statut"]]

    for a in Analyse.objects.all():
        data.append([
            a.patient.nom,
            a.type_analyse,
            a.statut
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    return response


# ─────────────────────────────
# 🗑 DELETE AJAX (IMPORTANT)
# ─────────────────────────────
@login_required
@require_POST
def delete_analyse(request, id):
    analyse = get_object_or_404(Analyse, id=id)
    analyse.delete()
    return HttpResponse(status=200)