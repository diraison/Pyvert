#!/usr/bin/env python3

import os
import sys
import getopt

################################################

def usage(cmdname, exitcode):
    print("""usage : {} [-h] [PYEXO_URL]

        Génère les fichiers markdown correspondant aux exercices placés
        dans docs/ et portant l'extension .dat
        Puis génère le fichier mkdocs.yml en recréant toute l'arborescence
        en respectant l'ordre des numéros préfixes (qui sont retirés des
        pages web).

        PYEXO_URL est l'url utilisée pour le cadre intégré à chaque page
        d'exercice. Par défaut, il correspond à "/pyexo.html".
""".format(cmdname))
    sys.exit(exitcode)

def configure(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "h", ["help"])
    except getopt.GetoptError:
        usage(argv[0], 1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(argv[0], 0)
    if len(args) == 0:
        return "/pyexo.html"
    elif len(args) == 1:
        return args[0]
    print("trop d'arguments")
    usage(argv[0], 1)

################################################

def lecture_patron(chemin):
    with open(chemin) as fichier:
        patron = fichier.read()
    return patron

################################################

def creer_markdown(chemin, fichier, patron):
    print(chemin, fichier, end="\t")
    if not fichier.endswith(".dat"):
        print("RIEN")
        return None
    nouveau_fichier = fichier[:-4] + ".md"
    print("=> ", os.path.join(chemin, nouveau_fichier), end="\t")
    markdown = patron.replace("CHEMIN", os.path.join(chemin, fichier)).replace("TITRE", simplifier_nom(fichier))
    try:
        with open(os.path.join(chemin, nouveau_fichier), "w") as fmarkdown:
            fmarkdown.write(markdown)
    except:
        print("ECHEC")
        return None
    print("FAIT")
    return os.path.join(chemin, nouveau_fichier)

def generer_markdown(pyexo_url):
    patron = lecture_patron("exercice.tmpl").replace("PYEXO_URL", pyexo_url)
    exercices = []
    for chemin, repertoires, fichiers in os.walk("docs"):
        # fichiers.sort()
        for fichier in fichiers:
            if fichier.endswith(".dat"):
                exercice = creer_markdown(chemin, fichier, patron)
                if exercice is not None:
                    exercices.append(exercice)
    return exercices

################################################

def simplifier_nom(nom):
    while nom and nom[0] in "0123456789.-_ ":
        nom = nom[1:]
    nom = nom[:-3] if nom.endswith(".md") else nom
    nom = nom[:-4] if nom.endswith(".dat") else nom
    nom = nom.replace("."," ").replace("_", " ")
    return nom

def parcourir_arbre(arbre, niveau):
    s = ""
    for chemin in sorted(arbre.keys()):
        if isinstance(arbre[chemin], str):
            s += "  " * niveau + "- \"{}\":".format(simplifier_nom(chemin))
            _, _, fichier = arbre[chemin].partition(os.sep)  # enleve "docs/"
            s += " \"{}\"\n".format(fichier)
        else:
            s += "  " * niveau + "- \"{}\":\n".format(simplifier_nom(chemin))
            s += parcourir_arbre(arbre[chemin], niveau+1)
    return s

def generer_arborescence(exercices):
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
    return parcourir_arbre(arbre["docs"],1)

def generer_mkdocs(exercices):
    print("mkdocs.tmpl", end="\t")
    patron = lecture_patron("mkdocs.tmpl")
    arborescence = generer_arborescence(exercices)
    print("=> mkdocs.yml", end="\t")
    yaml = patron.replace("EXERCICES", arborescence)
    try:
        with open("mkdocs.yml", "w") as fmkdocs:
            fmkdocs.write(yaml)
    except:
        print("ECHEC")
        return
    print("FAIT")

################################################

def main(argv):
    pyexo_url = configure(argv)
    exercices = generer_markdown(pyexo_url)
    generer_mkdocs(exercices)


if __name__ == "__main__":
    main(sys.argv)

