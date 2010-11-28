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

class DocumentAccueilModifications(object):
    def __init__(self, who, date):
        self.inscrit = who
        self.date = date

    def GetFields(self):
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
        self.cotisation = Cotisation(self.inscrit, self.date)
        
        fields = [('nom-creche', creche.nom),
                ('adresse-creche', creche.adresse),
                ('code-postal-creche', str(creche.code_postal)),
                ('departement-creche', GetDepartement(creche.code_postal)),
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
                ('heures-semaine', GetHeureString( self.cotisation.heures_semaine)),
                ('heures-periode', self.cotisation.heures_periode),
                ('nombre-factures', self.cotisation.nombre_factures),
                ('heures-mois', self.cotisation.heures_mois),
                ('montant-heure-garde', self.cotisation.montant_heure_garde),
                ('cotisation-mensuelle', self.cotisation.cotisation_mensuelle),
                ('date', '%.2d/%.2d/%d' % (self.date.day, self.date.month, self.date.year)),
                ('debut-inscription', inscription.debut),
                ('fin-inscription', inscription.fin),
                ('annee-debut', self.cotisation.debut.year),
                ('annee-fin', self.cotisation.debut.year+1),
                ('permanences', self.GetPermanences(inscription)),
                ('enfants-a-charge', self.cotisation.enfants_a_charge),
                ('carence-maladie', creche.minimum_maladie),
                ('IsPresentDuringTranche', self.IsPresentDuringTranche),
                ]
        
        if self.cotisation.assiette_annuelle is not None:
            fields.append(('annee-revenu', self.cotisation.date_revenus.year))
            fields.append(('assiette-annuelle', self.cotisation.assiette_annuelle))
            fields.append(('assiette-mensuelle', self.cotisation.assiette_mensuelle))
            fields.append(('taux-effort', self.cotisation.taux_effort))
            
        for i, (parent, revenu, abattement) in enumerate(self.cotisation.revenus_parents):
            i += 1
            fields.append(('parent%d' % i, GetPrenomNom(parent)))
            fields.append(('relation-parent%d' % i, parent.relation))
            fields.append(('revenu-parent%d' % i, revenu))
            fields.append(('abattement-parent%d' % i, abattement))
            
        if creche.conges_inscription or creche.facturation_jours_feries == JOURS_FERIES_DEDUITS_ANNUELLEMENT:
            fields.append(('dates-conges-inscription', ", ".join([GetDateString(d) for d in self.cotisation.conges_inscription])))
            fields.append(('heures-fermeture-creche', GetHeureString(self.cotisation.heures_fermeture_creche)))
            fields.append(('heures-accueil-non-facture', GetHeureString(self.cotisation.heures_accueil_non_facture)))
            heures_brut_periode = self.cotisation.heures_periode + self.cotisation.heures_fermeture_creche + self.cotisation.heures_accueil_non_facture
            fields.append(('heures-brut-periode', GetHeureString(heures_brut_periode)))
            fields.append(('semaines-brut-periode', "%.2f" % (heures_brut_periode / self.cotisation.heures_semaine)))
    
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

        return fields

    def IsPresentDuringTranche(self, weekday, debut, fin):
        journee = self.inscrit.getInscription(self.date).reference[weekday]
        if IsPresentDuringTranche(journee, debut, fin):
            return "X"
        else:
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

class ContratAccueilModifications(DocumentAccueilModifications):
    def __init__(self, who, date):
        DocumentAccueilModifications.__init__(self, who, date)
        self.template = 'Contrat accueil.odt'
        self.default_output = u"Contrat accueil %s - %s.odt" % (GetPrenomNom(who), GetDateString(date, weekday=False))

    def execute(self, filename, dom):
        if filename != 'content.xml':
            return None
        
        fields = self.GetFields()
        
        # print dom.toprettyxml()
        doc = dom.getElementsByTagName("office:text")[0]
            
        ReplaceTextFields(doc, fields)
        return {}
    
class FraisGardeModifications(DocumentAccueilModifications):
    def __init__(self, who, date):
        DocumentAccueilModifications.__init__(self, who, date)
        self.template = 'Frais de garde.ods'
        self.default_output = u"Frais de garde %s - %s.odt" % (GetPrenomNom(who), GetDateString(date, weekday=False))
        
    def execute(self, filename, dom):
        if filename != 'content.xml':
            return None
        
        spreadsheet = dom.getElementsByTagName('office:spreadsheet').item(0)
        table = spreadsheet.getElementsByTagName("table:table").item(0)       
        lignes = table.getElementsByTagName("table:table-row")

        fields = self.GetFields()
                      
        ReplaceFields(lignes, fields)
        if len(self.cotisation.revenus_parents) < 2:
            table.removeChild(lignes[3])
            table.removeChild(lignes[4])
        elif not self.cotisation.revenus_parents[1][2]:
            table.removeChild(lignes[4]) 
        if len(self.cotisation.revenus_parents) < 1:
            table.removeChild(lignes[1])
            table.removeChild(lignes[2])
        elif not self.cotisation.revenus_parents[0][2]:
            table.removeChild(lignes[2])
            
        return {} 
            

if __name__ == '__main__':
    import os
    from config import *
    from data import *
    LoadConfig()
    Load()
            
    today = datetime.date.today()

    filename = 'contrat-1.odt'
    try:
        GenerateOODocument(ContratAccueilModifications(creche.inscrits[0], today), filename)
        print u'Fichier %s généré' % filename
    except CotisationException, e:
        print e.errors
        
    filename = 'frais-1.ods'
    try:
        GenerateOODocument(FraisGardeModifications(creche.inscrits[0], today), filename)
        print u'Fichier %s généré' % filename
    except CotisationException, e:
        print e.errors
