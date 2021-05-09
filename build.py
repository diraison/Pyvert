#!/usr/bin/env python3
"""
Ceci est l'outil de création des fichiers markdown pour les exercices
au format .dat qui se trouvent dans le répertoire docs/ ; et de génération
du fichier mkdocs.yml incluant ces exercices en respectant l'ordre imposé
par les préfixes numériques des fichiers.
"""


import os
import sys
import getopt

PYEXO_URL = "/pyexo.html"

################################################

def usage(cmdname, exitcode):
    """ affiche les options de la ligne de commande et quitte le programme """
    print("""usage : {} [-h] --url PYEXO_URL

        Génère les fichiers markdown correspondant aux exercices placés
        dans docs/ et portant l'extension .dat
        Puis génère le fichier mkdocs.yml en recréant toute l'arborescence
        en respectant l'ordre des numéros préfixes (qui sont retirés des
        pages web).

        PYEXO_URL est l'url utilisé pour le cadre intégré à chaque page
        d'exercice. Par défaut, il correspond à "{}".
""".format(cmdname, PYEXO_URL))
    sys.exit(exitcode)

def configure(argv):
    """ lecture des options de configuration et renvoie de l'url de pyexo """
    pyexo_url = PYEXO_URL
    try:
        opts, args = getopt.getopt(argv[1:], "hu:", ["help", "url="])
    except getopt.GetoptError:
        usage(argv[0], 1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(argv[0], 0)
        if opt in ("-u", "--url"):
            pyexo_url = arg
    if args:
        usage(argv[0], 1)   # trop d'arguments
    return pyexo_url or PYEXO_URL

################################################

def lecture_patron(chemin):
    """ renvoie le contenu du fichier patron """
    with open(chemin) as fichier:
        patron = fichier.read()
    return patron

################################################

def creer_markdown(chemin, fichier, patron):
    """ génère le fichier markdown d'un exercice """
    print(chemin, fichier, end="\t")
    if not fichier.endswith(".dat"):
        print("RIEN")
        return None
    nouveau_fichier = fichier[:-4] + ".md"
    print("=> ", os.path.join(chemin, nouveau_fichier), end="\t")
    markdown = patron.replace("CHEMIN", os.path.join(chemin, fichier))\
                     .replace("TITRE", simplifier_nom(fichier))
    try:
        with open(os.path.join(chemin, nouveau_fichier), "w") as fmarkdown:
            fmarkdown.write(markdown)
    except IOError as erreur:
        print("ECHEC : {}".format(erreur))
        return None
    print("FAIT")
    return os.path.join(chemin, nouveau_fichier)

def generer_markdown(pyexo_url):
    """ génère l'ensemble de fichiers markdown des exercices """
    patron = lecture_patron("exercice.tmpl").replace("PYEXO_URL", pyexo_url)
    exercices = []
    for chemin, _, fichiers in os.walk("docs"):
        # fichiers.sort()
        for fichier in fichiers:
            if fichier.endswith(".dat"):
                exercice = creer_markdown(chemin, fichier, patron)
                if exercice is not None:
                    exercices.append(exercice)
    return exercices

################################################

def simplifier_nom(nom):
    """ supprime le préfixe numérique, les extensions et place des espaces """
    while nom and nom[0] in "0123456789.-_ ":
        nom = nom[1:]
    nom = nom[:-3] if nom.endswith(".md") else nom
    nom = nom[:-4] if nom.endswith(".dat") else nom
    nom = nom.replace(".", " ").replace("_", " ")
    return nom

def parcourir_arbre(arbre, niveau):
    """ renvoie la chaîne de navigation correspondant à l'arborescence """
    nav = ""
    for chemin in sorted(arbre.keys()):
        if isinstance(arbre[chemin], str):
            nav += "  " * niveau + "- \"{}\":".format(simplifier_nom(chemin))
            _, _, fichier = arbre[chemin].partition(os.sep)  # enleve "docs/"
            nav += " \"{}\"\n".format(fichier)
        else:
            nav += "  " * niveau + "- \"{}\":\n".format(simplifier_nom(chemin))
            nav += parcourir_arbre(arbre[chemin], niveau+1)
    return nav

def generer_arborescence(exercices):
    """ génère l'arborescence des exercices et renvoie la chaîne de navigation """
    arbre = {}
    for exercice in exercices:
        chemin = exercice
        sousarbre = arbre
        while exercice != "":
            racine, _, exercice = exercice.partition(os.sep)
            if racine not in sousarbre:
                sousarbre[racine] = {}
            sousarbre = sousarbre[racine]
            if os.sep not in exercice and exercice.endswith(".md"):
                sousarbre[exercice] = chemin
    return parcourir_arbre(arbre["docs"], 1)

def generer_mkdocs(exercices):
    """ génère le fichier mkdocs.yml à partir du patron et des exercices """
    print("mkdocs.tmpl", end="\t")
    patron = lecture_patron("mkdocs.tmpl")
    arborescence = generer_arborescence(exercices)
    print("=> mkdocs.yml", end="\t")
    yaml = patron.replace("EXERCICES", arborescence).replace("NBEXOS", str(len(exercices)))
    try:
        with open("mkdocs.yml", "w") as fmkdocs:
            fmkdocs.write(yaml)
    except IOError as erreur:
        print("ECHEC : {}".format(erreur))
        return
    print("FAIT")

################################################

def main(argv):
    """ fonction principale appelée avec les arguments de la ligne de commande """
    pyexo_url = configure(argv)
    exercices = generer_markdown(pyexo_url)
    generer_mkdocs(exercices)


if __name__ == "__main__":
    main(sys.argv)
