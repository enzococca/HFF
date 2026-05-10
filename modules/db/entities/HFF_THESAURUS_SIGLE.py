"""HFF Thesaurus entity. Maps to hff_system__thesaurus_sigle table.

Holds per-(table, field) controlled vocabularies for the form comboboxes.
See modules/utility/hff_combobox_defaults.py for the in-code seed values
that are loaded into this table on first open.
"""
from builtins import object


class HFF_THESAURUS_SIGLE(object):
    def __init__(self,
                 id_thesaurus_sigle,
                 nome_tabella,
                 sigla,
                 sigla_estesa,
                 descrizione,
                 tipologia_sigla,
                 lingua):
        self.id_thesaurus_sigle = id_thesaurus_sigle
        self.nome_tabella = nome_tabella
        self.sigla = sigla
        self.sigla_estesa = sigla_estesa
        self.descrizione = descrizione
        self.tipologia_sigla = tipologia_sigla
        self.lingua = lingua

    def __repr__(self):
        return ("<HFF_THESAURUS_SIGLE("
                "%r, %r, %r, %r, %r, %r, %r)>"
                % (self.id_thesaurus_sigle,
                   self.nome_tabella,
                   self.sigla,
                   self.sigla_estesa,
                   self.descrizione,
                   self.tipologia_sigla,
                   self.lingua))
