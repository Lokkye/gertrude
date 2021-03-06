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

import os.path
import datetime, time
from constants import *
from controls import *
from sqlobjects import *
import wx
from planning import LinePlanningWidget

types_creche = [(u"Parental", TYPE_PARENTAL),
                (u"Familial", TYPE_FAMILIAL),
                (u"Associatif", TYPE_ASSOCIATIF),
                (u"Municipal", TYPE_MUNICIPAL),
                (u"Micro-crèche", TYPE_MICRO_CRECHE),
                (u"Multi-accueil", TYPE_MULTI_ACCUEIL),
                (u"Assistante maternelle", TYPE_ASSISTANTE_MATERNELLE),
                (u"Garderie périscolaire", TYPE_GARDERIE_PERISCOLAIRE)]

modes_facturation = [("Forfait 10h / jour", FACTURATION_FORFAIT_10H),
                     (u"PSU", FACTURATION_PSU),
                     (u"PSU avec taux d'effort personnalisés", FACTURATION_PSU_TAUX_PERSONNALISES),
                     (u"PAJE (taux horaire spécifique)", FACTURATION_PAJE),
                     (u"Horaires réels", FACTURATION_HORAIRES_REELS),
                     (u"Facturation personnalisée (forfait mensuel)", FACTURATION_FORFAIT_MENSUEL)]

modes_facturation_adaptation = [(u'Facturation normale', PERIODE_ADAPTATION_FACTUREE_NORMALEMENT),
                                (u"Horaires réels", FACTURATION_HORAIRES_REELS)]

temps_facturation = [(u"Fin de mois", FACTURATION_FIN_MOIS),
                     (u"Début de mois : contrat mois + réalisé mois-1", FACTURATION_DEBUT_MOIS_CONTRAT),
                     (u"Début de mois : prévisionnel mois + réalisé mois-1", FACTURATION_DEBUT_MOIS_PREVISIONNEL),
                     ]

class CrecheTab(AutoTab):
    def __init__(self, parent):
        global delbmp
        delbmp = wx.Bitmap(GetBitmapFile("remove.png"), wx.BITMAP_TYPE_PNG)
        observers['sites'] = 0
        observers['groupes'] = 0
        AutoTab.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.FlexGridSizer(0, 2, 5, 5)
        sizer2.AddGrowableCol(1, 1)
        sizer2.AddMany([wx.StaticText(self, -1, u'Nom de la structure :'), (AutoTextCtrl(self, creche, 'nom'), 0, wx.EXPAND)])
        sizer2.AddMany([wx.StaticText(self, -1, 'Adresse :'), (AutoTextCtrl(self, creche, 'adresse'), 0, wx.EXPAND)])
        sizer2.AddMany([wx.StaticText(self, -1, 'Code Postal :'), (AutoNumericCtrl(self, creche, 'code_postal', precision=0), 0, wx.EXPAND)])
        sizer2.AddMany([wx.StaticText(self, -1, 'Ville :'), (AutoTextCtrl(self, creche, 'ville'), 0, wx.EXPAND)])
        sizer2.AddMany([wx.StaticText(self, -1, u'Téléphone :'), (AutoPhoneCtrl(self, creche, 'telephone'), 0, wx.EXPAND)])
        sizer2.AddMany([wx.StaticText(self, -1, 'E-mail :'), (AutoTextCtrl(self, creche, 'email'), 0, wx.EXPAND)])
        sizer2.AddMany([wx.StaticText(self, -1, u"Serveur pour l'envoi d'emails :"), (AutoTextCtrl(self, creche, 'smtp_server'), 0, wx.EXPAND)])
        sizer2.AddMany([wx.StaticText(self, -1, u"Email de la CAF :"), (AutoTextCtrl(self, creche, 'caf_email'), 0, wx.EXPAND)])
        type_structure_choice = AutoChoiceCtrl(self, creche, 'type', items=types_creche)
        self.Bind(wx.EVT_CHOICE, self.onTypeStructureChoice, type_structure_choice)
        sizer2.AddMany([wx.StaticText(self, -1, 'Type :'), (type_structure_choice, 0, wx.EXPAND)])
        sizer2.AddMany([wx.StaticText(self, -1, u'Capacité :'), (LinePlanningWidget(self, creche.tranches_capacite), 0, wx.EXPAND)])       
        self.sizer.Add(sizer2, 0, wx.EXPAND|wx.ALL, 5)
        
        self.sites_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Sites"), wx.VERTICAL)
        self.sites_sizer = wx.BoxSizer(wx.VERTICAL)
        for i, site in enumerate(creche.sites):
            self.line_site_add(i)
        self.sites_box_sizer.Add(self.sites_sizer, 0, wx.EXPAND|wx.ALL, 5)
        button_add = wx.Button(self, -1, u'Nouveau site')
        if readonly:
            button_add.Disable()
        self.sites_box_sizer.Add(button_add, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.add_site, button_add)
        self.sizer.Add(self.sites_box_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.groupes_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Groupes"), wx.VERTICAL)
        self.groupes_sizer = wx.BoxSizer(wx.VERTICAL)
        for i, groupe in enumerate(creche.groupes):
            self.line_groupe_add(i)
        self.groupes_box_sizer.Add(self.groupes_sizer, 0, wx.EXPAND|wx.ALL, 5)
        button_add = wx.Button(self, -1, u'Nouveau groupe')
        if readonly:
            button_add.Disable()
        self.groupes_box_sizer.Add(button_add, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.add_groupe, button_add)
        self.sizer.Add(self.groupes_box_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        if config.options & CATEGORIES:
            self.categories_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, u"Catégories"), wx.VERTICAL)
            self.categories_sizer = wx.BoxSizer(wx.VERTICAL)
            for i, categorie in enumerate(creche.categories):
                self.line_categorie_add(i)
            self.categories_box_sizer.Add(self.categories_sizer, 0, wx.EXPAND|wx.ALL, 5)
            button_add = wx.Button(self, -1, u'Nouvelle catégorie')
            if readonly:
                button_add.Disable()
            self.categories_box_sizer.Add(button_add, 0, wx.ALL, 5)
            self.Bind(wx.EVT_BUTTON, self.add_categorie, button_add)
            self.sizer.Add(self.categories_box_sizer, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(self.sizer)

    def UpdateContents(self):
        for i in range(len(self.sites_sizer.GetChildren()), len(creche.sites)):
            self.line_site_add(i)
        for i in range(len(creche.sites), len(self.sites_sizer.GetChildren())):
            self.line_site_del()
        for i in range(len(self.groupes_sizer.GetChildren()), len(creche.groupes)):
            self.line_groupe_add(i)
        for i in range(len(creche.groupes), len(self.groupes_sizer.GetChildren())):
            self.line_groupe_del()
        self.sizer.Layout()
        AutoTab.UpdateContents(self)

    def line_site_add(self, index):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, 'Nom :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoTextCtrl(self, creche, 'sites[%d].nom' % index, observers=['sites']), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, 'Adresse :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoTextCtrl(self, creche, 'sites[%d].adresse' % index), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, 'Code Postal :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoNumericCtrl(self, creche, 'sites[%d].code_postal' % index, precision=0), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, 'Ville :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoTextCtrl(self, creche, 'sites[%d].ville' % index), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Téléphone'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoPhoneCtrl(self, creche, 'sites[%d].telephone' % index), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Capacité'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoNumericCtrl(self, creche, 'sites[%d].capacite' % index, precision=0), 1, wx.EXPAND)])                
        delbutton = wx.BitmapButton(self, -1, delbmp)
        delbutton.index = index
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_BUTTON, self.remove_site, delbutton)
        self.sites_sizer.Add(sizer, 0, wx.EXPAND|wx.BOTTOM, 5)

    def line_site_del(self):
        index = len(self.sites_sizer.GetChildren()) - 1
        sizer = self.sites_sizer.GetItem(index)
        sizer.DeleteWindows()
        self.sites_sizer.Detach(index)

    def add_site(self, event):
        observers['sites'] = time.time()
        history.Append(Delete(creche.sites, -1))
        creche.sites.append(Site())
        self.line_site_add(len(creche.sites) - 1)
        self.sizer.Layout()

    def remove_site(self, event):
        observers['sites'] = time.time()
        index = event.GetEventObject().index
        history.Append(Insert(creche.sites, index, creche.sites[index]))
        self.line_site_del()
        creche.sites[index].delete()
        del creche.sites[index]
        self.sizer.FitInside(self)
        self.UpdateContents()

    def line_groupe_add(self, index):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, 'Nom :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoTextCtrl(self, creche, 'groupes[%d].nom' % index, observers=['groupes']), 1, wx.EXPAND), (AutoNumericCtrl(self, creche, 'groupes[%d].ordre' % index, observers=['groupes'], precision=0), 0, wx.EXPAND)])
        delbutton = wx.BitmapButton(self, -1, delbmp)
        delbutton.index = index
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_BUTTON, self.remove_groupe, delbutton)
        self.groupes_sizer.Add(sizer, 0, wx.EXPAND|wx.BOTTOM, 5)

    def line_groupe_del(self):
        index = len(self.groupes_sizer.GetChildren()) - 1
        sizer = self.groupes_sizer.GetItem(index)
        sizer.DeleteWindows()
        self.groupes_sizer.Detach(index)

    def add_groupe(self, event):
        observers['groupes'] = time.time()
        history.Append(Delete(creche.groupes, -1))
        if len(creche.groupes) == 0:
            ordre = 0
        else:
            ordre = creche.groupes[-1].ordre + 1
        creche.groupes.append(Groupe(ordre))
        self.line_groupe_add(len(creche.groupes) - 1)
        self.sizer.FitInside(self)
        self.sizer.Layout()

    def remove_groupe(self, event):
        observers['groupes'] = time.time()
        index = event.GetEventObject().index
        history.Append(Insert(creche.groupes, index, creche.groupes[index]))
        self.line_groupe_del()
        creche.groupes[index].delete()
        del creche.groupes[index]
        self.sizer.FitInside(self)
        self.UpdateContents()
        
    def line_categorie_add(self, index):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, 'Nom :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoTextCtrl(self, creche, 'categories[%d].nom' % index, observers=['categories']), 1, wx.EXPAND)])
        delbutton = wx.BitmapButton(self, -1, delbmp)
        delbutton.index = index
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_BUTTON, self.remove_categorie, delbutton)
        self.categories_sizer.Add(sizer, 0, wx.EXPAND|wx.BOTTOM, 5)

    def line_categorie_del(self):
        index = len(self.categories_sizer.GetChildren()) - 1
        sizer = self.categories_sizer.GetItem(index)
        sizer.DeleteWindows()
        self.categories_sizer.Detach(index)

    def add_categorie(self, event):
        observers['categories'] = time.time()
        history.Append(Delete(creche.categories, -1))
        creche.categories.append(Categorie())
        self.line_categorie_add(len(creche.categories) - 1)
        self.sizer.FitInside(self)
        self.sizer.Layout()

    def remove_categorie(self, event):
        observers['categories'] = time.time()
        index = event.GetEventObject().index
        history.Append(Insert(creche.categories, index, creche.categories[index]))
        self.line_categorie_del()
        creche.categories[index].delete()
        del creche.categories[index]
        self.sizer.FitInside(self)
        self.UpdateContents()
        
    def onTypeStructureChoice(self, event):
        object = event.GetEventObject()
        value = object.GetClientData(object.GetSelection())
        self.GetParent().DisplayProfesseursTab(value==TYPE_GARDERIE_PERISCOLAIRE)
        event.Skip()

class ProfesseursTab(AutoTab):
    def __init__(self, parent):
        global delbmp
        observers['professeurs'] = 0
        delbmp = wx.Bitmap(GetBitmapFile("remove.png"), wx.BITMAP_TYPE_PNG)
        AutoTab.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.professeurs_sizer = wx.BoxSizer(wx.VERTICAL)
        for professeur in creche.professeurs:
            self.affiche_professeur(professeur)
        self.sizer.Add(self.professeurs_sizer, 0, wx.EXPAND|wx.ALL, 5)
        button_add = wx.Button(self, -1, 'Nouveau professeur')
        self.sizer.Add(button_add, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.ajoute_professeur, button_add)
        self.SetSizer(self.sizer)

    def UpdateContents(self):
        pass

    def affiche_professeur(self, professeur):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, u'Prénom :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoTextCtrl(self, professeur, 'prenom', observers=['professeurs']), 0, wx.ALIGN_CENTER_VERTICAL)])
        sizer.AddMany([(wx.StaticText(self, -1, 'Nom :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoTextCtrl(self, professeur, 'nom', observers=['professeurs']), 0, wx.ALIGN_CENTER_VERTICAL)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Entrée :', size=(50,-1)), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), AutoDateCtrl(self, professeur, 'entree', observers=['professeurs'])])
        sizer.AddMany([(wx.StaticText(self, -1, 'Sortie :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), AutoDateCtrl(self, professeur, 'sortie', observers=['professeurs'])])
        delbutton = wx.BitmapButton(self, -1, delbmp, style=wx.NO_BORDER)
        delbutton.professeur, delbutton.sizer = professeur, sizer
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        self.Bind(wx.EVT_BUTTON, self.retire_professeur, delbutton)
        self.professeurs_sizer.Add(sizer)

    def ajoute_professeur(self, event):
        observers['professeurs'] = time.time()
        history.Append(Delete(creche.professeurs, -1))
        professeur = Professeur()
        creche.professeurs.append(professeur)
        self.affiche_professeur(professeur)        
        self.sizer.FitInside(self)
        
    def retire_professeur(self, event):
        observers['professeurs'] = time.time()
        obj = event.GetEventObject()
        for i, professeur in enumerate(creche.professeurs):
            if professeur == obj.professeur:
                history.Append(Insert(creche.professeurs, i, professeur))
                sizer = self.professeurs_sizer.GetItem(i)
                sizer.DeleteWindows()
                self.professeurs_sizer.Detach(i)
                professeur.delete()
                del creche.professeurs[i]
                self.sizer.FitInside(self)
                self.Refresh()
                break
            
class ResponsabilitesTab(AutoTab, PeriodeMixin):
    def __init__(self, parent):
        AutoTab.__init__(self, parent)
        PeriodeMixin.__init__(self, 'bureaux')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(PeriodeChoice(self, Bureau), 0, wx.TOP, 5)
        sizer2 = wx.FlexGridSizer(0, 2, 5, 5)
        sizer2.AddGrowableCol(1, 1)
        self.responsables_ctrls = []
        if creche.type == TYPE_MULTI_ACCUEIL:
            self.gerant_ctrl = AutoComboBox(self, None, 'gerant')
            sizer2.AddMany([(wx.StaticText(self, -1, u'Gérant(e) :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.gerant_ctrl, 0, wx.EXPAND)])
            self.directeur_ctrl = AutoComboBox(self, None, 'directeur')        
            sizer2.AddMany([(wx.StaticText(self, -1, u'Directeur(trice) :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.directeur_ctrl, 0, wx.EXPAND)])
            self.directeur_adjoint_ctrl = AutoComboBox(self, None, 'directeur_adjoint')        
            sizer2.AddMany([(wx.StaticText(self, -1, u'Directeur(trice) adjoint(e) :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.directeur_adjoint_ctrl, 0, wx.EXPAND)])
            self.comptable_ctrl = AutoComboBox(self, None, 'comptable')        
            sizer2.AddMany([(wx.StaticText(self, -1, u'Comptable :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.comptable_ctrl, 0, wx.EXPAND)])
            self.secretaire_ctrl = AutoComboBox(self, None, 'secretaire')        
            sizer2.AddMany([(wx.StaticText(self, -1, u'Secrétaire :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.secretaire_ctrl, 0, wx.EXPAND)])
        else:
            self.gerant_ctrl = None
            self.responsables_ctrls.append(AutoComboBox(self, None, 'president'))
            sizer2.AddMany([(wx.StaticText(self, -1, u'Président(e) :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.responsables_ctrls[-1], 0, wx.EXPAND)])
            self.responsables_ctrls.append(AutoComboBox(self, None, 'vice_president'))
            sizer2.AddMany([(wx.StaticText(self, -1, u'Vice président(e) :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.responsables_ctrls[-1], 0, wx.EXPAND)])
            self.responsables_ctrls.append(AutoComboBox(self, None, 'tresorier'))
            sizer2.AddMany([(wx.StaticText(self, -1, u'Trésorier(ère) :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.responsables_ctrls[-1], 0, wx.EXPAND)])
            self.responsables_ctrls.append(AutoComboBox(self, None, 'secretaire'))        
            sizer2.AddMany([(wx.StaticText(self, -1, u'Secrétaire :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.responsables_ctrls[-1], 0, wx.EXPAND)])
            self.directeur_ctrl = AutoComboBox(self, None, 'directeur')        
            sizer2.AddMany([(wx.StaticText(self, -1, u'Directeur(trice) :'), 0, wx.ALIGN_CENTER_VERTICAL), (self.directeur_ctrl, 0, wx.EXPAND)])
        sizer.Add(sizer2, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)

    def UpdateContents(self):
        self.SetInstance(creche)

    def SetInstance(self, instance, periode=None):
        self.instance = instance
        if instance and len(instance.bureaux) > 0:
            if periode is None:
                current_periode = eval("self.instance.%s[-1]" % self.member)
            else:
                current_periode = eval("self.instance.%s[%d]" % (self.member, periode))
            
            salaries = self.GetNomsSalaries(current_periode)
            
            if self.gerant_ctrl:
                self.gerant_ctrl.SetItems(salaries)
                self.directeur_ctrl.SetItems(salaries)
                self.directeur_adjoint_ctrl.SetItems(salaries)
                self.comptable_ctrl.SetItems(salaries)                
                self.secretaire_ctrl.SetItems(salaries)
            else:
                parents = self.GetNomsParents(current_periode)
                for ctrl in self.responsables_ctrls:
                    ctrl.SetItems(parents)
                self.directeur_ctrl.SetItems(salaries)
        PeriodeMixin.SetInstance(self, instance, periode)

    def GetNomsParents(self, periode):
        noms = set()
        for inscrit in GetInscrits(periode.debut, periode.fin):
            for parent in inscrit.parents.values():
                noms.add(GetPrenomNom(parent))
        noms = list(noms)
        noms.sort(cmp=lambda x,y: cmp(x.lower(), y.lower()))
        return noms
    
    def GetNomsSalaries(self, periode):
        noms = []
        for salarie in creche.salaries:
            noms.append(GetPrenomNom(salarie))
        noms.sort(cmp=lambda x,y: cmp(x.lower(), y.lower()))
        return noms

activity_modes = [("Normal", 0),
                  (u"Libère une place", MODE_LIBERE_PLACE),
                  (u"Sans horaires", MODE_SANS_HORAIRES),
                  (u"Présence non facturée", MODE_PRESENCE_NON_FACTUREE),
                  (u"Sans horaire, systématique", MODE_SYSTEMATIQUE_SANS_HORAIRES)
                 ]

activity_ownership = [(u"Enfants et Salariés", ACTIVITY_OWNER_ALL),
                      (u"Enfants", ACTIVITY_OWNER_ENFANTS),
                      (u"Salariés", ACTIVITY_OWNER_SALARIES)
                     ]

class ActivitesTab(AutoTab):
    def __init__(self, parent):
        global delbmp
        delbmp = wx.Bitmap(GetBitmapFile("remove.png"), wx.BITMAP_TYPE_PNG)
        AutoTab.__init__(self, parent)
        observers['activites'] = 0
        self.color_buttons = {}
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Couleurs"), wx.VERTICAL)
        flex_sizer = wx.FlexGridSizer(0, 3, 3, 2)
        flex_sizer.AddGrowableCol(1, 1)
        for label, activite, field in ((u"présences", creche.activites[0], "couleur"), (u"présences supplémentaires", creche.activites[0], "couleur_supplement"), (u"présences prévisionnelles", creche.activites[0], "couleur_previsionnel"), (u"absences pour congés", creche.couleurs[VACANCES], "couleur"), (u"absences non prévenues", creche.couleurs[ABSENCE_NON_PREVENUE], "couleur"), (u"absences pour maladie", creche.couleurs[MALADE], "couleur")):
            color_button = wx.Button(self, -1, "", size=(20, 20))            
            r, g, b, a, h = couleur = getattr(activite, field)
            color_button.SetBackgroundColour(wx.Colour(r, g, b))
            self.Bind(wx.EVT_BUTTON, self.onColorButton, color_button)
            color_button.hash_cb = HashComboBox(self)
            if readonly:
                color_button.Disable()
                color_button.hash_cb.Disable()
            color_button.activite = color_button.hash_cb.activite = activite
            color_button.field = color_button.hash_cb.field = [field]
            self.color_buttons[(activite.value, field)] = color_button
            self.UpdateHash(color_button.hash_cb, couleur)
            self.Bind(wx.EVT_COMBOBOX, self.onHashChange, color_button.hash_cb)
            flex_sizer.AddMany([(wx.StaticText(self, -1, u'Couleur des %s :' % label), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (color_button, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (color_button.hash_cb, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)])
        box_sizer.Add(flex_sizer, 0, wx.BOTTOM, 5)
        button = wx.Button(self, -1, u'Rétablir les couleurs par défaut')
        self.Bind(wx.EVT_BUTTON, self.OnCouleursDefaut, button)
        box_sizer.Add(button, 0, wx.ALL, 5)
        self.sizer.Add(box_sizer, 0, wx.ALL|wx.EXPAND, 5)

        box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, u'Activités'), wx.VERTICAL)
        self.activites_sizer = wx.BoxSizer(wx.VERTICAL)
        for activity in creche.activites.values():
            if activity.value > 0:
                self.line_add(activity)
        box_sizer.Add(self.activites_sizer, 0, wx.EXPAND|wx.ALL, 5)
        button_add = wx.Button(self, -1, u'Nouvelle activité')
        box_sizer.Add(button_add, 0, wx.ALL, 5)
        if readonly:
            button.Disable()
            button_add.Disable()
        self.Bind(wx.EVT_BUTTON, self.activite_add, button_add)
        self.sizer.Add(box_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.UpdateContents()

    def UpdateContents(self):
        self.color_buttons[(0, "couleur_supplement")].Enable(not readonly and creche.presences_supplementaires)
        self.color_buttons[(0, "couleur_supplement")].hash_cb.Enable(not readonly and creche.presences_supplementaires)
        self.color_buttons[(0, "couleur_previsionnel")].Enable(not readonly and creche.presences_previsionnelles)
        self.color_buttons[(0, "couleur_previsionnel")].hash_cb.Enable(not readonly and creche.presences_previsionnelles)
        self.activites_sizer.Clear(True)
        for activity in creche.activites.values():
            if activity.value > 0:
                self.line_add(activity)
        self.sizer.Layout()
        
    def OnCouleursDefaut(self, event):
        history.Append(None)
        observers['activites'] = time.time()
        creche.activites[0].couleur = [5, 203, 28, 150, wx.SOLID]
        creche.activites[0].couleur_supplement = [5, 203, 28, 250, wx.SOLID]
        creche.activites[0].couleur_previsionnel = [5, 203, 28, 50, wx.SOLID]
        creche.couleurs[VACANCES].couleur = [0, 0, 255, 150, wx.SOLID]
        creche.couleurs[ABSENCE_NON_PREVENUE].couleur = [0, 0, 255, 150, wx.SOLID]
        creche.couleurs[MALADE].couleur = [190, 35, 29, 150, wx.SOLID]
        for activite, field in [(creche.activites[0], "couleur"), (creche.activites[0], "couleur_supplement"), (creche.activites[0], "couleur_previsionnel")]:
            r, g, b, a, h = color = getattr(activite, field)
            self.color_buttons[(0, field)].SetBackgroundColour(wx.Colour(r, g, b))
            self.UpdateHash(self.color_buttons[(0, field)].hash_cb, color)        

    def line_add(self, activity):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, u'Libellé :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoTextCtrl(self, creche, 'activites[%d].label' % activity.value), 1, wx.EXPAND)])
        mode_choice = AutoChoiceCtrl(self, creche, 'activites[%d].mode' % activity.value, items=activity_modes, observers=['activites'])
        self.Bind(wx.EVT_CHOICE, self.onModeChoice, mode_choice)
        sizer.AddMany([(wx.StaticText(self, -1, 'Mode :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (mode_choice, 0, 0)])
        color_button = mode_choice.color_button = wx.Button(self, -1, "", size=(20, 20))
        r, g, b, a, h = activity.couleur
        color_button.SetBackgroundColour(wx.Colour(r, g, b))
        self.Bind(wx.EVT_BUTTON, self.onColorButton, color_button)
        color_button.static = wx.StaticText(self, -1, 'Couleur :')
        color_button.hash_cb = HashComboBox(self)
        color_button.activite = color_button.hash_cb.activite = activity
        color_button.field = color_button.hash_cb.field = ["couleur", "couleur_supplement", "couleur_previsionnel"]
        self.UpdateHash(color_button.hash_cb, activity.couleur)
        self.Bind(wx.EVT_COMBOBOX, self.onHashChange, color_button.hash_cb)
        sizer.AddMany([(color_button.static, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (color_button, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (color_button.hash_cb, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)])
        if creche.tarification_activites:
            sizer.AddMany([(wx.StaticText(self, -1, 'Tarif :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoNumericCtrl(self, creche, 'activites[%d].tarif' % activity.value, precision=2), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)])
        delbutton = wx.BitmapButton(self, -1, delbmp)
        delbutton.index = activity.value        
        if readonly or activity.mode == MODE_SANS_HORAIRES:
            color_button.Disable()
            color_button.static.Disable()
            color_button.hash_cb.Disable()
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_BUTTON, self.activite_del, delbutton)
        self.activites_sizer.Add(sizer, 0, wx.EXPAND|wx.BOTTOM, 5)

    def activite_add(self, event):
        observers['activites'] = time.time()
        activity = Activite()
        colors = [tmp.couleur for tmp in creche.activites.values()]
        for h in (wx.BDIAGONAL_HATCH, wx.CROSSDIAG_HATCH, wx.FDIAGONAL_HATCH, wx.CROSS_HATCH, wx.HORIZONTAL_HATCH, wx.VERTICAL_HATCH, wx.TRANSPARENT, wx.SOLID):
            for color in (wx.RED, wx.BLUE, wx.CYAN, wx.GREEN, wx.LIGHT_GREY):
                r, g, b = color.Get()
                if (r, g, b, 150, h) not in colors:
                    activity.couleur = (r, g, b, 150, h)
                    activity.couleur_supplement = (r, g, b, 250, h)
                    activity.couleur_previsionnel = (r, g, b, 50, h)
                    break
            if activity.couleur:
                break
        else:
            activity.couleur = 0, 0, 0, 150, wx.SOLID
            activity.couleur_supplement = 0, 0, 0, 250, wx.SOLID
            activity.couleur_previsionnel = 0, 0, 0, 50, wx.SOLID
        creche.activites[activity.value] = activity
        history.Append(Delete(creche.activites, activity.value))
        self.line_add(activity)
        self.sizer.Layout()

    def activite_del(self, event):
        observers['activites'] = time.time()
        index = event.GetEventObject().index
        entrees = []
        for inscrit in creche.inscrits:
            for date in inscrit.journees:
                journee = inscrit.journees[date]
                for start, end, activity in journee.activites:
                    if activity == index:
                        entrees.append((inscrit, date))
                        break
        if len(entrees) > 0:
            message = 'Cette activité est utilisée par :\n'
            for inscrit, date in entrees:
                message += '%s %s le %s, ' % (inscrit.prenom, inscrit.nom, GetDateString(date))
            message += '\nVoulez-vous vraiment la supprimer ?'
            dlg = wx.MessageDialog(self, message, 'Confirmation', wx.OK|wx.CANCEL|wx.ICON_WARNING)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_OK:
                return
        for inscrit, date in entrees:
            journee = inscrit.journees[date]
            journee.remove_activities(index)
        history.Append(Insert(creche.activites, index, creche.activites[index]))
        for i, child in enumerate(self.activites_sizer.GetChildren()):
            sizer = child.GetSizer()
            if index == sizer.GetItem(len(sizer.Children)-1).GetWindow().index:
                sizer.DeleteWindows()
                self.activites_sizer.Detach(i)
        creche.activites[index].delete()
        del creche.activites[index]
        self.sizer.Layout()
        self.UpdateContents()

    def UpdateHash(self, hash_cb, color):
        r, g, b, a, h = color
        hash_cb.Clear()
        for i, hash in enumerate((wx.SOLID, wx.TRANSPARENT, wx.BDIAGONAL_HATCH, wx.CROSSDIAG_HATCH, wx.FDIAGONAL_HATCH, wx.CROSS_HATCH, wx.HORIZONTAL_HATCH, wx.VERTICAL_HATCH)):
            hash_cb.Append("", (r, g, b, a, hash))
            if hash == h:
                hash_cb.SetSelection(i)
    
    def onModeChoice(self, event):
        object = event.GetEventObject()
        color_button = object.color_button
        value = object.GetClientData(object.GetSelection())
        color_button.Enable(value != MODE_SANS_HORAIRES)
        color_button.static.Enable(value != MODE_SANS_HORAIRES)
        color_button.hash_cb.Enable(value != MODE_SANS_HORAIRES)
        event.Skip()
        
    def onColorButton(self, event):
        history.Append(None)
        observers['activites'] = time.time()
        obj = event.GetEventObject()
        r, g, b, a, h = couleur = getattr(obj.activite, obj.field[0])
        data = wx.ColourData()
        data.SetColour((r, g, b, a))
        try:
            import wx.lib.agw.cubecolourdialog as CCD
            dlg = CCD.CubeColourDialog(self, data)
            dlg.GetColourData().SetChooseFull(True)
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetColourData()
                colour = data.GetColour()
                r, g, b, a = colour.Red(), colour.Green(), colour.Blue(), colour.Alpha()
        except ImportError:
            dlg = wx.ColourDialog(self, data)
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetColourData()
                r, g, b = data.GetColour()
        couleur = r, g, b, a, h
        for field in obj.field:
            setattr(obj.activite, field, couleur)
            if obj.activite.idx is None:
                obj.activite.create() 
        obj.SetBackgroundColour(wx.Colour(r, g, b))
        self.UpdateHash(obj.hash_cb, couleur)
    
    def onHashChange(self, event):
        history.Append(None)
        observers['activites'] = time.time()
        obj = event.GetEventObject()
        for field in obj.field:
            setattr(obj.activite, field, obj.GetClientData(obj.GetSelection()))
            if obj.activite.idx is None:
                obj.activite.create()

class ChargesTab(AutoTab, PeriodeMixin):
    def __init__(self, parent):
        AutoTab.__init__(self, parent)
        PeriodeMixin.__init__(self, 'charges')
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.annee_choice = wx.Choice(self, -1)
        for annee in range(today.year - 1, today.year + 2):
            self.annee_choice.Append(u"Année %d" % annee, annee)
        self.Bind(wx.EVT_CHOICE, self.EvtAnneeChoice, self.annee_choice)
        sizer.Add(self.annee_choice, 0, wx.TOP, 5)
        sizer2 = wx.FlexGridSizer(12, 2, 5, 5)
        self.charges_ctrls = []
        for m in range(12):
            ctrl = AutoNumericCtrl(self, None, 'charges', precision=2)
            self.charges_ctrls.append(ctrl)
            sizer2.AddMany([wx.StaticText(self, -1, months[m] + ' :'), ctrl])
        sizer.Add(sizer2, 0, wx.ALL, 5)
        self.annee_choice.SetSelection(1)
        self.EvtAnneeChoice(None)
        sizer.Fit(self)
        self.SetSizer(sizer)

    def EvtAnneeChoice(self, evt):
        selected = self.annee_choice.GetSelection()
        annee = self.annee_choice.GetClientData(selected)
        for m in range(12):
            date = datetime.date(annee, m+1, 1)
            if not date in creche.charges:
                creche.charges[date] = Charges(date)
            self.charges_ctrls[m].SetInstance(creche.charges[date])
        
class CafTab(AutoTab, PeriodeMixin):
    def __init__(self, parent):
        AutoTab.__init__(self, parent)
        PeriodeMixin.__init__(self, 'baremes_caf')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(PeriodeChoice(self, BaremeCAF), 0, wx.TOP, 5)
        sizer2 = wx.FlexGridSizer(4, 2, 5, 5)
        sizer2.AddMany([wx.StaticText(self, -1, 'Plancher annuel :'), AutoNumericCtrl(self, None, 'plancher', precision=2)])
        sizer2.AddMany([wx.StaticText(self, -1, 'Plafond annuel :'), AutoNumericCtrl(self, None, 'plafond', precision=2)])
        sizer.Add(sizer2, 0, wx.ALL, 5)
        sizer.Fit(self)
        self.SetSizer(sizer)

    def UpdateContents(self):
        self.SetInstance(creche)
        
class JoursFermeturePanel(AutoTab):
    def __init__(self, parent):
        AutoTab.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        labels_conges = [j[0] for j in jours_fermeture]
        for text in labels_conges:
            checkbox = wx.CheckBox(self, -1, text)
            if readonly:
                checkbox.Disable()
            if text in creche.feries:
                checkbox.SetValue(True)
            self.sizer.Add(checkbox, 0, wx.EXPAND)
            self.Bind(wx.EVT_CHECKBOX, self.feries_check, checkbox)
        self.conges_sizer = wx.BoxSizer(wx.VERTICAL)
        for i, conge in enumerate(creche.conges):
            self.line_add(i)
        self.sizer.Add(self.conges_sizer, 0, wx.ALL, 5)
        button_add = wx.Button(self, -1, u"Ajouter une période de fermeture")
        if readonly:
            button_add.Disable()
        self.sizer.Add(button_add, 0, wx.EXPAND+wx.TOP, 5)
        self.Bind(wx.EVT_BUTTON, self.conges_add, button_add)
        observers['conges'] = 0
#        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
#        sizer2.AddMany([(wx.StaticText(self, -1, u'Nombre de semaines de congés déduites :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoNumericCtrl(self, creche, 'semaines_conges', min=0, precision=0), 0, wx.EXPAND)])
#        self.sizer.Add(sizer2, 0, wx.EXPAND+wx.TOP, 5)
        sizer.Add(self.sizer, 0, wx.EXPAND+wx.ALL, 5)
        self.SetSizer(sizer)

    def UpdateContents(self):
        for i in range(len(self.conges_sizer.GetChildren()), len(creche.conges)):
            self.line_add(i)
        for i in range(len(creche.conges), len(self.conges_sizer.GetChildren())):
            self.line_del()
        self.sizer.Layout()
        AutoTab.UpdateContents(self)

    def line_add(self, index):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, 'Debut :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoDateCtrl(self, creche, 'conges[%d].debut' % index, mois=True, observers=['conges'])])
        sizer.AddMany([(wx.StaticText(self, -1, 'Fin :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoDateCtrl(self, creche, 'conges[%d].fin' % index, mois=True, observers=['conges'])])
        sizer.AddMany([(wx.StaticText(self, -1, u'Libellé :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoTextCtrl(self, creche, 'conges[%d].label' % index, observers=['conges'])])
        sizer.AddMany([(wx.StaticText(self, -1, u'Options :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'conges[%d].options' % index, [(u'Congé', 0), (u'Accueil non facturé', ACCUEIL_NON_FACTURE), (u'Pas de facture pendant ce mois', MOIS_SANS_FACTURE), (u'Uniquement supplément/déduction', MOIS_FACTURE_UNIQUEMENT_HEURES_SUPP)], observers=['conges']), 0, wx.EXPAND)])
        delbutton = wx.BitmapButton(self, -1, delbmp)
        if readonly:
            delbutton.Disable()
        delbutton.index = index
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        self.Bind(wx.EVT_BUTTON, self.conges_del, delbutton)
        self.conges_sizer.Add(sizer)

    def line_del(self):
        index = len(self.conges_sizer.GetChildren()) - 1
        sizer = self.conges_sizer.GetItem(index)
        sizer.DeleteWindows()
        self.conges_sizer.Detach(index)

    def conges_add(self, event):
        observers['conges'] = time.time()
        history.Append(Delete(creche.conges, -1))
        creche.add_conge(Conge(creche))
        self.line_add(len(creche.conges) - 1)
        self.sizer.Layout()

    def conges_del(self, event):
        observers['conges'] = time.time()
        index = event.GetEventObject().index
        history.Append(Insert(creche.conges, index, creche.conges[index]))
        self.line_del()
        creche.conges[index].delete()
        del creche.conges[index]
        self.sizer.Layout()
        self.UpdateContents()

    def feries_check(self, event):
        label = event.GetEventObject().GetLabelText()
        if event.IsChecked():
            conge = Conge(creche, creation=False)
            conge.debut = label
            conge.create()
            creche.add_conge(conge)
        else:
            conge = creche.feries[label]
            del creche.feries[label]
            conge.delete()            
        history.Append(None)

class ReservatairesTab(AutoTab):
    def __init__(self, parent):
        AutoTab.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.reservataires_sizer = wx.BoxSizer(wx.VERTICAL)
        for i, reservataire in enumerate(creche.reservataires):
            self.line_add(i)
        self.sizer.Add(self.reservataires_sizer, 0, wx.ALL, 5)
        button_add = wx.Button(self, -1, u'Nouveau réservataire')
        if readonly:
            button_add.Disable()
        self.sizer.Add(button_add, 0, wx.EXPAND+wx.TOP, 5)
        self.Bind(wx.EVT_BUTTON, self.reservataire_add, button_add)
        observers['reservataires'] = 0
#        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
#        sizer2.AddMany([(wx.StaticText(self, -1, u'Nombre de semaines de congés déduites :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoNumericCtrl(self, creche, 'semaines_conges', min=0, precision=0), 0, wx.EXPAND)])
#        self.sizer.Add(sizer2, 0, wx.EXPAND+wx.TOP, 5)
        sizer.Add(self.sizer, 0, wx.EXPAND+wx.ALL, 5)
        self.SetSizer(sizer)

    def UpdateContents(self):
        for i in range(len(self.reservataires_sizer.GetChildren()), len(creche.reservataires)):
            self.line_add(i)
        for i in range(len(creche.reservataires), len(self.reservataires_sizer.GetChildren())):
            self.line_del()
        self.sizer.Layout()
        AutoTab.UpdateContents(self)

    def line_add(self, index):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, 'Debut :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoDateCtrl(self, creche, 'reservataires[%d].debut' % index, mois=True, observers=['reservataires'])])
        sizer.AddMany([(wx.StaticText(self, -1, 'Fin :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoDateCtrl(self, creche, 'reservataires[%d].fin' % index, mois=True, observers=['reservataires'])])
        sizer.AddMany([(wx.StaticText(self, -1, u'Nom :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoTextCtrl(self, creche, 'reservataires[%d].nom' % index, observers=['reservataires'])])
        sizer.AddMany([(wx.StaticText(self, -1, u'Places :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoNumericCtrl(self, creche, 'reservataires[%d].places' % index, precision=0, observers=['reservataires'])])
        sizer.AddMany([(wx.StaticText(self, -1, 'Adresse :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoTextCtrl(self, creche, 'reservataires[%d].adresse' % index, observers=['reservataires'])])
        sizer.AddMany([(wx.StaticText(self, -1, 'Code Postal :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoNumericCtrl(self, creche, 'reservataires[%d].code_postal' % index, precision=0, observers=['reservataires'])])
        sizer.AddMany([(wx.StaticText(self, -1, 'Ville :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoTextCtrl(self, creche, 'reservataires[%d].ville' % index, observers=['reservataires'])])
        sizer.AddMany([(wx.StaticText(self, -1, u'Téléphone :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoPhoneCtrl(self, creche, 'reservataires[%d].telephone' % index, observers=['reservataires'])])
        sizer.AddMany([(wx.StaticText(self, -1, 'E-mail :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), AutoTextCtrl(self, creche, 'reservataires[%d].email' % index, observers=['reservataires'])])
        
        # sizer.AddMany([(wx.StaticText(self, -1, u'Options :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'reservataires[%d].options' % index, [(u'Congé', 0), (u'Accueil non facturé', ACCUEIL_NON_FACTURE), (u'Pas de facture pendant ce mois', MOIS_SANS_FACTURE), (u'Uniquement supplément/déduction', MOIS_FACTURE_UNIQUEMENT_HEURES_SUPP)], observers=['reservataires']), 0, wx.EXPAND)])
        delbutton = wx.BitmapButton(self, -1, delbmp)
        if readonly:
            delbutton.Disable()
        delbutton.index = index
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        self.Bind(wx.EVT_BUTTON, self.reservataire_del, delbutton)
        self.reservataires_sizer.Add(sizer)

    def line_del(self):
        index = len(self.reservataires_sizer.GetChildren()) - 1
        sizer = self.reservataires_sizer.GetItem(index)
        sizer.DeleteWindows()
        self.reservataires_sizer.Detach(index)

    def reservataire_add(self, event):
        observers['reservataires'] = time.time()
        history.Append(Delete(creche.reservataires, -1))
        creche.reservataires.append(Reservataire())
        self.line_add(len(creche.reservataires) - 1)
        self.sizer.FitInside(self)
        self.sizer.Layout()

    def reservataire_del(self, event):
        observers['reservataires'] = time.time()
        index = event.GetEventObject().index
        history.Append(Insert(creche.reservataires, index, creche.reservataires[index]))
        self.line_del()
        creche.reservataires[index].delete()
        del creche.reservataires[index]
        self.sizer.FitInside(self)
        self.sizer.Layout()
        self.UpdateContents()

class ParametersPanel(AutoTab):
    def __init__(self, parent):
        AutoTab.__init__(self, parent)
        observers['tarifs'] = 0
        observers['plages'] = 0
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.FlexGridSizer(0, 2, 5, 5)
        sizer.AddGrowableCol(1, 1)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.ouverture_cb = AutoTimeCtrl(self, creche, "ouverture")
        self.fermeture_cb = AutoTimeCtrl(self, creche, "fermeture")
        self.ouverture_cb.check_function = self.ouverture_check
        self.fermeture_cb.check_function = self.fermeture_check
        self.Bind(wx.EVT_CHOICE, self.onOuverture, self.ouverture_cb)
        self.Bind(wx.EVT_CHOICE, self.onOuverture, self.fermeture_cb)
        sizer2.AddMany([(self.ouverture_cb, 1, wx.EXPAND), (self.ouverture_cb.spin, 0, wx.EXPAND), (wx.StaticText(self, -1, '-'), 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10), (self.fermeture_cb, 1, wx.EXPAND), (self.fermeture_cb.spin, 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Heures d\'ouverture :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (sizer2, 0, wx.EXPAND)])
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.affichage_min_cb = AutoTimeCtrl(self, creche, "affichage_min")
        self.affichage_max_cb = AutoTimeCtrl(self, creche, "affichage_max")
        self.Bind(wx.EVT_CHOICE, self.onAffichage, self.affichage_min_cb)
        self.Bind(wx.EVT_CHOICE, self.onAffichage, self.affichage_max_cb)
        sizer2.AddMany([(self.affichage_min_cb, 1, wx.EXPAND), (self.affichage_min_cb.spin, 0, wx.EXPAND), (wx.StaticText(self, -1, '-'), 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10), (self.affichage_max_cb, 1, wx.EXPAND), (self.affichage_max_cb.spin, 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Heures affichées sur le planning :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (sizer2, 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Granularité du planning :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'granularite', [('10 minutes', 10), ('1/4 heure', 15), ('1/2 heure', 30), ('1 heure', 60)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Ordre d'affichage sur le planning :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'tri_planning', [(u'Par prénom', TRI_PRENOM), ('Par nom', TRI_NOM), ('Par groupe', TRI_GROUPE)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Préinscriptions :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'preinscriptions', [(u'Géré', True), (u'Non géré', False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Présences prévisionnelles :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'presences_previsionnelles', [(u'Géré', True), (u'Non géré', False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Présences supplémentaires :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'presences_supplementaires', [(u'Géré', True), (u'Non géré', False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Modes d'inscription :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'modes_inscription', [(u'Crèche à plein-temps uniquement', MODE_5_5), ('Tous modes', MODE_5_5+MODE_4_5+MODE_3_5+MODE_HALTE_GARDERIE)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Mode d'accueil par défaut :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'mode_accueil_defaut', items=ModeAccueilItems), 0, wx.EXPAND)])
        mode_facturation_choice = AutoChoiceCtrl(self, creche, 'mode_facturation', modes_facturation)
        self.Bind(wx.EVT_CHOICE, self.onModeFacturationChoice, mode_facturation_choice)
        sizer.AddMany([(wx.StaticText(self, -1, u'Mode de facturation :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (mode_facturation_choice, 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, ''), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'repartition', [(u'Avec mensualisation', REPARTITION_MENSUALISATION), (u'Avec mensualisation, mois incomplets aux même tarif', REPARTITION_MENSUALISATION_DEBUT_FIN_INCLUS), (u'Sans mensualisation', REPARTITION_SANS_MENSUALISATION)]), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, ''), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'temps_facturation', temps_facturation), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Revenus pris en compte :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'periode_revenus', [(u'Année N-2', REVENUS_YM2), (u'CAFPRO', REVENUS_CAFPRO)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Clôture des factures :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'cloture_factures', [(u'Activée', True), (u'Désactivée', False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Mode de facturation des périodes d'adaptation :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'facturation_periode_adaptation', modes_facturation_adaptation), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Mode d'arrondi des horaires des enfants :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'arrondi_heures', [(u"Pas d'arrondi", SANS_ARRONDI), (u"Arrondi à l'heure", ARRONDI_HEURE), (u"Arrondi à l'heure avec marge d'1/2heure", ARRONDI_HEURE_MARGE_DEMI_HEURE), (u"Arrondi à la demi heure", ARRONDI_DEMI_HEURE), (u"Arrondi des heures d'arrivée et de départ", ARRONDI_HEURE_ARRIVEE_DEPART)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Mode d'arrondi de la facturation des enfants :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'arrondi_facturation', [(u"Pas d'arrondi", SANS_ARRONDI), (u"Arrondi à l'heure", ARRONDI_HEURE), (u"Arrondi à la demi heure", ARRONDI_DEMI_HEURE), (u"Arrondi des heures d'arrivée et de départ", ARRONDI_HEURE_ARRIVEE_DEPART)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Mode d'arrondi des horaires des salariés :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'arrondi_heures_salaries', [(u"Pas d'arrondi", SANS_ARRONDI), (u"Arrondi à l'heure", ARRONDI_HEURE), (u"Arrondi des heures d'arrivée et de départ", ARRONDI_HEURE_ARRIVEE_DEPART)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Gestion des absences prévues au contrat :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'conges_inscription', [('Non', 0), (u'Oui', 1), (u"Oui, avec gestion d'heures supplémentaires", 2)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Déduction des jours fériés et absences prévues au contrat :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'facturation_jours_feries', [(u"En semaines (nombre de semaines entré à l'inscription)", JOURS_FERIES_NON_DEDUITS), (u"En jours (décompte précis des jours de présence sur l'ensemble du contrat)", JOURS_FERIES_DEDUITS_ANNUELLEMENT)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Tarification des activités :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'tarification_activites', [(u'Non géré', ACTIVITES_NON_FACTUREES), (u'A la journée', ACTIVITES_FACTUREES_JOURNEE), (u"Période d'adaptation, à la journée", ACTIVITES_FACTUREES_JOURNEE_PERIODE_ADAPTATION)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Traitement des absences pour maladie :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'traitement_maladie', [(u"Avec carence en jours ouvrés", DEDUCTION_MALADIE_AVEC_CARENCE_JOURS_OUVRES), (u"Avec carence en jours calendaires", DEDUCTION_MALADIE_AVEC_CARENCE_JOURS_CALENDAIRES), ("Sans carence", DEDUCTION_MALADIE_SANS_CARENCE)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Durée de la carence :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoNumericCtrl(self, creche, 'minimum_maladie', min=0, precision=0), 0, 0)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Traitement des absences pour hospitalisation :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'gestion_maladie_hospitalisation', [(u"Géré", True), (u"Non géré", False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Traitement des absences pour maladie sans justificatif :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'gestion_maladie_sans_justificatif', [(u"Géré", True), (u"Non géré", False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Traitement des absences non prévenues :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'gestion_absences_non_prevenues', [(u"Géré", True), (u"Non géré", False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Traitement des préavis de congés :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'gestion_preavis_conges', [(u"Géré", True), (u"Non géré", False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Traitement des départs anticipés :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'gestion_depart_anticipe', [(u"Géré", True), (u"Non géré", False)]), 0, wx.EXPAND)])        
        sizer.AddMany([(wx.StaticText(self, -1, u"Gestion d'alertes :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'gestion_alertes', [(u'Activée', True), (u'Désactivée', False)]), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u"Age maximum des enfants :"), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoNumericCtrl(self, creche, 'age_maximum', min=0, max=5, precision=0), 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'Alerte dépassement capacité dans les plannings :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoChoiceCtrl(self, creche, 'alerte_depassement_planning', [(u"Activée", True), (u"Désactivée", False)]), 0, wx.EXPAND)])        
        self.sizer.Add(sizer, 0, wx.EXPAND|wx.ALL, 5)

        self.plages_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, u"Plages horaires spéciales"), wx.VERTICAL)
        self.plages_sizer = wx.BoxSizer(wx.VERTICAL)
        for i, plage in enumerate(creche.plages_horaires):
            self.line_plage_add(i)
        self.plages_box_sizer.Add(self.plages_sizer, 0, wx.EXPAND|wx.ALL, 5)
        button_add = wx.Button(self, -1, u'Nouvelle plage horaire')
        if readonly:
            button_add.Disable()        
        self.plages_box_sizer.Add(button_add, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.add_plage, button_add)
        self.sizer.Add(self.plages_box_sizer, 0, wx.EXPAND|wx.ALL, 5)
                
        self.tarifs_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, u"Tarifs spéciaux"), wx.VERTICAL)
        self.tarifs_sizer = wx.BoxSizer(wx.VERTICAL)
        for i, tarif in enumerate(creche.tarifs_speciaux):
            self.line_tarif_add(i)
        self.tarifs_box_sizer.Add(self.tarifs_sizer, 0, wx.EXPAND|wx.ALL, 5)
        button_add = wx.Button(self, -1, u'Nouveau tarif spécial')
        if readonly:
            button_add.Disable()        
        self.tarifs_box_sizer.Add(button_add, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.add_tarif, button_add)
        self.sizer.Add(self.tarifs_box_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(self.sizer)

    def line_plage_add(self, index):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        debut_ctrl = AutoTimeCtrl(self, creche, 'plages_horaires[%d].debut' % index, observers=['plages'])
        fin_ctrl = AutoTimeCtrl(self, creche, 'plages_horaires[%d].fin' % index, observers=['plages']) 
        sizer.AddMany([(wx.StaticText(self, -1, u'Plage horaire :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (debut_ctrl, 1, wx.EXPAND), (debut_ctrl.spin, 0, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, u'-'), 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10), (fin_ctrl, 1, wx.EXPAND), (fin_ctrl.spin, 0, wx.EXPAND)])
        sizer.AddMany([(AutoChoiceCtrl(self, creche, 'plages_horaires[%d].flags' % index, items=[("Fermeture", PLAGE_FERMETURE), (u"Insécable", PLAGE_INSECABLE)], observers=['plages']), 1, wx.LEFT|wx.EXPAND, 5)])
        delbutton = wx.BitmapButton(self, -1, delbmp)
        delbutton.index = index
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_BUTTON, self.remove_plage, delbutton)
        self.plages_sizer.Add(sizer, 0, wx.EXPAND|wx.BOTTOM, 5)
        if readonly:
            delbutton.Disable()

    def line_plage_del(self):
        index = len(self.plages_sizer.GetChildren()) - 1
        sizer = self.plages_sizer.GetItem(index)
        sizer.DeleteWindows()
        self.plages_sizer.Detach(index)

    def add_plage(self, event):
        observers['plages'] = time.time()
        history.Append(Delete(creche.plages_horaires, -1))
        creche.plages_horaires.append(PlageHoraire())
        self.line_plage_add(len(creche.plages_horaires) - 1)
        self.sizer.FitInside(self)

    def remove_plage(self, event):
        observers['plages'] = time.time()
        index = event.GetEventObject().index
        history.Append(Insert(creche.plages_horaires, index, creche.plages_horaires[index]))
        self.line_plage_del()
        creche.plages_horaires[index].delete()
        del creche.plages_horaires[index]
        self.sizer.FitInside(self)
        self.UpdateContents()
    
    def line_tarif_add(self, index):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, u'Libellé :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoTextCtrl(self, creche, 'tarifs_speciaux[%d].label' % index, observers=['tarifs']), 1, wx.RIGHT|wx.EXPAND, 5)])
        sizer.AddMany([(AutoChoiceCtrl(self, creche, 'tarifs_speciaux[%d].type' % index, items=[("Majoration", TARIF_SPECIAL_MAJORATION), (u"Réduction", TARIF_SPECIAL_REDUCTION)]), 1, wx.EXPAND)])
        sizer.AddMany([(wx.StaticText(self, -1, 'Valeur :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (AutoNumericCtrl(self, creche, 'tarifs_speciaux[%d].valeur' % index, precision=2), 1, wx.RIGHT|wx.EXPAND, 5)])
        sizer.AddMany([(AutoChoiceCtrl(self, creche, 'tarifs_speciaux[%d].unite' % index, items=[(u"€", TARIF_SPECIAL_UNITE_EUROS), (u"%", TARIF_SPECIAL_UNITE_POURCENTAGE), (u"€/heure", TARIF_SPECIAL_UNITE_EUROS_PAR_HEURE)]), 1, wx.EXPAND)])
        delbutton = wx.BitmapButton(self, -1, delbmp)
        delbutton.index = index
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_BUTTON, self.remove_tarif, delbutton)
        self.tarifs_sizer.Add(sizer, 0, wx.EXPAND|wx.BOTTOM, 5)
        if readonly:
            delbutton.Disable()

    def line_tarif_del(self):
        index = len(self.tarifs_sizer.GetChildren()) - 1
        sizer = self.tarifs_sizer.GetItem(index)
        sizer.DeleteWindows()
        self.tarifs_sizer.Detach(index)

    def add_tarif(self, event):
        observers['tarifs'] = time.time()
        history.Append(Delete(creche.tarifs_speciaux, -1))
        creche.tarifs_speciaux.append(TarifSpecial())
        self.line_tarif_add(len(creche.tarifs_speciaux) - 1)
        self.sizer.FitInside(self)

    def remove_tarif(self, event):
        observers['tarifs'] = time.time()
        index = event.GetEventObject().index
        history.Append(Insert(creche.tarifs_speciaux, index, creche.tarifs_speciaux[index]))
        self.line_tarif_del()
        creche.tarifs_speciaux[index].delete()
        del creche.tarifs_speciaux[index]
        self.sizer.FitInside(self)
        self.UpdateContents()

    def onModeFacturationChoice(self, event):
        object = event.GetEventObject()
        value = object.GetClientData(object.GetSelection())
        self.GetParent().DisplayTarifHorairePanel(value in (FACTURATION_PAJE, FACTURATION_HORAIRES_REELS))
        self.GetParent().DisplayTauxEffortPanel(value == FACTURATION_PSU_TAUX_PERSONNALISES)
        event.Skip()
            
    def ouverture_check(self, ouverture, a, b):
        return a >= ouverture * 4
    
    def fermeture_check(self, fermeture, a, b):
        return b <= fermeture * 4
    
    def onOuverture(self, event):
        errors = []
        obj = event.GetEventObject()
        value = event.GetClientData()
        for inscrit in creche.inscrits:
            for inscription in inscrit.inscriptions:
                for j, jour in enumerate(inscription.reference):
                    for a, b, v in jour.activites.keys():
                        if not obj.check_function(value, a, b):
                            errors.append((inscrit, jour, " (%s)" % periodestr(inscription), days[j%7].lower()))
            for j in inscrit.journees.keys():
                jour = inscrit.journees[j]
                for a, b, v in jour.activites.keys():
                    if not obj.check_function(value, a, b):
                        errors.append((inscrit, jour, "", date2str(j)))
                
        if errors:
            message = u"Diminuer la période d'ouverture changera les plannings des enfants suivants :\n"
            for inscrit, jour, info, date in errors:
                message += '  %s %s%s le %s\n' % (inscrit.prenom, inscrit.nom, info, date)
            message += 'Confirmer ?'
            dlg = wx.MessageDialog(self, message, 'Confirmation', wx.OK|wx.CANCEL|wx.ICON_WARNING)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_OK:
                obj.UpdateContents()
                return
        obj.AutoChange(value)
# TODO
#        for inscrit, jour, info, date in errors:
#            for i in range(0, int(creche.ouverture*4)) + range(int(creche.fermeture*4), TAILLE_TABLE_ACTIVITES):
#                jour.values[i] = 0
#            jour.save()
        if creche.affichage_min > creche.ouverture:
            creche.affichage_min = creche.ouverture
            self.affichage_min_cb.UpdateContents()
        if creche.affichage_max < creche.fermeture:
            creche.affichage_max = creche.fermeture
            self.affichage_max_cb.UpdateContents()
            
    def onAffichage(self, event):
        obj = event.GetEventObject()
        value = event.GetClientData()
        error = False
        if obj is self.affichage_min_cb:
            if value > creche.ouverture:
                error = True
        else:
            if value < creche.fermeture:
                error = True
        if error:
            dlg = wx.MessageDialog(self, u"La période d'affichage doit couvrir au moins l'amplitude horaire de la structure !", "Erreur", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            obj.UpdateContents()
        else:
            obj.AutoChange(value)

    def onPause(self, event):
        obj = event.GetEventObject()
        value = event.GetClientData()
        obj.AutoChange(value)
            
class TarifHorairePanel(AutoTab):
    def __init__(self, parent):
        AutoTab.__init__(self, parent)
        self.delbmp = wx.Bitmap(GetBitmapFile("remove.png"), wx.BITMAP_TYPE_PNG)
        addbutton = wx.Button(self, -1, "Ajouter un cas")
        if readonly:
            addbutton.Disable()
        addbutton.index = 0
        self.Bind(wx.EVT_BUTTON, self.onAdd, addbutton)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(addbutton, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP, 5)
        self.controls = []
        if creche.formule_taux_horaire:
            for i, cas in enumerate(creche.formule_taux_horaire):
                self.line_add(i, cas[0], cas[1])
        self.SetSizer(self.sizer)
        self.Layout()
        
    def line_add(self, index, condition="", taux=0.0):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)
        cas = wx.StaticText(self, -1, "[Cas %d]" % (index+1))
        cas.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(cas, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        condition_ctrl = wx.TextCtrl(self, -1, condition)
        condition_ctrl.index = index
        sizer1.AddMany([(wx.StaticText(self, -1, 'Condition :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (condition_ctrl, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)])
        taux_ctrl = wx.TextCtrl(self, -1, str(taux))
        taux_ctrl.index = index
        sizer1.AddMany([(wx.StaticText(self, -1, 'Tarif horaire :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (taux_ctrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)])
        delbutton = wx.BitmapButton(self, -1, self.delbmp)
        delbutton.index = index
        addbutton = wx.Button(self, -1, "Ajouter un cas")
        addbutton.index = index+1
        sizer1.Add(delbutton, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(sizer1, 0, wx.EXPAND)
        sizer.Add(addbutton, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP, 5)
        self.Bind(wx.EVT_TEXT, self.onConditionChange, condition_ctrl)
        self.Bind(wx.EVT_TEXT, self.onTauxChange, taux_ctrl)
        self.Bind(wx.EVT_BUTTON, self.onDel, delbutton)
        self.Bind(wx.EVT_BUTTON, self.onAdd, addbutton)
        self.controls.insert(index, (cas, condition_ctrl, taux_ctrl, delbutton, addbutton))
        self.sizer.Insert(index+1, sizer, 0, wx.EXPAND|wx.BOTTOM, 5)
        if readonly:
            condition_ctrl.Disable()
            taux_ctrl.Disable()
            delbutton.Disable()
            addbutton.Disable()
     

    def onAdd(self, event):
        object = event.GetEventObject()
        self.line_add(object.index)
        if creche.formule_taux_horaire is None:
            creche.formule_taux_horaire = [["", 0.0]]
        else:
            creche.formule_taux_horaire.insert(object.index, ["", 0.0])
        creche.update_formule_taux_horaire()
        for i in range(object.index+1, len(self.controls)):
            self.controls[i][0].SetLabel("[Cas %d]" % (i+1))
            for control in self.controls[i][1:]:
                control.index += 1
        self.sizer.FitInside(self)
        history.Append(None)
    
    def onDel(self, event):
        index = event.GetEventObject().index
        sizer = self.sizer.GetItem(index+1)
        sizer.DeleteWindows()
        self.sizer.Detach(index+1)
        del self.controls[index]
        if len(creche.formule_taux_horaire) == 1:
            creche.formule_taux_horaire = None
        else:
            del creche.formule_taux_horaire[index]
        creche.update_formule_taux_horaire()
        for i in range(index, len(self.controls)):
            self.controls[i][0].SetLabel("[Cas %d]" % (i+1))
            for control in self.controls[i][1:]:
                control.index -= 1
        self.sizer.FitInside(self)
        history.Append(None)
    
    def onConditionChange(self, event):
        object = event.GetEventObject()
        creche.formule_taux_horaire[object.index][0] = object.GetValue()
        creche.update_formule_taux_horaire()
        if creche.test_formule_taux_horaire(object.index):
            object.SetBackgroundColour(wx.WHITE)
        else:
            object.SetBackgroundColour(wx.RED)
        object.Refresh()
        history.Append(None)
        
    def onTauxChange(self, event):
        object = event.GetEventObject()
        creche.formule_taux_horaire[object.index][1] = float(object.GetValue())
        creche.update_formule_taux_horaire()
        history.Append(None)
        
class TauxEffortPanel(AutoTab):
    def __init__(self, parent):
        AutoTab.__init__(self, parent)
        self.delbmp = wx.Bitmap(GetBitmapFile("remove.png"), wx.BITMAP_TYPE_PNG)
        addbutton = wx.Button(self, -1, "Ajouter un cas")
        addbutton.index = 0
        self.Bind(wx.EVT_BUTTON, self.onAdd, addbutton)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(addbutton, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP, 5)
        self.controls = []
        if creche.formule_taux_effort:
            for i, cas in enumerate(creche.formule_taux_effort):
                self.line_add(i, cas[0], cas[1])
        self.SetSizer(self.sizer)
        self.Layout()
        
    def line_add(self, index, condition="", taux=0.0):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)
        cas = wx.StaticText(self, -1, "[Cas %d]" % (index+1))
        cas.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(cas, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        condition_ctrl = wx.TextCtrl(self, -1, condition)
        condition_ctrl.index = index
        sizer1.AddMany([(wx.StaticText(self, -1, 'Condition :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (condition_ctrl, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)])
        taux_ctrl = wx.TextCtrl(self, -1, str(taux))
        taux_ctrl.index = index
        sizer1.AddMany([(wx.StaticText(self, -1, "Taux d'effort :"), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5), (taux_ctrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)])
        delbutton = wx.BitmapButton(self, -1, self.delbmp)
        delbutton.index = index
        addbutton = wx.Button(self, -1, "Ajouter un cas")
        addbutton.index = index+1
        sizer1.Add(delbutton, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(sizer1, 0, wx.EXPAND)
        sizer.Add(addbutton, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP, 5)
        self.Bind(wx.EVT_TEXT, self.onConditionChange, condition_ctrl)
        self.Bind(wx.EVT_TEXT, self.onTauxChange, taux_ctrl)
        self.Bind(wx.EVT_BUTTON, self.onDel, delbutton)
        self.Bind(wx.EVT_BUTTON, self.onAdd, addbutton)
        self.controls.insert(index, (cas, condition_ctrl, taux_ctrl, delbutton, addbutton))
        self.sizer.Insert(index+1, sizer, 0, wx.EXPAND|wx.BOTTOM, 5)         

    def onAdd(self, event):
        object = event.GetEventObject()
        self.line_add(object.index)
        if creche.formule_taux_effort is None:
            creche.formule_taux_effort = [["", 0.0]]
        else:
            creche.formule_taux_effort.insert(object.index, ["", 0.0])
        creche.update_formule_taux_effort()
        for i in range(object.index+1, len(self.controls)):
            self.controls[i][0].SetLabel("[Cas %d]" % (i+1))
            for control in self.controls[i][1:]:
                control.index += 1
        self.sizer.FitInside(self)
        history.Append(None)
    
    def onDel(self, event):
        index = event.GetEventObject().index
        sizer = self.sizer.GetItem(index+1)
        sizer.DeleteWindows()
        self.sizer.Detach(index+1)
        del self.controls[index]
        if len(creche.formule_taux_effort) == 1:
            creche.formule_taux_effort = None
        else:
            del creche.formule_taux_effort[index]
        creche.update_formule_taux_effort()
        for i in range(index, len(self.controls)):
            self.controls[i][0].SetLabel("[Cas %d]" % (i+1))
            for control in self.controls[i][1:]:
                control.index -= 1
        self.sizer.FitInside(self)
        history.Append(None)
    
    def onConditionChange(self, event):
        object = event.GetEventObject()
        creche.formule_taux_effort[object.index][0] = object.GetValue()
        creche.update_formule_taux_effort()
        if creche.test_formule_taux_effort(object.index):
            object.SetBackgroundColour(wx.WHITE)
        else:
            object.SetBackgroundColour(wx.RED)
        object.Refresh()
        history.Append(None)
        
    def onTauxChange(self, event):
        object = event.GetEventObject()
        creche.formule_taux_effort[object.index][1] = float(object.GetValue())
        creche.update_formule_taux_effort()
        history.Append(None)    

profiles = [("Administrateur", PROFIL_ALL),
            ("Equipe", PROFIL_ALL-PROFIL_ADMIN),
            ("Bureau", PROFIL_BUREAU),
            (u"Trésorier", PROFIL_TRESORIER),
            ("Inscriptions", PROFIL_INSCRIPTIONS),
            (u"Saisie présences", PROFIL_SAISIE_PRESENCES),
            (u"Utilisateur lecture seule", PROFIL_LECTURE_SEULE),
            ]

class UsersTab(AutoTab):
    def __init__(self, parent):
        global delbmp
        delbmp = wx.Bitmap(GetBitmapFile("remove.png"), wx.BITMAP_TYPE_PNG)
        AutoTab.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.users_sizer = wx.BoxSizer(wx.VERTICAL)
        for i, user in enumerate(creche.users):
            self.line_add(i)
        self.sizer.Add(self.users_sizer, 0, wx.EXPAND|wx.ALL, 5)
        button_add = wx.Button(self, -1, 'Nouvel utilisateur')
        if readonly:
            button_add.Disable()      
        self.sizer.Add(button_add, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.user_add, button_add)
        self.SetSizer(self.sizer)

    def UpdateContents(self):
        for i in range(len(self.users_sizer.GetChildren()), len(creche.users)):
            self.line_add(i)
        for i in range(len(creche.users), len(self.users_sizer.GetChildren())):
            self.line_del()
        self.sizer.Layout()
        AutoTab.UpdateContents(self)

    def line_add(self, index):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(wx.StaticText(self, -1, 'Login :'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoTextCtrl(self, creche, 'users[%d].login' % index), 0, wx.ALIGN_CENTER_VERTICAL)])
        sizer.AddMany([(wx.StaticText(self, -1, 'Mot de passe :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), (AutoTextCtrl(self, creche, 'users[%d].password' % index), 0, wx.ALIGN_CENTER_VERTICAL)])
        profile_choice = AutoChoiceCtrl(self, creche, 'users[%d].profile' % index, items=profiles)
        profile_choice.index = index
        self.Bind(wx.EVT_CHOICE, self.user_modify_profile, profile_choice)
        sizer.AddMany([(wx.StaticText(self, -1, 'Profil :'), 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10), profile_choice])
        delbutton = wx.BitmapButton(self, -1, delbmp, style=wx.NO_BORDER)
        if readonly:
            delbutton.Disable()              
        delbutton.index = index
        sizer.Add(delbutton, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        self.Bind(wx.EVT_BUTTON, self.user_del, delbutton)
        self.users_sizer.Add(sizer)

    def line_del(self):
        index = len(self.users_sizer.GetChildren()) - 1
        sizer = self.users_sizer.GetItem(index)
        sizer.DeleteWindows()
        self.users_sizer.Detach(index)

    def user_add(self, event):
        history.Append(Delete(creche.users, -1))
        creche.users.append(User())
        self.line_add(len(creche.users) - 1)
        self.sizer.Layout()

    def user_del(self, event):
        index = event.GetEventObject().index
        nb_admins = len([user for i, user in enumerate(creche.users) if (i != index and user.profile == PROFIL_ALL)])
        if len(creche.users) == 1 or nb_admins > 0:
            history.Append(Insert(creche.users, index, creche.users[index]))
            self.line_del()
            creche.users[index].delete()
            del creche.users[index]
            self.sizer.Layout()
            self.UpdateContents()
        else:
            dlg = wx.MessageDialog(self, "Il faut au moins un administrateur", 'Message', wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def user_modify_profile(self, event):
        obj = event.GetEventObject()
        index = obj.index
        if creche.users[index].profile == PROFIL_ALL and event.GetClientData() != PROFIL_ALL:
            nb_admins = len([user for i, user in enumerate(creche.users) if (i != index and user.profile == PROFIL_ALL)])
            if nb_admins == 0:
                dlg = wx.MessageDialog(self, "Il faut au moins un administrateur", "Message", wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                event.Skip(False)
                obj.SetSelection(0) # PROFIL_ALL
            else:
                event.Skip(True)
        else:
            event.Skip(True)
            
class ParametresNotebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, style=wx.LB_DEFAULT)
        self.AddPage(CrecheTab(self), 'Structure')
        self.professeurs_tab = ProfesseursTab(self)
        if creche.type == TYPE_GARDERIE_PERISCOLAIRE:
            self.AddPage(self.professeurs_tab, 'Professeurs')
            self.professeurs_tab_displayed = 1
        else:
            self.professeurs_tab.Show(False)
            self.professeurs_tab_displayed = 0
        self.AddPage(ResponsabilitesTab(self), u'Responsabilités')
        if IsTemplateFile("Synthese financiere.ods"):
            self.AddPage(ChargesTab(self), u'Charges')
            self.charges_tab_displayed = 1
        else:
            self.charges_tab_displayed = 0
        self.AddPage(CafTab(self), 'C.A.F.')
        self.AddPage(JoursFermeturePanel(self), u"Fermeture de l'établissement")
        self.AddPage(ActivitesTab(self), u'Couleurs / Activités')
        self.AddPage(ParametersPanel(self), u'Paramètres')
        self.tarif_horaire_panel = TarifHorairePanel(self)
        if creche.mode_facturation in (FACTURATION_PAJE, FACTURATION_HORAIRES_REELS):
            self.AddPage(self.tarif_horaire_panel, 'Tarif horaire')
            self.tarif_horaire_panel_displayed = 1
        else:
            self.tarif_horaire_panel.Show(False)
            self.tarif_horaire_panel_displayed = 0
        self.taux_effort_panel = TauxEffortPanel(self)
        if creche.mode_facturation == FACTURATION_PSU_TAUX_PERSONNALISES:
            self.AddPage(self.taux_effort_panel, "Taux d'effort")
            self.taux_effort_panel_displayed = 1
        else:
            self.taux_effort_panel.Show(False)
            self.taux_effort_panel_displayed = 0
        self.AddPage(UsersTab(self), u'Utilisateurs et mots de passe')
        if config.options & RESERVATAIRES:
            self.AddPage(ReservatairesTab(self), u'Réservataires')
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, event):
        page = self.GetPage(event.GetSelection())
        page.UpdateContents()
        event.Skip()

    def UpdateContents(self):
        page = self.GetCurrentPage()
        page.UpdateContents()
        
    def DisplayTarifHorairePanel(self, enable):
        if enable == self.tarif_horaire_panel_displayed:
            return
        else:
            self.tarif_horaire_panel.Show(enable)
            tab_index = 7 + self.professeurs_tab_displayed + self.charges_tab_displayed
            if enable:
                self.InsertPage(tab_index, self.tarif_horaire_panel, u'Tarif horaire')
            else:
                self.RemovePage(tab_index)

        self.tarif_horaire_panel_displayed = enable
        self.Layout()
        
    def DisplayTauxEffortPanel(self, enable):
        if enable == self.taux_effort_panel_displayed:
            return
        else:
            self.taux_effort_panel.Show(enable)
            tab_index = 7 + self.professeurs_tab_displayed + self.charges_tab_displayed + self.tarif_horaire_panel_displayed
            if enable:
                self.InsertPage(tab_index, self.taux_effort_panel, u"Taux d'effort")
            else:
                self.RemovePage(tab_index)

        self.taux_effort_panel_displayed = enable
        self.Layout()
        
    def DisplayProfesseursTab(self, enable):
        if enable == self.professeurs_tab_displayed:
            return
        else:
            self.professeurs_tab.Show(enable)
            if enable:
                self.InsertPage(2, self.professeurs_tab, 'Professeurs')
            else:
                self.RemovePage(2)

        self.professeurs_tab_displayed = enable
        self.Layout()

class ConfigurationPanel(GPanel):
    name = "Configuration"
    bitmap = GetBitmapFile("configuration.png")
    profil = PROFIL_ADMIN
    def __init__(self, parent):
        GPanel.__init__(self, parent, 'Configuration')
        self.notebook = ParametresNotebook(self)
        self.sizer.Add(self.notebook, 1, wx.EXPAND)

    def UpdateContents(self):
        self.notebook.UpdateContents()

