from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User


class Patient(models.Model):
    
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Compte utilisateur"
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom", default="")
    age = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        verbose_name="Âge"
    )
    sexe = models.CharField(
        max_length=1,
        choices=SEXE_CHOICES,
        verbose_name="Sexe",
        default='M'
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email"
    )
    adresse = models.TextField(
        blank=True,
        null=True,
        verbose_name="Adresse"
    )
    date_naissance = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de naissance"
    )
    date_inscription = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'inscription"
    )

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    def nom_complet(self):
        return f"{self.nom} {self.prenom}"


class Analyse(models.Model):

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours',   'En cours'),
        ('termine',    'Terminé'),
        ('annule',     'Annulé'),
    ]

    TYPE_CHOICES = [
        ('sanguin',      'Analyse sanguine'),
        ('urine',        'Analyse urinaire'),
        ('bacterio',     'Bactériologie'),
        ('biochimie',    'Biochimie'),
        ('hormonale',    'Hormonale'),
        ('radiologie',   'Radiologie'),
        ('autre',        'Autre'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name="Patient"
    )
    type_analyse = models.CharField(
        max_length=100,
        choices=TYPE_CHOICES,
        verbose_name="Type d'analyse"
    )
    resultat = models.TextField(
        verbose_name="Résultat",
        blank=True,
        null=True
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    observations = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observations / Notes"
    )
    medecin = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Médecin prescripteur"
    )
    date_prescription = models.DateField(
        default=timezone.now,
        verbose_name="Date de prescription"
    )
    date_resultat = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Date du résultat"
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le"
    )

    class Meta:
        verbose_name = "Analyse"
        verbose_name_plural = "Analyses"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.get_type_analyse_display()} — {self.patient.nom_complet()}"

    def est_termine(self):
        return self.statut == 'termine'