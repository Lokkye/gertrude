# -*- coding: utf-8 -*-

##    This file is part of Gertrude.
##
##    Gertrude is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 3 of the License, or
##    (at your option) any later version.
##
##    Gertrude is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with Gertrude; if not, see <http://www.gnu.org/licenses/>.

from constants import *
from functions import *
from sqlobjects import Parent
from cotisation import Cotisation, CotisationException
from ooffice import *

class ContratAccueilModifications(object):
    def __init__(self, who, date):
        self.template = 'Contrat accueil.odt'
        self.default_output = u"Contrat accueil %s - %s.odt" % (GetPrenomNom(who), GetDateString(date, weekday=False))
        self.inscrit = who
        self.date = date

    def execute(self, filename, dom):
        if filename != 'content.xml':
            return None
        
        errors = {}
        president = tresorier = directeur = ""
        bureau = Select(creche.bureaux, self.date)
        if bureau:
            president = bureau.president
            tresorier = bureau.tresorier
            directeur = bureau.directeur
            
        plancher_caf = "non rempli"
        plafond_caf = "non rempli"
        bareme_caf = Select(creche.baremes_caf, self.date)
        if bareme_caf:
            plancher_caf = "%.2f" % bareme_caf.plancher
            plafond_caf = "%.2f" % bareme_caf.plafond
            
        inscription = self.inscrit.getInscription(self.date)
        cotisation = Cotisation(self.inscrit, self.date)
        
        # print dom.toprettyxml()
        doc = dom.getElementsByTagName("office:text")[0]
            
        fields = [('nom-creche', creche.nom),
                ('adresse-creche', creche.adresse),
                ('code-postal-creche', str(creche.code_postal)),
                ('departement-creche', str(creche.code_postal/1000)),
                ('ville-creche', creche.ville),
                ('telephone-creche', creche.telephone),
                ('email-creche', creche.email),
                ('prenom', self.inscrit.prenom),
                ('nom', self.inscrit.nom),
                ('parents', GetParentsString(self.inscrit)),
                ('adresse', self.inscrit.adresse),
                ('code-postal', self.inscrit.code_postal),
                ('ville', self.inscrit.ville),
                ('numero-securite-sociale', self.inscrit.numero_securite_sociale),
                ('numero-allocataire-caf', self.inscrit.numero_allocataire_caf),
                ('naissance', self.inscrit.naissance),
                ('president', president),
                ('tresorier', tresorier),
                ('directeur', directeur),
                ('plancher-caf', plancher_caf),
                ('plafond-caf', plafond_caf),
                ('heures-semaine', GetHeureString(cotisation.heures_semaine)),
                ('heures-periode', cotisation.heures_periode),
                ('nombre-factures', cotisation.nombre_factures),
                ('heures-mois', cotisation.heures_mois),
                ('montant-heure-garde', cotisation.montant_heure_garde),
                ('cotisation-mensuelle', "%.2f" % cotisation.cotisation_mensuelle),
                ('date', '%.2d/%.2d/%d' % (self.date.day, self.date.month, self.date.year)),
                ('debut-inscription', inscription.debut),
                ('fin-inscription', inscription.fin),
                ('annee-debut', cotisation.debut.year),
                ('annee-fin', cotisation.debut.year+1),
                ('permanences', self.GetPermanences(inscription)),
                ('enfants-a-charge', cotisation.enfants_a_charge),
                ('carence-maladie', creche.minimum_maladie),
                ('IsPresentDuringTranche', self.IsPresentDuringTranche),
                ]
        
        if cotisation.assiette_annuelle is not None:
            fields.append(('assiette-annuelle', "%.2f" % cotisation.assiette_annuelle))
            fields.append(('taux-effort', cotisation.taux_effort))
            
        if creche.conges_inscription or creche.facturation_jours_feries == JOURS_FERIES_DEDUITS_ANNUELLEMENT:
            fields.append(('dates-conges-inscription', ", ".join([GetDateString(d) for d in cotisation.conges_inscription])))
            fields.append(('heures-fermeture-creche', GetHeureString(cotisation.heures_fermeture_creche)))
            fields.append(('heures-accueil-non-facture', GetHeureString(cotisation.heures_accueil_non_facture)))
            heures_brut_periode = cotisation.heures_periode + cotisation.heures_fermeture_creche + cotisation.heures_accueil_non_facture
            fields.append(('heures-brut-periode', GetHeureString(heures_brut_periode)))
            fields.append(('semaines-brut-periode', "%.2f" % (heures_brut_periode / cotisation.heures_semaine)))
    
        for jour in range(5):
            jour_reference = inscription.reference[jour]
            debut, fin = jour_reference.GetPlageHoraire()
            fields.append(('heure-debut[%d]' % jour, GetHeureString(debut)))
            fields.append(('heure-fin[%d]' % jour, GetHeureString(fin)))
            fields.append(('heures-jour[%d]' % jour, GetHeureString(jour_reference.GetNombreHeures())))

#            if inscrit.sexe == 1:
#                fields.append(('ne-e', u"né"))
#            else:
#                fields.append(('ne-e', u"née"))
            
        ReplaceTextFields(doc, fields)
        return errors
    
    def IsPresentDuringTranche(self, weekday, debut, fin):
        journee = self.inscrit.getInscription(self.date).reference[weekday]
        for i in range(int(debut * (60 / BASE_GRANULARITY)), int(fin * (60 / BASE_GRANULARITY))):
            if journee.values[i]:
                return "X"
        return ""
    
    def GetPermanences(self, inscription):
        jours, heures = inscription.GetJoursHeuresReference()           
        if heures >= 11:
            result = 8
        elif heures >= 8:
            result = 6
        else:
            result = 4
        if GetEnfantsCount(inscription.inscrit, inscription.debut)[1]:
            return 2 + result
        else:
            return result        
    
            

if __name__ == '__main__':
    import os
    from config import *
    from data import *
    LoadConfig()
    Load()
            
    today = datetime.date.today()

    filename = 'contrat-1.odt'
    try:
        GenerateDocument(ContratAccueilModifications(creche.inscrits[0], today), filename)
        print u'Fichier %s généré' % filename
    except CotisationException, e:
        print e.errors
