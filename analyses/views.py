from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from django.views.decorators.http import require_POST

from .models import Patient, Analyse


# ─────────────────────────────
# 🔐 AUTH
# ─────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'patient'):
            return redirect('espace_patient')
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if hasattr(user, 'patient'):
                return redirect('espace_patient')
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
    return render(request, "dashboard.html", {
        "nb_patients": Patient.objects.count(),
        "nb_analyses": Analyse.objects.count(),
        "nb_termines": Analyse.objects.filter(statut='termine').count(),
        "nb_en_attente": Analyse.objects.filter(statut='en_attente').count(),
        "latest": Analyse.objects.select_related('patient').order_by('-date_creation')[:5],
    })


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
    patients = paginator.get_page(request.GET.get('page'))

    return render(request, "patients.html", {"patients": patients})


# ➕ ADD PATIENT
@login_required
def add_patient(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        Patient.objects.create(
            user=user,
            nom=request.POST.get("nom"),
            prenom=request.POST.get("prenom"),
            age=request.POST.get("age"),
            sexe=request.POST.get("sexe"),
            telephone=request.POST.get("telephone"),
            email=request.POST.get("email"),
            adresse=request.POST.get("adresse"),
            date_naissance=request.POST.get("date_naissance") or None,
        )
        messages.success(request, "Patient ajouté avec succès !")
        return redirect("patients")

    return render(request, "add_patient.html")


# ✏ EDIT PATIENT
@login_required
def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)

    if request.method == "POST":
        patient.nom = request.POST.get("nom")
        patient.prenom = request.POST.get("prenom")
        patient.age = request.POST.get("age")
        patient.sexe = request.POST.get("sexe")
        patient.telephone = request.POST.get("telephone")
        patient.email = request.POST.get("email")
        patient.adresse = request.POST.get("adresse")
        patient.date_naissance = request.POST.get("date_naissance") or None
        patient.save()
        return redirect("patients")

    return render(request, "edit_patient.html", {"patient": patient})


# 🗑 DELETE PATIENT
@login_required
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if patient.user:
        patient.user.delete()
    patient.delete()
    return redirect("patients")


# 👁 DETAIL PATIENT
@login_required
def detail_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    return render(request, "detail_patient.html", {"patient": patient})


# 🏥 ESPACE PATIENT
@login_required
def espace_patient(request):
    if not hasattr(request.user, 'patient'):
        return redirect('dashboard')

    patient = request.user.patient
    analyses = Analyse.objects.filter(patient=patient)

    return render(request, "espace_patient.html", {
        "patient": patient,
        "analyses": analyses,
        "nb_total": analyses.count(),
        "nb_termines": analyses.filter(statut='termine').count(),
        "nb_en_attente": analyses.filter(statut='en_attente').count(),
    })


# ─────────────────────────────
# 🧪 ANALYSES
# ─────────────────────────────
@login_required
def analyses(request):
    qs = Analyse.objects.select_related('patient').all()
    return render(request, "analyses.html", {"analyses": qs})


# ➕ ADD ANALYSE
@login_required
def add_analyse(request):
    patients = Patient.objects.all()

    if request.method == "POST":
        Analyse.objects.create(
            patient=Patient.objects.get(id=request.POST.get("patient")),
            type_analyse=request.POST.get("type_analyse"),
            statut=request.POST.get("statut")
        )
        return redirect("analyses")

    return render(request, "add_analyse.html", {"patients": patients})


# ✏ EDIT ANALYSE
@login_required
def edit_analyse(request, id):
    analyse = get_object_or_404(Analyse, id=id)
    patients = Patient.objects.all()

    if request.method == "POST":
        analyse.patient = Patient.objects.get(id=request.POST.get("patient"))
        analyse.type_analyse = request.POST.get("type_analyse")
        analyse.statut = request.POST.get("statut")
        analyse.save()
        return redirect("analyses")

    return render(request, "edit_analyse.html", {
        "analyse": analyse,
        "patients": patients
    })


# 🗑 DELETE ANALYSE
@login_required
@require_POST
def delete_analyse(request, id):
    analyse = get_object_or_404(Analyse, id=id)
    analyse.delete()
    return redirect("analyses")


# ─────────────────────────────
# 📄 PDF GLOBAL
# ─────────────────────────────
@login_required
def export_analyses_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="analyses.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("🏥 MedAnalyses", styles['Title']))
    elements.append(Paragraph("Liste complète des analyses", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [["Patient", "Type", "Médecin", "Date", "Statut"]]
    for a in Analyse.objects.select_related('patient').all():
        statut_map = {
            'termine': 'Terminé',
            'en_attente': 'En attente',
            'en_cours': 'En cours',
            'annule': 'Annulé',
        }
        data.append([
            f"{a.patient.nom} {a.patient.prenom}",
            a.get_type_analyse_display(),
            a.medecin or "—",
            a.date_creation.strftime("%d/%m/%Y"),
            statut_map.get(a.statut, a.statut),
        ])

    table = Table(data, colWidths=[110, 100, 100, 70, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4ff')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Document généré le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles['Normal']
    ))

    doc.build(elements)
    return response


# ─────────────────────────────
# 📄 PDF PAR PATIENT
# ─────────────────────────────
@login_required
def export_patient_pdf(request, id):
    patient = get_object_or_404(Patient, id=id)
    analyses = Analyse.objects.filter(patient=patient)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="analyses_{patient.nom}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    # ─── TITRE ───
    elements.append(Paragraph("🏥 MedAnalyses", styles['Title']))
    elements.append(Paragraph("Rapport d'analyses médicales", styles['Normal']))
    elements.append(Spacer(1, 20))

    # ─── INFOS PATIENT ───
    elements.append(Paragraph("📋 Informations du Patient", styles['Heading2']))
    elements.append(Spacer(1, 8))

    info_data = [
        ["Nom complet", f"{patient.nom} {patient.prenom}"],
        ["Âge", f"{patient.age} ans"],
        ["Sexe", patient.get_sexe_display()],
        ["Téléphone", patient.telephone or "—"],
        ["Email", patient.email or "—"],
        ["Adresse", patient.adresse or "—"],
        ["Date de naissance", str(patient.date_naissance) if patient.date_naissance else "—"],
        ["Date d'inscription", patient.date_inscription.strftime("%d/%m/%Y")],
    ]

    info_table = Table(info_data, colWidths=[150, 350])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.HexColor('#f0f4ff'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 25))

    # ─── STATS ───
    elements.append(Paragraph("📊 Résumé des Analyses", styles['Heading2']))
    elements.append(Spacer(1, 8))

    nb_total = analyses.count()
    nb_termine = analyses.filter(statut='termine').count()
    nb_attente = analyses.filter(statut='en_attente').count()
    nb_cours = analyses.filter(statut='en_cours').count()

    stats_data = [
        ["Total", "Terminées", "En attente", "En cours"],
        [str(nb_total), str(nb_termine), str(nb_attente), str(nb_cours)],
    ]

    stats_table = Table(stats_data, colWidths=[125, 125, 125, 125])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e8f0fe')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 16),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))

    elements.append(stats_table)
    elements.append(Spacer(1, 25))

    # ─── TABLEAU ANALYSES ───
    elements.append(Paragraph("🧪 Détail des Analyses", styles['Heading2']))
    elements.append(Spacer(1, 8))

    data = [["Type d'analyse", "Médecin", "Date", "Statut", "Résultat"]]
    statut_map = {
        'termine': 'Terminé',
        'en_attente': 'En attente',
        'en_cours': 'En cours',
        'annule': 'Annulé',
    }
    for a in analyses:
        data.append([
            a.get_type_analyse_display(),
            a.medecin or "—",
            a.date_creation.strftime("%d/%m/%Y"),
            statut_map.get(a.statut, a.statut),
            a.resultat or "En attente...",
        ])

    analyses_table = Table(data, colWidths=[110, 100, 70, 80, 140])
    analyses_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4ff')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))

    elements.append(analyses_table)
    elements.append(Spacer(1, 30))

    # ─── PIED DE PAGE ───
    elements.append(Paragraph(
        f"Document généré le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles['Normal']
    ))

    doc.build(elements)
    return response